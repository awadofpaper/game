"""
NPC Housing System
Manages NPC residences, inn rentals, sleeping schedules, and homeless-to-housed transitions
"""
import random
from logger_config import logger


class NPCResidence:
    """Represents an NPC's living situation"""
    def __init__(self, npc_id, residence_type="none"):
        self.npc_id = npc_id
        self.residence_type = residence_type  # "owned", "rented", "inn", "shelter", "homeless"
        self.building_id = None  # ID of the building (house, inn room, etc.)
        self.town_name = None
        self.rent_cost = 0
        self.rent_due_day = None
        self.move_in_day = None
        self.evicted = False


class NPCHousingSystem:
    """Manages all NPC housing assignments and rentals"""
    
    def __init__(self, game_time, town_manager):
        self.game_time = game_time
        self.town_manager = town_manager
        self.residences = {}  # {npc_id: NPCResidence}
        self.house_occupancy = {}  # {building_id: npc_id}
        self.inn_occupancy = {}  # {(town_name, room_number): npc_id}
        
        # Costs
        self.house_rent_base = 50  # Base rent per month
        self.inn_rent_daily = 5  # Inn room rent per day
        
        logger.info("[HOUSING] NPC Housing System initialized")
    
    def assign_npc_to_house(self, npc_id, building_id, town_name, owned=False):
        """Assign an NPC to a specific house"""
        # Check if house is already occupied
        if building_id in self.house_occupancy:
            logger.warning(f"[HOUSING] Building {building_id} already occupied by {self.house_occupancy[building_id]}")
            return False
        
        # Create or update residence
        if npc_id not in self.residences:
            self.residences[npc_id] = NPCResidence(npc_id)
        
        residence = self.residences[npc_id]
        residence.residence_type = "owned" if owned else "rented"
        residence.building_id = building_id
        residence.town_name = town_name
        residence.move_in_day = self.game_time.day_count
        
        if not owned:
            residence.rent_cost = self.house_rent_base
            residence.rent_due_day = self.game_time.day_count + 30  # Monthly rent
        
        # Mark building as occupied
        self.house_occupancy[building_id] = npc_id
        
        logger.info(f"[HOUSING] {npc_id} moved into {building_id} in {town_name} ({'owned' if owned else 'rented'})")
        return True
    
    def rent_inn_room(self, npc_id, town_name, room_number=None):
        """NPC rents an inn room"""
        # Find available room if not specified
        if room_number is None:
            room_number = self._find_available_inn_room(town_name)
            if room_number is None:
                return False, "No available rooms"
        
        # Create or update residence
        if npc_id not in self.residences:
            self.residences[npc_id] = NPCResidence(npc_id)
        
        residence = self.residences[npc_id]
        residence.residence_type = "inn"
        residence.building_id = f"{town_name}_inn"
        residence.town_name = town_name
        residence.rent_cost = self.inn_rent_daily
        residence.rent_due_day = self.game_time.day_count + 1  # Daily rent
        residence.move_in_day = self.game_time.day_count
        
        # Mark room as occupied
        self.inn_occupancy[(town_name, room_number)] = npc_id
        
        logger.info(f"[HOUSING] {npc_id} rented inn room {room_number} in {town_name}")
        return True, f"Rented room {room_number}"
    
    def _find_available_inn_room(self, town_name):
        """Find an available inn room in town"""
        max_rooms = 6  # Assuming 6 rooms per inn
        occupied_rooms = {room for (town, room), npc in self.inn_occupancy.items() if town == town_name}
        
        for room_num in range(1, max_rooms + 1):
            if room_num not in occupied_rooms:
                return room_num
        return None
    
    def evict_npc(self, npc_id, reason="unpaid_rent"):
        """Evict NPC from their residence"""
        if npc_id not in self.residences:
            return False
        
        residence = self.residences[npc_id]
        
        # Remove from occupancy tracking
        if residence.building_id in self.house_occupancy:
            del self.house_occupancy[residence.building_id]
        
        # Remove from inn occupancy
        for (town, room), occupant in list(self.inn_occupancy.items()):
            if occupant == npc_id:
                del self.inn_occupancy[(town, room)]
                break
        
        # Mark as homeless
        residence.residence_type = "homeless"
        residence.evicted = True
        residence.building_id = None
        
        logger.info(f"[HOUSING] {npc_id} evicted ({reason})")
        return True
    
    def get_npc_residence(self, npc_id):
        """Get NPC's current residence"""
        return self.residences.get(npc_id)
    
    def is_npc_homeless(self, npc_id):
        """Check if NPC is homeless"""
        residence = self.residences.get(npc_id)
        if not residence:
            return True
        return residence.residence_type in ["homeless", "shelter", "none"]
    
    def get_npc_home_location(self, npc_id):
        """Get NPC's home coordinates (for pathfinding to home)"""
        residence = self.residences.get(npc_id)
        if not residence or not residence.building_id or not residence.town_name:
            return None
        
        # Find the building in the town
        for town in self.town_manager.towns:
            if town.name == residence.town_name:
                for building in town.buildings:
                    building_id = f"{town.name}_{building.name}"
                    if building_id == residence.building_id:
                        return (building.x + building.width // 2, building.y + building.height // 2)
        
        return None
    
    def should_npc_go_home(self, current_hour):
        """Check if it's time for NPCs to go home (sleeping hours)"""
        # Sleep time: 10 PM (22:00) to 6 AM (6:00)
        return current_hour >= 22 or current_hour < 6
    
    def update_rent_collection(self, npc):
        """Check and collect rent from NPC"""
        residence = self.residences.get(id(npc))
        if not residence or residence.residence_type in ["owned", "homeless", "none"]:
            return
        
        # Check if rent is due
        if self.game_time.day_count >= residence.rent_due_day:
            # Try to collect rent
            if hasattr(npc, 'dubloons') and npc.dubloons >= residence.rent_cost:
                npc.dubloons -= residence.rent_cost
                
                # Set next rent due date
                if residence.residence_type == "inn":
                    residence.rent_due_day = self.game_time.day_count + 1  # Daily
                else:
                    residence.rent_due_day = self.game_time.day_count + 30  # Monthly
                
                logger.debug(f"[HOUSING] Collected {residence.rent_cost}g rent from {npc.name}")
            else:
                # Can't pay rent - evict
                logger.warning(f"[HOUSING] {npc.name} can't afford rent ({residence.rent_cost}g), evicting")
                self.evict_npc(id(npc), "unpaid_rent")
    
    def auto_assign_homeless_npcs(self, npc_list):
        """Automatically assign housing to homeless NPCs, ensuring 90-95% are housed by dynamically creating new houses if needed."""
        assigned_count = 0
        homeless_npcs = []
        total_npcs = len(npc_list)
        # First pass: try to assign existing houses/inns
        for npc in npc_list:
            npc_id = id(npc)
            if not self.is_npc_homeless(npc_id):
                continue
            town_name = getattr(npc, 'current_town', None)
            if not town_name:
                continue
            town = None
            for t in self.town_manager.towns:
                if t.name == town_name:
                    town = t
                    break
            if not town:
                continue
            available_house = self._find_available_house(town)
            if available_house and hasattr(npc, 'dubloons') and npc.dubloons >= self.house_rent_base * 2:
                building_id = f"{town.name}_{available_house.name}"
                if self.assign_npc_to_house(npc_id, building_id, town.name, owned=False):
                    assigned_count += 1
                    continue
            if hasattr(npc, 'dubloons') and npc.dubloons >= self.inn_rent_daily * 7:
                success, msg = self.rent_inn_room(npc_id, town.name)
                if success:
                    assigned_count += 1
                    continue
            homeless_npcs.append((npc, town))

        # Calculate housing ratio
        housed = total_npcs - len(homeless_npcs)
        target_housed = int(total_npcs * 0.92)  # 92% target (between 90-95%)
        needed_houses = max(0, target_housed - housed)

        # Dynamically create new houses and assign to remaining homeless NPCs
        for i, (npc, town) in enumerate(homeless_npcs):
            if i >= needed_houses:
                break  # Only house up to target
            # Dynamically add a house to the town
            new_house = self._add_dynamic_house_to_town(town)
            if new_house:
                npc_id = id(npc)
                building_id = f"{town.name}_{new_house.name}"
                if self.assign_npc_to_house(npc_id, building_id, town.name, owned=False):
                    assigned_count += 1

        logger.info(f"[HOUSING] Auto-assigned housing to {assigned_count} homeless NPCs (including dynamic houses)")
        return assigned_count

    def _add_dynamic_house_to_town(self, town):
        """Dynamically add a new house to the town and return the Building object."""
        from town_system import BuildingType, Building
        # Generate a unique house name
        base_name = "Dynamic House"
        existing_names = {b.name for b in town.buildings}
        idx = 1
        while f"{base_name} {idx}" in existing_names:
            idx += 1
        house_name = f"{base_name} {idx}"
        # Place house at a random valid location near town center
        width, height = 60, 70
        placed = False
        for attempt in range(10):
            angle = random.uniform(0, 2 * 3.14159)
            radius = int(town.radius * 0.5 + random.random() * town.radius * 0.3)
            x = int(town.center_x + radius * random.uniform(0.7, 1.0) * random.choice([-1, 1]))
            y = int(town.center_y + radius * random.uniform(0.7, 1.0) * random.choice([-1, 1]))
            new_rect = None
            try:
                import pygame
                new_rect = pygame.Rect(x, y, width, height)
            except Exception:
                # If pygame not available, just use x, y
                pass
            collision = False
            for existing in town.buildings:
                if new_rect and hasattr(existing, 'rect'):
                    padded_rect = existing.rect.inflate(20, 20)
                    if new_rect.colliderect(padded_rect):
                        collision = True
                        break
            if not collision:
                building = Building(BuildingType.HOUSE, x, y, width, height, name=house_name)
                town.buildings.append(building)
                placed = True
                return building
        # If couldn't place after 10 attempts, just append anyway (may overlap)
        building = Building(BuildingType.HOUSE, town.center_x, town.center_y, width, height, name=house_name)
        town.buildings.append(building)
        return building
    
    def _find_available_house(self, town):
        """Find an unoccupied house in town"""
        from town_system import BuildingType
        
        for building in town.buildings:
            # Skip non-residential buildings
            if building.type not in [BuildingType.HOUSE]:
                continue
            
            building_id = f"{town.name}_{building.name}"
            
            # Check if occupied
            if building_id not in self.house_occupancy:
                return building
        
        return None
    
    def get_housing_stats(self):
        """Get statistics about housing"""
        owned = sum(1 for r in self.residences.values() if r.residence_type == "owned")
        rented = sum(1 for r in self.residences.values() if r.residence_type == "rented")
        inn = sum(1 for r in self.residences.values() if r.residence_type == "inn")
        shelter = sum(1 for r in self.residences.values() if r.residence_type == "shelter")
        homeless = sum(1 for r in self.residences.values() if r.residence_type == "homeless")
        
        return {
            'owned': owned,
            'rented': rented,
            'inn': inn,
            'shelter': shelter,
            'homeless': homeless,
            'total': len(self.residences)
        }

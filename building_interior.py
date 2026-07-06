"""
Building Interior System
Allows players to enter buildings and explore interior spaces with furniture, NPCs, and interactive objects
"""

import pygame
import random
from logger_config import logger


class InteriorObject:
    """An object inside a building (furniture, chest, door, etc.)"""
    def __init__(self, x, y, width, height, obj_type, name="Object"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obj_type  # table, chair, chest, door, bed, shelf, desk, etc.
        self.name = name
        self.color = self._get_color()
        # Only doors, staircases, and altars should be non-solid (walkable)
        # All furniture (tables, chairs, beds, barrels, etc.) should have collision
        # Walls must be solid to contain player inside building
        self.solid = obj_type not in ["rug", "window", "door", "staircase", "room_door", "altar"]  
        self.interactable = obj_type in ["chest", "door", "desk", "shelf", "bed", "altar", "staircase", "room_door"]
        
        # For chests
        self.locked = obj_type == "chest"
        self.opened = False
        self.items = []
        self.owned = False  # Is this private property? (stealing triggers crime)
        self.owner = None  # Owner name (e.g., "Mayor", "Bank", "Shopkeeper")
        
        # For doors (exit back to town)
        self.is_exit = obj_type == "door"
        
        # For room doors (lockable, rentable)
        self.lockpick_difficulty = 30  # Default lockpick difficulty
        self.room_number = None  # Room identifier for inn doors
        self.rented_by = None  # Player name/ID if rented
        
        # For staircases (floor transitions)
        self.target_floor = None  # Which floor this staircase leads to
        self.stair_type = None  # "up" or "down"
        
        # Floor tracking (which floor is this object on)
        self.floor = 1  # Default to floor 1 (ground floor)
    
    def _get_color(self):
        """Get object color based on type"""
        colors = {
            "wall": (60, 60, 60),  # Darker grey so walls stand out more
            "table": (139, 90, 43),
            "chair": (160, 82, 45),
            "chest": (101, 67, 33),
            "door": (120, 60, 20),
            "room_door": (139, 69, 19),  # Saddle brown for room doors
            "bed": (220, 180, 140),
            "shelf": (150, 100, 50),
            "desk": (120, 80, 40),
            "counter": (140, 90, 50),
            "rug": (180, 130, 80),
            "window": (135, 206, 250),
            "fireplace": (200, 50, 50),
            "barrel": (100, 70, 40),
            "crate": (130, 90, 50),
            "altar": (120, 120, 120),  # Grey stone altar
            "staircase": (160, 140, 110),  # Light brown for stairs
        }
        return colors.get(self.type, (150, 150, 150))


class BuildingInterior:
    """Represents the interior space of a building"""
    def __init__(self, building_type, width=1400, height=1000, town_name=None, town_treasury_system=None, bank_manager=None, weapon_restriction_system=None):
        self.building_type = building_type
        self.width = width
        self.height = height
        self.objects = []
        self.npcs = []  # NPCs inside this building
        self.floor_color = (200, 180, 160)  # Wood floor
        self.wall_thickness = 20
        
        # Multi-floor support
        self.current_floor = 1  # Player's current floor (1 = ground, 2 = second floor, etc.)
        self.num_floors = 1  # Default to single floor
        
        # Inn-specific: track rentable rooms
        self.inn_rooms = {}  # room_number -> {'rented': bool, 'rented_by': player_id, 'door': obj}
        
        # Economy systems for dynamic loot
        self.town_name = town_name
        self.town_treasury_system = town_treasury_system
        self.bank_manager = bank_manager
        self.weapon_restriction_system = weapon_restriction_system
        
        # Generate interior layout based on building type
        self._generate_interior()
    
    def _generate_interior(self):
        """Generate interior layout with furniture and objects"""
        # Add walls around the perimeter
        self._add_walls()
        
        # Add door near bottom center for exit
        door_x = self.width // 2 - 20
        door_y = self.height - self.wall_thickness - 5
        exit_door = InteriorObject(door_x, door_y, 40, self.wall_thickness + 5, "door", "Exit Door")
        self.objects.append(exit_door)
        
        # Clear NPCs list before generating
        self.npcs = []
        
        # Import BuildingType for type comparison
        try:
            from town_system import BuildingType
            # Generate furniture based on building type
            if self.building_type == BuildingType.INN:
                self._generate_inn_interior()
            elif self.building_type == BuildingType.SHOP:
                self._generate_shop_interior()
            elif self.building_type == BuildingType.BLACKSMITH:
                self._generate_blacksmith_interior()
            elif self.building_type == BuildingType.TOWN_HALL:
                self._generate_town_hall_interior()
            elif self.building_type == BuildingType.TAVERN:
                self._generate_tavern_interior()
            elif self.building_type == BuildingType.TEMPLE:
                self._generate_temple_interior()
            elif self.building_type == BuildingType.BANK:
                self._generate_bank_interior()
            elif self.building_type == BuildingType.HOUSE:
                self._generate_house_interior()
            elif self.building_type == BuildingType.LOOTBOX_SHOP:
                self._generate_lootbox_shop_interior()
            elif self.building_type == BuildingType.JAIL:
                self._generate_jail_interior()
            else:
                # Generic interior
                self._generate_generic_interior()
        except ImportError:
            # Fallback for string-based types
            if self.building_type == "inn":
                self._generate_inn_interior()
            elif self.building_type == "shop":
                self._generate_shop_interior()
            elif self.building_type == "blacksmith":
                self._generate_blacksmith_interior()
            elif self.building_type == "town_hall":
                self._generate_town_hall_interior()
            elif self.building_type == "tavern":
                self._generate_tavern_interior()
            elif self.building_type == "temple":
                self._generate_temple_interior()
            elif self.building_type == "bank":
                self._generate_bank_interior()
            elif self.building_type == "house":
                self._generate_house_interior()
            elif self.building_type == "lootbox_shop":
                self._generate_lootbox_shop_interior()
            elif self.building_type == "jail":
                self._generate_jail_interior()
            else:
                # Generic interior
                self._generate_generic_interior()
        
        # Add NPCs after furniture generation
        self._place_npcs()
    
    def _place_npcs(self):
        """Place NPCs inside the building based on type"""
        try:
            from town_system import BuildingType
            
            if self.building_type == BuildingType.SHOP:
                # Shopkeeper behind counter
                self.npcs.append({
                    'x': self.width // 2,
                    'y': 120,
                    'name': 'Shopkeeper',
                    'color': (150, 100, 50),
                    'role': 'merchant'
                })
            
            elif self.building_type == BuildingType.INN:
                # Innkeeper at counter
                self.npcs.append({
                    'x': self.width // 2,
                    'y': 140,
                    'name': 'Innkeeper',
                    'color': (180, 120, 80),
                    'role': 'innkeeper'
                })
                # Patron in hallway
                self.npcs.append({
                    'x': self.width // 2 + 100,
                    'y': 500,
                    'name': 'Patron',
                    'color': (100, 100, 150),
                    'role': 'patron'
                })
            
            elif self.building_type == BuildingType.BLACKSMITH:
                # Blacksmith near forge
                self.npcs.append({
                    'x': 200,
                    'y': 180,
                    'name': 'Blacksmith',
                    'color': (150, 50, 50),
                    'role': 'blacksmith'
                })
            
            elif self.building_type == BuildingType.TOWN_HALL:
                # Mayor in private office
                self.npcs.append({
                    'x': 160,
                    'y': 200,
                    'name': 'Mayor',
                    'color': (150, 150, 50),
                    'role': 'mayor'
                })
                # Clerk at reception desk in lobby
                self.npcs.append({
                    'x': 700,
                    'y': 300,
                    'name': 'Clerk',
                    'color': (120, 120, 120),
                    'role': 'clerk'
                })
            
            elif self.building_type == BuildingType.TAVERN:
                # Bartender behind bar
                self.npcs.append({
                    'x': 260,
                    'y': 150,
                    'name': 'Bartender',
                    'color': (140, 100, 60),
                    'role': 'bartender'
                })
                # Patron at table
                self.npcs.append({
                    'x': 570,
                    'y': 620,
                    'name': 'Patron',
                    'color': (100, 100, 150),
                    'role': 'patron'
                })
                # Multiple patrons
                for i in range(3):
                    self.npcs.append({
                        'x': 150 + i * 150,
                        'y': 300 + (i % 2) * 100,
                        'name': f'Patron {i+1}',
                        'color': (80 + i*20, 80 + i*20, 120 + i*20),
                        'role': 'patron'
                    })
            
            elif self.building_type == BuildingType.TEMPLE:
                # Priest in the middle of the room
                self.npcs.append({
                    'x': self.width // 2,
                    'y': 400,
                    'name': 'Priest',
                    'color': (200, 200, 200),
                    'role': 'priest'
                })
                # Worshipper near pews
                self.npcs.append({
                    'x': self.width // 2 + 100,
                    'y': 550,
                    'name': 'Worshipper',
                    'color': (150, 150, 180),
                    'role': 'worshipper'
                })
            
            elif self.building_type == BuildingType.BANK:
                # Banker behind counter
                self.npcs.append({
                    'x': self.width // 2,
                    'y': 120,
                    'name': 'Banker',
                    'color': (100, 100, 150),
                    'role': 'banker'
                })
                # Guard
                self.npcs.append({
                    'x': self.width // 2 + 150,
                    'y': 250,
                    'name': 'Bank Guard',
                    'color': (150, 50, 50),
                    'role': 'guard'
                })
            
            elif self.building_type == BuildingType.HOUSE:
                # Resident
                self.npcs.append({
                    'x': self.width // 2 + 80,
                    'y': 250,
                    'name': 'Resident',
                    'color': (120, 120, 100),
                    'role': 'resident'
                })
            
            elif self.building_type == BuildingType.LOOTBOX_SHOP:
                # MaXx behind counter
                self.npcs.append({
                    'x': self.width // 2,
                    'y': 120,
                    'name': 'MaXx Silicon-Dioxide',
                    'color': (255, 20, 147),  # Hot pink
                    'role': 'lootbox_merchant'
                })
        
        except ImportError:
            # Fallback for string-based types
            building_type_str = str(self.building_type).lower()
            if 'lootbox' in building_type_str:
                self.npcs.append({'x': self.width // 2, 'y': 120, 'name': 'MaXx Silicon-Dioxide', 'color': (255, 20, 147), 'role': 'lootbox_merchant'})
            elif 'shop' in building_type_str:
                self.npcs.append({'x': self.width // 2, 'y': 120, 'name': 'Shopkeeper', 'color': (150, 100, 50), 'role': 'merchant'})
            elif 'inn' in building_type_str:
                self.npcs.append({'x': self.width // 2 - 60, 'y': 100, 'name': 'Innkeeper', 'color': (180, 120, 80), 'role': 'innkeeper'})
            elif 'blacksmith' in building_type_str:
                self.npcs.append({'x': self.width // 2 - 100, 'y': 150, 'name': 'Blacksmith', 'color': (150, 50, 50), 'role': 'blacksmith'})
            elif 'tavern' in building_type_str:
                self.npcs.append({'x': self.width // 2, 'y': 120, 'name': 'Bartender', 'color': (140, 100, 60), 'role': 'bartender'})
            elif 'temple' in building_type_str:
                self.npcs.append({'x': self.width // 2, 'y': 400, 'name': 'Priest', 'color': (200, 200, 200), 'role': 'priest'})
            elif 'bank' in building_type_str:
                self.npcs.append({'x': self.width // 2, 'y': 120, 'name': 'Banker', 'color': (100, 100, 150), 'role': 'banker'})
            elif 'house' in building_type_str:
                self.npcs.append({'x': self.width // 2 + 80, 'y': 250, 'name': 'Resident', 'color': (120, 120, 100), 'role': 'resident'})
            elif 'town_hall' in building_type_str or 'townhall' in building_type_str:
                self.npcs.append({'x': self.width // 2, 'y': 150, 'name': 'Mayor', 'color': (150, 150, 50), 'role': 'mayor'})
    
    def get_nearby_npc(self, x, y, max_distance=60):
        """Find the nearest NPC within range on current floor"""
        closest_npc = None
        closest_dist = max_distance
        
        for npc in self.npcs:
            # Skip NPCs not on current floor
            if npc.get('floor', 1) != self.current_floor:
                continue
            
            dx = npc['x'] - x
            dy = npc['y'] - y
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist < closest_dist:
                closest_dist = dist
                closest_npc = npc
        
        return closest_npc
    
    def get_nearby_staircase(self, x, y, max_distance=80):
        """Find the nearest staircase within range on current floor"""
        closest_staircase = None
        closest_dist = max_distance
        
        for obj in self.objects:
            if obj.type == "staircase" and obj.floor == self.current_floor:
                obj_center_x = obj.x + obj.width // 2
                obj_center_y = obj.y + obj.height // 2
                dx = x - obj_center_x
                dy = y - obj_center_y
                dist = (dx * dx + dy * dy) ** 0.5
                
                if dist < closest_dist:
                    closest_dist = dist
                    closest_staircase = obj
        
        return closest_staircase
    
    def change_floor(self, target_floor):
        """Change to a different floor"""
        if 1 <= target_floor <= self.num_floors:
            old_floor = self.current_floor
            self.current_floor = target_floor
            logger.info(f"[INTERIOR] Changed from floor {old_floor} to floor {target_floor}")
            return True
        return False
    
    def rent_room(self, room_number, player_id):
        """Rent a room to a player (unlocks door)"""
        if room_number in self.inn_rooms:
            room = self.inn_rooms[room_number]
            room['rented'] = True
            room['rented_by'] = player_id
            door = room['door']
            door.locked = False  # Unlock the rented room
            door.rented_by = player_id
            logger.info(f"[INN] Room {room_number} rented to player {player_id}")
            
            # Update nightstand ownership (no longer stealing if you rented it)
            for obj in self.objects:
                if hasattr(obj, 'room_number') and obj.room_number == room_number:
                    if obj.type == "chest":
                        obj.owned = False  # Not stealing from your own room
            
            return True
        return False
    
    def unrent_room(self, room_number):
        """End room rental (locks door again)"""
        if room_number in self.inn_rooms:
            room = self.inn_rooms[room_number]
            room['rented'] = False
            room['rented_by'] = None
            door = room['door']
            door.locked = True  # Re-lock the room
            door.rented_by = None
            logger.info(f"[INN] Room {room_number} rental ended")
            
            # Restore nightstand ownership
            for obj in self.objects:
                if hasattr(obj, 'room_number') and obj.room_number == room_number:
                    if obj.type == "chest":
                        obj.owned = True
                        obj.owner = f"Room {room_number} Guest"
            
            return True
        return False
    
    def is_room_rented(self, room_number):
        """Check if a room is currently rented"""
        if room_number in self.inn_rooms:
            return self.inn_rooms[room_number]['rented']
        return False
    
    def get_rented_room(self, player_id):
        """Get the room number rented by a specific player"""
        for room_num, room_data in self.inn_rooms.items():
            if room_data['rented'] and room_data['rented_by'] == player_id:
                return room_num
        return None
    
    def _add_walls(self):
        """Add walls around the perimeter"""
        t = self.wall_thickness
        # Top wall
        self.objects.append(InteriorObject(0, 0, self.width, t, "wall", "Wall"))
        # Left wall
        self.objects.append(InteriorObject(0, 0, t, self.height, "wall", "Wall"))
        # Right wall
        self.objects.append(InteriorObject(self.width - t, 0, t, self.height, "wall", "Wall"))
        # Bottom wall (with gap for door)
        door_gap_start = self.width // 2 - 25
        door_gap_end = self.width // 2 + 25
        self.objects.append(InteriorObject(0, self.height - t, door_gap_start, t, "wall", "Wall"))
        self.objects.append(InteriorObject(door_gap_end, self.height - t, self.width - door_gap_end, t, "wall", "Wall"))
    
    def _generate_shop_interior(self):
        """Generate shop interior with counter, shelves, and display items"""
        # Counter near the front-center
        counter = InteriorObject(self.width // 2 - 120, 120, 240, 80, "counter", "Shop Counter")
        self.objects.append(counter)
        
        # Shelves along walls - more spread out
        self.objects.append(InteriorObject(80, 100, 120, 60, "shelf", "Shelf"))
        self.objects.append(InteriorObject(self.width - 200, 100, 120, 60, "shelf", "Shelf"))
        self.objects.append(InteriorObject(80, 250, 120, 60, "shelf", "Shelf"))
        self.objects.append(InteriorObject(self.width - 200, 250, 120, 60, "shelf", "Shelf"))
        self.objects.append(InteriorObject(80, 400, 120, 60, "shelf", "Shelf"))
        self.objects.append(InteriorObject(self.width - 200, 400, 120, 60, "shelf", "Shelf"))
        
        # Display tables in center area
        self.objects.append(InteriorObject(self.width // 2 - 250, 450, 150, 100, "table", "Display Table"))
        self.objects.append(InteriorObject(self.width // 2 + 100, 450, 150, 100, "table", "Display Table"))
        self.objects.append(InteriorObject(self.width // 2 - 75, 650, 150, 100, "table", "Display Table"))
        
        # Crates for storage
        self.objects.append(InteriorObject(self.width - 180, 550, 60, 60, "crate", "Crate"))
        self.objects.append(InteriorObject(self.width - 250, 550, 60, 60, "crate", "Crate"))
        
        # Storage chest (can be locked, items might be marked as stolen if taken)
        storage_chest = InteriorObject(self.width - 180, 180, 80, 60, "chest", "Storage Chest")
        storage_chest.owned = True
        storage_chest.owner = "Shopkeeper"
        storage_chest.locked = True
        storage_chest.items = [
            ("dubloons", random.randint(10, 30)),  # Cash register money
            ("health_potion", 1),  # Max 1 potion
            ("bread", random.randint(2, 5)),
            ("herbs", random.randint(2, 4))
        ]
        self.objects.append(storage_chest)
    
    def _generate_lootbox_shop_interior(self):
        """Generate compact lootbox shop interior with counter and minimal furniture"""
        # Counter near the front-center (smaller than normal shop)
        counter = InteriorObject(self.width // 2 - 80, 100, 160, 50, "counter", "MaXx's Counter")
        self.objects.append(counter)
        
        # Two chairs for customers (one on each side, in middle area)
        self.objects.append(InteriorObject(60, 200, 40, 40, "chair", "Chair"))
        self.objects.append(InteriorObject(self.width - 100, 200, 40, 40, "chair", "Chair"))
        
        # Small display table near the side (not blocking spawn area)
        self.objects.append(InteriorObject(60, 280, 80, 50, "table", "Display Table"))
    
    def _generate_town_hall_interior(self):
        """Generate town hall with hallway leading to mayor's office, lobby, and meeting room"""
        # HALLWAY - Horizontal corridor across the middle
        hallway_y = self.height // 2 - 60
        hallway_height = 120
        
        # Upper wall of hallway (creates lobby area) - with gap for doorway in center
        doorway_width = 120
        left_wall_width = (self.width - doorway_width) // 2 - self.wall_thickness
        self.objects.append(InteriorObject(self.wall_thickness, hallway_y, left_wall_width, 15, "wall", "Interior Wall"))
        self.objects.append(InteriorObject(self.width // 2 + doorway_width // 2, hallway_y, left_wall_width, 15, "wall", "Interior Wall"))
        
        # Lower wall of hallway (creates meeting room area) - with gap for doorway in center
        self.objects.append(InteriorObject(self.wall_thickness, hallway_y + hallway_height - 15, left_wall_width, 15, "wall", "Interior Wall"))
        self.objects.append(InteriorObject(self.width // 2 + doorway_width // 2, hallway_y + hallway_height - 15, left_wall_width, 15, "wall", "Interior Wall"))
        
        # MAYOR'S OFFICE (at far left, behind a wall)
        office_door_y = hallway_y + hallway_height // 2 - 30
        # Wall separating mayor's office from hallway (with gap for door)
        self.objects.append(InteriorObject(self.wall_thickness, hallway_y, 300, office_door_y - hallway_y, "wall", "Office Wall"))
        self.objects.append(InteriorObject(self.wall_thickness, office_door_y + 60, 300, hallway_y + hallway_height - (office_door_y + 60), "wall", "Office Wall"))
        
        # Office door (in hallway leading to mayor's office)
        office_door = InteriorObject(self.wall_thickness + 280, office_door_y, 40, 60, "door", "Mayor's Office")
        office_door.is_exit = False  # This door doesn't exit the building
        self.objects.append(office_door)
        
        # MAYOR'S PRIVATE OFFICE FURNITURE
        # Large desk in the back corner
        mayor_desk = InteriorObject(80, 120, 180, 100, "desk", "Mayor's Desk")
        self.objects.append(mayor_desk)
        
        # Important chest behind mayor's desk (STEALABLE but very risky!)
        # Dynamic loot based on town treasury balance
        mayor_chest = InteriorObject(140, 80, 60, 50, "chest", "Mayor's Strongbox")
        mayor_chest.locked = True
        mayor_chest.owned = True
        mayor_chest.owner = "Mayor"
        mayor_chest.lockpick_difficulty = 60  # Very hard (requires high lockpick skill)
        
        # Calculate dynamic gold from treasury (70% of treasury balance, min 200, NO CAP)
        treasury_gold = 200  # Default minimum
        if self.town_treasury_system and self.town_name:
            treasury_balance = self.town_treasury_system.get_balance(self.town_name)
            treasury_gold = max(200, int(treasury_balance * 0.7))  # No maximum cap
        
        mayor_chest.items = [
            ("dubloons", treasury_gold),  # Dynamic from town treasury
            ("health_potion", random.randint(2, 4)),
            ("mana_potion", random.randint(1, 2)),
            ("lockpick", random.randint(1, 2))
        ]
        self.objects.append(mayor_chest)
        
        # CONFISCATED WEAPONS CHEST (next to mayor's desk)
        # This is where weapons taken from citizens are stored
        weapons_chest = InteriorObject(60, 260, 70, 60, "chest", "Confiscated Weapons Locker")
        weapons_chest.locked = True
        weapons_chest.owned = True
        weapons_chest.owner = "Town Guard"
        weapons_chest.lockpick_difficulty = 45  # Hard (requires good lockpick skill)
        weapons_chest.is_confiscated_weapons = True  # Special flag
        
        # Populate with confiscated weapons (dynamic based on actual confiscations)
        weapons_chest.items = []
        if self.weapon_restriction_system and self.town_name:
            confiscated_weapons = self.weapon_restriction_system.town_hall_storage.get(self.town_name, [])
            if confiscated_weapons:
                # Convert weapon objects to item tuples for chest
                for weapon in confiscated_weapons:
                    weapon_name = getattr(weapon, 'name', 'weapon')
                    weapons_chest.items.append((weapon_name, 1))
                logger.info(f"[TOWN HALL] Loaded {len(confiscated_weapons)} confiscated weapons into chest")
            else:
                # Empty chest if no weapons confiscated
                weapons_chest.items.append(("note", 1))  # Placeholder note
        else:
            # Fallback if system not available
            weapons_chest.items.append(("note", 1))
        
        self.objects.append(weapons_chest)
        
        # Filing cabinet in office
        self.objects.append(InteriorObject(80, 280, 80, 60, "shelf", "File Cabinet"))
        
        # Bookshelf in office
        self.objects.append(InteriorObject(200, 280, 80, 60, "shelf", "Bookshelf"))
        
        # LOBBY AREA (above hallway) - Citizen waiting area
        # Bulletin board
        self.objects.append(InteriorObject(400, 80, 100, 80, "shelf", "Bulletin Board"))
        
        # Waiting benches
        self.objects.append(InteriorObject(600, 150, 120, 50, "chair", "Waiting Bench"))
        self.objects.append(InteriorObject(800, 150, 120, 50, "chair", "Waiting Bench"))
        self.objects.append(InteriorObject(1000, 150, 120, 50, "chair", "Waiting Bench"))
        
        # Reception desk in lobby
        self.objects.append(InteriorObject(600, 280, 200, 80, "counter", "Reception Desk"))
        
        # Records cabinet
        records = InteriorObject(1200, 150, 80, 60, "chest", "Records Cabinet")
        records.locked = True
        records.owned = True
        records.owner = "Town Hall"
        records.items = [
            ("health_potion", random.randint(1, 3)),
            ("lockpick", 1)
        ]
        self.objects.append(records)
        
        # MEETING ROOM (below hallway) - Council chamber
        # Large council table
        self.objects.append(InteriorObject(self.width // 2 - 200, 650, 400, 150, "table", "Council Table"))
        
        # Council chairs around table
        self.objects.append(InteriorObject(self.width // 2 - 280, 680, 60, 50, "chair", "Council Chair"))
        self.objects.append(InteriorObject(self.width // 2 - 280, 750, 60, 50, "chair", "Council Chair"))
        self.objects.append(InteriorObject(self.width // 2 + 220, 680, 60, 50, "chair", "Council Chair"))
        self.objects.append(InteriorObject(self.width // 2 + 220, 750, 60, 50, "chair", "Council Chair"))
        self.objects.append(InteriorObject(self.width // 2 - 30, 600, 60, 50, "chair", "Head Chair"))
        
        # Storage chest in meeting room
        meeting_storage = InteriorObject(1100, 700, 70, 50, "chest", "Supply Chest")
        meeting_storage.owned = True
        meeting_storage.owner = "Town Hall"
        meeting_storage.items = [
            ("bread", random.randint(3, 6)),
            ("health_potion", random.randint(1, 2))
        ]
        self.objects.append(meeting_storage)
    
    def _generate_inn_interior(self):
        """Generate inn interior with reception on floor 1 and individual bedrooms on floor 2"""
        # Set up multi-floor inn
        self.num_floors = 2
        logger.info("[INN] Generating 2-floor inn interior with private room system")
        
        # ========== FLOOR 1: RECEPTION & COMMON AREA ==========
        # Reception counter near entrance
        reception_counter = InteriorObject(self.width // 2 - 150, 100, 300, 80, "counter", "Reception Desk")
        reception_counter.floor = 1
        self.objects.append(reception_counter)
        
        # Innkeeper NPC behind reception (will be placed on floor 1)
        self.npcs.append({
            'x': self.width // 2,
            'y': 150,
            'name': 'Innkeeper',
            'color': (180, 140, 100),
            'role': 'innkeeper',
            'floor': 1
        })
        
        # Waiting chairs
        for i, x_pos in enumerate([200, self.width - 260]):
            chair = InteriorObject(x_pos, 100, 60, 50, "chair", f"Chair {i+1}")
            chair.floor = 1
            self.objects.append(chair)
        
        # Common area table and chairs (floor 1)
        common_table = InteriorObject(self.width // 2 - 80, 400, 160, 100, "table", "Common Table")
        common_table.floor = 1
        self.objects.append(common_table)
        
        for i, (x, y) in enumerate([(self.width // 2 - 150, 450), (self.width // 2 + 90, 450)]):
            chair = InteriorObject(x, y, 60, 50, "chair", f"Chair {i+3}")
            chair.floor = 1
            self.objects.append(chair)
        
        # Inn storage chest (floor 1)
        inn_storage = InteriorObject(100, 350, 80, 60, "chest", "Inn Storage")
        inn_storage.owned = True
        inn_storage.owner = "Innkeeper"
        inn_storage.locked = False
        inn_storage.floor = 1
        inn_storage.items = [
            ("dubloons", random.randint(10, 30)),
            ("health_potion", random.randint(1, 2)),
            ("bread", random.randint(4, 8)),
            ("herbs", random.randint(2, 4))
        ]
        self.objects.append(inn_storage)
        
        # STAIRCASE to second floor (positioned near entrance for easy access)
        # Placing it to the left of the door/spawn area
        # Made larger (150x120) for better visibility
        stair_x = self.width // 2 - 150
        stair_y = self.height - 280
        staircase_up = InteriorObject(stair_x, stair_y, 150, 120, "staircase", "Stairs to Rooms")
        staircase_up.floor = 1
        staircase_up.target_floor = 2
        staircase_up.stair_type = "up"
        staircase_up.solid = False  # Can walk through to trigger floor change
        self.objects.append(staircase_up)
        
        # ========== FLOOR 2: BEDROOMS WITH HALLWAY ==========
        # Central hallway dimensions
        hallway_width = 200
        hallway_x_start = self.width // 2 - hallway_width // 2
        hallway_x_end = hallway_x_start + hallway_width
        
        # Staircase arrival point (top of stairs on floor 2) - same size as floor 1 stairs
        staircase_down = InteriorObject(stair_x, stair_y, 150, 120, "staircase", "Stairs to Lobby")
        staircase_down.floor = 2
        staircase_down.target_floor = 1
        staircase_down.stair_type = "down"
        staircase_down.solid = False
        self.objects.append(staircase_down)
        
        # Create 6 individual rooms (3 on each side of hallway)
        room_configs = [
            # Left side rooms
            {'number': 1, 'x': self.wall_thickness + 50, 'y': 100, 'side': 'left'},
            {'number': 2, 'x': self.wall_thickness + 50, 'y': 350, 'side': 'left'},
            {'number': 3, 'x': self.wall_thickness + 50, 'y': 600, 'side': 'left'},
            # Right side rooms
            {'number': 4, 'x': self.width - 350, 'y': 100, 'side': 'right'},
            {'number': 5, 'x': self.width - 350, 'y': 350, 'side': 'right'},
            {'number': 6, 'x': self.width - 350, 'y': 600, 'side': 'right'},
        ]
        
        room_width = 250
        room_height = 200
        
        for room_cfg in room_configs:
            room_num = room_cfg['number']
            room_x = room_cfg['x']
            room_y = room_cfg['y']
            is_left = room_cfg['side'] == 'left'
            
            # Room walls (create enclosed space)
            # Top wall
            top_wall = InteriorObject(room_x - 10, room_y - 10, room_width + 20, 10, "wall", f"Room {room_num} Wall")
            top_wall.floor = 2
            self.objects.append(top_wall)
            
            # Bottom wall
            bottom_wall = InteriorObject(room_x - 10, room_y + room_height, room_width + 20, 10, "wall", f"Room {room_num} Wall")
            bottom_wall.floor = 2
            self.objects.append(bottom_wall)
            
            # Side walls (with gap for door)
            if is_left:
                # Left room: door on right side (facing hallway)
                left_wall = InteriorObject(room_x - 10, room_y, 10, room_height, "wall", f"Room {room_num} Wall")
                left_wall.floor = 2
                self.objects.append(left_wall)
                
                # Right wall with door gap
                door_y_offset = room_height // 2 - 30
                right_wall_top = InteriorObject(room_x + room_width, room_y, 10, door_y_offset, "wall", f"Room {room_num} Wall")
                right_wall_top.floor = 2
                self.objects.append(right_wall_top)
                
                right_wall_bottom = InteriorObject(room_x + room_width, room_y + door_y_offset + 60, 10, room_height - door_y_offset - 60, "wall", f"Room {room_num} Wall")
                right_wall_bottom.floor = 2
                self.objects.append(right_wall_bottom)
                
                # Door position (on right wall, facing hallway)
                door_x = room_x + room_width
                door_y = room_y + door_y_offset
            else:
                # Right room: door on left side (facing hallway)
                right_wall = InteriorObject(room_x + room_width, room_y, 10, room_height, "wall", f"Room {room_num} Wall")
                right_wall.floor = 2
                self.objects.append(right_wall)
                
                # Left wall with door gap
                door_y_offset = room_height // 2 - 30
                left_wall_top = InteriorObject(room_x - 10, room_y, 10, door_y_offset, "wall", f"Room {room_num} Wall")
                left_wall_top.floor = 2
                self.objects.append(left_wall_top)
                
                left_wall_bottom = InteriorObject(room_x - 10, room_y + door_y_offset + 60, 10, room_height - door_y_offset - 60, "wall", f"Room {room_num} Wall")
                left_wall_bottom.floor = 2
                self.objects.append(left_wall_bottom)
                
                # Door position (on left wall, facing hallway)
                door_x = room_x - 10
                door_y = room_y + door_y_offset
            
            # Create room door (LOCKED by default, lockpickable)
            room_door = InteriorObject(door_x, door_y, 10, 60, "room_door", f"Room {room_num}")
            room_door.floor = 2
            room_door.room_number = room_num
            room_door.locked = True  # All rooms locked by default
            room_door.lockpick_difficulty = 25 + room_num * 5  # Harder rooms have harder locks
            room_door.is_exit = False
            room_door.solid = True  # Doors block movement when closed/locked
            room_door.opened = False
            room_door.rented_by = None
            self.objects.append(room_door)
            
            # Track room in inn_rooms dict
            self.inn_rooms[room_num] = {
                'rented': False,
                'rented_by': None,
                'door': room_door
            }
            
            # Furniture inside room
            # Bed
            bed_x = room_x + 30
            bed_y = room_y + 30
            bed = InteriorObject(bed_x, bed_y, 120, 80, "bed", f"Bed {room_num}")
            bed.floor = 2
            bed.room_number = room_num
            self.objects.append(bed)
            
            # Nightstand with chest
            nightstand = InteriorObject(bed_x + 140, bed_y + 15, 60, 50, "chest", f"Nightstand {room_num}")
            nightstand.floor = 2
            nightstand.room_number = room_num
            nightstand.locked = False
            nightstand.owned = True  # Taking items is stealing unless rented
            nightstand.owner = f"Room {room_num} Guest"
            nightstand.items = [
                ("dubloons", random.randint(0, 5)),
                ("health_potion", random.randint(0, 1))
            ]
            self.objects.append(nightstand)
            
            # Small table
            table = InteriorObject(bed_x, bed_y + 100, 80, 60, "table", f"Table {room_num}")
            table.floor = 2
            table.room_number = room_num
            self.objects.append(table)
            
            # Chair
            chair = InteriorObject(bed_x + 90, bed_y + 110, 50, 40, "chair", f"Chair {room_num}")
            chair.floor = 2
            chair.room_number = room_num
            self.objects.append(chair)
        
        logger.info(f"[INN] Created 6 private rooms with lockable doors on floor 2")
        logger.info(f"[INN] Room rental tracking initialized: {len(self.inn_rooms)} rooms available")
    
    def _generate_blacksmith_interior(self):
        """Generate blacksmith with forge area, work area, and display area"""
        # FORGE AREA (left side)
        # Large forge/fireplace
        self.objects.append(InteriorObject(120, 120, 140, 100, "fireplace", "Forge"))
        
        # Anvil next to forge
        self.objects.append(InteriorObject(300, 140, 80, 60, "desk", "Anvil"))
        
        # Coal/material storage near forge
        self.objects.append(InteriorObject(120, 260, 70, 70, "barrel", "Coal Barrel"))
        self.objects.append(InteriorObject(210, 260, 70, 70, "barrel", "Iron Barrel"))
        
        # WORK AREA (center)
        # Large work table
        self.objects.append(InteriorObject(self.width // 2 - 120, 400, 240, 120, "table", "Work Table"))
        
        # Tool storage
        tool_chest = InteriorObject(450, 250, 100, 70, "chest", "Tool Chest")
        tool_chest.owned = True
        tool_chest.owner = "Blacksmith"
        tool_chest.locked = False
        tool_chest.items = [
            ("dubloons", random.randint(0, 10)),  # Petty cash
            ("ore", random.randint(8, 15)),  # High crafting materials
            ("lockpick", random.randint(1, 3)),  # Smiths make metal tools
            ("cloth", random.randint(1, 3))
        ]
        self.objects.append(tool_chest)
        
        # DISPLAY AREA (right side)
        # Weapon racks
        self.objects.append(InteriorObject(self.width - 180, 120, 100, 60, "shelf", "Weapon Rack"))
        self.objects.append(InteriorObject(self.width - 180, 220, 100, 60, "shelf", "Weapon Rack"))
        self.objects.append(InteriorObject(self.width - 180, 320, 100, 60, "shelf", "Armor Stand"))
        
        # Equipment display area
        self.objects.append(InteriorObject(self.width - 350, 600, 120, 80, "table", "Display Table"))
        self.objects.append(InteriorObject(self.width - 180, 600, 120, 80, "table", "Display Table"))
        
        # Quenching barrel
        self.objects.append(InteriorObject(300, 380, 70, 70, "barrel", "Water Barrel"))
    
    def _generate_tavern_interior(self):
        """Generate tavern with bar, tables, and seating areas"""
        # Long bar counter
        self.objects.append(InteriorObject(120, 120, 300, 80, "counter", "Bar"))
        
        # Bar stools (chairs)
        self.objects.append(InteriorObject(160, 210, 50, 50, "chair", "Bar Stool"))
        self.objects.append(InteriorObject(240, 210, 50, 50, "chair", "Bar Stool"))
        self.objects.append(InteriorObject(320, 210, 50, 50, "chair", "Bar Stool"))
        
        # Tables and chairs scattered around - more spacious
        table_positions = [
            (250, 400), (550, 350), (850, 380),
            (250, 600), (550, 580), (850, 620),
            (250, 800), (900, 800)
        ]
        for i, (x, y) in enumerate(table_positions):
            self.objects.append(InteriorObject(x, y, 120, 80, "table", f"Table {i+1}"))
            self.objects.append(InteriorObject(x - 60, y + 15, 50, 50, "chair", "Chair"))
            self.objects.append(InteriorObject(x + 130, y + 15, 50, 50, "chair", "Chair"))
        
        # Barrels in corner (storage)
        self.objects.append(InteriorObject(self.width - 150, 120, 70, 70, "barrel", "Ale Barrel"))
        self.objects.append(InteriorObject(self.width - 150, 210, 70, 70, "barrel", "Wine Barrel"))
        self.objects.append(InteriorObject(self.width - 240, 120, 70, 70, "barrel", "Mead Barrel"))
        
        # Tavern tip jar/lockbox behind bar
        tavern_chest = InteriorObject(200, 80, 60, 50, "chest", "Tip Lockbox")
        tavern_chest.locked = True
        tavern_chest.owned = True
        tavern_chest.owner = "Tavern Owner"
        tavern_chest.items = [
            ("dubloons", random.randint(5, 8)),  # Tips only
            ("herbs", random.randint(1, 2)),
            ("cloth", 1)
        ]
        self.objects.append(tavern_chest)
        
        # Fireplace for ambiance
        self.objects.append(InteriorObject(self.width - 200, 450, 100, 80, "fireplace", "Fireplace"))
    
    def _generate_temple_interior(self):
        """Generate temple with altar and prayer areas"""
        # Altar at the back (custom religious symbol)
        altar = InteriorObject(self.width // 2 - 80, 80, 160, 100, "altar", "Altar")
        # Ensure altar is interactable (redundant but explicit)
        altar.interactable = True
        altar.solid = True  # Can't walk through altar
        self.objects.append(altar)
        logger.info(f"[TEMPLE] Created altar at ({altar.x}, {altar.y}), interactable={altar.interactable}")
        
        # Pews for seating
        for i in range(4):
            y = 230 + i * 70
            self.objects.append(InteriorObject(150, y, 150, 40, "table", f"Pew {i+1}"))
            self.objects.append(InteriorObject(self.width - 300, y, 150, 40, "table", f"Pew {i+1}"))
        
        # Offering box near the entrance (bottom of room)
        offering_box = InteriorObject(self.width // 2 - 40, self.height - 180, 80, 50, "chest", "Offering Box")
        offering_box.locked = False
        offering_box.owned = True  # Taking from offering box is theft!
        offering_box.owner = "Temple"
        offering_box.items = [
            ("dubloons", random.randint(20, 80)),  # Donations
            ("health_potion", 1)  # Max 1 potion
        ]
        self.objects.append(offering_box)
    
    def _generate_bank_interior(self):
        """Generate bank with vault, counters, and security"""
        # Counter
        self.objects.append(InteriorObject(self.width // 2 - 100, 150, 200, 60, "counter", "Bank Counter"))
        
        # Vault area in back (multiple chests)
        # Dynamic loot based on bank revenue (deposits, loans, fees)
        
        # Calculate dynamic gold per vault from bank revenue
        base_vault_gold = 50
        if self.bank_manager:
            # Each vault gets 25% of bank revenue, NO CAP
            base_vault_gold = max(50, int(self.bank_manager.bank_revenue * 0.25))
        
        vault1 = InteriorObject(150, 80, 60, 50, "chest", "Vault 1")
        vault1.locked = True
        vault1.owned = True
        vault1.owner = "Bank"
        vault1.lockpick_difficulty = 50  # Hard (requires good lockpick skill)
        vault1.items = [
            ("dubloons", random.randint(base_vault_gold, base_vault_gold + 50)),
            ("health_potion", random.randint(0, 1))
        ]
        self.objects.append(vault1)
        
        vault2 = InteriorObject(230, 80, 60, 50, "chest", "Vault 2")
        vault2.locked = True
        vault2.owned = True
        vault2.owner = "Bank"
        vault2.lockpick_difficulty = 50  # Hard
        vault2.items = [
            ("dubloons", random.randint(base_vault_gold, base_vault_gold + 50)),
            ("health_potion", random.randint(0, 1))
        ]
        self.objects.append(vault2)
        
        vault3 = InteriorObject(self.width - 210, 80, 60, 50, "chest", "Vault 3")
        vault3.locked = True
        vault3.owned = True
        vault3.owner = "Bank"
        vault3.lockpick_difficulty = 50  # Hard
        vault3.items = [
            ("dubloons", random.randint(base_vault_gold, base_vault_gold + 50)),
            ("health_potion", random.randint(0, 1))
        ]
        self.objects.append(vault3)
        
        vault4 = InteriorObject(self.width - 290, 80, 60, 50, "chest", "Vault 4")
        vault4.locked = True
        vault4.owned = True
        vault4.owner = "Bank"
        vault4.lockpick_difficulty = 50  # Hard
        vault4.items = [
            ("dubloons", random.randint(base_vault_gold, base_vault_gold + 50)),
            ("health_potion", random.randint(0, 1))
        ]
        self.objects.append(vault4)
        
        # MASTER VAULT DOOR - leads to high-security vault room
        # Only accessible during break-ins, extremely difficult to pick
        vault_door = InteriorObject(self.width // 2, self.height - 200, 80, 40, "room_door", "Vault Room")
        vault_door.locked = True
        vault_door.owned = True
        vault_door.owner = "Bank"
        vault_door.lockpick_difficulty = 90  # Master-level lockpicking required
        vault_door.room_number = "VAULT"  # Special identifier
        vault_door.color = (60, 60, 80)  # Dark steel color for high security
        self.objects.append(vault_door)
        
        # Master vault chest - behind the vault door
        # Hidden from normal gameplay, only accessible during break-ins
        master_vault = InteriorObject(self.width // 2 - 30, self.height - 120, 80, 60, "chest", "Master Vault")
        master_vault.locked = True
        master_vault.owned = True
        master_vault.owner = "Bank"
        master_vault.lockpick_difficulty = 95  # Nearly impossible to pick
        master_vault.items = [
            ("dubloons", random.randint(base_vault_gold * 5, base_vault_gold * 10)),  # 5-10x normal vault
            ("diamond", random.randint(1, 3)),
            ("ruby", random.randint(2, 5)),
            ("gold_bar", random.randint(1, 2)),
        ]
        self.objects.append(master_vault)
        
        # Seating area
        self.objects.append(InteriorObject(100, 350, 40, 40, "chair", "Waiting Chair"))
        self.objects.append(InteriorObject(160, 350, 40, 40, "chair", "Waiting Chair"))
        self.objects.append(InteriorObject(self.width - 140, 350, 40, 40, "chair", "Waiting Chair"))
    
    def _generate_house_interior(self):
        """Generate generic house with bed, table, storage"""
        # Bed
        self.objects.append(InteriorObject(80, 100, 100, 60, "bed", "Bed"))
        
        # Table and chairs
        self.objects.append(InteriorObject(self.width // 2 - 60, 250, 120, 80, "table", "Dining Table"))
        self.objects.append(InteriorObject(self.width // 2 - 100, 270, 40, 40, "chair", "Chair"))
        self.objects.append(InteriorObject(self.width // 2 + 80, 270, 40, 40, "chair", "Chair"))
        
        # Storage chest (residential - player might be able to steal from)
        chest = InteriorObject(self.width - 130, 100, 70, 50, "chest", "Storage Chest")
        chest.locked = True
        chest.owned = True
        chest.owner = "Homeowner"
        chest.items = [
            ("dubloons", random.randint(0, 5)),  # Poor people, max 5g
            ("bread", random.randint(1, 3)),
            ("herbs", random.randint(0, 2)),
            ("cloth", random.randint(0, 1))
        ]
        self.objects.append(chest)
        
        # Shelf
        self.objects.append(InteriorObject(80, 350, 80, 40, "shelf", "Shelf"))
    
    def _generate_jail_interior(self):
        """Generate jail interior with cell block, guard office, and exercise yard"""
        # GUARD OFFICE (front area near entrance)
        office_wall_y = 250
        # Horizontal wall separating guard office from cell block
        self.objects.append(InteriorObject(self.wall_thickness, office_wall_y, self.width - 2*self.wall_thickness, 15, "wall", "Guard Station Wall"))
        
        # Guard office door (center of wall)
        guard_door = InteriorObject(self.width // 2 - 40, office_wall_y - 5, 80, 20, "door", "Cell Block Entry")
        guard_door.is_exit = False
        guard_door.locked = True  # Locked from inside (guards only)
        self.objects.append(guard_door)
        
        # GUARD OFFICE FURNITURE
        # Guard desk near door
        self.objects.append(InteriorObject(150, 120, 180, 80, "desk", "Guard Desk"))
        
        # Guard weapons locker (contains guard equipment)
        weapons_locker = InteriorObject(950, 100, 80, 100, "chest", "Weapons Locker")
        weapons_locker.locked = True
        weapons_locker.lockpick_difficulty = 70  # Very hard
        weapons_locker.owned = True
        weapons_locker.owner = "Prison Guards"
        weapons_locker.items = [
            ("iron_sword", 2),
            ("steel_sword", 1),
            ("health_potion", 5),
            ("lockpick", 3),
            ("dubloons", random.randint(50, 150))
        ]
        self.objects.append(weapons_locker)
        
        # Guard chairs
        self.objects.append(InteriorObject(400, 130, 40, 40, "chair", "Guard Chair"))
        self.objects.append(InteriorObject(500, 130, 40, 40, "chair", "Guard Chair"))
        
        # CELL BLOCK CORRIDOR (center aisle)
        corridor_width = 200
        corridor_x = (self.width - corridor_width) // 2
        
        # PRISON CELLS - 3 cells on each side (6 total)
        cell_width = (corridor_x - self.wall_thickness - 30) // 1  # Width for each side
        cell_height = 180
        cell_spacing = 20
        
        # Left side cells (3 cells stacked vertically)
        for i in range(3):
            cell_y = office_wall_y + 50 + i * (cell_height + cell_spacing)
            
            # Cell walls (3 walls - left, top, bottom)
            self.objects.append(InteriorObject(self.wall_thickness, cell_y, 15, cell_height, "wall", f"Cell {i+1} Wall"))
            self.objects.append(InteriorObject(self.wall_thickness, cell_y, cell_width, 15, "wall", f"Cell {i+1} Wall"))
            self.objects.append(InteriorObject(self.wall_thickness, cell_y + cell_height - 15, cell_width, 15, "wall", f"Cell {i+1} Wall"))
            
            # Cell bars (front - using window type for non-solid visual bars)
            cell_bars = InteriorObject(self.wall_thickness + cell_width - 20, cell_y + 30, 20, cell_height - 60, "window", f"Cell {i+1} Bars")
            cell_bars.color = (80, 80, 80)  # Dark gray bars
            self.objects.append(cell_bars)
            
            # Cell bed
            self.objects.append(InteriorObject(self.wall_thickness + 30, cell_y + 40, 80, 40, "bed", f"Prison Bunk"))
            
            # Small chest in cell (prisoner belongings - mostly empty)
            cell_chest = InteriorObject(self.wall_thickness + 30, cell_y + cell_height - 80, 50, 40, "chest", "Prisoner Storage")
            cell_chest.items = [("bread", 1)] if random.random() < 0.3 else []
            self.objects.append(cell_chest)
        
        # Right side cells (3 cells stacked vertically)
        right_cell_x = corridor_x + corridor_width + 10
        for i in range(3):
            cell_y = office_wall_y + 50 + i * (cell_height + cell_spacing)
            
            # Cell walls (3 walls - right, top, bottom)
            self.objects.append(InteriorObject(right_cell_x + cell_width - 15, cell_y, 15, cell_height, "wall", f"Cell {i+4} Wall"))
            self.objects.append(InteriorObject(right_cell_x, cell_y, cell_width, 15, "wall", f"Cell {i+4} Wall"))
            self.objects.append(InteriorObject(right_cell_x, cell_y + cell_height - 15, cell_width, 15, "wall", f"Cell {i+4} Wall"))
            
            # Cell bars (front)
            cell_bars = InteriorObject(right_cell_x, cell_y + 30, 20, cell_height - 60, "window", f"Cell {i+4} Bars")
            cell_bars.color = (80, 80, 80)
            self.objects.append(cell_bars)
            
            # Cell bed
            self.objects.append(InteriorObject(right_cell_x + cell_width - 120, cell_y + 40, 80, 40, "bed", "Prison Bunk"))
            
            # Small chest in cell
            cell_chest = InteriorObject(right_cell_x + cell_width - 120, cell_y + cell_height - 80, 50, 40, "chest", "Prisoner Storage")
            cell_chest.items = [("bread", 1)] if random.random() < 0.3 else []
            self.objects.append(cell_chest)
        
        # EXERCISE YARD (back area)
        yard_y = office_wall_y + 50 + 3 * (cell_height + cell_spacing) + 30
        
        # Wall separating cell block from exercise yard
        self.objects.append(InteriorObject(self.wall_thickness, yard_y, self.width - 2*self.wall_thickness, 15, "wall", "Yard Wall"))
        
        # Yard door (center)
        yard_door = InteriorObject(self.width // 2 - 40, yard_y - 5, 80, 20, "door", "Exercise Yard")
        yard_door.is_exit = False
        self.objects.append(yard_door)
        
        # Exercise equipment in yard
        self.objects.append(InteriorObject(200, yard_y + 50, 100, 60, "table", "Weight Bench"))
        self.objects.append(InteriorObject(900, yard_y + 50, 80, 80, "table", "Exercise Equipment"))
        
        # Yard storage (rarely has items)
        yard_storage = InteriorObject(600, yard_y + 100, 60, 50, "chest", "Yard Storage")
        yard_storage.items = [("bread", random.randint(1, 3))] if random.random() < 0.4 else []
        self.objects.append(yard_storage)
        
        logger.info(f"[JAIL INTERIOR] Generated jail with 6 cells, guard office, and exercise yard")
    
    def _generate_generic_interior(self):
        """Generate generic interior for undefined building types"""
        # Simple table and chairs
        self.objects.append(InteriorObject(self.width // 2 - 60, 200, 120, 80, "table", "Table"))
        self.objects.append(InteriorObject(self.width // 2 - 100, 220, 40, 40, "chair", "Chair"))
        self.objects.append(InteriorObject(self.width // 2 + 80, 220, 40, 40, "chair", "Chair"))
        
        # Storage
        self.objects.append(InteriorObject(100, 100, 70, 50, "chest", "Chest"))
    
    def get_spawn_position(self):
        """Get the position where player spawns when entering (near door)"""
        # Spawn in center of open floor area, away from all furniture
        # Staircase is at x=550-700, so spawn at x=900 to be clear
        return (900, 850)
    
    def get_exit_door(self):
        """Get the exit door object"""
        for obj in self.objects:
            if obj.is_exit:
                return obj
        return None
    
    def check_collision(self, player_rect):
        """Check if player collides with any solid objects on current floor"""
        for obj in self.objects:
            if obj.solid:
                # Skip objects not on current floor
                if hasattr(obj, 'floor') and obj.floor != self.current_floor:
                    continue
                
                obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                if player_rect.colliderect(obj_rect):
                    return obj
        return None
    
    def get_nearby_interactable(self, player_x, player_y, max_distance=60):
        """Find nearby interactable object on current floor"""
        nearest = None
        nearest_dist = max_distance
        
        from logger_config import logger
        interactable_count = 0
        
        for obj in self.objects:
            if obj.interactable:
                # Skip objects not on current floor
                if hasattr(obj, 'floor') and obj.floor != self.current_floor:
                    continue
                
                interactable_count += 1
                # Check distance to center of object
                obj_center_x = obj.x + obj.width // 2
                obj_center_y = obj.y + obj.height // 2
                dx = player_x - obj_center_x
                dy = player_y - obj_center_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance < nearest_dist:
                    nearest_dist = distance
                    nearest = obj
                    logger.debug(f"[INTERIOR] Found closer interactable: {obj.name} at distance {distance:.1f} on floor {self.current_floor}")
        
        if interactable_count == 0:
            logger.warning(f"[INTERIOR] No interactable objects found on floor {self.current_floor}!")
        elif nearest is None:
            logger.debug(f"[INTERIOR] Found {interactable_count} interactable objects on floor {self.current_floor}, but none within {max_distance} pixels")
        
        return nearest
    
    def draw(self, screen, camera_x=0, camera_y=0, viewport_offset_x=0, viewport_offset_y=0):
        """Draw the interior with optional viewport offset for centering"""
        # Draw floor (fill only the interior area if centered)
        if viewport_offset_x > 0 or viewport_offset_y > 0:
            floor_rect = pygame.Rect(viewport_offset_x, viewport_offset_y, self.width, self.height)
            pygame.draw.rect(screen, self.floor_color, floor_rect)
        else:
            screen.fill(self.floor_color)
        
        # Draw floor indicator if multi-floor building
        if self.num_floors > 1:
            from font_manager import get_font
            font = get_font(None, 24)
            floor_text = font.render(f"Floor {self.current_floor}/{self.num_floors}", True, (255, 255, 255))
            text_bg = pygame.Rect(10, 10, floor_text.get_width() + 20, floor_text.get_height() + 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), text_bg)
            screen.blit(floor_text, (20, 15))
        
        # Draw only objects on current floor
        for obj in self.objects:
            # Skip objects not on current floor
            if hasattr(obj, 'floor') and obj.floor != self.current_floor:
                continue
            
            obj_rect = pygame.Rect(obj.x - camera_x + viewport_offset_x, obj.y - camera_y + viewport_offset_y, obj.width, obj.height)
            
            # Special rendering for different object types
            if obj.type == "staircase":
                # Draw stairs with visual indicator
                pygame.draw.rect(screen, obj.color, obj_rect)
                pygame.draw.rect(screen, (100, 80, 60), obj_rect, 3)  # Border
                
                # Draw arrow indicator
                from font_manager import get_font
                font = get_font(None, 20)
                arrow = "▲" if obj.stair_type == "up" else "▼"
                text = font.render(f"{arrow} {obj.name}", True, (255, 255, 255))
                text_x = obj.x - camera_x + viewport_offset_x + obj.width // 2 - text.get_width() // 2
                text_y = obj.y - camera_y + viewport_offset_y + obj.height // 2 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))
                
            elif obj.type == "room_door":
                # Draw room door with lock indicator
                pygame.draw.rect(screen, obj.color, obj_rect)
                pygame.draw.rect(screen, (80, 50, 20), obj_rect, 2)  # Border
                
                # Draw lock indicator if locked
                if obj.locked and not obj.opened:
                    lock_x = obj.x - camera_x + viewport_offset_x + obj.width // 2
                    lock_y = obj.y - camera_y + viewport_offset_y + obj.height // 2
                    pygame.draw.circle(screen, (255, 215, 0), (lock_x, lock_y), 10)  # Gold lock
                    pygame.draw.circle(screen, (180, 140, 0), (lock_x, lock_y), 10, 2)  # Lock border
                
                # Draw room number
                from font_manager import get_font
                font = get_font(None, 18)
                room_text = font.render(str(obj.room_number), True, (255, 255, 255))
                text_x = obj.x - camera_x + viewport_offset_x + obj.width // 2 - room_text.get_width() // 2
                text_y = obj.y - camera_y + viewport_offset_y + 5
                screen.blit(room_text, (text_x, text_y))
                
            elif obj.type == "altar":
                # Draw base/pedestal (stick)
                base_width = 20
                base_height = obj.height
                base_x = obj.x - camera_x + viewport_offset_x + obj.width // 2 - base_width // 2
                base_y = obj.y - camera_y + viewport_offset_y
                pygame.draw.rect(screen, (100, 100, 100), (base_x, base_y, base_width, base_height))
                
                # Draw upside down triangle (religious symbol)
                triangle_size = 50
                apex_x = obj.x - camera_x + viewport_offset_x + obj.width // 2
                apex_y = obj.y - camera_y + viewport_offset_y + obj.height - 10  # Point at bottom
                left_x = apex_x - triangle_size
                left_y = obj.y - camera_y + viewport_offset_y + 10
                right_x = apex_x + triangle_size
                right_y = obj.y - camera_y + viewport_offset_y + 10
                
                triangle_points = [(apex_x, apex_y), (left_x, left_y), (right_x, right_y)]
                pygame.draw.polygon(screen, (120, 120, 120), triangle_points)  # Grey triangle
                pygame.draw.polygon(screen, (80, 80, 80), triangle_points, 3)  # Darker outline
            else:
                # Normal rendering for other objects
                pygame.draw.rect(screen, obj.color, obj_rect)
                
                # Draw thick white border for walls to make them VERY visible
                if obj.type == "wall":
                    pygame.draw.rect(screen, (255, 255, 255), obj_rect, 4)  # Thick white border
            
            # Draw border for interactable objects (except already specially rendered)
            if obj.interactable and obj.type not in ["altar", "staircase", "room_door"]:
                pygame.draw.rect(screen, (255, 255, 100), obj_rect, 2)
            
            # Special indicators
            if obj.type == "chest":
                # Draw lock indicator if locked
                if obj.locked and not obj.opened:
                    lock_x = obj.x - camera_x + viewport_offset_x + obj.width // 2
                    lock_y = obj.y - camera_y + viewport_offset_y + obj.height // 2
                    pygame.draw.circle(screen, (255, 215, 0), (lock_x, lock_y), 8)  # Gold lock
            elif obj.type == "door" and obj.is_exit:
                # Draw exit indicator
                from font_manager import get_font
                font = get_font(None, 16)
                text = font.render("EXIT", True, (255, 255, 255))
                text_x = obj.x - camera_x + viewport_offset_x + obj.width // 2 - text.get_width() // 2
                text_y = obj.y - camera_y + viewport_offset_y + obj.height // 2 - text.get_height() // 2
                screen.blit(text, (text_x, text_y))
        
        # Draw NPCs only on current floor
        for npc in self.npcs:
            # Skip NPCs not on current floor
            if npc.get('floor', 1) != self.current_floor:
                continue
                
            npc_screen_x = npc['x'] - camera_x + viewport_offset_x
            npc_screen_y = npc['y'] - camera_y + viewport_offset_y
            npc_size = 48
            npc_color = npc.get('color', (100, 150, 200))
            pygame.draw.rect(screen, npc_color, (npc_screen_x - npc_size//2, npc_screen_y - npc_size//2, npc_size, npc_size))
            
            # Draw name label
            from font_manager import get_font
            font = get_font(None, 14)
            name_text = font.render(npc.get('name', 'NPC'), True, (255, 255, 255))
            name_x = npc_screen_x - name_text.get_width() // 2
            name_y = npc_screen_y - npc_size // 2 - 20
            screen.blit(name_text, (name_x, name_y))

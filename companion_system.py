"""
Companion System - Hire bodyguards, mercenaries, and mages for protection and combat
Players and NPCs can hire companions at inns/taverns
Companions follow employer, auto-defend, and collect loot
"""

import pygame
import random
import math
import time
from enum import Enum


class CompanionType(Enum):
    """Types of companions available for hire"""
    BASIC_GUARD = "basic_guard"
    ELITE_MERCENARY = "elite_mercenary"
    MAGE = "mage"
    ARCHER = "archer"
    KNIGHT = "knight"


class CompanionState(Enum):
    """Companion AI states"""
    FOLLOWING = "following"
    COMBAT = "combat"
    COLLECTING_LOOT = "collecting_loot"
    RESTING = "resting"  # After death, at inn


class Companion:
    """A hireable combat companion"""
    
    def __init__(self, companion_type, name, inn_location):
        self.companion_type = companion_type
        self.name = name
        self.inn_home = inn_location  # Where they respawn
        
        # Position
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(self.x - 16, self.y - 16, 32, 32)
        
        # Employment
        self.employer = None  # Reference to player or NPC
        self.hired = False
        self.earnings_owed = 0  # 30% of all money/loot value acquired
        self.hire_time = 0  # When hired (game time)
        
        # Death and recovery
        self.alive = True
        self.is_resting = False
        self.rest_end_time = 0  # Game time when 1-month rest ends
        self.death_time = 0
        
        # State
        self.state = CompanionState.FOLLOWING
        self.combat_target = None
        
        # Movement
        self.speed = 120  # pixels per second
        self.follow_distance = 60  # Stay this close to employer
        
        # Combat stats based on type
        self._initialize_stats()
        
        # Basic starting equipment (cannot be taken by employer)
        self.starting_equipment = self._get_starting_equipment()
        self.equipment = self.starting_equipment.copy()
        
        # Additional equipment slots (employer can add/remove)
        self.extra_equipment = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }
        
        # Inventory (loot collected goes here, transferred to employer)
        self.inventory = {}
        
        # Combat
        self.last_attack_time = 0
        self.attack_cooldown = 1.5  # seconds
        self.attack_range = 50
        self.detection_range = 200  # Auto-engage enemies within this range
        
        # Visual
        self.color = self._get_type_color()
        
    def _initialize_stats(self):
        """Set stats based on companion type"""
        if self.companion_type == CompanionType.BASIC_GUARD:
            self.level = random.randint(5, 10)
            self.max_health = 80
            self.health = self.max_health
            self.base_damage = 15
            self.defense = 10
            self.magic_power = 0
            self.hire_level_requirement = {"any": 1}  # No requirement
            
        elif self.companion_type == CompanionType.ELITE_MERCENARY:
            self.level = random.randint(15, 25)
            self.max_health = 150
            self.health = self.max_health
            self.base_damage = 30
            self.defense = 20
            self.magic_power = 0
            self.hire_level_requirement = {"level": 15}  # Need player level 15
            
        elif self.companion_type == CompanionType.MAGE:
            self.level = random.randint(10, 15)
            self.max_health = 60  # Low health
            self.health = self.max_health
            self.base_damage = 10  # Low physical damage
            self.defense = 5  # Low defense
            self.magic_power = 40  # High magic
            self.hire_level_requirement = {"magic": 20}  # Need magic skill
            
        elif self.companion_type == CompanionType.ARCHER:
            self.level = random.randint(8, 12)
            self.max_health = 70
            self.health = self.max_health
            self.base_damage = 20
            self.defense = 8
            self.magic_power = 0
            self.attack_range = 150  # Longer range
            self.hire_level_requirement = {"any": 5}  # Need some experience
            
        elif self.companion_type == CompanionType.KNIGHT:
            self.level = random.randint(20, 30)
            self.max_health = 200  # Very tanky
            self.health = self.max_health
            self.base_damage = 35
            self.defense = 30  # High defense
            self.magic_power = 0
            self.hire_level_requirement = {"strength": 25}  # Need high strength
    
    def _get_starting_equipment(self):
        """Get basic starting equipment that companion keeps forever"""
        if self.companion_type == CompanionType.BASIC_GUARD:
            return {"weapon": "iron_sword", "armor": "leather_armor"}
        elif self.companion_type == CompanionType.ELITE_MERCENARY:
            return {"weapon": "steel_sword", "armor": "chainmail"}
        elif self.companion_type == CompanionType.MAGE:
            return {"weapon": "wooden_staff", "armor": "mage_robes"}
        elif self.companion_type == CompanionType.ARCHER:
            return {"weapon": "hunting_bow", "armor": "leather_armor"}
        elif self.companion_type == CompanionType.KNIGHT:
            return {"weapon": "longsword", "armor": "plate_armor"}
        return {}
    
    def _get_type_color(self):
        """Visual color for companion type"""
        colors = {
            CompanionType.BASIC_GUARD: (100, 100, 150),
            CompanionType.ELITE_MERCENARY: (150, 50, 50),
            CompanionType.MAGE: (100, 50, 200),
            CompanionType.ARCHER: (50, 150, 50),
            CompanionType.KNIGHT: (200, 180, 50)
        }
        return colors.get(self.companion_type, (100, 100, 100))
    
    def can_be_hired(self, employer):
        """Check if this companion can be hired by employer"""
        if self.hired or not self.alive or self.is_resting:
            return False
        
        # Check level requirements
        req = self.hire_level_requirement
        
        if "any" in req:
            # No specific requirement, just minimum level
            return employer.level >= req["any"]
        
        if "level" in req and employer.level < req["level"]:
            return False
        
        # Check skill requirements
        if hasattr(employer, 'skills_manager'):
            if "strength" in req:
                strength = employer.skills_manager.get_skill_level("strength")
                if strength < req["strength"]:
                    return False
            if "magic" in req:
                magic = employer.skills_manager.get_skill_level("magic")
                if magic < req["magic"]:
                    return False
        
        return True
    
    def hire(self, employer, game_time):
        """Hire this companion"""
        self.employer = employer
        self.hired = True
        self.hire_time = game_time.total_hours
        self.earnings_owed = 0
        self.x = employer.x
        self.y = employer.y
        self.state = CompanionState.FOLLOWING
        print(f"[COMPANION] {self.name} hired by {employer.name}")
    
    def dismiss(self):
        """Dismiss companion (returns to inn)"""
        self.employer = None
        self.hired = False
        self.state = CompanionState.RESTING
        # Keep earnings_owed - will be settled at inn
        print(f"[COMPANION] {self.name} dismissed, returning to inn")
    
    def die(self, game_time):
        """Companion dies - loses all loot, keeps starting equipment"""
        self.alive = False
        self.health = 0
        self.is_resting = True
        self.rest_end_time = game_time.total_hours + (24 * 30)  # 1 month (30 days)
        self.death_time = game_time.total_hours
        
        # Lose all collected loot
        self.inventory.clear()
        
        # Lose extra equipment, keep starting equipment
        self.extra_equipment = {"weapon": None, "armor": None, "accessory": None}
        self.equipment = self.starting_equipment.copy()
        
        # Return to inn
        if self.employer:
            self.employer = None
            self.hired = False
        
        print(f"[COMPANION] {self.name} has died! Resting for 1 month.")
    
    def check_rest_status(self, game_time):
        """Check if rest period is over"""
        if self.is_resting and game_time.total_hours >= self.rest_end_time:
            self.is_resting = False
            self.alive = True
            self.health = self.max_health
            print(f"[COMPANION] {self.name} has recovered and is available for hire!")
    
    def get_rest_message(self):
        """Message when player tries to hire during rest"""
        return f"{self.name}: I really need a rest from our travels. You'll have to come back later."
    
    def add_earnings(self, amount):
        """Add to earnings owed (30% of loot/money)"""
        self.earnings_owed += amount * 0.3
    
    def update(self, dt, game_time, all_enemies, all_npcs=None):
        """Update companion AI"""
        if not self.hired or not self.alive:
            return
        
        if not self.employer or not self.employer.alive:
            self.dismiss()
            return
        
        # Update position rect
        self.rect.x = int(self.x) - 16
        self.rect.y = int(self.y) - 16
        
        if self.state == CompanionState.FOLLOWING:
            self._update_following(dt)
            self._check_for_threats(all_enemies, all_npcs)
            
        elif self.state == CompanionState.COMBAT:
            self._update_combat(dt, game_time)
            
        elif self.state == CompanionState.COLLECTING_LOOT:
            self._update_loot_collection(dt)
    
    def _update_following(self, dt):
        """Follow employer"""
        if not self.employer:
            return
        
        # Calculate distance to employer
        dx = self.employer.x - self.x
        dy = self.employer.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Only move if too far away
        if distance > self.follow_distance:
            # Normalize direction
            if distance > 0:
                dx /= distance
                dy /= distance
            
            # Move towards employer
            move_speed = self.speed * dt
            self.x += dx * move_speed
            self.y += dy * move_speed
    
    def _check_for_threats(self, all_enemies, all_npcs):
        """Auto-detect and engage nearby threats"""
        if not self.employer:
            return
        
        # Check enemies
        for enemy in all_enemies:
            if not enemy.alive:
                continue
            
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            
            # If enemy is attacking employer or close to us, engage
            if dist <= self.detection_range:
                if hasattr(enemy, 'target') and enemy.target == self.employer:
                    self.engage_target(enemy)
                    return
                elif dist <= self.attack_range * 2:
                    self.engage_target(enemy)
                    return
        
        # Check hostile NPCs
        if all_npcs:
            for npc in all_npcs:
                if not hasattr(npc, 'combat_target'):
                    continue
                if npc.combat_target == self.employer:
                    dist = math.sqrt((npc.x - self.x)**2 + (npc.y - self.y)**2)
                    if dist <= self.detection_range:
                        self.engage_target(npc)
                        return
    
    def engage_target(self, target):
        """Engage enemy in combat"""
        self.combat_target = target
        self.state = CompanionState.COMBAT
        print(f"[COMPANION] {self.name} engaging {getattr(target, 'name', 'enemy')}!")
    
    def _update_combat(self, dt, game_time):
        """Combat AI - move to target and attack"""
        if not self.combat_target or not self.combat_target.alive:
            self.combat_target = None
            self.state = CompanionState.FOLLOWING
            return
        
        # Calculate distance to target
        dx = self.combat_target.x - self.x
        dy = self.combat_target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Move towards target if out of range
        if distance > self.attack_range:
            if distance > 0:
                dx /= distance
                dy /= distance
            move_speed = self.speed * dt
            self.x += dx * move_speed
            self.y += dy * move_speed
        else:
            # In range - attack
            if time.time() - self.last_attack_time >= self.attack_cooldown:
                self.attack_target()
                self.last_attack_time = time.time()
    
    def attack_target(self):
        """Perform attack on combat target"""
        if not self.combat_target:
            return
        
        # Calculate damage
        damage = self.base_damage + (self.level * 2)
        
        # Add weapon damage from extra equipment
        if self.extra_equipment["weapon"]:
            weapon = self.extra_equipment["weapon"]
            if hasattr(weapon, 'damage'):
                damage += weapon.damage
        
        # Add magic damage if mage
        if self.magic_power > 0:
            damage += self.magic_power
        
        # Apply damage
        if hasattr(self.combat_target, 'take_damage'):
            self.combat_target.take_damage(damage, self.employer)
        elif hasattr(self.combat_target, 'health'):
            self.combat_target.health -= damage
        
        print(f"[COMPANION] {self.name} attacked {getattr(self.combat_target, 'name', 'enemy')} for {damage} damage!")
        
        # Check if target died
        if hasattr(self.combat_target, 'health') and self.combat_target.health <= 0:
            self.combat_target = None
            self.state = CompanionState.FOLLOWING
    
    def _update_loot_collection(self, dt, dropped_items_list=None):
        """Move to loot and collect it"""
        if not dropped_items_list:
            self.state = CompanionState.FOLLOWING
            return
        
        # Find nearest dropped item within range
        nearest_item = None
        nearest_distance = float('inf')
        collection_range = 150  # Pixels
        
        for dropped in dropped_items_list:
            if not hasattr(dropped, 'rect'):
                continue
            
            dx = dropped.rect.centerx - self.x
            dy = dropped.rect.centery - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < collection_range and distance < nearest_distance:
                nearest_item = dropped
                nearest_distance = distance
        
        if not nearest_item:
            self.state = CompanionState.FOLLOWING
            return
        
        # Move towards loot
        dx = nearest_item.rect.centerx - self.x
        dy = nearest_item.rect.centery - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance <= 20:  # Close enough to pick up
            # Collect the item for employer
            if hasattr(self.employer, 'dubloons') and hasattr(nearest_item, 'amount'):
                # Dubloons
                self.employer.dubloons += nearest_item.amount
                print(f"[COMPANION] {self.name} collected {nearest_item.amount} dubloons for you!")
            elif hasattr(nearest_item, 'equipment_id'):
                # Equipment
                if hasattr(self.employer, 'add_item'):
                    from item import Item
                    equipment_data = nearest_item.data
                    item_stats = {}
                    if 'base_damage' in equipment_data:
                        item_stats['damage'] = equipment_data['base_damage']
                    if 'defense' in equipment_data:
                        item_stats['Defense'] = equipment_data['defense']
                    
                    item = Item(
                        name=equipment_data.get('name', 'Item'),
                        item_type=equipment_data.get('type', 'misc'),
                        item_stats=item_stats
                    )
                    if hasattr(nearest_item, 'rarity'):
                        item.rarity = nearest_item.rarity
                    
                    self.employer.add_item(item)
                    print(f"[COMPANION] {self.name} collected {equipment_data.get('name', 'item')} for you!")
            
            # Remove from dropped list
            try:
                dropped_items_list.remove(nearest_item)
            except ValueError:
                pass  # Already removed
            
            self.state = CompanionState.FOLLOWING
        else:
            # Move towards loot
            if distance > 0:
                dx /= distance
                dy /= distance
            move_speed = self.speed * dt
            self.x += dx * move_speed
            self.y += dy * move_speed
    
    def take_damage(self, damage, attacker):
        """Companion takes damage"""
        # Reduce damage by defense
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        
        print(f"[COMPANION] {self.name} took {actual_damage} damage! HP: {self.health}/{self.max_health}")
        
        # Check death
        if self.health <= 0:
            # Will be handled by die() call from combat system
            pass
    
    def draw(self, screen, camera_x, camera_y):
        """Draw companion on screen"""
        if not self.hired or not self.alive:
            return
        
        # Calculate screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw companion (larger circle than player to distinguish)
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), 18)
        pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), 18, 2)
        
        # Draw health bar
        bar_width = 40
        bar_height = 4
        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - 30
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_pct = self.health / self.max_health
        health_width = int(bar_width * health_pct)
        health_color = (0, 255, 0) if health_pct > 0.5 else (255, 165, 0) if health_pct > 0.25 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Draw name
        font = pygame.font.SysFont(None, 16)
        name_surface = font.render(self.name, True, (200, 200, 255))
        name_rect = name_surface.get_rect(center=(screen_x, screen_y - 40))
        screen.blit(name_surface, name_rect)
        
        # Draw state indicator
        if self.state == CompanionState.COMBAT:
            indicator = font.render("!", True, (255, 0, 0))
            screen.blit(indicator, (screen_x + 15, screen_y - 15))


class CompanionManager:
    """Manages all companions in the game"""
    
    def __init__(self):
        self.companions = []  # All companions in game
        self.active_companions = []  # Currently hired companions
        
    def spawn_companions_at_inn(self, inn_location, town_name):
        """Spawn companions at an inn"""
        # Create one of each type per inn
        types_to_spawn = [
            CompanionType.BASIC_GUARD,
            CompanionType.ELITE_MERCENARY,
            CompanionType.MAGE,
            CompanionType.ARCHER,
            CompanionType.KNIGHT
        ]
        
        for comp_type in types_to_spawn:
            name = self._generate_companion_name(comp_type, town_name)
            companion = Companion(comp_type, name, inn_location)
            self.companions.append(companion)
        
        print(f"[COMPANION] Spawned {len(types_to_spawn)} companions at {town_name} inn")
    
    def _generate_companion_name(self, comp_type, town_name):
        """Generate unique name for companion"""
        prefixes = ["Brave", "Bold", "Swift", "Mighty", "Wise", "Silent", "Iron", "Steel"]
        suffixes = ["guard", "blade", "staff", "arrow", "shield", "fist", "eye", "heart"]
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix} {suffix.capitalize()} of {town_name}"
    
    def get_available_companions(self, inn_location):
        """Get all companions available at this inn"""
        available = []
        for companion in self.companions:
            if companion.inn_home == inn_location and not companion.hired:
                available.append(companion)
        return available
    
    def hire_companion(self, companion, employer, game_time):
        """Hire a companion"""
        if companion.can_be_hired(employer):
            # Check max companions for employer
            current_count = sum(1 for c in self.active_companions if c.employer == employer)
            max_companions = 2  # Max 2 companions
            
            if current_count >= max_companions:
                return False, "You can only hire up to 2 companions at once."
            
            companion.hire(employer, game_time)
            self.active_companions.append(companion)
            return True, f"Hired {companion.name}!"
        
        if companion.is_resting:
            return False, companion.get_rest_message()
        
        return False, "You don't meet the requirements to hire this companion."
    
    def dismiss_companion(self, companion):
        """Dismiss a companion"""
        companion.dismiss()
        if companion in self.active_companions:
            self.active_companions.remove(companion)
    
    def update_all(self, dt, game_time, all_enemies, all_npcs):
        """Update all active companions"""
        for companion in self.active_companions[:]:  # Copy list to allow removal
            companion.update(dt, game_time, all_enemies, all_npcs)
            
            # Check for death
            if companion.health <= 0 and companion.alive:
                companion.die(game_time)
                if companion in self.active_companions:
                    self.active_companions.remove(companion)
        
        # Check rest status for all companions
        for companion in self.companions:
            if companion.is_resting:
                companion.check_rest_status(game_time)
    
    def draw_all(self, screen, camera_x, camera_y):
        """Draw all active companions"""
        # OPTIMIZATION: Screen culling - only draw companions on screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        for companion in self.active_companions:
            screen_x = companion.x - camera_x
            screen_y = companion.y - camera_y
            
            # Only draw if on screen (with small buffer)
            if -50 < screen_x < screen_width + 50 and -50 < screen_y < screen_height + 50:
                companion.draw(screen, camera_x, camera_y)
    
    def get_employer_companions(self, employer):
        """Get all companions hired by specific employer"""
        return [c for c in self.active_companions if c.employer == employer]

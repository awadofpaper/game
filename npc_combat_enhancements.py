"""
NPC Combat Enhancements - Advanced combat, looting, fleeing, and ally alerts
Adds permadeath, inventory looting, threat assessment, and group combat
"""

import math
import random


class NPCCombatAI:
    """Enhanced combat AI for NPCs"""
    
    @staticmethod
    def assess_threat(npc, target, nearby_allies=None, nearby_enemies=None):
        """
        Assess if target is too dangerous to attack
        Returns: ('safe', 'risky', 'flee')
        """
        if not target or not hasattr(target, 'level'):
            return 'safe'
        
        # Calculate own strength
        own_strength = npc.level + (npc.health / npc.max_health) * 10
        if npc.weapon:
            own_strength += npc.weapon.get('damage', 0)
        if npc.armor:
            own_strength += npc.armor.get('defense', 0) * 0.5
        
        # Add ally strength
        if nearby_allies:
            for ally in nearby_allies:
                ally_strength = ally.level * 0.5  # Allies count for 50%
                own_strength += ally_strength
        
        # Calculate target strength
        target_strength = target.level + (target.health / target.max_health) * 10
        
        # Add target's weapon/armor
        if hasattr(target, 'weapon') and target.weapon:
            target_strength += target.weapon.get('damage', 0)
        if hasattr(target, 'armor') and target.armor:
            target_strength += target.armor.get('defense', 0) * 0.5
        
        # Add enemy allies
        if nearby_enemies:
            for enemy in nearby_enemies:
                if hasattr(enemy, 'level'):
                    enemy_strength = enemy.level * 0.5
                    target_strength += enemy_strength
        
        # Determine threat level
        strength_ratio = own_strength / target_strength if target_strength > 0 else 99
        
        if strength_ratio >= 1.5:
            return 'safe'  # Much stronger, safe to attack
        elif strength_ratio >= 0.8:
            return 'risky'  # Close match, risky but possible
        else:
            return 'flee'  # Outmatched, should flee
    
    @staticmethod
    def should_attack(npc, target, all_npcs=None):
        """
        Decide if NPC should attack target
        Considers threat assessment before attacking
        """
        # Find nearby allies and enemies
        nearby_allies = []
        nearby_enemies = []
        
        if all_npcs:
            for other_npc in all_npcs:
                if other_npc == npc or not other_npc.alive or other_npc.is_recovering:
                    continue
                
                dist = math.sqrt((npc.x - other_npc.x)**2 + (npc.y - other_npc.y)**2)
                if dist <= 300:  # Within alert range
                    # Check if ally or enemy
                    if hasattr(other_npc, 'town') and hasattr(npc, 'town'):
                        if other_npc.town == npc.town:
                            nearby_allies.append(other_npc)
                        elif other_npc.combat_target == target:
                            nearby_allies.append(other_npc)  # Also fighting same target
        
        # Assess threat
        threat_level = NPCCombatAI.assess_threat(npc, target, nearby_allies, nearby_enemies)
        
        if threat_level == 'flee':
            return False  # Too dangerous
        elif threat_level == 'risky':
            # Aggressive NPCs might still attack
            if npc.base_damage > 10 and random.random() < 0.3:
                return True
            return False
        else:  # safe
            return True
    
    @staticmethod
    def should_flee(npc, attacker, all_npcs=None):
        """
        Decide if NPC should flee from combat
        """
        if not attacker:
            return False
        
        # Low health = flee
        if npc.health < npc.max_health * 0.3:
            return True
        
        # Check threat assessment
        nearby_allies = []
        if all_npcs:
            for other_npc in all_npcs:
                if other_npc == npc or not other_npc.alive or other_npc.is_recovering:
                    continue
                
                dist = math.sqrt((npc.x - other_npc.x)**2 + (npc.y - other_npc.y)**2)
                if dist <= 300:
                    if hasattr(other_npc, 'town') and hasattr(npc, 'town'):
                        if other_npc.town == npc.town:
                            nearby_allies.append(other_npc)
        
        threat_level = NPCCombatAI.assess_threat(npc, attacker, nearby_allies)
        
        return threat_level == 'flee'
    
    @staticmethod
    def call_for_help(npc, attacker, all_npcs, screen_width, screen_height, camera_x, camera_y):
        """
        Alert nearby allies if they're on screen
        Returns list of NPCs that responded
        """
        if not all_npcs:
            return []
        
        responders = []
        
        for ally in all_npcs:
            if ally == npc or not ally.alive or ally.is_recovering:
                continue
            
            # Check if on screen
            ally_screen_x = ally.x - camera_x
            ally_screen_y = ally.y - camera_y
            
            if 0 <= ally_screen_x <= screen_width and 0 <= ally_screen_y <= screen_height:
                # Check if ally (same town or friendly)
                is_ally = False
                if hasattr(ally, 'town') and hasattr(npc, 'town'):
                    if ally.town == npc.town:
                        is_ally = True
                
                if is_ally:
                    # Check if not already in combat
                    if not ally.combat_target:
                        # Ally responds!
                        ally.combat_target = attacker
                        responders.append(ally)
                        print(f"[ALLY ALERT] {ally.name} comes to help {npc.name}!")
        
        return responders


class NPCLootingSystem:
    """System for NPCs looting defeated enemies"""
    
    @staticmethod
    def loot_defeated_npc(victor, victim):
        """
        Victor loots everything from victim's inventory
        Returns dict of looted items
        """
        if not victim or not hasattr(victim, 'inventory'):
            return {}
        
        looted = {}
        
        # Steal everything from inventory
        for item_name, count in victim.inventory.items():
            if count > 0:
                # Add to victor's inventory
                if item_name not in victor.inventory:
                    victor.inventory[item_name] = 0
                victor.inventory[item_name] += count
                looted[item_name] = count
        
        # Clear victim's inventory
        victim.inventory.clear()
        victim.current_weight = 0
        
        # Steal dubloons
        if hasattr(victim, 'dubloons') and victim.dubloons > 0:
            stolen_dubloons = victim.dubloons
            victor.dubloons += stolen_dubloons
            victim.dubloons = 0
            looted['dubloons'] = stolen_dubloons
        
        if looted:
            total_items = sum(v for k, v in looted.items() if k != 'dubloons')
            print(f"[LOOTING] {victor.name} looted {total_items} items and {looted.get('dubloons', 0)}g from {victim.name}")
        
        return looted
    
    @staticmethod
    def loot_defeated_enemy(npc, enemy_drops):
        """
        NPC loots items from defeated enemy
        enemy_drops is a list of item names ['iron_ore', 'iron_ore', 'gold']
        """
        if not enemy_drops:
            return
        
        for item_name in enemy_drops:
            if item_name not in npc.inventory:
                npc.inventory[item_name] = 0
            npc.inventory[item_name] += 1
        
        print(f"[LOOTING] {npc.name} collected {len(enemy_drops)} items from enemy")
    
    @staticmethod
    def calculate_loot_value(inventory):
        """
        Calculate total value of inventory for insurance/payment purposes
        Returns total value in dubloons
        """
        # Base item values (simplified)
        item_values = {
            'iron_ore': 10,
            'copper_ore': 5,
            'gold_ore': 30,
            'silver_ore': 20,
            'coal': 8,
            'wood': 5,
            'fish': 3,
            'rare_fish': 15,
            'herbs': 5,
            'rare_herb': 20,
            'stone': 2,
            'gem': 50
        }
        
        total_value = 0
        for item_name, count in inventory.items():
            if item_name == 'dubloons':
                total_value += count
            else:
                item_value = item_values.get(item_name, 1)  # Default 1g if unknown
                total_value += item_value * count
        
        return total_value


class NPCFleeingAI:
    """AI for NPCs fleeing from combat"""
    
    @staticmethod
    def flee_from_target(npc, threat, dt):
        """
        Move away from threat at high speed
        Returns True if successfully fleeing
        """
        if not threat:
            return False
        
        # Calculate flee direction (opposite of threat)
        dx = npc.x - threat.x
        dy = npc.y - threat.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            # Random flee direction if exactly on top
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            distance = math.sqrt(dx * dx + dy * dy)
        
        # Normalize
        dx /= distance
        dy /= distance
        
        # Flee at double speed
        flee_speed = npc.speed * 2 * dt
        npc.x += dx * flee_speed
        npc.y += dy * flee_speed
        
        # Update rect
        npc.rect.x = int(npc.x) - 16
        npc.rect.y = int(npc.y) - 16
        
        return True
    
    @staticmethod
    def find_safe_location(npc, threat, world):
        """
        Find safe location away from threat (town, etc)
        Returns (x, y) or None
        """
        # For now, flee towards home town
        if hasattr(npc, 'town'):
            return npc.town.center_x, npc.town.center_y
        
        return None
    
    @staticmethod
    def is_safe_distance(npc, threat):
        """Check if NPC has fled far enough"""
        if not threat:
            return True
        
        dist = math.sqrt((npc.x - threat.x)**2 + (npc.y - threat.y)**2)
        return dist > 500  # Safe if 500+ pixels away


class NPCCombatManager:
    """
    Central manager for NPC combat, looting, and fleeing
    Integrates all combat enhancements
    """
    
    def __init__(self):
        self.combat_log = []  # Track combat events
        self.flee_npcs = {}  # {npc_id: flee_target}
    
    def update_npc_combat(self, npc, dt, game_time, all_npcs, all_enemies, screen_width, screen_height, camera_x, camera_y):
        """
        Update NPC combat behavior with enhancements
        """
        if not npc.alive or npc.is_recovering:
            return
        
        # Check if fleeing
        npc_id = id(npc)
        if npc_id in self.flee_npcs:
            threat = self.flee_npcs[npc_id]
            
            # Flee from threat
            NPCFleeingAI.flee_from_target(npc, threat, dt)
            
            # Check if safe
            if NPCFleeingAI.is_safe_distance(npc, threat):
                del self.flee_npcs[npc_id]
                npc.combat_target = None
                print(f"[FLEE] {npc.name} escaped to safety!")
            return
        
        # Check if should flee from current combat
        if npc.combat_target:
            should_flee = NPCCombatAI.should_flee(npc, npc.combat_target, all_npcs)
            if should_flee:
                self.flee_npcs[npc_id] = npc.combat_target
                print(f"[FLEE] {npc.name} is fleeing from {npc.combat_target.name}!")
                return
        
        # Normal combat logic handled by existing NPC update
        # We just enhance decision-making and add looting
    
    def on_npc_kill(self, victor, victim, game_time):
        """
        Called when an NPC kills another NPC
        Handles looting and permanent death
        """
        # Loot everything
        looted = NPCLootingSystem.loot_defeated_npc(victor, victim)
        
        # Record event
        self.combat_log.append({
            'time': game_time.total_hours,
            'victor': victor.name,
            'victim': victim.name,
            'loot': looted
        })
        
        # Victim dies permanently (no respawn as per user requirement)
        victim.alive = False
        victim.is_recovering = False  # Can't recover
        
        print(f"[PERMADEATH] {victim.name} has been killed by {victor.name}. They will not respawn.")
    
    def call_allies(self, npc, attacker, all_npcs, screen_width, screen_height, camera_x, camera_y):
        """Call for help from nearby allies"""
        responders = NPCCombatAI.call_for_help(
            npc, attacker, all_npcs, 
            screen_width, screen_height, 
            camera_x, camera_y
        )
        return responders

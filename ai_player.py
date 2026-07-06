"""
AI Player - Automated testing agent for RPG game
Navigates, tests features, and reports issues
"""

import random
import math
import logging

logger = logging.getLogger(__name__)


class AIPlayer:
    """AI agent that controls the player to test game features"""
    
    def __init__(self):
        self.enabled = False
        self.current_goal = None
        self.goal_timer = 0
        self.test_log = []
        self.action_cooldown = 0
        
        # AI decision rate limiting (10 FPS = 100ms between decisions)
        self.decision_rate_ms = 100  # Make decisions every 100ms
        self.last_decision_time = 0
        
        # Goals the AI can pursue (EXPANDED - full gameplay)
        self.goals = [
            # Combat & Leveling (high priority)
            "fight_enemies",      # Primary goal - combat and leveling
            "fight_enemies",      # Duplicate to increase weight
            "hunt_for_xp",        # Actively seek enemies to level up
            "test_magic",         # Test spell casting
            
            # Resource gathering (medium priority)
            "gather_sticks",      # Get weapons
            "gather_resources",   # Mine/forage/woodcut resources
            
            # Survival (medium priority)
            "manage_health",      # Use potions/visit temple when low HP
            "manage_stamina",     # Eat food when hungry
            "rest_at_inn",        # Sleep to recover HP/stamina
            
            # Economy (medium priority)
            "shop_for_gear",      # Buy better weapons/armor
            "sell_loot",          # Sell gathered materials for gold
            "use_bank",           # Deposit gold when rich
            
            # Quests (medium priority)
            "find_quests",        # Talk to NPCs to get quests
            "complete_quests",    # Work on active quest objectives
            "turn_in_quests",     # Return to quest givers
            
            # Crafting & Cooking (low priority)
            "craft_items",        # Craft weapons/armor/tools
            "cook_food",          # Cook at campfires
            
            # Exploration & Dungeons (low priority)
            "explore_world",      # Random wandering
            "visit_town",         # Visit towns
            "enter_dungeon",      # Find and enter dungeons
            "loot_dungeon",       # Clear dungeons for loot
            
            # Social (low priority)
            "talk_to_npcs",       # Build relationships
            "get_blessings",      # Visit temples
        ]
        
        # AI state tracking
        self.visited_towns = set()
        self.last_position = (0, 0)
        self.stuck_counter = 0
        self.goal_completion_count = {}
        self.sticks_collected = 0
        self.has_weapon = False
        self.last_level = 1
        self.kills_this_session = 0
        self.magic_uses = 0
        
        # Movement direction commitment
        self.current_direction = None
        self.direction_timer = 0
        
        # Combat state tracking
        self.in_combat = False
        self.combat_target = None  # The enemy we're currently fighting
        self.combat_lock_timer = 0  # How long to stay locked on target
        
        # Equipment state tracking
        self.gear_equipped_this_goal = False  # Only equip once per goal to prevent frame-by-frame checks
        
        # Health/Stamina tracking
        self.health_low_threshold = 0.3  # 30% HP = low
        self.stamina_low_threshold = 0.2  # 20% stamina = low
        self.last_hp = 100
        self.last_stamina = 100
        
        # Economy tracking
        self.gold_savings_target = 1000  # Try to save 1000+ gold
        self.items_to_sell = []  # Track items we want to sell
        
        # Quest tracking
        self.accepted_quests = {}  # {quest_id: quest_data}
        self.completed_quests = set()
        self.visited_npcs = set()
        
        # Dungeon tracking
        self.last_dungeon_entered = None
        self.dungeons_cleared = 0
        
        # Building tracking
        self.last_inn_visited = None
        self.last_shop_visited = None
        
    def toggle(self):
        """Toggle AI player on/off"""
        self.enabled = not self.enabled
        if self.enabled:
            self.log_action("AI Player ENABLED - Starting automated testing")
            self.select_new_goal()
        else:
            self.log_action("AI Player DISABLED")
        return self.enabled
    
    def create_character(self):
        """
        AI character creation with smart archetypes
        
        Returns:
            dict: {
                'race': Race object,
                'stats': dict of stat allocations,
                'skin_tone': tuple (r, g, b),
                'name': str
            }
        """
        from race_system import HUMAN, ELF, DWARF, ORC, HALFLING, TIEFLING
        
        # Define 6 archetypes with optimal race/stat combinations
        archetypes = {
            'warrior': {
                'race': ORC,
                'stats': {'strength': 3, 'agility': 2, 'intelligence': 0, 'charisma': 0, 'perception': 1, 'luck': 0},
                'description': 'Brutal melee fighter'
            },
            'mage': {
                'race': ELF,
                'stats': {'strength': 0, 'agility': 1, 'intelligence': 3, 'charisma': 1, 'perception': 1, 'luck': 0},
                'description': 'Magic specialist'
            },
            'rogue': {
                'race': HALFLING,
                'stats': {'strength': 0, 'agility': 3, 'intelligence': 0, 'charisma': 1, 'perception': 1, 'luck': 1},
                'description': 'Sneaky and lucky'
            },
            'tank': {
                'race': DWARF,
                'stats': {'strength': 2, 'agility': 0, 'intelligence': 0, 'charisma': 1, 'perception': 2, 'luck': 1},
                'description': 'Durable defender'
            },
            'diplomat': {
                'race': HUMAN,
                'stats': {'strength': 1, 'agility': 1, 'intelligence': 1, 'charisma': 2, 'perception': 1, 'luck': 0},
                'description': 'Balanced and social'
            },
            'wild': {
                'race': TIEFLING,
                'stats': {'strength': 1, 'agility': 1, 'intelligence': 2, 'charisma': 2, 'perception': 0, 'luck': 0},
                'description': 'Chaotic caster'
            }
        }
        
        # Randomly select an archetype
        archetype_name = random.choice(list(archetypes.keys()))
        archetype = archetypes[archetype_name]
        
        # Generate AI name based on archetype
        name = f"AI_{archetype_name.capitalize()}_{random.randint(100, 999)}"
        
        # Random skin tone (warm tones for visibility)
        skin_tone = (
            random.randint(180, 255),
            random.randint(150, 220),
            random.randint(120, 200)
        )
        
        self.log_action(f"🤖 Created character: {name} ({archetype_name}) - {archetype['description']}")
        self.log_action(f"   Race: {archetype['race'].name}, Stats: {archetype['stats']}")
        
        return {
            'race': archetype['race'],
            'stats': archetype['stats'],
            'skin_tone': skin_tone,
            'name': name
        }
    
    def log_action(self, message):
        """Log AI actions for testing analysis"""
        logger.info(f"[AI PLAYER] {message}")
        self.test_log.append(message)
        
        # Keep log from growing too large
        if len(self.test_log) > 100:
            self.test_log = self.test_log[-50:]
    
    def select_new_goal(self, player=None):
        """Choose a new goal to pursue based on player state"""
        # Smart goal selection based on player state
        if player:
            # SURVIVAL PRIORITY: If health/stamina critical, fix it immediately
            if player.health < player.max_health * 0.3:
                self.current_goal = "manage_health"
                self.goal_timer = 1800  # 30 seconds
                self.log_action(f"🚨 EMERGENCY: Health critical ({player.health}/{player.max_health}) - seeking healing!")
                return
            
            if player.stamina < player.max_stamina * 0.2:
                self.current_goal = "manage_stamina"
                self.goal_timer = 1800
                self.log_action(f"🚨 EMERGENCY: Stamina critical - seeking food!")
                return
            
            # ECONOMY PRIORITY: If rich, bank the gold
            if player.dubloons > 2000:
                self.current_goal = "use_bank"
                self.goal_timer = 3600
                self.log_action(f"💰 Depositing wealth (Gold: {player.dubloons})")
                return
            
            # MAINTENANCE PRIORITY: If gear damaged or stamina/health low, recover
            if player.health < player.max_health * 0.6:
                self.current_goal = "rest_at_inn"
                self.goal_timer = 3600
                self.log_action(f"🛏️ Time to rest (HP: {player.health}/{player.max_health})")
                return
            
            # GEAR PRIORITY: If no weapon and level > 5, shop for gear
            equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
            if not equipped_weapon and player.level > 5 and player.dubloons > 150:
                self.current_goal = "shop_for_gear"
                self.goal_timer = 3600
                self.log_action(f"⚔️ Need better gear (Level: {player.level}, Gold: {player.dubloons})")
                return
            
            # LOOT PRIORITY: If carrying lots of materials, sell them
            material_count = sum(player.inventory.get(m, 0) for m in ['wood', 'stone', 'iron', 'copper', 'leather'])
            if material_count > 20:
                self.current_goal = "sell_loot"
                self.goal_timer = 3600
                self.log_action(f"💸 Inventory full of loot ({material_count} items) - selling!")
                return
        
        # Normal goal selection with weights
        goal_weights = []
        for goal in self.goals:
            count = self.goal_completion_count.get(goal, 0)
            
            # Prioritize combat and XP goals
            if goal in ['fight_enemies', 'hunt_for_xp']:
                weight = max(5, 20 - count)  # Very high weight
            # Medium priority for survival and economy
            elif goal in ['manage_health', 'manage_stamina', 'rest_at_inn', 'shop_for_gear', 'sell_loot']:
                weight = max(3, 12 - count)  # Medium weight
            # Lower priority for exploration and quests
            elif goal in ['find_quests', 'complete_quests', 'turn_in_quests']:
                weight = max(2, 8 - count)
            # Low priority for other goals
            else:
                weight = max(1, 6 - count)
            
            goal_weights.append(weight)
        
        self.current_goal = random.choices(self.goals, weights=goal_weights)[0]
        self.goal_timer = 3600  # 60 seconds at 60fps - STAY COMMITTED TO GOALS!
        self.gear_equipped_this_goal = False  # Reset equipment flag for new goal
        self.log_action(f"🎯 New goal: {self.current_goal} (duration: 60s)")

    
    def update(self, dt, player, game_state):
        """
        Update AI player logic and return actions to execute
        
        Args:
            dt: Delta time
            player: Player object
            game_state: Dict with game state info (towns, enemies, time, etc.)
            
        Returns:
            dict: Actions to execute this frame
        """
        if not self.enabled:
            return {}
        
        # Rate limiting: Only make decisions at 10 FPS (every 100ms)
        import pygame
        current_time = pygame.time.get_ticks()
        time_since_last_decision = current_time - self.last_decision_time
        
        if time_since_last_decision < self.decision_rate_ms:
            # Not time for a new decision yet - return empty action
            return {}
        
        # Time for a new decision - update the timer
        self.last_decision_time = current_time
        
        # Decrease cooldowns
        if self.action_cooldown > 0:
            self.action_cooldown -= 1
        
        if self.direction_timer > 0:
            self.direction_timer -= 1
        
        if self.combat_lock_timer > 0:
            self.combat_lock_timer -= 1
        
        # PRIORITY: If in combat, handle combat exclusively until target is dead or we retreat
        if self.in_combat and self.combat_target is not None:
            # Check if our target is still alive
            enemies = game_state.get('enemies', [])
            target_alive = False
            for enemy in enemies:
                if enemy is self.combat_target and enemy.alive:
                    target_alive = True
                    break
            
            if not target_alive or self.combat_lock_timer <= 0:
                # Target is dead or we timed out - exit combat
                if not target_alive:
                    self.log_action(f"✅ Target defeated! Exiting combat mode")
                else:
                    self.log_action(f"⏱️ Combat timeout - re-evaluating")
                self.in_combat = False
                self.combat_target = None
                self.combat_lock_timer = 0
            else:
                # Continue fighting current target
                return self.execute_combat_on_target(player, game_state)
        
        # Decrease goal timer
        self.goal_timer -= 1
        if self.goal_timer <= 0:
            # Mark current goal as completed
            self.goal_completion_count[self.current_goal] = \
                self.goal_completion_count.get(self.current_goal, 0) + 1
            self.select_new_goal(player)  # Pass player for smart decision making
        
        # Check if stuck (not moving)
        current_pos = (player.x, player.y)
        world = game_state.get('world')
        
        # PRIORITY: Check if we're on a breakable tile and should break it
        # Do this BEFORE stuck detection so we break tiles instead of changing direction
        if world and self.action_cooldown == 0:
            result = self.check_and_break_tile(player, world)
            if result:
                # We found a breakable tile - reset stuck counter since we're actively working on it
                self.stuck_counter = 0
                return result
        
        # Now check if stuck (more lenient - allow time to work)
        if math.dist(current_pos, self.last_position) < 5:
            self.stuck_counter += 1
            if self.stuck_counter > 240:  # Stuck for 4 seconds - be patient!
                self.log_action("🚧 Stuck detected! Trying new direction")
                # Don't reset entire goal, just change direction
                self.current_direction = random.choice(['up', 'down', 'left', 'right'])
                self.direction_timer = 1200  # Commit to new direction for 20 seconds
                self.stuck_counter = 0
        else:
            self.stuck_counter = 0
        self.last_position = current_pos
        
        # Track leveling progress
        if player.level > self.last_level:
            self.log_action(f"🎉 LEVEL UP! Now level {player.level} (Kills: {self.kills_this_session})")
            self.last_level = player.level
        
        # Execute current goal
        actions = self.execute_goal(player, game_state)
        
        return actions
    
    def check_and_break_tile(self, player, world):
        """Check if near breakable tile and break it"""
        from config import Config
        tile_size = Config.TILE_SIZE
        
        # Convert player pixel position to tile grid coordinates
        tile_x = (int(player.x) // tile_size) * tile_size
        tile_y = (int(player.y) // tile_size) * tile_size
        
        # Define breakable tile types
        breakable_types = {'tree', 'bush', 'rock_group', 'mushroom_patch', 'grass'}
        
        # CHECK ALL 9 SURROUNDING TILES for breakable resources
        for dy in [-tile_size, 0, tile_size]:
            for dx in [-tile_size, 0, tile_size]:
                check_x = tile_x + dx
                check_y = tile_y + dy
                check_tile = world.get_tile(check_x, check_y)
                
                if check_tile and hasattr(check_tile, 'layers'):
                    obj = check_tile.layers.get('object')
                    ground = check_tile.layers.get('ground')
                    
                    # Check if there's a breakable tile
                    resource_type = obj if obj in breakable_types else (ground if ground in breakable_types else None)
                    
                    if resource_type:
                        # Found breakable tile - break it directly!
                        self.log_action(f"Found {resource_type} at tile ({check_x//tile_size}, {check_y//tile_size}) px ({check_x}, {check_y})")
                        self.action_cooldown = 10  # Very quick retry (reduced from 20)
                        return {'break_tile': True}  # Direct tile breaking, not space key
        
        return None
    
    def execute_goal(self, player, game_state):
        """Execute the current goal and return actions"""
        actions = {}
        
        if self.current_goal == "explore_world":
            actions = self.explore_world(player, game_state)
            
        elif self.current_goal == "visit_town":
            actions = self.visit_town(player, game_state)
            
        elif self.current_goal == "gather_sticks":
            actions = self.gather_sticks(player, game_state)
            
        elif self.current_goal == "fight_enemies":
            actions = self.fight_enemies(player, game_state)
            
        elif self.current_goal == "hunt_for_xp":
            actions = self.hunt_for_xp(player, game_state)
            
        elif self.current_goal == "test_magic":
            actions = self.test_magic(player, game_state)
            
        elif self.current_goal == "enter_building":
            actions = self.enter_building(player, game_state)
        
        # NEW GOAL HANDLERS
        elif self.current_goal == "manage_health":
            actions = self.manage_health(player, game_state)
            
        elif self.current_goal == "manage_stamina":
            actions = self.manage_stamina(player, game_state)
            
        elif self.current_goal == "rest_at_inn":
            actions = self.rest_at_inn(player, game_state)
            
        elif self.current_goal == "gather_resources":
            actions = self.gather_resources(player, game_state)
            
        elif self.current_goal == "shop_for_gear":
            actions = self.shop_for_gear(player, game_state)
            
        elif self.current_goal == "sell_loot":
            actions = self.sell_loot(player, game_state)
            
        elif self.current_goal == "use_bank":
            actions = self.use_bank(player, game_state)
            
        elif self.current_goal == "find_quests":
            actions = self.find_quests(player, game_state)
            
        elif self.current_goal == "complete_quests":
            actions = self.complete_quests(player, game_state)
            
        elif self.current_goal == "turn_in_quests":
            actions = self.turn_in_quests(player, game_state)
            
        elif self.current_goal == "craft_items":
            actions = self.craft_items(player, game_state)
            
        elif self.current_goal == "cook_food":
            actions = self.cook_food(player, game_state)
            
        elif self.current_goal == "enter_dungeon":
            actions = self.enter_dungeon(player, game_state)
            
        elif self.current_goal == "loot_dungeon":
            actions = self.loot_dungeon(player, game_state)
            
        elif self.current_goal == "talk_to_npcs":
            actions = self.talk_to_npcs(player, game_state)
            
        elif self.current_goal == "get_blessings":
            actions = self.get_blessings(player, game_state)
        
        return actions
    
    def explore_world(self, player, game_state):
        """Random exploration movement with direction commitment"""
        # If we have a committed direction and timer is active, keep going that way
        if self.direction_timer > 0 and self.current_direction:
            return {'move': self.current_direction}
        
        # Time to pick a new direction - commit for 20 seconds (1200 frames)
        self.current_direction = random.choice(['up', 'down', 'left', 'right'])
        self.direction_timer = 1200  # 20 seconds at 60fps - STAY COMMITTED!
        self.log_action(f"🧭 New exploration direction: {self.current_direction.upper()} (20s)")
        return {'move': self.current_direction}
    
    def visit_town(self, player, game_state):
        """Navigate to nearest unvisited town"""
        towns = game_state.get('towns', [])
        in_town = game_state.get('in_town', False)
        
        if in_town:
            current_town = game_state.get('current_town_name')
            if current_town:
                self.visited_towns.add(current_town)
                self.log_action(f"Arrived in town: {current_town}")
            return {'move': 'up'}  # Move around in town
        
        # Find nearest unvisited town
        nearest_town = None
        nearest_dist = float('inf')
        
        for town in towns:
            if town.name in self.visited_towns:
                continue
            dx = town.center_x - player.x
            dy = town.center_y - player.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_town = town
        
        if nearest_town:
            # Move toward town
            return self.move_toward(player, nearest_town.center_x, nearest_town.center_y)
        else:
            # All towns visited, pick random one
            if towns:
                target = random.choice(towns)
                return self.move_toward(player, target.center_x, target.center_y)
        
        return {}
    
    def test_curfew(self, player, game_state):
        """Test curfew enforcement by being in town at night"""
        in_town = game_state.get('in_town', False)
        current_hour = game_state.get('current_hour', 12)
        
        # Wait for nighttime (curfew hours: 17:00 - 02:00)
        if current_hour < 17 and current_hour > 2:
            self.log_action(f"Waiting for curfew hours (current: {current_hour}:00)")
            return {'move': 'up'}  # Just move around
        
        if not in_town:
            # Go to nearest town
            towns = game_state.get('towns', [])
            if towns:
                target = random.choice(towns)
                self.log_action(f"Heading to {target.name} to test curfew")
                return self.move_toward(player, target.center_x, target.center_y)
        else:
            # In town during curfew - walk around to test guard detection
            self.log_action(f"Testing curfew enforcement at {current_hour}:00")
            direction = random.choice(['up', 'down', 'left', 'right'])
            return {'move': direction}
        
        return {}
    
    def visit_jail(self, player, game_state):
        """Navigate to the jail building"""
        jail_building = game_state.get('jail_building')
        
        if jail_building:
            # Move toward jail
            dx = jail_building.x - player.x
            dy = jail_building.y - player.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 100:
                self.log_action(f"Arrived at jail! Distance: {dist:.0f}")
                # Try to enter
                if self.action_cooldown == 0:
                    self.action_cooldown = 30
                    return {'press_key': 'e'}
            else:
                self.log_action(f"Heading to jail (distance: {dist:.0f})")
                return self.move_toward(player, jail_building.x, jail_building.y)
        
        return {}
    
    def gather_sticks(self, player, game_state):
        """Gather sticks from trees and equip them"""
        gathering_nodes = game_state.get('gathering_nodes', [])
        
        # Check if we have sticks in inventory and need to equip them
        stick_count = player.inventory.get('stick', 0)
        if stick_count > 0 and not self.has_weapon:
            # Directly equip sticks programmatically instead of opening inventory
            if self.action_cooldown == 0:
                self.log_action(f"Auto-equipping {stick_count} sticks as weapon")
                self.action_cooldown = 60
                self.has_weapon = True
                
                # Create a stick weapon and equip it
                from item import Item
                stick_weapon = Item(
                    name=f"Stick Bundle ({stick_count})",
                    item_type="weapon",
                    stats={'damage': 5 + stick_count * 2}  # Damage scales with stick count
                )
                player.equip(stick_weapon, 'weapon')
                self.log_action(f"Equipped stick weapon (DMG: {stick_weapon.stats['damage']})")
                return {}  # Continue with current goal
        
        # Find nearest tree to gather sticks from
        # Import NodeType enum
        try:
            from gathering_nodes import NodeType
            tree_nodes = [n for n in gathering_nodes if n.node_type == NodeType.WOODCUTTING]
        except:
            # Fallback if import fails
            tree_nodes = gathering_nodes
        
        if tree_nodes:
            # Find nearest tree
            nearest = min(tree_nodes, 
                         key=lambda n: math.dist((player.x, player.y), (n.x, n.y)))
            
            dx = nearest.x - player.x
            dy = nearest.y - player.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 50:  # Get close to tree (within attack range)
                # Try to break the tile directly
                if self.action_cooldown == 0:
                    self.log_action(f"Breaking tree directly (dist: {dist:.0f})")
                    self.action_cooldown = 20  # Quick retry for tile breaking
                    return {'break_tile': True}  # Direct tile breaking
                else:
                    # Wait for cooldown while staying in place
                    return {}  # Don't move while on cooldown
            else:
                self.log_action(f"🪵 Moving to tree (dist: {dist:.0f})")
                return self.move_toward(player, nearest.x, nearest.y)
        
        # No trees visible - explore with committed direction to find more
        self.log_action("🔍 No trees visible - exploring to find trees")
        return self.explore_world(player, game_state)
    
    def check_and_equip_best_gear(self, player):
        """Check inventory for any unequipped weapons/armor and equip the best available"""
        from item import Item
        
        equipped_something = False
        items_in_inventory = player.inventory.get('items', [])
        
        if not items_in_inventory:
            return False
        
        # Define equipment slots and their priorities
        equipment_slots = {
            'weapon': None,
            'armor': None,
            'accessory': None,
            'main_hand': None,
            'off_hand': None,
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
        }
        
        # Find best item for each slot from inventory
        for item in items_in_inventory:
            if not isinstance(item, Item) or item.is_broken():
                continue
            
            item_type = item.type.lower()
            
            # Map item types to equipment slots
            slot = None
            if item_type in ['weapon', 'sword', 'axe', 'bow', 'staff']:
                slot = 'weapon'
            elif item_type in ['armor', 'chest', 'chestplate']:
                slot = 'armor'
            elif item_type in ['accessory', 'ring', 'amulet', 'necklace']:
                slot = 'accessory'
            elif item_type in ['helmet', 'head']:
                slot = 'head'
            elif item_type == 'legs':
                slot = 'legs'
            elif item_type == 'feet':
                slot = 'feet'
            elif item_type == 'shield':
                slot = 'off_hand'
            
            if not slot:
                continue
            
            # Calculate item value (damage + defense + other stats)
            item_value = 0
            if hasattr(item, 'damage'):
                item_value += item.damage
            if hasattr(item, 'stats'):
                item_value += item.stats.get('damage', 0)
                item_value += item.stats.get('defense', 0)
                item_value += item.stats.get('attack', 0)
            
            # Keep track of best item for this slot
            if equipment_slots[slot] is None:
                equipment_slots[slot] = (item, item_value)
            else:
                current_best_value = equipment_slots[slot][1]
                if item_value > current_best_value:
                    equipment_slots[slot] = (item, item_value)
        
        # Now equip the best items if they're better than what we have
        for slot, item_data in equipment_slots.items():
            if item_data is None:
                continue
            
            best_item, best_value = item_data
            current_item = player.equipment.get(slot)
            
            # Calculate current item value
            current_value = 0
            if current_item:
                if hasattr(current_item, 'damage'):
                    current_value += current_item.damage
                if hasattr(current_item, 'stats'):
                    current_value += current_item.stats.get('damage', 0)
                    current_value += current_item.stats.get('defense', 0)
                    current_value += current_item.stats.get('attack', 0)
            
            # Equip if slot is empty OR new item is better
            if current_item is None or best_value > current_value:
                try:
                    player.equip(best_item, slot)
                    equipped_something = True
                    self.log_action(f"⚔️ EQUIPPED {best_item.name} to {slot} slot (value: {best_value})")
                except Exception as e:
                    self.log_action(f"❌ Failed to equip {best_item.name}: {e}")
        
        return equipped_something
    
    def fight_enemies(self, player, game_state):
        """Engage enemies for combat and leveling"""
        enemies = game_state.get('enemies', [])
        
        # PRIORITY: Check inventory and equip gear ONCE per goal (not every frame!)
        if not self.gear_equipped_this_goal:
            self.check_and_equip_best_gear(player)
            self.gear_equipped_this_goal = True
        
        # If already in combat with a valid target, stay locked on it - DON'T re-select!
        if self.in_combat and self.combat_target and self.combat_target.alive:
            return self.execute_combat_on_target(player, game_state)
        
        # Check if we have ANY combat capability
        equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
        has_magic = (hasattr(player, 'primary_spell') and player.primary_spell) or \
                    (hasattr(player, 'secondary_spell') and player.secondary_spell)
        has_sticks = player.inventory.get('stick', 0) > 0
        
        # MUST have weapon OR magic to fight
        if not equipped_weapon and not has_magic:
            if has_sticks:
                # We have sticks but need to equip them
                self.log_action("🪵 No weapon equipped! Need to equip sticks first")
                return self.gather_sticks(player, game_state)
            else:
                # No weapon and no sticks - must gather sticks first
                self.log_action("⚠️ UNARMED! Cannot fight without weapon or magic - gathering sticks")
                return self.gather_sticks(player, game_state)
        
        # Calculate player damage
        player_damage = 20 + (player.level * 5)  # Base damage
        if equipped_weapon:
            if hasattr(equipped_weapon, 'damage'):
                player_damage += equipped_weapon.damage
            elif hasattr(equipped_weapon, 'stats') and 'damage' in equipped_weapon.stats:
                player_damage += int(equipped_weapon.stats['damage'])
        
        if enemies:
            # Find nearest enemy we can fight (more aggressive)
            target = None
            target_dist = float('inf')
            
            for enemy in enemies:
                if not enemy.alive:
                    continue
                    
                # More aggressive: fight if we have >30% HP and some damage
                if player.health > player.max_health * 0.3 and player_damage > 5:
                    dx = enemy.rect.centerx - player.x
                    dy = enemy.rect.centery - player.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < target_dist:
                        target_dist = dist
                        target = enemy
            
            if target:
                # ENTER COMBAT MODE - Lock onto this target and COMMIT
                if not self.in_combat or self.combat_target is not target:
                    self.in_combat = True
                    self.combat_target = target
                    self.combat_lock_timer = 1800  # Lock for 30 seconds - STAY COMMITTED!
                    self.log_action(f"🎯 ENGAGING COMBAT with {target.type}! (Locked for 30s)")
                
                # Execute combat on locked target
                return self.execute_combat_on_target(player, game_state)
            else:
                # No enemies in range - explore to find more
                return self.explore_world(player, game_state)
        else:
            # No enemies loaded - explore to find them
            return self.explore_world(player, game_state)
    
    def hunt_for_xp(self, player, game_state):
        """Actively hunt enemies to gain XP and level up"""
        enemies = game_state.get('enemies', [])
        
        # PRIORITY: Check inventory and equip gear ONCE per goal (not every frame!)
        if not self.gear_equipped_this_goal:
            self.check_and_equip_best_gear(player)
            self.gear_equipped_this_goal = True
        
        # If already in combat with a valid target, stay locked on it - DON'T re-select!
        if self.in_combat and self.combat_target and self.combat_target.alive:
            return self.execute_combat_on_target(player, game_state)
        
        # Check if we have ANY combat capability
        equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
        has_magic = (hasattr(player, 'primary_spell') and player.primary_spell) or \
                    (hasattr(player, 'secondary_spell') and player.secondary_spell)
        has_sticks = player.inventory.get('stick', 0) > 0
        
        # MUST have weapon OR magic to hunt
        if not equipped_weapon and not has_magic:
            if has_sticks:
                # We have sticks but need to equip them
                self.log_action("🪵 No weapon for hunting! Equipping sticks first")
                return self.gather_sticks(player, game_state)
            else:
                # No weapon and no sticks - must gather sticks first
                self.log_action("⚠️ UNARMED! Cannot hunt without weapon or magic - gathering sticks")
                return self.gather_sticks(player, game_state)
        
        # Calculate player combat stats
        player_damage = 20 + (player.level * 5)
        if equipped_weapon:
            if hasattr(equipped_weapon, 'damage'):
                player_damage += equipped_weapon.damage
            elif hasattr(equipped_weapon, 'stats') and 'damage' in equipped_weapon.stats:
                player_damage += int(equipped_weapon.stats['damage'])
        
        if enemies:
            # Find ALL nearby enemies (aggressive hunting)
            nearest_enemy = None
            nearest_dist = float('inf')
            
            for enemy in enemies:
                if not enemy.alive:
                    continue
                
                dx = enemy.rect.centerx - player.x
                dy = enemy.rect.centery - player.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Hunt anything within range if we have >20% HP
                if dist < 500 and player.health > player.max_health * 0.2:
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_enemy = enemy
            
            if nearest_enemy:
                # ENTER COMBAT MODE - Lock onto this target and COMMIT
                if not self.in_combat or self.combat_target is not nearest_enemy:
                    self.in_combat = True
                    self.combat_target = nearest_enemy
                    self.combat_lock_timer = 1800  # Lock for 30 seconds - STAY COMMITTED!
                    xp_potential = getattr(nearest_enemy, 'xp_reward', 10)
                    self.log_action(f"🎯 ENGAGING HUNT with {nearest_enemy.type} (+{xp_potential} XP)! (Locked for 30s)")
                
                # Execute combat on locked target
                return self.execute_combat_on_target(player, game_state)
            else:
                # No enemies in range - explore actively to find more
                self.log_action(f"🔍 Searching for enemies to hunt (Lvl {player.level}, XP: {player.xp})")
                return self.explore_world(player, game_state)
        else:
            # No enemies - explore to find spawn areas
            return self.explore_world(player, game_state)
    
    def execute_combat_on_target(self, player, game_state):
        """Execute combat actions on the locked combat target"""
        if not self.combat_target or not self.combat_target.alive:
            # Target is dead or invalid - exit combat
            self.in_combat = False
            self.combat_target = None
            return {}
        
        # Verify we still have combat capability (weapon OR magic)
        equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
        has_magic = (hasattr(player, 'primary_spell') and player.primary_spell) or \
                    (hasattr(player, 'secondary_spell') and player.secondary_spell)
        
        if not equipped_weapon and not has_magic:
            # Lost our weapon/magic during combat - disengage!
            self.log_action(f"⚠️ UNARMED in combat! Disengaging from {self.combat_target.type}")
            self.in_combat = False
            self.combat_target = None
            # Try to get a weapon
            if player.inventory.get('stick', 0) > 0:
                return self.gather_sticks(player, game_state)
            else:
                return self.gather_sticks(player, game_state)
        
        target = self.combat_target
        
        # Calculate distance to target
        dx = target.rect.centerx - player.x
        dy = target.rect.centery - player.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Set facing direction based on target position (ALWAYS before attacking)
        if abs(dx) > abs(dy):
            # Target is more to left/right
            if dx > 0:
                player.facing_direction = 'right'
            else:
                player.facing_direction = 'left'
        else:
            # Target is more up/down
            if dy > 0:
                player.facing_direction = 'down'
            else:
                player.facing_direction = 'up'
        
        # Calculate player damage
        player_damage = 20 + (player.level * 5)
        equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
        if equipped_weapon:
            if hasattr(equipped_weapon, 'damage'):
                player_damage += equipped_weapon.damage
            elif hasattr(equipped_weapon, 'stats') and 'damage' in equipped_weapon.stats:
                player_damage += int(equipped_weapon.stats['damage'])
        
        # Check if we should retreat
        if player.health < player.max_health * 0.2:
            self.log_action(f"🚨 Low HP! Retreating from {target.type}")
            self.in_combat = False
            self.combat_target = None
            # Move away from enemy
            return {'move': 'left' if dx > 0 else 'right'}
        
        # Combat logic
        if dist < 120:
            # In attack range
            if equipped_weapon:
                # Use weapon for melee combat
                if self.action_cooldown == 0:
                    weapon_name = getattr(equipped_weapon, 'name', 'weapon')
                    self.log_action(f"⚔️ ATTACKING {target.type} with {weapon_name} (Dist: {dist:.0f}, DMG: {player_damage}, HP: {player.health}/{player.max_health})")
                    self.action_cooldown = 15  # Slightly faster attacks
                    self.kills_this_session += 1
                    return {'press_key': 'space'}
                else:
                    # Waiting for cooldown - maintain position and facing
                    return {}
            elif has_magic and dist < 300:
                # Use magic if we have it (longer range)
                if self.action_cooldown == 0:
                    spell_name = player.secondary_spell if (hasattr(player, 'secondary_spell') and player.secondary_spell) else player.primary_spell
                    self.log_action(f"✨ CASTING {spell_name} at {target.type} (Dist: {dist:.0f}, HP: {player.health}/{player.max_health})")
                    self.action_cooldown = 30  # Magic has longer cooldown
                    self.magic_uses += 1
                    return {'press_key': 'right_click'}
                else:
                    # Waiting for cooldown
                    return {}
            else:
                # No valid combat method - shouldn't happen but retreat just in case
                self.log_action(f"⚠️ No combat method available!")
                self.in_combat = False
                self.combat_target = None
                return {}
        else:
            # Move toward target - with direction commitment to prevent jitter
            return self.move_toward(player, target.rect.centerx, target.rect.centery, commit=True)
    
    def test_magic(self, player, game_state):
        """Test magic spell casting"""
        enemies = game_state.get('enemies', [])
        
        # Check if player has magic spells equipped
        has_primary = hasattr(player, 'primary_spell') and player.primary_spell
        has_secondary = hasattr(player, 'secondary_spell') and player.secondary_spell
        
        if not has_primary and not has_secondary:
            self.log_action("⚠️ No spells equipped - skipping magic test")
            return self.fight_enemies(player, game_state)
        
        # Find target for magic
        if enemies:
            target = None
            target_dist = float('inf')
            
            for enemy in enemies:
                if not enemy.alive:
                    continue
                
                dx = enemy.rect.centerx - player.x
                dy = enemy.rect.centery - player.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Magic has longer range
                if dist < 300 and dist < target_dist:
                    target_dist = dist
                    target = enemy
            
            if target:
                # Determine direction to enemy and set facing before casting
                dx = target.rect.centerx - player.x
                dy = target.rect.centery - player.y
                
                # Set facing direction based on enemy position
                if abs(dx) > abs(dy):
                    # Enemy is more to left/right
                    if dx > 0:
                        player.facing_direction = 'right'
                    else:
                        player.facing_direction = 'left'
                else:
                    # Enemy is more up/down
                    if dy > 0:
                        player.facing_direction = 'down'
                    else:
                        player.facing_direction = 'up'
                
                # Cast spell at enemy
                if self.action_cooldown == 0:
                    spell_name = player.secondary_spell if has_secondary else player.primary_spell
                    self.log_action(f"✨ Casting {spell_name} at {target.type} (dist: {target_dist:.0f})")
                    self.action_cooldown = 30  # Spell cooldown
                    self.magic_uses += 1
                    
                    # Right-click for secondary spell (magic attack)
                    return {'press_key': 'right_click'}
                else:
                    # Move to casting range - commit to direction to prevent jitter
                    if target_dist > 200:
                        return self.move_toward(player, target.rect.centerx, target.rect.centery, commit=True)
                    else:
                        # In range, just wait for cooldown
                        return {}
        
        # No targets - find enemies
        return self.hunt_for_xp(player, game_state)
    
    def enter_building(self, player, game_state):
        """Test entering buildings"""
        in_town = game_state.get('in_town', False)
        in_building = game_state.get('in_building_interior', False)
        
        if in_building:
            # Exit building
            if self.action_cooldown == 0:
                self.log_action("Exiting building")
                self.action_cooldown = 60
                return {'press_key': 'f'}
        elif in_town:
            # Move around town to find building entrance
            if self.action_cooldown == 0:
                self.action_cooldown = 30
                return {'press_key': 'e'}
            return {'move': random.choice(['up', 'down', 'left', 'right'])}
        else:
            # Go to town first
            return self.visit_town(player, game_state)
        
        return {}
    
    def test_shops(self, player, game_state):
        """Test shop interactions"""
        in_building = game_state.get('in_building_interior', False)
        
        if in_building:
            # Try to interact with NPCs
            if self.action_cooldown == 0:
                self.log_action("Attempting shop interaction")
                self.action_cooldown = 60
                return {'press_key': 'e'}
        else:
            # Enter a building first
            return self.enter_building(player, game_state)
        
        return {}
    
    def move_toward(self, player, target_x, target_y, commit=False):
        """Calculate movement direction toward target with optional direction commitment
        
        Args:
            player: The player entity
            target_x: Target X coordinate
            target_y: Target Y coordinate  
            commit: If True, commits to direction for 5 seconds to prevent jitter
        """
        # If we have a committed direction and timer is still active, use it!
        if commit and self.direction_timer > 0 and self.current_direction:
            return {'move': self.current_direction}
        
        dx = target_x - player.x
        dy = target_y - player.y
        
        # Choose dominant direction (favor larger delta)
        if abs(dx) > abs(dy):
            if dx > 0:
                chosen_direction = 'right'
            else:
                chosen_direction = 'left'
        else:
            if dy > 0:
                chosen_direction = 'down'
            else:
                chosen_direction = 'up'
        
        # If commit mode, lock this direction for 5 seconds to prevent jitter
        if commit:
            self.current_direction = chosen_direction
            self.direction_timer = 300  # 5 seconds - commit to this direction!
            
        return {'move': chosen_direction}
    
    # ===== NEW GOAL METHODS FOR EXPANDED GAMEPLAY =====
    
    def manage_health(self, player, game_state):
        """Use potions or visit temple when health is low"""
        # Check if we have health potions in inventory
        potion_count = player.inventory.get('health_potion', 0) or player.inventory.get('potion', 0)
        
        if potion_count > 0 and player.health < player.max_health * 0.5:
            # Use health potion
            if self.action_cooldown == 0:
                self.log_action(f"🧪 Using health potion (Current HP: {player.health}/{player.max_health})")
                self.action_cooldown = 30
                return {'press_key': 'i'}  # Open inventory, would need to press on potion
            return {}
        
        # Otherwise go to temple
        in_town = game_state.get('in_town', False)
        if not in_town:
            self.log_action(f"🏥 Going to temple for healing (HP: {player.health}/{player.max_health})")
            return self.visit_town(player, game_state)
        
        # In town - move toward temple
        return {'move': random.choice(['up', 'down', 'left', 'right'])}
    
    def manage_stamina(self, player, game_state):
        """Eat food when stamina is low"""
        # Check for food in inventory
        food_items = ['bread', 'meat', 'fruit', 'cooked_meat', 'berries']
        has_food = any(player.inventory.get(item, 0) > 0 for item in food_items)
        
        if has_food and player.stamina < player.max_stamina * 0.3:
            if self.action_cooldown == 0:
                self.log_action(f"🍖 Eating food (Stamina: {player.stamina}/{player.max_stamina})")
                self.action_cooldown = 30
                return {'press_key': 'i'}  # Open inventory
            return {}
        
        # No food, go to town to buy some
        in_town = game_state.get('in_town', False)
        if not in_town:
            return self.visit_town(player, game_state)
        
        return {'move': random.choice(['up', 'down', 'left', 'right'])}
    
    def rest_at_inn(self, player, game_state):
        """Rest at inn to recover HP and stamina"""
        in_town = game_state.get('in_town', False)
        in_building = game_state.get('in_building_interior', False)
        building_type = game_state.get('current_building_type')
        
        if in_building and 'inn' in str(building_type).lower():
            # In inn - rest
            if self.action_cooldown == 0:
                self.log_action(f"🛏️ Resting at inn (HP: {player.health}/{player.max_health})")
                self.action_cooldown = 60
                return {'press_key': 'e'}  # Interact with innkeeper
            return {}
        elif in_town:
            # In town - find inn
            return {'move': random.choice(['up', 'down', 'left', 'right'])}
        else:
            # Go to town
            return self.visit_town(player, game_state)
    
    def gather_resources(self, player, game_state):
        """Gather various resources (mining, foraging, woodcutting)"""
        # Similar to gather_sticks but for all resources
        gathering_nodes = game_state.get('gathering_nodes', [])
        
        if gathering_nodes:
            nearest = min(gathering_nodes, 
                         key=lambda n: math.dist((player.x, player.y), (n.x, n.y)))
            dx = nearest.x - player.x
            dy = nearest.y - player.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 50:
                if self.action_cooldown == 0:
                    self.log_action(f"⛏️ Gathering resources (dist: {dist:.0f})")
                    self.action_cooldown = 20
                    return {'break_tile': True}
            else:
                return self.move_toward(player, nearest.x, nearest.y)
        
        return self.explore_world(player, game_state)
    
    def shop_for_gear(self, player, game_state):
        """Buy better weapons and armor from shops"""
        in_town = game_state.get('in_town', False)
        in_building = game_state.get('in_building_interior', False)
        building_type = game_state.get('current_building_type')
        
        # Check if we have enough gold for gear
        if player.dubloons < 100:
            self.log_action(f"💰 Not enough gold for gear (Have: {player.dubloons})")
            return self.sell_loot(player, game_state)
        
        if in_building and ('shop' in str(building_type).lower() or 'blacksmith' in str(building_type).lower()):
            # In shop - buy gear
            if self.action_cooldown == 0:
                self.log_action(f"🛒 Browsing shop (Gold: {player.dubloons})")
                self.action_cooldown = 60
                return {'press_key': 'e'}  # Interact with shopkeeper
            return {}
        elif in_town:
            # In town - find shop
            return {'move': random.choice(['up', 'down', 'left', 'right'])}
        else:
            # Go to town
            return self.visit_town(player, game_state)
    
    def sell_loot(self, player, game_state):
        """Sell gathered materials and junk for gold"""
        in_town = game_state.get('in_town', False)
        in_building = game_state.get('in_building_interior', False)
        building_type = game_state.get('current_building_type')
        
        # Check if we have items to sell
        items_to_sell = ['wood', 'stick', 'stone', 'iron', 'copper', 'leather', 'herb']
        has_sellable = any(player.inventory.get(item, 0) > 0 for item in items_to_sell)
        
        if not has_sellable:
            self.log_action("📦 No items to sell")
            return self.gather_resources(player, game_state)
        
        if in_building and 'shop' in str(building_type).lower():
            # In shop - sell items
            if self.action_cooldown == 0:
                self.log_action(f"💸 Selling loot (Gold: {player.dubloons})")
                self.action_cooldown = 60
                return {'press_key': 'e'}  # Interact with merchant
            return {}
        elif in_town:
            return {'move': random.choice(['up', 'down', 'left', 'right'])}
        else:
            return self.visit_town(player, game_state)
    
    def use_bank(self, player, game_state):
        """Deposit gold at bank when we have lots of it"""
        in_town = game_state.get('in_town', False)
        in_building = game_state.get('in_building_interior', False)
        building_type = game_state.get('current_building_type')
        
        # Only bank if we have over 2000 gold
        if player.dubloons < 2000:
            return self.hunt_for_xp(player, game_state)
        
        if in_building and 'bank' in str(building_type).lower():
            # In bank - deposit
            if self.action_cooldown == 0:
                self.log_action(f"🏦 Depositing gold (Have: {player.dubloons})")
                self.action_cooldown = 60
                return {'press_key': 'e'}  # Interact with banker
            return {}
        elif in_town:
            return {'move': random.choice(['up', 'down', 'left', 'right'])}
        else:
            return self.visit_town(player, game_state)
    
    def find_quests(self, player, game_state):
        """Talk to NPCs to find quests"""
        in_town = game_state.get('in_town', False)
        in_building = game_state.get('in_building_interior', False)
        
        if in_building:
            # In building - talk to NPCs
            if self.action_cooldown == 0:
                self.log_action("💬 Talking to NPC for quests")
                self.action_cooldown = 60
                return {'press_key': 'e'}  # Talk to NPC
            return {}
        elif in_town:
            return {'move': random.choice(['up', 'down', 'left', 'right'])}
        else:
            return self.visit_town(player, game_state)
    
    def complete_quests(self, player, game_state):
        """Work on active quest objectives"""
        # Get quest data from game_state
        active_quests = game_state.get('active_quests', [])
        
        if not active_quests:
            self.log_action("📋 No active quests - finding new ones")
            return self.find_quests(player, game_state)
        
        # Pick first active quest
        quest = active_quests[0] if isinstance(active_quests, list) else active_quests.get('current')
        
        if quest:
            self.log_action(f"🎯 Working on quest: {quest.get('name', 'Unknown')}")
            # AI should move toward quest objectives
            return self.hunt_for_xp(player, game_state)
        
        return self.explore_world(player, game_state)
    
    def turn_in_quests(self, player, game_state):
        """Return to quest givers to complete quests"""
        in_town = game_state.get('in_town', False)
        in_building = game_state.get('in_building_interior', False)
        
        completed_quests = game_state.get('completed_quests', [])
        
        if not completed_quests:
            return self.find_quests(player, game_state)
        
        if in_building:
            # Talk to quest giver
            if self.action_cooldown == 0:
                self.log_action("✅ Turning in quest")
                self.action_cooldown = 60
                return {'press_key': 'e'}
            return {}
        elif in_town:
            return {'move': random.choice(['up', 'down', 'left', 'right'])}
        else:
            return self.visit_town(player, game_state)
    
    def craft_items(self, player, game_state):
        """Craft weapons, armor, and tools"""
        # Check if we have crafting materials
        craft_materials = ['wood', 'stone', 'iron', 'copper', 'fiber']
        has_materials = any(player.inventory.get(m, 0) > 0 for m in craft_materials)
        
        if not has_materials:
            self.log_action("📦 No craft materials - gathering resources")
            return self.gather_resources(player, game_state)
        
        # Find campfire or crafting station
        self.log_action(f"🔨 Crafting items (Mats: {sum(player.inventory.get(m, 0) for m in craft_materials)})")
        
        if self.action_cooldown == 0:
            self.action_cooldown = 60
            return {'press_key': 'c'}  # Craft menu
        
        return {}
    
    def cook_food(self, player, game_state):
        """Cook food at campfires"""
        # Check for raw materials
        raw_materials = ['meat', 'fish', 'mushroom', 'herb']
        has_raw = any(player.inventory.get(m, 0) > 0 for m in raw_materials)
        
        if not has_raw:
            return self.gather_resources(player, game_state)
        
        self.log_action("🍳 Cooking food")
        
        if self.action_cooldown == 0:
            self.action_cooldown = 60
            return {'press_key': 'space'}  # Interact with campfire
        
        return {}
    
    def enter_dungeon(self, player, game_state):
        """Find and enter dungeons"""
        # Look for dungeons in game state
        dungeons = game_state.get('dungeons', [])
        
        if dungeons:
            nearest = min(dungeons, key=lambda d: math.dist((player.x, player.y), (d.get('x', 0), d.get('y', 0))))
            dx = nearest.get('x', 0) - player.x
            dy = nearest.get('y', 0) - player.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 80:
                if self.action_cooldown == 0:
                    self.log_action(f"🚪 Entering dungeon")
                    self.action_cooldown = 60
                    return {'press_key': 'e'}  # Enter dungeon
                return {}
            else:
                self.log_action(f"🗺️ Moving to dungeon (dist: {dist:.0f})")
                return self.move_toward(player, nearest.get('x', 0), nearest.get('y', 0))
        
        # No dungeons - explore
        return self.explore_world(player, game_state)
    
    def loot_dungeon(self, player, game_state):
        """Clear dungeons and loot treasures"""
        in_dungeon = game_state.get('in_dungeon', False)
        
        if not in_dungeon:
            # Enter a dungeon first
            return self.enter_dungeon(player, game_state)
        
        # In dungeon - fight enemies and look for loot
        self.log_action("⚔️ Looting dungeon")
        return self.fight_enemies(player, game_state)
    
    def talk_to_npcs(self, player, game_state):
        """Build relationships with NPCs through dialogue"""
        in_building = game_state.get('in_building_interior', False)
        
        if in_building:
            if self.action_cooldown == 0:
                self.log_action("💬 Talking to NPC")
                self.action_cooldown = 60
                return {'press_key': 'e'}  # Talk to NPC
            return {}
        
        # Find NPCs in towns
        in_town = game_state.get('in_town', False)
        if not in_town:
            return self.visit_town(player, game_state)
        
        return self.enter_building(player, game_state)
    
    def get_blessings(self, player, game_state):
        """Visit temple for blessings and healing"""
        in_town = game_state.get('in_town', False)
        in_building = game_state.get('in_building_interior', False)
        building_type = game_state.get('current_building_type')
        
        if in_building and 'temple' in str(building_type).lower():
            # In temple - get blessing
            if self.action_cooldown == 0:
                self.log_action("⛪ Getting blessing from priest")
                self.action_cooldown = 60
                return {'press_key': 'e'}
            return {}
        elif in_town:
            return {'move': random.choice(['up', 'down', 'left', 'right'])}
        else:
            return self.visit_town(player, game_state)
    
    # ===== END NEW GOAL METHODS =====
    
    def get_status(self):
        """Get AI status for display"""
        if not self.enabled:
            return "AI: Disabled"
        
        weapon_status = "✓" if self.has_weapon else "✗"
        status = f"AI: {self.current_goal} | Lvl: {self.last_level} | Kills: {self.kills_this_session} | Weapon: {weapon_status}"
        
        # Add direction info when exploring
        if self.current_goal == "explore_world" and self.current_direction:
            dir_time = self.direction_timer // 60  # Convert frames to seconds
            status += f" | Dir: {self.current_direction.upper()} ({dir_time}s)"
        
        return status
    
    def get_recent_log(self, count=5):
        """Get recent log entries"""
        return self.test_log[-count:] if self.test_log else []

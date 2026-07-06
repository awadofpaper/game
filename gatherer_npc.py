"""
Gatherer NPC System - NPCs that gather resources, bank them, and compete with players
Phase 1: Basic gathering, banking, inventory management
Phase 2: Combat, dialogue, shopping (future)
"""

import pygame
import random
import math
from skills_system import SkillsManager, MINING_RESOURCES, WOODCUTTING_RESOURCES, FISHING_RESOURCES


class GathererType:
    """Types of gatherer NPCs"""
    MINER = "miner"
    WOODCUTTER = "woodcutter"
    FISHER = "fisher"


class GathererState:
    """States for gatherer NPC behavior"""
    IDLE = "idle"
    TRAVELING_TO_NODE = "traveling_to_node"
    GATHERING = "gathering"
    RETURNING_TO_BANK = "returning_to_bank"
    BANKING = "banking"
    RECOVERING = "recovering"  # Phase 2: After death


class GathererNPC:
    """NPC that gathers resources and acts like a player"""
    
    def __init__(self, name, x, y, gatherer_type, town, config):
        # SECURITY: Sanitize NPC name to prevent save corruption
        from utils import sanitize_name
        self.name = sanitize_name(name, max_length=32)
        self.x = x
        self.y = y
        self.gatherer_type = gatherer_type
        self.town = town  # Home town reference
        self.config = config
        self.world = None  # Set by main.py after initialization
        
        # Visual
        self.rect = pygame.Rect(int(x) - 16, int(y) - 16, 32, 32)
        self.color = self._get_type_color()
        
        # Skills system (same as player)
        self.skills_manager = SkillsManager()
        
        # Inventory system (28 slots, same as player)
        self.inventory = {}  # {item_name: count}
        self.inventory_slots = 28
        self.base_weight_capacity = 100  # Same as player
        self.current_weight = 0
        
        # Currency
        self.dubloons = random.randint(50, 200)  # Starting money
        
        # Gathering tool (start with bronze)
        self.tool = self._get_starting_tool()
        
        # Give NPCs spare tools in inventory for profession switching (30% chance)
        if random.random() < 0.3:
            spare_tools = ['bronze_pickaxe', 'bronze_axe', 'fishing_net']
            # Remove current tool from spare options
            spare_options = [t for t in spare_tools if t != self.tool]
            if spare_options and random.random() < 0.5:
                spare_tool = random.choice(spare_options)
                self.inventory[spare_tool] = 1
        
        # State machine
        self.state = GathererState.IDLE
        self.target_node = None
        self.gathering_progress = 0
        self.gathering_timer = 0
        self.is_training = False  # Profession switching training flag
        
        # Banking
        self.bank_manager = None  # Set by main.py
        self.home_bank = None  # Nearest bank in home town
        
        # Movement
        self.speed = 100  # pixels per second
        self.path_target_x = None
        self.path_target_y = None
        
        # Interaction
        self.interaction_radius = 80
        
        # Game time reference (set during update)
        self.game_time = None
        
        # Combat stats (Phase 2)
        self.level = random.randint(5, 15)  # Combat level
        self.max_health = random.randint(50, 100)
        self.health = self.max_health
        self.base_damage = random.randint(5, 15)
        self.alive = True
        self.last_attack_time = 0
        self.attack_cooldown = 1.0  # seconds between attacks
        self.attack_range = 40  # pixels
        
        # Combat targets
        self.combat_target = None  # Player or another NPC
        self.aggro_timer = 0  # Timer before attacking trespasser
        self.warned_player = False  # Has warned player to leave
        self.bribed_until = 0  # Game time when bribe expires
        
        # Equipment (Phase 2)
        self.weapon = None  # Can upgrade from shops
        self.armor = None
        
        # Recovery (Phase 2)
        self.is_recovering = False
        self.recovery_end_time = 0  # Total game hours when recovery ends
        self.respawn_x = x  # Where to respawn
        self.respawn_y = y
        
    def _get_type_color(self):
        """Get color based on gatherer type"""
        colors = {
            GathererType.MINER: (139, 90, 43),      # Brown for miners
            GathererType.WOODCUTTER: (34, 139, 34), # Forest green for woodcutters
            GathererType.FISHER: (65, 105, 225)     # Royal blue for fishers
        }
        return colors.get(self.gatherer_type, (150, 150, 150))
    
    def _get_starting_tool(self):
        """Get starting tool based on type"""
        tools = {
            GathererType.MINER: 'bronze_pickaxe',
            GathererType.WOODCUTTER: 'bronze_axe',
            GathererType.FISHER: 'fishing_net'
        }
        return tools.get(self.gatherer_type, 'bronze_pickaxe')
    
    def get_weight_capacity(self):
        """Calculate weight capacity (base 100, no stat bonuses for NPCs in Phase 1)"""
        # Phase 2: Add strength stat bonus
        return self.base_weight_capacity
    
    def get_current_weight(self):
        """Calculate current inventory weight (1 lb per item)"""
        total_weight = sum(self.inventory.values())
        return total_weight
    
    def can_carry_more(self, additional_weight=1):
        """Check if can carry more weight"""
        return (self.get_current_weight() + additional_weight) <= self.get_weight_capacity()
    
    def get_inventory_count(self):
        """Get number of different item types (not total count)"""
        return len([item for item, count in self.inventory.items() if count > 0])
    
    def is_inventory_full(self):
        """Check if inventory is full (28 slot limit or weight limit)"""
        return self.get_inventory_count() >= self.inventory_slots or not self.can_carry_more()
    
    def add_to_inventory(self, item_name, count=1):
        """Add item to inventory if there's space"""
        if not self.can_carry_more(count):
            return False
        
        if item_name not in self.inventory:
            self.inventory[item_name] = 0
        self.inventory[item_name] += count
        self.current_weight = self.get_current_weight()
        return True
    
    def find_nearest_node(self, gathering_nodes_manager):
        """Find nearest available node of appropriate type"""
        from gathering_nodes import NodeType, NodeState
        
        # Determine which node type to look for
        node_type_map = {
            GathererType.MINER: NodeType.MINING,
            GathererType.WOODCUTTER: NodeType.WOODCUTTING,
            GathererType.FISHER: NodeType.FISHING
        }
        target_node_type = node_type_map.get(self.gatherer_type)
        
        if not target_node_type:
            return None
        
        # Find all available nodes of the right type
        available_nodes = [
            node for node in gathering_nodes_manager.nodes
            if node.node_type == target_node_type 
            and node.state == NodeState.AVAILABLE
        ]
        
        if not available_nodes:
            return None
        
        # Find nearest
        nearest = None
        nearest_dist = float('inf')
        
        for node in available_nodes:
            dist = math.sqrt((node.x - self.x) ** 2 + (node.y - self.y) ** 2)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = node
        
        return nearest
    
    def find_home_bank(self):
        """Find nearest bank in home town"""
        from town_system import BuildingType
        
        if not self.town:
            return None
        
        for building in self.town.buildings:
            if building.type == BuildingType.BANK:
                return building
        
        return None
    
    def move_towards(self, target_x, target_y, dt):
        """Move towards a target position"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 5:
            return True  # Reached destination
        
        # Normalize and move
        if distance > 0:
            move_x = (dx / distance) * self.speed * dt
            move_y = (dy / distance) * self.speed * dt
            self.x += move_x
            self.y += move_y
            
            # Update rect
            self.rect.x = int(self.x) - 16
            self.rect.y = int(self.y) - 16
        
        return False
    
    def start_gathering(self, node):
        """Start gathering from a node"""
        from gathering_nodes import NodeState
        
        # Try to claim the node
        if node.state == NodeState.AVAILABLE:
            node.state = NodeState.BEING_GATHERED
            node.gatherer = self
            node.gather_start_time = pygame.time.get_ticks()
            
            self.target_node = node
            self.state = GathererState.GATHERING
            self.gathering_progress = 0
            self.gathering_timer = 0
            return True
        
        return False
    
    def update_gathering(self, dt, game_time):
        """Update gathering progress"""
        if not self.target_node or self.state != GathererState.GATHERING:
            return
        
        from gathering_nodes import NodeState
        from skills_system import MINING_RESOURCES, WOODCUTTING_RESOURCES, FISHING_RESOURCES
        
        # Check if node is still valid
        if self.target_node.state != NodeState.BEING_GATHERED or self.target_node.gatherer != self:
            # Someone else took it or it depleted
            self.state = GathererState.IDLE
            self.target_node = None
            return
        
        # Get resource data
        resource_type = self.target_node.resource_type
        resource_data = None
        skill_name = None
        
        if resource_type in MINING_RESOURCES:
            resource_data = MINING_RESOURCES[resource_type]
            skill_name = 'Mining'
        elif resource_type in WOODCUTTING_RESOURCES:
            resource_data = WOODCUTTING_RESOURCES[resource_type]
            skill_name = 'Woodcutting'
        elif resource_type in FISHING_RESOURCES:
            resource_data = FISHING_RESOURCES[resource_type]
            skill_name = 'Fishing'
        
        if not resource_data:
            self.state = GathererState.IDLE
            self.target_node = None
            return
        
        # Check level requirement
        if not self.skills_manager.can_perform_action(skill_name, resource_data['level']):
            # Can't gather this, find another node
            self.target_node.state = NodeState.AVAILABLE
            self.target_node.gatherer = None
            self.state = GathererState.IDLE
            self.target_node = None
            return
        
        # Calculate gather time (base 3 seconds, modified by tool speed)
        base_time = 3.0
        tool_speed = 1.0  # Phase 2: Get actual tool stats
        gather_time = base_time / tool_speed
        
        self.gathering_timer += dt
        self.gathering_progress = min(1.0, self.gathering_timer / gather_time)
        
        # Complete gathering
        if self.gathering_progress >= 1.0:
            self.complete_gathering(resource_type, resource_data['xp'], game_time)
    
    def complete_gathering(self, resource_type, xp_amount, game_time):
        """Complete gathering and add resource to inventory"""
        from gathering_nodes import NodeState
        from tile import Tile
        
        # Determine skill
        skill_name = None
        if resource_type in MINING_RESOURCES:
            skill_name = 'Mining'
        elif resource_type in WOODCUTTING_RESOURCES:
            skill_name = 'Woodcutting'
        elif resource_type in FISHING_RESOURCES:
            skill_name = 'Fishing'
        
        if skill_name:
            # Add XP
            levels_gained = self.skills_manager.add_xp(skill_name, xp_amount)
            
            # Add resource (raw fish for fishing)
            item_to_add = resource_type
            if skill_name == 'Fishing':
                item_to_add = f"raw_{resource_type}"
            
            # Try to add to inventory
            if self.add_to_inventory(item_to_add, 1):
                print(f"[NPC {self.name}] Gathered {item_to_add} (+{xp_amount} XP)")
            else:
                print(f"[NPC {self.name}] Inventory full!")
        
        # Mark node as depleted and remove tree tile if woodcutting
        if self.target_node:
            self.target_node.deplete(game_time.day_count)
            
            # Remove tree tile from world (same as when player breaks it)
            if skill_name == 'Woodcutting' and self.world:
                tile_x = int(self.target_node.x // 32)
                tile_y = int(self.target_node.y // 32)
                
                # Check if it's a tree and replace with grass
                current_tile = self.world.get_tile(tile_x, tile_y)
                if current_tile == Tile.TREE:
                    self.world.set_tile(tile_x, tile_y, Tile.GRASS)
        
        # Clear gathering state
        self.target_node = None
        self.state = GathererState.IDLE
        self.gathering_progress = 0
        self.gathering_timer = 0
    
    def deposit_resources_to_bank(self):
        """Deposit all gathered resources to bank"""
        if not self.bank_manager:
            return
        
        deposited_count = 0
        items_to_remove = []
        
        for item_name, count in self.inventory.items():
            if count > 0:
                # Try to deposit each item
                for _ in range(count):
                    if self.bank_manager.store_item(item_name):
                        deposited_count += 1
                    else:
                        break  # Bank full
                
                items_to_remove.append(item_name)
        
        # Clear deposited items
        for item_name in items_to_remove:
            self.inventory[item_name] = 0
        
        self.current_weight = self.get_current_weight()
        
        if deposited_count > 0:
            print(f"[NPC {self.name}] Deposited {deposited_count} items to bank")
    
    def take_damage(self, amount, attacker=None):
        """Take damage from combat"""
        if self.is_recovering:
            return  # Invulnerable during recovery
        
        self.health -= amount
        
        if self.health <= 0:
            self.health = 0
            self.die(attacker, self.game_time)
        else:
            # Fight back if attacked
            if attacker and not self.combat_target:
                self.combat_target = attacker
                self.state = GathererState.IDLE  # Stop gathering to fight
    
    def die(self, killer=None, game_time=None):
        """Handle NPC death"""
        print(f"[NPC {self.name}] Defeated by {killer.name if hasattr(killer, 'name') else 'enemy'}!")
        
        self.alive = False
        
        # Drop only gathered resources (NOT equipment, but keep tool)
        dropped_items = []
        for item_name, count in self.inventory.items():
            if count > 0:
                dropped_items.extend([item_name] * count)
        
        # Clear inventory
        self.inventory.clear()
        self.current_weight = 0
        
        # Schedule respawn (immediate but with 2-day recovery)
        self.respawn(game_time)
        
        return dropped_items
    
    def respawn(self, game_time=None):
        """Respawn immediately but in recovery state"""
        self.alive = True
        self.health = self.max_health
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.rect.x = int(self.x) - 16
        self.rect.y = int(self.y) - 16
        
        # Enter recovery state for 2 game days (48 hours)
        self.is_recovering = True
        if game_time:
            current_minutes = game_time.get_total_minutes()
            current_hours = current_minutes / 60.0
            self.recovery_end_time = current_hours + 48
        else:
            self.recovery_end_time = 48  # Will be set later
        
        self.state = GathererState.IDLE
        self.combat_target = None
        self.target_node = None
        
        print(f"[NPC {self.name}] Respawned in recovery mode (2 days)")
    
    def check_recovery_status(self, game_time):
        """Check if recovery period is over"""
        if self.is_recovering:
            current_minutes = game_time.get_total_minutes()
            current_hours = current_minutes / 60.0
            if current_hours >= self.recovery_end_time:
                self.is_recovering = False
                print(f"[NPC {self.name}] Recovery complete!")
    
    def get_damage(self):
        """Calculate total damage including weapon bonus"""
        damage = self.base_damage
        # Add weapon damage bonus
        if self.weapon:
            damage += self.weapon.get('damage', 0)
        return damage
    
    def attack_target(self, target, current_time):
        """Attack a target (player, NPC, or enemy)"""
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        # Check range
        distance = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        if distance > self.attack_range:
            return False
        
        # Deal damage
        damage = self.get_damage()
        if hasattr(target, 'take_damage'):
            target.take_damage(damage, attacker=self)
            print(f"[NPC {self.name}] Attacked {target.name if hasattr(target, 'name') else 'target'} for {damage} damage")
        
        self.last_attack_time = current_time
        return True
    
    def can_interact_with_player(self, player):
        """Check if player is close enough to interact"""
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance <= self.interaction_radius
    
    def is_bribed(self, game_time):
        """Check if NPC is currently bribed"""
        if self.bribed_until > 0:
            current_minutes = game_time.get_total_minutes()
            current_hours = current_minutes / 60.0
            return current_hours < self.bribed_until
        return False
    
    def should_shop_for_equipment(self):
        """Decide if NPC should shop for better equipment"""
        # Only shop if have enough money (300+ dubloons)
        if self.dubloons < 300:
            return False
        
        # Random chance to shop (10% per update cycle when idle)
        if random.random() < 0.1:
            return True
        
        return False
    
    def find_nearest_shop(self):
        """Find nearest shop in home town"""
        # Look for shops in home town
        if hasattr(self.town, 'shops'):
            nearest_shop = None
            nearest_dist = float('inf')
            
            for shop in self.town.shops:
                if shop.shop_type == "general_store":  # Only general stores sell equipment
                    dist = math.sqrt((shop.x - self.x) ** 2 + (shop.y - self.y) ** 2)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_shop = shop
            
            return nearest_shop
        return None
    
    def buy_equipment(self, shop):
        """Try to buy better equipment from shop"""
        if not shop or self.dubloons < 100:
            return False
        
        # Look for better weapon or armor
        # Skip unique/legendary items (player-only)
        affordable_items = []
        
        if hasattr(shop, 'inventory'):
            for item_name, item_data in shop.inventory.items():
                # Check if affordable
                price = item_data.get('price', 0)
                if price <= self.dubloons and price > 0:
                    # Check if it's equipment (not unique)
                    item_type = item_data.get('type', '')
                    rarity = item_data.get('rarity', 'common')
                    
                    if item_type in ['weapon', 'armor'] and rarity not in ['unique', 'legendary']:
                        # Check if better than current
                        if item_type == 'weapon' and (not self.weapon or item_data.get('damage', 0) > self.weapon.get('damage', 0)):
                            affordable_items.append((item_name, item_data, price))
                        elif item_type == 'armor' and (not self.armor or item_data.get('defense', 0) > self.armor.get('defense', 0)):
                            affordable_items.append((item_name, item_data, price))
        
        # Buy random affordable upgrade
        if affordable_items:
            item_name, item_data, price = random.choice(affordable_items)
            
            # Deduct money
            self.dubloons -= price
            
            # Equip item
            item_type = item_data.get('type')
            if item_type == 'weapon':
                self.weapon = item_data.copy()
                self.weapon['name'] = item_name
                print(f"[NPC {self.name}] Bought {item_name} for {price} dubloons")
            elif item_type == 'armor':
                self.armor = item_data.copy()
                self.armor['name'] = item_name
                print(f"[NPC {self.name}] Bought {item_name} for {price} dubloons")
            
            return True
        
        return False
    
    def find_enemy_npcs_nearby(self, all_npcs, max_distance=200):
        """Find other gatherer NPCs nearby that might be threats"""
        enemies = []
        
        for other_npc in all_npcs:
            if other_npc == self:
                continue
            
            # Check distance
            dist = math.sqrt((other_npc.x - self.x) ** 2 + (other_npc.y - self.y) ** 2)
            if dist <= max_distance:
                # Check if they're at "our" node
                if self.target_node and other_npc.target_node == self.target_node:
                    # Both want the same node - potential conflict
                    enemies.append(other_npc)
        
        return enemies
    
    def decide_npc_combat(self, other_npc):
        """Decide whether to attack another NPC for a node"""
        # Factors:
        # 1. Our combat level vs theirs
        # 2. Our health vs theirs
        # 3. Personality (aggressive NPCs more likely to fight)
        
        if self.is_recovering or other_npc.is_recovering:
            return False
        
        # Calculate "strength" scores
        our_strength = self.level + (self.health / self.max_health) * 10
        their_strength = other_npc.level + (other_npc.health / other_npc.max_health) * 10
        
        # Add weapon bonus
        if self.weapon:
            our_strength += self.weapon.get('damage', 0)
        if other_npc.weapon:
            their_strength += other_npc.weapon.get('damage', 0)
        
        # Aggressive NPCs fight more often
        aggression_bonus = 0
        if self.base_damage > 10:
            aggression_bonus = 5
        
        our_strength += aggression_bonus
        
        # Fight if we're significantly stronger (20% advantage)
        if our_strength > their_strength * 1.2:
            if random.random() < 0.3:  # 30% chance to actually initiate
                return True
        
        return False
    
    def update(self, dt, game_time, gathering_nodes_manager, all_npcs=None, player=None):
        """Main update loop for NPC AI"""
        
        # Store game_time reference for use in other methods
        self.game_time = game_time
        
        # Check warning timer (dialogue consequence warning system)
        if self.warned_player and self.aggro_timer > 0 and player:
            self.aggro_timer -= dt
            
            # Check distance to player
            distance_to_player = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
            tiles_away = distance_to_player / 32  # Convert pixels to tiles
            
            if self.aggro_timer <= 0:
                # Timer expired, check if player is still too close
                if tiles_away < 10:
                    # Player didn't leave, attack!
                    self.combat_target = player
                    self.warned_player = False
                    self.aggro_timer = 0
                    print(f"[GATHERER] {self.name} attacks player for not leaving!")
                else:
                    # Player left in time
                    self.warned_player = False
                    self.aggro_timer = 0
                    print(f"[GATHERER] {self.name} calms down - player left")
            elif tiles_away >= 10:
                # Player left early, cancel warning
                self.warned_player = False
                self.aggro_timer = 0
                print(f"[GATHERER] {self.name} warning canceled - player left early")
        
        # Check recovery status
        if self.is_recovering:
            self.check_recovery_status(game_time)
            return  # Don't do anything else while recovering
        
        # Combat AI (if has target)
        if self.combat_target:
            # Move towards target and attack
            if hasattr(self.combat_target, 'alive') and not self.combat_target.alive:
                self.combat_target = None
            elif hasattr(self.combat_target, 'health') and self.combat_target.health <= 0:
                self.combat_target = None
            else:
                # Move towards combat target
                distance = math.sqrt((self.x - self.combat_target.x) ** 2 + (self.y - self.combat_target.y) ** 2)
                if distance <= self.attack_range:
                    # In range, attack
                    import time
                    self.attack_target(self.combat_target, time.time())
                else:
                    # Move closer
                    self.move_towards(self.combat_target.x, self.combat_target.y, dt)
                return  # Don't do normal behavior while in combat
        
        # State machine
        if self.state == GathererState.IDLE:
            # Check if should shop for equipment
            if self.should_shop_for_equipment():
                shop = self.find_nearest_shop()
                if shop:
                    # Try to buy equipment
                    self.buy_equipment(shop)
            
            # Check if inventory is full
            if self.is_inventory_full():
                # Go bank resources
                self.state = GathererState.RETURNING_TO_BANK
                if not self.home_bank:
                    self.home_bank = self.find_home_bank()
            else:
                # Find a node to gather from
                nearest_node = self.find_nearest_node(gathering_nodes_manager)
                if nearest_node:
                    # Check for NPC competition at this node
                    if all_npcs:
                        competitors = self.find_enemy_npcs_nearby(all_npcs)
                        for competitor in competitors:
                            if competitor.target_node == nearest_node:
                                # Decide if we fight for this node
                                if self.decide_npc_combat(competitor):
                                    print(f"[NPC {self.name}] Challenging {competitor.name} for node!")
                                    self.combat_target = competitor
                                    return
                    
                    self.target_node = nearest_node
                    self.state = GathererState.TRAVELING_TO_NODE
                    self.path_target_x = nearest_node.x
                    self.path_target_y = nearest_node.y
        
        elif self.state == GathererState.TRAVELING_TO_NODE:
            if self.target_node and self.path_target_x and self.path_target_y:
                # Move towards node
                reached = self.move_towards(self.path_target_x, self.path_target_y, dt)
                
                if reached:
                    # Try to start gathering
                    if self.start_gathering(self.target_node):
                        # Successfully started
                        pass
                    else:
                        # Node taken, go back to idle
                        self.state = GathererState.IDLE
                        self.target_node = None
            else:
                self.state = GathererState.IDLE
        
        elif self.state == GathererState.GATHERING:
            self.update_gathering(dt, game_time)
        
        elif self.state == GathererState.RETURNING_TO_BANK:
            if self.home_bank:
                bank_x = self.home_bank.x + self.home_bank.width // 2
                bank_y = self.home_bank.y + self.home_bank.height // 2
                
                reached = self.move_towards(bank_x, bank_y, dt)
                
                if reached:
                    self.state = GathererState.BANKING
            else:
                # No bank, just dump resources (shouldn't happen)
                self.inventory.clear()
                self.current_weight = 0
                self.state = GathererState.IDLE
        
        elif self.state == GathererState.BANKING:
            # Deposit resources
            self.deposit_resources_to_bank()
            self.state = GathererState.IDLE
    
    def draw(self, screen, camera):
        """Draw the NPC"""
        # Calculate screen position
        screen_x = self.rect.x - camera.x
        screen_y = self.rect.y - camera.y
        
        # Grey out if recovering
        npc_color = self.color
        if self.is_recovering:
            # Greyed out appearance
            npc_color = tuple(c // 2 for c in self.color)
        
        # Draw body
        pygame.draw.rect(screen, npc_color, (screen_x, screen_y, 32, 32))
        
        # Draw tool indicator (small colored square)
        tool_color = (200, 200, 200)
        if self.gatherer_type == GathererType.MINER:
            tool_color = (180, 180, 180)  # Grey pickaxe
        elif self.gatherer_type == GathererType.WOODCUTTER:
            tool_color = (139, 69, 19)  # Brown axe
        elif self.gatherer_type == GathererType.FISHER:
            tool_color = (160, 82, 45)  # Sienna fishing rod
        
        pygame.draw.rect(screen, tool_color, (screen_x + 20, screen_y + 20, 8, 8))
        
        # Draw name label with cached font
        font = pygame.font.SysFont(None, 16)
        name_text = self.name
        if self.is_recovering:
            name_text += " (Recovering)"
        name_surf = font.render(name_text, True, (255, 255, 255))
        name_rect = name_surf.get_rect(center=(screen_x + 16, screen_y - 10))
        screen.blit(name_surf, name_rect)
        
        # Draw training indicator (book icon above head)
        if self.state == GathererState.IDLE and hasattr(self, 'is_training') and self.is_training:
            # Draw a small book icon
            book_x = screen_x + 12
            book_y = screen_y - 35
            pygame.draw.rect(screen, (255, 200, 100), (book_x, book_y, 8, 10))  # Book cover
            pygame.draw.line(screen, (100, 50, 0), (book_x + 4, book_y), (book_x + 4, book_y + 10), 1)  # Book spine
            # Draw "T" for training
            training_font = pygame.font.SysFont(None, 12)
            training_surf = training_font.render("T", True, (255, 255, 100))
            screen.blit(training_surf, (screen_x + 11, screen_y - 26))
        
        # Draw health bar (Phase 2)
        if not self.is_recovering and self.health < self.max_health:
            health_bar_width = 32
            health_bar_height = 4
            health_x = screen_x
            health_y = screen_y - 20
            
            # Background (red)
            pygame.draw.rect(screen, (200, 0, 0), (health_x, health_y, health_bar_width, health_bar_height))
            # Health (green)
            health_ratio = self.health / self.max_health
            health_width = int(health_bar_width * health_ratio)
            pygame.draw.rect(screen, (0, 200, 0), (health_x, health_y, health_width, health_bar_height))
        
        # Draw gathering progress bar
        if self.state == GathererState.GATHERING and self.gathering_progress > 0:
            bar_width = 32
            bar_height = 4
            bar_x = screen_x
            bar_y = screen_y + 34
            
            # Background
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Progress
            progress_width = int(bar_width * self.gathering_progress)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, progress_width, bar_height))


class GathererNPCManager:
    """Manages all gatherer NPCs in the world"""
    
    def __init__(self):
        self.npcs = []
    
    def spawn_gatherers_for_town(self, town, gathering_nodes_manager, config, max_gatherers=None):
        """Spawn gatherers for a town based on nearby terrain/nodes"""
        
        # Determine town specialization based on nearby nodes
        specialization = self._determine_town_specialization(town, gathering_nodes_manager)
        
        # Generate NPCs based on specialization
        npc_counts = self._get_npc_counts_for_specialization(specialization)
        
        # Apply max_gatherers limit if specified
        if max_gatherers is not None:
            # Reduce counts proportionally to fit within max_gatherers
            total = sum(npc_counts.values())
            if total > max_gatherers:
                # Keep only the dominant type(s) up to max_gatherers
                sorted_types = sorted(npc_counts.items(), key=lambda x: x[1], reverse=True)
                npc_counts = {}
                remaining = max_gatherers
                for gatherer_type, _ in sorted_types:
                    if remaining > 0:
                        npc_counts[gatherer_type] = 1
                        remaining -= 1
        
        npc_id = 0
        for gatherer_type, count in npc_counts.items():
            for i in range(count):
                # Spawn near town center with some randomness
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(50, 150)
                x = town.center_x + distance * math.cos(angle)
                y = town.center_y + distance * math.sin(angle)
                
                name = self._generate_npc_name(gatherer_type, npc_id)
                npc = GathererNPC(name, x, y, gatherer_type, town, config)
                self.npcs.append(npc)
                npc_id += 1
        
        print(f"[NPC] Spawned {len(npc_counts)} gatherers for {town.name}: {npc_counts}")
    
    def _determine_town_specialization(self, town, gathering_nodes_manager):
        """Determine town specialization based on nearby nodes"""
        from gathering_nodes import NodeType
        
        # Count nearby nodes within 500 pixels
        radius = 500
        node_counts = {
            NodeType.MINING: 0,
            NodeType.WOODCUTTING: 0,
            NodeType.FISHING: 0
        }
        
        for node in gathering_nodes_manager.nodes:
            dist = math.sqrt((node.x - town.center_x) ** 2 + (node.y - town.center_y) ** 2)
            if dist <= radius:
                node_counts[node.node_type] += 1
        
        # Determine specialization
        total_nodes = sum(node_counts.values())
        if total_nodes == 0:
            return "balanced"
        
        # If one type dominates (>50%), specialize in it
        for node_type, count in node_counts.items():
            if count / total_nodes > 0.5:
                if node_type == NodeType.MINING:
                    return "mining"
                elif node_type == NodeType.WOODCUTTING:
                    return "woodcutting"
                elif node_type == NodeType.FISHING:
                    return "fishing"
        
        return "balanced"
    
    def _get_npc_counts_for_specialization(self, specialization):
        """Get NPC counts based on specialization"""
        # Total: 4-9 NPCs per town
        total_npcs = random.randint(4, 9)
        
        if specialization == "mining":
            miners = min(random.randint(5, 7), total_npcs)
            remaining = max(0, total_npcs - miners)
            if remaining > 0:
                woodcutters = random.randint(0, remaining)
                fishers = remaining - woodcutters
            else:
                woodcutters = 0
                fishers = 0
            return {
                GathererType.MINER: miners,
                GathererType.WOODCUTTER: woodcutters,
                GathererType.FISHER: fishers
            }
        
        elif specialization == "woodcutting":
            woodcutters = min(random.randint(5, 7), total_npcs)
            remaining = max(0, total_npcs - woodcutters)
            if remaining > 0:
                miners = random.randint(0, remaining)
                fishers = remaining - miners
            else:
                miners = 0
                fishers = 0
            return {
                GathererType.MINER: miners,
                GathererType.WOODCUTTER: woodcutters,
                GathererType.FISHER: fishers
            }
        
        elif specialization == "fishing":
            fishers = min(random.randint(5, 7), total_npcs)
            remaining = max(0, total_npcs - fishers)
            if remaining > 0:
                miners = random.randint(0, remaining)
                woodcutters = remaining - miners
            else:
                miners = 0
                woodcutters = 0
            return {
                GathererType.MINER: miners,
                GathererType.WOODCUTTER: woodcutters,
                GathererType.FISHER: fishers
            }
        
        else:  # balanced
            # Distribute evenly
            miners = total_npcs // 3
            woodcutters = total_npcs // 3
            fishers = total_npcs - miners - woodcutters
            return {
                GathererType.MINER: miners,
                GathererType.WOODCUTTER: woodcutters,
                GathererType.FISHER: fishers
            }
    
    def _generate_npc_name(self, gatherer_type, npc_id):
        """Generate a name for the NPC"""
        first_names = ["Bob", "Alice", "John", "Emma", "Michael", "Sarah", "David", "Lisa", "Tom", "Jane"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Wilson", "Moore"]
        
        type_titles = {
            GathererType.MINER: "Miner",
            GathererType.WOODCUTTER: "Woodcutter",
            GathererType.FISHER: "Fisher"
        }
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        title = type_titles.get(gatherer_type, "Gatherer")
        
        return f"{first} the {title}"
    
    def update_all(self, dt, game_time, gathering_nodes_manager, player=None):
        """Update all gatherer NPCs"""
        for npc in self.npcs:
            npc.update(dt, game_time, gathering_nodes_manager, self.npcs, player)
    
    def draw_all(self, screen, camera):
        """Draw all gatherer NPCs"""
        for npc in self.npcs:
            npc.draw(screen, camera)
    
    def get_nearby_npc(self, x, y, max_distance=80):
        """Find nearest NPC within range"""
        nearest = None
        nearest_dist = max_distance
        
        for npc in self.npcs:
            dist = math.sqrt((npc.x - x) ** 2 + (npc.y - y) ** 2)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = npc
        
        return nearest

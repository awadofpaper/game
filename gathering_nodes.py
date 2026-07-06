"""
Gathering Nodes - Resource nodes for Mining, Woodcutting, and Fishing
"""

import pygame
import random
from enum import Enum

class NodeType(Enum):
    MINING = "mining"
    WOODCUTTING = "woodcutting"
    FISHING = "fishing"

class NodeState(Enum):
    AVAILABLE = "available"
    BEING_GATHERED = "being_gathered"
    DEPLETED = "depleted"

class GatheringNode:
    """A resource node that can be gathered from"""
    
    def __init__(self, x, y, node_type, resource_type, node_id):
        self.x = x
        self.y = y
        self.node_type = node_type  # NodeType enum
        self.resource_type = resource_type  # e.g., 'copper', 'oak_logs', 'shrimp'
        self.node_id = node_id  # Unique identifier
        
        self.state = NodeState.AVAILABLE
        self.gatherer = None  # Who is currently gathering (player or NPC)
        self.gather_progress = 0.0  # 0.0 to 1.0
        
        # Respawn tracking
        self.depleted_on_day = None
        self.respawn_days = self._get_respawn_days()
        self.base_respawn_days = self.respawn_days  # Store base for weather calculations
        
        # Visual
        self.color = self._get_color()
        self.size = 32
        self.pulse_timer = random.uniform(0, 3.14)  # For visual pulse effect
        
    def _get_respawn_days(self):
        """Get respawn time in game days for this resource"""
        from skills_system import MINING_RESOURCES, WOODCUTTING_RESOURCES, FISHING_RESOURCES
        
        if self.node_type == NodeType.MINING:
            return MINING_RESOURCES.get(self.resource_type, {}).get('respawn_days', 1)
        elif self.node_type == NodeType.WOODCUTTING:
            return WOODCUTTING_RESOURCES.get(self.resource_type, {}).get('respawn_days', 1)
        elif self.node_type == NodeType.FISHING:
            return FISHING_RESOURCES.get(self.resource_type, {}).get('respawn_days', 1)
        return 1
    
    def _get_color(self):
        """Get visual color for this resource"""
        from skills_system import MINING_RESOURCES, WOODCUTTING_RESOURCES, FISHING_RESOURCES
        
        if self.node_type == NodeType.MINING:
            return MINING_RESOURCES.get(self.resource_type, {}).get('color', (128, 128, 128))
        elif self.node_type == NodeType.WOODCUTTING:
            return WOODCUTTING_RESOURCES.get(self.resource_type, {}).get('color', (139, 90, 43))
        elif self.node_type == NodeType.FISHING:
            return FISHING_RESOURCES.get(self.resource_type, {}).get('color', (100, 149, 237))
        return (128, 128, 128)
    
    def can_gather(self, gatherer):
        """Check if this node can be gathered by someone"""
        if self.state == NodeState.DEPLETED:
            return False
        if self.state == NodeState.BEING_GATHERED and self.gatherer != gatherer:
            return False  # Someone else is gathering
        return True
    
    def start_gathering(self, gatherer):
        """Start gathering from this node"""
        if not self.can_gather(gatherer):
            return False
        
        self.state = NodeState.BEING_GATHERED
        self.gatherer = gatherer
        self.gather_progress = 0.0
        return True
    
    def stop_gathering(self, gatherer):
        """Stop gathering (cancelled or completed)"""
        if self.gatherer == gatherer:
            self.state = NodeState.AVAILABLE
            self.gatherer = None
            self.gather_progress = 0.0
    
    def update_gathering(self, dt, gather_speed=1.0):
        """Update gathering progress. Returns True when complete."""
        if self.state != NodeState.BEING_GATHERED:
            return False
        
        # Base gather time: 3 seconds for low tier, 10 seconds for high tier
        base_time = 3.0 if self.respawn_days <= 3 else 10.0
        gather_time = base_time * gather_speed
        
        self.gather_progress += dt / gather_time
        
        if self.gather_progress >= 1.0:
            return True  # Gathering complete!
        
        return False
    
    def deplete(self, current_day):
        """Mark node as depleted"""
        self.state = NodeState.DEPLETED
        self.gatherer = None
        self.gather_progress = 0.0
        self.depleted_on_day = current_day
    
    def check_respawn(self, current_day, weather_system=None, game_time=None):
        """Check if node should respawn (with optional weather/season modifiers)"""
        if self.state != NodeState.DEPLETED:
            return False
        
        if self.depleted_on_day is None:
            return False
        
        days_passed = current_day - self.depleted_on_day
        
        # Calculate effective respawn time with weather/season modifiers
        effective_respawn_days = self.base_respawn_days
        
        if weather_system and game_time:
            # Get weather modifier based on node type
            current_weather, _ = weather_system.get_current_weather()
            weather_mod = self._get_weather_modifier(current_weather)
            
            # Get seasonal modifier
            seasonal_mod = self._get_seasonal_modifier(game_time.get_season())
            
            # Apply modifiers
            effective_respawn_days = self.base_respawn_days * weather_mod * seasonal_mod
        
        if days_passed >= effective_respawn_days:
            self.state = NodeState.AVAILABLE
            self.depleted_on_day = None
            return True
        
        return False
    
    def _get_weather_modifier(self, weather):
        """Get weather modifier for respawn rate (lower = faster respawn)"""
        if self.node_type == NodeType.FISHING:
            # Rain helps fish respawn faster
            if weather in ('light_rain', 'heavy_rain', 'storm'):
                return 0.7  # 30% faster
            elif weather in ('fog',):
                return 0.85  # 15% faster
            elif weather in ('drought', 'heatwave'):
                return 1.5  # 50% slower (water levels low)
        elif self.node_type == NodeType.MINING:
            # Cold weather makes ground easier to break (frozen cracks)
            if weather in ('snow', 'blizzard'):
                return 0.9  # 10% faster
            elif weather in ('heatwave',):
                return 1.2  # 20% slower (rock too hot to work)
        elif self.node_type == NodeType.WOODCUTTING:
            # Moderate weather is best for tree growth
            if weather in ('light_rain',):
                return 0.8  # 20% faster
            elif weather in ('drought', 'heatwave'):
                return 1.4  # 40% slower (trees stressed)
            elif weather in ('snow', 'blizzard'):
                return 1.5  # 50% slower (dormant)
        
        return 1.0  # No modifier
    
    def _get_seasonal_modifier(self, season):
        """Get seasonal modifier for respawn rate (lower = faster respawn)"""
        if self.node_type == NodeType.WOODCUTTING:
            # Trees grow better in spring/summer
            if season == 'spring':
                return 0.7  # 30% faster (growth season)
            elif season == 'summer':
                return 0.9  # 10% faster
            elif season == 'autumn':
                return 1.1  # 10% slower
            elif season == 'winter':
                return 1.8  # 80% slower (dormant)
        elif self.node_type == NodeType.FISHING:
            # Fish more active in warmer months
            if season == 'spring':
                return 0.85  # 15% faster (spawning season)
            elif season == 'summer':
                return 0.9  # 10% faster
            elif season == 'winter':
                return 1.3  # 30% slower (less active)
        elif self.node_type == NodeType.MINING:
            # Mining less affected by seasons
            if season == 'winter':
                return 0.95  # 5% faster (easier to break frozen ground)
        
        return 1.0  # No modifier
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the node"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Don't draw if off-screen
        if screen_x < -50 or screen_x > screen.get_width() + 50:
            return
        if screen_y < -50 or screen_y > screen.get_height() + 50:
            return
        
        # Different visuals based on state
        if self.state == NodeState.DEPLETED:
            # Faded out
            color = tuple(c // 3 for c in self.color)
            pygame.draw.circle(screen, color, (screen_x, screen_y), self.size // 2)
            pygame.draw.circle(screen, (100, 100, 100), (screen_x, screen_y), self.size // 2, 2)
        
        elif self.state == NodeState.BEING_GATHERED:
            # Pulsing while being gathered
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0
            size = int(self.size // 2 + pulse * 4)
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), size)
            pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), size, 3)
            
            # Progress bar
            bar_width = 40
            bar_height = 6
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y + self.size // 2 + 5
            
            # Background
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Progress
            progress_width = int(bar_width * self.gather_progress)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, progress_width, bar_height))
            # Border
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        
        else:  # AVAILABLE
            # Normal appearance with subtle pulse
            self.pulse_timer += 0.02
            pulse = (pygame.math.Vector2(0, 1).rotate(self.pulse_timer * 50).y + 1) * 0.5
            size = int(self.size // 2 + pulse * 2)
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), size)
            pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), size, 2)
            
            # Resource type indicator (icon/letter)
            font = pygame.font.SysFont(None, 20)
            if self.node_type == NodeType.MINING:
                text = font.render("⛏", True, (255, 255, 255))
            elif self.node_type == NodeType.WOODCUTTING:
                text = font.render("🪓", True, (255, 255, 255))
            else:  # FISHING
                text = font.render("🎣", True, (255, 255, 255))
            
            screen.blit(text, (screen_x - text.get_width() // 2, screen_y - text.get_height() // 2))
    
    def get_distance_to(self, x, y):
        """Get distance from this node to a position"""
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5


class GatheringNodesManager:
    """Manages all gathering nodes in the world"""
    
    def __init__(self):
        self.nodes = []
        self.next_node_id = 0
        self.world = None  # Will be set when generating nodes
    
    def add_node(self, x, y, node_type, resource_type):
        """Add a new gathering node"""
        node = GatheringNode(x, y, node_type, resource_type, self.next_node_id)
        self.nodes.append(node)
        self.next_node_id += 1
        return node
    
    def get_nearby_node(self, x, y, node_type=None, max_distance=60):
        """Get the nearest available node to a position"""
        nearest = None
        nearest_dist = max_distance
        
        for node in self.nodes:
            if node_type and node.node_type != node_type:
                continue
            
            if node.state == NodeState.DEPLETED:
                continue
            
            dist = node.get_distance_to(x, y)
            if dist < nearest_dist:
                nearest = node
                nearest_dist = dist
        
        return nearest
    
    def get_node_by_id(self, node_id):
        """Get node by ID"""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def get_node_count(self):
        """Get total number of nodes"""
        return len(self.nodes)
    
    def is_valid_terrain_for_node(self, x, y, node_type):
        """Check if position has valid terrain for the node type"""
        if not self.world:
            return True  # Skip validation if no world provided
        
        tile = self.world.get_tile(x, y)
        terrain = tile.layers.get('ground', 'grass')
        
        if node_type == NodeType.MINING:
            # Mining nodes can spawn on rock groups, grass, dirt, or near rock patches
            return terrain in ['rock_group', 'grass', 'dirt']
        
        elif node_type == NodeType.WOODCUTTING:
            # Woodcutting nodes should be on grass or dirt (not on existing trees, water, roads)
            return terrain in ['grass', 'dirt']
        
        elif node_type == NodeType.FISHING:
            # Fishing nodes should be near water or on sand (beach/coast)
            if terrain in ['water', 'sand']:
                return True
            # Also allow on grass if near water (check adjacent tiles)
            if terrain == 'grass':
                config = self.world.config
                tile_size = config.TILE_SIZE
                # Check 4 adjacent tiles
                for dx, dy in [(tile_size, 0), (-tile_size, 0), (0, tile_size), (0, -tile_size)]:
                    adj_tile = self.world.get_tile(x + dx, y + dy)
                    if adj_tile.layers.get('ground', 'grass') == 'water':
                        return True
            return False
        
        return True
    
    def find_valid_spawn_position(self, start_x, start_y, node_type, max_attempts=20):
        """Find a valid spawn position near the target coordinates"""
        import random
        
        # Try the original position first
        if self.is_valid_terrain_for_node(start_x, start_y, node_type):
            return start_x, start_y
        
        # Try nearby positions in expanding radius
        for attempt in range(max_attempts):
            angle = random.uniform(0, 6.28)
            distance = (attempt + 1) * 75  # Expand search radius (increased from 50)
            offset_x = int(distance * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            offset_y = int(distance * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            
            test_x = start_x + offset_x
            test_y = start_y + offset_y
            
            if self.is_valid_terrain_for_node(test_x, test_y, node_type):
                return test_x, test_y
        
        # Fallback: return original position (better to have node on wrong terrain than no node)
        return start_x, start_y
    
    def update(self, dt, game_time, player, weather_system=None):
        """Update all nodes"""
        # Check for respawns based on total game days elapsed
        # Calculate total days from year, month, and day
        total_days = ((game_time.year_count - 1) * game_time.months_per_year * game_time.days_per_month + 
                      (game_time.month_count - 1) * game_time.days_per_month + 
                      game_time.day_count)
        self.check_respawns(total_days, weather_system, game_time)
        
        # Update gathering progress for player
        if player.gathering_node:
            node = player.gathering_node
            
            # Check if player moved away from node
            distance_to_node = ((player.x - node.x) ** 2 + (player.y - node.y) ** 2) ** 0.5
            if distance_to_node > 80:  # Moved too far away
                player.stop_gathering()
            elif node.state == NodeState.BEING_GATHERED and node.gatherer == player:
                # Get tool speed multiplier
                tool_speed = 1.0
                if player.gathering_tool:
                    from skills_system import MINING_TOOLS, WOODCUTTING_TOOLS, FISHING_TOOLS
                    all_tools = {**MINING_TOOLS, **WOODCUTTING_TOOLS, **FISHING_TOOLS}
                    tool_data = all_tools.get(player.gathering_tool, {})
                    tool_speed = tool_data.get('speed', 1.0)
                
                # Update gathering progress
                complete = node.update_gathering(dt, tool_speed)
                
                if complete:
                    # Get resource data for XP reward
                    from skills_system import MINING_RESOURCES, WOODCUTTING_RESOURCES, FISHING_RESOURCES
                    
                    resource_dict = {
                        NodeType.MINING: MINING_RESOURCES,
                        NodeType.WOODCUTTING: WOODCUTTING_RESOURCES,
                        NodeType.FISHING: FISHING_RESOURCES
                    }
                    
                    resource_data = resource_dict.get(node.node_type, {}).get(node.resource_type, {})
                    xp_reward = resource_data.get('xp', 0)
                    
                    # Complete gathering (awards XP and adds item)
                    player.complete_gathering(node.resource_type, xp_reward)
                    
                    # Deplete the node
                    node.deplete(total_days)
    
    def check_respawns(self, current_day, weather_system=None, game_time=None):
        """Check all depleted nodes for respawns (with optional weather/season effects)"""
        respawned_count = 0
        for node in self.nodes:
            if node.check_respawn(current_day, weather_system, game_time):
                respawned_count += 1
        return respawned_count
    
    def draw(self, screen, camera_x, camera_y):
        """Draw all nodes"""
        for node in self.nodes:
            node.draw(screen, camera_x, camera_y)
    
    def generate_world_nodes(self, world_width, world_height, towns, world=None):
        """Generate all gathering nodes across the world"""
        import random
        from skills_system import MINING_RESOURCES, WOODCUTTING_RESOURCES, FISHING_RESOURCES
        
        self.world = world  # Store for terrain validation
        
        # MINING NODES
        self._generate_mining_nodes(world_width, world_height, towns)
        
        # WOODCUTTING NODES
        self._generate_woodcutting_nodes(world_width, world_height, towns)
        
        # FISHING NODES
        self._generate_fishing_nodes(world_width, world_height, towns)
        
        print(f"Generated {len(self.nodes)} total gathering nodes")
    
    def _is_in_any_town(self, x, y, towns):
        """Check if position is inside any town zone"""
        for town in towns:
            if town.is_in_town(x, y):
                return True
        return False
    
    def _generate_mining_nodes(self, world_width, world_height, towns):
        """Generate mining nodes - all outside town zones"""
        # Copper: 10 outside towns (600-1200 pixels away)
        for i in range(10):
            town = random.choice(towns)
            angle = random.uniform(0, 6.28)
            dist = random.uniform(600, 1200)  # Far from town
            x = town.center_x + int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            y = town.center_y + int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            x, y = self.find_valid_spawn_position(x, y, NodeType.MINING)
            # Verify not in any town zone
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.MINING, 'copper')
        
        # Tin: 8 outside towns (600-1200 pixels away)
        for i in range(8):
            town = random.choice(towns)
            angle = random.uniform(0, 6.28)
            dist = random.uniform(600, 1200)  # Far from town
            x = town.center_x + int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            y = town.center_y + int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            x, y = self.find_valid_spawn_position(x, y, NodeType.MINING)
            # Verify not in any town zone
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.MINING, 'tin')
        
        # Iron: 8 between towns (avoid towns)
        for i in range(8):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.MINING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.MINING, 'iron')
        
        # Coal: 6 scattered (avoid towns)
        for i in range(6):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.MINING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.MINING, 'coal')
        
        # Silver: 4 (avoid towns)
        for i in range(4):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.MINING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.MINING, 'silver')
        
        # Gold: 3 (avoid towns)
        for i in range(3):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.MINING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.MINING, 'gold')
        
        # Mithril: 3 (avoid towns)
        for i in range(3):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.MINING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.MINING, 'mithril')
        
        # Adamantite: 2 (avoid towns)
        for i in range(2):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.MINING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.MINING, 'adamantite')
        
        # Runite: 2 fixed positions (far corners) - validate and avoid towns
        x, y = self.find_valid_spawn_position(world_width - 800, 800, NodeType.MINING)
        if not self._is_in_any_town(x, y, towns):
            self.add_node(x, y, NodeType.MINING, 'runite')
        x, y = self.find_valid_spawn_position(800, world_height - 800, NodeType.MINING)
        if not self._is_in_any_town(x, y, towns):
            self.add_node(x, y, NodeType.MINING, 'runite')
    
    def _generate_woodcutting_nodes(self, world_width, world_height, towns):
        """Generate woodcutting nodes - all outside town zones"""
        # Regular: 15 everywhere (but not in towns)
        for i in range(15):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.WOODCUTTING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.WOODCUTTING, 'regular_logs')
        
        # Oak: 10 outside towns (600-1200 pixels away)
        for i in range(10):
            town = random.choice(towns)
            angle = random.uniform(0, 6.28)
            dist = random.uniform(600, 1200)  # Far from town
            x = town.center_x + int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            y = town.center_y + int(dist * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            x, y = self.find_valid_spawn_position(x, y, NodeType.WOODCUTTING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.WOODCUTTING, 'oak_logs')
        
        # Willow: 8 (avoid towns)
        for i in range(8):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.WOODCUTTING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.WOODCUTTING, 'willow_logs')
        
        # Maple: 6 (avoid towns)
        for i in range(6):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.WOODCUTTING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.WOODCUTTING, 'maple_logs')
        
        # Yew: 4 (avoid towns)
        for i in range(4):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.WOODCUTTING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.WOODCUTTING, 'yew_logs')
        
        # Magic: 2 fixed positions - validate and avoid towns
        x, y = self.find_valid_spawn_position(world_width // 2, 800, NodeType.WOODCUTTING)
        if not self._is_in_any_town(x, y, towns):
            self.add_node(x, y, NodeType.WOODCUTTING, 'magic_logs')
        x, y = self.find_valid_spawn_position(world_width // 2, world_height - 800, NodeType.WOODCUTTING)
        if not self._is_in_any_town(x, y, towns):
            self.add_node(x, y, NodeType.WOODCUTTING, 'magic_logs')
    
    def _generate_fishing_nodes(self, world_width, world_height, towns):
        """Generate fishing nodes - avoid town zones"""
        # Shrimp/Sardine: 10 near water/coast (avoid towns)
        for i in range(10):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            resource = 'shrimp' if i % 2 == 0 else 'sardine'
            x, y = self.find_valid_spawn_position(x, y, NodeType.FISHING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.FISHING, resource)
        
        # Herring: 6 (avoid towns)
        for i in range(6):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.FISHING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.FISHING, 'herring')
        
        # Trout/Salmon: 6 (avoid towns)
        for i in range(6):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            resource = 'trout' if i % 2 == 0 else 'salmon'
            x, y = self.find_valid_spawn_position(x, y, NodeType.FISHING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.FISHING, resource)
        
        # Tuna: 4 (avoid towns)
        for i in range(4):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.FISHING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.FISHING, 'tuna')
        
        # Lobster: 3 (avoid towns)
        for i in range(3):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.FISHING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.FISHING, 'lobster')
        
        # Swordfish: 2 (avoid towns)
        for i in range(2):
            x = random.randint(500, world_width - 500)
            y = random.randint(500, world_height - 500)
            x, y = self.find_valid_spawn_position(x, y, NodeType.FISHING)
            if not self._is_in_any_town(x, y, towns):
                self.add_node(x, y, NodeType.FISHING, 'swordfish')
        
        # Shark: 2 fixed positions - validate and avoid towns
        x, y = self.find_valid_spawn_position(world_width - 1000, world_height - 1000, NodeType.FISHING)
        if not self._is_in_any_town(x, y, towns):
            self.add_node(x, y, NodeType.FISHING, 'shark')
        x, y = self.find_valid_spawn_position(1000, 1000, NodeType.FISHING)
        if not self._is_in_any_town(x, y, towns):
            self.add_node(x, y, NodeType.FISHING, 'shark')

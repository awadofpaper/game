"""
Stealth System - Vision cones, detection, and assassination mechanics
Handles NPC/guard vision, detection chance, and stealth-based actions
"""

import pygame
import math
import time


class VisionCone:
    """Represents an NPC's field of vision"""
    
    def __init__(self, owner_x, owner_y, direction=0, range_distance=150, angle=90):
        """
        Initialize vision cone
        
        Args:
            owner_x: X position of the owner
            owner_y: Y position of the owner
            direction: Direction in degrees (0=right, 90=down, 180=left, 270=up)
            range_distance: How far the NPC can see
            angle: Vision cone angle in degrees (90 = 90 degree cone)
        """
        self.owner_x = owner_x
        self.owner_y = owner_y
        self.direction = direction
        self.range_distance = range_distance
        self.angle = angle
    
    def update_position(self, x, y, direction=None):
        """Update vision cone position and direction"""
        self.owner_x = x
        self.owner_y = y
        if direction is not None:
            self.direction = direction
    
    def is_point_in_cone(self, target_x, target_y):
        """Check if a point is within the vision cone"""
        # Calculate distance
        dx = target_x - self.owner_x
        dy = target_y - self.owner_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if within range
        if distance > self.range_distance or distance < 1:
            return False
        
        # Calculate angle to target
        angle_to_target = math.degrees(math.atan2(dy, dx))
        
        # Normalize angles to 0-360
        angle_to_target = angle_to_target % 360
        direction_normalized = self.direction % 360
        
        # Calculate angle difference
        angle_diff = abs(angle_to_target - direction_normalized)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # Check if within cone angle
        return angle_diff <= self.angle / 2
    
    def get_detection_distance(self, target_x, target_y):
        """Get actual distance to target if in vision cone, None otherwise"""
        if self.is_point_in_cone(target_x, target_y):
            dx = target_x - self.owner_x
            dy = target_y - self.owner_y
            return math.sqrt(dx * dx + dy * dy)
        return None
    
    def draw(self, screen, camera_x, camera_y, color=(255, 255, 0, 50)):
        """Draw vision cone for debugging (semi-transparent)"""
        # Create points for the cone
        points = [(self.owner_x - camera_x, self.owner_y - camera_y)]
        
        # Calculate cone edges
        half_angle = self.angle / 2
        start_angle = self.direction - half_angle
        end_angle = self.direction + half_angle
        
        # Add points along the arc
        steps = 20
        for i in range(steps + 1):
            angle = math.radians(start_angle + (end_angle - start_angle) * i / steps)
            x = self.owner_x + self.range_distance * math.cos(angle)
            y = self.owner_y + self.range_distance * math.sin(angle)
            points.append((x - camera_x, y - camera_y))
        
        # Draw semi-transparent polygon
        if len(points) > 2:
            surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(surface, color, points)
            screen.blit(surface, (0, 0))


class StealthSystem:
    """Manages stealth mechanics, detection, and assassination"""
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.vision_cones = {}  # {npc_id: VisionCone}
        self.stealth_mode_active = False
        self.detection_alerts = []  # List of (npc_id, detection_level, timestamp)
    
    def create_vision_cone(self, npc_id, x, y, direction=0, range_distance=150, angle=90):
        """Create or update vision cone for an NPC"""
        self.vision_cones[npc_id] = VisionCone(x, y, direction, range_distance, angle)
    
    def update_vision_cone(self, npc_id, x, y, direction=None):
        """Update an NPC's vision cone position"""
        if npc_id in self.vision_cones:
            self.vision_cones[npc_id].update_position(x, y, direction)
    
    def remove_vision_cone(self, npc_id):
        """Remove vision cone (when NPC dies/despawns)"""
        if npc_id in self.vision_cones:
            del self.vision_cones[npc_id]
    
    def calculate_detection_chance(self, player, npc, base_distance):
        """
        Calculate chance of being detected by an NPC
        
        Args:
            player: Player object with stats
            npc: NPC object with stats
            base_distance: Distance from NPC to player
            
        Returns:
            float: Detection chance (0.0 to 1.0)
        """
        # Base detection chance based on distance
        max_distance = 150
        distance_factor = 1.0 - (base_distance / max_distance)
        distance_factor = max(0.0, min(1.0, distance_factor))
        
        # Player stealth stat (Agility)
        player_stealth = getattr(player, 'agility', 10)  # Direct attribute access with default
        stealth_modifier = 1.0 - (player_stealth / 200.0)  # Max 50% reduction at 100 Agility
        
        # NPC perception (if they have it)
        npc_perception = 10
        if hasattr(npc, 'stats'):
            npc_perception = npc.stats.get_stat("Perception") if hasattr(npc.stats, 'get_stat') else 10
        perception_modifier = 1.0 + (npc_perception / 100.0)  # Up to 2x at 100 perception
        
        # Time of day modifier (night = harder to see)
        time_modifier = self.get_time_detection_modifier()
        
        # Movement modifier (moving = easier to detect)
        movement_modifier = 1.0
        if hasattr(player, 'move_dir'):
            if any(player.move_dir.values()):
                movement_modifier = 1.5  # 50% easier to detect while moving
        
        # Calculate final detection chance
        detection_chance = distance_factor * stealth_modifier * perception_modifier * time_modifier * movement_modifier
        
        return max(0.05, min(0.95, detection_chance))  # Clamp between 5-95%
    
    def get_time_detection_modifier(self):
        """Get detection modifier based on time of day (night = 15% reduction)"""
        if not self.game_time:
            return 1.0
        
        hour, _ = self.game_time.get_time_hm()
        
        # Night time (11PM - 3AM) = 15% reduction in detection
        if hour >= 23 or hour <= 3:
            return 0.85  # 15% reduction
        
        return 1.0
    
    def check_player_detection(self, player, npcs):
        """
        Check if player is detected by any NPCs
        
        Args:
            player: Player object
            npcs: List of NPC objects
            
        Returns:
            list: List of (npc_id, detection_chance) tuples for NPCs that can see player
        """
        detections = []
        
        for npc in npcs:
            npc_id = getattr(npc, 'name', id(npc))
            
            # Check if NPC has vision cone
            if npc_id not in self.vision_cones:
                continue
            
            vision_cone = self.vision_cones[npc_id]
            
            # Check if player is in vision cone
            distance = vision_cone.get_detection_distance(player.x, player.y)
            if distance is not None:
                # Calculate detection chance
                detection_chance = self.calculate_detection_chance(player, npc, distance)
                detections.append((npc_id, detection_chance, npc))
        
        return detections
    
    def can_assassinate(self, player, target, required_perk="silent_but_deadly"):
        """
        Check if player can perform assassination on target
        
        Requirements:
        - Must be behind target
        - Must have "Silent but deadly" perk (requires Talking >= 40)
        - Must be within melee range
        
        Args:
            player: Player object
            target: Target NPC
            required_perk: Perk key required for assassination
            
        Returns:
            tuple: (can_assassinate: bool, reason: str)
        """
        # Check if player has required perk
        if hasattr(player, 'skills_manager'):
            if not player.skills_manager.perks.get(required_perk, False):
                return False, "Requires 'Silent but deadly' perk (Talking >= 40)"
        
        # Check distance (must be in melee range)
        dx = target.x - player.x
        dy = target.y - player.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 50:  # Melee range
            return False, "Target too far away"
        
        # Check if behind target (simplified - check if player is in opposite direction of target facing)
        # Get target direction (if they have one)
        target_direction = 0
        if hasattr(target, 'direction'):
            target_direction = target.direction
        elif hasattr(target, 'facing'):
            # Convert facing to angle
            facing_map = {'right': 0, 'down': 90, 'left': 180, 'up': 270}
            target_direction = facing_map.get(target.facing, 0)
        
        # Calculate angle from target to player
        angle_to_player = math.degrees(math.atan2(dy, dx)) % 360
        
        # Check if player is behind target (within 90 degrees of opposite direction)
        opposite_direction = (target_direction + 180) % 360
        angle_diff = abs(angle_to_player - opposite_direction)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        if angle_diff > 90:  # Must be within 90 degrees of directly behind
            return False, "Must be behind target"
        
        return True, "Ready to assassinate"
    
    def perform_assassination(self, target):
        """
        Execute assassination (instant kill)
        
        Args:
            target: Target NPC to assassinate
            
        Returns:
            bool: True if successful
        """
        # Instant kill
        if hasattr(target, 'health'):
            target.health = 0
        if hasattr(target, 'alive'):
            target.alive = False
        
        return True
    
    def draw_vision_cones(self, screen, camera_x, camera_y, debug=False):
        """Draw all vision cones (for debugging)"""
        if not debug:
            return
        
        for npc_id, cone in self.vision_cones.items():
            cone.draw(screen, camera_x, camera_y)

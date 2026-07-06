"""
Advanced AI System - Enemy Group Tactics
Intelligent enemy coordination, formations, and strategic behaviors
"""

import pygame
import math
import time
import random
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass, field

# Import personality system
try:
    import sys
    import os
    # Add current directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from ai_personality_system import (
        Personality, EmotionalState, PersonalitySystem, 
        get_personality_manager, BehaviorResult
    )
    from ai_behavior_trees import get_behavior_tree_factory
    from environmental_tactics import get_environmental_tactics, TacticalBehavior
    PERSONALITY_SYSTEM_AVAILABLE = True
    print("Advanced AI personality system loaded!")
except ImportError as e:
    PERSONALITY_SYSTEM_AVAILABLE = False
    print(f"Personality system not available - using basic AI: {e}")

class AIRole(Enum):
    """AI roles for enemy coordination"""
    LEADER = "leader"
    TANK = "tank"
    RANGED = "ranged"
    FLANKER = "flanker"
    HEALER = "healer"
    SCOUT = "scout"

class Formation(Enum):
    """Combat formations for enemy groups"""
    CIRCLE = "circle"
    LINE = "line"
    WEDGE = "wedge"
    AMBUSH = "ambush"
    PINCER = "pincer"
    RETREAT = "retreat"

class AIState(Enum):
    """AI behavioral states"""
    PATROL = "patrol"
    ALERT = "alert"
    ENGAGE = "engage"
    PURSUE = "pursue"
    RETREAT = "retreat"
    REGROUP = "regroup"
    COORDINATE = "coordinate"

@dataclass
class AIMemory:
    """AI memory for tracking events and player behavior"""
    last_seen_player_pos: Tuple[int, int] = (0, 0)
    last_seen_time: float = 0
    player_danger_level: float = 1.0  # 1.0 = normal, 2.0 = dangerous, 0.5 = weak
    known_player_abilities: Set[str] = field(default_factory=set)
    group_casualties: int = 0
    successful_attacks: int = 0
    failed_attacks: int = 0
    retreat_count: int = 0

@dataclass
class FormationPosition:
    """Position within a formation"""
    relative_x: float
    relative_y: float
    role: AIRole
    priority: int = 1  # Higher priority gets better positions

class EnemyGroup:
    """Manages coordinated enemy behavior"""
    
    def __init__(self, group_id: str):
        self.group_id = group_id
        self.members: List = []  # Enemy objects
        self.leader: Optional[object] = None
        self.formation: Formation = Formation.LINE
        self.state: AIState = AIState.PATROL
        self.memory = AIMemory()
        
        # Group coordination
        self.formation_center = (0, 0)
        self.formation_radius = 100
        self.formation_angle = 0
        
        # Tactical timers
        self.last_formation_change = 0
        self.last_state_change = 0
        self.coordination_cooldown = 0
        
        # Group stats
        self.total_health_ratio = 1.0
        self.average_level = 1
        self.group_morale = 1.0
        
        print(f"Enemy group {group_id} created")
    
    def add_member(self, enemy, role: AIRole = AIRole.TANK):
        """Add an enemy to the group"""
        self.members.append(enemy)
        
        # Set AI properties
        if not hasattr(enemy, 'ai_role'):
            enemy.ai_role = role
        if not hasattr(enemy, 'ai_state'):
            enemy.ai_state = AIState.PATROL
        if not hasattr(enemy, 'formation_pos'):
            enemy.formation_pos = FormationPosition(0, 0, role)
        if not hasattr(enemy, 'ai_memory'):
            enemy.ai_memory = AIMemory()
        
        # Initialize personality system
        if PERSONALITY_SYSTEM_AVAILABLE and not hasattr(enemy, 'personality_system'):
            try:
                enemy_id = f"{self.group_id}_{len(self.members)}"
                personality_manager = get_personality_manager()
                
                # Choose personality based on role and enemy type
                personality_type = self._determine_personality_for_role(role, enemy)
                if personality_type:
                    enemy.personality_system = personality_manager.create_personality(enemy_id, personality_type)
                    
                    # Create behavior tree
                    tree_factory = get_behavior_tree_factory()
                    enemy_type = getattr(enemy, 'enemy_type', 'warrior')
                    combat_role = 'ranged' if role in [AIRole.RANGED, AIRole.SCOUT] else 'melee'
                    enemy.behavior_tree = tree_factory.create_tree_for_enemy(enemy_type, personality_type, combat_role)
                    
                    print(f"Created {personality_type.value} personality for {enemy_type} {role.value}")
                else:
                    enemy.personality_system = None
                    enemy.behavior_tree = None
            except Exception as e:
                print(f"Failed to create personality system: {e}")
                enemy.personality_system = None
                enemy.behavior_tree = None
        else:
            enemy.personality_system = None
            enemy.behavior_tree = None
        
        # Select leader (highest level or designated leader role)
        if role == AIRole.LEADER or self.leader is None:
            if self.leader is None or (hasattr(enemy, 'level') and hasattr(self.leader, 'level') and enemy.level > self.leader.level):
                self.leader = enemy
                enemy.ai_role = AIRole.LEADER
        
        self._update_group_stats()
        print(f"Added {role.value} to group {self.group_id}")
    
    def _determine_personality_for_role(self, role: AIRole, enemy):
        """Determine appropriate personality for enemy role"""
        if not PERSONALITY_SYSTEM_AVAILABLE:
            return None
        
        # Role-based personality tendencies
        role_personalities = {
            AIRole.LEADER: [Personality.TACTICAL, Personality.AGGRESSIVE, Personality.PROTECTIVE],
            AIRole.TANK: [Personality.STUBBORN, Personality.PROTECTIVE, Personality.AGGRESSIVE],
            AIRole.RANGED: [Personality.CAUTIOUS, Personality.TACTICAL, Personality.COWARDLY],
            AIRole.FLANKER: [Personality.AGGRESSIVE, Personality.ADAPTIVE, Personality.COWARDLY],
            AIRole.HEALER: [Personality.PROTECTIVE, Personality.CAUTIOUS, Personality.TACTICAL],
            AIRole.SCOUT: [Personality.CAUTIOUS, Personality.ADAPTIVE, Personality.COWARDLY]
        }
        
        # Enemy type influences (if available)
        enemy_type = getattr(enemy, 'enemy_type', 'warrior').lower()
        type_personalities = {
            'berserker': [Personality.BERSERKER, Personality.AGGRESSIVE],
            'coward': [Personality.COWARDLY, Personality.CAUTIOUS],
            'elite': [Personality.TACTICAL, Personality.ADAPTIVE],
            'grunt': [Personality.STUBBORN, Personality.AGGRESSIVE]
        }
        
        # Combine possibilities
        possible_personalities = role_personalities.get(role, [Personality.AGGRESSIVE])
        if enemy_type in type_personalities:
            possible_personalities.extend(type_personalities[enemy_type])
        
        # Random selection with some weighting
        return random.choice(possible_personalities)
    
    def remove_member(self, enemy):
        """Remove an enemy from the group"""
        if enemy in self.members:
            self.members.remove(enemy)
            
            # Select new leader if needed
            if enemy == self.leader:
                self.leader = None
                for member in self.members:
                    if member.ai_role == AIRole.LEADER or self.leader is None:
                        self.leader = member
                        member.ai_role = AIRole.LEADER
                        break
            
            self._update_group_stats()
            self.memory.group_casualties += 1
            
            # Check if group should retreat or regroup
            if len(self.members) <= 2 and self.memory.group_casualties >= 2:
                self._change_state(AIState.RETREAT)
    
    def _update_group_stats(self):
        """Update group statistics"""
        if not self.members:
            return
        
        total_health = 0
        max_health = 0
        total_level = 0
        
        for member in self.members:
            if hasattr(member, 'health') and hasattr(member, 'max_health'):
                total_health += member.health
                max_health += member.max_health
            if hasattr(member, 'level'):
                total_level += member.level
        
        self.total_health_ratio = total_health / max_health if max_health > 0 else 0
        self.average_level = total_level / len(self.members) if self.members else 1
        
        # Calculate morale based on casualties and health
        casualty_factor = max(0.3, 1.0 - (self.memory.group_casualties * 0.2))
        health_factor = max(0.5, self.total_health_ratio)
        self.group_morale = casualty_factor * health_factor
    
    def update(self, dt: float, player_pos: Tuple[int, int], tilemap):
        """Update group AI behavior"""
        if not self.members or not self.leader:
            return
        
        current_time = time.time()
        
        # Update formation center based on leader position
        if hasattr(self.leader, 'x') and hasattr(self.leader, 'y'):
            self.formation_center = (self.leader.x, self.leader.y)
        
        # Detect player and update memory
        self._detect_player(player_pos, current_time)
        
        # Update AI state based on conditions
        self._update_ai_state(current_time, player_pos)
        
        # Execute formation and coordination
        if current_time - self.coordination_cooldown > 1.0:  # Coordinate every second
            self._execute_formation()
            self._coordinate_attacks(player_pos)
            self.coordination_cooldown = current_time
        
        # Update individual member AI
        for member in self.members[:]:  # Copy list to allow removal during iteration
            if hasattr(member, 'health') and member.health <= 0:
                self.remove_member(member)
                continue
            
            self._update_member_ai(member, dt, player_pos, tilemap)
    
    def _detect_player(self, player_pos: Tuple[int, int], current_time: float):
        """Detect and track player position"""
        player_x, player_y = player_pos
        
        # Check if any member can see the player
        player_detected = False
        detection_range = 150
        
        for member in self.members:
            if not hasattr(member, 'x') or not hasattr(member, 'y'):
                continue
                
            distance = math.sqrt((member.x - player_x)**2 + (member.y - player_y)**2)
            
            if distance <= detection_range:
                player_detected = True
                self.memory.last_seen_player_pos = player_pos
                self.memory.last_seen_time = current_time
                
                # Analyze player threat level
                self._analyze_player_threat(player_pos, distance)
                break
    
    def _analyze_player_threat(self, player_pos: Tuple[int, int], distance: float):
        """Analyze player threat level based on behavior"""
        # Increase danger level if player is close
        if distance < 50:
            self.memory.player_danger_level = min(3.0, self.memory.player_danger_level + 0.1)
        
        # Decrease danger level over time if player keeps distance
        elif distance > 120:
            self.memory.player_danger_level = max(0.5, self.memory.player_danger_level - 0.05)
    
    def _update_ai_state(self, current_time: float, player_pos: Tuple[int, int]):
        """Update group AI state based on conditions"""
        player_x, player_y = player_pos
        time_since_seen = current_time - self.memory.last_seen_time
        
        # State transition logic
        if self.state == AIState.PATROL:
            if time_since_seen < 2.0:  # Recently saw player
                self._change_state(AIState.ALERT)
        
        elif self.state == AIState.ALERT:
            if time_since_seen < 1.0:  # Player still visible
                self._change_state(AIState.ENGAGE)
            elif time_since_seen > 10.0:  # Lost player for a while
                self._change_state(AIState.PATROL)
        
        elif self.state == AIState.ENGAGE:
            if self.group_morale < 0.3:  # Low morale
                self._change_state(AIState.RETREAT)
            elif time_since_seen > 5.0:  # Lost player
                self._change_state(AIState.PURSUE)
            elif len(self.members) < 3 and self.memory.group_casualties > 0:
                self._change_state(AIState.REGROUP)
        
        elif self.state == AIState.PURSUE:
            if time_since_seen < 1.0:  # Found player again
                self._change_state(AIState.ENGAGE)
            elif time_since_seen > 15.0:  # Give up chase
                self._change_state(AIState.PATROL)
        
        elif self.state == AIState.RETREAT:
            if time_since_seen > 20.0 and self.group_morale > 0.6:  # Recovered
                self._change_state(AIState.REGROUP)
        
        elif self.state == AIState.REGROUP:
            if len(self.members) >= 3 or time_since_seen > 30.0:
                self._change_state(AIState.PATROL)
    
    def _change_state(self, new_state: AIState):
        """Change group AI state"""
        if new_state != self.state:
            print(f"Group {self.group_id} state: {self.state.value} → {new_state.value}")
            self.state = new_state
            self.last_state_change = time.time()
            
            # Update formation based on state
            self._select_formation_for_state(new_state)
            
            # Update all members' state
            for member in self.members:
                member.ai_state = new_state
    
    def _select_formation_for_state(self, state: AIState):
        """Select appropriate formation for AI state"""
        formation_map = {
            AIState.PATROL: Formation.LINE,
            AIState.ALERT: Formation.CIRCLE,
            AIState.ENGAGE: Formation.WEDGE,
            AIState.PURSUE: Formation.WEDGE,
            AIState.RETREAT: Formation.RETREAT,
            AIState.REGROUP: Formation.CIRCLE
        }
        
        new_formation = formation_map.get(state, Formation.LINE)
        if new_formation != self.formation:
            self.formation = new_formation
            self.last_formation_change = time.time()
            print(f"Group {self.group_id} formation: {new_formation.value}")
    
    def _execute_formation(self):
        """Execute current formation positioning"""
        if not self.members or not self.leader:
            return
        
        formation_positions = self._calculate_formation_positions()
        
        for member, target_pos in zip(self.members, formation_positions):
            if hasattr(member, 'formation_target'):
                member.formation_target = target_pos
            else:
                # Fallback: set target position directly
                if hasattr(member, 'target_x') and hasattr(member, 'target_y'):
                    member.target_x, member.target_y = target_pos
    
    def _calculate_formation_positions(self) -> List[Tuple[int, int]]:
        """Calculate positions for current formation"""
        positions = []
        member_count = len(self.members)
        center_x, center_y = self.formation_center
        
        if self.formation == Formation.CIRCLE:
            for i, member in enumerate(self.members):
                angle = (2 * math.pi * i) / member_count + self.formation_angle
                x = center_x + math.cos(angle) * self.formation_radius
                y = center_y + math.sin(angle) * self.formation_radius
                positions.append((int(x), int(y)))
        
        elif self.formation == Formation.LINE:
            spacing = 40
            start_offset = -(member_count - 1) * spacing / 2
            for i, member in enumerate(self.members):
                x = center_x + start_offset + (i * spacing)
                y = center_y
                positions.append((int(x), int(y)))
        
        elif self.formation == Formation.WEDGE:
            # V-formation with leader at point
            for i, member in enumerate(self.members):
                if member == self.leader:
                    positions.append((center_x, center_y))
                else:
                    side = 1 if i % 2 == 0 else -1
                    row = (i + 1) // 2
                    x = center_x + side * row * 30
                    y = center_y + row * 40
                    positions.append((int(x), int(y)))
        
        elif self.formation == Formation.RETREAT:
            # Scattered retreat formation
            for i, member in enumerate(self.members):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(60, 120)
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                positions.append((int(x), int(y)))
        
        else:  # Default to circle
            return self._calculate_formation_positions()
        
        return positions
    
    def _coordinate_attacks(self, player_pos: Tuple[int, int]):
        """Coordinate group attacks on player"""
        if self.state not in [AIState.ENGAGE, AIState.PURSUE]:
            return
        
        player_x, player_y = player_pos
        
        # Assign roles and tactics based on member types
        tanks = [m for m in self.members if m.ai_role == AIRole.TANK]
        ranged = [m for m in self.members if m.ai_role == AIRole.RANGED]
        flankers = [m for m in self.members if m.ai_role == AIRole.FLANKER]
        
        # Tank tactics: Engage directly
        for tank in tanks:
            if hasattr(tank, 'target_x'):
                tank.target_x = player_x
                tank.target_y = player_y
                tank.ai_priority = "attack_player"
        
        # Ranged tactics: Keep distance and surround
        for i, ranger in enumerate(ranged):
            if hasattr(ranger, 'target_x'):
                angle = (2 * math.pi * i) / len(ranged) if ranged else 0
                distance = 100  # Stay at range
                ranger.target_x = player_x + math.cos(angle) * distance
                ranger.target_y = player_y + math.sin(angle) * distance
                ranger.ai_priority = "attack_ranged"
        
        # Flanker tactics: Circle around player
        for i, flanker in enumerate(flankers):
            if hasattr(flanker, 'target_x'):
                angle = time.time() * 0.5 + (i * math.pi)  # Rotating movement
                distance = 80
                flanker.target_x = player_x + math.cos(angle) * distance
                flanker.target_y = player_y + math.sin(angle) * distance
                flanker.ai_priority = "flank_player"
    
    def _update_member_ai(self, member, dt: float, player_pos: Tuple[int, int], tilemap):
        """Update individual member AI behavior"""
        if not hasattr(member, 'x') or not hasattr(member, 'y'):
            return
        
        # Check for environmental tactics first
        tactical_action = None
        if PERSONALITY_SYSTEM_AVAILABLE:
            try:
                from environmental_tactics import get_environmental_tactics
                environmental_tactics = get_environmental_tactics()
                
                # Prepare context for tactical decision making
                context = {
                    'player_velocity': getattr(member, 'last_player_velocity', (0, 0)),
                    'player_facing': getattr(member, 'last_player_facing', 0),
                    'ai_group': self,
                    'dt': dt,
                    'tilemap': tilemap,
                    'group_state': getattr(self, 'current_state', 'patrol'),
                    'member_role': getattr(member, 'ai_role', None)
                }
                
                # Choose tactical behavior
                tactical_behavior = environmental_tactics.choose_tactical_behavior(
                    member, player_pos, context
                )
                
                # Execute tactical behavior if chosen
                if tactical_behavior:
                    tactical_action = environmental_tactics.execute_tactical_behavior(
                        member, tactical_behavior, player_pos, context
                    )
                    
                    # Store the current tactic for result tracking
                    member.current_tactic = tactical_behavior
                    member.tactic_start_time = time.time()
                    
            except Exception as e:
                print(f"Environmental tactics error: {e}")
                tactical_action = None
        
        # Update personality system
        if (PERSONALITY_SYSTEM_AVAILABLE and hasattr(member, 'personality_system') and 
            member.personality_system is not None):
            member.personality_system.update(dt)
            
            # Execute behavior tree if available
            if hasattr(member, 'behavior_tree'):
                context = {
                    'player_pos': player_pos,
                    'ai_group': self,
                    'personality_system': member.personality_system,
                    'dt': dt,
                    'tilemap': tilemap,
                    'tactical_action': tactical_action  # Pass tactical action to behavior tree
                }
                
                # Execute the behavior tree
                result = member.behavior_tree.execute(member, context)
                
                # Handle behavior tree results
                if result == BehaviorResult.SUCCESS:
                    # Behavior completed successfully
                    if hasattr(member.personality_system, 'react_to_event'):
                        member.personality_system.react_to_event("successful_behavior", 0.1)
                        
                    # Record tactical success if using environmental tactics
                    if hasattr(member, 'current_tactic') and tactical_action:
                        self._record_tactical_success(member, True)
                        
                elif result == BehaviorResult.FAILURE:
                    # Behavior failed - try alternative
                    if hasattr(member.personality_system, 'react_to_event'):
                        member.personality_system.react_to_event("failed_behavior", 0.1)
                        
                    # Record tactical failure if using environmental tactics
                    if hasattr(member, 'current_tactic') and tactical_action:
                        self._record_tactical_success(member, False)
        
        # Handle movement - prioritize environmental tactics over formation
        if tactical_action and 'move_to' in tactical_action:
            # Use environmental tactical movement
            self._handle_environmental_movement(member, tactical_action, dt)
        elif hasattr(member, 'formation_target'):
            # Fallback to formation-based movement
            target_x, target_y = member.formation_target
            
            # Simple movement towards target
            dx = target_x - member.x
            dy = target_y - member.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 10:  # Move if not at target
                speed = getattr(member, 'speed', 50) * dt
                
                # Apply personality speed modifier if available
                if (PERSONALITY_SYSTEM_AVAILABLE and hasattr(member, 'personality_system') and 
                    member.personality_system is not None):
                    speed_mod = member.personality_system.get_behavior_modifier('movement_speed')
                    speed *= speed_mod
                
                if distance > 0:
                    member.x += (dx / distance) * speed
                    member.y += (dy / distance) * speed
        
        # Role-specific behavior
        if hasattr(member, 'ai_priority'):
            self._execute_role_behavior(member, player_pos, dt)
    
    def _execute_role_behavior(self, member, player_pos: Tuple[int, int], dt: float):
        """Execute role-specific AI behavior"""
        player_x, player_y = player_pos
        
        if not hasattr(member, 'ai_priority'):
            return
        
        priority = member.ai_priority
        
        if priority == "attack_player":
            # Direct attack behavior
            distance = math.sqrt((member.x - player_x)**2 + (member.y - player_y)**2)
            if distance < 40 and hasattr(member, 'attack_cooldown'):
                # Apply personality modifiers to attack timing
                cooldown = member.attack_cooldown
                if PERSONALITY_SYSTEM_AVAILABLE and hasattr(member, 'personality_system'):
                    attack_freq_mod = member.personality_system.get_behavior_modifier('attack_frequency')
                    cooldown /= attack_freq_mod
                
                if getattr(member, 'last_attack', 0) + cooldown < time.time():
                    member.last_attack = time.time()
                    
                    # Trigger attack (would be handled by existing attack system)
                    if hasattr(member, 'attack_player'):
                        member.attack_player = True
                        
                        # Emotional reaction to attacking
                        if PERSONALITY_SYSTEM_AVAILABLE and hasattr(member, 'personality_system'):
                            member.personality_system.react_to_event("attacked_player", 0.2)
        
        elif priority == "attack_ranged":
            # Ranged attack behavior
            distance = math.sqrt((member.x - player_x)**2 + (member.y - player_y)**2)
            if 60 < distance < 120 and hasattr(member, 'ranged_attack_cooldown'):
                if getattr(member, 'last_ranged_attack', 0) + member.ranged_attack_cooldown < time.time():
                    member.last_ranged_attack = time.time()
                    # Trigger ranged attack
                    if hasattr(member, 'ranged_attack_player'):
                        member.ranged_attack_player = True
        
        elif priority == "flank_player":
            # Flanking behavior - try to get behind player
            # This would integrate with existing movement/pathfinding systems
            pass
    
    def _record_tactical_success(self, member, success: bool):
        """Record the success or failure of a tactical behavior"""
        if hasattr(member, 'current_tactic'):
            try:
                from environmental_tactics import get_environmental_tactics
                environmental_tactics = get_environmental_tactics()
                environmental_tactics.record_tactic_result(member, member.current_tactic, success)
                
                # Clear current tactic
                delattr(member, 'current_tactic')
                if hasattr(member, 'tactic_start_time'):
                    delattr(member, 'tactic_start_time')
                    
            except ImportError:
                pass  # Environmental tactics not available
    
    def _handle_environmental_movement(self, member, tactical_action: Dict[str, any], dt: float):
        """Handle movement based on environmental tactical decisions"""
        if not tactical_action or 'move_to' not in tactical_action:
            return
        
        target_x, target_y = tactical_action['move_to']
        
        # Calculate movement
        dx = target_x - member.x
        dy = target_y - member.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:  # Only move if not at target
            speed = getattr(member, 'speed', 50) * dt
            
            # Apply tactical behavior modifiers
            behavior = tactical_action.get('behavior', '')
            
            if tactical_action.get('move_stealthily', False):
                speed *= 0.5  # Move slower when stealthy
            elif tactical_action.get('aggressive_approach', False):
                speed *= 1.5  # Move faster when aggressive
            
            # Apply personality speed modifier if available
            if (PERSONALITY_SYSTEM_AVAILABLE and hasattr(member, 'personality_system') and 
                member.personality_system is not None):
                speed_mod = member.personality_system.get_behavior_modifier('movement_speed')
                speed *= speed_mod
            
            # Normalize and apply movement
            if distance > 0:
                member.x += (dx / distance) * speed
                member.y += (dy / distance) * speed
                
                # Set member flags based on tactical behavior
                if tactical_action.get('concealed', False):
                    member.is_concealed = True
                if tactical_action.get('hold_position', False):
                    member.should_hold_position = True
                if tactical_action.get('wait_for_player', False):
                    member.waiting_for_player = True

class AIGroupManager:
    """Manages all enemy groups and their interactions"""
    
    def __init__(self):
        self.groups: Dict[str, EnemyGroup] = {}
        self.next_group_id = 1
        
        # Global AI settings
        self.ai_enabled = True
        self.difficulty_multiplier = 1.0
        self.coordination_range = 200
        
        print("AI Group Manager initialized")
    
    def create_group(self, group_id: str = None) -> EnemyGroup:
        """Create a new enemy group"""
        if group_id is None:
            group_id = f"group_{self.next_group_id}"
            self.next_group_id += 1
        
        group = EnemyGroup(group_id)
        self.groups[group_id] = group
        return group
    
    def add_enemy_to_group(self, enemy, group_id: str, role: AIRole = AIRole.TANK):
        """Add an enemy to a specific group"""
        if group_id not in self.groups:
            self.create_group(group_id)
        
        self.groups[group_id].add_member(enemy, role)
        
        # Mark enemy with group association
        enemy.ai_group_id = group_id
    
    def auto_group_enemies(self, enemies: List, max_group_size: int = 5) -> List[str]:
        """Automatically group nearby enemies"""
        ungrouped = [e for e in enemies if not hasattr(e, 'ai_group_id')]
        group_ids = []
        
        while ungrouped:
            # Start new group with first ungrouped enemy
            leader = ungrouped.pop(0)
            group = self.create_group()
            group_ids.append(group.group_id)
            
            # Add leader
            self.add_enemy_to_group(leader, group.group_id, AIRole.LEADER)
            
            # Find nearby enemies to add to group
            group_size = 1
            remaining = ungrouped.copy()
            
            for enemy in remaining:
                if group_size >= max_group_size:
                    break
                
                if hasattr(leader, 'x') and hasattr(enemy, 'x'):
                    distance = math.sqrt((leader.x - enemy.x)**2 + (leader.y - enemy.y)**2)
                    
                    if distance <= self.coordination_range:
                        # Assign role based on enemy type
                        role = self._determine_enemy_role(enemy)
                        self.add_enemy_to_group(enemy, group.group_id, role)
                        ungrouped.remove(enemy)
                        group_size += 1
        
        return group_ids
    
    def _determine_enemy_role(self, enemy) -> AIRole:
        """Determine appropriate AI role for enemy based on type"""
        enemy_type = getattr(enemy, 'enemy_type', 'unknown')
        
        role_mapping = {
            'archer': AIRole.RANGED,
            'mage': AIRole.RANGED,
            'scout': AIRole.SCOUT,
            'rogue': AIRole.FLANKER,
            'assassin': AIRole.FLANKER,
            'healer': AIRole.HEALER,
            'tank': AIRole.TANK,
            'warrior': AIRole.TANK,
            'knight': AIRole.TANK,
            'leader': AIRole.LEADER,
            'captain': AIRole.LEADER
        }
        
        return role_mapping.get(enemy_type.lower(), AIRole.TANK)
    
    def update_all_groups(self, dt: float, player_pos: Tuple[int, int], tilemap):
        """Update all enemy groups"""
        if not self.ai_enabled:
            return
        
        # Update environmental awareness with current tilemap
        if PERSONALITY_SYSTEM_AVAILABLE and tilemap:
            try:
                from environmental_tactics import get_environmental_tactics
                environmental_tactics = get_environmental_tactics()
                if environmental_tactics.environmental_awareness:
                    environmental_tactics.analyze_tilemap(tilemap)
            except ImportError:
                pass  # Environmental tactics not available
        
        # Update personality manager
        if PERSONALITY_SYSTEM_AVAILABLE:
            personality_manager = get_personality_manager()
            personality_manager.update_all_personalities(dt)
        
        # Remove empty groups
        empty_groups = [gid for gid, group in self.groups.items() if not group.members]
        for gid in empty_groups:
            del self.groups[gid]
        
        # Update all active groups
        for group in self.groups.values():
            group.update(dt, player_pos, tilemap)
    
    def get_group_for_enemy(self, enemy) -> Optional[EnemyGroup]:
        """Get the group that contains a specific enemy"""
        group_id = getattr(enemy, 'ai_group_id', None)
        return self.groups.get(group_id) if group_id else None
    
    def disband_group(self, group_id: str):
        """Disband a group and remove all member associations"""
        if group_id in self.groups:
            group = self.groups[group_id]
            for member in group.members:
                if hasattr(member, 'ai_group_id'):
                    delattr(member, 'ai_group_id')
            del self.groups[group_id]
    
    def set_difficulty(self, difficulty: float):
        """Set global AI difficulty multiplier"""
        self.difficulty_multiplier = max(0.1, min(3.0, difficulty))
        
        # Apply to all groups
        for group in self.groups.values():
            # Adjust reaction times, coordination speed, etc.
            group.coordination_cooldown *= (2.0 - self.difficulty_multiplier)
    
    def get_debug_info(self) -> Dict:
        """Get debug information about AI groups"""
        return {
            'total_groups': len(self.groups),
            'total_enemies': sum(len(g.members) for g in self.groups.values()),
            'group_states': {gid: g.state.value for gid, g in self.groups.items()},
            'group_formations': {gid: g.formation.value for gid, g in self.groups.items()},
            'difficulty': self.difficulty_multiplier
        }

# Global AI manager instance
_ai_manager = None

def get_ai_manager() -> AIGroupManager:
    """Get the global AI group manager instance"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIGroupManager()
    return _ai_manager
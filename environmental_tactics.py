"""
Environmental AI Tactics
Advanced AI behaviors that use environmental awareness for strategic positioning
"""

import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

try:
    from environmental_awareness import (
        get_environmental_awareness, TerrainType, CoverQuality, 
        TacticalPosition, TerrainFeature
    )
    from ai_personality_system import Personality, EmotionalState
    ENVIRONMENTAL_SYSTEM_AVAILABLE = True
except ImportError:
    ENVIRONMENTAL_SYSTEM_AVAILABLE = False

class TacticalBehavior(Enum):
    """Types of environmental tactical behaviors"""
    SEEK_COVER = "seek_cover"
    USE_HIGH_GROUND = "use_high_ground"
    AMBUSH_SETUP = "ambush_setup"
    CHOKEPOINT_CONTROL = "chokepoint_control"
    FLANK_MANEUVER = "flank_maneuver"
    KITE_AROUND_OBSTACLES = "kite_around_obstacles"
    PUSH_INTO_HAZARDS = "push_into_hazards"
    BRIDGE_CONTROL = "bridge_control"
    CONCEALMENT_APPROACH = "concealment_approach"

class EnvironmentalTactics:
    """Manages environmental tactics for AI enemies"""
    
    def __init__(self):
        self.environmental_awareness = get_environmental_awareness() if ENVIRONMENTAL_SYSTEM_AVAILABLE else None
        
        # Tactical preferences by personality
        self.personality_tactics = {
            Personality.AGGRESSIVE: [
                TacticalBehavior.USE_HIGH_GROUND,
                TacticalBehavior.FLANK_MANEUVER,
                TacticalBehavior.PUSH_INTO_HAZARDS
            ],
            Personality.COWARDLY: [
                TacticalBehavior.SEEK_COVER,
                TacticalBehavior.CONCEALMENT_APPROACH,
                TacticalBehavior.KITE_AROUND_OBSTACLES
            ],
            Personality.TACTICAL: [
                TacticalBehavior.CHOKEPOINT_CONTROL,
                TacticalBehavior.USE_HIGH_GROUND,
                TacticalBehavior.AMBUSH_SETUP
            ],
            Personality.BERSERKER: [
                TacticalBehavior.FLANK_MANEUVER,
                TacticalBehavior.PUSH_INTO_HAZARDS
            ],
            Personality.CAUTIOUS: [
                TacticalBehavior.SEEK_COVER,
                TacticalBehavior.USE_HIGH_GROUND,
                TacticalBehavior.CONCEALMENT_APPROACH
            ],
            Personality.PROTECTIVE: [
                TacticalBehavior.CHOKEPOINT_CONTROL,
                TacticalBehavior.SEEK_COVER,
                TacticalBehavior.BRIDGE_CONTROL
            ],
            Personality.ADAPTIVE: [
                # Adaptive enemies learn which tactics work
                TacticalBehavior.SEEK_COVER,
                TacticalBehavior.FLANK_MANEUVER,
                TacticalBehavior.AMBUSH_SETUP
            ]
        }
        
        # Tactical memory for learning
        self.tactic_success_rates = {}
        
        print("Environmental Tactics system initialized")
    
    def analyze_tilemap(self, tilemap: List[List[int]], tile_size: int = 32):
        """Analyze tilemap for environmental features"""
        if self.environmental_awareness:
            self.environmental_awareness.analyze_tilemap(tilemap, tile_size)
    
    def choose_tactical_behavior(self, enemy, player_pos: Tuple[int, int], 
                               context: Dict[str, Any]) -> Optional[TacticalBehavior]:
        """Choose the best tactical behavior for current situation"""
        if not ENVIRONMENTAL_SYSTEM_AVAILABLE:
            return None
        
        enemy_pos = (getattr(enemy, 'x', 0), getattr(enemy, 'y', 0))
        personality_system = getattr(enemy, 'personality_system', None)
        
        if not personality_system:
            return None
        
        # Get personality-preferred tactics
        personality_type = personality_system.personality_type
        preferred_tactics = self.personality_tactics.get(personality_type, [])
        
        # Analyze current situation
        situation_tactics = self._analyze_situation(enemy_pos, player_pos, context)
        
        # Combine preferences with situation analysis
        viable_tactics = []
        for tactic in preferred_tactics:
            if tactic in situation_tactics:
                # Calculate viability score
                base_score = situation_tactics[tactic]
                
                # Apply personality modifiers
                personality_bonus = self._get_personality_bonus(tactic, personality_system)
                
                # Apply learning bonus (for adaptive personalities)
                learning_bonus = self._get_learning_bonus(tactic, enemy)
                
                total_score = base_score + personality_bonus + learning_bonus
                viable_tactics.append((tactic, total_score))
        
        # Choose best tactic
        if viable_tactics:
            viable_tactics.sort(key=lambda x: x[1], reverse=True)
            return viable_tactics[0][0]
        
        return None
    
    def execute_tactical_behavior(self, enemy, behavior: TacticalBehavior, 
                                player_pos: Tuple[int, int], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tactical behavior and return movement/action instructions"""
        if not ENVIRONMENTAL_SYSTEM_AVAILABLE:
            return {}
        
        enemy_pos = (getattr(enemy, 'x', 0), getattr(enemy, 'y', 0))
        
        if behavior == TacticalBehavior.SEEK_COVER:
            return self._execute_seek_cover(enemy, enemy_pos, player_pos, context)
        
        elif behavior == TacticalBehavior.USE_HIGH_GROUND:
            return self._execute_use_high_ground(enemy, enemy_pos, player_pos, context)
        
        elif behavior == TacticalBehavior.AMBUSH_SETUP:
            return self._execute_ambush_setup(enemy, enemy_pos, player_pos, context)
        
        elif behavior == TacticalBehavior.FLANK_MANEUVER:
            return self._execute_flank_maneuver(enemy, enemy_pos, player_pos, context)
        
        elif behavior == TacticalBehavior.KITE_AROUND_OBSTACLES:
            return self._execute_kite_around_obstacles(enemy, enemy_pos, player_pos, context)
        
        elif behavior == TacticalBehavior.PUSH_INTO_HAZARDS:
            return self._execute_push_into_hazards(enemy, enemy_pos, player_pos, context)
        
        elif behavior == TacticalBehavior.CHOKEPOINT_CONTROL:
            return self._execute_chokepoint_control(enemy, enemy_pos, player_pos, context)
        
        elif behavior == TacticalBehavior.CONCEALMENT_APPROACH:
            return self._execute_concealment_approach(enemy, enemy_pos, player_pos, context)
        
        return {}
    
    def _analyze_situation(self, enemy_pos: Tuple[int, int], 
                          player_pos: Tuple[int, int], 
                          context: Dict[str, Any]) -> Dict[TacticalBehavior, float]:
        """Analyze current tactical situation and score available behaviors"""
        situation_scores = {}
        
        distance_to_player = math.sqrt((player_pos[0] - enemy_pos[0])**2 + 
                                      (player_pos[1] - enemy_pos[1])**2)
        
        # Cover seeking - more valuable when under fire or at medium range
        if 80 < distance_to_player < 200:
            cover_pos = self.environmental_awareness.find_best_cover_position(
                enemy_pos, player_pos
            )
            if cover_pos and cover_pos.overall_rating > 20:
                situation_scores[TacticalBehavior.SEEK_COVER] = cover_pos.overall_rating
        
        # High ground - valuable for ranged combat
        high_ground = self.environmental_awareness.find_high_ground(enemy_pos)
        if high_ground and distance_to_player > 60:
            situation_scores[TacticalBehavior.USE_HIGH_GROUND] = high_ground.elevation_bonus
        
        # Flanking - good when player is near cover or obstacles
        player_terrain = self.environmental_awareness.get_terrain_at_position(player_pos)
        if any(t.terrain_type == TerrainType.COVER for t in player_terrain):
            situation_scores[TacticalBehavior.FLANK_MANEUVER] = 30
        
        # Ambush setup - good when player is moving predictably
        if distance_to_player > 150:
            situation_scores[TacticalBehavior.AMBUSH_SETUP] = 25
        
        # Kiting - good for ranged enemies when player is close
        if distance_to_player < 80:
            situation_scores[TacticalBehavior.KITE_AROUND_OBSTACLES] = 35
        
        # Chokepoint control - valuable when near chokepoints
        chokepoints = self.environmental_awareness.get_chokepoints()
        for chokepoint in chokepoints:
            if chokepoint.distance_to_point(*enemy_pos) < 100:
                situation_scores[TacticalBehavior.CHOKEPOINT_CONTROL] = 40
                break
        
        # Concealment approach - good for ambush or when outmatched
        concealment_available = any(
            t.provides_concealment for t in 
            self.environmental_awareness.get_terrain_at_position(enemy_pos)
        )
        if concealment_available and distance_to_player > 100:
            situation_scores[TacticalBehavior.CONCEALMENT_APPROACH] = 30
        
        return situation_scores
    
    def _get_personality_bonus(self, tactic: TacticalBehavior, 
                              personality_system) -> float:
        """Get personality-based bonus for a tactic"""
        personality_type = personality_system.personality_type
        emotional_state = personality_system.emotional_profile.current_state
        
        bonus = 0.0
        
        # Base personality preferences
        if tactic in self.personality_tactics.get(personality_type, []):
            bonus += 15
        
        # Emotional state modifiers
        if emotional_state == EmotionalState.FEARFUL:
            if tactic in [TacticalBehavior.SEEK_COVER, TacticalBehavior.CONCEALMENT_APPROACH]:
                bonus += 20
            elif tactic in [TacticalBehavior.FLANK_MANEUVER, TacticalBehavior.PUSH_INTO_HAZARDS]:
                bonus -= 15
        
        elif emotional_state == EmotionalState.ANGRY:
            if tactic in [TacticalBehavior.FLANK_MANEUVER, TacticalBehavior.PUSH_INTO_HAZARDS]:
                bonus += 15
            elif tactic in [TacticalBehavior.SEEK_COVER, TacticalBehavior.CONCEALMENT_APPROACH]:
                bonus -= 10
        
        elif emotional_state == EmotionalState.CONFIDENT:
            if tactic in [TacticalBehavior.USE_HIGH_GROUND, TacticalBehavior.AMBUSH_SETUP]:
                bonus += 10
        
        return bonus
    
    def _get_learning_bonus(self, tactic: TacticalBehavior, enemy) -> float:
        """Get learning-based bonus for adaptive personalities"""
        personality_system = getattr(enemy, 'personality_system', None)
        if not personality_system:
            return 0.0
        
        if personality_system.personality_type != Personality.ADAPTIVE:
            return 0.0
        
        # Get success rate from learning memory
        tactic_name = tactic.value
        confidence = personality_system.learning_memory.get_tactic_confidence(tactic_name)
        
        # Higher confidence = higher bonus (up to +20)
        return (confidence - 0.5) * 40  # Maps 0.5-1.0 to 0-20
    
    def _execute_seek_cover(self, enemy, enemy_pos: Tuple[int, int], 
                           player_pos: Tuple[int, int], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cover seeking behavior"""
        cover_pos = self.environmental_awareness.find_best_cover_position(
            enemy_pos, player_pos
        )
        
        if cover_pos:
            return {
                'move_to': (cover_pos.x, cover_pos.y),
                'behavior': 'seek_cover',
                'priority': 'high',
                'maintain_sight': True  # Try to keep line of sight to player
            }
        
        return {}
    
    def _execute_use_high_ground(self, enemy, enemy_pos: Tuple[int, int], 
                                player_pos: Tuple[int, int], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute high ground usage behavior"""
        high_ground = self.environmental_awareness.find_high_ground(enemy_pos)
        
        if high_ground:
            return {
                'move_to': (high_ground.x, high_ground.y),
                'behavior': 'use_high_ground',
                'priority': 'medium',
                'combat_bonus': True  # Indicates this position provides combat advantage
            }
        
        return {}
    
    def _execute_ambush_setup(self, enemy, enemy_pos: Tuple[int, int], 
                             player_pos: Tuple[int, int], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ambush setup behavior"""
        # Predict player movement (simplified)
        player_velocity = context.get('player_velocity', (0, 0))
        predicted_path = []
        
        # Simple prediction - extend current velocity
        for i in range(1, 6):  # Predict 5 steps ahead
            pred_x = player_pos[0] + player_velocity[0] * i * 30
            pred_y = player_pos[1] + player_velocity[1] * i * 30
            predicted_path.append((pred_x, pred_y))
        
        ambush_positions = self.environmental_awareness.find_ambush_positions(predicted_path)
        
        if ambush_positions:
            best_ambush = max(ambush_positions, key=lambda p: p.overall_rating)
            return {
                'move_to': (best_ambush.x, best_ambush.y),
                'behavior': 'ambush_setup',
                'priority': 'medium',
                'wait_for_player': True,  # Wait in position instead of pursuing
                'concealed': True
            }
        
        return {}
    
    def _execute_flank_maneuver(self, enemy, enemy_pos: Tuple[int, int], 
                               player_pos: Tuple[int, int], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute flanking maneuver"""
        # Calculate flanking positions (90 degrees from player's facing)
        player_facing = context.get('player_facing', 0)  # Player's facing direction
        
        flank_angles = [player_facing + 90, player_facing - 90]  # Left and right flanks
        best_flank = None
        best_rating = -1
        
        for angle in flank_angles:
            rad = math.radians(angle)
            flank_distance = 120  # Flanking distance
            
            flank_x = int(player_pos[0] + math.cos(rad) * flank_distance)
            flank_y = int(player_pos[1] + math.sin(rad) * flank_distance)
            
            # Check if flanking position is viable
            if self.environmental_awareness.is_position_safe((flank_x, flank_y)):
                # Calculate path difficulty
                path_clear = True
                # Simple path checking - in real implementation you'd use proper pathfinding
                
                if path_clear:
                    flank_position = TacticalPosition(flank_x, flank_y)
                    self.environmental_awareness._analyze_tactical_position(
                        flank_position, enemy_pos, player_pos
                    )
                    
                    if flank_position.overall_rating > best_rating:
                        best_rating = flank_position.overall_rating
                        best_flank = flank_position
        
        if best_flank:
            return {
                'move_to': (best_flank.x, best_flank.y),
                'behavior': 'flank_maneuver',
                'priority': 'high',
                'approach_stealthily': True,
                'coordinate_timing': True  # Should coordinate with allies
            }
        
        return {}
    
    def _execute_kite_around_obstacles(self, enemy, enemy_pos: Tuple[int, int], 
                                      player_pos: Tuple[int, int], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute kiting behavior around obstacles"""
        # Find nearest cover between enemy and player
        nearby_cover = None
        min_distance = float('inf')
        
        for feature in self.environmental_awareness.terrain_features:
            if feature.terrain_type == TerrainType.COVER:
                center = feature.get_center()
                distance = math.sqrt((center[0] - enemy_pos[0])**2 + 
                                   (center[1] - enemy_pos[1])**2)
                
                if distance < min_distance and distance < 100:
                    min_distance = distance
                    nearby_cover = feature
        
        if nearby_cover:
            # Position on opposite side of cover from player
            cover_center = nearby_cover.get_center()
            
            # Vector from player to cover center
            to_cover_x = cover_center[0] - player_pos[0]
            to_cover_y = cover_center[1] - player_pos[1]
            
            # Normalize and extend beyond cover
            distance = math.sqrt(to_cover_x**2 + to_cover_y**2)
            if distance > 0:
                extend_distance = max(nearby_cover.width, nearby_cover.height) + 30
                kite_x = cover_center[0] + (to_cover_x / distance) * extend_distance
                kite_y = cover_center[1] + (to_cover_y / distance) * extend_distance
                
                return {
                    'move_to': (kite_x, kite_y),
                    'behavior': 'kite_around_obstacles',
                    'priority': 'high',
                    'maintain_distance': True,
                    'use_ranged_attacks': True
                }
        
        return {}
    
    def _execute_push_into_hazards(self, enemy, enemy_pos: Tuple[int, int], 
                                  player_pos: Tuple[int, int], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute behavior to push player into hazards"""
        # Find hazards near player
        hazards_near_player = []
        
        for feature in self.environmental_awareness.terrain_features:
            if feature.terrain_type == TerrainType.HAZARD:
                distance = feature.distance_to_point(*player_pos)
                if distance < 150:  # Hazard is reasonably close to player
                    hazards_near_player.append((feature, distance))
        
        if hazards_near_player:
            # Choose closest hazard
            hazards_near_player.sort(key=lambda x: x[1])
            target_hazard = hazards_near_player[0][0]
            hazard_center = target_hazard.get_center()
            
            # Position to drive player toward hazard
            # Position on opposite side of player from hazard
            to_player_x = player_pos[0] - hazard_center[0]
            to_player_y = player_pos[1] - hazard_center[1]
            
            distance = math.sqrt(to_player_x**2 + to_player_y**2)
            if distance > 0:
                push_distance = distance + 50  # Position beyond player
                push_x = hazard_center[0] + (to_player_x / distance) * push_distance
                push_y = hazard_center[1] + (to_player_y / distance) * push_distance
                
                return {
                    'move_to': (push_x, push_y),
                    'behavior': 'push_into_hazards',
                    'priority': 'medium',
                    'aggressive_approach': True,
                    'target_hazard': hazard_center
                }
        
        return {}
    
    def _execute_chokepoint_control(self, enemy, enemy_pos: Tuple[int, int], 
                                   player_pos: Tuple[int, int], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute chokepoint control behavior"""
        chokepoints = self.environmental_awareness.get_chokepoints()
        
        if chokepoints:
            # Find best chokepoint to control
            best_chokepoint = None
            best_value = -1
            
            for chokepoint in chokepoints:
                # Value based on position relative to player
                center = chokepoint.get_center()
                distance_to_enemy = chokepoint.distance_to_point(*enemy_pos)
                distance_to_player = chokepoint.distance_to_point(*player_pos)
                
                # Prefer chokepoints closer to enemy but between enemy and player
                value = max(0, 200 - distance_to_enemy)
                if distance_to_enemy < distance_to_player:
                    value += 50  # Bonus for being on player's side
                
                if value > best_value:
                    best_value = value
                    best_chokepoint = chokepoint
            
            if best_chokepoint:
                center = best_chokepoint.get_center()
                return {
                    'move_to': center,
                    'behavior': 'chokepoint_control',
                    'priority': 'high',
                    'hold_position': True,
                    'block_passage': True
                }
        
        return {}
    
    def _execute_concealment_approach(self, enemy, enemy_pos: Tuple[int, int], 
                                     player_pos: Tuple[int, int], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute concealed approach behavior"""
        # Find concealed positions closer to player
        concealment_features = [
            f for f in self.environmental_awareness.terrain_features 
            if f.provides_concealment
        ]
        
        best_concealment = None
        best_score = -1
        
        for feature in concealment_features:
            center = feature.get_center()
            distance_to_player = math.sqrt((center[0] - player_pos[0])**2 + 
                                         (center[1] - player_pos[1])**2)
            distance_to_enemy = math.sqrt((center[0] - enemy_pos[0])**2 + 
                                        (center[1] - enemy_pos[1])**2)
            
            # Prefer positions closer to player but not too close
            if 50 < distance_to_player < 120 and distance_to_enemy > 30:
                score = 150 - distance_to_player  # Closer to player = better
                
                if score > best_score:
                    best_score = score
                    best_concealment = feature
        
        if best_concealment:
            center = best_concealment.get_center()
            return {
                'move_to': center,
                'behavior': 'concealment_approach',
                'priority': 'medium',
                'move_stealthily': True,
                'avoid_detection': True
            }
        
        return {}
    
    def record_tactic_result(self, enemy, tactic: TacticalBehavior, success: bool):
        """Record the result of a tactical behavior for learning"""
        personality_system = getattr(enemy, 'personality_system', None)
        if personality_system and personality_system.personality_type == Personality.ADAPTIVE:
            # Record in personality's learning memory
            personality_system.learning_memory.record_tactic_result(tactic.value, success)
            
            # Also record in global tactic memory
            tactic_key = f"{enemy.enemy_type}_{tactic.value}"
            if tactic_key not in self.tactic_success_rates:
                self.tactic_success_rates[tactic_key] = {'success': 0, 'total': 0}
            
            self.tactic_success_rates[tactic_key]['total'] += 1
            if success:
                self.tactic_success_rates[tactic_key]['success'] += 1

# Global environmental tactics instance
_environmental_tactics = None

def get_environmental_tactics() -> EnvironmentalTactics:
    """Get the global environmental tactics instance"""
    global _environmental_tactics
    if _environmental_tactics is None:
        _environmental_tactics = EnvironmentalTactics()
    return _environmental_tactics
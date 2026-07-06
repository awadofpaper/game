"""
Advanced AI Behavior Tree Factory
Creates dynamic behavior trees based on enemy type and personality
"""

import random
import math
from typing import Dict, List, Any, Callable
from ai_personality_system import (
    BehaviorNode, ActionNode, ConditionNode, SequenceNode, 
    SelectorNode, ParallelNode, BehaviorResult, Personality, EmotionalState
)


class BehaviorTreeFactory:
    """Factory for creating behavior trees based on enemy characteristics"""

    def _player_too_close_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if player is too close to the enemy (for ranged AI to retreat)."""
        # Placeholder: always return False
        return False

    def __init__(self):
        # Pre-defined behavior patterns
        self.behavior_patterns = {
            'aggressive_melee': self._create_aggressive_melee_tree,
            'defensive_ranged': self._create_defensive_ranged_tree,
            'tactical_leader': self._create_tactical_leader_tree,
            'berserker_rush': self._create_berserker_rush_tree,
            'cowardly_hit_run': self._create_cowardly_hit_run_tree,
            'adaptive_fighter': self._create_adaptive_fighter_tree,
            'protective_guardian': self._create_protective_guardian_tree,
            'cautious_sniper': self._create_cautious_sniper_tree
        }
        
        print("Behavior Tree Factory initialized")
    
    def create_tree_for_enemy(self, enemy_type: str, personality: Personality, 
                            combat_role: str = "melee") -> BehaviorNode:
        """Create a behavior tree for a specific enemy"""
        
        # Determine base pattern from personality and role
        if personality == Personality.AGGRESSIVE:
            pattern = 'aggressive_melee' if combat_role == 'melee' else 'defensive_ranged'
        elif personality == Personality.COWARDLY:
            pattern = 'cowardly_hit_run'
        elif personality == Personality.TACTICAL:
            pattern = 'tactical_leader'
        elif personality == Personality.BERSERKER:
            pattern = 'berserker_rush'
        elif personality == Personality.CAUTIOUS:
            pattern = 'cautious_sniper' if combat_role == 'ranged' else 'defensive_ranged'
        elif personality == Personality.PROTECTIVE:
            pattern = 'protective_guardian'
        elif personality == Personality.ADAPTIVE:
            pattern = 'adaptive_fighter'
        else:
            pattern = 'aggressive_melee'  # Default
        
        # Create the base tree
        if pattern in self.behavior_patterns:
            return self.behavior_patterns[pattern](enemy_type, personality)
        else:
            return self._create_default_tree(enemy_type, personality)
    
    def _create_aggressive_melee_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create behavior tree for aggressive melee fighters"""
        return SelectorNode("AggressiveMelee", [
            # Emergency behaviors
            SequenceNode("EmergencyRetreat", [
                ConditionNode("HealthCritical", self._health_critical_condition),
                ConditionNode("NoAlliesNearby", self._no_allies_condition),
                ActionNode("FleeToSafety", self._flee_action)
            ]),
            
            # Combat behaviors
            SequenceNode("AggressiveCombat", [
                ConditionNode("PlayerInRange", self._player_in_melee_range_condition),
                SelectorNode("CombatOptions", [
                    # Special attacks when angry
                    SequenceNode("RageAttack", [
                        ConditionNode("IsAngry", self._is_angry_condition),
                        ActionNode("PowerAttack", self._power_attack_action)
                    ]),
                    # Normal melee attack
                    ActionNode("MeleeAttack", self._melee_attack_action)
                ])
            ]),
            
            # Pursuit behaviors
            SequenceNode("PursuePlayer", [
                ConditionNode("PlayerVisible", self._player_visible_condition),
                ActionNode("ChargeAtPlayer", self._charge_action)
            ]),
            
            # Search and patrol
            ActionNode("SearchForPlayer", self._search_action)
        ])
    
    def _create_defensive_ranged_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create behavior tree for defensive ranged fighters"""
        return SelectorNode("DefensiveRanged", [
            # Emergency behaviors
            SequenceNode("EmergencyRetreat", [
                ConditionNode("PlayerTooClose", self._player_too_close_condition),
                ActionNode("CreateDistance", self._create_distance_action)
            ]),
            
            # Ranged combat
            SequenceNode("RangedCombat", [
                ConditionNode("PlayerInRangedRange", self._player_in_ranged_range_condition),
                ConditionNode("HasAmmo", self._has_ammo_condition),
                ParallelNode("RangedAttackSequence", [
                    ActionNode("AimAtPlayer", self._aim_action),
                    ActionNode("RangedAttack", self._ranged_attack_action),
                    ActionNode("MaintainDistance", self._maintain_distance_action)
                ])
            ]),
            
            # Repositioning
            SequenceNode("FindBetterPosition", [
                ConditionNode("PositionCompromised", self._position_compromised_condition),
                ActionNode("FindCover", self._find_cover_action)
            ]),
            
            # Patrol
            ActionNode("PatrolArea", self._patrol_action)
        ])
    
    def _create_tactical_leader_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create behavior tree for tactical leaders"""
        return SelectorNode("TacticalLeader", [
            # Leadership behaviors
            SequenceNode("CommandTroops", [
                ConditionNode("HasAllies", self._has_allies_condition),
                SelectorNode("LeadershipActions", [
                    SequenceNode("CallReinforcements", [
                        ConditionNode("Outnumbered", self._outnumbered_condition),
                        ActionNode("CallForHelp", self._call_for_help_action)
                    ]),
                    SequenceNode("CoordinateAttack", [
                        ConditionNode("PlayerInSight", self._player_visible_condition),
                        ActionNode("IssueAttackOrders", self._issue_attack_orders_action)
                    ]),
                    ActionNode("MaintainFormation", self._maintain_formation_action)
                ])
            ]),
            
            # Personal combat (when necessary)
            SequenceNode("PersonalCombat", [
                ConditionNode("MustFightPersonally", self._must_fight_personally_condition),
                SelectorNode("SmartCombat", [
                    ActionNode("TacticalAttack", self._tactical_attack_action),
                    ActionNode("DefensiveManeuver", self._defensive_maneuver_action)
                ])
            ]),
            
            # Positioning and observation
            ActionNode("AnalyzeBattlefield", self._analyze_battlefield_action)
        ])
    
    def _create_berserker_rush_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create behavior tree for berserker fighters"""
        return SelectorNode("BerserkerRush", [
            # Berserker rage mode
            SequenceNode("RageMode", [
                ConditionNode("InRage", self._in_rage_condition),
                SelectorNode("RageActions", [
                    SequenceNode("FrenziedAttack", [
                        ConditionNode("PlayerInRange", self._player_in_melee_range_condition),
                        ActionNode("FrenziedMeleeAttack", self._frenzied_attack_action)
                    ]),
                    ActionNode("ChargeRecklessly", self._reckless_charge_action)
                ])
            ]),
            
            # Build up rage
            SequenceNode("BuildRage", [
                ConditionNode("PlayerVisible", self._player_visible_condition),
                ActionNode("WorkIntoRage", self._build_rage_action)
            ]),
            
            # Basic aggressive pursuit
            ActionNode("AggressivePursuit", self._aggressive_pursuit_action)
        ])
    
    def _create_cowardly_hit_run_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create behavior tree for cowardly hit-and-run fighters"""
        return SelectorNode("CowardlyHitRun", [
            # Immediate flee conditions
            SequenceNode("ImmediateFlee", [
                SelectorNode("FleeConditions", [
                    ConditionNode("HealthLow", self._health_low_condition),
                    ConditionNode("Outnumbered", self._outnumbered_condition),
                    ConditionNode("PlayerTooStrong", self._player_too_strong_condition)
                ]),
                ActionNode("FleeToAllies", self._flee_action)
            ]),
            
            # Opportunistic attacks
            SequenceNode("OpportunisticAttack", [
                ConditionNode("PlayerDistracted", self._player_distracted_condition),
                ConditionNode("HasAdvantage", self._has_advantage_condition),
                ActionNode("QuickStrike", self._quick_strike_action),
                ActionNode("ImmediateRetreat", self._immediate_retreat_action)
            ]),
            
            # Cautious approach
            SequenceNode("CautiousApproach", [
                ConditionNode("PlayerVisible", self._player_visible_condition),
                ActionNode("StalkFromDistance", self._stalk_action)
            ]),
            
            # Hide and observe
            ActionNode("HideAndObserve", self._hide_action)
        ])
    
    def _create_adaptive_fighter_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create behavior tree for adaptive fighters that learn"""
        return SelectorNode("AdaptiveFighter", [
            # Learned behaviors (based on memory)
            SequenceNode("LearnedBehavior", [
                ConditionNode("HasLearnedPattern", self._has_learned_pattern_condition),
                ActionNode("ExecuteLearnedTactic", self._execute_learned_tactic_action)
            ]),
            
            # Experimental behaviors
            SequenceNode("ExperimentalBehavior", [
                ConditionNode("ShouldExperiment", self._should_experiment_condition),
                ActionNode("TryNewTactic", self._try_new_tactic_action)
            ]),
            
            # Standard combat with adaptation
            SequenceNode("AdaptiveCombat", [
                ConditionNode("PlayerInRange", self._player_in_combat_range_condition),
                SelectorNode("AdaptiveAttacks", [
                    ActionNode("CounterPlayerStyle", self._counter_player_style_action),
                    ActionNode("StandardAttack", self._standard_attack_action)
                ])
            ]),
            
            # Learning observation
            ActionNode("ObserveAndLearn", self._observe_and_learn_action)
        ])
    
    def _create_protective_guardian_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create behavior tree for protective guardians"""
        return SelectorNode("ProtectiveGuardian", [
            # Emergency retreat when critical
            SequenceNode("EmergencyRetreat", [
                ConditionNode("HealthCritical", self._health_critical_condition),
                ActionNode("Flee", self._flee_action)
            ]),
            
            # Defensive combat - protect area
            SequenceNode("DefensiveCombat", [
                ConditionNode("PlayerInMeleeRange", self._player_in_melee_range_condition),
                ActionNode("MeleeAttack", self._melee_attack_action)
            ]),
            
            # Guard position when player visible
            SequenceNode("GuardAndWatch", [
                ConditionNode("PlayerVisible", self._player_visible_condition),
                ActionNode("BasicAttack", self._basic_attack_action)
            ]),
            
            # Patrol when idle
            ActionNode("Patrol", self._basic_patrol_action)
        ])
    
    def _create_cautious_sniper_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create behavior tree for cautious snipers"""
        return SelectorNode("CautiousSniper", [
            # Flee when health is low
            SequenceNode("FleeWhenLow", [
                ConditionNode("HealthLow", self._health_low_condition),
                ActionNode("Flee", self._flee_action)
            ]),
            
            # Ranged combat
            SequenceNode("RangedAttack", [
                ConditionNode("PlayerInRangedRange", self._player_in_ranged_range_condition),
                ActionNode("BasicAttack", self._basic_attack_action)
            ]),
            
            # Retreat if player too close
            SequenceNode("KeepDistance", [
                ConditionNode("PlayerTooClose", self._player_too_close_condition),
                ActionNode("Flee", self._flee_action)
            ]),
            
            # Search for player
            ActionNode("Search", self._search_action)
        ])
    
    def _create_default_tree(self, enemy_type: str, personality: Personality) -> BehaviorNode:
        """Create a default behavior tree"""
        return SelectorNode("DefaultBehavior", [
            SequenceNode("BasicCombat", [
                ConditionNode("PlayerInRange", self._player_in_combat_range_condition),
                ActionNode("BasicAttack", self._basic_attack_action)
            ]),
            ActionNode("BasicPatrol", self._basic_patrol_action)
        ])
    
    # Condition Functions
    def _health_critical_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if enemy health is critical"""
        health_ratio = getattr(enemy, 'health', 100) / getattr(enemy, 'max_health', 100)
        # Use default threshold of 0.2 (20% health)
        return health_ratio < 0.2
    
    def _health_low_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if enemy health is low"""
        health_ratio = getattr(enemy, 'health', 100) / getattr(enemy, 'max_health', 100)
        return health_ratio < 0.4
    
    def _no_allies_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if no allies are nearby"""
        # Would integrate with group system
        group = context.get('ai_group')
        return group is None or len(group.members) <= 1
    
    def _player_in_melee_range_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if player is in melee range"""
        player_pos = context.get('player_pos', (0, 0))
        enemy_rect = getattr(enemy, 'rect', None)
        if enemy_rect:
            enemy_x, enemy_y = enemy_rect.x, enemy_rect.y
        else:
            enemy_x, enemy_y = 0, 0
        distance = ((player_pos[0] - enemy_x)**2 + (player_pos[1] - enemy_y)**2)**0.5
        return distance < 50  # Melee range
    
    def _player_in_ranged_range_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if player is in ranged range"""
        player_pos = context.get('player_pos', (0, 0))
        enemy_rect = getattr(enemy, 'rect', None)
        if enemy_rect:
            enemy_x, enemy_y = enemy_rect.x, enemy_rect.y
        else:
            enemy_x, enemy_y = 0, 0
        distance = ((player_pos[0] - enemy_x)**2 + (player_pos[1] - enemy_y)**2)**0.5
        return 60 < distance < 200  # Ranged range
    
    def _player_in_combat_range_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if player is in any combat range"""
        return (self._player_in_melee_range_condition(enemy, context) or 
                self._player_in_ranged_range_condition(enemy, context))
    
    def _player_visible_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if player is visible"""
        # Would integrate with line-of-sight system
        player_pos = context.get('player_pos', (0, 0))
        enemy_rect = getattr(enemy, 'rect', None)
        if enemy_rect:
            enemy_x, enemy_y = enemy_rect.x, enemy_rect.y
        else:
            enemy_x, enemy_y = 0, 0
        distance = ((player_pos[0] - enemy_x)**2 + (player_pos[1] - enemy_y)**2)**0.5
        return distance < 300  # Visibility range
    
    def _is_angry_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if enemy is angry"""
        personality = context.get('personality_system')
        if personality:
            return personality.emotional_profile.current_state == EmotionalState.ANGRY
        return False
    
    def _in_rage_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if enemy is in berserker rage"""
        personality = context.get('personality_system')
        if personality:
            return (personality.emotional_profile.anger_level > 0.7 and
                   personality.traits.aggression > 0.8)
        return False
    
    def _has_allies_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if enemy has allies"""
        group = context.get('ai_group')
        return group is not None and len(group.members) > 1
    
    def _outnumbered_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if enemy is outnumbered"""
        group = context.get('ai_group')
        if group:
            return len(group.members) < 2  # Simplified outnumbered check
        return True

    def _player_too_strong_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if player is much stronger than the enemy (for cowardly AI)."""
        player_stats = context.get('player_stats', {})
        enemy_stats = getattr(enemy, 'stats', {})
        # Use 'Strength' as a proxy, fallback to level or health if not present
        player_strength = player_stats.get('Strength') or player_stats.get('strength') or player_stats.get('level') or player_stats.get('health') or 10
        enemy_strength = enemy_stats.get('Strength') if isinstance(enemy_stats, dict) else getattr(enemy, 'strength', 10)
        if enemy_strength is None:
            enemy_strength = getattr(enemy, 'level', 10)
        if enemy_strength is None:
            enemy_strength = getattr(enemy, 'health', 10)
        try:
            return player_strength >= 1.5 * enemy_strength
        except Exception:
            return False
    
    def _player_distracted_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if player is distracted (fighting other enemies or facing away)."""
        # Check if there are other enemies nearby engaging the player
        all_enemies = context.get('all_enemies', [])
        if not all_enemies:
            return False
        
        # Count enemies closer to player than this enemy
        player = context.get('player')
        if not player:
            return False
        
        enemy_dist = enemy.distance_to_player if hasattr(enemy, 'distance_to_player') else 999999
        
        closer_enemies = 0
        for other_enemy in all_enemies:
            if other_enemy is enemy:
                continue
            other_dist = getattr(other_enemy, 'distance_to_player', 999999)
            if other_dist < enemy_dist and other_dist < 150:  # Within engagement range
                closer_enemies += 1
        
        # Player is distracted if fighting other enemies
        return closer_enemies > 0
    
    def _has_advantage_condition(self, enemy, context: Dict[str, Any]) -> bool:
        """Check if enemy has tactical advantage over player."""
        player_stats = context.get('player_stats', {})
        
        # Advantage if player health is low
        player_health = player_stats.get('health', 100)
        player_max_health = player_stats.get('max_health', 100)
        if player_max_health > 0:
            health_ratio = player_health / player_max_health
            if health_ratio < 0.3:  # Player below 30% health
                return True
        
        # Advantage if enemy has allies nearby
        allies_nearby = len([e for e in context.get('all_enemies', []) 
                            if e is not enemy and getattr(e, 'distance_to_player', 999999) < 200])
        if allies_nearby >= 2:
            return True
        
        # Advantage if enemy health is good
        enemy_health_ratio = enemy.health / enemy.max_health if hasattr(enemy, 'max_health') and enemy.max_health > 0 else 1.0
        if enemy_health_ratio > 0.7:  # Enemy above 70% health
            return True
        
        return False
    
    # Action Functions
    def _basic_attack_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Basic attack action"""
        if hasattr(enemy, 'attack_player'):
            enemy.attack_player = True
            return BehaviorResult.SUCCESS
        return BehaviorResult.FAILURE
    
    def _melee_attack_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Melee attack with personality modifiers"""
        personality = context.get('personality_system')
        
        if hasattr(enemy, 'attack_player'):
            enemy.attack_player = True
            
            # Apply base damage (personality modifiers removed)
            if hasattr(enemy, 'base_damage'):
                enemy.current_damage = enemy.base_damage
            
            # Emotional reactions
            if personality and random.random() < 0.3:  # 30% chance of emotional reaction
                personality.react_to_event("attempted_attack", 0.3)
            
            return BehaviorResult.SUCCESS
        return BehaviorResult.FAILURE
    
    def _power_attack_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Powerful attack when angry"""
        personality = context.get('personality_system')
        
        if hasattr(enemy, 'attack_player'):
            enemy.attack_player = True
            
            # Enhanced damage when angry
            if personality and hasattr(enemy, 'base_damage'):
                anger_bonus = personality.emotional_profile.anger_level * 0.5
                enemy.current_damage = enemy.base_damage * (1.5 + anger_bonus)
            
            # Consume some anger
            if personality:
                personality.emotional_profile.anger_level *= 0.8
            
            return BehaviorResult.SUCCESS
        return BehaviorResult.FAILURE
    
    def _flee_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Flee from player"""
        player_pos = context.get('player_pos', (0, 0))
        enemy_rect = getattr(enemy, 'rect', None)
        if not enemy_rect:
            return BehaviorResult.FAILURE
        
        enemy_x, enemy_y = enemy_rect.x, enemy_rect.y
        
        # Move away from player
        dx = enemy_x - player_pos[0]
        dy = enemy_y - player_pos[1]
        distance = (dx*dx + dy*dy)**0.5
        
        if distance > 0:
            flee_speed = getattr(enemy, 'speed', 50) * 1.5  # Faster when fleeing
            enemy_rect.x += (dx / distance) * flee_speed * context.get('dt', 0.016)
            enemy_rect.y += (dy / distance) * flee_speed * context.get('dt', 0.016)
            
            # Emotional reaction to fleeing
            personality = context.get('personality_system')
            if personality and random.random() < 0.1:
                personality.react_to_event("fled_from_combat", 0.3)
            
            return BehaviorResult.RUNNING
        
        return BehaviorResult.SUCCESS
    
    def _quick_strike_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Quick opportunistic attack (for cowardly hit-and-run)."""
        if hasattr(enemy, 'attack_player'):
            enemy.attack_player = True
            
            # Quick attack - slightly reduced damage but faster
            if hasattr(enemy, 'base_damage'):
                enemy.current_damage = enemy.base_damage * 0.8  # 80% damage for speed
            
            # Set attack cooldown shorter for quick strikes
            if hasattr(enemy, 'attack_cooldown'):
                enemy.attack_cooldown = getattr(enemy, 'base_attack_cooldown', 1.0) * 0.7
            
            return BehaviorResult.SUCCESS
        return BehaviorResult.FAILURE
    
    def _immediate_retreat_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Immediately retreat after attacking (for cowardly hit-and-run)."""
        player_pos = context.get('player_pos', (0, 0))
        enemy_rect = getattr(enemy, 'rect', None)
        if not enemy_rect:
            return BehaviorResult.FAILURE
        
        enemy_x, enemy_y = enemy_rect.x, enemy_rect.y
        
        # Move away from player quickly
        dx = enemy_x - player_pos[0]
        dy = enemy_y - player_pos[1]
        distance = (dx*dx + dy*dy)**0.5
        
        if distance > 0 and distance < 300:  # Retreat if within 300 pixels
            retreat_speed = getattr(enemy, 'speed', 50) * 2.0  # Very fast retreat
            enemy_rect.x += (dx / distance) * retreat_speed * context.get('dt', 0.016)
            enemy_rect.y += (dy / distance) * retreat_speed * context.get('dt', 0.016)
            
            # Mark that enemy is retreating
            if hasattr(enemy, 'is_retreating'):
                enemy.is_retreating = True
            
            return BehaviorResult.RUNNING
        
        return BehaviorResult.SUCCESS
    
    def _charge_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Charge at player"""
        player_pos = context.get('player_pos', (0, 0))
        enemy_rect = getattr(enemy, 'rect', None)
        if not enemy_rect:
            return BehaviorResult.FAILURE
        
        enemy_x, enemy_y = enemy_rect.x, enemy_rect.y
        
        dx = player_pos[0] - enemy_x
        dy = player_pos[1] - enemy_y
        distance = (dx*dx + dy*dy)**0.5
        
        if distance > 30:  # Still need to move closer
            charge_speed = getattr(enemy, 'speed', 50)
            
            enemy_rect.x += (dx / distance) * charge_speed * context.get('dt', 0.016)
            enemy_rect.y += (dy / distance) * charge_speed * context.get('dt', 0.016)
            
            return BehaviorResult.RUNNING
        
        return BehaviorResult.SUCCESS
    
    def _search_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Search for player"""
        enemy_rect = getattr(enemy, 'rect', None)
        if not enemy_rect:
            return BehaviorResult.FAILURE
        
        # Simple random movement for searching
        if not hasattr(enemy, 'search_direction'):
            enemy.search_direction = random.uniform(0, 2 * 3.14159)
        
        search_speed = getattr(enemy, 'speed', 50) * 0.5
        enemy_rect.x += math.cos(enemy.search_direction) * search_speed * context.get('dt', 0.016)
        enemy_rect.y += math.sin(enemy.search_direction) * search_speed * context.get('dt', 0.016)
        
        # Change direction occasionally
        if random.random() < 0.02:  # 2% chance per frame
            enemy.search_direction = random.uniform(0, 2 * 3.14159)
        
        return BehaviorResult.RUNNING
    
    # More action implementations would go here...
    # For brevity, I'm implementing key actions. The rest would follow similar patterns.
    
    def _basic_patrol_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Basic patrol behavior"""
        return self._search_action(enemy, context)
    
    def _stalk_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Stalk player from a distance (for cowardly enemies)."""
        player_pos = context.get('player_pos', (0, 0))
        enemy_rect = getattr(enemy, 'rect', None)
        if not enemy_rect:
            return BehaviorResult.FAILURE
        
        enemy_x, enemy_y = enemy_rect.centerx, enemy_rect.centery
        
        # Calculate distance to player
        dx = player_pos[0] - enemy_x
        dy = player_pos[1] - enemy_y
        distance = (dx*dx + dy*dy)**0.5
        
        # Maintain a stalking distance (150-250 pixels)
        ideal_distance = 200
        tolerance = 50
        
        if distance < ideal_distance - tolerance:
            # Too close - back away slowly
            if distance > 0:
                stalk_speed = getattr(enemy, 'speed', 50) * 0.5
                enemy_rect.x -= (dx / distance) * stalk_speed * context.get('dt', 0.016)
                enemy_rect.y -= (dy / distance) * stalk_speed * context.get('dt', 0.016)
        elif distance > ideal_distance + tolerance:
            # Too far - move closer slowly
            if distance > 0:
                stalk_speed = getattr(enemy, 'speed', 50) * 0.6
                enemy_rect.x += (dx / distance) * stalk_speed * context.get('dt', 0.016)
                enemy_rect.y += (dy / distance) * stalk_speed * context.get('dt', 0.016)
        
        # Stay in stalking mode
        return BehaviorResult.RUNNING
    
    def _hide_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Hide and observe player (for cowardly enemies)."""
        player_pos = context.get('player_pos', (0, 0))
        enemy_rect = getattr(enemy, 'rect', None)
        if not enemy_rect:
            return BehaviorResult.FAILURE
        
        enemy_x, enemy_y = enemy_rect.centerx, enemy_rect.centery
        
        # Calculate distance to player
        dx = player_pos[0] - enemy_x
        dy = player_pos[1] - enemy_y
        distance = (dx*dx + dy*dy)**0.5
        
        # If too close, move away to hiding distance (300+ pixels)
        if distance < 300:
            if distance > 0:
                hide_speed = getattr(enemy, 'speed', 50) * 0.8
                enemy_rect.x -= (dx / distance) * hide_speed * context.get('dt', 0.016)
                enemy_rect.y -= (dy / distance) * hide_speed * context.get('dt', 0.016)
            return BehaviorResult.RUNNING
        
        # At safe distance - stay hidden and observe
        return BehaviorResult.SUCCESS

    def _frenzied_attack_action(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Frenzied melee attack for berserker/rage mode"""
        # Perform a high-damage attack and apply rage status effect
        personality = context.get('personality_system')
        # Calculate frenzied damage
        base_damage = getattr(enemy, 'base_damage', getattr(enemy, 'damage', 10))
        rage_multiplier = 2.0
        if personality:
            rage_multiplier += personality.emotional_profile.anger_level
        frenzied_damage = int(base_damage * rage_multiplier)
        # Attack player
        if hasattr(enemy, 'attack_player'):
            enemy.attack_player = True
            enemy.current_damage = frenzied_damage
            # Apply rage status effect if available
            if hasattr(enemy, 'apply_status_effect'):
                enemy.apply_status_effect('rage', duration=8.0)
            # Emotional reaction: reduce anger after attack
            if personality:
                personality.react_to_event("frenzied_attack", 0.5)
                personality.emotional_profile.anger_level *= 0.7
            return BehaviorResult.SUCCESS
        return BehaviorResult.FAILURE

# Global factory instance
_behavior_tree_factory = None

def get_behavior_tree_factory() -> BehaviorTreeFactory:
    """Get the global behavior tree factory instance"""
    global _behavior_tree_factory
    if _behavior_tree_factory is None:
        _behavior_tree_factory = BehaviorTreeFactory()
    return _behavior_tree_factory
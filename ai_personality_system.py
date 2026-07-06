"""
Advanced AI Behavior Trees & Personality System
Dynamic enemy personalities with emotional states and adaptive learning
"""

import pygame
import math
import time
import random
import json
from typing import Dict, List, Tuple, Optional, Set, Any
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

class Personality(Enum):
    """Enemy personality types affecting behavior"""
    AGGRESSIVE = "aggressive"
    COWARDLY = "cowardly"
    TACTICAL = "tactical"
    BERSERKER = "berserker"
    CAUTIOUS = "cautious"
    STUBBORN = "stubborn"
    ADAPTIVE = "adaptive"
    PROTECTIVE = "protective"

class EmotionalState(Enum):
    """Emotional states affecting AI decisions"""
    CALM = "calm"
    ANGRY = "angry"
    FEARFUL = "fearful"
    CONFIDENT = "confident"
    DESPERATE = "desperate"
    FOCUSED = "focused"
    PANICKED = "panicked"
    VENGEFUL = "vengeful"

class BehaviorResult(Enum):
    """Results from behavior tree node execution"""
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"
    PENDING = "pending"

@dataclass
class PersonalityTraits:
    """Personality trait values (0.0 to 1.0)"""
    aggression: float = 0.5
    courage: float = 0.5
    intelligence: float = 0.5
    loyalty: float = 0.5
    adaptability: float = 0.5
    patience: float = 0.5
    persistence: float = 0.5
    caution: float = 0.5
    
    def get_trait(self, trait_name: str) -> float:
        """Get a specific trait value"""
        return getattr(self, trait_name, 0.5)
    
    def modify_trait(self, trait_name: str, delta: float):
        """Modify a trait value (with bounds)"""
        if hasattr(self, trait_name):
            current = getattr(self, trait_name)
            new_value = max(0.0, min(1.0, current + delta))
            setattr(self, trait_name, new_value)

@dataclass
class EmotionalProfile:
    """Current emotional state and modifiers"""
    current_state: EmotionalState = EmotionalState.CALM
    anger_level: float = 0.0
    fear_level: float = 0.0
    confidence_level: float = 0.5
    stress_level: float = 0.0
    
    # Emotional decay rates (how quickly emotions fade)
    anger_decay: float = 0.1
    fear_decay: float = 0.15
    stress_decay: float = 0.05
    confidence_growth: float = 0.02
    
    def update(self, dt: float):
        """Update emotional state over time"""
        # Decay emotions naturally
        self.anger_level = max(0.0, self.anger_level - self.anger_decay * dt)
        self.fear_level = max(0.0, self.fear_level - self.fear_decay * dt)
        self.stress_level = max(0.0, self.stress_level - self.stress_decay * dt)
        
        # Confidence slowly returns to baseline
        baseline_confidence = 0.5
        if self.confidence_level < baseline_confidence:
            self.confidence_level = min(baseline_confidence, self.confidence_level + self.confidence_growth * dt)
        
        # Determine dominant emotional state
        self._update_emotional_state()
    
    def _update_emotional_state(self):
        """Update the current emotional state based on levels"""
        if self.fear_level > 0.7:
            self.current_state = EmotionalState.PANICKED if self.stress_level > 0.6 else EmotionalState.FEARFUL
        elif self.anger_level > 0.7:
            self.current_state = EmotionalState.VENGEFUL if self.stress_level > 0.5 else EmotionalState.ANGRY
        elif self.confidence_level > 0.8:
            self.current_state = EmotionalState.CONFIDENT
        elif self.stress_level > 0.6:
            self.current_state = EmotionalState.DESPERATE
        elif self.anger_level > 0.3 and self.confidence_level > 0.6:
            self.current_state = EmotionalState.FOCUSED
        else:
            self.current_state = EmotionalState.CALM
    
    def add_anger(self, amount: float, reason: str = ""):
        """Increase anger level"""
        self.anger_level = min(1.0, self.anger_level + amount)
        self.stress_level = min(1.0, self.stress_level + amount * 0.3)
    
    def add_fear(self, amount: float, reason: str = ""):
        """Increase fear level"""
        self.fear_level = min(1.0, self.fear_level + amount)
        self.confidence_level = max(0.0, self.confidence_level - amount * 0.5)
        self.stress_level = min(1.0, self.stress_level + amount * 0.4)
    
    def add_confidence(self, amount: float, reason: str = ""):
        """Increase confidence level"""
        self.confidence_level = min(1.0, self.confidence_level + amount)
        self.fear_level = max(0.0, self.fear_level - amount * 0.3)

@dataclass
class LearningMemory:
    """AI learning and memory system"""
    player_combat_patterns: Dict[str, float] = field(default_factory=dict)
    successful_tactics: Dict[str, int] = field(default_factory=dict)
    failed_tactics: Dict[str, int] = field(default_factory=dict)
    damage_taken_by_ability: Dict[str, float] = field(default_factory=dict)
    damage_dealt_by_ability: Dict[str, float] = field(default_factory=dict)
    
    # Learning rates
    learning_rate: float = 0.1
    memory_decay_rate: float = 0.01
    
    def learn_player_pattern(self, pattern: str, effectiveness: float):
        """Learn about player combat patterns"""
        if pattern not in self.player_combat_patterns:
            self.player_combat_patterns[pattern] = 0.0
        
        # Update with weighted average
        current = self.player_combat_patterns[pattern]
        self.player_combat_patterns[pattern] = current * (1 - self.learning_rate) + effectiveness * self.learning_rate
    
    def record_tactic_result(self, tactic: str, success: bool):
        """Record the success/failure of a tactic"""
        if success:
            self.successful_tactics[tactic] = self.successful_tactics.get(tactic, 0) + 1
        else:
            self.failed_tactics[tactic] = self.failed_tactics.get(tactic, 0) + 1
    
    def get_tactic_confidence(self, tactic: str) -> float:
        """Get confidence in a tactic (0.0 to 1.0)"""
        successes = self.successful_tactics.get(tactic, 0)
        failures = self.failed_tactics.get(tactic, 0)
        
        if successes + failures == 0:
            return 0.5  # Unknown tactic
        
        return successes / (successes + failures)
    
    def decay_memories(self, dt: float):
        """Gradually decay old memories"""
        decay_amount = self.memory_decay_rate * dt
        
        # Decay player patterns
        for pattern in list(self.player_combat_patterns.keys()):
            self.player_combat_patterns[pattern] *= (1 - decay_amount)
            if self.player_combat_patterns[pattern] < 0.1:
                del self.player_combat_patterns[pattern]

# Behavior Tree Node Classes
class BehaviorNode(ABC):
    """Abstract base class for behavior tree nodes"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_result = BehaviorResult.PENDING
        self.last_execution_time = 0
    
    @abstractmethod
    def execute(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Execute the behavior node"""
        pass
    
    def reset(self):
        """Reset node state"""
        self.last_result = BehaviorResult.PENDING

class ActionNode(BehaviorNode):
    """Leaf node that performs an action"""
    
    def __init__(self, name: str, action_func):
        super().__init__(name)
        self.action_func = action_func
    
    def execute(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Execute the action"""
        try:
            result = self.action_func(enemy, context)
            self.last_result = result
            self.last_execution_time = time.time()
            return result
        except Exception as e:
            print(f"Error executing action {self.name}: {e}")
            return BehaviorResult.FAILURE

class ConditionNode(BehaviorNode):
    """Node that checks a condition"""
    
    def __init__(self, name: str, condition_func):
        super().__init__(name)
        self.condition_func = condition_func
    
    def execute(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Check the condition"""
        try:
            if self.condition_func(enemy, context):
                return BehaviorResult.SUCCESS
            else:
                return BehaviorResult.FAILURE
        except Exception as e:
            print(f"Error checking condition {self.name}: {e}")
            return BehaviorResult.FAILURE

class SequenceNode(BehaviorNode):
    """Node that executes children in sequence (AND logic)"""
    
    def __init__(self, name: str, children: List[BehaviorNode]):
        super().__init__(name)
        self.children = children
        self.current_child = 0
    
    def execute(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Execute children in sequence"""
        while self.current_child < len(self.children):
            result = self.children[self.current_child].execute(enemy, context)
            
            if result == BehaviorResult.FAILURE:
                self.reset()
                return BehaviorResult.FAILURE
            elif result == BehaviorResult.RUNNING:
                return BehaviorResult.RUNNING
            elif result == BehaviorResult.SUCCESS:
                self.current_child += 1
            else:
                return BehaviorResult.FAILURE
        
        # All children succeeded
        self.reset()
        return BehaviorResult.SUCCESS
    
    def reset(self):
        super().reset()
        self.current_child = 0
        for child in self.children:
            child.reset()

class SelectorNode(BehaviorNode):
    """Node that tries children until one succeeds (OR logic)"""
    
    def __init__(self, name: str, children: List[BehaviorNode]):
        super().__init__(name)
        self.children = children
        self.current_child = 0
    
    def execute(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Try children until one succeeds"""
        while self.current_child < len(self.children):
            result = self.children[self.current_child].execute(enemy, context)
            
            if result == BehaviorResult.SUCCESS:
                self.reset()
                return BehaviorResult.SUCCESS
            elif result == BehaviorResult.RUNNING:
                return BehaviorResult.RUNNING
            elif result == BehaviorResult.FAILURE:
                self.current_child += 1
            else:
                return BehaviorResult.FAILURE
        
        # All children failed
        self.reset()
        return BehaviorResult.FAILURE
    
    def reset(self):
        super().reset()
        self.current_child = 0
        for child in self.children:
            child.reset()

class ParallelNode(BehaviorNode):
    """Node that executes all children simultaneously"""
    
    def __init__(self, name: str, children: List[BehaviorNode], success_threshold: int = None):
        super().__init__(name)
        self.children = children
        self.success_threshold = success_threshold or len(children)  # All must succeed by default
        self.child_results = [BehaviorResult.PENDING] * len(children)
    
    def execute(self, enemy, context: Dict[str, Any]) -> BehaviorResult:
        """Execute all children in parallel"""
        successes = 0
        failures = 0
        running = 0
        
        for i, child in enumerate(self.children):
            if self.child_results[i] == BehaviorResult.PENDING:
                self.child_results[i] = child.execute(enemy, context)
            
            if self.child_results[i] == BehaviorResult.SUCCESS:
                successes += 1
            elif self.child_results[i] == BehaviorResult.FAILURE:
                failures += 1
            elif self.child_results[i] == BehaviorResult.RUNNING:
                running += 1
        
        # Check success condition
        if successes >= self.success_threshold:
            self.reset()
            return BehaviorResult.SUCCESS
        
        # Check failure condition (too many failures)
        if failures > len(self.children) - self.success_threshold:
            self.reset()
            return BehaviorResult.FAILURE
        
        # Still running
        return BehaviorResult.RUNNING
    
    def reset(self):
        super().reset()
        self.child_results = [BehaviorResult.PENDING] * len(self.children)
        for child in self.children:
            child.reset()

class PersonalitySystem:
    """Manages enemy personality and emotional state"""
    
    def __init__(self, personality_type: Personality):
        self.personality_type = personality_type
        self.traits = self._create_personality_traits(personality_type)
        self.emotional_profile = EmotionalProfile()
        self.learning_memory = LearningMemory()
        
        # Behavior modifiers based on personality
        self.behavior_modifiers = self._calculate_behavior_modifiers()
        
        print(f"Created {personality_type.value} personality with traits: {self.traits}")
    
    def _create_personality_traits(self, personality: Personality) -> PersonalityTraits:
        """Create personality traits based on type"""
        base_traits = PersonalityTraits()
        
        if personality == Personality.AGGRESSIVE:
            base_traits.aggression = 0.9
            base_traits.courage = 0.8
            base_traits.patience = 0.2
            base_traits.caution = 0.1
            
        elif personality == Personality.COWARDLY:
            base_traits.aggression = 0.1
            base_traits.courage = 0.2
            base_traits.caution = 0.9
            base_traits.adaptability = 0.7
            
        elif personality == Personality.TACTICAL:
            base_traits.intelligence = 0.9
            base_traits.patience = 0.8
            base_traits.caution = 0.7
            base_traits.adaptability = 0.8
            
        elif personality == Personality.BERSERKER:
            base_traits.aggression = 1.0
            base_traits.courage = 0.9
            base_traits.intelligence = 0.3
            base_traits.patience = 0.1
            base_traits.persistence = 0.9
            
        elif personality == Personality.CAUTIOUS:
            base_traits.caution = 0.9
            base_traits.intelligence = 0.7
            base_traits.patience = 0.8
            base_traits.aggression = 0.3
            
        elif personality == Personality.STUBBORN:
            base_traits.persistence = 0.9
            base_traits.loyalty = 0.8
            base_traits.adaptability = 0.2
            base_traits.courage = 0.7
            
        elif personality == Personality.ADAPTIVE:
            base_traits.adaptability = 0.9
            base_traits.intelligence = 0.8
            base_traits.patience = 0.6
            
        elif personality == Personality.PROTECTIVE:
            base_traits.loyalty = 0.9
            base_traits.courage = 0.8
            base_traits.caution = 0.6
            base_traits.aggression = 0.6
        
        # Add some randomization for uniqueness
        for trait_name in ['aggression', 'courage', 'intelligence', 'loyalty', 'adaptability', 'patience', 'persistence', 'caution']:
            variation = random.uniform(-0.1, 0.1)
            base_traits.modify_trait(trait_name, variation)
        
        return base_traits
    
    def _calculate_behavior_modifiers(self) -> Dict[str, float]:
        """Calculate behavior modifiers based on personality and emotions"""
        modifiers = {
            'attack_frequency': 1.0,
            'retreat_threshold': 0.3,
            'help_call_threshold': 0.5,
            'formation_adherence': 1.0,
            'risk_taking': 0.5,
            'learning_rate': 0.1,
            'reaction_time': 1.0,
            'accuracy_modifier': 1.0,
            'damage_modifier': 1.0,
            'movement_speed': 1.0
        }
        
        # Personality-based modifications
        modifiers['attack_frequency'] = 0.5 + self.traits.aggression
        modifiers['retreat_threshold'] = 0.1 + (1.0 - self.traits.courage) * 0.5
        modifiers['formation_adherence'] = 0.5 + self.traits.loyalty * 0.5
        modifiers['risk_taking'] = self.traits.aggression * 0.5 + (1.0 - self.traits.caution) * 0.5
        modifiers['learning_rate'] = self.traits.intelligence * 0.2
        modifiers['reaction_time'] = 2.0 - self.traits.intelligence
        
        # Emotional modifications
        if self.emotional_profile.current_state == EmotionalState.ANGRY:
            modifiers['attack_frequency'] *= 1.5
            modifiers['accuracy_modifier'] *= 0.8
            modifiers['damage_modifier'] *= 1.2
            
        elif self.emotional_profile.current_state == EmotionalState.FEARFUL:
            modifiers['retreat_threshold'] *= 2.0
            modifiers['accuracy_modifier'] *= 0.7
            modifiers['movement_speed'] *= 1.3
            
        elif self.emotional_profile.current_state == EmotionalState.CONFIDENT:
            modifiers['attack_frequency'] *= 1.3
            modifiers['accuracy_modifier'] *= 1.2
            modifiers['risk_taking'] *= 1.4
            
        elif self.emotional_profile.current_state == EmotionalState.DESPERATE:
            modifiers['attack_frequency'] *= 1.8
            modifiers['retreat_threshold'] *= 0.5
            modifiers['risk_taking'] *= 2.0
            
        elif self.emotional_profile.current_state == EmotionalState.PANICKED:
            modifiers['accuracy_modifier'] *= 0.5
            modifiers['formation_adherence'] *= 0.3
            modifiers['movement_speed'] *= 1.5
        
        return modifiers
    
    def update(self, dt: float):
        """Update personality system"""
        self.emotional_profile.update(dt)
        self.learning_memory.decay_memories(dt)
        self.behavior_modifiers = self._calculate_behavior_modifiers()
    
    def react_to_event(self, event: str, intensity: float = 0.5, context: Dict = None):
        """React to game events emotionally"""
        context = context or {}
        
        if event == "took_damage":
            damage_ratio = context.get('damage_ratio', 0.5)
            if self.traits.courage < 0.5:
                self.emotional_profile.add_fear(damage_ratio * 0.3)
            else:
                self.emotional_profile.add_anger(damage_ratio * 0.4)
                
        elif event == "ally_died":
            if self.traits.loyalty > 0.6:
                self.emotional_profile.add_anger(0.6, "ally death")
                if self.traits.courage < 0.4:
                    self.emotional_profile.add_fear(0.4, "ally death")
                    
        elif event == "dealt_damage":
            self.emotional_profile.add_confidence(0.2, "successful attack")
            
        elif event == "missed_attack":
            if self.personality_type == Personality.BERSERKER:
                self.emotional_profile.add_anger(0.3, "missed attack")
                
        elif event == "player_fled":
            self.emotional_profile.add_confidence(0.4, "player retreat")
            
        elif event == "outnumbered":
            if self.traits.courage < 0.6:
                self.emotional_profile.add_fear(0.5, "outnumbered")
        
        # Learning from events
        if context.get('learn', True):
            self.learning_memory.learn_player_pattern(event, intensity)
    
    def get_behavior_modifier(self, modifier_name: str) -> float:
        """Get a specific behavior modifier"""
        return self.behavior_modifiers.get(modifier_name, 1.0)
    
    def should_use_tactic(self, tactic: str) -> bool:
        """Decide whether to use a specific tactic based on personality and learning"""
        confidence = self.learning_memory.get_tactic_confidence(tactic)
        personality_bonus = 0.0
        
        # Personality influences tactic preferences
        if "aggressive" in tactic.lower():
            personality_bonus = self.traits.aggression * 0.3
        elif "defensive" in tactic.lower():
            personality_bonus = self.traits.caution * 0.3
        elif "tactical" in tactic.lower():
            personality_bonus = self.traits.intelligence * 0.3
        elif "retreat" in tactic.lower():
            personality_bonus = (1.0 - self.traits.courage) * 0.3
        
        final_confidence = confidence + personality_bonus
        risk_threshold = self.get_behavior_modifier('risk_taking')
        
        return final_confidence >= risk_threshold

# Global personality system manager
class PersonalityManager:
    """Manages personality systems for all enemies"""
    
    def __init__(self):
        self.personalities: Dict[str, PersonalitySystem] = {}
        self.personality_templates = {}
        self.global_learning_data = {}
        
        print("Personality Manager initialized")
    
    def create_personality(self, enemy_id: str, personality_type: Personality = None) -> PersonalitySystem:
        """Create a personality system for an enemy"""
        if personality_type is None:
            personality_type = random.choice(list(Personality))
        
        personality_system = PersonalitySystem(personality_type)
        self.personalities[enemy_id] = personality_system
        
        return personality_system
    
    def get_personality(self, enemy_id: str) -> Optional[PersonalitySystem]:
        """Get personality system for an enemy"""
        return self.personalities.get(enemy_id)
    
    def remove_personality(self, enemy_id: str):
        """Remove personality system when enemy dies"""
        if enemy_id in self.personalities:
            del self.personalities[enemy_id]
    
    def update_all_personalities(self, dt: float):
        """Update all personality systems"""
        for personality in self.personalities.values():
            personality.update(dt)
    
    def share_global_learning(self, learner_id: str, knowledge: str, effectiveness: float):
        """Share learning between enemies of the same faction"""
        # This would be used for faction-wide learning
        if knowledge not in self.global_learning_data:
            self.global_learning_data[knowledge] = []
        
        self.global_learning_data[knowledge].append({
            'learner': learner_id,
            'effectiveness': effectiveness,
            'timestamp': time.time()
        })
        
        # Apply learning to other enemies (faction-based learning)
        for enemy_id, personality in self.personalities.items():
            if enemy_id != learner_id:
                personality.learning_memory.learn_player_pattern(knowledge, effectiveness * 0.5)

# Global instance
_personality_manager = None

def get_personality_manager() -> PersonalityManager:
    """Get the global personality manager instance"""
    global _personality_manager
    if _personality_manager is None:
        _personality_manager = PersonalityManager()
    return _personality_manager
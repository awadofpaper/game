"""
Summoning and Necromancy System
Allows players to summon creatures and raise the dead to fight alongside them
"""
import pygame
import random
import math
from typing import List, Optional, Dict
from enum import Enum


class SummonType(Enum):
    """Types of summonable creatures"""
    WOLF = "wolf"
    FIRE_ELEMENTAL = "fire_elemental"
    ICE_ELEMENTAL = "ice_elemental"
    LIGHTNING_ELEMENTAL = "lightning_elemental"
    DEMON = "demon"
    SHADOW_BEAST = "shadow_beast"
    SKELETON = "skeleton"
    ZOMBIE = "zombie"
    GHOST = "ghost"
    BONE_GOLEM = "bone_golem"


class SummonState(Enum):
    """AI states for summoned creatures"""
    FOLLOWING = "following"
    ATTACKING = "attacking"
    DEFENDING = "defending"
    IDLE = "idle"


class SummonedCreature:
    """A summoned creature that fights for the player"""
    
    def __init__(self, summon_type: SummonType, x: float, y: float, summoner, duration: float = 30.0, from_corpse: bool = False):
        self.summon_type = summon_type
        self.x = x
        self.y = y
        self.summoner = summoner  # Reference to player
        self.duration = duration  # Lifetime in seconds
        self.lifetime = 0.0  # Time alive
        self.from_corpse = from_corpse  # True if raised from dead
        
        # State
        self.alive = True
        self.state = SummonState.FOLLOWING
        self.target = None
        
        # Stats based on type and summoner level
        self._initialize_stats()
        
        # Movement
        self.speed = self.base_speed
        self.follow_distance = 80
        self.detection_range = 250
        self.leash_distance = 400  # Max distance from summoner
        
        # Combat
        self.last_attack_time = 0
        self.attack_cooldown = self.base_attack_cooldown
        self.attack_range = self.base_attack_range
        
        # Collision
        self.rect = pygame.Rect(int(self.x - 16), int(self.y - 16), 32, 32)
        
        # Visual effects
        self.animation_frame = 0
        self.animation_timer = 0
        
    def _initialize_stats(self):
        """Initialize stats based on summon type and summoner level"""
        summoner_level = getattr(self.summoner, 'level', 1)
        magic_power = getattr(self.summoner, 'stats', {}).get('Magic', 0)
        
        # Base stats per summon type
        stats = SUMMON_STATS.get(self.summon_type, {})
        
        # Calculate scaled stats
        self.max_health = int(stats.get('health', 50) + summoner_level * 5 + magic_power * 0.5)
        self.health = self.max_health
        self.damage = int(stats.get('damage', 10) + summoner_level * 2 + magic_power * 0.3)
        self.defense = int(stats.get('defense', 5) + summoner_level * 1)
        self.base_speed = stats.get('speed', 100)
        self.base_attack_cooldown = stats.get('attack_cooldown', 1.5)
        self.base_attack_range = stats.get('attack_range', 50)
        
        # Special abilities
        self.abilities = stats.get('abilities', [])
        self.element = stats.get('element', None)
        
        # If raised from corpse, reduce stats by 30%
        if self.from_corpse:
            self.max_health = int(self.max_health * 0.7)
            self.health = self.max_health
            self.damage = int(self.damage * 0.7)
            self.defense = int(self.defense * 0.5)
        
        # Visual properties
        self.color = stats.get('color', (150, 150, 150))
        self.size = stats.get('size', 32)
        
        # Buff system
        self.active_buffs = {}  # {buff_name: {duration: float, multipliers: dict}}
        self.buff_damage_multiplier = 1.0
        self.buff_speed_multiplier = 1.0
        
    def apply_buff(self, buff_name: str, duration: float, damage_boost: float = 0.0, speed_boost: float = 0.0):
        """Apply a buff to this summon"""
        self.active_buffs[buff_name] = {
            'duration': duration,
            'damage_boost': damage_boost,
            'speed_boost': speed_boost
        }
        self._update_buff_multipliers()
    
    def _update_buff_multipliers(self):
        """Recalculate buff multipliers from all active buffs"""
        self.buff_damage_multiplier = 1.0
        self.buff_speed_multiplier = 1.0
        
        for buff_data in self.active_buffs.values():
            self.buff_damage_multiplier += buff_data.get('damage_boost', 0.0)
            self.buff_speed_multiplier += buff_data.get('speed_boost', 0.0)
    
    def _update_buffs(self, dt: float):
        """Update buff durations and remove expired buffs"""
        expired_buffs = []
        
        for buff_name, buff_data in self.active_buffs.items():
            buff_data['duration'] -= dt
            if buff_data['duration'] <= 0:
                expired_buffs.append(buff_name)
        
        for buff_name in expired_buffs:
            del self.active_buffs[buff_name]
        
        if expired_buffs:
            self._update_buff_multipliers()
        
    def update(self, dt: float, enemies: List, player_x: float, player_y: float):
        """Update summon AI and behavior"""
        if not self.alive:
            return
        
        # Update buffs
        self._update_buffs(dt)
        
        # Update lifetime
        self.lifetime += dt
        if self.lifetime >= self.duration and self.duration > 0:
            self.despawn()
            return
        
        # Check leash distance
        distance_to_summoner = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
        if distance_to_summoner > self.leash_distance:
            # Teleport back to summoner if too far
            self.x = player_x + random.randint(-50, 50)
            self.y = player_y + random.randint(-50, 50)
        
        # Update state based on situation
        self._update_state(enemies, player_x, player_y)
        
        # Execute current state behavior
        if self.state == SummonState.FOLLOWING:
            self._follow_summoner(dt, player_x, player_y)
        elif self.state == SummonState.ATTACKING:
            self._attack_behavior(dt)
        elif self.state == SummonState.DEFENDING:
            self._defend_summoner(dt, player_x, player_y)
        
        # Update rect for collision
        self.rect.x = int(self.x - 16)
        self.rect.y = int(self.y - 16)
        
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= 0.1:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
    
    def _update_state(self, enemies: List, player_x: float, player_y: float):
        """Update AI state based on situation"""
        # Check if current target is still valid
        if self.target and (not hasattr(self.target, 'alive') or not self.target.alive):
            self.target = None
            self.state = SummonState.FOLLOWING
        
        # Find nearest enemy
        nearest_enemy = None
        nearest_distance = self.detection_range
        
        for enemy in enemies:
            if not hasattr(enemy, 'alive') or not enemy.alive:
                continue
            
            distance = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_enemy = enemy
        
        # Engage enemy if found
        if nearest_enemy and self.state == SummonState.FOLLOWING:
            self.target = nearest_enemy
            self.state = SummonState.ATTACKING
        
        # Check if summoner is in danger (enemy near summoner)
        if not self.target:
            for enemy in enemies:
                if not hasattr(enemy, 'alive') or not enemy.alive:
                    continue
                
                distance_to_summoner = math.sqrt((enemy.x - player_x)**2 + (enemy.y - player_y)**2)
                if distance_to_summoner < 150:  # Enemy within 150 pixels of summoner
                    self.target = enemy
                    self.state = SummonState.DEFENDING
                    break
    
    def _follow_summoner(self, dt: float, player_x: float, player_y: float):
        """Follow the summoner"""
        # Calculate distance to summoner
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Only move if outside follow distance
        if distance > self.follow_distance:
            # Normalize and move
            if distance > 0:
                dx /= distance
                dy /= distance
                current_speed = self.speed * self.buff_speed_multiplier
                self.x += dx * current_speed * dt
                self.y += dy * current_speed * dt
    
    def _attack_behavior(self, dt: float):
        """Attack current target"""
        if not self.target or not hasattr(self.target, 'alive') or not self.target.alive:
            self.target = None
            self.state = SummonState.FOLLOWING
            return
        
        # Move towards target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.attack_range:
            # Move closer
            if distance > 0:
                dx /= distance
                dy /= distance
                current_speed = self.speed * self.buff_speed_multiplier
                self.x += dx * current_speed * dt
                self.y += dy * current_speed * dt
        else:
            # In range, attack
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.attack_target()
                self.last_attack_time = current_time
    
    def _defend_summoner(self, dt: float, player_x: float, player_y: float):
        """Defend the summoner"""
        # Position between summoner and threat
        if self.target and hasattr(self.target, 'alive') and self.target.alive:
            # Calculate intercept position
            target_dx = self.target.x - player_x
            target_dy = self.target.y - player_y
            target_distance = math.sqrt(target_dx**2 + target_dy**2)
            
            if target_distance > 0:
                # Position 60% of the way to enemy
                intercept_x = player_x + (target_dx / target_distance) * min(100, target_distance * 0.6)
                intercept_y = player_y + (target_dy / target_distance) * min(100, target_distance * 0.6)
                
                # Move to intercept position
                dx = intercept_x - self.x
                dy = intercept_y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 20:
                    if distance > 0:
                        dx /= distance
                        dy /= distance
                        current_speed = self.speed * self.buff_speed_multiplier
                        self.x += dx * current_speed * dt
                        self.y += dy * current_speed * dt
                
                # Attack if in range
                dist_to_target = math.sqrt((self.target.x - self.x)**2 + (self.target.y - self.y)**2)
                if dist_to_target <= self.attack_range:
                    current_time = pygame.time.get_ticks() / 1000.0
                    if current_time - self.last_attack_time >= self.attack_cooldown:
                        self.attack_target()
                        self.last_attack_time = current_time
        else:
            # No threat, return to following
            self.state = SummonState.FOLLOWING
    
    def attack_target(self):
        """Attack the current target"""
        if not self.target:
            return
        
        # Deal damage to target (with buff multiplier)
        buffed_damage = int(self.damage * self.buff_damage_multiplier)
        if hasattr(self.target, 'take_damage'):
            self.target.take_damage(buffed_damage)
        elif hasattr(self.target, 'health'):
            self.target.health -= buffed_damage
        
        # Apply elemental effects
        if self.element == 'fire' and hasattr(self.target, 'apply_status_effect'):
            self.target.apply_status_effect('burn', duration=3.0, damage=5)
        elif self.element == 'ice' and hasattr(self.target, 'apply_status_effect'):
            self.target.apply_status_effect('freeze', duration=2.0)
        elif self.element == 'lightning' and hasattr(self.target, 'apply_status_effect'):
            self.target.apply_status_effect('shock', duration=2.0, damage=3)
    
    def take_damage(self, damage: int):
        """Take damage from an attack"""
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        
        if self.health <= 0:
            self.health = 0
            self.die()
        
        return actual_damage
    
    def die(self):
        """Handle summon death"""
        self.alive = False
    
    def despawn(self):
        """Summon duration expired"""
        self.alive = False
    
    def draw(self, screen, camera_x: float, camera_y: float):
        """Draw the summoned creature"""
        if not self.alive:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw different shapes based on type
        if self.summon_type == SummonType.WOLF:
            # Draw wolf body
            pygame.draw.ellipse(screen, self.color, (screen_x - 16, screen_y - 12, 32, 24))
            # Head
            pygame.draw.circle(screen, self.color, (screen_x - 10, screen_y - 15), 8)
            # Eyes
            pygame.draw.circle(screen, (255, 255, 0), (screen_x - 12, screen_y - 16), 2)
            pygame.draw.circle(screen, (255, 255, 0), (screen_x - 8, screen_y - 16), 2)
        
        elif self.summon_type in [SummonType.FIRE_ELEMENTAL, SummonType.ICE_ELEMENTAL, SummonType.LIGHTNING_ELEMENTAL]:
            # Draw elemental as pulsing orb
            pulse = abs(self.animation_frame - 2) * 3
            radius = 16 + pulse
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), radius)
            # Inner glow
            inner_color = tuple(min(255, c + 80) for c in self.color)
            pygame.draw.circle(screen, inner_color, (screen_x, screen_y), radius - 6)
        
        elif self.summon_type == SummonType.DEMON:
            # Draw demon as large menacing figure
            pygame.draw.ellipse(screen, self.color, (screen_x - 20, screen_y - 15, 40, 30))
            # Horns
            points_left = [(screen_x - 15, screen_y - 20), (screen_x - 20, screen_y - 30), (screen_x - 10, screen_y - 18)]
            points_right = [(screen_x + 15, screen_y - 20), (screen_x + 20, screen_y - 30), (screen_x + 10, screen_y - 18)]
            pygame.draw.polygon(screen, (150, 0, 0), points_left)
            pygame.draw.polygon(screen, (150, 0, 0), points_right)
            # Eyes
            pygame.draw.circle(screen, (255, 0, 0), (screen_x - 8, screen_y - 10), 3)
            pygame.draw.circle(screen, (255, 0, 0), (screen_x + 8, screen_y - 10), 3)
        
        elif self.summon_type in [SummonType.SKELETON, SummonType.ZOMBIE]:
            # Draw undead as humanoid
            body_color = (220, 220, 200) if self.summon_type == SummonType.SKELETON else (100, 150, 100)
            # Body
            pygame.draw.rect(screen, body_color, (screen_x - 10, screen_y - 5, 20, 20))
            # Head
            pygame.draw.circle(screen, body_color, (screen_x, screen_y - 15), 8)
            # Arms
            pygame.draw.line(screen, body_color, (screen_x - 10, screen_y), (screen_x - 18, screen_y + 10), 3)
            pygame.draw.line(screen, body_color, (screen_x + 10, screen_y), (screen_x + 18, screen_y + 10), 3)
            # Glowing eyes
            pygame.draw.circle(screen, (0, 255, 0), (screen_x - 4, screen_y - 16), 2)
            pygame.draw.circle(screen, (0, 255, 0), (screen_x + 4, screen_y - 16), 2)
        
        else:
            # Default: simple colored circle
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), 16)
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 6
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - 30
            
            # Background
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            # Health
            health_width = int(bar_width * (self.health / self.max_health))
            health_color = (0, 255, 0) if not self.from_corpse else (150, 255, 150)
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Draw indicator for raised undead
        if self.from_corpse:
            # Skull icon above head
            pygame.draw.circle(screen, (200, 200, 200), (screen_x, screen_y - 35), 5)
            pygame.draw.circle(screen, (0, 0, 0), (screen_x - 2, screen_y - 36), 1)
            pygame.draw.circle(screen, (0, 0, 0), (screen_x + 2, screen_y - 36), 1)


# Summon stat definitions
SUMMON_STATS = {
    SummonType.WOLF: {
        'health': 60,
        'damage': 15,
        'defense': 5,
        'speed': 140,
        'attack_cooldown': 1.2,
        'attack_range': 45,
        'color': (120, 90, 70),
        'size': 32,
        'abilities': ['pack_tactics']
    },
    SummonType.FIRE_ELEMENTAL: {
        'health': 40,
        'damage': 25,
        'defense': 3,
        'speed': 100,
        'attack_cooldown': 1.5,
        'attack_range': 60,
        'element': 'fire',
        'color': (255, 100, 0),
        'size': 32,
        'abilities': ['burn', 'fire_aura']
    },
    SummonType.ICE_ELEMENTAL: {
        'health': 50,
        'damage': 18,
        'defense': 8,
        'speed': 90,
        'attack_cooldown': 1.8,
        'attack_range': 55,
        'element': 'ice',
        'color': (100, 150, 255),
        'size': 32,
        'abilities': ['freeze', 'slow_aura']
    },
    SummonType.LIGHTNING_ELEMENTAL: {
        'health': 35,
        'damage': 28,
        'defense': 2,
        'speed': 120,
        'attack_cooldown': 1.3,
        'attack_range': 80,
        'element': 'lightning',
        'color': (255, 255, 100),
        'size': 28,
        'abilities': ['chain_lightning', 'shock']
    },
    SummonType.DEMON: {
        'health': 100,
        'damage': 35,
        'defense': 15,
        'speed': 110,
        'attack_cooldown': 2.0,
        'attack_range': 50,
        'element': 'dark',
        'color': (150, 0, 50),
        'size': 48,
        'abilities': ['fear', 'lifesteal', 'hellfire']
    },
    SummonType.SKELETON: {
        'health': 40,
        'damage': 12,
        'defense': 3,
        'speed': 85,
        'attack_cooldown': 1.4,
        'attack_range': 45,
        'color': (220, 220, 200),
        'size': 32,
        'abilities': ['undead']
    },
    SummonType.ZOMBIE: {
        'health': 70,
        'damage': 18,
        'defense': 8,
        'speed': 70,
        'attack_cooldown': 2.0,
        'attack_range': 40,
        'color': (100, 150, 100),
        'size': 36,
        'abilities': ['undead', 'disease']
    },
    SummonType.GHOST: {
        'health': 30,
        'damage': 20,
        'defense': 20,  # High defense (ethereal)
        'speed': 100,
        'attack_cooldown': 1.6,
        'attack_range': 50,
        'element': 'spirit',
        'color': (200, 200, 255),
        'size': 32,
        'abilities': ['ethereal', 'phase_through_walls']
    },
    SummonType.BONE_GOLEM: {
        'health': 150,
        'damage': 30,
        'defense': 25,
        'speed': 60,
        'attack_cooldown': 2.5,
        'attack_range': 55,
        'color': (180, 180, 170),
        'size': 48,
        'abilities': ['undead', 'taunt', 'bone_armor']
    }
}


class SummoningSystem:
    """Manages all summoned creatures and necromancy"""
    
    def __init__(self, body_disposal_system=None):
        self.summoned_creatures: List[SummonedCreature] = []
        self.max_summons = 5  # Maximum active summons
        self.body_disposal_system = body_disposal_system  # Reference to shared corpse system
        
    def summon_creature(self, summon_type: SummonType, x: float, y: float, summoner, duration: float = 30.0) -> Optional[SummonedCreature]:
        """Summon a new creature"""
        # Check if at summon limit
        active_summons = [s for s in self.summoned_creatures if s.alive]
        if len(active_summons) >= self.max_summons:
            return None
        
        # Create summon
        summon = SummonedCreature(summon_type, x, y, summoner, duration)
        self.summoned_creatures.append(summon)
        
        return summon
    
    def raise_dead(self, corpse_data: Dict, summoner, duration: float = 60.0) -> Optional[SummonedCreature]:
        """Raise a dead enemy as undead minion"""
        # Check if at summon limit
        active_summons = [s for s in self.summoned_creatures if s.alive]
        if len(active_summons) >= self.max_summons:
            return None
        
        # Determine undead type based on corpse
        enemy_type = corpse_data.get('type', 'zombie')
        
        # Map enemy types to undead types
        if 'skeleton' in enemy_type.lower():
            undead_type = SummonType.SKELETON
        elif any(word in enemy_type.lower() for word in ['ghost', 'spirit', 'wraith']):
            undead_type = SummonType.GHOST
        elif 'boss' in enemy_type.lower() or corpse_data.get('was_boss', False):
            # Bosses become bone golems
            undead_type = SummonType.BONE_GOLEM
        else:
            # Default to zombie
            undead_type = SummonType.ZOMBIE
        
        # Create raised undead
        x = corpse_data.get('x', summoner.x)
        y = corpse_data.get('y', summoner.y)
        
        undead = SummonedCreature(undead_type, x, y, summoner, duration, from_corpse=True)
        self.summoned_creatures.append(undead)
        
        # Mark corpse as used in body_disposal_system
        if self.body_disposal_system:
            for corpse in self.body_disposal_system.corpses:
                if corpse.x == x and corpse.y == y:
                    corpse.picked_up = True  # Mark as consumed by necromancy
                    break
        
        return undead
    
    def register_corpse(self, enemy, x: float, y: float):
        """Register an enemy corpse for potential raising (now handled by body_disposal_system)"""
        # This method is kept for backwards compatibility but does nothing
        # Corpse tracking is now unified in body_disposal_system
        pass
    
    def get_nearby_corpses(self, x: float, y: float, radius: float = 100) -> List[Dict]:
        """Get corpses near a position (queries body_disposal_system)"""
        nearby = []
        
        if not self.body_disposal_system:
            return nearby
        
        # Query corpses from body_disposal_system and convert to dict format
        for corpse in self.body_disposal_system.corpses:
            # Skip corpses that are picked up or buried
            if corpse.picked_up or corpse.buried:
                continue
            
            distance = math.sqrt((corpse.x - x)**2 + (corpse.y - y)**2)
            if distance <= radius:
                # Convert Corpse object to dict format for necromancy
                corpse_dict = {
                    'type': corpse.name,  # Use name as type for enemy identification
                    'x': corpse.x,
                    'y': corpse.y,
                    'level': 1,  # Default level (could be enhanced with stored level)
                    'was_boss': 'boss' in corpse.name.lower() or 'dragon' in corpse.name.lower(),
                    'timestamp': corpse.death_time
                }
                nearby.append(corpse_dict)
        
        return nearby
    
    def update(self, dt: float, enemies: List, player_x: float, player_y: float):
        """Update all summoned creatures"""
        for summon in self.summoned_creatures:
            if summon.alive:
                summon.update(dt, enemies, player_x, player_y)
        
        # Remove dead summons
        self.summoned_creatures = [s for s in self.summoned_creatures if s.alive]
    
    def draw(self, screen, camera_x: float, camera_y: float):
        """Draw all summoned creatures"""
        # OPTIMIZATION: Screen culling - only draw summons on screen
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        for summon in self.summoned_creatures:
            if summon.alive:
                screen_x = summon.x - camera_x
                screen_y = summon.y - camera_y
                
                # Only draw if on screen (with small buffer)
                if -50 < screen_x < screen_width + 50 and -50 < screen_y < screen_height + 50:
                    summon.draw(screen, camera_x, camera_y)
    
    def get_active_summons(self) -> List[SummonedCreature]:
        """Get list of active summons"""
        return [s for s in self.summoned_creatures if s.alive]
    
    def dismiss_all(self):
        """Dismiss all summons"""
        for summon in self.summoned_creatures:
            summon.despawn()
    
    def dismiss_oldest(self):
        """Dismiss the oldest summon to make room"""
        active = self.get_active_summons()
        if active:
            oldest = max(active, key=lambda s: s.lifetime)
            oldest.despawn()
    
    def empower_summons(self, duration: float, damage_boost: float = 0.5, speed_boost: float = 0.3):
        """Apply empower buff to all active summons"""
        count = 0
        for summon in self.summoned_creatures:
            if summon.alive:
                summon.apply_buff('empower_undead', duration, damage_boost, speed_boost)
                count += 1
        return count


# Global instance (will be initialized with body_disposal_system in main.py)
summoning_system = None


def get_summoning_system() -> SummoningSystem:
    """Get the global summoning system"""
    return summoning_system


def initialize_summoning_system(body_disposal_system) -> SummoningSystem:
    """Initialize the global summoning system with body disposal system reference"""
    global summoning_system
    summoning_system = SummoningSystem(body_disposal_system)
    return summoning_system

"""
Spell Projectile System
Handles spell projectiles, visual effects, and damage application
"""

import pygame
import math
import time

# Cache for trail and glow surfaces to prevent memory leaks
_surface_cache = {}

def get_cached_trail_surface(size, color):
    """Get a cached trail surface to prevent memory leaks"""
    key = (int(size), color)
    if key not in _surface_cache:
        surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (int(size), int(size)), int(size))
        _surface_cache[key] = surf
    return _surface_cache[key]

def get_cached_glow_surface(size, color):
    """Get a cached glow surface to prevent memory leaks"""
    key = ('glow', int(size), color[:3])  # Ignore alpha for caching
    if key not in _surface_cache:
        surf = pygame.Surface((int(size * 4), int(size * 4)), pygame.SRCALPHA)
        glow_color = (*color[:3], 100)
        pygame.draw.circle(surf, glow_color, (int(size * 2), int(size * 2)), int(size * 2))
        _surface_cache[key] = surf
    return _surface_cache[key]

class SpellProjectile:
    """A spell projectile that travels and damages enemies"""
    
    def __init__(self, x, y, target_x, target_y, spell_data, caster):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.caster = caster
        self.spell_data = spell_data
        self.alive = True
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.vx = (dx / distance) * self.get_speed()
            self.vy = (dy / distance) * self.get_speed()
        else:
            self.vx = 0
            self.vy = 0
        
        # Projectile properties - calculate base damage
        base_damage = spell_data.get("damage", 0)
        
        # Apply caster's Spell_Power multiplier
        spell_power = 1.0
        if hasattr(caster, 'stats'):
            spell_power = caster.stats.get_stat("Spell_Power")
        
        self.damage = int(base_damage * spell_power)
        self.base_damage = base_damage  # Store for display
        self.element = spell_data.get("element", "none")
        self.effects = spell_data.get("effects", [])
        self.max_range = spell_data.get("range", 300)
        self.aoe_radius = spell_data.get("aoe_radius", 0)
        
        # Visual properties
        self.color = self.get_color()
        self.size = self.get_size()
        self.trail = []  # For particle trail
        self.creation_time = time.time()
        self.duration = 5.0  # Max lifetime in seconds
        
    def get_speed(self):
        """Get projectile speed based on spell type"""
        spell_type = self.spell_data.get("type", "projectile")
        speeds = {
            "projectile": 400,  # pixels per second
            "fast": 600,
            "slow": 250,
            "instant": 1000
        }
        return speeds.get(spell_type, 400)
    
    def get_color(self):
        """Get color based on element"""
        element_colors = {
            "fire": (255, 100, 0),
            "ice": (100, 200, 255),
            "lightning": (255, 255, 100),
            "water": (50, 150, 255),
            "wind": (200, 255, 200),
            "dark": (100, 50, 150),
            "light": (255, 255, 200),
            "nature": (100, 255, 100),
            "arcane": (200, 100, 255)
        }
        return element_colors.get(self.element, (200, 200, 200))
    
    def get_size(self):
        """Get projectile size"""
        damage = self.spell_data.get("damage", 10)
        return min(16, max(6, damage // 3))
    
    def update(self, dt, enemies, player):
        """Update projectile position and check collisions"""
        if not self.alive:
            return
        
        # Check lifetime
        if time.time() - self.creation_time > self.duration:
            self.alive = False
            return
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # OPTIMIZATION: Kill projectiles that go way off screen (prevents memory leak)
        # Allow some buffer beyond max_range for edge cases
        off_screen_threshold = self.max_range * 2
        distance_from_start = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2)
        if distance_from_start > off_screen_threshold:
            self.alive = False
            return
        
        # Add trail particle (limit trail length to prevent memory growth)
        current_time = time.time()
        if len(self.trail) >= 10:
            self.trail.pop(0)
        self.trail.append((self.x, self.y, current_time))
        
        # Check if traveled too far
        distance_traveled = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2)
        if distance_traveled > self.max_range:
            self.alive = False
            return
        
        # Check collision with enemies
        projectile_rect = pygame.Rect(self.x - self.size, self.y - self.size, 
                                      self.size * 2, self.size * 2)
        
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            if projectile_rect.colliderect(enemy.rect):
                # Hit enemy
                self.hit_target(enemy, player)
                
                # Check for AoE damage
                if self.aoe_radius > 0:
                    self.apply_aoe_damage(enemies, player)
                
                self.alive = False
                return
    
    def hit_target(self, enemy, player):
        """Apply damage and effects to target"""
        # Start with already scaled damage (includes Spell_Power)
        damage = self.damage
        
        # Crit chance based on player stats if caster is player
        is_crit = False
        if hasattr(self.caster, 'stats'):
            crit_chance = 0.1 + (self.caster.stats.get_stat("Luck") * 0.01)
            import random
            if random.random() < crit_chance:
                damage = int(damage * 1.5)
                is_crit = True
        
        # Apply damage
        enemy.take_damage(damage, player=player, all_enemies=[])
        
        # Show damage feedback
        spell_name = self.spell_data.get('name', 'Spell')
        if is_crit:
            print(f"[SPELL] CRITICAL! {spell_name} hit {enemy.type} for {damage} damage!")
        else:
            # Show base vs scaled damage if spell power > 1.0
            if hasattr(self.caster, 'stats'):
                spell_power = self.caster.stats.get_stat("Spell_Power")
                if spell_power > 1.0:
                    print(f"[SPELL] {spell_name} hit {enemy.type} for {damage} damage! (Base: {self.base_damage}, Power: {spell_power:.2f}x)")
                else:
                    print(f"[SPELL] {spell_name} hit {enemy.type} for {damage} damage!")
            else:
                print(f"[SPELL] {spell_name} hit {enemy.type} for {damage} damage!")
        
        # Apply status effects
        for effect in self.effects:
            if effect == "slow":
                enemy.speed = int(enemy.speed * 0.7)
                print(f"[SPELL] {enemy.type} slowed!")
            elif effect == "burn":
                if hasattr(enemy, 'status_effects'):
                    enemy.status_effects.append({"type": "burn", "duration": 5, "damage": 2})
    
    def apply_aoe_damage(self, enemies, player):
        """Apply area of effect damage"""
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            distance = math.sqrt((enemy.rect.centerx - self.x)**2 + 
                               (enemy.rect.centery - self.y)**2)
            
            if distance <= self.aoe_radius:
                # AoE does 70% of the already-scaled spell damage
                aoe_damage = int(self.damage * 0.7)
                enemy.take_damage(aoe_damage, player=player, all_enemies=[])
                print(f"[SPELL] AoE hit {enemy.type} for {aoe_damage} damage!")
    
    def draw(self, screen, camera_offset):
        """Render the projectile"""
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # OPTIMIZATION: Use cached surfaces for trails to prevent memory leak
        now = time.time()
        for i, (tx, ty, t) in enumerate(self.trail):
            age = now - t
            if age < 0.5:  # Trail lasts 0.5 seconds
                alpha = int(255 * (1 - age / 0.5))
                trail_x = int(tx - camera_offset[0])
                trail_y = int(ty - camera_offset[1])
                trail_size = max(2, self.size * (1 - age / 0.5))
                
                # Use cached surface with alpha blending
                trail_color = (*self.color, alpha // 2)
                trail_surface = get_cached_trail_surface(trail_size, trail_color)
                screen.blit(trail_surface, (trail_x - trail_size, trail_y - trail_size),
                          special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw main projectile
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)
        
        # OPTIMIZATION: Use cached glow surface to prevent memory leak
        if self.element in ["lightning", "light", "arcane"]:
            glow_surface = get_cached_glow_surface(self.size, self.color)
            screen.blit(glow_surface, (screen_x - self.size * 2, screen_y - self.size * 2),
                      special_flags=pygame.BLEND_RGBA_ADD)
        
        # Draw AoE indicator if applicable
        if self.aoe_radius > 0:
            pygame.draw.circle(screen, (*self.color, 50), (screen_x, screen_y), 
                             int(self.aoe_radius), 2)


class SpellEffect:
    """Visual effect for spell impacts, buffs, etc."""
    
    # Shared particle surface cache to prevent memory leaks
    _particle_cache = {}
    
    @staticmethod
    def get_particle_surface(size, color):
        """Get cached particle surface"""
        key = (int(size), color[:3])  # Ignore alpha for cache key
        if key not in SpellEffect._particle_cache:
            surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            # Pre-render at full alpha, we'll adjust with blend modes
            pygame.draw.circle(surf, (*color[:3], 255), (int(size), int(size)), int(size))
            SpellEffect._particle_cache[key] = surf
        return SpellEffect._particle_cache[key]
    
    def __init__(self, x, y, effect_type, color, duration=1.0):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.color = color
        self.duration = duration
        self.creation_time = time.time()
        self.alive = True
        self.particles = []
        
        # Create particles based on effect type
        if effect_type == "explosion":
            import random
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(50, 150)
                self.particles.append({
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "size": random.randint(3, 8),
                    "life": random.uniform(0.3, 0.8)
                })
        elif effect_type == "heal":
            import random
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(20, 60)
                self.particles.append({
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": -random.uniform(50, 100),  # Float upward
                    "size": random.randint(2, 6),
                    "life": random.uniform(0.5, 1.0)
                })
    
    def update(self, dt):
        """Update effect"""
        elapsed = time.time() - self.creation_time
        if elapsed > self.duration:
            self.alive = False
            return
        
        # Update particles
        for particle in self.particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["life"] -= dt
    
    def draw(self, screen, camera_offset):
        """Render effect with cached surfaces to prevent memory leak"""
        for particle in self.particles:
            if particle["life"] > 0:
                screen_x = int(particle["x"] - camera_offset[0])
                screen_y = int(particle["y"] - camera_offset[1])
                alpha = max(0, min(255, int(255 * (particle["life"] / 0.8))))
                
                # Use cached particle surface with alpha blending
                particle_surface = self.get_particle_surface(particle["size"], self.color)
                # Set alpha on the surface copy
                particle_surface.set_alpha(alpha)
                screen.blit(particle_surface, (screen_x - particle["size"], 
                                              screen_y - particle["size"]),
                          special_flags=pygame.BLEND_RGBA_MULT)


class InstantSpell:
    """Spell that applies instantly without projectile (like healing, teleport, etc.)"""
    
    def __init__(self, x, y, spell_data, caster, target=None):
        self.x = x
        self.y = y
        self.spell_data = spell_data
        self.caster = caster
        self.target = target or caster
        self.executed = False
    
    def execute(self, player, enemies):
        """Execute the instant spell effect"""
        if self.executed:
            return
        
        spell_type = self.spell_data.get("type", "self")
        
        # Get spell power multiplier from caster
        spell_power = 1.0
        if hasattr(self.caster, 'stats'):
            spell_power = self.caster.stats.get_stat("Spell_Power")
        
        if spell_type == "self":
            # Healing spell - scaled by Spell_Power
            if "healing" in self.spell_data:
                base_heal = self.spell_data["healing"]
                heal_amount = int(base_heal * spell_power)
                old_health = self.target.health
                
                # Get max health (handle both stats object and direct attribute)
                if hasattr(self.target, 'stats') and hasattr(self.target.stats, 'get_stat'):
                    max_health = self.target.stats.get_stat("Max_Health")
                elif hasattr(self.target, 'max_health'):
                    max_health = self.target.max_health
                else:
                    max_health = 100  # Default fallback
                
                self.target.health = min(self.target.health + heal_amount, max_health)
                actual_heal = self.target.health - old_health
                print(f"[SPELL] Healed for {actual_heal} HP! (Base: {base_heal}, Power: {spell_power:.2f}x)")
            
            # Shield spell - scaled by Spell_Power
            if "shield_amount" in self.spell_data:
                base_shield = self.spell_data["shield_amount"]
                shield = int(base_shield * spell_power)
                if not hasattr(self.target, 'shield'):
                    self.target.shield = 0
                self.target.shield += shield
                print(f"[SPELL] Shield activated! +{shield} shield (Base: {base_shield}, Power: {spell_power:.2f}x)")
            
            # Buff spell
            if "effects" in self.spell_data:
                for effect in self.spell_data["effects"]:
                    if effect == "damage_boost":
                        # Temporary damage boost (would need to track duration)
                        print(f"[SPELL] Damage boosted!")
                    elif effect == "speed_boost":
                        # Temporary speed boost
                        print(f"[SPELL] Speed boosted!")
        
        elif spell_type == "movement":
            # Teleport spell
            if hasattr(self.caster, 'x') and hasattr(self.caster, 'y'):
                # Get mouse position or target position
                teleport_range = self.spell_data.get("range", 200)
                # For now, teleport in the direction player is facing
                # This would be improved with mouse targeting
                dx = self.x - self.caster.x
                dy = self.y - self.caster.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    # Clamp to max range
                    if distance > teleport_range:
                        dx = (dx / distance) * teleport_range
                        dy = (dy / distance) * teleport_range
                    
                    self.caster.x += dx
                    self.caster.y += dy
                    print(f"[SPELL] Teleported!")
        
        self.executed = True
        return True

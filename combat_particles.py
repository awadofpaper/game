"""
Combat particle effects and visual feedback system
"""
import pygame
import random
import time
import math

class StatusEffectParticle:
    """Particle for status effects (burn, poison, freeze, etc.)"""
    def __init__(self, effect_type, position, target_size=(24, 24)):
        """
        Create status effect particle
        
        Args:
            effect_type: Type of effect ("burn", "poison", "freeze", "bleed", "shock")
            position: (x, y) center position
            target_size: (width, height) of the affected entity
        """
        self.effect_type = effect_type
        self.x, self.y = position
        self.target_size = target_size
        self.birth_time = time.time()
        self.alive = True
        
        # Effect-specific properties
        if effect_type == "burn":
            self.duration = 0.6
            self.color = (255, 100, 0)
            self.particle_count = 8
            self.spread_radius = max(target_size) // 2 + 10
        elif effect_type == "poison":
            self.duration = 0.8
            self.color = (100, 200, 50)
            self.particle_count = 12
            self.spread_radius = max(target_size) // 2 + 15
        elif effect_type == "freeze":
            self.duration = 0.5
            self.color = (150, 200, 255)
            self.particle_count = 10
            self.spread_radius = max(target_size) // 2 + 12
        elif effect_type == "bleed":
            self.duration = 0.4
            self.color = (200, 0, 0)
            self.particle_count = 6
            self.spread_radius = max(target_size) // 2 + 8
        elif effect_type == "shock":
            self.duration = 0.3
            self.color = (255, 255, 100)
            self.particle_count = 15
            self.spread_radius = max(target_size) // 2 + 20
        else:
            self.duration = 0.5
            self.color = (255, 255, 255)
            self.particle_count = 8
            self.spread_radius = max(target_size) // 2 + 10
        
        # Generate individual particles
        self.particles = []
        for i in range(self.particle_count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.spread_radius)
            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance
            
            # Velocity based on effect type
            if effect_type == "burn":
                vx = random.uniform(-10, 10)
                vy = random.uniform(-60, -20)  # Rise up
            elif effect_type == "poison":
                vx = random.uniform(-20, 20)
                vy = random.uniform(-10, 10)  # Float around
            elif effect_type == "freeze":
                vx = 0
                vy = random.uniform(5, 15)  # Fall down
            elif effect_type == "bleed":
                vx = random.uniform(-15, 15)
                vy = random.uniform(20, 40)  # Fall down fast
            elif effect_type == "shock":
                vx = random.uniform(-40, 40)
                vy = random.uniform(-40, 40)  # Erratic
            else:
                vx = random.uniform(-20, 20)
                vy = random.uniform(-20, 20)
            
            size = random.randint(2, 5)
            self.particles.append({
                'x': px, 'y': py,
                'vx': vx, 'vy': vy,
                'size': size,
                'life': 1.0
            })
    
    def update(self, dt):
        """Update particle positions"""
        age = time.time() - self.birth_time
        if age >= self.duration:
            self.alive = False
            return
        
        # Update each particle
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Update life based on age
            particle['life'] = 1.0 - (age / self.duration)
            
            # Apply gravity for certain effects
            if self.effect_type in ["bleed", "freeze"]:
                particle['vy'] += 50 * dt  # Gravity
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw status effect particles"""
        if not self.alive:
            return
        
        for particle in self.particles:
            if particle['life'] <= 0:
                continue
            
            # Calculate screen position
            screen_x = int(particle['x'] - camera_x)
            screen_y = int(particle['y'] - camera_y)
            
            # Calculate alpha based on life
            alpha = int(255 * particle['life'])
            
            # Color variation for effect
            color = self.color
            if self.effect_type == "burn":
                # Flicker between orange and yellow
                r = self.color[0]
                g = int(self.color[1] + random.randint(-30, 30))
                b = 0
                color = (r, g, b)
            elif self.effect_type == "shock":
                # Electric white-yellow flicker
                intensity = random.randint(200, 255)
                color = (intensity, intensity, random.randint(100, 255))
            
            # Draw particle with alpha
            if particle['size'] > 0:
                particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, (*color, alpha), 
                                 (particle['size'], particle['size']), particle['size'])
                screen.blit(particle_surface, (screen_x - particle['size'], screen_y - particle['size']))


class WeaponSlashEffect:
    """Visual effect for melee weapon attacks"""
    def __init__(self, weapon_type, position, direction, color=(255, 255, 255)):
        """
        Create weapon slash effect
        
        Args:
            weapon_type: Type of weapon ("sword", "axe", "dagger", "hammer", "spear")
            position: (x, y) center position
            direction: Angle in radians for attack direction
            color: RGB color tuple
        """
        self.weapon_type = weapon_type
        self.x, self.y = position
        self.direction = direction
        self.color = color
        self.birth_time = time.time()
        self.alive = True
        
        # Weapon-specific properties
        if weapon_type in ["sword", "greatsword", "longsword"]:
            self.duration = 0.3
            self.arc_angle = 90  # Wide arc
            self.radius = 40
            self.trail_count = 5
        elif weapon_type in ["axe", "greataxe", "battleaxe"]:
            self.duration = 0.4
            self.arc_angle = 100  # Wider, slower arc
            self.radius = 45
            self.trail_count = 6
        elif weapon_type in ["dagger", "knife", "shortsword"]:
            self.duration = 0.2
            self.arc_angle = 60  # Quick, narrow arc
            self.radius = 30
            self.trail_count = 3
        elif weapon_type in ["hammer", "mace", "warhammer"]:
            self.duration = 0.5
            self.arc_angle = 80
            self.radius = 35
            self.trail_count = 4
        elif weapon_type in ["spear", "lance", "pike"]:
            self.duration = 0.25
            self.arc_angle = 30  # Thrust, not slash
            self.radius = 50
            self.trail_count = 3
        else:
            self.duration = 0.3
            self.arc_angle = 80
            self.radius = 35
            self.trail_count = 4
    
    def update(self, dt):
        """Update effect"""
        age = time.time() - self.birth_time
        if age >= self.duration:
            self.alive = False
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw weapon slash effect"""
        if not self.alive:
            return
        
        age = time.time() - self.birth_time
        progress = age / self.duration
        
        # Calculate alpha (fade out)
        alpha = int(255 * (1 - progress))
        
        # Screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw weapon trail based on type
        if self.weapon_type in ["spear", "lance", "pike"]:
            # Thrust effect - line with expanding point
            end_x = screen_x + math.cos(self.direction) * self.radius * (1 + progress)
            end_y = screen_y + math.sin(self.direction) * self.radius * (1 + progress)
            
            # Draw thrust line
            line_surface = pygame.Surface((abs(int(end_x - screen_x)) + 10, 
                                          abs(int(end_y - screen_y)) + 10), pygame.SRCALPHA)
            pygame.draw.line(line_surface, (*self.color, alpha),
                           (5, 5), (int(end_x - screen_x) + 5, int(end_y - screen_y) + 5), 3)
            screen.blit(line_surface, (min(screen_x, end_x) - 5, min(screen_y, end_y) - 5))
        else:
            # Arc slash effect
            arc_range = math.radians(self.arc_angle)
            start_angle = self.direction - arc_range/2
            
            # Draw multiple arc segments for trailing effect
            for i in range(self.trail_count):
                trail_progress = (i / self.trail_count) * progress
                trail_alpha = int(alpha * (1 - i / self.trail_count))
                
                # Calculate arc segment
                segment_angle = start_angle + arc_range * trail_progress
                
                # Draw arc segment
                start_x = screen_x + math.cos(segment_angle - 0.1) * self.radius * 0.7
                start_y = screen_y + math.sin(segment_angle - 0.1) * self.radius * 0.7
                end_x = screen_x + math.cos(segment_angle) * self.radius
                end_y = screen_y + math.sin(segment_angle) * self.radius
                
                if trail_alpha > 0:
                    pygame.draw.line(screen, (*self.color, trail_alpha),
                                   (int(start_x), int(start_y)),
                                   (int(end_x), int(end_y)), 3)


class HitImpactEffect:
    """Visual effect for when attacks land"""
    def __init__(self, position, is_crit=False, impact_type="normal"):
        """
        Create hit impact effect
        
        Args:
            position: (x, y) impact position
            is_crit: True for critical hit (more dramatic)
            impact_type: "normal", "heavy", "magic"
        """
        self.x, self.y = position
        self.is_crit = is_crit
        self.impact_type = impact_type
        self.birth_time = time.time()
        self.alive = True
        
        # Impact-specific properties
        if is_crit:
            self.duration = 0.4
            self.max_radius = 40
            self.color = (255, 255, 100)
            self.ring_count = 3
        elif impact_type == "heavy":
            self.duration = 0.35
            self.max_radius = 35
            self.color = (255, 150, 50)
            self.ring_count = 2
        elif impact_type == "magic":
            self.duration = 0.3
            self.max_radius = 30
            self.color = (150, 100, 255)
            self.ring_count = 2
        else:
            self.duration = 0.25
            self.max_radius = 25
            self.color = (255, 255, 255)
            self.ring_count = 1
        
        # Generate star burst lines for critical
        if is_crit:
            self.burst_lines = []
            for i in range(8):
                angle = (2 * math.pi * i / 8)
                self.burst_lines.append({
                    'angle': angle,
                    'length': random.randint(20, 40)
                })
    
    def update(self, dt):
        """Update effect"""
        age = time.time() - self.birth_time
        if age >= self.duration:
            self.alive = False
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw impact effect"""
        if not self.alive:
            return
        
        age = time.time() - self.birth_time
        progress = age / self.duration
        
        # Screen position
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw expanding rings
        for i in range(self.ring_count):
            ring_progress = (progress + i * 0.2) % 1.0
            radius = int(self.max_radius * ring_progress)
            alpha = int(255 * (1 - ring_progress))
            
            if radius > 0 and alpha > 0:
                ring_surface = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
                pygame.draw.circle(ring_surface, (*self.color, alpha),
                                 (radius*2, radius*2), radius, 3)
                screen.blit(ring_surface, (screen_x - radius*2, screen_y - radius*2))
        
        # Draw star burst for critical hits
        if self.is_crit and hasattr(self, 'burst_lines'):
            alpha = int(255 * (1 - progress))
            for line in self.burst_lines:
                length = line['length'] * progress
                end_x = screen_x + math.cos(line['angle']) * length
                end_y = screen_y + math.sin(line['angle']) * length
                
                if alpha > 0:
                    pygame.draw.line(screen, (*self.color, alpha),
                                   (screen_x, screen_y),
                                   (int(end_x), int(end_y)), 2)


class CombatParticleManager:
    """Manager for all combat particle effects"""
    def __init__(self):
        self.particles = []
    
    def add_status_effect(self, effect_type, position, target_size=(24, 24)):
        """Add status effect particles"""
        particle = StatusEffectParticle(effect_type, position, target_size)
        self.particles.append(particle)
    
    def add_weapon_slash(self, weapon_type, position, direction, color=(255, 255, 255)):
        """Add weapon slash effect"""
        effect = WeaponSlashEffect(weapon_type, position, direction, color)
        self.particles.append(effect)
    
    def add_hit_impact(self, position, is_crit=False, impact_type="normal"):
        """Add hit impact effect"""
        effect = HitImpactEffect(position, is_crit, impact_type)
        self.particles.append(effect)
    
    def update(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen, camera_x, camera_y)
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()

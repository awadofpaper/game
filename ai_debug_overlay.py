"""
AI Debug Visualization System
Displays enemy AI states, emotions, personalities, and behavior trees for debugging
"""

import pygame
import time
from ai_personality_system import Personality, EmotionalState

class AIDebugOverlay:
    """
    Debug overlay showing AI information for enemies
    Toggle with F8 key (separate from F7 debug mode)
    """
    
    def __init__(self):
        # Fonts
        self.font = pygame.font.SysFont(None, 16)
        self.small_font = pygame.font.SysFont(None, 14)
        self.title_font = pygame.font.SysFont(None, 20, bold=True)
        
        # Colors
        self.bg_color = (0, 0, 0, 180)  # Semi-transparent black
        self.personality_colors = {
            Personality.AGGRESSIVE: (255, 100, 100),
            Personality.COWARDLY: (255, 255, 100),
            Personality.TACTICAL: (100, 200, 255),
            Personality.BERSERKER: (255, 50, 50),
            Personality.CAUTIOUS: (200, 200, 100),
            Personality.STUBBORN: (150, 100, 50),
            Personality.ADAPTIVE: (150, 255, 150),
            Personality.PROTECTIVE: (100, 255, 200)
        }
        self.emotion_colors = {
            EmotionalState.CALM: (150, 150, 255),
            EmotionalState.ANGRY: (255, 50, 50),
            EmotionalState.FEARFUL: (255, 255, 100),
            EmotionalState.CONFIDENT: (100, 255, 100),
            EmotionalState.DESPERATE: (255, 150, 50),
            EmotionalState.FOCUSED: (150, 200, 255),
            EmotionalState.PANICKED: (255, 100, 255),
            EmotionalState.VENGEFUL: (200, 50, 150)
        }
        
        # Visibility toggles
        self.enabled = False  # Master toggle (F8)
        self.show_personality = True
        self.show_emotions = True
        self.show_behavior_tree = True
        self.show_stats = True
        self.show_vision_cones = True
        
        # Display mode
        self.detail_mode = "nearby"  # "nearby" or "all" or "selected"
        self.selected_enemy = None
        self.max_distance = 400  # Show info for enemies within this distance
        
        # Performance
        self.update_interval = 0.1  # Update AI info every 0.1s
        self.last_update = 0
        self.cached_enemy_data = {}
    
    def toggle(self):
        """Toggle debug overlay on/off"""
        self.enabled = not self.enabled
        return self.enabled
    
    def toggle_feature(self, feature):
        """Toggle specific feature visibility"""
        if feature == "personality":
            self.show_personality = not self.show_personality
        elif feature == "emotions":
            self.show_emotions = not self.show_emotions
        elif feature == "behavior":
            self.show_behavior_tree = not self.show_behavior_tree
        elif feature == "stats":
            self.show_stats = not self.show_stats
        elif feature == "vision":
            self.show_vision_cones = not self.show_vision_cones
    
    def cycle_detail_mode(self):
        """Cycle through detail modes"""
        modes = ["nearby", "all", "selected"]
        current_index = modes.index(self.detail_mode)
        self.detail_mode = modes[(current_index + 1) % len(modes)]
        return self.detail_mode
    
    def update_cache(self, enemies, player, personality_manager):
        """Update cached enemy data for display"""
        if time.time() - self.last_update < self.update_interval:
            return
        
        self.last_update = time.time()
        self.cached_enemy_data.clear()
        
        for enemy in enemies:
            enemy_id = id(enemy)
            
            # Get personality system
            personality_system = personality_manager.get_personality(str(enemy_id))
            if not personality_system:
                continue
            
            # Calculate distance to player
            distance = ((enemy.rect.centerx - player.x) ** 2 + (enemy.rect.centery - player.y) ** 2) ** 0.5
            
            # Filter based on mode
            if self.detail_mode == "nearby" and distance > self.max_distance:
                continue
            elif self.detail_mode == "selected" and enemy != self.selected_enemy:
                continue
            
            # Cache enemy data
            self.cached_enemy_data[enemy_id] = {
                'enemy': enemy,
                'personality_system': personality_system,
                'distance': distance,
                'screen_x': enemy.rect.centerx,
                'screen_y': enemy.rect.centery
            }
    
    def draw(self, screen, enemies, player, camera_x, camera_y, personality_manager):
        """Draw AI debug overlay"""
        if not self.enabled:
            return
        
        # Update cache
        self.update_cache(enemies, player, personality_manager)
        
        # Draw legend panel
        self._draw_legend(screen)
        
        # Draw enemy-specific overlays
        for enemy_id, data in self.cached_enemy_data.items():
            enemy = data['enemy']
            personality_system = data['personality_system']
            screen_x = enemy.rect.centerx - camera_x
            screen_y = enemy.rect.centery - camera_y
            
            # Draw vision cone
            if self.show_vision_cones:
                self._draw_vision_cone(screen, enemy, screen_x, screen_y)
            
            # Draw info box above enemy
            self._draw_enemy_info_box(screen, enemy, personality_system, screen_x, screen_y)
            
            # Draw behavior tree visualization
            if self.show_behavior_tree and hasattr(enemy, 'behavior_tree') and enemy.behavior_tree:
                self._draw_behavior_indicator(screen, enemy, screen_x, screen_y)
    
    def _draw_legend(self, screen):
        """Draw legend panel showing what colors mean"""
        panel_width = 300
        panel_height = 200
        panel_x = 10
        panel_y = 10
        
        # Background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.bg_color, (0, 0, panel_width, panel_height), border_radius=5)
        pygame.draw.rect(panel_surface, (255, 255, 255), (0, 0, panel_width, panel_height), 2, border_radius=5)
        
        # Title
        title = self.title_font.render("🔍 AI Debug (F8)", True, (255, 255, 100))
        panel_surface.blit(title, (10, 8))
        
        y = 35
        
        # Mode indicator
        mode_text = self.font.render(f"Mode: {self.detail_mode.upper()} (F9 to cycle)", True, (200, 200, 200))
        panel_surface.blit(mode_text, (10, y))
        y += 25
        
        # Personality legend
        legend_text = self.small_font.render("Personalities:", True, (255, 255, 255))
        panel_surface.blit(legend_text, (10, y))
        y += 18
        
        for personality, color in list(self.personality_colors.items())[:4]:
            color_box = pygame.Surface((12, 12))
            color_box.fill(color)
            panel_surface.blit(color_box, (15, y))
            name = self.small_font.render(personality.value.capitalize(), True, (220, 220, 220))
            panel_surface.blit(name, (32, y - 1))
            y += 16
        
        # Emotion legend
        y += 8
        legend_text = self.small_font.render("Emotions:", True, (255, 255, 255))
        panel_surface.blit(legend_text, (10, y))
        y += 18
        
        for emotion, color in list(self.emotion_colors.items())[:4]:
            color_box = pygame.Surface((12, 12))
            color_box.fill(color)
            panel_surface.blit(color_box, (15, y))
            name = self.small_font.render(emotion.value.capitalize(), True, (220, 220, 220))
            panel_surface.blit(name, (32, y - 1))
            y += 16
        
        screen.blit(panel_surface, (panel_x, panel_y))
    
    def _draw_vision_cone(self, screen, enemy, screen_x, screen_y):
        """Draw enemy vision cone"""
        if not hasattr(enemy, 'facing'):
            return
        
        # Vision cone parameters
        vision_distance = 200
        vision_angle = 60  # degrees
        
        # Calculate facing direction
        facing_map = {
            'right': 0,
            'left': 180,
            'up': 270,
            'down': 90
        }
        angle = facing_map.get(enemy.facing, 0)
        
        # Draw cone
        import math
        points = [(screen_x, screen_y)]
        for i in range(-vision_angle // 2, vision_angle // 2 + 1, 10):
            rad = math.radians(angle + i)
            px = screen_x + vision_distance * math.cos(rad)
            py = screen_y + vision_distance * math.sin(rad)
            points.append((px, py))
        
        if len(points) > 2:
            # Draw semi-transparent cone
            cone_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(cone_surface, (255, 255, 100, 30), points)
            screen.blit(cone_surface, (0, 0))
            
            # Draw outline
            pygame.draw.polygon(screen, (255, 255, 100, 100), points, 1)
    
    def _draw_enemy_info_box(self, screen, enemy, personality_system, screen_x, screen_y):
        """Draw info box above enemy head"""
        lines = []
        
        # Enemy type and level
        enemy_type = getattr(enemy, 'type', 'Unknown')
        enemy_level = getattr(enemy, 'level', 1)
        lines.append(f"{enemy_type} Lv.{enemy_level}")
        
        # Personality
        if self.show_personality:
            personality = personality_system.personality_type
            personality_color = self.personality_colors.get(personality, (255, 255, 255))
            lines.append((f"🧠 {personality.value.capitalize()}", personality_color))
        
        # Emotional state
        if self.show_emotions:
            emotion = personality_system.emotional_profile.current_state
            emotion_color = self.emotion_colors.get(emotion, (255, 255, 255))
            emotion_text = f"😊 {emotion.value.capitalize()}"
            
            # Add emotion level indicators
            anger = personality_system.emotional_profile.anger_level
            fear = personality_system.emotional_profile.fear_level
            confidence = personality_system.emotional_profile.confidence_level
            
            if anger > 0.5:
                emotion_text = f"😡 {emotion.value}"
            elif fear > 0.5:
                emotion_text = f"😰 {emotion.value}"
            elif confidence > 0.7:
                emotion_text = f"😎 {emotion.value}"
            
            lines.append((emotion_text, emotion_color))
        
        # Behavior stats
        if self.show_stats:
            hp_ratio = enemy.hp / enemy.max_hp if hasattr(enemy, 'hp') and hasattr(enemy, 'max_hp') else 1.0
            lines.append(f"HP: {int(hp_ratio * 100)}%")
            
            # Behavior modifiers
            aggression = personality_system.behavior_modifiers.get('attack_frequency', 1.0)
            lines.append(f"Aggression: {aggression:.1f}x")
        
        # Behavior tree state
        if self.show_behavior_tree and hasattr(enemy, 'behavior_tree'):
            if enemy.behavior_tree:
                tree_name = enemy.behavior_tree.name
                lines.append(f"⚙ {tree_name}")
        
        # Calculate box size
        max_width = 0
        for line in lines:
            text = line if isinstance(line, str) else line[0]
            width = self.small_font.size(text)[0]
            max_width = max(max_width, width)
        
        box_width = max_width + 12
        box_height = len(lines) * 16 + 8
        box_x = screen_x - box_width // 2
        box_y = screen_y - 60 - box_height
        
        # Draw background
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, self.bg_color, (0, 0, box_width, box_height), border_radius=4)
        pygame.draw.rect(box_surface, (200, 200, 200), (0, 0, box_width, box_height), 1, border_radius=4)
        
        # Draw text lines
        y = 4
        for line in lines:
            if isinstance(line, tuple):
                text, color = line
            else:
                text = line
                color = (255, 255, 255)
            
            rendered = self.small_font.render(text, True, color)
            box_surface.blit(rendered, (6, y))
            y += 16
        
        screen.blit(box_surface, (int(box_x), int(box_y)))
    
    def _draw_behavior_indicator(self, screen, enemy, screen_x, screen_y):
        """Draw behavior tree execution indicator"""
        # Draw a small pulsing circle to show behavior tree is active
        pulse = (time.time() % 1.0)
        radius = 5 + int(3 * pulse)
        alpha = int(255 * (1.0 - pulse))
        
        indicator_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(indicator_surface, (100, 255, 100, alpha), (radius, radius), radius, 2)
        screen.blit(indicator_surface, (int(screen_x - radius), int(screen_y - 40 - radius)))
    
    def draw_info_panel(self, screen, personality_manager):
        """Draw detailed info panel for selected enemy"""
        if not self.enabled or self.detail_mode != "selected" or not self.selected_enemy:
            return
        
        enemy_id = str(id(self.selected_enemy))
        personality_system = personality_manager.get_personality(enemy_id)
        
        if not personality_system:
            return
        
        # Draw detailed panel in bottom-left
        panel_width = 350
        panel_height = 300
        panel_x = 10
        panel_y = screen.get_height() - panel_height - 10
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.bg_color, (0, 0, panel_width, panel_height), border_radius=5)
        pygame.draw.rect(panel_surface, (255, 255, 255), (0, 0, panel_width, panel_height), 2, border_radius=5)
        
        # Title
        enemy_type = getattr(self.selected_enemy, 'type', 'Unknown')
        title = self.title_font.render(f"Selected: {enemy_type}", True, (255, 255, 100))
        panel_surface.blit(title, (10, 8))
        
        y = 35
        
        # Personality traits
        traits = personality_system.traits
        trait_names = ['aggression', 'courage', 'intelligence', 'adaptability']
        
        for trait_name in trait_names:
            value = getattr(traits, trait_name, 0.5)
            bar_width = 200
            bar_height = 16
            
            label = self.small_font.render(f"{trait_name.capitalize()}:", True, (200, 200, 200))
            panel_surface.blit(label, (10, y))
            
            # Draw bar
            bar_x = 120
            pygame.draw.rect(panel_surface, (50, 50, 50), (bar_x, y, bar_width, bar_height))
            pygame.draw.rect(panel_surface, (100, 200, 255), (bar_x, y, int(bar_width * value), bar_height))
            
            value_text = self.small_font.render(f"{value:.2f}", True, (255, 255, 255))
            panel_surface.blit(value_text, (bar_x + bar_width + 5, y))
            
            y += 20
        
        # Emotional levels
        y += 10
        emotional_label = self.font.render("Emotional State:", True, (255, 255, 255))
        panel_surface.blit(emotional_label, (10, y))
        y += 20
        
        emotions = {
            'Anger': personality_system.emotional_profile.anger_level,
            'Fear': personality_system.emotional_profile.fear_level,
            'Confidence': personality_system.emotional_profile.confidence_level,
            'Stress': personality_system.emotional_profile.stress_level
        }
        
        for emotion_name, value in emotions.items():
            bar_width = 150
            bar_height = 12
            
            label = self.small_font.render(f"{emotion_name}:", True, (200, 200, 200))
            panel_surface.blit(label, (10, y))
            
            bar_x = 100
            pygame.draw.rect(panel_surface, (50, 50, 50), (bar_x, y, bar_width, bar_height))
            
            # Color based on value
            if emotion_name == 'Anger':
                color = (255, int(100 * (1 - value)), int(100 * (1 - value)))
            elif emotion_name == 'Fear':
                color = (255, 255, int(100 * (1 - value)))
            elif emotion_name == 'Confidence':
                color = (int(100 * (1 - value)), 255, int(100 * (1 - value)))
            else:  # Stress
                color = (255, int(150 * (1 - value)), 0)
            
            pygame.draw.rect(panel_surface, color, (bar_x, y, int(bar_width * value), bar_height))
            
            y += 16
        
        screen.blit(panel_surface, (panel_x, panel_y))

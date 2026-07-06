"""
Advanced AI Settings UI
Configurable enemy AI behaviors and difficulty
Hotkey: F3
"""

import pygame
import json
import os
from typing import Dict, List
from advanced_ai_system import get_ai_manager, AIRole, Formation, AIState

class AISettingsUI:
    def __init__(self):
        self.active = False
        self.categories = ['Difficulty', 'Behavior', 'Groups', 'Debug']
        self.current_category = 0
        self.current_option = 0
        self.font = None
        
        # AI Settings
        self.ai_settings = {
            'ai_enabled': True,
            'difficulty': 1.0,  # 0.5 = Easy, 1.0 = Normal, 2.0 = Hard, 3.0 = Expert
            'coordination_range': 200,
            'max_group_size': 5,
            'reaction_time': 1.0,
            'formation_switching': True,
            'smart_positioning': True,
            'adaptive_tactics': True,
            'memory_enabled': True,
            'threat_analysis': True,
            'auto_grouping': True
        }
        
        # Difficulty presets
        self.difficulty_presets = {
            'Passive': {
                'difficulty': 0.3,
                'coordination_range': 100,
                'reaction_time': 3.0,
                'formation_switching': False,
                'adaptive_tactics': False
            },
            'Easy': {
                'difficulty': 0.7,
                'coordination_range': 150,
                'reaction_time': 2.0,
                'formation_switching': True,
                'adaptive_tactics': False
            },
            'Normal': {
                'difficulty': 1.0,
                'coordination_range': 200,
                'reaction_time': 1.0,
                'formation_switching': True,
                'adaptive_tactics': True
            },
            'Hard': {
                'difficulty': 1.5,
                'coordination_range': 250,
                'reaction_time': 0.7,
                'formation_switching': True,
                'adaptive_tactics': True
            },
            'Expert': {
                'difficulty': 2.0,
                'coordination_range': 300,
                'reaction_time': 0.5,
                'formation_switching': True,
                'adaptive_tactics': True
            },
            'Nightmare': {
                'difficulty': 3.0,
                'coordination_range': 400,
                'reaction_time': 0.3,
                'formation_switching': True,
                'adaptive_tactics': True
            }
        }
        
        self.load_settings()
        print("AI Settings UI initialized")
    
    def load_settings(self):
        """Load AI settings from file"""
        try:
            if os.path.exists('ai_settings.json'):
                with open('ai_settings.json', 'r') as f:
                    saved_settings = json.load(f)
                    self.ai_settings.update(saved_settings)
                    print("AI settings loaded from file")
        except Exception as e:
            print(f"Could not load AI settings: {e}")
        
        # Apply settings to AI manager
        self.apply_settings()
    
    def save_settings(self):
        """Save AI settings to file"""
        try:
            with open('ai_settings.json', 'w') as f:
                json.dump(self.ai_settings, f, indent=4)
            print("AI settings saved")
        except Exception as e:
            print(f"Could not save AI settings: {e}")
    
    def apply_settings(self):
        """Apply current settings to AI manager"""
        ai_manager = get_ai_manager()
        
        ai_manager.ai_enabled = self.ai_settings['ai_enabled']
        ai_manager.set_difficulty(self.ai_settings['difficulty'])
        ai_manager.coordination_range = self.ai_settings['coordination_range']
        
        print(f"Applied AI settings - Difficulty: {self.ai_settings['difficulty']}")
    
    def toggle(self):
        """Toggle AI settings UI"""
        self.active = not self.active
        if self.active:
            print("AI Settings opened")
        return self.active
    
    def handle_input(self, event):
        """Handle input events"""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3 or event.key == pygame.K_ESCAPE:
                self.toggle()
                return True
            
            elif event.key == pygame.K_LEFT:
                self.current_category = (self.current_category - 1) % len(self.categories)
                self.current_option = 0
                return True
            
            elif event.key == pygame.K_RIGHT:
                self.current_category = (self.current_category + 1) % len(self.categories)
                self.current_option = 0
                return True
            
            elif event.key == pygame.K_UP:
                self.current_option = max(0, self.current_option - 1)
                return True
            
            elif event.key == pygame.K_DOWN:
                max_options = len(self.get_current_options()) - 1
                self.current_option = min(max_options, self.current_option + 1)
                return True
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.activate_current_option()
                return True
            
            elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.save_settings()
                return True
        
        return False
    
    def get_current_options(self) -> List[str]:
        """Get options for current category"""
        category = self.categories[self.current_category]
        
        if category == 'Difficulty':
            return ['AI Enabled', 'Difficulty Level', 'Apply Preset', 'Reaction Time', 'Coordination Range']
        elif category == 'Behavior':
            return ['Formation Switching', 'Smart Positioning', 'Adaptive Tactics', 'Memory System', 'Threat Analysis']
        elif category == 'Groups':
            return ['Auto Grouping', 'Max Group Size', 'Group Management', 'Role Assignment']
        elif category == 'Debug':
            return ['Show Debug Info', 'Reset All Groups', 'Force Regroup', 'AI Statistics']
        
        return []
    
    def activate_current_option(self):
        """Activate the currently selected option"""
        category = self.categories[self.current_category]
        options = self.get_current_options()
        
        if self.current_option >= len(options):
            return
        
        option = options[self.current_option]
        
        if category == 'Difficulty':
            if option == 'AI Enabled':
                self.ai_settings['ai_enabled'] = not self.ai_settings['ai_enabled']
                self.apply_settings()
            
            elif option == 'Difficulty Level':
                # Cycle through difficulty levels
                levels = [0.3, 0.7, 1.0, 1.5, 2.0, 3.0]
                current_idx = 0
                for i, level in enumerate(levels):
                    if abs(self.ai_settings['difficulty'] - level) < 0.1:
                        current_idx = i
                        break
                
                next_idx = (current_idx + 1) % len(levels)
                self.ai_settings['difficulty'] = levels[next_idx]
                self.apply_settings()
            
            elif option == 'Apply Preset':
                # Cycle through presets
                presets = list(self.difficulty_presets.keys())
                current_preset = 'Normal'  # Default
                
                # Find current preset
                for preset_name, preset_values in self.difficulty_presets.items():
                    if abs(self.ai_settings['difficulty'] - preset_values['difficulty']) < 0.1:
                        current_preset = preset_name
                        break
                
                current_idx = presets.index(current_preset)
                next_idx = (current_idx + 1) % len(presets)
                next_preset = presets[next_idx]
                
                # Apply preset
                for key, value in self.difficulty_presets[next_preset].items():
                    if key in self.ai_settings:
                        self.ai_settings[key] = value
                
                self.apply_settings()
                print(f"Applied {next_preset} AI preset")
            
            elif option == 'Reaction Time':
                # Cycle reaction time: 0.3s, 0.5s, 1.0s, 2.0s, 3.0s
                times = [0.3, 0.5, 1.0, 2.0, 3.0]
                current_time = self.ai_settings['reaction_time']
                current_idx = 0
                
                for i, time_val in enumerate(times):
                    if abs(current_time - time_val) < 0.1:
                        current_idx = i
                        break
                
                next_idx = (current_idx + 1) % len(times)
                self.ai_settings['reaction_time'] = times[next_idx]
            
            elif option == 'Coordination Range':
                # Cycle coordination range
                ranges = [100, 150, 200, 250, 300, 400]
                current_range = self.ai_settings['coordination_range']
                current_idx = 0
                
                for i, range_val in enumerate(ranges):
                    if current_range == range_val:
                        current_idx = i
                        break
                
                next_idx = (current_idx + 1) % len(ranges)
                self.ai_settings['coordination_range'] = ranges[next_idx]
                self.apply_settings()
        
        elif category == 'Behavior':
            bool_settings = {
                'Formation Switching': 'formation_switching',
                'Smart Positioning': 'smart_positioning',
                'Adaptive Tactics': 'adaptive_tactics',
                'Memory System': 'memory_enabled',
                'Threat Analysis': 'threat_analysis'
            }
            
            if option in bool_settings:
                setting_key = bool_settings[option]
                self.ai_settings[setting_key] = not self.ai_settings[setting_key]
        
        elif category == 'Groups':
            if option == 'Auto Grouping':
                self.ai_settings['auto_grouping'] = not self.ai_settings['auto_grouping']
            
            elif option == 'Max Group Size':
                # Cycle group size: 3, 4, 5, 6, 8, 10
                sizes = [3, 4, 5, 6, 8, 10]
                current_size = self.ai_settings['max_group_size']
                current_idx = 0
                
                for i, size in enumerate(sizes):
                    if current_size == size:
                        current_idx = i
                        break
                
                next_idx = (current_idx + 1) % len(sizes)
                self.ai_settings['max_group_size'] = sizes[next_idx]
            
            elif option == 'Group Management':
                # Show group management actions
                print("Group management options accessed")
            
            elif option == 'Role Assignment':
                print("Role assignment options accessed")
        
        elif category == 'Debug':
            ai_manager = get_ai_manager()
            
            if option == 'Show Debug Info':
                debug_info = ai_manager.get_debug_info()
                print("AI Debug Info:", debug_info)
            
            elif option == 'Reset All Groups':
                for group_id in list(ai_manager.groups.keys()):
                    ai_manager.disband_group(group_id)
                print("All AI groups reset")
            
            elif option == 'Force Regroup':
                # This would trigger regrouping of all enemies
                print("Force regroup triggered")
            
            elif option == 'AI Statistics':
                stats = self.get_ai_statistics()
                print("AI Statistics:", stats)
    
    def get_ai_statistics(self) -> Dict:
        """Get AI performance statistics"""
        ai_manager = get_ai_manager()
        
        total_enemies = sum(len(g.members) for g in ai_manager.groups.values())
        active_groups = len(ai_manager.groups)
        
        state_counts = {}
        for group in ai_manager.groups.values():
            state = group.state.value
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            'total_enemies': total_enemies,
            'active_groups': active_groups,
            'states': state_counts,
            'difficulty': self.ai_settings['difficulty']
        }
    
    def draw(self, screen, font):
        """Draw AI settings UI"""
        if not self.active:
            return
        
        self.font = font
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Semi-transparent background
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 800
        panel_height = 600
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (100, 100, 100), (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title_text = font.render("Advanced AI Settings (F3)", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=panel_x + panel_width // 2, y=panel_y + 20)
        screen.blit(title_text, title_rect)
        
        # Category tabs
        tab_width = panel_width // len(self.categories)
        tab_y = panel_y + 60
        
        for i, category in enumerate(self.categories):
            tab_x = panel_x + i * tab_width
            tab_color = (80, 80, 80) if i == self.current_category else (60, 60, 60)
            
            pygame.draw.rect(screen, tab_color, (tab_x, tab_y, tab_width, 40))
            pygame.draw.rect(screen, (100, 100, 100), (tab_x, tab_y, tab_width, 40), 1)
            
            tab_text = font.render(category, True, (255, 255, 255))
            tab_text_rect = tab_text.get_rect(center=(tab_x + tab_width // 2, tab_y + 20))
            screen.blit(tab_text, tab_text_rect)
        
        # Content area
        content_y = tab_y + 50
        content_height = panel_height - 140
        
        self.draw_category_content(screen, font, panel_x, content_y, panel_width, content_height)
        
        # Instructions
        instructions = [
            "← → Change Category  ↑ ↓ Navigate  Enter/Space: Toggle  Ctrl+S: Save",
            "F3/Esc: Close"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = font.render(instruction, True, (200, 200, 200))
            inst_y = panel_y + panel_height - 40 + i * 20
            screen.blit(inst_text, (panel_x + 20, inst_y))
    
    def draw_category_content(self, screen, font, x, y, width, height):
        """Draw content for current category"""
        category = self.categories[self.current_category]
        options = self.get_current_options()
        
        # Draw options list
        option_height = 40
        start_y = y + 20
        
        for i, option in enumerate(options):
            option_y = start_y + i * option_height
            
            # Highlight current option
            if i == self.current_option:
                pygame.draw.rect(screen, (80, 120, 80), (x + 20, option_y - 5, width - 40, option_height - 10))
            
            # Option text
            option_text = font.render(option, True, (255, 255, 255))
            screen.blit(option_text, (x + 40, option_y))
            
            # Option value
            value_text = self.get_option_value_text(category, option)
            if value_text:
                value_surface = font.render(value_text, True, (200, 255, 200))
                value_x = x + width - 40 - value_surface.get_width()
                screen.blit(value_surface, (value_x, option_y))
        
        # Category-specific additional info
        if category == 'Debug':
            self.draw_debug_info(screen, font, x, start_y + len(options) * option_height + 40, width)
    
    def get_option_value_text(self, category: str, option: str) -> str:
        """Get display text for option value"""
        if category == 'Difficulty':
            if option == 'AI Enabled':
                return "ON" if self.ai_settings['ai_enabled'] else "OFF"
            elif option == 'Difficulty Level':
                diff = self.ai_settings['difficulty']
                if diff <= 0.5: return "Passive"
                elif diff <= 0.8: return "Easy"
                elif diff <= 1.2: return "Normal"
                elif diff <= 1.7: return "Hard"
                elif diff <= 2.5: return "Expert"
                else: return "Nightmare"
            elif option == 'Apply Preset':
                # Find current preset
                for preset_name, preset_values in self.difficulty_presets.items():
                    if abs(self.ai_settings['difficulty'] - preset_values['difficulty']) < 0.1:
                        return preset_name
                return "Custom"
            elif option == 'Reaction Time':
                return f"{self.ai_settings['reaction_time']:.1f}s"
            elif option == 'Coordination Range':
                return f"{self.ai_settings['coordination_range']}px"
        
        elif category == 'Behavior':
            bool_settings = {
                'Formation Switching': 'formation_switching',
                'Smart Positioning': 'smart_positioning',
                'Adaptive Tactics': 'adaptive_tactics',
                'Memory System': 'memory_enabled',
                'Threat Analysis': 'threat_analysis'
            }
            
            if option in bool_settings:
                setting_key = bool_settings[option]
                return "ON" if self.ai_settings[setting_key] else "OFF"
        
        elif category == 'Groups':
            if option == 'Auto Grouping':
                return "ON" if self.ai_settings['auto_grouping'] else "OFF"
            elif option == 'Max Group Size':
                return str(self.ai_settings['max_group_size'])
        
        return ""
    
    def draw_debug_info(self, screen, font, x, y, width):
        """Draw AI debug information"""
        ai_manager = get_ai_manager()
        debug_info = ai_manager.get_debug_info()
        
        info_lines = [
            f"Total Groups: {debug_info['total_groups']}",
            f"Total Enemies: {debug_info['total_enemies']}",
            f"Difficulty: {debug_info['difficulty']:.1f}x",
            "",
            "Group States:"
        ]
        
        # Add group state info
        for group_id, state in debug_info['group_states'].items():
            formation = debug_info['group_formations'].get(group_id, 'unknown')
            info_lines.append(f"  {group_id}: {state} ({formation})")
        
        # Draw info lines
        line_height = 25
        for i, line in enumerate(info_lines[:12]):  # Limit to 12 lines
            if line:  # Skip empty lines for spacing
                info_text = font.render(line, True, (200, 200, 200))
                screen.blit(info_text, (x + 40, y + i * line_height))

# Global instance
_ai_settings_ui = None

def get_ai_settings_ui():
    """Get global AI settings UI instance"""
    global _ai_settings_ui
    if _ai_settings_ui is None:
        _ai_settings_ui = AISettingsUI()
    return _ai_settings_ui
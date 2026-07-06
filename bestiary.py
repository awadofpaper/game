"""
Bestiary System for RPG Game
Tracks enemy kills by type and rarity, displays detailed enemy information
"""

import pygame


class Bestiary:
    def __init__(self, enemy_types, enemy_rarities):
        """
        Initialize the bestiary with all enemy information
        
        Parameters:
        - enemy_types: Dictionary of all enemy types (ENEMY_TYPES)
        - enemy_rarities: Dictionary of all rarities (ENEMY_RARITIES)
        """
        self.enemy_types = enemy_types
        self.enemy_rarities = enemy_rarities
        
        # Dictionary to track kill counts for each enemy type and rarity
        self.kills = {}
        
        # Initialize kill counter for all enemy types and rarities
        for enemy_type in enemy_types:
            if enemy_type not in self.kills:
                self.kills[enemy_type] = {}
            for rarity in enemy_rarities:
                self.kills[enemy_type][rarity] = 0
    
    def record_kill(self, enemy_type, rarity):
        """Record that player has killed an enemy"""
        if enemy_type not in self.kills:
            self.kills[enemy_type] = {}
        if rarity not in self.kills[enemy_type]:
            self.kills[enemy_type][rarity] = 0
        self.kills[enemy_type][rarity] += 1
    
    def get_kill_count(self, enemy_type=None, rarity=None):
        """Get kill count for a specific enemy type/rarity, or total"""
        if enemy_type is None:
            # Return total kills
            total = 0
            for e_type in self.kills:
                for r in self.kills[e_type]:
                    total += self.kills[e_type][r]
            return total
        elif rarity is None:
            # Return total kills for enemy type
            if enemy_type not in self.kills:
                return 0
            return sum(self.kills[enemy_type].values())
        else:
            # Return specific enemy type and rarity
            if enemy_type not in self.kills or rarity not in self.kills[enemy_type]:
                return 0
            return self.kills[enemy_type][rarity]
    
    def has_encountered(self, enemy_type):
        """Check if player has encountered this enemy at least once"""
        return self.get_kill_count(enemy_type) > 0
        
    def draw(self, screen, equipment_data, font, active_entry=None, scroll_offset=0):
        """
        Draw the bestiary interface
        
        Parameters:
        - screen: The pygame surface to draw on
        - equipment_data: Dictionary of equipment data (for showing drops)
        - font: Font for text rendering
        - active_entry: Currently selected enemy type
        - scroll_offset: Scroll position for enemy list
        """
        try:
            from graphics import get_font
        except ImportError:
            get_font = None
            
        screen_width, screen_height = screen.get_size()
        
        # Draw background panel
        panel_rect = pygame.Rect(50, 50, screen_width - 100, screen_height - 100)
        pygame.draw.rect(screen, (30, 30, 40), panel_rect)
        pygame.draw.rect(screen, (60, 60, 80), panel_rect, 3)
        
        # Draw title
        title_font = get_font(None, 48) if get_font else pygame.font.SysFont(None, 48)
        title = title_font.render("Bestiary", True, (220, 220, 220))
        screen.blit(title, (screen_width//2 - title.get_width()//2, 70))
        
        # Enemy list on left side
        list_width = 250
        list_x = 70
        list_y = 130
        list_height = screen_height - 180
        
        # Draw scrollable list background
        pygame.draw.rect(screen, (40, 40, 50), (list_x, list_y, list_width, list_height))
        pygame.draw.rect(screen, (60, 60, 80), (list_x, list_y, list_width, list_height), 2)
        
        # Draw enemy list with scroll
        sorted_enemies = sorted(self.enemy_types.keys())
        visible_start = scroll_offset
        visible_count = list_height // 30
        
        for i, enemy_type in enumerate(sorted_enemies[visible_start:visible_start + visible_count]):
            actual_idx = visible_start + i
            y_pos = list_y + i * 30
            
            # Skip if would draw beyond the list area
            if y_pos + 30 > list_y + list_height:
                break
                
            # Highlight selected enemy
            bg_color = (70, 70, 90) if active_entry == enemy_type else (40, 40, 50)
            item_rect = pygame.Rect(list_x, y_pos, list_width, 28)
            pygame.draw.rect(screen, bg_color, item_rect)
            pygame.draw.rect(screen, (60, 60, 80), item_rect, 1)
            
            # Show enemy name - only if encountered
            if self.has_encountered(enemy_type):
                enemy_name = enemy_type.replace("_", " ").title()
                name_text = font.render(enemy_name, True, (220, 220, 220))
                screen.blit(name_text, (list_x + 10, y_pos + 5))
                
                # Show kill count
                total_kills = self.get_kill_count(enemy_type)
                kill_text = font.render(f"{total_kills}", True, (150, 200, 150))
                screen.blit(kill_text, (list_x + list_width - kill_text.get_width() - 10, y_pos + 5))
            else:
                # Not encountered yet - show as ???
                unknown_text = font.render("???", True, (100, 100, 100))
                screen.blit(unknown_text, (list_x + 10, y_pos + 5))
        
        # Show detailed information for selected enemy
        if active_entry and active_entry in self.enemy_types and self.has_encountered(active_entry):
            detail_x = list_x + list_width + 30
            detail_y = 130
            detail_width = screen_width - detail_x - 70
            
            # Enemy name header
            name_font = get_font(None, 36) if get_font else pygame.font.SysFont(None, 36)
            name_text = name_font.render(active_entry.replace("_", " ").title(), True, (220, 220, 220))
            screen.blit(name_text, (detail_x, detail_y))
            
            # Base stats section
            enemy_data = self.enemy_types[active_entry]
            stats_y = detail_y + 50
            
            # Format stats nicely
            health_str = f"Health: {enemy_data['max_health']}"
            damage_str = f"Damage: {enemy_data['damage']}"
            speed_str = f"Speed: {enemy_data['speed']}"
            xp_str = f"XP: {enemy_data['xp_reward']}"
            
            stats_text = font.render(f"Base Stats: {health_str}  {damage_str}  {speed_str}  {xp_str}", 
                                    True, (200, 200, 200))
            screen.blit(stats_text, (detail_x, stats_y))
            
            # Rarities section
            rarities_y = stats_y + 40
            rarity_header = font.render("Kill Statistics by Rarity:", True, (200, 200, 200))
            screen.blit(rarity_header, (detail_x, rarities_y))
            
            # Table headers
            header_y = rarities_y + 30
            pygame.draw.line(screen, (100, 100, 120), (detail_x, header_y), 
                           (detail_x + detail_width - 20, header_y))
            headers = ["Rarity", "Health Mult", "Damage Mult", "Kills"]
            header_widths = [120, 120, 120, 100]
            
            header_x = detail_x
            for i, header in enumerate(headers):
                header_text = font.render(header, True, (180, 180, 180))
                screen.blit(header_text, (header_x + 10, header_y - 20))
                header_x += header_widths[i]
            
            # Draw rarity rows
            for i, rarity in enumerate(["Common", "Uncommon", "Rare", "Epic", "Legendary"]):
                row_y = header_y + 5 + i * 28
                
                # Alternate row colors for readability
                row_color = (45, 45, 55) if i % 2 == 0 else (40, 40, 50)
                pygame.draw.rect(screen, row_color, (detail_x, row_y, sum(header_widths) - 20, 25))
                
                # Rarity color based on tier
                rarity_color = (200, 200, 200) if rarity == "Common" else \
                            (100, 255, 100) if rarity == "Uncommon" else \
                            (100, 150, 255) if rarity == "Rare" else \
                            (200, 100, 255) if rarity == "Epic" else \
                            (255, 215, 0)  # Legendary
                
                # Draw rarity name with color
                rarity_text = font.render(rarity, True, rarity_color)
                screen.blit(rarity_text, (detail_x + 10, row_y + 3))
                
                # Get multiplier data
                rarity_data = self.enemy_rarities.get(rarity, {})
                health_mult = rarity_data.get("health_multiplier", 1.0)
                damage_mult = rarity_data.get("damage_multiplier", 1.0)
                
                # Initialize column position
                col_x = detail_x + header_widths[0]
                
                # Health multiplier
                health_text = font.render(f"x{health_mult}", True, (180, 180, 180))
                screen.blit(health_text, (col_x + 10, row_y + 3))
                col_x += header_widths[1]
                
                # Damage multiplier
                damage_text = font.render(f"x{damage_mult}", True, (180, 180, 180))
                screen.blit(damage_text, (col_x + 10, row_y + 3))
                col_x += header_widths[2]
                
                # Kill count
                kills = self.get_kill_count(active_entry, rarity)
                kills_color = (150, 255, 150) if kills > 0 else (100, 100, 100)
                kills_text = font.render(f"{kills}", True, kills_color)
                screen.blit(kills_text, (col_x + 10, row_y + 3))
            
            # Additional info section
            info_y = header_y + 160
            
            # Weapon info
            weapon = enemy_data.get("weapon", "none")
            if weapon != "none":
                weapon_label = font.render("Weapon:", True, (200, 200, 200))
                weapon_value = font.render(weapon.replace("_", " ").title(), True, (180, 180, 180))
                screen.blit(weapon_label, (detail_x, info_y))
                screen.blit(weapon_value, (detail_x + 100, info_y))
                info_y += 25
            
            # Magic abilities
            magic = enemy_data.get("magic", [])
            if magic:
                magic_label = font.render("Magic:", True, (200, 200, 200))
                screen.blit(magic_label, (detail_x, info_y))
                info_y += 25
                for spell in magic[:3]:  # Show max 3 spells
                    spell_text = font.render(f"  • {spell.replace('_', ' ').title()}", True, (150, 150, 200))
                    screen.blit(spell_text, (detail_x + 10, info_y))
                    info_y += 22
                    
            # Perception range
            perception = enemy_data.get("perception_range", 0)
            if perception > 0:
                perception_text = font.render(f"Detection Range: {perception} tiles", True, (180, 180, 180))
                screen.blit(perception_text, (detail_x, info_y))
                info_y += 25
                
        elif active_entry and not self.has_encountered(active_entry):
            # Show "Not yet encountered" message
            detail_x = list_x + list_width + 30
            detail_y = 200
            
            unknown_font = get_font(None, 32) if get_font else pygame.font.SysFont(None, 32)
            unknown_text = unknown_font.render("??? Not Yet Encountered ???", True, (120, 120, 120))
            screen.blit(unknown_text, (detail_x + 50, detail_y))
            
            hint_text = font.render("Defeat this enemy type to unlock its information", True, (100, 100, 100))
            screen.blit(hint_text, (detail_x + 30, detail_y + 50))
        
        # Draw instructions at bottom
        instructions_y = screen_height - 80
        inst_font = get_font(None, 20) if get_font else pygame.font.SysFont(None, 20)
        instructions = [
            "↑/↓ or Mouse: Navigate",
            "B or ESC: Close Bestiary",
        ]
        
        inst_x = screen_width // 2 - 200
        for instruction in instructions:
            inst_text = inst_font.render(instruction, True, (150, 150, 150))
            screen.blit(inst_text, (inst_x, instructions_y))
            inst_x += 250
            
    def to_dict(self):
        """Serialize bestiary data for saving"""
        return {
            'kills': self.kills
        }
    
    def from_dict(self, data):
        """Load bestiary data from save"""
        if 'kills' in data:
            self.kills = data['kills']

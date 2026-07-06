"""
Character Stats Menu UI
Allows players to view and allocate stat points to stats
Also provides character sheet to view equipment and total stats
"""

import pygame
import math


def draw_racial_traits_panel(screen, font, player, x, y, width, max_height=None):
    """
    Draw a panel showing the player's racial traits
    
    Args:
        screen: pygame screen surface
        font: pygame font for text
        player: Player object
        x, y: Top-left position
        width: Panel width
        max_height: Maximum height (optional)
    
    Returns:
        height: Actual height used by the panel
    """
    if not hasattr(player, 'race') or not player.race:
        return 0
    
    padding = 10
    line_height = 24
    current_y = y
    
    # Panel background
    panel_color = (30, 30, 45, 220)
    
    # Title
    title_font = pygame.font.SysFont(None, 28, bold=True)
    race_name = player.race.name
    race_icon = player.race.icon
    title_text = f"{race_icon} {race_name} Racial Traits"
    title_surf = title_font.render(title_text, True, (255, 215, 0))
    current_y += padding
    
    # Calculate total height needed
    traits_count = len(player.race.traits)
    estimated_height = padding * 2 + 30 + (traits_count * (line_height * 3 + padding))
    
    if max_height and estimated_height > max_height:
        panel_height = max_height
    else:
        panel_height = estimated_height
    
    # Draw panel background
    panel_surface = pygame.Surface((width, panel_height))
    panel_surface.set_alpha(220)
    panel_surface.fill((30, 30, 45))
    pygame.draw.rect(panel_surface, (100, 100, 150), (0, 0, width, panel_height), 2, border_radius=8)
    screen.blit(panel_surface, (x, y))
    
    # Draw title
    screen.blit(title_surf, (x + width // 2 - title_surf.get_width() // 2, current_y))
    current_y += 35
    
    # Draw each trait
    trait_font = pygame.font.SysFont(None, 22, bold=True)
    desc_font = pygame.font.SysFont(None, 18)
    
    for trait in player.race.traits:
        # Trait name
        trait_name_surf = trait_font.render(f"• {trait.name}", True, (150, 255, 150))
        screen.blit(trait_name_surf, (x + padding * 2, current_y))
        current_y += line_height
        
        # Trait description (word wrap)
        desc_lines = _wrap_text(trait.description, width - padding * 4, desc_font)
        for desc_line in desc_lines[:2]:  # Max 2 lines per trait
            desc_surf = desc_font.render(desc_line, True, (200, 200, 220))
            screen.blit(desc_surf, (x + padding * 3, current_y))
            current_y += line_height - 4
        
        current_y += padding
    
    return panel_height


def draw_active_trait_indicators(screen, font, player, x, y):
    """
    Draw active trait status indicators with animations (e.g., Orc rage, Elf mana regen)
    
    Args:
        screen: pygame screen surface
        font: pygame font
        player: Player object
        x, y: Top-left position for indicators
    
    Returns:
        height: Total height used by indicators
    """
    if not hasattr(player, 'trait_manager') or not player.trait_manager:
        return 0
    
    indicators = []
    current_y = y
    
    # Get current time for animations
    current_time = pygame.time.get_ticks() / 1000.0
    
    # Check for active racial trait effects
    if hasattr(player, 'race') and player.race:
        race_id = player.race.id
        
        # Orc Rage indicator - intense pulsing
        if race_id == 'orc' and hasattr(player.trait_manager, 'orc_rage_active'):
            if player.trait_manager.orc_rage_active:
                rage_timer = player.trait_manager.orc_rage_timer
                indicators.append({
                    'icon': '⚔️',
                    'name': 'UNSTOPPABLE RAGE',
                    'color': (255, 50, 50),
                    'detail': f'{rage_timer:.1f}s',
                    'bg_color': (80, 20, 20, 200),
                    'anim_type': 'pulse_fast'  # Fast intense pulse
                })
        
        # Elf Mana Regen indicator - gentle glow
        if race_id == 'elf':
            regen_rate = 0.008  # 0.8% per second
            indicators.append({
                'icon': '✨',
                'name': 'Eternal Mana Flow',
                'color': (150, 150, 255),
                'detail': f'+{regen_rate*100:.1f}%/s',
                'bg_color': (30, 30, 80, 180),
                'anim_type': 'glow'  # Soft glow
            })
        
        # Halfling Lucky indicator - sparkle
        if race_id == 'halfling':
            indicators.append({
                'icon': '🍀',
                'name': 'Miraculous Fortune',
                'color': (100, 255, 100),
                'detail': '8% dodge',
                'bg_color': (20, 60, 20, 180),
                'anim_type': 'sparkle'  # Sparkle effect
            })
        
        # Dwarf Stone Skin indicator - steady
        if race_id == 'dwarf':
            indicators.append({
                'icon': '🛡️',
                'name': 'Stone Skin',
                'color': (180, 180, 180),
                'detail': '-12% dmg',
                'bg_color': (50, 50, 50, 180),
                'anim_type': 'pulse_slow'  # Slow steady pulse
            })
        
        # Tiefling Infernal indicator - flicker
        if race_id == 'tiefling':
            indicators.append({
                'icon': '🔥',
                'name': 'Infernal Mastery',
                'color': (255, 100, 50),
                'detail': '-15% cost',
                'bg_color': (60, 20, 20, 180),
                'anim_type': 'flicker'  # Fire flicker
            })
        
        # Human bonus - shine
        if race_id == 'human':
            indicators.append({
                'icon': '⭐',
                'name': 'Jack of All Trades',
                'color': (255, 215, 0),
                'detail': '+5% XP',
                'bg_color': (60, 50, 20, 180),
                'anim_type': 'shine'  # Star shine
            })
    
    # Draw each indicator with animations
    indicator_width = 200
    indicator_height = 35
    padding = 5
    
    for indicator in indicators:
        # Calculate animation values
        anim_type = indicator.get('anim_type', 'none')
        alpha_mod = 1.0
        border_width = 2
        color_mod = 1.0
        
        if anim_type == 'pulse_fast':
            # Fast pulse for urgent effects (Orc rage)
            pulse = 0.7 + 0.3 * abs(math.sin(current_time * 4))
            alpha_mod = pulse
            border_width = 2 + int(2 * pulse)
            color_mod = pulse
            
        elif anim_type == 'pulse_slow':
            # Slow steady pulse (Dwarf defense)
            pulse = 0.8 + 0.2 * abs(math.sin(current_time * 1.5))
            alpha_mod = pulse
            
        elif anim_type == 'glow':
            # Gentle glow (Elf mana)
            glow = 0.6 + 0.4 * abs(math.sin(current_time * 2))
            color_mod = glow
            
        elif anim_type == 'sparkle':
            # Sparkle effect (Halfling luck)
            sparkle = 0.7 + 0.3 * abs(math.sin(current_time * 3 + math.cos(current_time * 5)))
            color_mod = sparkle
            
        elif anim_type == 'flicker':
            # Fire flicker (Tiefling)
            flicker = 0.75 + 0.25 * (math.sin(current_time * 6) * 0.5 + 0.5)
            color_mod = flicker
            alpha_mod = flicker
            
        elif anim_type == 'shine':
            # Star shine (Human)
            shine = 0.8 + 0.2 * abs(math.sin(current_time * 2.5))
            color_mod = shine
        
        # Background with animation
        bg_surf = pygame.Surface((indicator_width, indicator_height))
        bg_alpha = int(indicator['bg_color'][3] * alpha_mod)
        bg_surf.set_alpha(bg_alpha)
        bg_surf.fill(indicator['bg_color'][:3])
        screen.blit(bg_surf, (x, current_y))
        
        # Border with animation
        border_color = tuple(int(c * color_mod) for c in indicator['color'])
        pygame.draw.rect(screen, border_color, (x, current_y, indicator_width, indicator_height), 
                        border_width, border_radius=5)
        
        # Icon and name with animation
        icon_font = pygame.font.SysFont(None, 24)
        name_font = pygame.font.SysFont(None, 20, bold=True)
        detail_font = pygame.font.SysFont(None, 18)
        
        text_color = tuple(int(c * color_mod) for c in indicator['color'])
        icon_surf = icon_font.render(indicator['icon'], True, text_color)
        name_surf = name_font.render(indicator['name'], True, text_color)
        detail_surf = detail_font.render(indicator['detail'], True, (220, 220, 220))
        
        screen.blit(icon_surf, (x + padding, current_y + 5))
        screen.blit(name_surf, (x + 30, current_y + 5))
        screen.blit(detail_surf, (x + 30, current_y + 20))
        
        current_y += indicator_height + padding
    
    return current_y - y


def _wrap_text(text, max_width, font):
    """Wrap text to fit within max_width"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def draw_stats_menu(screen, font, player, reputation_system=None):
    """Draw the character stats allocation menu"""
    config = player.config
    
    # Semi-transparent background
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((20, 20, 30))
    screen.blit(overlay, (0, 0))
    
    # Title
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Character Stats", True, (255, 215, 0))
    screen.blit(title, (config.SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
    
    # Available points
    points_text = font.render(f"Stat Points Available: {player.stat_points}", True, (100, 255, 100))
    screen.blit(points_text, (config.SCREEN_WIDTH // 2 - points_text.get_width() // 2, 100))
    
    # Character info
    info_y = 150
    xp_needed = player.level * 100
    info_texts = [
        f"Level: {player.level}",
        f"XP: {player.xp}/{xp_needed}",
        f"Dubloons: {player.gold}",
    ]
    
    for text in info_texts:
        surf = font.render(text, True, (200, 200, 255))
        screen.blit(surf, (50, info_y))
        info_y += 30
    
    # Reputation info
    if reputation_system:
        info_y += 10
        rep_font = pygame.font.SysFont(None, 22)
        
        # Get faction reputations
        factions = list(reputation_system.faction_reputation.keys())
        if factions:
            rep_title = font.render("Reputation:", True, (150, 200, 255))
            screen.blit(rep_title, (50, info_y))
            info_y += 30
            
            # Show all factions
            for faction in factions:
                points = reputation_system.get_faction_reputation(faction)
                level = reputation_system.get_reputation_level(points)
                color = (100, 255, 100) if points >= 0 else (255, 100, 100)
                faction_text = rep_font.render(f"  {faction}: {level} ({points})", True, color)
                screen.blit(faction_text, (70, info_y))
                info_y += 25
        else:
            # No reputation yet - show neutral
            rep_text = rep_font.render("Reputation: Neutral (No factions yet)", True, (180, 180, 180))
            screen.blit(rep_text, (50, info_y))
            info_y += 30
    
    # Allocatable stats
    allocatable_stats = [
        "Strength", "Defense", "Magic", "Stamina",
        "Speed", "Agility", "Willpower", "Luck",
        "Intelligence", "Talking"
    ]
    
    # Draw stats in two columns
    start_y = 280
    col1_x = 100
    col2_x = 450
    row_height = 35
    
    # Map stat names to player attributes
    stat_to_attr = {
        "Strength": "strength",
        "Defense": "defense",
        "Magic": "magic",
        "Stamina": "stamina_stat",
        "Speed": "speed",
        "Agility": "agility",
        "Willpower": "willpower",
        "Luck": "luck",
        "Intelligence": "intelligence",
        "Talking": "talking"
    }
    
    for i, stat_name in enumerate(allocatable_stats):
        if i < 5:
            x = col1_x
            y = start_y + (i * row_height)
        else:
            x = col2_x
            y = start_y + ((i - 5) * row_height)
        
        attr_name = stat_to_attr.get(stat_name, stat_name.lower())
        stat_value = getattr(player, attr_name, 0)
        stat_text = f"{stat_name}: {stat_value}"
        
        surf = font.render(stat_text, True, (255, 255, 255))
        screen.blit(surf, (x, y))
    
    # Draw Racial Traits Panel (right side)
    if hasattr(player, 'race') and player.race:
        traits_x = config.SCREEN_WIDTH - 360
        traits_y = 150
        traits_width = 340
        draw_racial_traits_panel(screen, font, player, traits_x, traits_y, traits_width, max_height=400)
    
    # Instructions
    inst_y = config.SCREEN_HEIGHT - 120
    instructions = [
        "Press corresponding key to allocate a stat point:",
        "1-Strength  2-Defense  3-Magic  4-Stamina  5-Speed",
        "6-Agility  7-Willpower  8-Luck  9-Intelligence  0-Talking",
        "Press C to close"
    ]
    
    for i, inst in enumerate(instructions):
        color = (150, 150, 255) if i == 0 else (180, 180, 180)
        surf = font.render(inst, True, color)
        screen.blit(surf, (config.SCREEN_WIDTH // 2 - surf.get_width() // 2, inst_y + i * 25))


def handle_stats_menu_input(event, player):
    """
    Handle input for stats menu
    Returns: (close_menu: bool, message: str or None)
    """  
    allocatable_stats = [
        "Strength", "Defense", "Magic", "Stamina", "Speed",
        "Agility", "Willpower", "Luck", "Intelligence", "Talking"
    ]
    
    key_to_stat = {
        pygame.K_1: 0,  # Strength
        pygame.K_2: 1,  # Defense
        pygame.K_3: 2,  # Magic
        pygame.K_4: 3,  # Stamina
        pygame.K_5: 4,  # Speed
        pygame.K_6: 5,  # Agility
        pygame.K_7: 6,  # Willpower
        pygame.K_8: 7,  # Luck
        pygame.K_9: 8,  # Intelligence
        pygame.K_0: 9,  # Talking
    }
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_c or event.key == pygame.K_ESCAPE:
            return True, None
        
        if event.key in key_to_stat:
            stat_idx = key_to_stat[event.key]
            stat_name = allocatable_stats[stat_idx]
            success, message = player.allocate_stat_point(stat_name)
            return False, message
    
    return False, None


def draw_character_sheet(screen, font, player, mouse_pos=None):
    """
    Draw the character sheet showing equipment and total stats
    Args:
        screen: pygame screen surface
        font: pygame font for text
        player: Player object
        mouse_pos: (x, y) tuple of mouse position for tooltips
    """
    config = player.config
    
    # Semi-transparent background
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((20, 20, 30))
    screen.blit(overlay, (0, 0))
    
    # Title
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("Character Sheet", True, (255, 215, 0))
    screen.blit(title, (config.SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
    
    # Define equipment slots and their display positions
    equipment_slots = [
        ('weapon', 'Weapon'),
        ('off_hand', 'Off-Hand'),
        ('head', 'Head'),
        ('body', 'Body'),
        ('arms', 'Arms'),
        ('hands', 'Hands'),
        ('legs', 'Legs'),
        ('feet', 'Feet'),
        ('necklace', 'Necklace'),
        ('ring1', 'Ring 1'),
        ('ring2', 'Ring 2')
    ]
    
    # Left side: Equipment slots
    left_x = 50
    equip_y = 100
    row_height = 35
    
    equip_title = font.render("Equipment:", True, (150, 200, 255))
    screen.blit(equip_title, (left_x, equip_y))
    equip_y += 40
    
    # Track hover item for tooltip
    hover_item = None
    hover_rect = None
    
    for slot_id, slot_name in equipment_slots:
        item = player.equipment.get(slot_id)
        
        # Draw slot name
        slot_text = font.render(f"{slot_name}:", True, (180, 180, 180))
        screen.blit(slot_text, (left_x, equip_y))
        
        # Draw equipped item or "Empty"
        if item and hasattr(item, 'name'):
            item_name = item.name.replace('_', ' ').title()
            # Color by rarity if available
            rarity_colors = {
                'common': (200, 200, 200),
                'uncommon': (100, 255, 100),
                'rare': (100, 150, 255),
                'epic': (200, 100, 255),
                'legendary': (255, 165, 0)
            }
            item_color = rarity_colors.get(getattr(item, 'rarity', 'common'), (200, 200, 200))
            item_text = font.render(item_name, True, item_color)
            
            # Create hitbox for hover detection
            item_rect = pygame.Rect(left_x + 150, equip_y, 250, row_height)
            
            # Check if mouse is hovering over this item
            if mouse_pos and item_rect.collidepoint(mouse_pos):
                # Draw hover highlight
                pygame.draw.rect(screen, (60, 60, 80, 100), item_rect, border_radius=5)
                hover_item = item
                hover_rect = item_rect
        else:
            item_text = font.render("Empty", True, (100, 100, 100))
        
        screen.blit(item_text, (left_x + 150, equip_y))
        equip_y += row_height
    
    # Right side: Total Stats
    right_x = 450
    stats_y = 100
    
    stats_title = font.render("Total Stats:", True, (150, 200, 255))
    screen.blit(stats_title, (right_x, stats_y))
    stats_y += 40
    
    # Stat descriptions for tooltips
    stat_descriptions = {
        "Strength": "Increases physical damage and carry weight",
        "Defense": "Reduces damage taken from attacks",
        "Magic": "Increases spell damage and mana pool",
        "Stamina": "Increases max stamina for sprinting and dodging",
        "Speed": "Increases movement speed",
        "Agility": "Improves dodge chance and critical hit rate",
        "Willpower": "Increases mental resistance and mana regen",
        "Luck": "Improves loot drops and critical chance",
        "Intelligence": "Improves crafting and learning speed",
        "Talking": "Improves dialogue options and prices",
        "Perception": "Detects hidden items, traps, and stealth"
    }
    
    # Track hover stat for tooltip
    hover_stat = None
    hover_stat_rect = None
    
    # Display main stats
    main_stats = [
        "Strength", "Defense", "Magic", "Stamina",
        "Speed", "Agility", "Willpower", "Luck",
        "Intelligence", "Talking", "Perception"
    ]
    
    for stat_name in main_stats:
        base_value = player.stats.base_stats.get(stat_name, 0)
        total_value = player.stats.get_stat(stat_name)
        bonus = total_value - base_value
        
        # Create hitbox for stat hover
        stat_rect = pygame.Rect(right_x, stats_y, 300, row_height)
        
        # Check if mouse is hovering over this stat
        if mouse_pos and stat_rect.collidepoint(mouse_pos):
            # Draw hover highlight
            pygame.draw.rect(screen, (60, 60, 80, 100), stat_rect, border_radius=5)
            hover_stat = stat_name
            hover_stat_rect = stat_rect
        
        # Draw stat name and value
        if bonus > 0:
            # Show bonus in green
            stat_text = font.render(f"{stat_name}:", True, (180, 180, 180))
            value_text = font.render(f"{total_value} ({base_value}+{bonus})", True, (100, 255, 100))
        else:
            stat_text = font.render(f"{stat_name}:", True, (180, 180, 180))
            value_text = font.render(f"{total_value}", True, (255, 255, 255))
        
        screen.blit(stat_text, (right_x, stats_y))
        screen.blit(value_text, (right_x + 140, stats_y))
        stats_y += row_height
    
    # Bottom: Character Info
    info_y = config.SCREEN_HEIGHT - 120
    char_info = [
        f"Level: {player.level}  |  XP: {player.experience}/{player.experience_to_next_level}",
        f"Health: {int(player.health)}/{player.stats.get_stat('Max_Health')}  |  Mana: {int(player.mana)}/{player.stats.get_stat('Max_Mana')}",
        f"Dubloons: {player.dubloons}  |  Weight: {int(player.current_weight)}/{int(player.base_weight_capacity)}",
    ]
    
    for text in char_info:
        surf = font.render(text, True, (200, 200, 255))
        screen.blit(surf, (config.SCREEN_WIDTH // 2 - surf.get_width() // 2, info_y))
        info_y += 30
    
    # Draw Racial Traits Panel (bottom center)
    if hasattr(player, 'race') and player.race:
        traits_x = config.SCREEN_WIDTH // 2 - 250
        traits_y = stats_y + 20  # Below stats
        traits_width = 500
        draw_racial_traits_panel(screen, font, player, traits_x, traits_y, traits_width, max_height=200)
    
    # Instructions
    inst_text = font.render("Press E or ESC to close | Hover for details", True, (150, 150, 255))
    screen.blit(inst_text, (config.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, config.SCREEN_HEIGHT - 40))
    
    # Draw tooltips
    if hover_item:
        _draw_equipment_tooltip(screen, hover_item, hover_rect, player, font)
    elif hover_stat:
        _draw_stat_tooltip(screen, hover_stat, stat_descriptions.get(hover_stat, ""), hover_stat_rect, font)


def _draw_equipment_tooltip(screen, item, item_rect, player, font):
    """Draw tooltip for equipment item"""
    tooltip_font = pygame.font.SysFont(None, 20)
    padding = 10
    line_height = 22
    
    # Build tooltip lines
    lines = []
    
    # Item name with rarity
    rarity = getattr(item, 'rarity', 'common').title()
    rarity_colors = {
        'Common': (200, 200, 200),
        'Uncommon': (100, 255, 100),
        'Rare': (100, 150, 255),
        'Epic': (200, 100, 255),
        'Legendary': (255, 165, 0)
    }
    item_name = item.name.replace('_', ' ').title()
    lines.append((f"{item_name}", rarity_colors.get(rarity, (255, 255, 255))))
    lines.append((f"[{rarity}]", rarity_colors.get(rarity, (255, 255, 255))))
    lines.append(("", (255, 255, 255)))  # Spacer
    
    # Item type
    item_type = getattr(item, 'item_type', 'equipment').replace('_', ' ').title()
    lines.append((f"Type: {item_type}", (180, 180, 180)))
    
    # Stats
    if hasattr(item, 'stats') and item.stats:
        lines.append(("", (255, 255, 255)))  # Spacer
        lines.append(("Stats:", (150, 200, 255)))
        for stat, value in item.stats.items():
            if stat not in ['stack_count', 'max_stack']:
                stat_display = stat.replace('_', ' ').title()
                color = (100, 255, 100) if value > 0 else (255, 100, 100)
                lines.append((f"  +{value} {stat_display}", color))
    
    # Level requirement
    if hasattr(item, 'level_req'):
        level_req = getattr(item, 'level_req', 1)
        if level_req > 1:
            color = (100, 255, 100) if player.level >= level_req else (255, 100, 100)
            lines.append(("", (255, 255, 255)))  # Spacer
            lines.append((f"Requires Level {level_req}", color))
    
    # Calculate tooltip size
    max_width = max(tooltip_font.size(line[0])[0] for line in lines if line[0])
    tooltip_width = max_width + padding * 2
    tooltip_height = len(lines) * line_height + padding * 2
    
    # Position tooltip to the right of the item
    tooltip_x = item_rect.right + 10
    tooltip_y = item_rect.top
    
    # Keep tooltip on screen
    if tooltip_x + tooltip_width > screen.get_width():
        tooltip_x = item_rect.left - tooltip_width - 10
    if tooltip_y + tooltip_height > screen.get_height():
        tooltip_y = screen.get_height() - tooltip_height - 10
    
    # Draw tooltip background
    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    pygame.draw.rect(screen, (20, 20, 30, 240), tooltip_rect, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 150), tooltip_rect, 2, border_radius=5)
    
    # Draw tooltip text
    y_offset = tooltip_y + padding
    for line_text, color in lines:
        if line_text:
            text_surf = tooltip_font.render(line_text, True, color)
            screen.blit(text_surf, (tooltip_x + padding, y_offset))
        y_offset += line_height


def _draw_stat_tooltip(screen, stat_name, description, stat_rect, font):
    """Draw tooltip for stat"""
    tooltip_font = pygame.font.SysFont(None, 20)
    padding = 10
    line_height = 22
    
    # Build tooltip lines
    lines = [
        (stat_name, (255, 215, 0)),
        ("", (255, 255, 255)),  # Spacer
        (description, (200, 200, 200))
    ]
    
    # Calculate tooltip size
    max_width = max(tooltip_font.size(line[0])[0] for line in lines if line[0])
    tooltip_width = min(max_width + padding * 2, 300)  # Max width 300
    
    # Word wrap if needed
    if max_width > 280:
        wrapped_lines = []
        for line_text, color in lines:
            if line_text and tooltip_font.size(line_text)[0] > 280:
                words = line_text.split()
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if tooltip_font.size(test_line)[0] <= 280:
                        current_line = test_line
                    else:
                        wrapped_lines.append((current_line, color))
                        current_line = word
                if current_line:
                    wrapped_lines.append((current_line, color))
            else:
                wrapped_lines.append((line_text, color))
        lines = wrapped_lines
    
    tooltip_height = len(lines) * line_height + padding * 2
    
    # Position tooltip to the right of the stat
    tooltip_x = stat_rect.right + 10
    tooltip_y = stat_rect.top
    
    # Keep tooltip on screen
    if tooltip_x + tooltip_width > screen.get_width():
        tooltip_x = stat_rect.left - tooltip_width - 10
    if tooltip_y + tooltip_height > screen.get_height():
        tooltip_y = screen.get_height() - tooltip_height - 10
    
    # Draw tooltip background
    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    pygame.draw.rect(screen, (20, 20, 30, 240), tooltip_rect, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 150), tooltip_rect, 2, border_radius=5)
    
    # Draw tooltip text
    y_offset = tooltip_y + padding
    for line_text, color in lines:
        if line_text:
            text_surf = tooltip_font.render(line_text, True, color)
            screen.blit(text_surf, (tooltip_x + padding, y_offset))
        y_offset += line_height



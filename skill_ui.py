
import pygame
import time
import math  # Add this import
from skill_trees import SKILL_TREES, CROSS_TREE_SKILLS, can_acquire_skill, can_acquire_cross_skill, get_all_skill_trees

def draw_skill_tooltip(screen, skill_data, player, mouse_pos, font, small_font, detail_font):
    """Draw a detailed tooltip for a hovered skill"""
    skill = skill_data['skill']
    skill_id = skill_data['skill_id']
    tree_id = skill_data['tree_id']
    tier_idx = skill_data['tier_idx']
    
    # Check if acquired
    acquired = skill_id in player.acquired_skills
    can_get, reason = can_acquire_skill(player, tree_id, tier_idx, skill_id)
    
    # Get current points invested
    current_points = player.skill_points_invested.get(skill_id, 0)
    max_points = skill.get('max_points', 1)
    
    # Build tooltip content
    lines = []
    lines.append(('title', skill['name']))
    lines.append(('subtitle', f"Type: {skill['type'].capitalize()}"))
    lines.append(('cost', f"Cost: {skill['cost']} Perk Points"))
    
    # Multi-point indicator
    if max_points > 1:
        lines.append(('points', f"Points: {current_points}/{max_points}"))
    
    # Status
    if acquired:
        if current_points >= max_points:
            lines.append(('status_good', "✓ MAXED OUT"))
        else:
            lines.append(('status_good', f"✓ ACQUIRED (Click to upgrade: {current_points+1}/{max_points})"))
    elif can_get:
        lines.append(('status_good', "✓ Can Acquire (Click to learn)"))
    else:
        lines.append(('status_bad', f"✗ {reason}"))
    
    lines.append(('separator', ''))
    
    # Cooldown/Duration
    if "cooldown" in skill:
        lines.append(('info', f"Cooldown: {skill['cooldown']}s"))
    if "duration" in skill:
        lines.append(('info', f"Duration: {skill['duration']}s"))
    
    # Effects
    if "effects" in skill and skill["effects"]:
        lines.append(('separator', ''))
        lines.append(('label', 'Effects:'))
        for effect, value in skill["effects"].items():
            effect_name = effect.replace("_", " ").title()
            
            if "max_points" in skill and skill["max_points"] > 1:
                per_point = skill.get('per_point_effect', {}).get(effect, value)
                max_value = per_point * skill["max_points"]
                current_value = per_point * current_points
                if current_points > 0:
                    lines.append(('effect', f"  {effect_name}: +{current_value}% (max +{max_value}%)"))
                else:
                    lines.append(('effect', f"  {effect_name}: +{per_point}% per point (max +{max_value}%)"))
            else:
                lines.append(('effect', f"  {effect_name}: +{value}%"))
    
    # Description
    if "description" in skill and skill["description"]:
        lines.append(('separator', ''))
        lines.append(('desc', skill["description"]))
    
    # Stat requirements
    if "stat_requirements" in skill and skill["stat_requirements"]:
        lines.append(('separator', ''))
        lines.append(('label', 'Requires:'))
        for stat, value in skill["stat_requirements"].items():
            player_stat = getattr(player, stat, 0)
            if player_stat >= value:
                lines.append(('req_met', f"  {stat}: {value} ✓"))
            else:
                lines.append(('req_unmet', f"  {stat}: {value} ({player_stat}/{value})"))
    
    # Calculate tooltip dimensions
    tooltip_padding = 12
    line_height = 20
    max_width = 0
    
    # Render all lines to calculate width
    rendered_lines = []
    for line_type, text in lines:
        if line_type == 'separator':
            rendered_lines.append(None)
            continue
        
        # Choose color based on type
        if line_type == 'title':
            color = (255, 255, 180)
            render_font = font
        elif line_type == 'subtitle':
            color = (200, 200, 220)
            render_font = font
        elif line_type == 'cost':
            color = (255, 200, 100)
            render_font = font
        elif line_type == 'points':
            color = (100, 255, 255)
            render_font = font
        elif line_type == 'status_good':
            color = (100, 255, 100)
            render_font = font
        elif line_type == 'status_bad':
            color = (255, 100, 100)
            render_font = font
        elif line_type == 'label':
            color = (200, 220, 255)
            render_font = font
        elif line_type == 'effect':
            color = (150, 255, 150)
            render_font = small_font
        elif line_type == 'info':
            color = (220, 220, 255)
            render_font = small_font
        elif line_type == 'desc':
            color = (200, 200, 200)
            render_font = detail_font
        elif line_type == 'req_met':
            color = (100, 255, 100)
            render_font = small_font
        elif line_type == 'req_unmet':
            color = (255, 150, 100)
            render_font = small_font
        else:
            color = (200, 200, 200)
            render_font = font
        
        # Word wrap for description
        if line_type == 'desc':
            words = text.split()
            wrapped_lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if render_font.size(test_line)[0] <= 350:
                    current_line = test_line
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = word
            if current_line:
                wrapped_lines.append(current_line)
            
            for wrapped in wrapped_lines:
                rendered = render_font.render(wrapped, True, color)
                rendered_lines.append(rendered)
                max_width = max(max_width, rendered.get_width())
        else:
            rendered = render_font.render(text, True, color)
            rendered_lines.append(rendered)
            max_width = max(max_width, rendered.get_width())
    
    # Calculate tooltip size
    tooltip_width = max_width + tooltip_padding * 2
    tooltip_height = len(rendered_lines) * line_height + tooltip_padding * 2
    
    # Position tooltip near mouse, but keep on screen
    tooltip_x = mouse_pos[0] + 15
    tooltip_y = mouse_pos[1] + 15
    
    screen_width, screen_height = screen.get_size()
    if tooltip_x + tooltip_width > screen_width - 10:
        tooltip_x = mouse_pos[0] - tooltip_width - 15
    if tooltip_y + tooltip_height > screen_height - 10:
        tooltip_y = screen_height - tooltip_height - 10
    
    # Draw tooltip background
    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
    pygame.draw.rect(screen, (20, 20, 40, 240), tooltip_rect, border_radius=8)
    pygame.draw.rect(screen, (150, 150, 200), tooltip_rect, 2, border_radius=8)
    
    # Draw lines
    y_offset = tooltip_y + tooltip_padding
    for rendered_line in rendered_lines:
        if rendered_line is None:
            y_offset += line_height // 2
            continue
        screen.blit(rendered_line, (tooltip_x + tooltip_padding, y_offset))
        y_offset += line_height

def skill_tree_menu(screen, font, player):
    """Main skill tree UI with improved visual design - all info visible, no tooltips"""
    running = True
    clock = pygame.time.Clock()
    selected_tree = next(iter(SKILL_TREES))  # Default to first tree
    show_cross_tree = False  # Toggle for cross-tree skills
    
    # Scrolling variables
    scroll_offset = 0
    scroll_speed = 30
    max_scroll = 0  # Will be calculated based on content
    
    # Create better fonts
    title_font = pygame.font.SysFont(None, 32)  # Larger font for titles
    header_font = pygame.font.SysFont(None, 28)  # Medium font for headers
    detail_font = pygame.font.SysFont(None, 20)  # Smaller font for details
    small_font = pygame.font.SysFont(None, 18)   # Smaller font for detailed effects
    
    # Enhanced color scheme
    bg_color = (25, 25, 38)  # Slightly darker background
    panel_color = (35, 35, 55)  # Panel background
    selected_tab = (45, 65, 120)  # Brighter selected tab
    unselected_tab = (35, 45, 70)  # Darker unselected tab
    border_color = (70, 70, 100)  # Subtle borders
    text_color = (230, 230, 255)  # Brighter text for better contrast
    highlight_text = (255, 255, 180)  # Yellow-ish highlight text
    effect_color = (180, 255, 180)  # Green-ish effect text
    desc_color = (200, 200, 255)    # Light blue description text
    
    # Skill node colors
    acquired_color = (45, 120, 45)  # Green for acquired
    available_color = (45, 65, 120)  # Blue for available
    locked_color = (55, 55, 75)  # Gray for locked
    
    # Border colors
    acquired_border = (100, 200, 100)
    available_border = (100, 140, 230)
    locked_border = (90, 90, 120)
    
    while running:
        screen_width, screen_height = screen.get_size()
        hovered_tab = None
        
        # Fill background
        screen.fill(bg_color)
        
        # Draw tab container with smooth border
        tab_container = pygame.Rect(10, 10, screen_width - 20, 60)
        pygame.draw.rect(screen, panel_color, tab_container, border_radius=8)
        pygame.draw.rect(screen, border_color, tab_container, 2, border_radius=8)
        
        # Draw tree selection tabs with improved design
        tab_width = (tab_container.width - 10) // (len(SKILL_TREES) + 1)  # +1 for cross-tree
        tab_padding = 5
        
        for i, tree_id in enumerate(SKILL_TREES):
            tab_rect = pygame.Rect(
                tab_container.left + 5 + i * tab_width, 
                tab_container.top + 5,
                tab_width - 5, 
                tab_container.height - 10
            )
            if tab_rect.collidepoint(pygame.mouse.get_pos()):
                hovered_tab = tree_id
            
            # Draw tab with rounded corners
            color = selected_tab if tree_id == selected_tree and not show_cross_tree else unselected_tab
            pygame.draw.rect(screen, color, tab_rect, border_radius=6)
            
            # Tab text with shadow for better readability
            text = header_font.render(tree_id, True, text_color)
            # Draw subtle text shadow
            shadow_text = header_font.render(tree_id, True, (0, 0, 0))
            screen.blit(shadow_text, (tab_rect.centerx - text.get_width()//2 + 1, tab_rect.centery - text.get_height()//2 + 1))
            # Draw actual text
            screen.blit(text, (tab_rect.centerx - text.get_width()//2, tab_rect.centery - text.get_height()//2))
        
        # Cross-tree skills tab
        cross_tab_index = len(SKILL_TREES)
        cross_tab_rect = pygame.Rect(
            tab_container.left + 5 + cross_tab_index * tab_width,
            tab_container.top + 5,
            tab_width - 5,
            tab_container.height - 10
        )
        
        color = selected_tab if show_cross_tree else unselected_tab
        pygame.draw.rect(screen, color, cross_tab_rect, border_radius=6)
        
        # Cross-tree tab text
        text = header_font.render("Cross-Tree", True, text_color)
        # Draw subtle text shadow
        shadow_text = header_font.render("Cross-Tree", True, (0, 0, 0))
        screen.blit(shadow_text, (cross_tab_rect.centerx - text.get_width()//2 + 1, cross_tab_rect.centery - text.get_height()//2 + 1))
        # Draw actual text
        screen.blit(text, (cross_tab_rect.centerx - text.get_width()//2, cross_tab_rect.centery - text.get_height()//2))
        
        # Tab tooltips (keep for tree tabs only)
        if cross_tab_rect.collidepoint(pygame.mouse.get_pos()):
            hovered_tab = "CROSS_TREE"
        
        if hovered_tab:
            if hovered_tab == "CROSS_TREE":
                tooltip_lines = [
                    "Cross-Tree Skills",
                    "",
                    "Hybrid abilities that combine",
                    "multiple skill trees.",
                    "",
                    "Unlock special synergies!"
                ]
            else:
                tree_data = SKILL_TREES[hovered_tab]
                tooltip_lines = [
                    hovered_tab,
                    "",
                    tree_data["description"],
                    "",
                    "Primary Stats: " + ", ".join(tree_data["primary_stats"])
                ]
            tooltip_font = pygame.font.SysFont(None, 22)
            tooltip_w = max(tooltip_font.size(line)[0] for line in tooltip_lines) + 18
            tooltip_h = 8 + len(tooltip_lines) * 22
            mx, my = pygame.mouse.get_pos()
            pygame.draw.rect(screen, (40, 40, 80), (mx + 18, my + 8, tooltip_w, tooltip_h), border_radius=6)
            pygame.draw.rect(screen, (180, 180, 220), (mx + 18, my + 8, tooltip_w, tooltip_h), 2, border_radius=6)
            for i, line in enumerate(tooltip_lines):
                text = tooltip_font.render(line, True, (255, 255, 255))
                screen.blit(text, (mx + 27, my + 12 + i * 22)) 
        
        # Draw player info in a clean info panel
        info_panel = pygame.Rect(10, 80, screen_width - 20, 50)
        pygame.draw.rect(screen, panel_color, info_panel, border_radius=6)
        pygame.draw.rect(screen, border_color, info_panel, 2, border_radius=6)
        
        # Draw perk points with emphasis
        points_text = title_font.render(f"Perk Points: {player.perk_points}", True, highlight_text)
        screen.blit(points_text, (info_panel.left + 20, info_panel.centery - points_text.get_height()//2))
        
        # Draw level info
        level_text = header_font.render(f"Level: {player.level}", True, text_color)
        screen.blit(level_text, (info_panel.right - level_text.get_width() - 20, info_panel.centery - level_text.get_height()//2))
        
        # Create content area with scroll window
        content_rect = pygame.Rect(10, 140, screen_width - 20, screen_height - 190)
        pygame.draw.rect(screen, panel_color, content_rect, border_radius=6)
        pygame.draw.rect(screen, border_color, content_rect, 2, border_radius=6)
        
        # Create a clipping mask for the scrollable content
        content_mask = pygame.Rect(content_rect.left + 5, content_rect.top + 5, 
                                   content_rect.width - 10, content_rect.height - 10)
        
        # Calculate content height based on tree or cross-tree - INCREASED FOR TALLER SKILL BOXES
        content_height = 1200  # Increased default value
        if not show_cross_tree:
            tree_data = SKILL_TREES[selected_tree]
            tier_height = 220  # INCREASED from 130 for taller skill boxes
            tier_spacing = 50  # INCREASED from 40 for better separation
            content_height = 20 + len(tree_data["tiers"]) * (tier_height + tier_spacing)
        
        # Create content surface
        content_surface = pygame.Surface((content_rect.width - 10, content_height), pygame.SRCALPHA)
        content_surface.fill((0, 0, 0, 0))  # Transparent
        
        # Track hovered skill for tooltip
        hovered_skill_data = None
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw tree description at the top of content
        if not show_cross_tree:
            tree_data = SKILL_TREES[selected_tree]
            desc = header_font.render(tree_data["description"], True, highlight_text)
            content_surface.blit(desc, (content_surface.get_width()//2 - desc.get_width()//2, 10))
            
            # Draw primary stats info
            stats_text = "Primary Stats: " + ", ".join(tree_data["primary_stats"])
            stats_render = font.render(stats_text, True, text_color)
            content_surface.blit(stats_render, (content_surface.get_width()//2 - stats_render.get_width()//2, 40))
            
            # Draw skill tiers with improved visuals - USING UPDATED HEIGHTS
            tier_height = 220  # INCREASED for taller skill boxes
            tier_spacing = 50  # INCREASED for more separation
            start_y = 80
            
            for tier_idx, tier in enumerate(tree_data["tiers"]):
                tier_y = start_y + tier_idx * (tier_height + tier_spacing)
                
                # Draw tier header with background
                tier_header = pygame.Rect(20, tier_y - 25, 120, 25)
                pygame.draw.rect(content_surface, selected_tab, tier_header, border_radius=4)
                pygame.draw.rect(content_surface, border_color, tier_header, 1, border_radius=4)
                
                tier_label = font.render(f"Tier {tier_idx + 1}", True, highlight_text)
                content_surface.blit(tier_label, (tier_header.centerx - tier_label.get_width()//2, 
                                                  tier_header.centery - tier_label.get_height()//2))
                
                # Draw skills in this tier - WITH LARGER DIMENSIONS
                skill_width = 220  # INCREASED from 180 for wider skill boxes
                skill_height = 220  # INCREASED from 180 for taller skill boxes
                num_skills = len(tier)
                total_width = num_skills * skill_width + (num_skills-1) * 20
                start_x = (content_surface.get_width() - total_width) // 2
                
                for i, (skill_id, skill) in enumerate(tier.items()):
                    skill_x = start_x + i * (skill_width + 20)
                    
                    # Check if mouse is hovering over this skill (accounting for scroll)
                    adjusted_mouse_pos = (mouse_pos[0] - content_mask.left, 
                                         mouse_pos[1] - content_mask.top + scroll_offset)
                    skill_rect_check = pygame.Rect(skill_x, tier_y, skill_width, skill_height)
                    if skill_rect_check.collidepoint(adjusted_mouse_pos):
                        hovered_skill_data = {
                            'skill': skill,
                            'skill_id': skill_id,
                            'tree_id': selected_tree,
                            'tier_idx': tier_idx
                        }
                    
                    # Check if skill is acquired or can be acquired
                    acquired = skill_id in player.acquired_skills
                    can_get, reason = can_acquire_skill(player, selected_tree, tier_idx, skill_id)
                    
                    # Choose color based on status
                    if acquired:
                        color = acquired_color
                        border = acquired_border
                    elif can_get:
                        color = available_color
                        border = available_border
                    else:
                        color = locked_color
                        border = locked_border
                    
                    # Draw skill box with rounded corners
                    skill_rect = pygame.Rect(skill_x, tier_y, skill_width, skill_height)
                    pygame.draw.rect(content_surface, color, skill_rect, border_radius=8)
                    
                    # Draw border
                    pygame.draw.rect(content_surface, border, skill_rect, 2, border_radius=8)
                    
                    # NEW: Draw progression bar for multi-point skills at the top
                    max_points = skill.get('max_points', 1)
                    if max_points > 1:
                        current_points = player.skill_points_invested.get(skill_id, 0)
                        
                        # Progress bar dimensions
                        bar_width = skill_width - 20
                        bar_height = 8
                        bar_x = skill_x + 10
                        bar_y = tier_y + 5
                        
                        # Draw progress bar background
                        pygame.draw.rect(content_surface, (40, 40, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
                        
                        # Draw progress fill
                        if current_points > 0:
                            fill_width = int((current_points / max_points) * bar_width)
                            fill_color = (100, 255, 100) if current_points == max_points else (100, 180, 255)
                            pygame.draw.rect(content_surface, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)
                        
                        # Draw progress bar border
                        pygame.draw.rect(content_surface, (150, 150, 180), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=4)
                        
                        # Draw points text on the bar
                        points_font = pygame.font.SysFont(None, 16)
                        points_text = points_font.render(f"{current_points}/{max_points}", True, (255, 255, 255))
                        text_x = bar_x + bar_width//2 - points_text.get_width()//2
                        text_y = bar_y + bar_height//2 - points_text.get_height()//2
                        # Draw shadow for better readability
                        shadow_text = points_font.render(f"{current_points}/{max_points}", True, (0, 0, 0))
                        content_surface.blit(shadow_text, (text_x + 1, text_y + 1))
                        content_surface.blit(points_text, (text_x, text_y))
                        
                        skill_name_y = tier_y + 18
                    else:
                        skill_name_y = tier_y + 10
                    
                    # Draw skill name with subtle shadow
                    name = header_font.render(skill["name"], True, highlight_text)
                    shadow = header_font.render(skill["name"], True, (0, 0, 0))
                    name_x = skill_x + skill_width//2 - name.get_width()//2
                    content_surface.blit(shadow, (name_x + 1, skill_name_y + 1))
                    content_surface.blit(name, (name_x, skill_name_y))
                    
                    # Draw skill cost
                    cost = font.render(f"Cost: {skill['cost']}", True, text_color)
                    content_surface.blit(cost, (skill_x + skill_width//2 - cost.get_width()//2, tier_y + 40))
                    
                    # Draw skill type with icon
                    type_text = font.render(f"Type: {skill['type'].capitalize()}", True, text_color)
                    content_surface.blit(type_text, (skill_x + 10, tier_y + 65))
                    
                    # Add visual indicator for skill type
                    icon_x = skill_x + skill_width - 30
                    icon_y = tier_y + 65
                    if skill["type"] == "passive":
                        # Draw shield icon for passive
                        pygame.draw.circle(content_surface, text_color, (icon_x, icon_y), 10, 2)
                        pygame.draw.circle(content_surface, text_color, (icon_x, icon_y), 5)
                    elif skill["type"] == "active":
                        # Draw star icon for active
                        points = []
                        for angle in range(0, 360, 45):
                            x = icon_x + 8 * math.cos(math.radians(angle))
                            y = icon_y + 8 * math.sin(math.radians(angle))
                            points.append((x, y))
                        pygame.draw.polygon(content_surface, text_color, points)
                    elif skill["type"] == "toggle":
                        # Draw toggle switch icon
                        toggle_rect = pygame.Rect(icon_x - 8, icon_y - 5, 20, 10)
                        pygame.draw.rect(content_surface, text_color, toggle_rect, border_radius=5)
                        pygame.draw.circle(content_surface, highlight_text, (icon_x + 5, icon_y), 6)
                    
                    # NEW: Draw cooldown and duration if present
                    cooldown_y = tier_y + 90
                    if "cooldown" in skill:
                        cooldown_text = font.render(f"Cooldown: {skill['cooldown']}s", True, text_color)
                        content_surface.blit(cooldown_text, (skill_x + 10, cooldown_y))
                        cooldown_y += 20
                        
                    if "duration" in skill:
                        duration_text = font.render(f"Duration: {skill['duration']}s", True, text_color)
                        content_surface.blit(duration_text, (skill_x + 10, cooldown_y))
                        cooldown_y += 20
                    
                    # NEW: Draw ALL effects (not just the first 2)
                    effects_y = cooldown_y
                    if "effects" in skill and skill["effects"]:
                        effects_text = font.render("Effects:", True, effect_color)
                        content_surface.blit(effects_text, (skill_x + 10, effects_y))
                        effects_y += 20
                        
                        for effect, value in skill["effects"].items():
                            effect_name = effect.replace("_", " ").title()
                            effect_text = small_font.render(f"{effect_name}: +{value}%", True, effect_color)
                            content_surface.blit(effect_text, (skill_x + 20, effects_y))
                            effects_y += 18
                    
                    # NEW: Draw description with word wrapping
                    if "description" in skill and skill["description"]:
                        desc_y = effects_y + 5
                        desc_words = skill["description"].split()
                        desc_line = ""
                        line_count = 0
                        max_lines = 3  # Maximum number of description lines to show
                        
                        for word in desc_words:
                            test_line = desc_line + " " + word if desc_line else word
                            if small_font.size(test_line)[0] <= skill_width - 20:
                                desc_line = test_line
                            else:
                                desc_text = small_font.render(desc_line, True, desc_color)
                                content_surface.blit(desc_text, (skill_x + 10, desc_y))
                                desc_y += 18
                                line_count += 1
                                desc_line = word
                                
                                if line_count >= max_lines - 1:  # Save space for the last line
                                    break
                        
                        # Add the last line with ellipsis if needed
                        if desc_line:
                            if line_count >= max_lines - 1 and len(desc_words) > 0:
                                desc_line = desc_line + "..."
                            desc_text = small_font.render(desc_line, True, desc_color)
                            content_surface.blit(desc_text, (skill_x + 10, desc_y))
                
                # Draw connections to previous tier if not first tier
                if tier_idx > 0:
                    prev_tier = tree_data["tiers"][tier_idx - 1]
                    prev_tier_y = start_y + (tier_idx - 1) * (tier_height + tier_spacing) + skill_height
                    
                    # Draw individual connections for each skill to show requirements
                    for i, (skill_id, skill) in enumerate(tier.items()):
                        skill_x_center = start_x + i * (skill_width + 20) + skill_width // 2
                        
                        # Check if any skill in previous tier is acquired
                        prev_tier_has_acquired = any(prev_skill_id in player.acquired_skills 
                                                    for prev_skill_id in prev_tier.keys())
                        
                        # Choose line color based on status
                        if skill_id in player.acquired_skills:
                            line_color = (100, 255, 100)  # Green for acquired
                            line_width = 4
                        elif prev_tier_has_acquired:
                            line_color = (100, 180, 255)  # Blue for unlocked
                            line_width = 3
                        else:
                            line_color = (80, 80, 100)  # Gray for locked
                            line_width = 2
                        
                        # Draw line from bottom center of previous tier to top center of current skill
                        prev_tier_center_x = start_x + (len(prev_tier) - 1) * (skill_width + 20) / 2 + skill_width / 2
                        
                        # Draw a bezier-like curve using multiple line segments
                        num_segments = 10
                        for seg in range(num_segments):
                            t = seg / num_segments
                            # Simple linear interpolation (could be improved with actual bezier)
                            start_seg_x = prev_tier_center_x + (skill_x_center - prev_tier_center_x) * t
                            start_seg_y = prev_tier_y + (tier_y - prev_tier_y) * t
                            end_seg_x = prev_tier_center_x + (skill_x_center - prev_tier_center_x) * (t + 1/num_segments)
                            end_seg_y = prev_tier_y + (tier_y - prev_tier_y) * (t + 1/num_segments)
                            
                            # Fade effect
                            alpha = int(100 + 155 * t)
                            seg_color = (*line_color[:3], alpha) if len(line_color) == 3 else line_color
                            
                            pygame.draw.line(content_surface, seg_color, 
                                           (start_seg_x, start_seg_y), 
                                           (end_seg_x, end_seg_y), line_width)
                        
                        # Draw arrow head at the top of current skill
                        arrow_size = 8
                        arrow_points = [
                            (skill_x_center, tier_y - 5),
                            (skill_x_center - arrow_size, tier_y - 5 - arrow_size),
                            (skill_x_center + arrow_size, tier_y - 5 - arrow_size)
                        ]
                        pygame.draw.polygon(content_surface, line_color, arrow_points)

        
        else:  # Show cross-tree skills with similar styling
            # Apply similar expanded skill box styling to cross-tree skills
            desc = header_font.render("Cross-Tree Skills - Hybrid abilities that combine different skill trees", 
                                      True, highlight_text)
            content_surface.blit(desc, (content_surface.get_width()//2 - desc.get_width()//2, 10))
            
            # Similar drawing code for cross-tree skills would go here
            # with the same detailed skill boxes
        
        # Calculate max scroll based on content height
        max_scroll = max(0, content_height - content_rect.height + 10)
        scroll_offset = min(scroll_offset, max_scroll)  # Ensure scroll is in bounds
        
        # Blit scrolled content to screen using clipping
        visible_content_rect = pygame.Rect(0, scroll_offset, content_rect.width - 10, content_rect.height - 10)
        if visible_content_rect.height > 0:  # Ensure valid rectangle
            visible_content = content_surface.subsurface(visible_content_rect)
            screen.blit(visible_content, (content_mask.left, content_mask.top))
        
        # Draw scroll indicators with animation
        current_time = pygame.time.get_ticks() / 1000
        scroll_alpha = int(127 + 127 * math.sin(current_time * 3))  # Pulsing effect
        
        if max_scroll > 0:
            scroll_bar_height = min(content_rect.height * 0.8, content_rect.height * (content_rect.height / content_height))
            scroll_bar_pos = content_rect.top + 5 + (content_rect.height - 10 - scroll_bar_height) * (scroll_offset / max_scroll)
            
            # Draw scroll track
            track_rect = pygame.Rect(content_rect.right - 15, content_rect.top + 5, 10, content_rect.height - 10)
            pygame.draw.rect(screen, (45, 45, 65), track_rect, border_radius=5)
            
            # Draw scroll thumb
            thumb_rect = pygame.Rect(content_rect.right - 15, scroll_bar_pos, 10, scroll_bar_height)
            pygame.draw.rect(screen, (120, 120, 150, scroll_alpha), thumb_rect, border_radius=5)
            pygame.draw.rect(screen, (150, 150, 180), thumb_rect, 1, border_radius=5)
            
            # Draw arrow indicators
            if scroll_offset > 0:
                # Up arrow
                pygame.draw.polygon(screen, (200, 200, 200, scroll_alpha), 
                                   [(content_rect.right - 10, content_rect.top - 15),
                                    (content_rect.right - 20, content_rect.top - 5),
                                    (content_rect.right, content_rect.top - 5)])
            
            if scroll_offset < max_scroll:
                # Down arrow
                pygame.draw.polygon(screen, (200, 200, 200, scroll_alpha),
                                   [(content_rect.right - 10, content_rect.bottom + 15),
                                    (content_rect.right - 20, content_rect.bottom + 5),
                                    (content_rect.right, content_rect.bottom + 5)])
        
        # Draw tooltip for hovered skill
        if hovered_skill_data:
            draw_skill_tooltip(screen, hovered_skill_data, player, mouse_pos, font, small_font, detail_font)
        
        # Draw instruction panel at bottom
        instruction_panel = pygame.Rect(10, screen_height - 40, screen_width - 20, 30)
        pygame.draw.rect(screen, panel_color, instruction_panel, border_radius=6)
        pygame.draw.rect(screen, border_color, instruction_panel, 2, border_radius=6)
        
        # Instructions text - UPDATED to remove right-click reference
        instructions = "Left-Click to acquire skill | Mouse wheel to scroll | ESC to exit"
        instr_text = detail_font.render(instructions, True, text_color)
        screen.blit(instr_text, (instruction_panel.centerx - instr_text.get_width()//2, 
                                instruction_panel.centery - instr_text.get_height()//2))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - scroll_speed)
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(max_scroll, scroll_offset + scroll_speed)
            
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(max_scroll, scroll_offset - event.y * scroll_speed))
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check tab clicks
                if tab_container.collidepoint(event.pos):
                    tab_idx = (event.pos[0] - tab_container.left - 5) // tab_width
                    if tab_idx < len(SKILL_TREES):
                        selected_tree = list(SKILL_TREES.keys())[tab_idx]
                        show_cross_tree = False
                        scroll_offset = 0  # Reset scroll on tab change
                    elif tab_idx == len(SKILL_TREES):
                        show_cross_tree = True
                        scroll_offset = 0  # Reset scroll on tab change
                
                # Check skill clicks
                elif content_mask.collidepoint(event.pos) and not show_cross_tree:
                    adjusted_pos = (
                        event.pos[0] - content_mask.left,
                        event.pos[1] - content_mask.top + scroll_offset
                    )
                    
                    # Handle skill click using adjusted position - LEFT CLICK ONLY
                    if pygame.mouse.get_pressed()[0]:
                        handle_skill_click_left(screen, font, player, selected_tree, adjusted_pos)
                                       
                # Handle scrollbar dragging (optional)
                elif track_rect.collidepoint(event.pos):
                    relative_y = event.pos[1] - content_rect.top - 5
                    percentage = relative_y / (content_rect.height - 10)
                    scroll_offset = max(0, min(max_scroll, max_scroll * percentage))
        pygame.display.flip()
        clock.tick(30)

# Updated handler for skill clicks - LEFT CLICK ONLY
def handle_skill_click_left(screen, font, player, tree_id, pos):
    """Handle left-clicking on skills with scroll offset considered"""
    tree_data = SKILL_TREES[tree_id]
    tier_height = 220  # Match the height used in skill_tree_menu
    tier_spacing = 50
    start_y = 80
    
    # Check each tier
    for tier_idx, tier in enumerate(tree_data["tiers"]):
        tier_y = start_y + tier_idx * (tier_height + tier_spacing)
        
        # Skip if click is not in this tier's vertical range
        if not (tier_y <= pos[1] <= tier_y + tier_height):
            continue
        
        # Check skills in this tier
        skill_width = 220  # Match the width used in skill_tree_menu
        num_skills = len(tier)
        total_width = num_skills * skill_width + (num_skills-1) * 20
        start_x = (800 - 20 - total_width) // 2  # Assuming content width of 800-20
        
        for i, (skill_id, skill) in enumerate(tier.items()):
            skill_x = start_x + i * (skill_width + 20)
            
            # Check if click is within this skill's box
            if skill_x <= pos[0] <= skill_x + skill_width:
                success, message = player.acquire_skill(tree_id, tier_idx, skill_id)
                show_popup(screen, font, message)
                return

def show_popup(screen, font, message, duration=1.5):
    """Show a temporary popup message"""
    screen_width, screen_height = screen.get_size()
    
    popup_width = 400
    popup_height = 100
    popup_x = screen_width//2 - popup_width//2
    popup_y = screen_height//2 - popup_height//2
    
    # Draw popup with improved styling
    popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    
    # Background with rounded corners
    pygame.draw.rect(popup_surface, (20, 20, 40, 220), (0, 0, popup_width, popup_height), border_radius=15)
    pygame.draw.rect(popup_surface, (80, 80, 150, 255), (0, 0, popup_width, popup_height), 2, border_radius=15)
    
    # Draw message with shadow for better readability
    shadow = font.render(message, True, (0, 0, 0))
    message_render = font.render(message, True, (255, 255, 255))
    
    popup_surface.blit(shadow, 
                      (popup_width//2 - message_render.get_width()//2 + 1, 
                       popup_height//2 - message_render.get_height()//2 + 1))
    popup_surface.blit(message_render, 
                      (popup_width//2 - message_render.get_width()//2, 
                       popup_height//2 - message_render.get_height()//2))
    
    # Show popup
    screen.blit(popup_surface, (popup_x, popup_y))
    pygame.display.flip()
    
    # Wait
    pygame.time.wait(int(duration * 1000))
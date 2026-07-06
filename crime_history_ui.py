"""
Crime History Viewer UI
Displays player's complete crime record with details
"""

import pygame

def draw_crime_history(screen, font, player, game_time):
    """Draw the crime history viewer"""
    config = player.config
    
    # Semi-transparent dark background
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((10, 10, 15))
    screen.blit(overlay, (0, 0))
    
    # Main panel
    panel_width = 900
    panel_height = 650
    panel_x = (config.SCREEN_WIDTH - panel_width) // 2
    panel_y = (config.SCREEN_HEIGHT - panel_height) // 2
    
    # Panel background
    pygame.draw.rect(screen, (30, 30, 40), (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, (200, 50, 50), (panel_x, panel_y, panel_width, panel_height), 3)
    
    # Title with warning symbol
    title_font = pygame.font.SysFont(None, 48)
    title = title_font.render("🚨 CRIME RECORD 🚨", True, (255, 50, 50))
    screen.blit(title, (config.SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 15))
    
    # Current status
    status_y = panel_y + 70
    status_font = pygame.font.SysFont(None, 24)
    
    # Wanted status
    if player.is_wanted:
        wanted_text = status_font.render(f"⚠️ WANTED - Bounty: {player.wanted_level}g", True, (255, 100, 100))
    else:
        wanted_text = status_font.render("✓ Not Wanted", True, (100, 255, 100))
    screen.blit(wanted_text, (panel_x + 20, status_y))
    
    # On the lamb status
    if player.on_the_lamb:
        lamb_text = status_font.render("🚨 ON THE LAMB (Escaped Jail)", True, (255, 50, 50))
        screen.blit(lamb_text, (panel_x + 350, status_y))
    
    # Crime count
    total_crimes = len(player.crimes_committed)
    crime_count_text = status_font.render(f"Total Crimes: {total_crimes}", True, (255, 200, 100))
    screen.blit(crime_count_text, (panel_x + 20, status_y + 30))
    
    # Separator line
    pygame.draw.line(screen, (100, 100, 120), 
                    (panel_x + 10, status_y + 65), 
                    (panel_x + panel_width - 10, status_y + 65), 2)
    
    # Crime list header
    list_y = status_y + 80
    header_font = pygame.font.SysFont(None, 22)
    
    pygame.draw.rect(screen, (40, 40, 50), (panel_x + 10, list_y, panel_width - 20, 30))
    
    header_texts = [
        ("Day", panel_x + 20),
        ("Crime Type", panel_x + 80),
        ("Location", panel_x + 250),
        ("Details", panel_x + 500),
        ("Witnessed", panel_x + 750)
    ]
    
    for text, x_pos in header_texts:
        header = header_font.render(text, True, (200, 200, 200))
        screen.blit(header, (x_pos, list_y + 5))
    
    # Crime records
    if not player.crimes_committed:
        no_crimes_font = pygame.font.SysFont(None, 32)
        no_crimes_text = no_crimes_font.render("No crimes committed yet", True, (150, 150, 150))
        screen.blit(no_crimes_text, (config.SCREEN_WIDTH // 2 - no_crimes_text.get_width() // 2, list_y + 150))
    else:
        # Show most recent crimes first (last 10)
        crimes_to_show = list(reversed(player.crimes_committed))[-10:]
        
        row_y = list_y + 35
        row_height = 45
        crime_font = pygame.font.SysFont(None, 20)
        
        for i, crime in enumerate(reversed(crimes_to_show)):
            # Alternate row colors
            if i % 2 == 0:
                pygame.draw.rect(screen, (25, 25, 35), (panel_x + 10, row_y, panel_width - 20, row_height))
            else:
                pygame.draw.rect(screen, (35, 35, 45), (panel_x + 10, row_y, panel_width - 20, row_height))
            
            # Crime details
            crime_type = crime.get('type', 'unknown')
            location = crime.get('location', 'Unknown')
            day = crime.get('day', 0)
            witnessed = crime.get('witnessed', False)
            
            # Color based on severity
            if crime_type == 'murder':
                type_color = (255, 50, 50)
                icon = "🔪"
            elif crime_type == 'theft':
                type_color = (255, 150, 50)
                icon = "💰"
            elif crime_type == 'attempted_theft':
                type_color = (255, 200, 100)
                icon = "🔓"
            else:
                type_color = (200, 200, 200)
                icon = "⚠️"
            
            # Day
            day_text = crime_font.render(str(day), True, (150, 150, 255))
            screen.blit(day_text, (panel_x + 20, row_y + 5))
            
            # Crime type with icon
            type_text = crime_font.render(f"{icon} {crime_type.replace('_', ' ').title()}", True, type_color)
            screen.blit(type_text, (panel_x + 80, row_y + 5))
            
            # Location (truncate if too long)
            if len(location) > 25:
                location = location[:22] + "..."
            loc_text = crime_font.render(location, True, (200, 200, 200))
            screen.blit(loc_text, (panel_x + 250, row_y + 5))
            
            # Details (victim, item, etc.)
            details = ""
            if 'victim' in crime:
                details = f"Victim: {crime['victim']}"
            elif 'item' in crime:
                details = f"Target: {crime['item']}"
            
            if details:
                if len(details) > 22:
                    details = details[:19] + "..."
                detail_text = crime_font.render(details, True, (180, 180, 180))
                screen.blit(detail_text, (panel_x + 500, row_y + 5))
            
            # Witnessed status
            if witnessed:
                witness_text = crime_font.render("👁️ YES", True, (255, 100, 100))
                if 'witness' in crime and crime['witness']:
                    witness_name = crime['witness']
                    if len(witness_name) > 10:
                        witness_name = witness_name[:8] + "..."
                    witness_detail = crime_font.render(f"({witness_name})", True, (200, 100, 100))
                    screen.blit(witness_text, (panel_x + 750, row_y + 5))
                    screen.blit(witness_detail, (panel_x + 750, row_y + 23))
                else:
                    screen.blit(witness_text, (panel_x + 750, row_y + 12))
            else:
                witness_text = crime_font.render("✓ No", True, (100, 255, 100))
                screen.blit(witness_text, (panel_x + 750, row_y + 12))
            
            row_y += row_height
    
    # Statistics at bottom
    stats_y = panel_y + panel_height - 80
    pygame.draw.line(screen, (100, 100, 120), 
                    (panel_x + 10, stats_y - 10), 
                    (panel_x + panel_width - 10, stats_y - 10), 2)
    
    stats_font = pygame.font.SysFont(None, 22)
    
    # Calculate statistics
    murders = sum(1 for c in player.crimes_committed if c.get('type') == 'murder')
    thefts = sum(1 for c in player.crimes_committed if c.get('type') in ['theft', 'attempted_theft'])
    witnessed_crimes = sum(1 for c in player.crimes_committed if c.get('witnessed', False))
    
    stat_texts = [
        f"Murders: {murders}",
        f"Thefts: {thefts}",
        f"Witnessed: {witnessed_crimes}",
        f"Current Day: {game_time.day_count}"
    ]
    
    stat_x = panel_x + 30
    for stat in stat_texts:
        stat_surf = stats_font.render(stat, True, (200, 200, 200))
        screen.blit(stat_surf, (stat_x, stats_y + 10))
        stat_x += 200
    
    # Instructions
    instr_font = pygame.font.SysFont(None, 20)
    instr_text = instr_font.render("Press H to close  |  Showing 10 most recent crimes", True, (150, 150, 150))
    screen.blit(instr_text, (config.SCREEN_WIDTH // 2 - instr_text.get_width() // 2, panel_y + panel_height - 25))

"""
Save Slot UI - User interface for selecting save slots
"""

import pygame


def get_font(name, size):
    """Get or create a font"""
    return pygame.font.SysFont(name, size)


def format_playtime(seconds):
    """Format playtime in hours and minutes"""
    if seconds is None:
        return "N/A"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def draw_save_slot_selection(screen, config, save_slot_manager, selected_idx, mode="load", mouse_pos=None):
    """
    Draw save slot selection screen
    mode: "load" or "new" - determines UI text and behavior
    """
    screen.fill((20, 25, 35))
    
    # Title
    title_font = get_font(None, 60)
    if mode == "load":
        title_text = "Load Game"
        subtitle_text = "Select a save to load"
    else:
        title_text = "New Game"
        subtitle_text = "Select a save slot"
    
    title = title_font.render(title_text, True, (255, 255, 255))
    screen.blit(title, (config.SCREEN_WIDTH//2 - title.get_width()//2, 40))
    
    subtitle_font = get_font(None, 24)
    subtitle = subtitle_font.render(subtitle_text, True, (180, 180, 180))
    screen.blit(subtitle, (config.SCREEN_WIDTH//2 - subtitle.get_width()//2, 110))
    
    # Get all slot info
    slots = save_slot_manager.get_all_slots()
    
    # Draw save slots
    slot_height = 80
    start_y = 170
    slot_rects = []
    
    for i, slot_info in enumerate(slots):
        is_empty = slot_info['name'] == 'Empty Slot'
        is_selected = i == selected_idx
        
        # Calculate position
        y = start_y + i * (slot_height + 10)
        x = 50
        width = config.SCREEN_WIDTH - 100
        
        # Create rect for mouse detection
        slot_rect = pygame.Rect(x, y, width, slot_height)
        slot_rects.append(slot_rect)
        
        # Check if mouse is hovering
        is_hovered = mouse_pos and slot_rect.collidepoint(mouse_pos)
        
        # Draw slot background
        if is_selected or is_hovered:
            bg_color = (50, 70, 100)
            border_color = (100, 150, 200)
        else:
            bg_color = (35, 40, 50)
            border_color = (60, 70, 80)
        
        pygame.draw.rect(screen, bg_color, slot_rect)
        pygame.draw.rect(screen, border_color, slot_rect, 3)
        
        # Draw slot content
        slot_font = get_font(None, 28)
        detail_font = get_font(None, 20)
        
        if is_empty:
            # Empty slot
            empty_text = slot_font.render(f"Slot {slot_info['slot_number']}: Empty", True, (150, 150, 150))
            screen.blit(empty_text, (x + 20, y + 30))
            if mode == "new":
                hint = detail_font.render("Select to start new game", True, (100, 200, 100))
                screen.blit(hint, (x + width - hint.get_width() - 20, y + 30))
        else:
            # Existing save
            # Character name and level
            name_text = slot_font.render(f"Slot {slot_info['slot_number']}: {slot_info['name']} (Lv {slot_info['level']})", True, (255, 255, 255))
            screen.blit(name_text, (x + 20, y + 15))
            
            # Details (playtime, dubloons, last saved)
            playtime_str = format_playtime(slot_info['playtime'])
            details = f"Playtime: {playtime_str} | Dubloons: {slot_info['dubloons']} | Last Saved: {slot_info['last_saved']}"
            details_text = detail_font.render(details, True, (200, 200, 200))
            screen.blit(details_text, (x + 20, y + 48))
            
            # Warning for overwrite if in new mode
            if mode == "new":
                warning = detail_font.render("⚠ Will overwrite this save!", True, (255, 100, 100))
                screen.blit(warning, (x + width - warning.get_width() - 20, y + 15))
    
    # Instructions at bottom
    instruction_font = get_font(None, 22)
    instructions_y = config.SCREEN_HEIGHT - 60
    
    if mode == "load":
        instructions = "↑/↓: Navigate | ENTER: Load | ESC: Back"
    else:
        instructions = "↑/↓: Navigate | ENTER: Confirm | ESC: Back"
    
    instructions_surf = instruction_font.render(instructions, True, (180, 180, 180))
    screen.blit(instructions_surf, (config.SCREEN_WIDTH//2 - instructions_surf.get_width()//2, instructions_y))
    
    # Optional: Delete key hint for load mode
    if mode == "load" and not slots[selected_idx]['name'] == 'Empty Slot':
        delete_hint = get_font(None, 18).render("DEL: Delete this save", True, (255, 100, 100))
        screen.blit(delete_hint, (config.SCREEN_WIDTH//2 - delete_hint.get_width()//2, instructions_y + 30))
    
    pygame.display.flip()
    return slot_rects


def show_no_saves_message(screen, config):
    """Show 'no saved game data found' message"""
    screen.fill((20, 25, 35))
    
    # Error message
    error_font = get_font(None, 48)
    error_text = error_font.render("No Saved Game Data Found", True, (255, 100, 100))
    screen.blit(error_text, (config.SCREEN_WIDTH//2 - error_text.get_width()//2, config.SCREEN_HEIGHT//2 - 50))
    
    # Instruction
    instruction_font = get_font(None, 28)
    instruction = instruction_font.render("Press any key to return to menu", True, (180, 180, 180))
    screen.blit(instruction, (config.SCREEN_WIDTH//2 - instruction.get_width()//2, config.SCREEN_HEIGHT//2 + 20))
    
    pygame.display.flip()


def save_slot_selection_loop(screen, config, save_slot_manager, mode="load"):
    """
    Main loop for save slot selection
    Returns: selected slot number (1-5) or None if cancelled
    """
    selected = 0
    mouse_pos = None
    slot_rects = []
    
    # Check if there are any saves for load mode
    if mode == "load" and not save_slot_manager.has_any_saves():
        show_no_saves_message(screen, config)
        # Wait for any key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
        return None
    
    while True:
        slot_rects = draw_save_slot_selection(screen, config, save_slot_manager, selected, mode, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                # Update selection based on hover
                for i, rect in enumerate(slot_rects):
                    if rect.collidepoint(mouse_pos):
                        selected = i
                        break
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    for i, rect in enumerate(slot_rects):
                        if rect.collidepoint(mouse_pos):
                            selected = i
                            # Check if valid selection
                            slots = save_slot_manager.get_all_slots()
                            if mode == "load":
                                # Can only load existing saves
                                if slots[selected]['name'] != 'Empty Slot':
                                    return selected + 1  # Return 1-indexed slot number
                            else:  # mode == "new"
                                # Can select any slot
                                return selected + 1
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    selected = (selected - 1) % save_slot_manager.num_slots
                
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected = (selected + 1) % save_slot_manager.num_slots
                
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    slots = save_slot_manager.get_all_slots()
                    if mode == "load":
                        # Can only load existing saves
                        if slots[selected]['name'] != 'Empty Slot':
                            return selected + 1  # Return 1-indexed slot number
                    else:  # mode == "new"
                        # Can select any slot (including empty)
                        return selected + 1
                
                elif event.key == pygame.K_DELETE and mode == "load":
                    # Delete save slot
                    slots = save_slot_manager.get_all_slots()
                    if slots[selected]['name'] != 'Empty Slot':
                        # Confirm deletion
                        confirm_font = get_font(None, 32)
                        confirm_text = confirm_font.render("Delete this save? Y/N", True, (255, 80, 80))
                        confirm_rect = confirm_text.get_rect(center=(config.SCREEN_WIDTH//2, config.SCREEN_HEIGHT//2))
                        
                        # Darken screen
                        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
                        overlay.set_alpha(180)
                        overlay.fill((0, 0, 0))
                        screen.blit(overlay, (0, 0))
                        screen.blit(confirm_text, confirm_rect)
                        pygame.display.flip()
                        
                        confirming = True
                        while confirming:
                            for event2 in pygame.event.get():
                                if event2.type == pygame.QUIT:
                                    return None
                                elif event2.type == pygame.KEYDOWN:
                                    if event2.key == pygame.K_y:
                                        slot = save_slot_manager.get_slot(selected + 1)
                                        slot.delete()
                                        confirming = False
                                        # Redraw the screen
                                        slot_rects = draw_save_slot_selection(screen, config, save_slot_manager, selected, mode, mouse_pos)
                                    elif event2.key == pygame.K_n:
                                        confirming = False

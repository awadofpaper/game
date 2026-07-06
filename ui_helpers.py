"""
UI helper functions module.
Contains functions that require pygame display context (screen, config).
"""
import pygame
import sys
import logging
from game_utils import (
    MENU_OPTIONS, get_font, random_color, random_name
)
from resource_cache import get_cached_surface
from save_slot_ui import save_slot_selection_loop
from save_slot_system import SaveSlotManager
from election_system import CampaignPromise

logger = logging.getLogger(__name__)


def toggle_fullscreen(is_fullscreen, screen, config):
    """Toggle between fullscreen and windowed mode."""
    is_fullscreen = not is_fullscreen
    
    if is_fullscreen:
        # Switch to fullscreen
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        config.SCREEN_WIDTH = screen.get_width()
        config.SCREEN_HEIGHT = screen.get_height()
        logger.info(f"[DISPLAY] Switched to FULLSCREEN mode ({config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT})")
    else:
        # Switch to windowed mode (default resolution 1280x720)
        windowed_width = 1280
        windowed_height = 720
        screen = pygame.display.set_mode((windowed_width, windowed_height), pygame.RESIZABLE)
        config.SCREEN_WIDTH = windowed_width
        config.SCREEN_HEIGHT = windowed_height
        logger.info(f"[DISPLAY] Switched to WINDOWED mode ({config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT})")
    
    pygame.display.set_caption(config.GAME_TITLE)
    return is_fullscreen, screen


def show_help_menu(screen, config):
    """Display comprehensive help screen."""
    # Use default key bindings (key_bindings object isn't available yet)
    attack_binding = "SPACE / LEFT CLICK"
    dodge_binding = "CTRL / RIGHT CLICK"
    
    help_sections = [
        {
            "title": "MOVEMENT & EXPLORATION",
            "content": [
                "Arrow Keys / WASD: Move your character",
                "Shift: Toggle Sprint (uses stamina)",
                "Tab: Open full-screen map",
                "M: Toggle minimap / Mayor Powers (if mayor)",
                "+/-: Zoom map in/out",
                "0: Reset map zoom",
                "Explore towns, wilderness, and dungeons",
                "Watch your stamina - it regenerates when still",
                "Fast travel available from properties you own"
            ]
        },
        {
            "title": "HOTBAR SYSTEM (NEW!)",
            "content": [
                "1-9: Use items/spells in hotbar slots",
                "B: Lock/unlock hotbar (prevents accidents)",
                "Left-click drag: Reorder hotbar slots",
                "Right-click slot: Remove item from hotbar",
                "Mouse hover: View item details & cooldown",
                "Auto-assigns potions and spells on first load",
                "Cooldowns prevent spam (shown as dark overlay)",
                "Saves with your game - persistent setup"
            ]
        },
        {
            "title": "COMBAT & MAGIC",
            "content": [
                f"{attack_binding}: Attack nearby enemies",
                f"{dodge_binding}: Dodge roll",
                "Hotbar (1-9): Quick-use items/spells",
                "F: Cast selected spell (projectile)",
                "Combat skills improve with use",
                "Different weapons have ranges/speeds",
                "Watch HP, stamina, and mana",
                "Critical hits deal extra damage",
                "Dodge chance based on dexterity"
            ]
        },
        {
            "title": "DUNGEONS & BOSSES",
            "content": [
                "F: Enter dungeon (when near entrance)",
                "Boss loot preview shown before entering",
                "Select difficulty modifiers for better rewards",
                "Speedrun timer tracks clear time",
                "Discover secrets for bonus loot",
                "Traps deal damage - watch for warnings",
                "Boss fights drop set items & legendaries",
                "Dungeons have unique themes & hazards",
                "Death in dungeon forces reload",
                "Higher difficulty = better drop rates"
            ]
        },
        {
            "title": "INVENTORY & EQUIPMENT",
            "content": [
                "I: Open inventory",
                "E: Character sheet (NEW! - view equipment & total stats)",
                "C: Stats menu (allocate skill points)",
                "O: Equipment (legacy)",
                "R: Sort inventory / Trade routes UI",
                "E/Q: Equip items (in inventory)",
                "[: Toggle auto-loot ON/OFF",
                "] (bracket): Cycle auto-loot rarity filter",
                "Hover items for detailed tooltips",
                "Equipment degrades with use (if enabled)",
                "Repair items with materials or at shops",
                "Equipment comparison shows stat changes",
                "Character sheet shows base + bonus stats"
            ]
        },
        {
            "title": "GATHERING & CRAFTING",
            "content": [
                "Approach resources (trees, rocks, plants)",
                "Press E to gather (requires appropriate tool)",
                "NPCs react if you gather their resource!",
                "Dialogue affected by faction & reputation",
                "C: Open cooking menu (at fire or in town)",
                "Ctrl+B: Place cooking fire (costs 2 sticks)",
                "K: Skills menu",
                "Craft tools, weapons, armor, and consumables",
                "Cook food for buffs and healing",
                "Higher skill = better yields & quality",
                "Resources respawn over time",
                "Weather affects gathering success rates"
            ]
        },
        {
            "title": "QUESTS & NPCs",
            "content": [
                "T: Talk to NPCs (when near them)",
                "L: Open quest log",
                "Q: Toggle quest tracker",
                "H: Dialogue history",
                "Complete quests for XP, gold, and reputation",
                "Build relationships with NPCs",
                "Quest objectives tracked on minimap",
                "Some quests are time-sensitive"
            ]
        },
        {
            "title": "SHOPS & ECONOMY",
            "content": [
                "B: Open shop (when near merchant)",
                "I: Stock market & investments",
                "Buy and sell items at varying prices",
                "Prices vary by merchant type & reputation",
                "Market system for commodities trading",
                "Invest in shops, earn dividends",
                "Town treasuries fund public services",
                "Banks offer storage and insurance",
                "Property ownership available",
                "Trade routes generate passive income"
            ]
        },
        {
            "title": "SKILLS & PROGRESSION",
            "content": [
                "K: Open skills menu",
                "Gain XP by fighting, gathering, crafting",
                "Level up to gain skill points",
                "Allocate points to 5 core stats:",
                "  Strength, Stamina, Stealth, Endurance, Magic",
                "Individual skills level through use",
                "Special abilities unlock at milestones",
                "Skill XP shown in real-time"
            ]
        },
        {
            "title": "POLITICS & GOVERNANCE",
            "content": [
                "P: Campaign promises (during elections)",
                "V: Bribe voter (during elections)",
                "Run for mayor in town elections",
                "Implement policies as mayor:",
                "  - Curfew (17:00-02:00 nightly)",
                "  - Town lockdown & entry fees",
                "  - Weapon restrictions",
                "  - Tax rates & tariffs",
                "Mayor can abscond with treasury!",
                "Track absconded mayors for rewards"
            ]
        },
        {
            "title": "CRIME & LAW",
            "content": [
                "J: Crime history viewer",
                "Stealth system - avoid guard detection",
                "Wanted status affects town entry",
                "Guards pursue wanted criminals",
                "WARNING: 20-second timer when guards alerted!",
                "Get 10+ tiles away to escape pursuit",
                "Jail time for serious crimes",
                "Escape attempts possible but risky",
                "Exile from towns for severe crimes",
                "Bounties on your head incentivize capture"
            ]
        },
        {
            "title": "ADVANCED SYSTEMS",
            "content": [
                "R: Trade routes UI",
                "P: NPC professions menu",
                "X: Pickup/bury bodies",
                "Ctrl+B: Place cooking fire (costs 2 sticks)",
                "Y: Accept tracking quests",
                "NPC families and relationships",
                "Dynamic economy & market prices",
                "Weather affects NPC behavior",
                "Insurance policies available",
                "Multiple property ownership"
            ]
        },
        {
            "title": "TIME & WEATHER",
            "content": [
                "Day/night cycle affects gameplay",
                "Weather changes dynamically",
                "Rain/snow affects resource gathering",
                "NPCs have daily schedules",
                "Curfews enforced at night",
                "Visibility reduced in darkness",
                "Sleep to restore health & pass time",
                "Seasons affect resource availability"
            ]
        },
        {
            "title": "ACHIEVEMENTS & PETS",
            "content": [
                "A: View achievements",
                "Unlock achievements by playing",
                "Earn pet companions as rewards",
                "G: Open pet menu",
                "U: Cycle/toggle pets",
                "Pets follow and assist you",
                "Achievements track progress",
                "Hidden achievements discoverable"
            ]
        },
        {
            "title": "COSMETICS & LOOT BOXES (NEW!)",
            "content": [
                "V: Open cosmetic equip menu",
                "Visit MaXxS Silicon Dioxide Shop in ANY town",
                "Purchase mystery loot boxes for 3000 dubloons",
                "Watch exciting 5-8 second animation!",
                "Unlock cosmetics: colors, patterns, effects",
                "Rarity tiers from Common to LITERALLY IMPOSSIBLE",
                "Cosmetics are purely visual (no stats)",
                "Duplicates refund 30 dubloons (1% back!)",
                "Equip cosmetics for player/pet/armor/weapon",
                "Permanent unlocks saved with your game",
                "Max has... unique dialogue based on your actions"
            ]
        },
        {
            "title": "SAVING & SETTINGS",
            "content": [
                "ESC / P: Pause menu",
                "Save game from pause menu",
                "Multiple save slots available",
                "Auto-save when entering towns",
                "JSON-based saves (secure)",
                "F9: Accessibility options",
                "F10: Control remapping",
                "F11: Graphics settings",
                "Saves include hotbar configuration"
            ]
        },
        {
            "title": "TIPS & TRICKS",
            "content": [
                "Lock hotbar (B) before combat",
                "Assign potions to slots 1-2",
                "Reputation affects shop prices",
                "Stealth at night to avoid curfew fines",
                "Insurance protects expensive items",
                "NPCs remember your actions",
                "Weather patterns are predictable",
                "Market prices fluctuate - buy low!",
                "Property generates passive income",
                "Elections happen every 28 days"
            ]
        }
    ]
    
    current_page = 0
    max_page = len(help_sections) - 1
    scroll_offset = 0
    max_scroll = 0
    
    font_title = get_font(None, 48)
    font_section = get_font(None, 36)
    font_content = get_font(None, 28)
    font_nav = get_font(None, 24)
    
    viewing = True
    while viewing:
        screen.fill((20, 20, 30))
        
        # Title
        title = font_title.render("GAME HELP", True, (255, 255, 100))
        screen.blit(title, (config.SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        # Current section
        section = help_sections[current_page]
        section_title = font_section.render(section["title"], True, (100, 200, 255))
        screen.blit(section_title, (config.SCREEN_WIDTH//2 - section_title.get_width()//2, 100))
        
        # Content
        y = 160 - scroll_offset
        line_height = 35
        visible_area_top = 160
        visible_area_bottom = config.SCREEN_HEIGHT - 120
        
        for line in section["content"]:
            if y >= visible_area_top - line_height and y <= visible_area_bottom:
                text_surf = font_content.render(line, True, (220, 220, 220))
                screen.blit(text_surf, (100, y))
            y += line_height
        
        # Calculate max scroll
        total_content_height = len(section["content"]) * line_height
        visible_height = visible_area_bottom - visible_area_top
        max_scroll = max(0, total_content_height - visible_height)
        
        # Page indicator
        page_text = font_nav.render(f"Page {current_page + 1}/{max_page + 1}", True, (150, 150, 150))
        screen.blit(page_text, (config.SCREEN_WIDTH//2 - page_text.get_width()//2, config.SCREEN_HEIGHT - 90))
        
        # Navigation instructions
        nav_text = font_nav.render("Left/Right: Change Page  |  Up/Down: Scroll  |  ESC: Back", True, (180, 180, 180))
        screen.blit(nav_text, (config.SCREEN_WIDTH//2 - nav_text.get_width()//2, config.SCREEN_HEIGHT - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    viewing = False
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    current_page = (current_page - 1) % (max_page + 1)
                    scroll_offset = 0
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    current_page = (current_page + 1) % (max_page + 1)
                    scroll_offset = 0
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    scroll_offset = min(max_scroll, scroll_offset + 30)


def draw_menu(screen, config, selected_idx, mouse_pos=None):
    """Draw the main menu and return menu item rectangles."""
    screen.fill((20, 20, 30))
    font = get_font(None, 60)
    title = font.render(config.GAME_TITLE, True, (255, 255, 255))
    screen.blit(title, (config.SCREEN_WIDTH//2 - title.get_width()//2, 80))
    menu_font = get_font(None, 40)
    
    menu_rects = []  # Store menu item rectangles for mouse detection
    for i, option in enumerate(MENU_OPTIONS):
        text = menu_font.render(option, True, (255, 255, 255))
        text_x = config.SCREEN_WIDTH//2 - text.get_width()//2
        text_y = 200 + i*60
        text_rect = pygame.Rect(text_x, text_y, text.get_width(), text.get_height())
        menu_rects.append(text_rect)
        
        # Check if mouse is hovering
        is_hovered = mouse_pos and text_rect.collidepoint(mouse_pos)
        
        # Color: yellow if selected or hovered, white otherwise
        if i == selected_idx or is_hovered:
            color = (255, 255, 0)
        else:
            color = (200, 200, 200)
        
        text = menu_font.render(option, True, color)
        screen.blit(text, (text_x, text_y))
    
    pygame.display.flip()
    return menu_rects


def main_menu(screen, config, is_fullscreen=True, test_mode=False):
    """Show main menu and return selected action, save slot, and fullscreen state.
    
    Args:
        screen: Pygame screen surface
        config: Game config object
        is_fullscreen: Current fullscreen state
        test_mode: If True, bypass UI and return default action for automated testing/RL
    """
    # Automated mode for RL/testing - return default "new game" action
    if test_mode:
        save_slot_manager = SaveSlotManager(num_slots=5)
        selected_slot = save_slot_manager.get_slot(1)
        if selected_slot.exists():
            selected_slot.delete()
        return ("new", selected_slot, is_fullscreen)
    
    selected = 0
    menu_rects = []
    mouse_pos = None
    
    # Create save slot manager
    save_slot_manager = SaveSlotManager(num_slots=5)
    
    while True:
        menu_rects = draw_menu(screen, config, selected, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                # Update selection based on hover
                for i, rect in enumerate(menu_rects):
                    if rect.collidepoint(mouse_pos):
                        selected = i
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(mouse_pos):
                            selected = i
                            # Trigger the selection
                            fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
                            pygame.event.post(fake_event)
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Toggle fullscreen
                    is_fullscreen, screen = toggle_fullscreen(is_fullscreen, screen, config)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    selected = (selected - 1) % len(MENU_OPTIONS)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected = (selected + 1) % len(MENU_OPTIONS)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if MENU_OPTIONS[selected] == "New Game":
                        # Show save slot selection
                        slot_number = save_slot_selection_loop(screen, config, save_slot_manager, mode="new")
                        if slot_number is not None:
                            # Select the slot
                            selected_slot = save_slot_manager.get_slot(slot_number)
                            
                            # If save exists, show confirmation dialog
                            if selected_slot.exists():
                                confirm_font = get_font(None, 36)
                                warning_font = get_font(None, 28)
                                confirm_text = confirm_font.render("Starting a new game will overwrite this save!", True, (255, 80, 80))
                                question_text = warning_font.render("Would you like to continue? (Y/N)", True, (255, 255, 255))
                                
                                screen.fill((0, 0, 0))
                                screen.blit(confirm_text, (config.SCREEN_WIDTH//2 - confirm_text.get_width()//2, config.SCREEN_HEIGHT//2 - 40))
                                screen.blit(question_text, (config.SCREEN_WIDTH//2 - question_text.get_width()//2, config.SCREEN_HEIGHT//2 + 20))
                                pygame.display.flip()
                                
                                confirming = True
                                while confirming:
                                    for event2 in pygame.event.get():
                                        if event2.type == pygame.QUIT:
                                            pygame.quit(); sys.exit()
                                        elif event2.type == pygame.KEYDOWN:
                                            if event2.key == pygame.K_y:
                                                selected_slot.delete()
                                                return ("new", selected_slot, is_fullscreen)
                                            elif event2.key == pygame.K_n:
                                                confirming = False
                                                break
                            else:
                                # Slot is empty, proceed directly
                                return ("new", selected_slot, is_fullscreen)
                    elif MENU_OPTIONS[selected] == "Load Game":
                        # Show save slot selection
                        slot_number = save_slot_selection_loop(screen, config, save_slot_manager, mode="load")
                        if slot_number is not None:
                            selected_slot = save_slot_manager.get_slot(slot_number)
                            return ("load", selected_slot, is_fullscreen)
                    elif MENU_OPTIONS[selected] == "Help":
                        show_help_menu(screen, config)
                    elif MENU_OPTIONS[selected] == "Delete Save":
                        # Show save slot selection for deletion
                        slot_number = save_slot_selection_loop(screen, config, save_slot_manager, mode="load")
                        if slot_number is not None:
                            confirm_font = get_font(None, 36)
                            confirm_text = confirm_font.render("Delete this save? Y/N", True, (255, 80, 80))
                            screen.blit(confirm_text, (config.SCREEN_WIDTH//2 - confirm_text.get_width()//2, 480))
                            pygame.display.flip()
                            confirming = True
                            while confirming:
                                for event2 in pygame.event.get():
                                    if event2.type == pygame.QUIT:
                                        pygame.quit(); sys.exit()
                                    elif event2.type == pygame.KEYDOWN:
                                        if event2.key == pygame.K_y:
                                            selected_slot = save_slot_manager.get_slot(slot_number)
                                            selected_slot.delete()
                                            confirming = False
                                        elif event2.key == pygame.K_n:
                                            confirming = False
                    elif MENU_OPTIONS[selected] == "Exit":
                        pygame.quit()
                        sys.exit()


def show_trait_comparison(screen, config, all_races):
    """
    Show a comparison view of all racial traits side-by-side
    """
    font = get_font(None, 28)
    small_font = get_font(None, 20)
    tiny_font = get_font(None, 16)
    
    viewing = True
    scroll_offset = 0
    max_scroll = 0
    
    while viewing:
        screen.fill((10, 10, 20))
        
        # Title
        title = font.render("Racial Traits Comparison", True, (255, 215, 0))
        screen.blit(title, (config.SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        subtitle = tiny_font.render("Compare all racial traits to make an informed decision", True, (180, 180, 200))
        screen.blit(subtitle, (config.SCREEN_WIDTH//2 - subtitle.get_width()//2, 55))
        
        # Create table layout
        content_y = 100 - scroll_offset
        col_width = config.SCREEN_WIDTH // 3
        row_height = 200
        
        for i, race in enumerate(all_races):
            row = i // 3
            col = i % 3
            x = col * col_width + 10
            y = content_y + row * (row_height + 20)
            
            # Skip if off-screen
            if y + row_height < 90 or y > config.SCREEN_HEIGHT - 60:
                continue
            
            # Panel background
            panel_width = col_width - 20
            panel_height = row_height
            pygame.draw.rect(screen, (30, 30, 50), (x, y, panel_width, panel_height))
            pygame.draw.rect(screen, (100, 100, 150), (x, y, panel_width, panel_height), 2)
            
            # Race icon/name
            race_font = get_font(None, 24)
            race_name = race_font.render(race.name, True, (255, 255, 100))
            screen.blit(race_name, (x + 10, y + 10))
            
            # Divider line
            pygame.draw.line(screen, (80, 80, 120), (x + 10, y + 40), (x + panel_width - 10, y + 40), 1)
            
            # Traits
            trait_y = y + 50
            for trait in race.traits:
                # Trait name
                trait_name_surf = tiny_font.render(f"• {trait.name}", True, (150, 255, 150))
                screen.blit(trait_name_surf, (x + 15, trait_y))
                trait_y += 20
                
                # Trait description (wrapped, max 2 lines)
                desc_words = trait.description.split()
                line = ""
                lines_drawn = 0
                max_lines = 2
                
                for word in desc_words:
                    test_line = line + word + " "
                    if tiny_font.size(test_line)[0] < panel_width - 40:
                        line = test_line
                    else:
                        if line and lines_drawn < max_lines:
                            desc_surf = tiny_font.render(line.strip(), True, (200, 200, 220))
                            screen.blit(desc_surf, (x + 20, trait_y))
                            trait_y += 17
                            lines_drawn += 1
                        line = word + " "
                
                if line and lines_drawn < max_lines:
                    # Truncate if too long
                    if len(line) > 45:
                        line = line[:42] + "..."
                    desc_surf = tiny_font.render(line.strip(), True, (200, 200, 220))
                    screen.blit(desc_surf, (x + 20, trait_y))
                    trait_y += 22
                else:
                    trait_y += 5
            
            # Update max scroll if needed
            if y + panel_height > max_scroll:
                max_scroll = y + panel_height - 90
        
        # Draw top/bottom fade overlays if scrolled
        if scroll_offset > 0:
            fade_top = pygame.Surface((config.SCREEN_WIDTH, 30))
            fade_top.set_alpha(150)
            fade_top.fill((10, 10, 20))
            screen.blit(fade_top, (0, 90))
        
        if scroll_offset < max_scroll - config.SCREEN_HEIGHT + 150:
            fade_bottom = pygame.Surface((config.SCREEN_WIDTH, 40))
            fade_bottom.set_alpha(150)
            fade_bottom.fill((10, 10, 20))
            screen.blit(fade_bottom, (0, config.SCREEN_HEIGHT - 100))
        
        # Instructions at bottom
        instr_bg = pygame.Surface((config.SCREEN_WIDTH, 60))
        instr_bg.fill((20, 20, 30))
        screen.blit(instr_bg, (0, config.SCREEN_HEIGHT - 60))
        
        instr = small_font.render("Up/Down: Scroll | ESC/TAB: Back", True, (200, 200, 200))
        screen.blit(instr, (config.SCREEN_WIDTH//2 - instr.get_width()//2, config.SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_TAB]:
                    viewing = False
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    scroll_offset = min(max_scroll, scroll_offset + 30)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(max_scroll, scroll_offset - event.y * 30))


def character_creation(screen, config, is_fullscreen=True, test_mode=False, auto_name=None, auto_color=None, auto_skills=None, auto_race=None, auto_skin_tone=None):
    """Character creation with input validation. Returns (name, color, skills, race, skin_tone, is_fullscreen).
    
    Args:
        screen: Pygame screen surface
        config: Game config object
        is_fullscreen: Current fullscreen state
        test_mode: If True, bypass UI and use auto values or generate random
        auto_name: Optional name for test mode (random if None)
        auto_color: Optional color override (defaults to skin_tone if None)
        auto_skills: Optional skills dict for test mode (random if None)
        auto_race: Optional race ID for test mode (random if None)
        auto_skin_tone: Optional skin tone tuple for test mode (random if None)
    """
    from utils import sanitize_name
    from race_system import get_all_races, get_race_by_id
    
    # Automated mode for RL/testing
    if test_mode:
        import random
        
        # Race selection
        if auto_race:
            selected_race = get_race_by_id(auto_race)
        else:
            all_races = get_all_races()
            selected_race = random.choice(all_races)
        
        # Skin tone selection
        if auto_skin_tone:
            skin_tone = auto_skin_tone
        else:
            skin_tone = random.choice(selected_race.skin_tones)
        
        name = auto_name or random_name()
        
        # Color is now the same as skin tone (auto_color kept for backward compatibility)
        color = auto_color if auto_color else skin_tone
        
        if auto_skills:
            skills = auto_skills
        else:
            skill_names = ["Strength", "Defense", "Magic", "Stamina", "Speed", "Agility", "Willpower", "Luck", "Intelligence", "Talking"]
            allocations = [0] * len(skill_names)
            for _ in range(20):
                allocations[random.randint(0, len(skill_names)-1)] += 1
            skills = dict(zip(skill_names, allocations))
        
        return name, color, skills, selected_race, skin_tone, is_fullscreen
    
    # Race selection
    from race_system import get_all_races
    all_races = get_all_races()
    race_idx = 0
    selected_race = all_races[race_idx]
    selecting_race = True
    font = get_font(None, 36)
    small_font = get_font(None, 18)
    tiny_font = get_font(None, 16)
    
    while selecting_race:
        screen.fill((15, 15, 25))
        
        # Title
        title = font.render("Choose Your Race", True, (255, 255, 255))
        screen.blit(title, (config.SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        # Split screen: Left side = race boxes, Right side = detailed info
        # Left panel with race boxes
        left_panel_width = config.SCREEN_WIDTH * 2 // 3
        races_per_row = 3
        box_width = 340
        box_height = 140
        padding = 15
        start_x = 30
        start_y = 80
        
        for i, race in enumerate(all_races):
            row = i // races_per_row
            col = i % races_per_row
            x = start_x + col * (box_width + padding)
            y = start_y + row * (box_height + padding)
            
            # Highlight selected race
            is_selected = (i == race_idx)
            color = (80, 80, 180) if is_selected else (40, 40, 60)
            border_color = (180, 180, 255) if is_selected else (80, 80, 100)
            border_width = 3 if is_selected else 2
            
            # Box background
            pygame.draw.rect(screen, color, (x, y, box_width, box_height))
            pygame.draw.rect(screen, border_color, (x, y, box_width, box_height), border_width)
            
            # Race name (larger font)
            race_font = get_font(None, 28)
            race_name = race_font.render(race.name, True, (255, 255, 100) if is_selected else (255, 255, 255))
            screen.blit(race_name, (x + 10, y + 8))
            
            # Brief description (1 line)
            desc_short = race.description.split('.')[0][:50] + "..."
            desc_surf = tiny_font.render(desc_short, True, (200, 200, 200))
            screen.blit(desc_surf, (x + 10, y + 40))
            
            # Key stats - show top 2 positive and top 1 negative
            y_stat = y + 65
            positive_stats = [(k, v) for k, v in race.stat_modifiers.items() if v > 0]
            negative_stats = [(k, v) for k, v in race.stat_modifiers.items() if v < 0]
            positive_stats.sort(key=lambda item: item[1], reverse=True)
            negative_stats.sort(key=lambda item: item[1])
            
            # Show positive stats
            for stat, val in positive_stats[:2]:
                stat_name = stat.replace('_', ' ').title()
                if len(stat_name) > 12:
                    stat_name = stat_name[:10] + "."
                stat_surf = tiny_font.render(f"✓ +{val} {stat_name}", True, (120, 255, 120))
                screen.blit(stat_surf, (x + 10, y_stat))
                y_stat += 18
            
            # Show negative stat (if any)
            if negative_stats:
                stat, val = negative_stats[0]
                stat_name = stat.replace('_', ' ').title()
                if len(stat_name) > 12:
                    stat_name = stat_name[:10] + "."
                stat_surf = tiny_font.render(f"✗ {val} {stat_name}", True, (255, 140, 140))
                screen.blit(stat_surf, (x + 10, y_stat))
            
            # Traits indicator at bottom
            trait_y = y + box_height - 25
            trait_surf = tiny_font.render(f"🛡 {len(race.traits)} Traits", True, (255, 200, 100))
            screen.blit(trait_surf, (x + 10, trait_y))
        
        # Right panel - Detailed info for selected race
        detail_x = left_panel_width + 20
        detail_y = 80
        detail_width = config.SCREEN_WIDTH - detail_x - 20
        detail_height = config.SCREEN_HEIGHT - 160
        
        # Detail panel background with gradient effect
        pygame.draw.rect(screen, (25, 25, 45), (detail_x, detail_y, detail_width, detail_height))
        pygame.draw.rect(screen, (120, 120, 180), (detail_x, detail_y, detail_width, detail_height), 3)
        
        # Selected race details
        detail_font = get_font(None, 26)
        info_y = detail_y + 15
        
        # Race name with emphasis
        name_surf = detail_font.render(selected_race.name, True, (255, 255, 100))
        screen.blit(name_surf, (detail_x + 15, info_y))
        info_y += 40
        
        # Full description (wrapped)
        desc_words = selected_race.description.split()
        line = ""
        for word in desc_words:
            test_line = line + word + " "
            if tiny_font.size(test_line)[0] < detail_width - 30:
                line = test_line
            else:
                if line:
                    desc_surf = tiny_font.render(line, True, (230, 230, 230))
                    screen.blit(desc_surf, (detail_x + 15, info_y))
                    info_y += 20
                line = word + " "
        if line:
            desc_surf = tiny_font.render(line, True, (230, 230, 230))
            screen.blit(desc_surf, (detail_x + 15, info_y))
            info_y += 30
        
        # Stat modifiers section with enhanced visuals
        stat_box_y = info_y
        stat_box_height = 0
        
        # Count non-zero stat modifiers
        non_zero_stats = [(stat, value) for stat, value in selected_race.stat_modifiers.items() if value != 0]
        
        if non_zero_stats:
            stat_box_height = 35 + len(non_zero_stats) * 22 + 10
            # Draw box for stats
            pygame.draw.rect(screen, (40, 60, 90), (detail_x + 10, stat_box_y, detail_width - 20, stat_box_height))
            pygame.draw.rect(screen, (100, 150, 200), (detail_x + 10, stat_box_y, detail_width - 20, stat_box_height), 2)
            
            # Header
            stat_header = small_font.render("📊 Racial Stat Modifiers", True, (150, 255, 200))
            screen.blit(stat_header, (detail_x + 20, stat_box_y + 8))
            info_y = stat_box_y + 35
            
            # Display stats in two columns if many stats
            col1_stats = []
            col2_stats = []
            for i, (stat, value) in enumerate(sorted(non_zero_stats, key=lambda x: -x[1])):
                if i < (len(non_zero_stats) + 1) // 2:
                    col1_stats.append((stat, value))
                else:
                    col2_stats.append((stat, value))
            
            # Column 1
            col1_y = info_y
            for stat, value in col1_stats:
                stat_name = stat.replace('_', ' ').title()
                sign = "+" if value > 0 else ""
                color = (100, 255, 100) if value > 0 else (255, 120, 120)
                stat_text = tiny_font.render(f"{sign}{value:2d}  {stat_name}", True, color)
                screen.blit(stat_text, (detail_x + 25, col1_y))
                col1_y += 22
            
            # Column 2 (if needed)
            if col2_stats:
                col2_y = info_y
                col2_x = detail_x + detail_width // 2 + 10
                for stat, value in col2_stats:
                    stat_name = stat.replace('_', ' ').title()
                    sign = "+" if value > 0 else ""
                    color = (100, 255, 100) if value > 0 else (255, 120, 120)
                    stat_text = tiny_font.render(f"{sign}{value:2d}  {stat_name}", True, color)
                    screen.blit(stat_text, (col2_x, col2_y))
                    col2_y += 22
            
            info_y = stat_box_y + stat_box_height + 20
        
        # Note about starting stats
        note_font = get_font(None, 15)
        note_text = "You'll also receive 20 stat points to allocate at character creation"
        note_surf = note_font.render(note_text, True, (180, 180, 255))
        screen.blit(note_surf, (detail_x + 15, info_y))
        info_y += 30
        
        # Racial traits header
        trait_header = small_font.render("🛡️ Racial Traits", True, (255, 200, 100))
        screen.blit(trait_header, (detail_x + 15, info_y))
        info_y += 25
        
        # All traits with full descriptions
        for trait in selected_race.traits:
            # Trait name
            trait_name = tiny_font.render(f"• {trait.name}", True, (255, 255, 150))
            screen.blit(trait_name, (detail_x + 15, info_y))
            info_y += 20
            
            # Trait description (wrapped)
            desc_words = trait.description.split()
            line = ""
            for word in desc_words:
                test_line = line + word + " "
                if tiny_font.size(test_line)[0] < detail_width - 50:
                    line = test_line
                else:
                    if line:
                        desc_surf = tiny_font.render(line, True, (200, 200, 255))
                        screen.blit(desc_surf, (detail_x + 25, info_y))
                        info_y += 18
                    line = word + " "
            if line:
                desc_surf = tiny_font.render(line, True, (200, 200, 255))
                screen.blit(desc_surf, (detail_x + 25, info_y))
                info_y += 22
        
        # Instructions at bottom
        instr_bg = pygame.Surface((config.SCREEN_WIDTH, 50))
        instr_bg.fill((20, 20, 30))
        screen.blit(instr_bg, (0, config.SCREEN_HEIGHT - 50))
        
        instr = small_font.render("Arrow Keys: Navigate | Enter: Select | TAB: Compare Traits", True, (200, 200, 200))
        screen.blit(instr, (config.SCREEN_WIDTH//2 - instr.get_width()//2, config.SCREEN_HEIGHT - 35))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Toggle fullscreen
                    is_fullscreen, screen = toggle_fullscreen(is_fullscreen, screen, config)
                elif event.key == pygame.K_TAB:
                    # Show trait comparison view
                    show_trait_comparison(screen, config, all_races)
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    race_idx = (race_idx - 1) % len(all_races)
                    selected_race = all_races[race_idx]
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    race_idx = (race_idx + 1) % len(all_races)
                    selected_race = all_races[race_idx]
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    race_idx = (race_idx - 3) % len(all_races)
                    selected_race = all_races[race_idx]
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    race_idx = (race_idx + 3) % len(all_races)
                    selected_race = all_races[race_idx]
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    selecting_race = False
    
    # Skin tone selection
    skin_idx = 0
    skin_tone = selected_race.skin_tones[skin_idx]
    selecting_skin = True
    
    while selecting_skin:
        screen.fill((15, 15, 25))
        
        # Title
        title = font.render(f"Choose {selected_race.name} Skin Tone", True, (255, 255, 255))
        screen.blit(title, (config.SCREEN_WIDTH//2 - title.get_width()//2, 60))
        
        # Display skin tones in a row
        total_width = len(selected_race.skin_tones) * 100 + (len(selected_race.skin_tones) - 1) * 20
        start_x = (config.SCREEN_WIDTH - total_width) // 2
        y_pos = 200
        
        for i, tone in enumerate(selected_race.skin_tones):
            x = start_x + i * 120
            
            # Draw skin tone circle
            if i == skin_idx:
                # Selected - larger with border
                pygame.draw.circle(screen, (255, 255, 255), (x + 50, y_pos), 52, 3)
                pygame.draw.circle(screen, tone, (x + 50, y_pos), 50)
            else:
                pygame.draw.circle(screen, tone, (x + 50, y_pos), 40)
            
            # Skin tone name
            name_surf = small_font.render(selected_race.skin_tone_names[i], True, (255, 255, 255) if i == skin_idx else (180, 180, 180))
            screen.blit(name_surf, (x + 50 - name_surf.get_width()//2, y_pos + 70))
        
        # Preview character with selected skin tone
        preview_y = 380
        preview_label = font.render("Preview", True, (200, 200, 200))
        screen.blit(preview_label, (config.SCREEN_WIDTH//2 - preview_label.get_width()//2, preview_y - 40))
        pygame.draw.circle(screen, skin_tone, (config.SCREEN_WIDTH//2, preview_y), 60)
        pygame.draw.circle(screen, (255, 255, 255), (config.SCREEN_WIDTH//2, preview_y), 62, 2)
        
        # Instructions
        instr = small_font.render("Left/Right: Change | Enter: Confirm", True, (180, 180, 180))
        screen.blit(instr, (config.SCREEN_WIDTH//2 - instr.get_width()//2, config.SCREEN_HEIGHT - 80))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Toggle fullscreen
                    is_fullscreen, screen = toggle_fullscreen(is_fullscreen, screen, config)
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    skin_idx = (skin_idx - 1) % len(selected_race.skin_tones)
                    skin_tone = selected_race.skin_tones[skin_idx]
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    skin_idx = (skin_idx + 1) % len(selected_race.skin_tones)
                    skin_tone = selected_race.skin_tones[skin_idx]
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    selecting_skin = False
    
    # Name input
    name = ""
    font = get_font(None, 40)
    inputting_name = True
    error_message = ""
    
    while inputting_name:
        screen.fill((25,25,35))
        text = font.render("Enter your character's name:", True, (255,255,255))
        screen.blit(text, (config.SCREEN_WIDTH//2 - text.get_width()//2, 80))
        
        # Show current name
        name_surf = font.render(name+"_", True, (255,255,0))
        screen.blit(name_surf, (config.SCREEN_WIDTH//2 - name_surf.get_width()//2, 160))
        
        # Show error message if any
        if error_message:
            error_font = get_font(None, 24)
            error_surf = error_font.render(error_message, True, (255, 100, 100))
            screen.blit(error_surf, (config.SCREEN_WIDTH//2 - error_surf.get_width()//2, 200))
        
        instr = font.render("Type, Enter to confirm, R=random", True, (180,180,180))
        screen.blit(instr, (config.SCREEN_WIDTH//2-180, 240))
        
        # Show character restrictions
        small_font = get_font(None, 18)
        restriction_text = small_font.render("Letters, numbers, spaces, hyphens only (max 16 chars)", True, (150, 150, 150))
        screen.blit(restriction_text, (config.SCREEN_WIDTH//2 - restriction_text.get_width()//2, 280))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Toggle fullscreen
                    is_fullscreen, screen = toggle_fullscreen(is_fullscreen, screen, config)
                elif event.key == pygame.K_RETURN:
                    # Validate name before accepting
                    if not name.strip():
                        error_message = "Name cannot be empty!"
                    elif len(name.strip()) < 2:
                        error_message = "Name must be at least 2 characters!"
                    else:
                        # Sanitize and check if it changed
                        sanitized = sanitize_name(name, max_length=16)
                        if sanitized != name:
                            error_message = "Name contains invalid characters!"
                            name = sanitized  # Show sanitized version
                        else:
                            name = sanitized
                            inputting_name = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                    error_message = ""  # Clear error on edit
                elif event.key == pygame.K_r:
                    name = random_name()
                    error_message = ""
                elif event.unicode.isprintable() and len(name) < 16:
                    # Only allow safe characters
                    if event.unicode.isalnum() or event.unicode in ' -\'_':
                        name += event.unicode
                        error_message = ""

    # Use skin tone as player color (no separate color selection)
    color = skin_tone

    # Stat allocation (using actual player stat names)
    skills = ["Strength", "Defense", "Magic", "Stamina", "Speed", "Agility", "Willpower", "Luck", "Intelligence", "Talking"]
    skill_points = 6
    allocations = [0]*len(skills)
    skill_idx = 0
    allocating = True
    while allocating:
        screen.fill((25,25,35))
        text = font.render("Allocate your 6 starting stat points", True, (255,255,255))
        screen.blit(text, (config.SCREEN_WIDTH//2 - text.get_width()//2, 60))
        
        # Draw stats in two columns
        for i, skill in enumerate(skills):
            color2 = (255,255,0) if i==skill_idx else (255,255,255)
            if i < 5:
                x_pos = config.SCREEN_WIDTH//2 - 250
                y_pos = 140 + 45*i
            else:
                x_pos = config.SCREEN_WIDTH//2 + 50
                y_pos = 140 + 45*(i-5)
            label = font.render(f"{skill}: {allocations[i]}", True, color2)
            screen.blit(label, (x_pos, y_pos))
        
        pts = font.render(f"Points left: {skill_points}", True, (200,200,255))
        screen.blit(pts, (config.SCREEN_WIDTH//2 - pts.get_width()//2, 420))
        instr = font.render("Arrows: Move/Change, R=random, Enter: Confirm", True, (180,180,180))
        screen.blit(instr, (config.SCREEN_WIDTH//2-180, 450))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Toggle fullscreen
                    is_fullscreen, screen = toggle_fullscreen(is_fullscreen, screen, config)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    skill_idx = (skill_idx - 1) % len(skills)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    skill_idx = (skill_idx + 1) % len(skills)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    if skill_points > 0:
                        allocations[skill_idx] += 1
                        skill_points -= 1
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    if allocations[skill_idx] > 0:
                        allocations[skill_idx] -= 1
                        skill_points += 1
                elif event.key == pygame.K_r:
                    # Randomize all allocations
                    allocations = [0]*len(skills)
                    import random
                    for _ in range(20):
                        idx = random.randint(0, len(skills)-1)
                        allocations[idx] += 1
                    skill_points = 0  # All points distributed
                    skill_idx = random.randint(0, len(skills)-1)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if skill_points == 0:
                        allocating = False
    # Return name, color, skills, race, skin_tone, and is_fullscreen
    return name, color, dict(zip(skills, allocations)), selected_race, skin_tone, is_fullscreen


def draw_campaign_menu(screen, config, campaign_menu_state, election_timeline):
    """Draw the campaign promise selection menu."""
    # Semi-transparent background
    overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA, True)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))
    
    # Main panel
    panel_width = 800
    panel_height = 650
    panel_x = (config.SCREEN_WIDTH - panel_width) // 2
    panel_y = (config.SCREEN_HEIGHT - panel_height) // 2
    
    # Draw panel background
    panel_surf = get_cached_surface((panel_width, panel_height))
    panel_surf.fill((30, 30, 40))
    pygame.draw.rect(panel_surf, (100, 150, 200), (0, 0, panel_width, panel_height), 3)
    screen.blit(panel_surf, (panel_x, panel_y))
    
    # Title
    title_font = get_font(None, 36)
    title = title_font.render("🗳️ CAMPAIGN PROMISES", True, (255, 215, 0))
    screen.blit(title, (config.SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 20))
    
    # Instructions
    instruction_font = get_font(None, 18)
    selected_count = len(campaign_menu_state['selected_promises'])
    instruction_text = f"Select 3 promises for your campaign | Selected: {selected_count}/3"
    instruction = instruction_font.render(instruction_text, True, (180, 180, 180))
    screen.blit(instruction, (config.SCREEN_WIDTH // 2 - instruction.get_width() // 2, panel_y + 65))
    
    # Campaign days remaining
    days_left = 3 - election_timeline.days_in_campaign
    days_text = f"Campaign days remaining: {days_left}"
    days_surf = instruction_font.render(days_text, True, (255, 200, 100))
    screen.blit(days_surf, (config.SCREEN_WIDTH // 2 - days_surf.get_width() // 2, panel_y + 90))
    
    # Draw promise list
    promise_font = get_font(None, 22)
    list_y = panel_y + 130
    list_x = panel_x + 40
    
    all_promises = campaign_menu_state['all_promises']
    selected_promises = campaign_menu_state['selected_promises']
    selected_idx = campaign_menu_state['selected_idx']
    
    # Display promises (with scrolling if needed)
    visible_count = 12  # Number of promises to show at once
    start_idx = max(0, min(selected_idx - 5, len(all_promises) - visible_count))
    end_idx = min(start_idx + visible_count, len(all_promises))
    
    for i in range(start_idx, end_idx):
        promise = all_promises[i]
        is_selected = promise in selected_promises
        is_highlighted = i == selected_idx
        
        # Background for highlighted item
        if is_highlighted:
            highlight_surf = get_cached_surface((panel_width - 80, 35))
            highlight_surf.fill((60, 80, 120))
            screen.blit(highlight_surf, (list_x - 10, list_y - 5))
        
        # Checkmark for selected promises
        if is_selected:
            check_text = promise_font.render("✓", True, (100, 255, 100))
            screen.blit(check_text, (list_x, list_y))
            promise_color = (100, 255, 100)
        else:
            promise_color = (255, 255, 255) if is_highlighted else (200, 200, 200)
        
        # Promise text
        promise_text = promise_font.render(f"  {promise}", True, promise_color)
        screen.blit(promise_text, (list_x + 30, list_y))
        
        list_y += 40
    
    # Bottom instructions
    bottom_y = panel_y + panel_height - 80
    control_font = get_font(None, 20)
    
    controls = [
        "↑/↓: Navigate",
        "ENTER: Select/Deselect",
        "P/ESC: Close"
    ]
    
    control_x = panel_x + 50
    for control in controls:
        control_surf = control_font.render(control, True, (150, 150, 150))
        screen.blit(control_surf, (control_x, bottom_y))
        control_x += control_surf.get_width() + 50
    
    # Warning if 3 selected
    if selected_count == 3:
        warning_text = "Press ENTER to finalize your campaign promises!"
        warning_surf = control_font.render(warning_text, True, (255, 200, 100))
        screen.blit(warning_surf, (config.SCREEN_WIDTH // 2 - warning_surf.get_width() // 2, bottom_y + 35))

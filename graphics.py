import pygame


class Graphics:
    def draw_pause_menu(self, options, selected_idx, config, player_died=False, mouse_pos=None):
        font = pygame.font.SysFont(None, 48)
        small = pygame.font.SysFont(None, 32)
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))
        y = 160
        rects = []
        for i, opt in enumerate(options):
            color = (255,255,0) if i == selected_idx else (255,255,255)
            surf = font.render(opt, True, color)
            x = self.config.SCREEN_WIDTH//2 - surf.get_width()//2
            self.screen.blit(surf, (x, y))
            rects.append(pygame.Rect(x, y, surf.get_width(), surf.get_height()))
            y += 64
        instr = small.render("Arrows: Move  Enter: Select  Esc/P: Resume", True, (180,180,180))
        self.screen.blit(instr, (self.config.SCREEN_WIDTH//2 - instr.get_width()//2, y+16))
        return rects

    def draw_settings_menu(self, settings_options, settings_state, selected_idx, config):
        small = pygame.font.SysFont(None, 32)
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))
        y = 100
        for i, opt in enumerate(settings_options):
            name = opt[0]
            val = settings_state.get(name, "")
            if name == "Language":
                val = config.LANGUAGES[settings_state["Language"]]
            elif name == "Fullscreen":
                val = "On" if settings_state["Fullscreen"] else "Off"
            elif name == "Key Bindings":
                val = "(Press Enter to edit)"
            color = (255,255,0) if i == selected_idx else (255,255,255)
            txt = f"{name}: {val}"
            surf = small.render(txt, True, color)
            self.screen.blit(surf, (self.config.SCREEN_WIDTH//2 - surf.get_width()//2, y))
            y += 48
        instr = small.render("Arrows: Move/Change  Esc/P: Back", True, (180,180,180))
        self.screen.blit(instr, (self.config.SCREEN_WIDTH//2 - instr.get_width()//2, y+16))

    def __init__(self, config, screen):
        self.config = config
        self.screen = screen

    def render(self, world, player, entities, show_equipment=False, equip_menu_state=None, show_inventory=False, inventory_menu_state=None, inventory_categories=None, inventory_action_msg=None, inventory_inspect_item=None, inventory_items_by_cat=None, npc_manager=None):
        self.screen.fill((0, 0, 0))
        
        if show_equipment:
            if equip_menu_state is None:
                equip_menu_state = {}
            self.draw_equipment_menu(player, equip_menu_state)
            return
        if show_inventory:
            if inventory_menu_state is None:
                inventory_menu_state = {'submenu': 0, 'item_idx': 0}
            if inventory_categories is None:
                inventory_categories = ['Food', 'Weapons', 'Equipment', 'Quest Items', 'Other']
            self.draw_inventory_menu(player, inventory_menu_state, inventory_categories, inventory_items_by_cat)
            # Draw action message if any
            if inventory_action_msg:
                font = pygame.font.SysFont(None, 32)
                surf = font.render(inventory_action_msg, True, (255,255,0))
                self.screen.blit(surf, (self.config.SCREEN_WIDTH//2 - surf.get_width()//2, self.config.SCREEN_HEIGHT - 120))
            # Draw inspect popup if any
            if inventory_inspect_item:
                self.draw_inventory_inspect_popup(inventory_inspect_item)
            return

        # --- MAIN WORLD RENDERING LOGIC ---
        tile_size = self.config.TILE_SIZE
        # Convert player position to integers to prevent sub-pixel jittering
        px = int(player.x)
        py = int(player.y)
        # Center of screen in pixels
        cx = self.config.SCREEN_WIDTH // 2
        cy = self.config.SCREEN_HEIGHT // 2
        # How many tiles fit on screen
        tiles_x = self.config.SCREEN_WIDTH // tile_size + 2
        tiles_y = self.config.SCREEN_HEIGHT // tile_size + 2
        # Top-left tile to draw
        start_x = px - (tiles_x//2)*tile_size
        start_y = py - (tiles_y//2)*tile_size
        
        for ix in range(tiles_x):
            for iy in range(tiles_y):
                wx = (start_x + ix*tile_size) // tile_size * tile_size
                wy = (start_y + iy*tile_size) // tile_size * tile_size
                tile = world.get_tile(wx, wy)
                sx = cx + (wx - px)
                sy = cy + (wy - py)
                
                # Draw ground layer
                if tile and hasattr(tile, 'layers') and 'ground' in tile.layers:
                    self.draw_tile_layer(tile.layers['ground'], sx, sy, tile_size)
                # Draw object layer
                if tile and hasattr(tile, 'layers') and 'object' in tile.layers and tile.layers['object']:
                    self.draw_tile_layer(tile.layers['object'], sx, sy, tile_size)
                # Draw effect layer
                if tile and hasattr(tile, 'layers') and 'effect' in tile.layers and tile.layers['effect']:
                    self.draw_tile_layer(tile.layers['effect'], sx, sy, tile_size)
        
        # Draw player as a colored rectangle at center of screen (50% smaller, person-shaped)
        player_width = (tile_size - 4) // 2  # Half width for 50% size
        player_height = int((tile_size - 4) * 0.75)  # Taller than wide for person shape
        
        # Draw equipped weapon BEFORE player so it appears behind/beside
        self.draw_equipped_weapon(player, cx, cy, player_width, player_height, npc_manager)
        
        pygame.draw.rect(self.screen, player.color, (cx - player_width//2, cy - player_height//2, player_width, player_height))
        pygame.draw.rect(self.screen, (255,255,255), (cx - player_width//2, cy - player_height//2, player_width, player_height), 2)
        
        # Draw equipped items (helmet, armor, boots, gloves, shield) AFTER player
        self.draw_equipped_items(player, cx, cy, player_width, player_height)
        
        # Draw direction indicator arrow
        arrow_color = (255, 255, 100)  # Yellow arrow
        arrow_size = 12
        if hasattr(player, 'facing_direction'):
            if player.facing_direction == 'up':
                arrow_points = [(cx, cy - player_height//2 - 15), (cx - arrow_size//2, cy - player_height//2 - 5), (cx + arrow_size//2, cy - player_height//2 - 5)]
            elif player.facing_direction == 'down':
                arrow_points = [(cx, cy + player_height//2 + 15), (cx - arrow_size//2, cy + player_height//2 + 5), (cx + arrow_size//2, cy + player_height//2 + 5)]
            elif player.facing_direction == 'left':
                arrow_points = [(cx - player_width//2 - 15, cy), (cx - player_width//2 - 5, cy - arrow_size//2), (cx - player_width//2 - 5, cy + arrow_size//2)]
            elif player.facing_direction == 'right':
                arrow_points = [(cx + player_width//2 + 15, cy), (cx + player_width//2 + 5, cy - arrow_size//2), (cx + player_width//2 + 5, cy + arrow_size//2)]
            else:
                arrow_points = [(cx, cy + player_height//2 + 15), (cx - arrow_size//2, cy + player_height//2 + 5), (cx + arrow_size//2, cy + player_height//2 + 5)]
            pygame.draw.polygon(self.screen, arrow_color, arrow_points)
            pygame.draw.polygon(self.screen, (200, 200, 0), arrow_points, 2)
    
    def draw_equipped_weapon(self, player, cx, cy, player_width, player_height, npc_manager=None):
        """Draw equipped weapon beside player with swing animation"""
        import time
        import math
        
        # Check if player has equipped weapon
        equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
        if not equipped_weapon:
            return
        
        # Get weapon type and name
        weapon_name = getattr(equipped_weapon, 'name', '').lower()
        weapon_type = getattr(equipped_weapon, 'type', 'weapon').lower()
        
        # Determine weapon visual style
        if 'stick' in weapon_name or 'staff' in weapon_name:
            weapon_color = (139, 90, 43)  # Brown for sticks
            weapon_length = 20
            weapon_width = 3
        elif 'axe' in weapon_name:
            weapon_color = (180, 180, 180)  # Gray blade
            weapon_length = 18
            weapon_width = 8
        elif 'dagger' in weapon_name or 'knife' in weapon_name:
            weapon_color = (220, 220, 255)  # Light blue
            weapon_length = 12
            weapon_width = 3
        elif 'hammer' in weapon_name or 'mace' in weapon_name:
            weapon_color = (100, 100, 100)  # Dark gray
            weapon_length = 15
            weapon_width = 8
        elif 'spear' in weapon_name or 'lance' in weapon_name:
            weapon_color = (200, 200, 100)  # Yellow-ish
            weapon_length = 25
            weapon_width = 2
        else:  # Default sword-like weapon
            weapon_color = (200, 200, 200)  # Silver
            weapon_length = 18
            weapon_width = 4
        
        # Check for recent attack (swing animation)
        attack_time = getattr(player, 'last_attack_time', 0)
        time_since_attack = time.time() - attack_time
        is_swinging = time_since_attack < 0.35  # 350ms swing animation
        
        # Calculate swing animation angle
        swing_angle = 0
        if is_swinging:
            # Swing progress from 0 to 1
            swing_progress = time_since_attack / 0.35
            # Swing arc from -60 degrees to +60 degrees
            swing_angle = math.sin(swing_progress * math.pi) * 60  # Smooth arc
        
        # Get player facing direction
        facing = getattr(player, 'facing_direction', 'down')
        
        # Position weapon based on facing direction
        if facing == 'right':
            # Weapon on right side
            base_angle = -45 if not is_swinging else -45 + swing_angle
            weapon_x = cx + player_width//2 + 8
            weapon_y = cy
        elif facing == 'left':
            # Weapon on left side
            base_angle = 135 if not is_swinging else 135 - swing_angle
            weapon_x = cx - player_width//2 - 8
            weapon_y = cy
        elif facing == 'up':
            # Weapon above
            base_angle = -90 if not is_swinging else -90 + swing_angle
            weapon_x = cx + player_width//4
            weapon_y = cy - player_height//2 - 8
        else:  # down or default
            # Weapon below/beside
            base_angle = 45 if not is_swinging else 45 + swing_angle
            weapon_x = cx + player_width//2 + 8
            weapon_y = cy + player_height//4
        
        # Convert angle to radians
        angle_rad = math.radians(base_angle)
        
        # Calculate weapon end point
        end_x = weapon_x + math.cos(angle_rad) * weapon_length
        end_y = weapon_y + math.sin(angle_rad) * weapon_length
        
        # Draw weapon as a line with thickness
        pygame.draw.line(self.screen, weapon_color, 
                        (int(weapon_x), int(weapon_y)), 
                        (int(end_x), int(end_y)), 
                        weapon_width)
        
        # Add weapon highlight/edge
        highlight_color = tuple(min(255, c + 40) for c in weapon_color)
        pygame.draw.line(self.screen, highlight_color, 
                        (int(weapon_x), int(weapon_y)), 
                        (int(end_x), int(end_y)), 
                        max(1, weapon_width - 2))
        
        # For axes and hammers, add a head
        if weapon_width >= 7:
            # Draw weapon head as a small rectangle at the tip
            head_size = weapon_width + 2
            head_x = end_x - head_size//2
            head_y = end_y - head_size//2
            pygame.draw.rect(self.screen, weapon_color, 
                           (int(head_x), int(head_y), head_size, head_size))
            pygame.draw.rect(self.screen, highlight_color, 
                           (int(head_x), int(head_y), head_size, head_size), 1)
        
        # Draw inventory/equipment tooltip (bottom left)
        self.draw_inventory_tooltip(player)
        # Draw global population tracker (top left)
        if npc_manager is not None:
            font = pygame.font.SysFont(None, 32)
            pop_text = f"Population: {npc_manager.get_population()}"
            surf = font.render(pop_text, True, (255,255,200))
            self.screen.blit(surf, (20, 20))
    
    def draw_equipped_items(self, player, cx, cy, player_width, player_height):
        """Draw all equipped items: helmet, chest, boots, hands, shield"""
        import time
        import math
        
        # Draw helmet (floating above head)
        equipped_helmet = player.equipment.get('head')
        if equipped_helmet:
            helmet_name = getattr(equipped_helmet, 'name', '').lower()
            
            # Determine helmet color based on name
            if 'iron' in helmet_name or 'steel' in helmet_name:
                helmet_color = (180, 180, 190)  # Silver/gray
            elif 'leather' in helmet_name:
                helmet_color = (139, 90, 43)  # Brown
            elif 'crown' in helmet_name or 'gold' in helmet_name:
                helmet_color = (255, 215, 0)  # Gold
            elif 'mage' in helmet_name or 'wizard' in helmet_name:
                helmet_color = (120, 100, 180)  # Purple
            else:
                helmet_color = (160, 160, 160)  # Default gray
            
            # Helmet position - floating above head
            helmet_size = 14
            helmet_x = cx - helmet_size//2
            helmet_y = cy - player_height//2 - helmet_size - 4
            
            # Draw helmet as rounded rectangle
            pygame.draw.ellipse(self.screen, helmet_color, 
                              (int(helmet_x), int(helmet_y), helmet_size, helmet_size))
            # Highlight
            pygame.draw.ellipse(self.screen, tuple(min(255, c + 40) for c in helmet_color), 
                              (int(helmet_x), int(helmet_y), helmet_size, helmet_size), 2)
        
        # Draw chest armor (on player body)
        equipped_chest = player.equipment.get('chest') or player.equipment.get('armor')
        if equipped_chest:
            chest_name = getattr(equipped_chest, 'name', '').lower()
            
            # Determine armor color
            if 'plate' in chest_name or 'steel' in chest_name:
                armor_color = (200, 200, 210)  # Bright silver
            elif 'chain' in chest_name or 'mail' in chest_name:
                armor_color = (150, 150, 160)  # Gray
            elif 'leather' in chest_name:
                armor_color = (120, 80, 40)  # Brown leather
            elif 'mage' in chest_name or 'robe' in chest_name:
                armor_color = (80, 60, 140)  # Purple robes
            else:
                armor_color = (140, 140, 150)  # Default
            
            # Armor overlay on player body
            armor_width = player_width - 4
            armor_height = int(player_height * 0.6)
            armor_x = cx - armor_width//2
            armor_y = cy - armor_height//2
            
            # Draw armor as rectangle with border
            pygame.draw.rect(self.screen, armor_color,
                           (int(armor_x), int(armor_y), armor_width, armor_height))
            pygame.draw.rect(self.screen, tuple(min(255, c + 50) for c in armor_color),
                           (int(armor_x), int(armor_y), armor_width, armor_height), 1)
        
        # Draw boots (at feet - directly on character)
        equipped_boots = player.equipment.get('feet')
        if equipped_boots:
            boots_name = getattr(equipped_boots, 'name', '').lower()
            
            # Determine boots color
            if 'iron' in boots_name or 'steel' in boots_name:
                boots_color = (180, 180, 190)
            elif 'leather' in boots_name:
                boots_color = (100, 70, 30)
            elif 'speed' in boots_name or 'enchanted' in boots_name:
                boots_color = (100, 200, 255)  # Light blue
            else:
                boots_color = (120, 90, 50)
            
            # Boots at bottom of player
            boot_width = 10
            boot_height = 6
            left_boot_x = cx - player_width//3
            right_boot_x = cx + player_width//6
            boots_y = cy + player_height//2 - 2
            
            # Draw both boots
            pygame.draw.rect(self.screen, boots_color,
                           (int(left_boot_x - boot_width//2), int(boots_y), boot_width, boot_height))
            pygame.draw.rect(self.screen, boots_color,
                           (int(right_boot_x - boot_width//2), int(boots_y), boot_width, boot_height))
        
        # Draw gloves (floating near hands/arms)
        equipped_gloves = player.equipment.get('hands')
        if equipped_gloves:
            gloves_name = getattr(equipped_gloves, 'name', '').lower()
            
            # Determine gloves color
            if 'power' in gloves_name or 'gauntlet' in gloves_name:
                gloves_color = (200, 50, 50)  # Red
            elif 'leather' in gloves_name:
                gloves_color = (120, 80, 40)
            else:
                gloves_color = (140, 140, 140)
            
            # Get player facing direction
            facing = getattr(player, 'facing_direction', 'down')
            
            # Gloves float near arms
            glove_size = 8
            if facing == 'right':
                left_glove_x = cx - player_width//2 - 4
                right_glove_x = cx + player_width//2 + 4
            elif facing == 'left':
                left_glove_x = cx + player_width//2 + 4
                right_glove_x = cx - player_width//2 - 4
            else:
                left_glove_x = cx - player_width//2 - 2
                right_glove_x = cx + player_width//2 + 2
            
            gloves_y = cy
            
            # Draw gloves as small squares
            pygame.draw.rect(self.screen, gloves_color,
                           (int(left_glove_x - glove_size//2), int(gloves_y - glove_size//2), glove_size, glove_size))
            pygame.draw.rect(self.screen, gloves_color,
                           (int(right_glove_x - glove_size//2), int(gloves_y - glove_size//2), glove_size, glove_size))
        
        # Draw shield (opposite side of weapon)
        equipped_shield = player.equipment.get('off_hand')
        if equipped_shield:
            shield_name = getattr(equipped_shield, 'name', '').lower()
            
            # Determine shield appearance
            if 'wooden' in shield_name:
                shield_color = (120, 90, 50)
                shield_size = 16
            elif 'iron' in shield_name or 'steel' in shield_name:
                shield_color = (180, 180, 200)
                shield_size = 18
            elif 'tower' in shield_name:
                shield_color = (200, 200, 220)
                shield_size = 24
            else:
                shield_color = (160, 160, 170)
                shield_size = 18
            
            # Get player facing direction
            facing = getattr(player, 'facing_direction', 'down')
            
            # Position shield opposite to weapon
            if facing == 'right':
                # Shield on left
                shield_x = cx - player_width//2 - 12
                shield_y = cy
            elif facing == 'left':
                # Shield on right
                shield_x = cx + player_width//2 + 12
                shield_y = cy
            elif facing == 'up':
                # Shield on left side
                shield_x = cx - player_width//2 - 10
                shield_y = cy - player_height//4
            else:  # down or default
                # Shield on left side
                shield_x = cx - player_width//2 - 10
                shield_y = cy + player_height//4
            
            # Draw shield as oval/ellipse
            pygame.draw.ellipse(self.screen, shield_color,
                              (int(shield_x - shield_size//3), int(shield_y - shield_size//2), 
                               int(shield_size//1.5), shield_size))
            # Shield boss (center decoration)
            boss_size = shield_size // 4
            pygame.draw.circle(self.screen, tuple(min(255, c + 40) for c in shield_color),
                             (int(shield_x), int(shield_y)), boss_size)
            # Shield border
            pygame.draw.ellipse(self.screen, tuple(min(255, c + 60) for c in shield_color),
                              (int(shield_x - shield_size//3), int(shield_y - shield_size//2), 
                               int(shield_size//1.5), shield_size), 2)

    def draw_inventory_inspect_popup(self, item):
        font = pygame.font.SysFont(None, 32)
        small = pygame.font.SysFont(None, 24)
        # Popup background
        w, h = 340, 180
        x = self.config.SCREEN_WIDTH//2 - w//2
        y = self.config.SCREEN_HEIGHT//2 - h//2
        pygame.draw.rect(self.screen, (30,30,40), (x, y, w, h))
        pygame.draw.rect(self.screen, (200,200,100), (x, y, w, h), 2)
        # Item info
        if isinstance(item, tuple):
            name, count = item
            lines = [f"{name.title()} (x{count})"]
        else:
            lines = [f"{item.name}", f"Type: {getattr(item, 'type', 'Unknown')}"]
            if hasattr(item, 'durability'):
                lines.append(f"Durability: {item.durability}/{item.max_durability}")
            if hasattr(item, 'stats') and item.stats:
                for k, v in item.stats.items():
                    lines.append(f"{k.title()}: {v}")
        for i, line in enumerate(lines):
            surf = font.render(line, True, (255,255,220))
            self.screen.blit(surf, (x+20, y+20+i*36))
        # Instructions
        self.screen.blit(small.render("(Press any key to close)", True, (180,180,180)), (x+20, y+h-32))

    def draw_inventory_menu(self, player, state, categories, items_by_cat=None):
        font = pygame.font.SysFont(None, 36)
        small = pygame.font.SysFont(None, 28)
        # Draw menu title
        surf = font.render("Inventory", True, (255,255,200))
        self.screen.blit(surf, (self.config.SCREEN_WIDTH//2 - surf.get_width()//2, 40))
        # Draw category tabs
        tab_y = 90
        tab_x = 80
        for i, cat in enumerate(categories):
            color = (255,255,0) if i == state['submenu'] else (200,200,200)
            tab = small.render(cat, True, color)
            self.screen.blit(tab, (tab_x + i*140, tab_y))
        
        # Use the items_by_cat passed from main.py if available
        # This ensures display matches the selection logic
        if items_by_cat is None:
            # Fallback: build items_by_cat if not provided (shouldn't happen in normal gameplay)
            items_by_cat = {cat: [] for cat in categories}
            # Stackables (food, quest, other)
            for k, v in player.inventory.items():
                if k == 'items':
                    continue
                if v > 0:  # Only show items with quantity
                    if k in ['stick', 'fiber']:
                        items_by_cat['Other'].append((k, v))
                    # Example: add food/quest logic here
            # Equipment and weapons
            for item in player.inventory.get('items', []):
                if hasattr(item, 'type'):
                    if item.type == 'weapon':
                        items_by_cat['Weapons'].append(item)
                    elif item.type == 'armor' or item.type == 'accessory':
                        items_by_cat['Equipment'].append(item)
                    else:
                        items_by_cat['Other'].append(item)
                else:
                    items_by_cat['Other'].append(item)
        
        # Draw items in selected category
        selected_cat = categories[state['submenu']]
        items = items_by_cat[selected_cat]
        y = 140
        if not items:
            self.screen.blit(small.render("(No items)", True, (180,180,180)), (120, y))
        else:
            for i, item in enumerate(items):
                color = (0,255,0) if i == state['item_idx'] else (255,255,255)
                if isinstance(item, tuple):
                    # Stackable (name, count)
                    name, count = item
                    label = f"{name.title()} x{count}"
                else:
                    label = f"{item.name} ({item.durability}/{item.max_durability})"
                self.screen.blit(small.render(label, True, color), (120, y + i*32))
        # Instructions
        y2 = self.config.SCREEN_HEIGHT - 80
        self.screen.blit(small.render("Left/Right: Tab  Up/Down: Select  I/Esc: Close", True, (180,180,180)), (100, y2))

    def draw_equipment_menu(self, player, state):
        # Equipment menu with selection and stat comparison
        font = pygame.font.SysFont(None, 36)
        small = pygame.font.SysFont(None, 28)
        surf = font.render("Equipment & Inventory", True, (255,255,200))
        self.screen.blit(surf, (self.config.SCREEN_WIDTH//2 - surf.get_width()//2, 40))
        y = 100
        # Equipment slots
        slots = list(player.equipment.keys())
        slot_idx = state.get('slot_idx', 0)
        inv_idx = state.get('inv_idx', 0)
        mode = state.get('mode', 'equip')  # 'equip' or 'unequip'
        # Draw equipment slots
        for i, slot in enumerate(slots):
            eq = player.equipment[slot]
            color = (255,255,0) if i == slot_idx and mode=='unequip' else (255,255,255)
            eq_name = eq.name if eq else 'None'
            eq_dur = f" ({eq.durability}/{eq.max_durability})" if eq else ''
            self.screen.blit(small.render(f"{slot.title()}: {eq_name}{eq_dur}", True, color), (100, y + i*32))
        y += 32*len(slots) + 16
        # Inventory items (equipment only)
        items = [it for it in player.inventory['items']]
        for i, item in enumerate(items):
            color = (0,255,0) if i == inv_idx and mode=='equip' else (255,255,255)
            name = f"{item.name} ({item.durability}/{item.max_durability})"
            self.screen.blit(small.render(name, True, color), (100, y + i*28))
        # Stat comparison
        if mode == 'equip' and items:
            selected = items[inv_idx]
            slot = selected.type
            eq = player.equipment.get(slot)
            stat_y = y + len(items)*28 + 32
            self.screen.blit(small.render("Stat Comparison:", True, (255,255,200)), (100, stat_y))
            stat_y += 28
            for stat, val in selected.stats.items():
                eq_val = eq.stats.get(stat, 0) if eq else 0
                diff = val - eq_val
                if diff > 0:
                    col = (0,255,0)
                elif diff < 0:
                    col = (255,0,0)
                else:
                    col = (255,255,255)
                txt = f"{stat.title()}: {val} ({'+' if diff>0 else ''}{diff})"
                self.screen.blit(small.render(txt, True, col), (120, stat_y))
                stat_y += 24
        # Instructions
        y2 = self.config.SCREEN_HEIGHT - 120
        self.screen.blit(small.render("Arrows: Navigate | Enter: Equip/Use | Space: View Details", True, (180,180,180)), (100, y2))
        self.screen.blit(small.render("E/Q: Quick Equip | D: Drop | U: Use Consumable | I: Close", True, (180,180,180)), (100, y2+28))

    def draw_inventory_tooltip(self, player):
        font = pygame.font.SysFont(None, 28)
        stick_count = player.inventory.get('stick', 0)
        fiber_count = player.inventory.get('fiber', 0)
        # Stick stacking mechanic: damage = 1 + (sticks-1)*0.5, rounded
        stick_damage = 1 + max(0, stick_count-1)*0.5
        next_damage = 1 + stick_count*0.5
        lines = [
            f"Sticks: {stick_count}",
            f"Stick Damage: {stick_damage:.1f}",
            f"Next Stick: {next_damage:.1f}",
            f"Fiber: {fiber_count}"
        ]
        x, y = 16, self.config.SCREEN_HEIGHT - 28*len(lines) - 16
        for i, line in enumerate(lines):
            surf = font.render(line, True, (255,255,200))
            self.screen.blit(surf, (x, y + i*28))

    def draw_tile_layer(self, kind, x, y, size):
        # Draw tiles with visual distinction for objects
        if kind == 'empty':
            pygame.draw.rect(self.screen, (40,40,40), (x, y, size, size))
        elif kind == 'grass':
            pygame.draw.rect(self.screen, (60,180,60), (x, y, size, size))
        elif kind == 'rock_group':
            pygame.draw.rect(self.screen, (100,100,100), (x, y, size, size))
            # Add rock indicators
            pygame.draw.circle(self.screen, (120,120,120), (x+size//3, y+size//2), size//6)
            pygame.draw.circle(self.screen, (80,80,80), (x+2*size//3, y+2*size//3), size//7)
        elif kind == 'tree':
            # Draw grass background
            pygame.draw.rect(self.screen, (60,180,60), (x, y, size, size))
            # Draw tree trunk
            pygame.draw.rect(self.screen, (100,60,20), (x+size//2-3, y+size//2, 6, size//2))
            # Draw tree top
            pygame.draw.circle(self.screen, (30,120,30), (x+size//2, y+size//2), size//3)
        elif kind == 'bush':
            # Draw grass background
            pygame.draw.rect(self.screen, (60,180,60), (x, y, size, size))
            # Draw bush as smaller dark green circle
            pygame.draw.circle(self.screen, (40,140,40), (x+size//2, y+size//2), size//3)
        elif kind == 'snow':
            pygame.draw.rect(self.screen, (220,220,255), (x, y, size, size))
        elif kind == 'water':
            pygame.draw.rect(self.screen, (30,100,200), (x, y, size, size))
            # Add water wave lines
            for i in range(2):
                pygame.draw.arc(self.screen, (80,180,255), (x+4, y+size//2+i*4, size-8, 8), 0, 3.14, 2)
        elif kind == 'sand':
            pygame.draw.rect(self.screen, (200,180,120), (x, y, size, size))
        elif kind == 'stone':
            pygame.draw.rect(self.screen, (100,100,100), (x, y, size, size))
        else:
            # Unknown tile type: draw black square
            pygame.draw.rect(self.screen, (0,0,0), (x, y, size, size))
        
        # Draw grid lines for clarity (thin lines)
        pygame.draw.rect(self.screen, (0,0,0), (x, y, size, size), 1)

    def draw_centered_text(self, text, y, size=40, color=(255,255,255)):
        font = pygame.font.SysFont(None, size)
        surf = font.render(text, True, color)
        x = self.config.SCREEN_WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(surf, (x, y))

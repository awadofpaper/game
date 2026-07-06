import pygame

def spellbook_menu(screen, font, player, SPELLS):
    running = True
    clock = pygame.time.Clock()
    spell_list = sorted(SPELLS.keys())  # Show all spells, not just known
    selected = 0
    message = ""

    while running:
        screen.fill((30, 30, 50))
        screen_width, screen_height = screen.get_size()

        # Title
        title = font.render("Spellbook", True, (255, 255, 180))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 40))

        # List all spells, highlight selected, show locked/known
        y = 100
        for i, spell_id in enumerate(spell_list):
            spell = SPELLS.get(spell_id)
            if not spell:
                continue
            known = spell_id in player.known_spells
            if i == selected:
                color = (255, 255, 180) if known else (180, 180, 180)
            else:
                color = (220, 220, 255) if known else (120, 120, 120)
            suffix = ""
            if not known:
                suffix = " [LOCKED]"
            elif spell_id == player.selected_spell:
                suffix = " [Primary]"
            elif spell_id == player.secondary_spell:
                suffix = " [Secondary]"
            name_text = font.render(spell["name"] + suffix, True, color)
            screen.blit(name_text, (100, y))
            y += 36

        # Show details for selected spell (if known)
        if spell_list:
            spell_id = spell_list[selected]
            spell = SPELLS.get(spell_id)
            if spell:
                detail_lines = [
                    spell["name"],
                    "",
                    spell.get("description", ""),
                    "",
                    f"Mana Cost: {spell.get('mana_cost', '-')}",
                    f"Cooldown: {spell.get('cooldown', '-')}",
                ]
                if "damage" in spell:
                    detail_lines.append(f"Damage: {spell['damage']}")
                if "healing" in spell:
                    detail_lines.append(f"Healing: {spell['healing']}")
                if "type" in spell:
                    detail_lines.append(f"Type: {spell['type'].capitalize()}")
                # Add more as needed

                tooltip_font = pygame.font.SysFont(None, 22)
                tooltip_w = max(tooltip_font.size(line)[0] for line in detail_lines) + 18
                tooltip_h = 8 + len(detail_lines) * 22
                tx, ty = screen_width - tooltip_w - 60, 120
                # Dim background if locked
                bg_color = (40, 40, 80) if spell_id in player.known_spells else (30, 30, 30)
                pygame.draw.rect(screen, bg_color, (tx, ty, tooltip_w, tooltip_h), border_radius=6)
                pygame.draw.rect(screen, (180, 180, 220), (tx, ty, tooltip_w, tooltip_h), 2, border_radius=6)
                for i, line in enumerate(detail_lines):
                    text_color = (255, 255, 255) if spell_id in player.known_spells else (160, 160, 160)
                    text = tooltip_font.render(line, True, text_color)
                    screen.blit(text, (tx + 9, ty + 4 + i * 22))
                if spell_id not in player.known_spells:
                    lock_text = tooltip_font.render("LOCKED", True, (255, 80, 80))
                    screen.blit(lock_text, (tx + tooltip_w // 2 - lock_text.get_width() // 2, ty + tooltip_h - 28))

        # Show confirmation message if set
        if message:
            msg_font = pygame.font.SysFont(None, 26)
            msg = msg_font.render(message, True, (255, 255, 180))
            screen.blit(msg, (screen_width // 2 - msg.get_width() // 2, screen_height - 100))

        info = font.render("UP/DOWN: Select  F: Set Primary  G: Set Secondary  ESC: Close", True, (200, 200, 200))
        screen.blit(info, (screen_width // 2 - info.get_width() // 2, screen_height - 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(spell_list)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(spell_list)
                elif event.key == pygame.K_f and spell_list[selected] in player.known_spells:
                    player.selected_spell = spell_list[selected]
                    message = f"Set {SPELLS[spell_list[selected]]['name']} as Primary"
                elif event.key == pygame.K_g and spell_list[selected] in player.known_spells:
                    player.secondary_spell = spell_list[selected]
                    message = f"Set {SPELLS[spell_list[selected]]['name']} as Secondary"
        clock.tick(30)
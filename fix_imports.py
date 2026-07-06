"""
Quick script to fix duplicate import sections in main.py
Adds SpellHUD and AIDebugOverlay imports to BOTH sections
"""

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace both occurrences
content = content.replace(
    'from enemies import Enemy, spawn_enemy, determine_enemy_rarity, handle_enemy_drops, ENEMY_TYPES\nfrom key_bindings import',
    'from enemies import Enemy, spawn_enemy, determine_enemy_rarity, handle_enemy_drops, ENEMY_TYPES\nfrom spell_hud import SpellHUD\nfrom ai_debug_overlay import AIDebugOverlay\nfrom key_bindings import'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed imports in main.py")
print("Added spell_hud and ai_debug_overlay imports to all import sections")

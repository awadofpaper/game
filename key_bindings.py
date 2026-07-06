"""
Key Bindings System
Allows players to customize all game controls
"""

import pygame
import json
import os

# Mouse button constants (pygame uses numeric values for mouse buttons)
MOUSE_LEFT = 1
MOUSE_MIDDLE = 2
MOUSE_RIGHT = 3
MOUSE_SCROLL_UP = 4
MOUSE_SCROLL_DOWN = 5

class KeyBindings:
    """Manages customizable key bindings for all game actions"""
    
    # Default key bindings
    DEFAULT_BINDINGS = {
        # Movement
        "move_up": [pygame.K_w, pygame.K_UP],
        "move_down": [pygame.K_s, pygame.K_DOWN],
        "move_left": [pygame.K_a, pygame.K_LEFT],
        "move_right": [pygame.K_d, pygame.K_RIGHT],
        
        # Combat
        "attack": [pygame.K_SPACE, MOUSE_LEFT],  # Spacebar or Left Click
        "dodge": [pygame.K_LCTRL, pygame.K_RCTRL, MOUSE_RIGHT],  # Ctrl or Right Click
        "cast_primary_spell": [pygame.K_q],
        "cast_secondary_spell": [pygame.K_e],  # Changed from R to E for easier access
        
        # Menus
        "inventory": [pygame.K_i],
        # "equipment": [pygame.K_e],  # DISABLED: Conflicts with "interact"
        "skill_tree": [pygame.K_k],
        "spellbook": [pygame.K_b],
        "stats": [pygame.K_x],
        "pause": [pygame.K_p],  # ESC now used for fullscreen toggle
        
        # Interactions
        "interact": [pygame.K_e],  # E for general interaction (gathering, fires, building entry)
        "dungeon_enter": [pygame.K_f],
        "crafting": [pygame.K_c],
        
        # Quick actions
        "quick_save": [pygame.K_F5],
        "quick_load": [pygame.K_F9],
        "smart_inventory": [pygame.K_F6],
        "performance_settings": [pygame.K_F3],
        "accessibility_settings": [pygame.K_F2],
        "ai_settings": [pygame.K_F9],
        
        # Debug (can be disabled in settings)
        "debug_burn": [pygame.K_1],
        "debug_freeze": [pygame.K_2],
        "debug_poison": [pygame.K_3],
        "debug_blessed": [pygame.K_4],
        "debug_haste": [pygame.K_5],
        "debug_regen": [pygame.K_6],
        "debug_clear": [pygame.K_0],
    }
    
    # Action display names and descriptions
    ACTION_INFO = {
        "move_up": ("Move Up", "Move character upward"),
        "move_down": ("Move Down", "Move character downward"),
        "move_left": ("Move Left", "Move character left"),
        "move_right": ("Move Right", "Move character right"),
        "attack": ("Attack", "Primary attack/break tiles"),
        "dodge": ("Dodge Roll", "Quick dodge roll in movement direction"),
        "cast_primary_spell": ("Cast Primary Spell", "Cast your selected primary spell"),
        "cast_secondary_spell": ("Cast Secondary Spell", "Cast your selected secondary spell"),
        "inventory": ("Open Inventory", "View and manage inventory"),
        "equipment": ("Open Equipment", "View and equip items"),
        "skill_tree": ("Open Skill Tree", "View and unlock skills"),
        "stats": ("Character Stats", "Allocate stat points"),
        "spellbook": ("Open Spellbook", "View and select spells"),
        "pause": ("Pause Menu", "Open pause/settings menu"),
        "interact": ("Interact", "Talk to NPCs"),
        "dungeon_enter": ("Enter Dungeon", "Enter/exit dungeon"),
        "crafting": ("Crafting", "Open crafting menu"),
        "quick_save": ("Quick Save", "Save game instantly"),
        "quick_load": ("Quick Load", "Load last save"),
        "smart_inventory": ("Smart Inventory", "Toggle smart inventory UI"),
        "performance_settings": ("Performance", "Open performance settings"),
        "accessibility_settings": ("Accessibility", "Open accessibility settings"),
        "ai_settings": ("AI Settings", "Open AI settings"),
        "debug_burn": ("Debug: Burn", "Test burn status effect"),
        "debug_freeze": ("Debug: Freeze", "Test freeze status effect"),
        "debug_poison": ("Debug: Poison", "Test poison status effect"),
        "debug_blessed": ("Debug: Blessed", "Test blessed status effect"),
        "debug_haste": ("Debug: Haste", "Test haste status effect"),
        "debug_regen": ("Debug: Regeneration", "Test regeneration status effect"),
        "debug_clear": ("Debug: Clear", "Clear all status effects"),
    }
    
    # Categories for organized display
    CATEGORIES = {
        "Movement": ["move_up", "move_down", "move_left", "move_right"],
        "Combat": ["attack", "dodge", "cast_primary_spell", "cast_secondary_spell"],
        "Menus": ["inventory", "equipment", "skill_tree", "stats", "spellbook", "pause", "crafting"],
        "Interaction": ["interact", "dungeon_enter"],
        "Quick Actions": ["quick_save", "quick_load", "smart_inventory", "performance_settings", "accessibility_settings", "ai_settings"],
        "Debug": ["debug_burn", "debug_freeze", "debug_poison", "debug_blessed", "debug_haste", "debug_regen", "debug_clear"],
    }
    
    def __init__(self, config_file="keybindings.json"):
        self.config_file = config_file
        self.bindings = {}
        self.load_bindings()
        
    def load_bindings(self):
        """Load key bindings from file or use defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Convert key codes back from strings
                    self.bindings = {}
                    for action, keys in loaded.items():
                        self.bindings[action] = [int(k) for k in keys]
                print(f"[KEYBINDINGS] Loaded custom key bindings from {self.config_file}")
            except Exception as e:
                print(f"[KEYBINDINGS] Error loading key bindings: {e}")
                self.reset_to_defaults()
        else:
            self.reset_to_defaults()
    
    def save_bindings(self):
        """Save current key bindings to file"""
        try:
            # Convert key codes to strings for JSON
            saveable = {action: [str(k) for k in keys] for action, keys in self.bindings.items()}
            with open(self.config_file, 'w') as f:
                json.dump(saveable, f, indent=2)
            print(f"[KEYBINDINGS] Saved key bindings to {self.config_file}")
            return True
        except Exception as e:
            print(f"[KEYBINDINGS] Error saving key bindings: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset all key bindings to defaults"""
        self.bindings = {action: keys.copy() for action, keys in self.DEFAULT_BINDINGS.items()}
        print("[KEYBINDINGS] Reset to default key bindings")
    
    def is_action(self, action, key_code):
        """Check if a key code matches an action"""
        return action in self.bindings and key_code in self.bindings[action]
    
    def get_keys_for_action(self, action):
        """Get list of keys bound to an action"""
        return self.bindings.get(action, [])
    
    def get_key_name(self, key_code):
        """Get human-readable name for a key code"""
        # Check if it's a mouse button
        if key_code == MOUSE_LEFT:
            return "LEFT CLICK"
        elif key_code == MOUSE_MIDDLE:
            return "MIDDLE CLICK"
        elif key_code == MOUSE_RIGHT:
            return "RIGHT CLICK"
        elif key_code == MOUSE_SCROLL_UP:
            return "SCROLL UP"
        elif key_code == MOUSE_SCROLL_DOWN:
            return "SCROLL DOWN"
        # Otherwise it's a keyboard key
        return pygame.key.name(key_code).upper()
    
    def get_action_display(self, action):
        """Get formatted display string for an action's keys"""
        keys = self.get_keys_for_action(action)
        if not keys:
            return "Unbound"
        return " / ".join([self.get_key_name(k) for k in keys])
    
    def bind_key(self, action, key_code, slot=0):
        """Bind a key to an action (slot 0 = primary, slot 1 = secondary)"""
        if action not in self.bindings:
            self.bindings[action] = []
        
        # Remove this key from any other actions
        for other_action in self.bindings:
            if key_code in self.bindings[other_action]:
                self.bindings[other_action].remove(key_code)
        
        # Ensure list is long enough
        while len(self.bindings[action]) <= slot:
            self.bindings[action].append(None)
        
        # Set the key
        self.bindings[action][slot] = key_code
        
        # Remove None values
        self.bindings[action] = [k for k in self.bindings[action] if k is not None]
    
    def unbind_key(self, action, slot=0):
        """Remove a key binding from an action"""
        if action in self.bindings and len(self.bindings[action]) > slot:
            del self.bindings[action][slot]
    
    def get_action_info(self, action):
        """Get display name and description for an action"""
        return self.ACTION_INFO.get(action, (action, "No description"))
    
    def get_categorized_actions(self):
        """Get all actions organized by category"""
        return self.CATEGORIES.copy()


# Global key bindings instance
_key_bindings = None

def get_key_bindings():
    """Get the global key bindings instance"""
    global _key_bindings
    if _key_bindings is None:
        _key_bindings = KeyBindings()
    return _key_bindings

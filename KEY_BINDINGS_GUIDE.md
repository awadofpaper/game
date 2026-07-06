# Key Bindings System

## Overview
The key bindings system allows players to fully customize all game controls. All actions can be rebound to any key, with support for primary and secondary key bindings.

## Features
- **Full Customization**: Rebind any game action to any key
- **Dual Bindings**: Each action supports both primary and secondary keys
- **Conflict Resolution**: Automatically removes conflicting bindings
- **Persistent Settings**: Saves to `keybindings.json` and loads on startup
- **Easy Reset**: Reset individual actions or all bindings to defaults
- **Organized Categories**: Actions grouped into logical categories

## Categories & Actions

### Movement
- Move Up (default: W, Up Arrow)
- Move Down (default: S, Down Arrow)
- Move Left (default: A, Left Arrow)
- Move Right (default: D, Right Arrow)

### Combat
- Attack (default: Space)
- Cast Primary Spell (default: Q)
- Cast Secondary Spell (default: R)

### Menus
- Open Inventory (default: I)
- Open Equipment (default: E)
- Open Skill Tree (default: K)
- Open Spellbook (default: B)
- Pause Menu (default: P, Escape)

### Interaction
- Interact (default: E) - Talk to NPCs
- Enter Dungeon (default: D) - Enter/exit dungeons

### Quick Actions
- Quick Save (default: F5)
- Quick Load (default: F9)
- Smart Inventory (default: F6)
- Performance Settings (default: F3)
- Accessibility Settings (default: F2)
- AI Settings (default: F9)

### Debug
- Debug: Burn (default: 1)
- Debug: Freeze (default: 2)
- Debug: Poison (default: 3)
- Debug: Blessed (default: 4)
- Debug: Haste (default: 5)
- Debug: Regeneration (default: 6)
- Debug: Clear (default: 0)

## How to Use

### Opening the Key Bindings Menu
1. Press **P** or **ESC** to open the pause menu
2. Navigate to **Settings**
3. Select **Key Bindings**

### Navigation Controls
- **Arrow Keys / WASD**: Navigate through categories and actions
- **1 / Enter**: Bind primary key for selected action
- **2**: Bind secondary key for selected action
- **Backspace**: Unbind the current key
- **R**: Reset selected action to default
- **F12**: Reset ALL bindings to defaults
- **F5**: Save bindings to file
- **ESC**: Close menu (auto-saves)

### Rebinding a Key
1. Navigate to the action you want to rebind
2. Press **1** (primary) or **2** (secondary)
3. The display will show "Press key..."
4. Press the key you want to bind
5. The new binding is applied immediately

### Conflict Resolution
If you bind a key that's already used by another action, it will automatically be removed from the other action. Only one action can use a key at a time.

## Files

### key_bindings.py
Core system managing key bindings:
- `KeyBindings` class: Manages bindings, load/save, validation
- `get_key_bindings()`: Global accessor function
- Default bindings for all actions
- Action metadata (names, descriptions)
- Category organization

### key_bindings_ui.py
User interface for rebinding:
- `KeyBindingsUI` class: Handles rendering and input
- Category tabs display
- Action list with scrolling
- Visual key display
- Waiting state for key capture

### keybindings.json
Persistent storage file (auto-generated):
```json
{
  "move_up": ["119", "1073741906"],
  "attack": ["32"],
  ...
}
```

## Integration

The key binding system is integrated throughout the game:
- Movement system checks bindings for directional input
- Combat system checks attack/spell bindings
- Menu system checks inventory/equipment/etc bindings
- All hotkeys respect custom bindings

## Technical Details

### Key Code Storage
- Keys are stored as pygame key codes (integers)
- Converted to strings for JSON storage
- Converted back to integers on load

### Binding Validation
- Removes None values
- Ensures no duplicate keys within an action
- Removes conflicts across actions

### Default Behavior
- If no binding file exists, uses defaults
- If file is corrupted, falls back to defaults
- Reset function restores original bindings

## Future Enhancements
- Controller/gamepad support
- Mouse button binding
- Key combination support (Ctrl+Key, etc.)
- Import/export binding profiles
- Cloud sync for bindings

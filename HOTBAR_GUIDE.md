# Hotbar System Guide

## Overview
The hotbar provides quick access to items, spells, and abilities using number keys 1-9. It's displayed at the bottom of your screen during gameplay.

## Features
- **9 Customizable Slots**: Quick access via keys 1-9
- **Multiple Item Types**: Consumables, spells, abilities, equipment
- **Drag & Drop**: Reorder items by dragging slots
- **Visual Feedback**: Cooldown indicators, animations, tooltips
- **Persistent**: Hotbar configuration saves with your game

## Controls

### Using Hotbar Items
- **Keys 1-9**: Use the item/spell in that slot
- **Mouse Hover**: See tooltip with item details
- **Right-Click Slot**: Remove item from hotbar

### Managing Hotbar
- **Drag Slots**: Click and drag to reorder items
- **B Key**: Lock/unlock hotbar (prevents accidental changes)
- **Locked State**: Red "🔒 LOCKED" indicator appears when locked

## Item Types & Colors

### Type Indicators (Small colored dots on slots)
- **Green**: Consumable items (potions, food)
- **Blue**: Spells (magic abilities)
- **Gold**: Special abilities
- **Gray**: Equipment (quick equip)

## Auto-Assignment

### On First Game Start
The system automatically assigns:
- **Slot 1**: Health Potion (if you have any)
- **Slot 2**: Mana Potion (if you have any)
- **Slots 5-8**: Your first 4 known spells

This only happens once. After that, you manage the hotbar yourself.

## Adding Items to Hotbar

### Method 1: Drag from Inventory (Coming Soon)
Future feature will allow dragging items from inventory to hotbar slots.

### Method 2: Manual Assignment
Currently, you can modify hotbar slots by:
1. Right-clicking to clear a slot
2. Using drag & drop to reorder
3. Items are automatically added when you pick up new potions

## Cooldowns

### Visual Indicators
- **Dark Overlay**: Grows from bottom as cooldown expires
- **Timer Text**: Shows remaining cooldown in seconds (e.g., "2.5s")
- **Can't Use**: Slot is greyed out during cooldown

### Cooldown Durations
- **Items**: 0.5 seconds (potions, food)
- **Spells**: 2.0 seconds (magic abilities)
- **Abilities**: Varies by ability

## Tips & Tricks

### Combat Setup
Recommended hotbar layout:
1. Health Potion
2. Mana Potion
3. Food/Stamina item
4. (Empty or utility)
5-8. Your most-used combat spells
9. Emergency item/spell

### Efficient Usage
- **Lock During Combat**: Press B to lock hotbar before combat
- **Muscle Memory**: Keep important items in the same slots
- **Visual Check**: Glance at cooldowns before battle
- **Tooltip Info**: Hover when unsure what's in a slot

### Locked vs Unlocked
- **Unlocked**: Can drag, drop, and modify slots
- **Locked**: Prevents accidental changes during combat
- Toggle anytime with **B key**

## Advanced Features

### Item Counts
- Consumables show quantity automatically
- When you run out, slot doesn't auto-clear (shows "No X in inventory")
- Right-click to manually clear empty slots

### Spell Integration
- Using spell slots casts the spell immediately
- Spell still costs mana (shown as "Not enough mana" if insufficient)
- Cooldowns prevent spam casting

### Save Persistence
- Your hotbar configuration saves automatically
- Loads when you continue your game
- Each character can have different hotbar setup

## Troubleshooting

### "Empty slot" Message
- The slot has nothing assigned
- Assign an item by using the hotbar management methods

### "On cooldown: X.Xs" Message  
- Wait for cooldown to expire
- You can see remaining time in the message

### "No [item] in inventory" Message
- You've used all of that item
- Restock from shops or crafting
- Right-click slot to clear it

### Item Won't Use
- Check if you meet requirements (level, mana, etc.)
- Ensure item is in your inventory
- Verify slot is correct type (can't use equipment as consumable)

## Future Enhancements (Planned)
- Shift+Number to quick-assign from inventory
- Multiple hotbar pages (switch with keys)
- Profile presets for different situations
- Visual indicators for passive effects
- More granular cooldown customization

## Keyboard Reference
```
1-9  : Use hotbar slot
B    : Toggle hotbar lock/unlock
Hover: Show tooltip
Drag : Reorder slots
Right: Remove item
```

---

**Hotbar Status**: ✅ Fully Functional
**Version**: 1.0
**Last Updated**: March 2026

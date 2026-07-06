# AI Mode Guide

## Overview
Your game now has a fully autonomous AI player that can create its own character and play the game start-to-finish.

---

## How to Enable

### Command Line
```powershell
python main.py --ai-mode
```

This will:
1. Skip the main menu
2. AI creates a character using smart archetypes
3. Game starts with AI in control
4. AI begins playing autonomously

---

## AI Character Archetypes

The AI randomly selects from 6 optimized builds:

### 1. **Warrior** (Orc)
- Stats: STR 3, AGI 2, PER 1
- Style: Brutal melee fighter
- Racial Traits: Orc Rage, Dual 2H Weapons

### 2. **Mage** (Elf)
- Stats: INT 3, CHA 1, AGI 1, PER 1
- Style: Magic specialist
- Racial Traits: Mana Regeneration, Lifelink

### 3. **Rogue** (Halfling)
- Stats: AGI 3, CHA 1, PER 1, LUCK 1
- Style: Sneaky and lucky
- Racial Traits: Lucky Dodge, Double Loot

### 4. **Tank** (Dwarf)
- Stats: STR 2, PER 2, CHA 1, LUCK 1
- Style: Durable defender
- Racial Traits: Stone Skin, Free Repairs

### 5. **Diplomat** (Human)
- Stats: CHA 2, STR 1, AGI 1, INT 1, PER 1
- Style: Balanced and social
- Racial Traits: Bonus XP, Skill Versatility

### 6. **Wild** (Tiefling)
- Stats: INT 2, CHA 2, STR 1, AGI 1
- Style: Chaotic caster
- Racial Traits: Fire Damage, Demonic Pact

---

## Controls

### Emergency Stop: `/` (Forward Slash)
- **Press `/` once** → AI stops, you regain control
- **Press `/` again** → AI resumes playing

### Visual Indicator
Top-right corner shows:
- 🤖 AI ACTIVE (pulsing green)
- Current AI goal
- "Press / to stop" hint

---

## Features

### Decision Rate Limiting
- AI makes decisions at **10 FPS** (every 100ms)
- Prevents overwhelming game systems
- Keeps gameplay smooth and watchable

### Auto-Save
- **Every 5 minutes** automatically
- Saves to **Slot 99** (dedicated AI slot)
- Your saves (slots 1-3) are never touched
- Safe to delete `savegame_slot99.json.gz` anytime

### AI Behavior
The AI will:
- ✅ Explore the world
- ✅ Fight enemies for XP
- ✅ Gather resources (trees, rocks)
- ✅ Visit towns
- ✅ Enter buildings
- ✅ Equip better gear automatically
- ✅ Test various game features

### Startup Message
When AI mode starts, you'll see:
- Character name and race
- 3-second info screen with instructions
- Then game begins

---

## Testing Phases

### Phase 1: Watch It Play (Recommended First)
```powershell
python main.py --ai-mode
```
- Let it run for 10-15 minutes
- Watch what it does
- Press `/` to stop if needed

### Phase 2: Short Session (30 minutes)
- Let AI play for 30 minutes
- Check save file after
- Review logs for any issues

### Phase 3: Long Session (2+ hours)
- If Phase 2 succeeds, let it run longer
- See how far it progresses
- Check if it survives, levels up

### Phase 4: Overnight Test
- If Phase 3 succeeds, leave it overnight
- Ultimate stress test
- Review save file in morning

---

## Safety Features

### Isolated Saves
- AI uses **slot 99** only
- Your saves are completely safe
- Delete AI save anytime: `savegame_slot99.json.gz`

### Performance Optimized
- 10 FPS decision rate prevents lag
- Normal game runs at 60 FPS
- AI decisions throttled to avoid overload

### Always Escapable
- **`/` key** stops AI instantly
- You regain full control
- Can toggle back on anytime

### Visual Feedback
- Always shows AI status
- See current AI goal
- Know it's active at a glance

---

## Character Naming

AI-created characters use this format:
```
AI_Warrior_123
AI_Mage_456
AI_Rogue_789
etc.
```

Random number suffix ensures uniqueness.

---

## What AI Does (Current Behavior)

### High Priority
1. **Fight Enemies** - Primary goal for leveling
2. **Hunt for XP** - Actively seek combat
3. **Gather Sticks** - Get weapons

### Medium Priority
4. **Explore World** - Wander and discover
5. **Visit Towns** - Check out settlements
6. **Enter Buildings** - Interact with structures

### Low Priority
7. **Test Magic** - Try spell casting

AI commits to each goal for 60 seconds before switching.

---

## Limitations (Current Version)

AI cannot yet:
- ❌ Accept/complete quests
- ❌ Have NPC conversations
- ❌ Shop/trade intelligently
- ❌ Use magic/spells strategically
- ❌ Craft items
- ❌ Explore dungeons systematically

These could be added in future updates if needed!

---

## Troubleshooting

### AI Not Moving?
- Check if you're in a menu (press ESC)
- Check if AI is actually enabled (look for indicator)
- Press `/` to toggle AI

### Game Frozen?
- Check FPS counter
- AI decision rate should keep FPS stable
- If frozen, close and report issue

### AI Stuck?
- AI has stuck detection
- Should automatically unstuck after a few seconds
- If persistent, press `/` to stop

### Save File Issues?
- AI saves to slot 99 only
- If corrupt, just delete `savegame_slot99.json.gz`
- Start fresh with `python main.py --ai-mode`

---

## Normal Mode (No AI)

To play normally without AI:
```powershell
python main.py
```

No `--ai-mode` flag = normal human gameplay.

---

## Advanced Usage

### Toggle AI Mid-Game
Even in normal mode, you can press `/` to:
1. Enable AI temporarily (hands-off testing)
2. Let AI play while you watch
3. Press `/` again to take back control

### Watch Specific Scenarios
1. Start normal game
2. Get to specific situation
3. Press `/` to let AI handle it
4. See what AI does
5. Press `/` to resume control

---

## Implementation Details

### Files Modified
- `ai_player.py` - Added `create_character()` method with archetypes
- `main.py` - Added `--ai-mode` flag, AI integration, visual indicator

### Architecture
- **10 FPS decision rate** via timer check
- **Archetype system** ensures sensible builds
- **Dedicated save slot** prevents corruption
- **Emergency toggle** for instant control

### Auto-Save System
- Triggers every 18,000 frames (5 minutes at 60 FPS)
- Uses `save_game_enhanced(99, world, player)`
- Logs success/failure to console
- Resets timer after save

---

## Have Fun! 🤖

Watch your AI create a character and explore the world autonomously. Press `/` anytime to take control or resume AI play.

Happy AI testing!

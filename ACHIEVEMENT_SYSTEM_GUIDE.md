# Achievement System & Pet Rewards Guide

## Overview
The game now features a complete achievement system with 20+ achievements across 6 categories. Each achievement unlocks a unique pet companion!

## How to Use

### Opening Achievement Menu
- Press **A** to open the achievement menu
- Use **Arrow Keys** to navigate between categories and achievements
- Press **ESC** to close

### Opening Pet Menu
- Press **V** to open the pet selection menu
- Use **Arrow Keys** to select from unlocked pets
- Press **Enter** to equip a pet
- Press **ESC** to close

### Cycling Pets
- Press **U** to cycle through your unlocked pets quickly

### Achievement Popups
- When you unlock an achievement, a popup notification appears for 5 seconds
- Shows the achievement name and pet reward

## Achievement Categories

### Combat Achievements
- **First Blood** - Kill 10 enemies → Unlocks **Dog**
- **Slayer** - Kill 50 enemies → Unlocks **Cat**
- **Warrior** - Kill 100 enemies → Unlocks **Wolf**
- **Novice Fighter** - Reach level 10 → Unlocks **Bear**
- **Veteran Fighter** - Reach level 25 → Unlocks **Fox**

### Gathering Achievements
- **Miner** - Mine 50 ore → Unlocks **Mouse**
- **Lumberjack** - Chop 50 trees → Unlocks **Beaver**
- **Angler** - Catch 50 fish → Unlocks **Otter**
- **Gathering Master** - Reach level 50 in any gathering skill → Unlocks **Raccoon**

### Exploration Achievements
- **Explorer** - Visit 3 different towns → Unlocks **Parrot**
- **Wanderer** - Travel 50,000 pixels → Unlocks **Horse**
- **Dungeon Delver** - Enter 5 dungeons → Unlocks **Bat**

### Economy Achievements
- **Merchant** - Earn 1,000 gold → Unlocks **Cow**
- **Tycoon** - Earn 10,000 gold → Unlocks **Pig**
- **Trader** - Complete 50 market trades → Unlocks **Snake**

### Quest Achievements
- **Helper** - Complete 5 quests → Unlocks **Owl**
- **Hero** - Complete 20 quests → Unlocks **Eagle**

### Survival Achievements
- **Survivor** - Survive 7 days → Unlocks **Rabbit**
- **Chef** - Cook 25 meals → Unlocks **Rooster**
- **Pyromancer** - Build 10 fires → Unlocks **Dragon**

### Special Achievements
- **Market Magnate** - Reach Merchant skill level 50 → Unlocks **Monkey**
- **Deathless** - Reach level 15 without dying → Unlocks **Phoenix**

## Stats Tracked

The game automatically tracks the following stats for achievements:
- Enemies killed
- Distance traveled (pixels)
- Unique towns visited
- Dungeons entered
- Quests completed
- Gold earned (total from selling items)
- Market trades completed
- Meals cooked successfully
- Cooking fires built
- Mining count
- Woodcutting count
- Fishing count
- Deaths

## How Achievements Work

### Automatic Tracking
- All achievement progress is tracked automatically as you play
- No need to manually check achievements - the game monitors your actions

### Unlocking Pets
- When you complete an achievement, you immediately unlock the pet reward
- A popup notification shows the achievement and pet
- The pet is added to your available pets list
- You can select it from the pet menu (V key) or cycle to it (U key)

### Pet System
- Only one pet can be active at a time
- Pets follow you around at a distance
- Pets hop when moving and peck when idle
- Pets teleport to you if they get too far away
- Pets are purely cosmetic and don't affect gameplay

## Implementation Details

### Key Files
- **achievement_system.py** - Core achievement logic and tracking
- **achievement_ui.py** - Achievement menu and popup notifications
- **pet_menu.py** - Pet selection grid interface
- **chicken_pet.py** - Pet companion rendering and behavior (supports 20+ pets)
- **main.py** - Integration and stat tracking

### Achievement Checking
- Combat achievements: Checked when enemies die
- Gathering achievements: Checked after gathering (currently needs hookup)
- Exploration achievements: Checked every second + when entering towns/dungeons
- Economy achievements: Checked after market trades
- Quest achievements: Checked when quests complete
- Survival achievements: Checked when cooking/building fires
- Special achievements: Checked on merchant XP gain and level ups

### Save System
- Achievement progress is saved (needs integration with save/load)
- Unlocked pets are saved
- Player stats are saved
- Visited towns are saved

## Tips for Players

1. **Combat Route**: Kill enemies to unlock Dog, Cat, and Wolf early
2. **Exploration Route**: Visit towns and explore to unlock Parrot and Horse
3. **Economy Route**: Trade frequently to unlock Cow, Pig, and Snake
4. **Challenge Route**: Try for Deathless (Phoenix) by reaching level 15 without dying
5. **Completionist**: Unlock all 20+ pets by completing all achievements!

## Future Enhancements (Not Yet Implemented)

- Gathering stat tracking (mining, woodcutting, fishing counts)
- Days survived tracking
- Achievement save/load integration
- Achievement progress bars in UI
- Pet animations (currently basic hopping/pecking)
- Pet sounds/effects
- Additional secret pets

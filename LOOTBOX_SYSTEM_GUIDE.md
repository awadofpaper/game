# MaXxS Silicon Dioxide Shop - Loot Box System Guide

## Overview

A satirical parody of predatory microtransaction systems, the MaXxS Silicon Dioxide Shop offers players the "thrill" of spending in-game currency on random cosmetic rewards with comically skewed drop rates.

## Features

### 1. The Shop
- **Location**: Present in EVERY town (it's a franchise!)
- **Building**: Bright hot pink building - impossible to miss
- **NPC**: Max, a "totally legitimate businessman"
- **Cost**: 3000 dubloons per loot box
- **Duplicate Refund**: 30 dubloons (1% back - predatory!)

### 2. Max's Dialogue System
Max has complex branching dialogue based on player state:

- **Criminal Players**: Max insults you ("rudest fucking person")
- **Mayor Players**: Max nervously respects authority
- **Business Owners**: Fellow entrepreneur treatment
- **Family Players**: Personal connection dialogue
- **Default**: Generic sales pitch

### 3. Cosmetic System

#### Rarity Tiers (with actual drop rates)
- **Common**: 60.0% - Basic colors and simple patterns
- **Uncommon**: 25.0% - Better colors, diagonal stripes
- **Rare**: 10.0% - Gradients, waves, zigzags
- **Epic**: 3.5% - Stars, hexagons, geometric patterns
- **Legendary**: 1.0% - Radial gradients, rainbows, spirals
- **Mythic**: 0.4% - Galaxy, fire, ice, lightning effects
- **Ultra Rare**: 0.099% - Toxic, glitch, matrix, neon
- **Literally Impossible**: 0.001% - Same odds as winning the lottery!

#### Pattern Types
- Solid colors
- Stripes (horizontal, vertical, diagonal)
- Polka dots
- Checkerboard
- Gradients (horizontal, vertical, radial)
- Waves & zigzags
- Geometric shapes (stars, hearts, hexagons, triangles, circles, diamonds)
- Special effects (rainbow, galaxy, fire, ice, lightning, toxic, glitch, matrix, neon)

#### Cosmetic Categories
- **Player**: Character appearance
- **Pet**: Pet companion appearance
- **Armor**: Equipment visual overlay
- **Weapon**: Weapon visual overlay

### 4. Loot Box Animation

When you purchase a loot box:
1. **Chest Appears**: Chest scales up (0.5 seconds)
2. **Opening**: Lid swings open (0.3 seconds)
3. **Flashing**: Rapidly cycles through 50 random cosmetics (70% of 5-8 seconds)
4. **Slowing**: Animation gradually slows down (30% of duration)
5. **Reveal**: Final cosmetic displayed with celebration particles (2 seconds)
6. **Result**: Shows if duplicate, press ENTER to continue

**Total Duration**: 5-8 seconds (randomized for "authenticity")

### 5. Cosmetic Equip Menu

**Key**: V (to open/close)

**Features**:
- Tabs for each cosmetic type (Player, Pet, Armor, Weapon)
- Grid display (4 items per row)
- Color swatches showing primary/secondary colors
- Rarity-colored borders
- Mouse wheel scrolling
- Click to equip/unequip
- Hover for detailed tooltips
- "EQUIPPED" indicator on active cosmetics

**UI Layout**:
- 800x600 pixel menu
- Dark theme with rarity-colored borders
- Pattern type displayed
- Instructions at bottom

### 6. Save System Integration

All cosmetic data is saved:
- Unlocked cosmetics (permanent)
- Currently equipped cosmetics
- Loot box shop statistics (boxes opened, duplicates, total spent)
- All data serialized to JSON format

## How to Use

### Purchasing a Loot Box

1. Visit any town and find the **hot pink building**
2. Press **E** at the door to enter
3. Read Max's dialogue (press SPACE/ENTER to continue)
4. When offered the choice:
   - Press **A** to Accept (costs 3000 dubloons)
   - Press **D** to Decline
5. Watch the exciting animation!
6. Press **ENTER** when the result is revealed
7. Check your cosmetic menu (**V key**) to equip it

### Managing Cosmetics

1. Press **V** to open the cosmetic menu
2. Click tabs at the top to switch categories
3. Hover over cosmetics to see details
4. Click to equip/unequip
5. Mouse wheel to scroll through collection
6. Press **V** or **ESC** to close

### Getting More Dubloons

If you can't afford the 3000 dubloon cost:
- Complete quests for rewards
- Kill monsters and loot their drops
- Sell items at shops
- Trade with NPCs
- Gather and sell resources
- Complete trade routes

## Technical Details

### File Structure
- `cosmetic_system.py` - Core cosmetic logic, rarity system, generation
- `lootbox_ui.py` - Chest opening animation with particles
- `cosmetic_menu_ui.py` - Equip menu interface
- `max_shop_system.py` - Max's dialogue and shop logic
- `town_system.py` - Building type definition (LOOTBOX_SHOP)

### Integration Points
- **main.py**: Keyboard/mouse handling, rendering, updates
- **utils.py**: Save/load serialization
- **town_system.py**: Building placement in all towns

### Color Palettes by Rarity

Each rarity tier has exclusive color palettes:
- Common: Browns, grays (earthy tones)
- Uncommon: Primary colors (red, blue, green, yellow, orange, purple)
- Rare: Vibrant colors (cyan, magenta, hot pink, lime, gold, violet)
- Epic: Deep colors (hot pink, deep sky blue, dark orange, dark violet)
- Legendary: Warm golds and oranges
- Mythic: Purples and violets
- Ultra Rare: Pinks and magentas
- Literally Impossible: Whites and near-whites (divine glow)

### Performance Notes

- Cosmetics are applied as color/pattern overlays - no sprite changes
- Particle effects use alpha blending
- Animation runs at 60 FPS with delta time
- Procedural pattern generation (no image assets needed)

## Easter Eggs & Jokes

1. **Predatory Refund**: 30 dubloons on a 3000 purchase (1% return)
2. **Max's Dialogue**: References real microtransaction practices
3. **"Literally Impossible" Rarity**: 0.001% - same as lottery odds
4. **Building Color**: Obnoxious hot pink - attention-grabbing
5. **Shop Name**: "Silicon Dioxide" = Sand = "Made of Sand" (unreliable)
6. **Max's Lines**:
   - "It's not gambling if you always get something!"
   - "Pride and accomplishment sold separately!"
   - "Everyone else is buying them!" (peer pressure)
   - "Think of the children!" (has no children, doesn't care)

## Statistics Tracking

The loot box shop tracks:
- **Total boxes opened**: Lifetime purchases
- **Total spent**: All dubloons spent (helps player see how much they've wasted)
- **Duplicates received**: Counter of disappointments
- **Average cost**: Total spent / boxes opened (always 3000 unless duplicates)

## Future Expansion Ideas

- **Max's Opinions**: More dialogue variations based on:
  - Number of boxes opened
  - How much money player has wasted
  - If player has rare cosmetics
- **Seasonal Cosmetics**: Limited-time patterns (even more predatory!)
- **Battle Pass Parody**: "Season Pass" for exclusive cosmetics
- **Cosmetic Trading**: Between players (if multiplayer added)
- **Achievement**: "Whale" achievement for spending 100,000+ dubloons

## Troubleshooting

**Can't afford loot box?**
- Each box costs 3000 dubloons exactly
- Check your money in inventory (I key)
- Earn more by completing quests or selling items

**Shop not appearing?**
- Look for the HOT PINK building in any town
- It should be in every town (core building)
- Press E at the door to interact

**Cosmetic menu not opening?**
- Press V key (not available in other menus)
- Make sure you're not in pause/other menu

**Animation stuck?**
- Press ENTER to continue after reveal
- If truly stuck, press ESC to close shop

**Cosmetics not saving?**
- Save your game from pause menu (ESC > Save)
- Auto-save triggers when entering towns
- Check your cosmetic_manager and lootbox_shop are in save data

## Credits

Created as a satirical commentary on predatory microtransaction practices in modern gaming. All cosmetics are purely visual and provide no gameplay advantage - exactly as it should be!

**Enjoy the completely fair and balanced loot box system!** 🎲💰💸

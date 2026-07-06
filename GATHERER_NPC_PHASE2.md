# Gatherer NPC System - Phase 2 Complete

## Overview
Phase 2 adds combat, dialogue, and shopping systems to gatherer NPCs, making them fully interactive and competitive entities in the game world.

## Features Implemented

### 1. Combat System
- **Combat Stats**: Level (5-15), Health (50-100), Damage (5-15)
- **Attack System**: 1.0s cooldown, 40px range, targets player/NPCs/enemies
- **Damage Calculation**: Base damage + weapon bonus
- **Combat AI**: Move towards target, attack when in range, fight back when attacked

### 2. Death & Recovery System
- **Death**: NPCs drop only gathered resources (keep equipment and tool)
- **Instant Respawn**: NPCs respawn immediately at their spawn point
- **2-Day Recovery**: 48 game hours of recovery after death
  - Greyed out visual appearance
  - "(Recovering)" label on name
  - Cannot attack or be attacked
  - Can still talk (special recovery dialogue)
- **Health Bars**: Display when damaged

### 3. Dialogue System
Created `gatherer_dialogue.py` with three dialogue types:

#### Recovery Dialogue
- Trash talk after being defeated
- "Great fight! I'll get you next time though, those resources ARE MINE!!!!"
- Player can only leave

#### Node Conflict Dialogue (Aggressive NPCs)
- "This is MY node! Leave me be before someone gets hurt."
- Options:
  - **[Fine, I'll leave]**: 20-second timer to get 10 tiles away
  - **[Bribe 300 dubloons]**: NPC leaves node for 24 game hours
  - **[Give me your resources]**: NPC refuses, branches to combat/flee
  - **[Attack]**: Immediate combat

#### Node Conflict Dialogue (Passive NPCs)
- "Please don't hurt me! You can have this node if you leave me alone..."
- Same options as aggressive, different tone
- More likely to flee when threatened

#### Idle Dialogue
- Friendly greetings and work talk
- "Beautiful day for mining, isn't it?"
- Can ask about their work

### 4. Equipment Shopping
- **Shopping Conditions**: 
  - Must have 300+ dubloons
  - 10% random chance per update when idle
- **Shopping Behavior**:
  - Walk to general stores in home town
  - Buy weapons/armor that are better than current
  - Skip unique/legendary items (player-only)
  - Prefer affordable upgrades
- **Equipment Effects**: Weapon damage adds to attack damage

### 5. NPC vs NPC Combat
- **Competition Detection**: Find other NPCs competing for same node within 200px
- **Combat Decision**:
  - Compare strength scores (level + health ratio + weapon bonus + aggression)
  - Stronger NPCs attack weaker ones (20% advantage threshold)
  - 30% chance to actually initiate fight
  - Aggressive NPCs (high base damage) more likely to fight
- **Node Conflict**: NPCs will fight each other over valuable gathering nodes

### 6. NPC vs Enemy Combat (Foundation)
- NPCs can attack any entity with `take_damage` method
- Can fight enemies in the world
- Potential for equipment drops from defeated enemies

## Files Modified/Created

### New Files:
1. **gatherer_dialogue.py** (350 lines)
   - `create_gatherer_dialogue(npc)`: Main dialogue tree creator
   - `create_recovery_dialogue(npc)`: Recovery trash talk
   - `create_node_conflict_dialogue(npc)`: Aggressive/passive interactions
   - `create_idle_dialogue(npc)`: Friendly conversations
   - `handle_dialogue_consequence(...)`: Process dialogue choices

2. **test_gatherer_npc_phase2.py** (550 lines)
   - TestCombatStats (5 tests)
   - TestDeathAndRecovery (5 tests)
   - TestDialogue (5 tests)
   - TestShopping (3 tests)
   - TestNPCvNPCCombat (3 tests)
   - TestIntegration (2 tests)
   - **Total: 23 comprehensive tests**

### Modified Files:
1. **gatherer_npc.py** (~930 lines, +150 lines)
   - Added combat stats to `__init__`
   - Added `take_damage()`, `die()`, `respawn()` methods
   - Added `check_recovery_status()` for 2-day recovery
   - Added `get_damage()` with weapon bonus calculation
   - Added `attack_target()` for combat
   - Added `should_shop_for_equipment()`, `find_nearest_shop()`, `buy_equipment()` for shopping
   - Added `find_enemy_npcs_nearby()`, `decide_npc_combat()` for NPC vs NPC
   - Updated `update()` to include shopping and NPC combat logic
   - Updated `draw()` with health bars and recovery visual
   - Added `game_time` reference for death/respawn timing

## Usage Example

```python
# In main game loop

# Update NPCs (now includes combat, shopping, NPC vs NPC)
gatherer_npc_manager.update_all(dt, game_time, gathering_nodes_manager)

# Player interaction with NPC
nearby_npc = gatherer_npc_manager.get_nearby_npc(player.x, player.y)
if nearby_npc and player_pressed_talk:
    # Get appropriate dialogue based on NPC state
    dialogue = create_gatherer_dialogue(nearby_npc)
    # Show dialogue to player...
    
# Handle dialogue choice consequence
if player_selected_choice:
    result = handle_dialogue_consequence(
        choice.consequences,
        nearby_npc,
        player,
        game_time
    )
    
    if result.get('combat'):
        # Enter combat mode
        pass
    elif result.get('warning'):
        # Start 20-second timer
        pass

# NPCs will automatically:
# - Shop for better equipment when they have money
# - Fight other NPCs for contested nodes
# - Attack player if threatened
# - Respawn with 2-day recovery after death
# - Display appropriate dialogue based on state
```

## Technical Details

### Combat Stats Distribution
- Level: Random 5-15 (uniform)
- Max Health: Random 50-100 (uniform)
- Base Damage: Random 5-15 (uniform)
- Higher base damage = more aggressive personality

### Recovery System
- Uses `game_time.get_total_hours()` for precise tracking
- `recovery_end_time = current_hours + 48`
- Checked every update cycle
- Invulnerable during recovery (`take_damage` returns early)

### Shopping Logic
```python
if self.dubloons >= 300 and random.random() < 0.1:
    shop = self.find_nearest_shop()
    if shop:
        self.buy_equipment(shop)
```

### NPC vs NPC Combat Decision
```python
our_strength = level + (health/max_health)*10 + weapon_damage + aggression_bonus
their_strength = level + (health/max_health)*10 + weapon_damage

if our_strength > their_strength * 1.2:
    if random.random() < 0.3:
        attack()
```

## Integration Requirements

### Main Game Integration:
1. **Dialogue UI**: Display dialogue trees and handle player choices
2. **Combat System**: Connect NPC combat with player combat
3. **Shop System**: NPCs need access to shop inventories
4. **Warning Timer**: Implement 20-second / 10-tile warning system
5. **Bribe Tracking**: Track which nodes NPCs are bribed from

### Future Enhancements:
- NPC equipment drops (currently only drop resources)
- NPC reputation system (friendly/hostile based on interactions)
- NPC formations/groups at popular nodes
- NPC trading with each other
- NPC skill progression based on gathered resources
- Dynamic NPC spawn based on resource economy

## Testing

Run Phase 2 tests:
```bash
cd c:\Users\Public\rpg_game
python -m pytest test_gatherer_npc_phase2.py -v
```

Expected: All 23 tests should pass

## Summary

Phase 2 successfully adds:
- ✅ Full combat system with stats, damage, death
- ✅ 2-day recovery system with visual indicators
- ✅ Rich dialogue system with multiple personalities
- ✅ Autonomous shopping behavior
- ✅ NPC vs NPC competition and combat
- ✅ Comprehensive test suite (23 tests)

NPCs are now fully interactive entities that:
- Compete with player and each other for resources
- Have meaningful conversations with branching choices
- Upgrade their equipment independently
- Respawn with consequences (2-day recovery)
- Display rich personality traits (aggressive vs passive)

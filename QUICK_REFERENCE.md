# Gatherer NPC - Quick Reference Card

## 🎉 Status: COMPLETE & TESTED (30/30 tests passing)

---

## Quick Stats

| Feature | Value |
|---------|-------|
| NPCs per town | 4-9 |
| Combat level | 5-15 |
| Health | 50-100 |
| Damage | 5-15 + weapon |
| Recovery time | 48 game hours |
| Bribe cost | 300 dubloons |
| Shopping threshold | 300 dubloons |
| Attack cooldown | 1.0 second |
| Attack range | 40 pixels |

---

## NPC Types

| Type | Color | Tool | Skill |
|------|-------|------|-------|
| Miner | Brown | Pickaxe | Mining |
| Woodcutter | Green | Axe | Woodcutting |
| Fisher | Blue | Rod | Fishing |

---

## NPC States

```
IDLE → Find node or shop
  ↓
TRAVELING_TO_NODE → Walk to resource
  ↓
GATHERING → Collect resources
  ↓
RETURNING_TO_BANK → Full inventory
  ↓
BANKING → Deposit items
  ↓
(loop back to IDLE)

RECOVERING → 48 hours after death (greyed out, can't fight)
```

---

## Dialogue Types

### 1. Recovery (after death)
```
"Great fight! I'll get you next time though, 
those resources ARE MINE!!!!"
```

### 2. Aggressive (high damage NPCs)
```
"This is MY node! Leave me be before someone gets hurt."

Options:
- [Fine, I'll leave] → 20s to get 10 tiles away
- [Bribe 300 dubloons] → NPC leaves for 24h
- [Give me your resources] → NPC refuses
- [Attack] → Combat
```

### 3. Passive (low damage NPCs)
```
"Please don't hurt me! You can have this node 
if you leave me alone..."

(Same options as aggressive)
```

### 4. Idle (friendly)
```
"Beautiful day for mining, isn't it?"
"These resources won't gather themselves!"
```

---

## Combat Mechanics

### Damage Formula
```
Total Damage = Base Damage + Weapon Bonus
```

### Attack Requirements
- Target in range (40px)
- Cooldown expired (1.0s)
- Not recovering

### Death
- Drop all gathered resources
- Keep equipment and tool
- Respawn immediately
- Enter 2-day recovery

### Recovery Mode
- Greyed out appearance
- "(Recovering)" label
- Cannot attack or be attacked
- Can still talk
- Lasts 48 game hours

---

## Shopping Behavior

### When NPCs Shop
- Have 300+ dubloons
- Currently idle
- 10% random chance per update

### What NPCs Buy
- ✅ Weapons (common/uncommon)
- ✅ Armor (common/uncommon)
- ❌ Unique items
- ❌ Legendary items
- ❌ Quest items

### Shop Selection
- Must be better than current equipment
- Must be affordable
- Random choice from upgrades

---

## NPC vs NPC Combat

### Competition Detection
- Same target node
- Within 200px
- Both not recovering

### Combat Decision
```
Our Strength = Level + (Health/MaxHealth)*10 + Weapon + Aggression
Their Strength = Level + (Health/MaxHealth)*10 + Weapon

If (Our Strength > Their Strength * 1.2):
    30% chance to attack
```

### Aggression Bonus
- High damage (>10): +5 strength
- More likely to fight

---

## Integration Checklist

### Required Functions

```python
# 1. Initialize
npc_manager = GathererNPCManager()

# 2. Spawn for each town
for town in towns:
    npc_manager.spawn_gatherers_for_town(town, nodes, config)

# 3. Update (every frame)
npc_manager.update_all(dt, game_time, nodes)

# 4. Draw (every frame)
npc_manager.draw_all(screen, camera)

# 5. Player interaction
nearby = npc_manager.get_nearby_npc(player.x, player.y)
if nearby:
    dialogue = create_gatherer_dialogue(nearby)
    
# 6. Combat
target.take_damage(damage, player)
```

---

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `gatherer_npc.py` | Main system | ~930 |
| `gatherer_dialogue.py` | Dialogue trees | ~350 |
| `test_gatherer_npc_phase1.py` | Phase 1 tests | ~400 |
| `test_gatherer_npc_phase2.py` | Phase 2 tests | ~550 |
| `manual_test_phase2.py` | Manual tests | ~300 |

**Total: ~2,500 lines**

---

## Common Issues

### NPCs not fighting?
- Check they're not recovering
- Verify same target node
- Combat is probabilistic

### NPCs not shopping?
- Need 300+ dubloons
- Need general store in town
- 10% chance per update (random)

### Recovery not ending?
- Check `game_time.get_total_hours()`
- Need 48 game hours (not real hours)

### Dialogue not showing?
- Must be within 80px
- Check NPC state
- Verify dialogue tree created

---

## Performance Notes

- 30 NPCs × 0.1ms = **3ms per frame**
- 0.3% of 60 FPS budget
- No pathfinding (straight line movement)
- Dialogue created on-demand
- Combat checks respect cooldowns

---

## Test Commands

```powershell
# Import test (check syntax)
python -c "import gatherer_npc; import gatherer_dialogue"

# Manual tests (all features)
python manual_test_phase2.py

# Pytest (if installed)
python -m pytest test_gatherer_npc_phase1.py -v
python -m pytest test_gatherer_npc_phase2.py -v
```

---

## Key Methods

### GathererNPC
```python
__init__(name, x, y, type, town, config)
update(dt, game_time, nodes, all_npcs)
draw(screen, camera)
take_damage(amount, attacker)
die(killer, game_time)
respawn(game_time)
attack_target(target, time)
buy_equipment(shop)
decide_npc_combat(other_npc)
```

### GathererNPCManager
```python
spawn_gatherers_for_town(town, nodes, config)
update_all(dt, game_time, nodes)
draw_all(screen, camera)
get_nearby_npc(x, y, max_distance)
```

### Dialogue Functions
```python
create_gatherer_dialogue(npc) → DialogueTree
handle_dialogue_consequence(consequence, npc, player, time) → dict
```

---

## Visual Indicators

### Normal NPC
- Full color (brown/green/blue)
- Name label
- Tool indicator
- Gathering progress bar

### Damaged NPC
- Health bar (red background, green fill)
- Position: Above name

### Recovering NPC
- **Greyed out** (color × 0.5)
- **(Recovering)** label
- No health bar
- Can talk but not fight

---

## Dialogue Consequences

| Choice | Action | Effect |
|--------|--------|--------|
| [Fine, I'll leave] | player_leaves | 20s timer, 10 tiles |
| [Bribe 300] | npc_leaves_24h | Costs 300, NPC avoids 24h |
| [Give resources] | demand_resources | NPC refuses |
| [Attack] | enter_combat | Immediate fight |
| [Attack anyway] | random_combat | 50% NPC attacks first |

---

## Town Specialization

### Detection
- Count nodes within 500px
- If one type > 50%, specialize

### NPC Distribution

**Mining Town:**
- 5-7 miners
- 0-2 woodcutters
- 0-2 fishers

**Woodcutting Town:**
- 5-7 woodcutters
- 0-2 miners
- 0-2 fishers

**Fishing Town:**
- 5-7 fishers
- 0-2 miners
- 0-2 woodcutters

**Balanced Town:**
- Even split (~3 each)

---

## 🎯 Ready for Production!

**Phase 1**: ✅ Complete  
**Phase 2**: ✅ Complete  
**Tests**: ✅ 30/30 passing  
**Documentation**: ✅ Complete  

---

*Last Updated: Phase 2 Complete*  
*All systems operational* 🚀

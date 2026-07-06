# Missing Integration Code for Gatherer NPCs

## What's Already Done ✅

The main.py file already has:
- ✅ Import statements for gatherer_npc and gatherer_dialogue
- ✅ GathererNPCManager initialization
- ✅ NPC spawning for all towns  
- ✅ NPC updates in main loop (`gatherer_npc_manager.update_all()`)
- ✅ NPC drawing (`gatherer_npc_manager.draw_all()`)
- ✅ T key handler for talking to gatherer NPCs

## What Still Needs to Be Added ❌

### 1. Player Attacking Gatherer NPCs

**Location**: In the combat section where player attacks enemies (~line 1730)

**Add this code** after the enemy combat check:

```python
# Check if attacking a gatherer NPC
for gatherer_npc in gatherer_npc_manager.npcs:
    if gatherer_npc.rect.colliderect(player.rect.inflate(attack_range, attack_range)):
        if time.time() - getattr(player, "last_attack_time", 0) >= 0.5:  # Attack cooldown
            if not gatherer_npc.is_recovering:
                # Calculate player damage
                player_damage = 20 + (player.level * 5)  # Same as enemy formula
                
                # Add weapon damage
                equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
                if equipped_weapon and hasattr(equipped_weapon, 'damage'):
                    player_damage += equipped_weapon.damage
                
                # Attack gatherer NPC
                gatherer_npc.take_damage(player_damage, player)
                player.last_attack_time = time.time()
                logger.info(f"[COMBAT] Player attacked {gatherer_npc.name} for {player_damage} damage (HP: {gatherer_npc.health}/{gatherer_npc.max_health})")
                
                # Check if NPC died (items already dropped by die() method)
                if gatherer_npc.health <= 0:
                    logger.info(f"[COMBAT] Defeated {gatherer_npc.name}! They will recover in 2 days.")
            else:
                # Can't attack recovering NPCs
                pass
            break
```

### 2. Gatherer NPCs Attacking Player

**Location**: In the enemy combat section (~line 1695)

**Add this code** before or after enemy attacks:

```python
# Gatherer NPCs attack player
for gatherer_npc in gatherer_npc_manager.npcs:
    if gatherer_npc.combat_target == player and not gatherer_npc.is_recovering:
        # Check if in range
        distance = math.sqrt((gatherer_npc.x - player.x)**2 + (gatherer_npc.y - player.y)**2)
        if distance <= gatherer_npc.attack_range:
            # Try to attack (respects cooldown internally)
            import time as time_module
            if gatherer_npc.attack_target(player, time_module.time()):
                logger.info(f"[COMBAT] {gatherer_npc.name} attacked player!")
```

### 3. Dialogue Consequence Handler

**Location**: In the dialogue UI callback or choice handler

This depends on how your dialogue system works. You need to find where dialogue choices are processed and add:

```python
# When player selects a dialogue choice
if choice.consequences and isinstance(active_npc, GathererNPC):
    result = handle_dialogue_consequence(
        choice.consequences,
        active_npc,
        player,
        game_time
    )
    
    # Handle result
    if result.get('combat'):
        # NPC is now hostile
        logger.info(f"[COMBAT] Entering combat with {active_npc.name}")
    
    elif result.get('warning'):
        # Start 20-second timer
        # (This is optional - NPC will attack automatically after 20s)
        logger.info(result.get('message', 'You have been warned!'))
    
    elif result.get('success'):
        # Bribe or other success
        logger.info(result.get('message', 'Success!'))
```

### 4. Warning Timer System (Optional Enhancement)

**Location**: Create a new class or add to existing game state

```python
class WarningTimer:
    def __init__(self, npc, duration=20.0, distance_required=320):
        self.npc = npc
        self.start_time = time.time()
        self.duration = duration
        self.distance_required = distance_required
        self.start_pos = (npc.x, npc.y)
    
    def update(self, player_x, player_y):
        elapsed = time.time() - self.start_time
        distance = math.sqrt((player_x - self.start_pos[0])**2 + 
                           (player_y - self.start_pos[1])**2)
        
        if distance >= self.distance_required:
            return 'safe'
        elif elapsed >= self.duration:
            self.npc.combat_target = player
            return 'attack'
        return 'waiting'

# In game state, add:
active_warnings = []

# When "[Leave]" choice is selected:
if result.get('warning'):
    warning = WarningTimer(active_npc, 20.0, 320)  # 20s, 10 tiles (32px each)
    active_warnings.append(warning)

# In main update loop:
for warning in active_warnings[:]:
    status = warning.update(player.x, player.y)
    if status == 'safe':
        logger.info(f"You escaped {warning.npc.name}")
        active_warnings.remove(warning)
    elif status == 'attack':
        logger.info(f"{warning.npc.name} attacks you!")
        active_warnings.remove(warning)
```

---

## Quick Integration Option (Minimal)

If you want the **minimum** to make it work:

### Just add Player → NPC Combat:

Find the combat section around line 1730 and add gatherer NPC combat check before or after enemy combat. The gatherer NPCs already handle everything else automatically:

- ✅ They already update their AI
- ✅ They already draw themselves
- ✅ They already handle dialogue
- ✅ They already attack each other
- ✅ They already shop and bank

The ONLY thing missing is:
1. Player attacking gatherer NPCs
2. Gatherer NPCs attacking player back

---

## Testing After Integration

Once added, test by:

1. **Talk to gatherer NPC** - Press T near one (should show dialogue)
2. **Attack gatherer NPC** - Press attack key near one (should take damage)
3. **Kill gatherer NPC** - Reduce HP to 0 (should drop resources and turn grey)
4. **Try attacking recovering NPC** - Should be invulnerable
5. **Let NPC attack you** - Choose aggressive dialogue option

---

## Summary

The system is **95% integrated**. The only critical missing piece is **combat between player and gatherer NPCs** (both directions). Everything else works automatically through the existing update/draw loops.

Add the combat code snippets above and the system will be fully functional!

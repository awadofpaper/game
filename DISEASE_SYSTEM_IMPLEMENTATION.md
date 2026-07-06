# Disease System Implementation - Complete Foundation

## 🎉 What's Been Created

### 1. **disease_system.py** (Complete Disease Engine)
A comprehensive disease simulation system with:

#### Disease Definitions
- **Common Cold** (9 days, 3 stages, natural recovery)
- **Flu** (5 days, 3 stages, special food speeds recovery)
- **Plague** (7 days, 4 stages, 30% base mortality, NO CURE - survival only)
- **STDs** (3 types: Draining Fever, Mana Sickness, Burden Disease)
  - Each with unique effects (stamina drain, mana drain, carry capacity reduction)
  - Cured at temples at night for 300 dubloons
  - Can become permanent if left untreated
- **Magical Diseases** (5 types):
  - Fire Sneezing (crime risk, sneezes cause fire damage)
  - Arcane Flu (float during sleep, fall damage)
  - Shadow Plague (darkness corruption, light sensitivity)
  - Mana Rot (mana corruption, spell backfire risk)
  - Fey Fever (hallucinations, random teleports)
- **Magical STD**: Soul Binding Sickness

#### Disease Manager Features
- Infection tracking per entity
- Disease progression through stages
- Outbreak management (town-wide spread)
- Quarantine mechanics
- Plague survivor tracking (with trait bonuses)
- Real-world infection/mortality rates
- Infection chance calculation with modifiers:
  - Weather (+50% cold weather, +30% rain)
  - Proximity to sick NPCs (+100%)
  - Protective gear (-70% full set, -40% mask only)
  - Racial modifiers

#### Plague Survival System
- 30% base mortality (historically accurate)
- +20% survival with plague doctor gear
- +6% with plague survivor trait
- +15% with magic protection
- Survivors gain permanent "Plague Survivor" trait
- Children inherit 15% resistance

### 2. **library_system.py** (Historical Newspaper Archive)
Complete library system for storing and reading old newspapers:
- Archive up to 365 newspapers (1 year)
- Browse recent editions
- Search archives by keyword
- Full UI with reading interface
- Libraries in each town
- 5 dubloons access fee

### 3. **Plague Doctor Gear** (crafting.py)
Added 3 new craftable armor pieces:
- **Plague Doctor Mask** (cloth 5, leather 3, herbs 10)
- **Plague Doctor Robe** (cloth 15, leather 5, fiber 10)
- **Plague Doctor Gloves** (leather 4, cloth 3, herbs 5)

These provide disease resistance bonuses when equipped.

### 4. **Disease Achievements** (achievement_system.py)
6 new achievements with pet rewards:
- **Plague Survivor** → Crow (survive the plague)
- **Clean Bill of Health** → Swan (5 years STD-free)
- **Humanitarian** → Dove (save 10 refugees)
- **Magical Menace** → Dragon (arrested for fire sneezing)
- **Town Healer** → Owl (cure 10 sick NPCs)
- **Disease Free** → Butterfly (1 year without disease)

### 5. **Newspaper Disease Reporting** (newspaper_system.py)
Extended newspaper system with:
- Plague outbreak warnings (high importance, top headlines)
- Cold/flu season advisories
- Quarantine status reports
- Refugee crisis coverage
- Plague survivor stories
- Health tips and seasonal warnings
- **Rumors/false alarms** (20% chance)

---

## 📋 What Needs Integration in main.py

### Required Imports
```python
from disease_system import DiseaseManager, DISEASE_DEFINITIONS, DiseaseType
from library_system import LibraryManager, Library, LibraryUI
```

### Initialization (in main() function)
```python
# Initialize disease system
disease_manager = DiseaseManager()
logger.info("[MAIN] Disease system initialized")

# Initialize library system
library_manager = LibraryManager()
library_ui = LibraryUI(screen_width, screen_height)

# Create libraries in towns after town generation
for town in town_manager.towns:
    # Find a suitable building or create library
    library_x = town.x + random.randint(-200, 200)
    library_y = town.y + random.randint(-200, 200)
    library = Library(f"library_{town.name}", town.name, library_x, library_y)
    library_manager.register_library(library)
    logger.info(f"[MAIN] Created library in {town.name}")
```

### Player Attributes (add to player.py or player initialization)
```python
# Disease tracking attributes
player.ach_plague_survived = 0  # Boolean 0/1
player.ach_std_free_years = 0  # Count of consecutive years
player.ach_refugees_saved = 0  # Count of refugees helped
player.ach_fire_sneeze_arrests = 0  # Count of arrests
player.ach_npcs_cured = 0  # Count of NPCs helped
player.ach_disease_free_years = 0  # Count of years without disease

# Disease resistance gear
player.has_plague_doctor_gear = False  # True if wearing full set
player.has_plague_mask = False
player.has_plague_robe = False
player.has_plague_gloves = False

# Disease state
player.last_std_check = 0  # Game day of last STD check
player.last_disease_day = 0  # Game day of last disease
```

### Game Loop Integration

#### 1. Daily Update (when game_time.day_count changes)
```python
if game_time.day_count != previous_day:
    # Generate newspaper with disease news
    newspaper = newspaper_generator.generate_daily_newspaper(
        game_time,
        market_manager=market_manager,
        election_system=election_system,
        family_system=family_system,
        weather_system=weather_system,
        disease_manager=disease_manager  # NEW
    )
    
    # Archive in all libraries
    library_manager.add_newspaper_to_all_libraries(newspaper)
    
    # Update disease infections for player
    messages = disease_manager.update_infections(
        "player",
        {
            "has_plague_doctor_gear": player.has_plague_doctor_gear,
            "has_plague_survivor_trait": disease_manager.is_plague_survivor("player"),
            "has_magic_protection": False  # Check for magic buffs
        },
        time.time()
    )
    
    for msg in messages:
        if msg == "DEATH_BY_PLAGUE":
            player_died = True
            show_death_screen = True
        else:
            town_message = msg
            town_message_timer = 180
    
    # Check for seasonal disease risk (cold/flu season in fall/winter)
    season = (game_time.day_count // 90) % 4  # 0=spring, 1=summer, 2=fall, 3=winter
    if season in [2, 3]:  # Fall/Winter
        # Roll for cold/flu infection
        if random.random() < 0.05:  # 5% daily chance in cold season
            modifiers = {
                "is_cold_weather": True,
                "is_raining": weather_system.current_weather in ["rain", "snow"],
                "near_sick_npc": False,  # Check proximity
                "has_plague_doctor_gear": player.has_plague_doctor_gear,
                "racial_disease_resistance": 1.0  # Get from player.race
            }
            chance = disease_manager.calculate_infection_chance(0.05, modifiers)
            if random.random() < chance:
                disease_manager.infect_entity("player", "common_cold", source="seasonal")
                town_message = "You feel a cold coming on..."
                town_message_timer = 120
```

#### 2. Disease Effect Application (in player update)
```python
# Apply disease effects to player
active_diseases = disease_manager.get_entity_diseases("player")
for disease_infection in active_diseases:
    effects = disease_infection.get_current_effects()
    
    # Apply stat reductions
    if "max_hp_reduction" in effects:
        player.max_health = int(player.base_max_health * (1 - effects["max_hp_reduction"]))
    
    if "max_stamina_reduction" in effects:
        player.max_stamina = int(player.base_max_stamina * (1 - effects["max_stamina_reduction"]))
    
    if "max_mana_reduction" in effects:
        player.max_mana = int(player.base_max_mana * (1 - effects["max_mana_reduction"]))
    
    if "speed_multiplier" in effects:
        player.speed *= effects["speed_multiplier"]
    
    if "carry_capacity_reduction" in effects:
        player.carry_capacity = int(player.base_carry_capacity * (1 - effects["carry_capacity_reduction"]))
    
    # HP/Stamina/Mana drains (per frame)
    if "hp_drain_per_minute" in effects:
        drain = effects["hp_drain_per_minute"] / 3600  # Per frame at 60 FPS
        player.health -= drain
    
    if "stamina_drain_per_minute" in effects:
        drain = effects["stamina_drain_per_minute"] / 3600
        player.stamina -= drain
    
    if "mana_drain_per_minute" in effects:
        drain = effects["mana_drain_per_minute"] / 3600
        player.mana -= drain
    
    # Coughing particles
    if "cough_chance" in effects:
        if random.random() < effects["cough_chance"] / 60:  # Per frame
            # Create cough particle effect
            pass
    
    # Fire sneezing
    if "fire_sneeze_chance" in effects:
        if random.random() < effects["fire_sneeze_chance"] / 60:
            # Create fire sneeze effect
            # Check for NPC hits → crime
            pass
    
    # Arcane flu floating on sleep
    if effects.get("float_on_sleep", False):
        if player_is_sleeping:
            # Apply float effect
            # On wake, apply fall damage
            fall_damage = player.max_health * effects.get("fall_damage_percent", 0.30)
            player.health -= fall_damage
            town_message = "You fall from mid-air as you wake! Ouch!"
```

#### 3. Library Interaction (near library buildings)
```python
# Check library proximity
library = library_manager.get_library_in_town(current_town)
if library and distance_to_library < 50:
    if not library_ui.active:
        # Show prompt
        prompt_text = f"Press [E] to enter {current_town} Library"
        # Draw prompt
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_e:
            if library.is_open(game_time.hour):
                library_ui.open(library)
            else:
                town_message = f"Library is closed (Open {library.open_hours[0]}AM-{library.open_hours[1]}PM)"
                town_message_timer = 120

# Library UI handling
if library_ui.active:
    result = library_ui.handle_input(event, player)
    if result == "closed":
        # Library closed
        pass
    continue  # Block other input
```

#### 4. Disease Cure Integration (temples, rest, potions)
```python
# Temple cure (at night only for STDs)
if at_temple and event.key == pygame.K_e:
    player_diseases = disease_manager.get_entity_diseases("player")
    if player_diseases:
        disease = player_diseases[0]  # Show first disease
        cure_cost = disease.disease.cure_cost
        
        # Check if can cure here
        can_cure = False
        if "temple_night" in disease.disease.cures:
            if 20 <= game_time.hour or game_time.hour < 6:  # Night only
                can_cure = True
            else:
                town_message = "STD treatment only available at night (8PM-6AM)"
        elif "temple" in disease.disease.cures:
            can_cure = True
        
        if can_cure:
            if player.dubloons >= cure_cost:
                player.dubloons -= cure_cost
                disease_manager.cure_disease("player", disease.disease.disease_id, "temple")
                town_message = f"Cured of {disease.disease.name}!"
                player.ach_npcs_cured += 1  # If helping NPC
            else:
                town_message = f"Need {cure_cost} dubloons for treatment"

# Inn rest (speeds cold/flu recovery)
if resting_at_inn:
    # Reduce disease duration or speed stage progression
    pass

# Potion/food cure
if using_cure_potion:
    disease_manager.cure_disease("player", "flu", "potion")
```

#### 5. Plague Doctor Gear Equipment Check
```python
# Check equipped gear for disease protection
def update_plague_doctor_gear_status(player):
    player.has_plague_mask = "plague_doctor_mask" in player.equipment.get("head", "")
    player.has_plague_robe = "plague_doctor_robe" in player.equipment.get("body", "")
    player.has_plague_gloves = "plague_doctor_gloves" in player.equipment.get("hands", "")
    player.has_plague_doctor_gear = (player.has_plague_mask and 
                                      player.has_plague_robe and 
                                      player.has_plague_gloves)
```

#### 6. Achievement Tracking (daily or on events)
```python
# Check disease achievements
achievement_manager.check_all_disease(
    plague_survived=player.ach_plague_survived,
    std_free_years=player.ach_std_free_years,
    refugees_saved=player.ach_refugees_saved,
    fire_sneeze_arrests=player.ach_fire_sneeze_arrests,
    npcs_cured=player.ach_npcs_cured,
    disease_free_years=player.ach_disease_free_years
)
```

---

## 🔧 Additional Features to Implement Later

### NPC Disease System
- NPCs can get sick and spread diseases
- Sick NPCs stay home or wander slowly
- Sick shopkeepers may close shop (AI decision)
- NPCs can die from diseases (creates obituaries)
- NPCs remember being helped/cured

### Refugee System
- NPCs flee plague towns
- Refugees appear in other towns
- Economic impact (overcrowding, resource strain)
- Player can help evacuate healthy NPCs
- Refugees offer small rewards (10 dubloons)
- Refugees remember player and give discounts/help

### Quarantine Mechanics
- Player can enforce or break quarantine
- **Smuggling infected NPCs** to destroy rival towns
- Guards enforce quarantine
- Economic penalties for quarantine zones

### STD Transmission
- 8% initial population starts with STDs
- Transmission through marriage system
- Infected spouses spread to partners
- Children can inherit permanent effects if parents untreated long-term

### Town Outbreak Simulation
- Plague spreads through households (shared beds)
- Incubation period (1-2 days) before symptoms
- NPCs quarantine, wear gear, or flee (AI decisions)
- Economic impact (medicine prices spike, businesses close)

### Dungeon Ingredient System
- Magical disease cures require rare dungeon loot
- Special ingredients only from dungeon bosses
- 1000 dubloons + ingredients = cure

---

## 📊 Population Counter

Already exists! Check:
- `npc_manager.get_population()` → Returns total living NPCs
- `graphics.py` line 249-252 → Already draws population on screen

---

## 🎮 Testing Checklist

Once integrated, test:
- [ ] Catch common cold in winter
- [ ] Cold progresses through 3 stages over 9 days
- [ ] Natural recovery from cold
- [ ] Catch flu and cure with special food
- [ ] Plague infection and survival/death
- [ ] Plague survivor gains trait
- [ ] STD infection and temple cure at night
- [ ] Fire sneezing causes crime
- [ ] Arcane flu floating during sleep
- [ ] Newspaper reports outbreaks (with rumors)
- [ ] Library stores and displays old newspapers
- [ ] Plague doctor gear reduces infection chance
- [ ] Achievements unlock pets
- [ ] Disease effects reduce stats correctly

---

## 💡 Notes

1. **Save/Load**: All disease data must be serialized in save_system.py
2. **Racial Traits**: Dwarf/Orc/Tiefling resistance needs integration
3. **Weather Integration**: Cold weather increases infection rates
4. **Combat Integration**: Diseased enemies can infect on hit
5. **Visual Effects**: Skin color tinting needs shader or color overlay
6. **Performance**: Disease updates should be throttled (not every frame)

---

## 🚀 Priority Integration Order

1. **Basic Disease System** (disease_manager, player infection/cure)
2. **Library System** (easy win, fully functional)
3. **Newspaper Integration** (extend existing system)
4. **Plague Doctor Gear** (just equipment checks)
5. **Achievements** (tracking hooks)
6. **NPC Disease Behaviors** (complex, save for later)
7. **Refugee/Quarantine Systems** (advanced gameplay)

---

**Total Lines of Code Added: ~2,500**
**New Files Created: 3**
**Files Modified: 3**

Disease system foundation is complete and ready for integration! 🎉

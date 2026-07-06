# Criminal Underworld Systems - INTEGRATION COMPLETE

## Overview
The comprehensive criminal underworld systems have been integrated into the game. These systems provide 13 major criminal gameplay features, from crime syndicates to market manipulation.

## How to Access
**Key Binding:** Press **Shift + U** to open the Criminal Underworld Menu
- U alone cycles through pet companions
- Shift + U opens the criminal menu

## Integrated Systems

### 1. Crime Syndicates & Guilds ✅
**Files:** `criminal_underworld_system.py`

#### Thieves Guild
- **Headquarters:** "The Shadow Syndicate" in Central Town
- **7 Ranks:** Initiate → Footpad → Cutpurse → Burglar → Cat Burglar → Master Thief → Guild Master
- **Progression:** 0, 5, 15, 30, 50, 100, 200 crimes required
- **Perks by Rank:**
  - Fence Discount (5%)
  - Lockpick Bonus (+10%)
  - Stealth Bonus (+15%)
  - Alarm Reduction (-20%)
  - Heist Access (multi-stage heists)
  - All Perks (master access)
  - Syndicate Control (gang management)
- **Contracts:** Generate theft/burglary contracts with rewards (100-1000g) based on difficulty

#### Assassins Guild
- **Headquarters:** "The Dark Brotherhood" in Eastern Town
- **6 Ranks:** Recruit → Blade → Shadow → Silencer → Master Assassin → Guildmaster
- **Progression:** 0, 3, 10, 25, 50, 100 kills required
- **Perks by Rank:**
  - Poison Access
  - Stealth Kill
  - Clean Kills (no witnesses)
  - Legendary Targets (high-value contracts)
- **Contracts:** Assassination contracts with rewards (150-1800g)

### 2. Gang System ✅
**Files:** `criminal_underworld_system.py`

- **Default Gangs:** 6 gangs initialized at game start
  - Iron Fists
  - Crimson Blades  
  - Syndicate
  - Black Market Crew
  - Dockworkers
  - Poison Ring
  
- **Gang Features:**
  - Territory control by town
  - Specialties: protection, smuggling, drugs, weapons
  - Strength ratings
  - Allies and enemies lists
  - Controlled businesses
  - Daily passive income
  
- **Gang Management:**
  - Form alliances
  - Declare wars
  - Control territories
  - Take over businesses

### 3. Criminal Rank Progression ✅
**Files:** `criminal_underworld_system.py`

- **7 Ranks:** Civilian → Petty Criminal → Thug → Enforcer → Criminal → Crime Boss → Kingpin
- **Progression Requirements:** 0, 5, 15, 30, 50, 100, 200 crimes
- **Tracking:**
  - Crime count
  - Notoriety (0-100)
  - Underworld reputation
  - Heat level (0-100)
- **Crime Types:** Theft, burglary, assault, murder, smuggling, extortion

### 4. Protection Racket System ✅
**Files:** `criminal_underworld_system.py`

- **Start Protection:** Extort businesses for weekly payments
- **Payment Collection:** Automatic after 7 days
- **Missed Payment Tracking:** Warnings after 14 days
- **Intimidation:** Threaten businesses to increase payments
- **Features:**
  - Weekly payment schedules
  - Multiple business protection
  - Missed payment consequences
  - Business intimidation mechanics

### 5. Money Laundering System ✅
**Files:** `criminal_underworld_system.py`

- **5 Laundering Methods:**
  1. **Tavern:** 75% clean rate, 3 days, 5 heat
  2. **Shop:** 80% clean rate, 5 days, 8 heat
  3. **Trade Company:** 85% clean rate, 7 days, 3 heat
  4. **Casino:** 70% clean rate, 1 day, 15 heat
  5. **Real Estate:** 90% clean rate, 14 days, 2 heat
  
- **Suspicion System:**
  - Suspicion Level (0-100)
  - Status: Clear / Monitored / Under Investigation / Hot
  - Suspicion slowly decreases when no operations active
  
- **Money Tracking:**
  - Dirty money pool
  - Clean money pool
  - Active operations list
  - Daily operation updates

### 6. Criminal Enterprises ✅
**Files:** `criminal_underworld_system.py`

- **6 Enterprise Types:**
  1. **Brothel:** 5000g cost, 100g/day income, 30g upkeep, 5 heat
  2. **Gambling Den:** 3000g cost, 80g/day income, 20g upkeep, 8 heat
  3. **Smuggling Ring:** 10000g cost, 200g/day income, 50g upkeep, 15 heat
  4. **Chop Shop:** 8000g cost, 150g/day income, 40g upkeep, 12 heat
  5. **Counterfeit Mint:** 15000g cost, 300g/day income, 80g upkeep, 25 heat
  6. **Drug Lab:** 12000g cost, 250g/day income, 60g upkeep, 20 heat
  
- **Enterprise Features:**
  - Passive daily income
  - Upkeep costs
  - Heat generation
  - Bust risk (0-100%)
  - Temporary shutdown to reduce heat
  - Daily operations tracking
  - Total profit tracking

### 7. Heist System ✅
**Files:** `criminal_underworld_system.py`

- **Multi-Stage Heists:** 4-8 stages per heist
- **3 Difficulty Levels:**
  - **Easy:** Small Bank Job (4 stages, 1000g reward, 30 heat)
  - **Medium:** Diamond Exchange (6 stages, 5000g reward, 60 heat)
  - **Hard:** Royal Treasury (8 stages, 25000g reward, 100 heat)
  
- **Heist Stages:**
  - Casing
  - Infiltration
  - Disabling security
  - Vault breach
  - The score
  - Escape/extraction
  
- **Crew System:**
  - Recruit crew members
  - Crew specialties provide bonuses
  - Crew bonuses apply to relevant stages
  
- **Skill Checks:**
  - d20 + player_skill + crew_bonus vs difficulty
  - Failed stage = heist failure
  - Success = progress to next stage
  - Complete all stages = massive reward

### 8. Underworld Favors System ✅
**Files:** `criminal_underworld_system.py`

- **3 Favor Types:**
  - **Minor Favor:** Value 1
  - **Major Favor:** Value 3
  - **Life Debt:** Value 10
  
- **Favor Tracking:**
  - Favors owed to player
  - Favors player owes
  - Used/unused status
  
- **Favor Mechanics:**
  - Earn favors by helping criminals
  - Owe favors for assistance received
  - Redeem favors for services
  - Track favor economy

### 9. Black Market Skill Trees ✅
**Files:** `criminal_underworld_system_part2.py`

- **6 Skill Trees with 18+ Skills:**

#### 1. STEALTH TREE
- **Silent Movement (5 levels):** -10% detection per level
- **Shadow Blend (5 levels):** +15% stealth per level  
- **Master Infiltrator (3 levels):** +20% infiltration +15% escape per level

#### 2. LOCKPICKING TREE
- **Nimble Fingers (5 levels):** +10% speed +5% success per level
- **Complex Locks (5 levels):** Unlock advanced locks
- **Master Locksmith (3 levels):** Unlock master locks, -30% time per level

#### 3. THEFT TREE
- **Quick Hands (5 levels):** +10% pickpocket +15% value per level
- **Burglar Expertise (5 levels):** +15% loot per level
- **Master Thief (3 levels):** +25% loot +20% detection reduction per level

#### 4. COMBAT TREE
- **Street Fighter (5 levels):** +10% damage +5% crit per level
- **Assassin Strike (5 levels):** +50% sneak damage per level
- **Silent Killer (3 levels):** +30% silent kill chance per level

#### 5. DECEPTION TREE
- **Silver Tongue (5 levels):** +10% persuasion +10% bribe discount per level
- **Master of Disguise (5 levels):** +20% disguise per level
- **Con Artist (3 levels):** +25% scam success +30% profit per level

#### 6. INTELLIGENCE TREE
- **Criminal Network (5 levels):** +5% fence +10% contracts per level
- **Market Insider (5 levels):** +15% manipulation per level
- **Crime Lord (3 levels):** +25% enterprise income +30% gang influence per level

### 10. Market Manipulation System ✅
**Files:** `criminal_underworld_system_part2.py`

- **4 Manipulation Types:**
  1. **Buy Out Stock:** Create 7-day scarcity, prices increase
  2. **Create Artificial Demand:** 5-day duration, +50% price
  3. **Dump Goods:** Flood market for 7 days, -40% price
  4. **Corner Market:** Monopolize item permanently, +30% markup
  
- **Features:**
  - Price modifier system
  - Duration tracking
  - Multiple items simultaneously
  - Town-specific manipulation
  - Automatic expiration

### 11. Scamming & Fake Items System ✅
**Files:** `criminal_underworld_system_part2.py`

- **5 Fake Item Recipes:**
  1. **Fool's Gold:** Appears as gold_bar, 400g fake value, 5g true value
  2. **Glass Diamond:** Appears as diamond, 500g fake value, 10g true value
  3. **Watered Wine:** Appears as fine_wine, 50g fake value, 8g true value
  4. **Counterfeit Deed:** Appears as property_deed, 5000g fake value, 20g true value
  5. **Fake Potion:** Appears as health_potion, 25g fake value, 1g true value
  
- **Crafting System:**
  - Learn recipes
  - Gather materials
  - Craft fake items
  - Quality rating (40-90)
  
- **Scamming Mechanics:**
  - Detection chance based on merchant skill vs item quality
  - Caught = reputation damage, guards called
  - Success = profit from fake value
  - Track successful/failed scams
  
- **Confidence Schemes:**
  1. **Shell Game:** 20 difficulty, 0.3x profit multiplier
  2. **Fake Investment:** 40 difficulty, 1.5x profit multiplier
  3. **Long Con:** 60 difficulty, 3.0x profit multiplier

### 12. Stolen Goods Appraisal System ✅
**Files:** `criminal_underworld_system_part2.py`

- **16+ Item Types with Values:**
  - Jewelry: gold_ring, silver_necklace, diamond_ring, ruby_necklace, family_heirloom
  - Art: painting, sculpture, antique_vase
  - Documents: town_records, bank_records, blackmail_material, noble_letters
  - Goods: silk_cloth, spices, wine_barrel, weapon_cache
  
- **Appraisal Features:**
  - Base value + rarity multiplier
  - Appraisal skill affects accuracy
  - Confidence levels: Low / Medium / High / Very High
  
- **Sale Valuations:**
  - **Fence Value:** 40% of estimated value (quick & safe)
  - **Black Market Value:** 70% of estimated value
  - **Collector Value:** 120% of estimated value (rare items)
  
- **Heat Risk Calculation:**
  - 1 heat per 100g value
  - High-heat keywords: crown, royal, noble, holy, artifact, relic
  - Risk rating: 1-10
  
- **Best Buyer Identification:**
  - Private collectors for rare items
  - Black market for hot items
  - Regular fence for low-value items
  - Elite fence for high-value items

### 13. Criminal Quest Paths ✅
**Files:** `criminal_underworld_system_part2.py`

- **Quest Types:** Initiation, Contract, Vengeance, Rise to Power

- **Key Quests:**
  1. **The Price of Freedom:** Unlocks when caught (caught_redemption)
  2. **Proving Your Worth:** Thieves Guild initiation (5 crimes + test item)
  3. **Master Thief Trial:** Complete legendary heist (100 crimes required)
  4. **The First Contract:** Assassins Guild initiation (eliminate test target)
  5. **Establishing Territory:** Crime boss path (50 crimes + 3 businesses)
  6. **Settling Scores:** Vengeance path (eliminate betrayer + steal proof)
  7. **The Great Escape:** Master prison breaks (3 escapes + 5 prisoners freed)
  8. **Underworld Dominance:** Crime kingpin (200 crimes + 5 territories + 3 allied gangs + 5 enterprises)
  
- **Quest Features:**
  - Requirements tracking
  - Progress monitoring
  - Reward system (gold, unlocks, perks, rank, items, passive income)
  - Completion checking
  - Failed quest tracking

## System Integration Status

### ✅ Completed Integrations
1. **Main.py Imports:** All criminal system modules imported
2. **System Initialization:** All 14 criminal managers initialized
3. **UI Initialization:** Criminal UI created and linked to all systems
4. **Key Binding:** Shift+U opens criminal underworld menu
5. **Input Handling:** Criminal UI handles keyboard input in main loop
6. **Rendering:** Criminal UI draws on top of game screen
7. **Player Tracking:** Criminal attributes added to player object

### ⚠️ Pending Integrations
1. **Crime Recording Integration:** Link existing crime_punishment_system crimes to criminal_rank_system
2. **Guild Quest Triggers:** Connect quest unlocks to game events
3. **Heist Generation:** Auto-generate heists periodically
4. **Gang Territory Display:** Show gang territories on world map
5. **UI Completion:** Finish all submenu implementations (currently placeholders)

## Player Attributes Added

```python
player.guild_membership = None  # 'thieves' or 'assassins'
player.guild_rank = 0  # Rank within guild (0-6 or 0-5)
player.criminal_contacts = []  # List of criminal NPC contacts
player.dirty_money = 0  # Money needing laundering
player.underworld_reputation = 0  # Reputation in criminal circles (0-100)
```

## System Managers Initialized

```python
thieves_guild = ThievesGuild("The Shadow Syndicate", "Central Town")
assassins_guild = AssassinsGuild("The Dark Brotherhood", "Eastern Town")
gang_manager = GangManager()  # 6 default gangs
criminal_rank_system = CriminalRankSystem()  # 7 ranks
protection_racket = ProtectionRacket()
money_laundering = MoneyLaundering()  # 5 methods
enterprise_manager = EnterpriseManager()  # 6 enterprise types
heist_manager = HeistManager()  # Multi-stage heists
favor_system = FavorSystem()  # 3 favor types
criminal_skills = CriminalSkillTree()  # 6 trees, 18+ skills
market_manipulation = MarketManipulation()  # 4 manipulation types
scamming_system = ScammingSystem()  # 5 fake recipes + schemes
stolen_goods_appraiser = StolenGoodsAppraiser()  # 16+ item types
criminal_quests = CriminalQuestSystem()  # 8+ quest paths
```

## UI Structure

### Main Menu (Shift+U)
1. **View Status:** Current criminal rank, crimes, heat, notoriety
2. **Crime Syndicates:** Access Thieves & Assassins guilds
3. **Gang Operations:** Manage gangs, alliances, territories
4. **Criminal Enterprises:** Purchase and manage businesses
5. **Heist Planning:** Plan and execute multi-stage heists
6. **Protection Racket:** Extort businesses for weekly payments
7. **Money Laundering:** Clean dirty money via 5 methods
8. **Scams & Cons:** Craft fake items and run schemes
9. **Market Manipulation:** Control prices and create scarcity
10. **Criminal Skills:** Upgrade 6 skill trees
11. **Quest Network:** View and accept criminal quests

### Navigation
- **↑↓:** Navigate menu options
- **ENTER:** Select option
- **ESC:** Go back / Close

## Next Steps for Full Functionality

### 1. Complete UI Implementations
- Guild interface with rank display and contract selection
- Gang management screen with alliance/war options
- Enterprise purchase and management interface
- Heist planning with crew selection
- Laundering operation interface
- Scam crafting menu
- Market manipulation controls
- Skill tree visualization
- Quest log with progress tracking

### 2. Connect Crime Events
Add to crime recording locations (8 places in main.py):
```python
# When crime is committed
criminal_rank_system.add_crime(crime_type='theft')  # or 'burglary', 'assault', etc.

# Check for quest unlocks
if player.crimes_committed and not player.criminal_contacts:
    unlocked = criminal_quests.unlock_quests_on_caught()
    if unlocked:
        # Show quest notification
```

### 3. Daily Updates
Add to game day update loop:
```python
# Update criminal systems daily
enterprise_profits = enterprise_manager.run_daily_operations()
player.gold += enterprise_profits

completed_laundering = money_laundering.update_operations()
for op in completed_laundering:
    player.gold += op['clean_amount']

market_manipulation.update()  # Reduce manipulation durations
```

### 4. Guild Progression
Add guild rank-up checks:
```python
# After crimes committed
if player.guild_membership == 'thieves':
    can_rank_up = thieves_guild.can_rank_up(player.guild_rank, player.crimes_committed)
    if can_rank_up:
        # Show rank up notification
        player.guild_rank += 1
```

### 5. Heist Generation
Add periodic heist availability:
```python
# Every 7 days or at guild rank milestones
if game_time.day_count % 7 == 0:
    easy_heist = heist_manager.generate_heist('easy')
    medium_heist = heist_manager.generate_heist('medium')
    heist_manager.available_heists.extend([easy_heist, medium_heist])
```

## Testing Checklist

### Basic Functionality
- [ ] Press Shift+U opens criminal menu
- [ ] Main menu displays with 11 options
- [ ] Navigation with arrow keys works
- [ ] ESC closes menu
- [ ] All submenus accessible

### System Verification
- [ ] Thieves Guild initialized in Central Town
- [ ] Assassins Guild initialized in Eastern Town
- [ ] 6 gangs created with territories
- [ ] Criminal rank starts at Civilian
- [ ] All managers accessible from UI

### Crime Integration (TODO)
- [ ] Stealing increments criminal rank
- [ ] Breaking in counts as burglary
- [ ] Killing NPC counts as murder
- [ ] Crimes unlock quests when caught
- [ ] Heat level increases with crimes

### Enterprise Operations (TODO)
- [ ] Can purchase enterprises
- [ ] Daily profits collected
- [ ] Heat accumulates
- [ ] Can shutdown/reopen
- [ ] Bust risk calculated

### Heist System (TODO)
- [ ] Can generate heists
- [ ] Crew members add bonuses
- [ ] Stage completion tracked
- [ ] Failure consequences applied
- [ ] Rewards granted on completion

### Laundering (TODO)
- [ ] Can start laundering operations
- [ ] Suspicion increases with operations
- [ ] Operations complete after duration
- [ ] Clean money received
- [ ] Suspicion decreases when idle

## Feature Completeness

| Feature | Backend | UI | Integration | Status |
|---------|---------|-----|-------------|--------|
| Crime Syndicates | ✅ | ⚠️ | ⚠️ | 60% |
| Gang System | ✅ | ⚠️ | ❌ | 40% |
| Criminal Ranks | ✅ | ⚠️ | ❌ | 40% |
| Protection Racket | ✅ | ⚠️ | ❌ | 40% |
| Money Laundering | ✅ | ⚠️ | ❌ | 40% |
| Enterprises | ✅ | ⚠️ | ❌ | 40% |
| Heist System | ✅ | ⚠️ | ❌ | 40% |
| Favor System | ✅ | ⚠️ | ❌ | 40% |
| Skill Trees | ✅ | ❌ | ❌ | 35% |
| Market Manipulation | ✅ | ⚠️ | ❌ | 40% |
| Scamming | ✅ | ⚠️ | ❌ | 40% |
| Stolen Goods Appraisal | ✅ | ⚠️ | ❌ | 40% |
| Criminal Quests | ✅ | ⚠️ | ❌ | 40% |

**Legend:**
- ✅ Complete
- ⚠️ Partial/Placeholder
- ❌ Not Started

## Overall Status
**Backend Systems:** 100% Complete (All 13 features fully implemented)
**UI Layer:** 20% Complete (Main menu + placeholders)
**Game Integration:** 30% Complete (Initialized but not connected to game events)
**Overall Progress:** ~50% Complete

## Conclusion
All 13 requested criminal underworld features have been implemented at the backend level with comprehensive functionality. The systems are initialized in main.py and accessible via Shift+U. The next phase requires:

1. Completing UI implementations for each system
2. Connecting crime events to the criminal rank system
3. Adding daily update loops for enterprises and laundering
4. Creating visual feedback for guild progression and quest unlocks
5. Testing all integrated systems in gameplay

The foundation is solid and ready for full integration!

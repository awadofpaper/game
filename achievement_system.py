"""
Achievement system with pet rewards
Each achievement unlocks a unique pet companion
"""
import logging

logger = logging.getLogger(__name__)


class Achievement:
    """Single achievement with tracking"""
    
    def __init__(self, id, name, description, category, target, pet_reward):
        self.id = id
        self.name = name
        self.description = description
        self.category = category  # Combat, Gathering, Exploration, etc.
        self.target = target  # Target value to unlock
        self.current = 0  # Current progress
        self.unlocked = False
        self.pet_reward = pet_reward  # Pet unlocked by this achievement
        self.just_unlocked = False  # For popup notification
    
    def update_progress(self, value):
        """Update progress and check if unlocked"""
        if self.unlocked:
            return False
        
        self.current = value
        if self.current >= self.target:
            self.unlocked = True
            self.just_unlocked = True
            logger.info(f"[ACHIEVEMENT] Unlocked: {self.name} - Reward: {self.pet_reward}")
            return True
        return False
    
    def get_progress_text(self):
        """Get progress string"""
        if self.unlocked:
            return "UNLOCKED"
        return f"{self.current}/{self.target}"


class AchievementManager:
    """Manages all achievements and pet unlocks"""
    
    def __init__(self):
        self.achievements = []
        self.unlocked_pets = ["chicken"]  # Start with chicken
        self.recent_unlocks = []  # For displaying popups
        self._initialize_achievements()
    
    def _initialize_achievements(self):
        """Create all achievements"""
        
        # COMBAT ACHIEVEMENTS
        self.achievements.append(Achievement(
            "combat_kills_10", "First Blood", "Kill 10 enemies",
            "Combat", 10, "dog"
        ))
        self.achievements.append(Achievement(
            "combat_kills_50", "Warrior", "Kill 50 enemies",
            "Combat", 50, "cat"
        ))
        self.achievements.append(Achievement(
            "combat_kills_100", "Slayer", "Kill 100 enemies",
            "Combat", 100, "wolf"
        ))
        self.achievements.append(Achievement(
            "combat_level_10", "Apprentice", "Reach level 10",
            "Combat", 10, "fox"
        ))
        self.achievements.append(Achievement(
            "combat_level_25", "Expert", "Reach level 25",
            "Combat", 25, "bear"
        ))
        
        # GATHERING ACHIEVEMENTS
        self.achievements.append(Achievement(
            "gather_mining_50", "Rock Collector", "Mine 50 ore",
            "Gathering", 50, "mouse"
        ))
        self.achievements.append(Achievement(
            "gather_woodcut_50", "Lumberjack", "Cut 50 logs",
            "Gathering", 50, "beaver"
        ))
        self.achievements.append(Achievement(
            "gather_fishing_50", "Fisher", "Catch 50 fish",
            "Gathering", 50, "otter"
        ))
        self.achievements.append(Achievement(
            "gather_master", "Resource Master", "Reach level 50 in any gathering skill",
            "Gathering", 50, "raccoon"
        ))
        
        # EXPLORATION ACHIEVEMENTS
        self.achievements.append(Achievement(
            "explore_towns_3", "Tourist", "Visit all 3 towns",
            "Exploration", 3, "parrot"
        ))
        self.achievements.append(Achievement(
            "explore_distance", "Wanderer", "Travel 50,000 pixels",
            "Exploration", 50000, "horse"
        ))
        self.achievements.append(Achievement(
            "explore_dungeons", "Dungeon Delver", "Enter 5 dungeons",
            "Exploration", 5, "bat"
        ))
        
        # ECONOMY ACHIEVEMENTS
        self.achievements.append(Achievement(
            "economy_gold_1000", "Merchant", "Earn 1,000 dubloons",
            "Economy", 1000, "cow"
        ))
        self.achievements.append(Achievement(
            "economy_gold_10000", "Tycoon", "Earn 10,000 dubloons",
            "Economy", 10000, "pig"
        ))
        self.achievements.append(Achievement(
            "economy_trades_50", "Trader", "Complete 50 market trades",
            "Economy", 50, "snake"
        ))
        
        # QUEST ACHIEVEMENTS
        self.achievements.append(Achievement(
            "quest_complete_5", "Helper", "Complete 5 quests",
            "Quests", 5, "owl"
        ))
        self.achievements.append(Achievement(
            "quest_complete_20", "Hero", "Complete 20 quests",
            "Quests", 20, "eagle"
        ))
        
        # SURVIVAL ACHIEVEMENTS
        self.achievements.append(Achievement(
            "survival_days_7", "Survivor", "Survive 7 days",
            "Survival", 7, "rabbit"
        ))
        self.achievements.append(Achievement(
            "survival_cook_25", "Chef", "Cook 25 meals",
            "Survival", 25, "rooster"
        ))
        self.achievements.append(Achievement(
            "survival_fires_10", "Pyromancer", "Build 10 fires",
            "Survival", 10, "dragon"
        ))
        
        # SPECIAL ACHIEVEMENTS
        self.achievements.append(Achievement(
            "special_merchant_50", "Market Magnate", "Reach Merchant skill level 50",
            "Special", 50, "monkey"
        ))
        self.achievements.append(Achievement(
            "special_death_0", "Deathless", "Reach level 15 without dying",
            "Special", 15, "phoenix"
        ))
        self.achievements.append(Achievement(
            "special_kill_tutorial", "No Good Deed...", "Kill the tutorial NPC who tried to help you",
            "Special", 1, "raven"
        ))
        
        # DISEASE & SURVIVAL ACHIEVEMENTS
        self.achievements.append(Achievement(
            "disease_plague_survivor", "Plague Survivor", "Survive the plague",
            "Survival", 1, "crow"
        ))
        self.achievements.append(Achievement(
            "disease_no_std_5_years", "Clean Bill of Health", "Go 5 years without contracting an STD",
            "Survival", 5, "swan"
        ))
        self.achievements.append(Achievement(
            "disease_saved_10_refugees", "Humanitarian", "Help 10 refugees escape plague towns",
            "Survival", 10, "dove"
        ))
        self.achievements.append(Achievement(
            "disease_fire_sneeze_felon", "Magical Menace", "Get arrested for fire sneezing on an NPC",
            "Survival", 1, "dragon"
        ))
        self.achievements.append(Achievement(
            "disease_cured_10_npcs", "Town Healer", "Help cure 10 sick NPCs",
            "Survival", 10, "owl"
        ))
        self.achievements.append(Achievement(
            "disease_no_infection_1_year", "Disease Free", "Go 1 year without any disease",
            "Survival", 1, "butterfly"
        ))
        
        # RACIAL TRAIT ACHIEVEMENTS
        self.achievements.append(Achievement(
            "trait_orc_rage_50", "Berserker", "Enter Orc rage mode 50 times",
            "Traits", 50, "lion"
        ))
        self.achievements.append(Achievement(
            "trait_halfling_dodge_100", "Untouchable", "Dodge 100 attacks as a Halfling",
            "Traits", 100, "hare"
        ))
        self.achievements.append(Achievement(
            "trait_halfling_double_loot_50", "Lucky Streak", "Get 50 double loots as a Halfling",
            "Traits", 50, "magpie"
        ))
        self.achievements.append(Achievement(
            "trait_dwarf_free_repairs_25", "Master Smith", "Get 25 free repairs as a Dwarf",
            "Traits", 25, "mole"
        ))
        self.achievements.append(Achievement(
            "trait_elf_regen_10000", "Eternal", "Regenerate 10,000 mana as an Elf",
            "Traits", 10000, "unicorn"
        ))
        self.achievements.append(Achievement(
            "trait_human_bonus_xp_1000", "Overachiever", "Gain 1,000 bonus XP as a Human",
            "Traits", 1000, "elephant"
        ))
        self.achievements.append(Achievement(
            "trait_tiefling_fire_damage_5000", "Inferno", "Deal 5,000 fire spell damage as a Tiefling",
            "Traits", 5000, "salamander"
        ))
        self.achievements.append(Achievement(
            "trait_orc_dual_2h", "Titan Warrior", "Equip two 2-handed weapons as an Orc",
            "Traits", 1, "gorilla"
        ))

    
    def check_achievement(self, achievement_id, current_value):
        """Update specific achievement progress"""
        for achievement in self.achievements:
            if achievement.id == achievement_id:
                if achievement.update_progress(current_value):
                    self.unlocked_pets.append(achievement.pet_reward)
                    self.recent_unlocks.append(achievement)
                    return True
        return False
    
    def check_all_combat(self, kills, level):
        """Check all combat achievements"""
        self.check_achievement("combat_kills_10", kills)
        self.check_achievement("combat_kills_50", kills)
        self.check_achievement("combat_kills_100", kills)
        self.check_achievement("combat_level_10", level)
        self.check_achievement("combat_level_25", level)
    
    def check_all_gathering(self, mining_count, woodcutting_count, fishing_count, max_skill_level):
        """Check all gathering achievements"""
        self.check_achievement("gather_mining_50", mining_count)
        self.check_achievement("gather_woodcut_50", woodcutting_count)
        self.check_achievement("gather_fishing_50", fishing_count)
        self.check_achievement("gather_master", max_skill_level)
    
    def check_all_exploration(self, towns_visited, distance_traveled, dungeons_entered):
        """Check all exploration achievements"""
        self.check_achievement("explore_towns_3", towns_visited)
        self.check_achievement("explore_distance", distance_traveled)
        self.check_achievement("explore_dungeons", dungeons_entered)
    
    def check_all_economy(self, total_gold_earned, trades_completed):
        """Check all economy achievements"""
        self.check_achievement("economy_gold_1000", total_gold_earned)
        self.check_achievement("economy_gold_10000", total_gold_earned)
        self.check_achievement("economy_trades_50", trades_completed)
    
    def check_all_quests(self, quests_completed):
        """Check all quest achievements"""
        self.check_achievement("quest_complete_5", quests_completed)
        self.check_achievement("quest_complete_20", quests_completed)
    
    def check_all_survival(self, days_survived, meals_cooked, fires_built):
        """Check all survival achievements"""
        self.check_achievement("survival_days_7", days_survived)
        self.check_achievement("survival_cook_25", meals_cooked)
        self.check_achievement("survival_fires_10", fires_built)
    
    def check_special(self, merchant_level, level_without_death):
        """Check special achievements"""
        self.check_achievement("special_merchant_50", merchant_level)
        self.check_achievement("special_death_0", level_without_death)
    
    def check_all_disease(self, plague_survived, std_free_years, refugees_saved, 
                          fire_sneeze_arrests, npcs_cured, disease_free_years):
        """Check all disease achievements"""
        self.check_achievement("disease_plague_survivor", plague_survived)
        self.check_achievement("disease_no_std_5_years", std_free_years)
        self.check_achievement("disease_saved_10_refugees", refugees_saved)
        self.check_achievement("disease_fire_sneeze_felon", fire_sneeze_arrests)
        self.check_achievement("disease_cured_10_npcs", npcs_cured)
        self.check_achievement("disease_no_infection_1_year", disease_free_years)
    
    def check_all_racial_traits(self, orc_rage_count, halfling_dodges, halfling_double_loots, 
                                 dwarf_free_repairs, elf_mana_regen_total, human_bonus_xp,
                                 tiefling_fire_damage, orc_dual_2h_equipped):
        """Check all racial trait achievements"""
        self.check_achievement("trait_orc_rage_50", orc_rage_count)
        self.check_achievement("trait_halfling_dodge_100", halfling_dodges)
        self.check_achievement("trait_halfling_double_loot_50", halfling_double_loots)
        self.check_achievement("trait_dwarf_free_repairs_25", dwarf_free_repairs)
        self.check_achievement("trait_elf_regen_10000", int(elf_mana_regen_total))
        self.check_achievement("trait_human_bonus_xp_1000", int(human_bonus_xp))
        self.check_achievement("trait_tiefling_fire_damage_5000", int(tiefling_fire_damage))
        self.check_achievement("trait_orc_dual_2h", 1 if orc_dual_2h_equipped else 0)
    
    def get_recent_unlock(self):
        """Get and clear most recent unlock for popup"""
        if self.recent_unlocks:
            achievement = self.recent_unlocks.pop(0)
            achievement.just_unlocked = False
            return achievement
        return None
    
    def get_unlocked_count(self):
        """Get number of unlocked achievements"""
        return sum(1 for a in self.achievements if a.unlocked)
    
    def get_total_count(self):
        """Get total number of achievements"""
        return len(self.achievements)
    
    def get_achievements_by_category(self):
        """Get achievements organized by category"""
        categories = {}
        for achievement in self.achievements:
            if achievement.category not in categories:
                categories[achievement.category] = []
            categories[achievement.category].append(achievement)
        return categories
    
    def save_state(self):
        """Save achievement state"""
        return {
            'achievements': {
                a.id: {
                    'current': a.current,
                    'unlocked': a.unlocked
                } for a in self.achievements
            },
            'unlocked_pets': self.unlocked_pets
        }
    
    def load_state(self, state):
        """Load achievement state"""
        if 'achievements' in state:
            for achievement in self.achievements:
                if achievement.id in state['achievements']:
                    data = state['achievements'][achievement.id]
                    achievement.current = data.get('current', 0)
                    achievement.unlocked = data.get('unlocked', False)
        
        if 'unlocked_pets' in state:
            self.unlocked_pets = state['unlocked_pets']

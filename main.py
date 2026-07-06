# pyright: reportUnusedVariable=false, reportUnusedImport=false, reportOptionalMemberAccess=false
# type: ignore
"""
RPG Game - Main Entry Point
A comprehensive 2D RPG with extensive systems including towns, dungeons, NPCs, combat, and economy.
"""

import pygame
import sys
import math
import time
import random
import logging
# Equipment UI imports (Diablo-style equipment screen)
from equipment_ui import EquipmentUI
from equipment_manager import EquipmentManager
from config import Config
from world import World
from player import Player
from graphics import Graphics
from entities import EntityManager
from utils import save_game, load_game
from save_slot_system import SaveSlotManager, SaveSlot
from save_slot_ui import save_slot_selection_loop
from game_time import GameTime
from performance_manager import get_performance_manager, update_performance_monitoring
from performance_settings_ui import get_performance_settings_ui
from weather import WeatherSystem
from weather_items import apply_weather_effects_to_player, add_weather_protection_methods_to_player
from accessibility_settings import get_accessibility_settings
from accessibility_ui import get_accessibility_ui
from font_settings_ui import get_font_settings_ui
from ai_personality_system import get_personality_manager
from ai_behavior_trees import get_behavior_tree_factory
from ai_settings_ui import get_ai_settings_ui
from inventory_system import Inventory
from equipment import Equipment
import loot
from floating_text import FloatingText, DamageNumber, CombatText
from combat_particles import CombatParticleManager
from combat_log import CombatLog
from enhanced_loot import get_enhanced_loot_system
from loot_ui import get_boss_loot_preview_ui, get_set_bonus_display_ui
from dungeon_variety import get_dungeon_variety_system
from dungeon_variety_ui import (
    get_dungeon_info_ui, get_speed_run_timer_ui, get_trap_warning_ui,
    get_secret_discovered_ui, get_dungeon_modifier_selection_ui
)
from summoning_system import get_summoning_system, initialize_summoning_system, SummonType
from summoning_ui import get_summon_info_ui, get_necromancy_indicator_ui, get_summon_cast_effect_ui
from dropped_equipment import DroppedEquipment
from dungeon_generator import Dungeon, create_dungeon
from town_instance import create_town_instance
from skill_ui import skill_tree_menu
from stats_menu import draw_stats_menu, handle_stats_menu_input, draw_character_sheet, draw_active_trait_indicators
from crime_history_ui import draw_crime_history
from smart_inventory import SmartInventoryManager
from smart_inventory_ui import SmartInventoryUI
from smart_inventory_integration import integrate_smart_inventory_with_player
from spell_combinations import AdvancedSpellSystem
from spellbook_ui import spellbook_menu
from spells import SPELLS, STARTER_SPELLS
from npc_basic import BasicNPC, NPCManager, create_starter_npcs, create_town_guards
from npc_dialogue import DialogueUI as AdvancedDialogueUI, create_elder_sage_npc
from optimization_enhancements import get_frame_limiter, get_spatial_hash
from save_integration import integrate_enhanced_saves
from resource_respawn import ResourceRespawnManager
from enemies import Enemy, spawn_enemy, determine_enemy_rarity, handle_enemy_drops, ENEMY_TYPES
from spell_hud import SpellHUD
from ai_debug_overlay import AIDebugOverlay
from key_bindings import get_key_bindings, MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT
from key_bindings_ui import get_keybindings_ui
from crafting import get_crafting_ui
from repair_system import get_repair_system
from locked_chests import get_chest_manager
from minimap import Minimap
from fullscreen_map import FullscreenMap
from reputation_system import ReputationSystem
from quest_system import QuestManager, ObjectiveType
from quest_ui import QuestLogUI, QuestTrackerUI
from dialogue_system import DialogueManager
from dialogue_ui import DialogueUI, DialogueHistoryUI
from mayor_powers_ui import MayorPowersUI
from shop_system import ShopManager
from shop_ui import ShopUI
from shop_ownership_ui import ShopOwnershipUI
from economic_events_ui import EconomicEventsUI
from trading_menu_ui import TradingMenuUI
from bartering_ui import BarteringUI
from advanced_trading_systems import QualitySystemManager, TimeBasedSalesManager, AppraisalSystem, ConsignmentAuctionManager
from advanced_trading_ui import AdvancedTradingUI
from building_expansions import EquipmentBuybackSystem, TavernFoodTrading, MarketStallSystem, SafetyDepositSystem
from building_expansions_ui import TavernFoodTradingUI, MarketStallUI, SafetyDepositBoxUI
from merchant_reputation_system import MerchantReputationManager
from dynamic_inventory_system import DynamicInventoryManager
from haggling_system import HagglingSystem, BarteringSystem
from special_orders_system import SpecialOrderManager
from trade_routes_system import CaravanManager
from shop_ownership_system import ShopOwnershipManager
from smuggling_system import SmugglingSystem
from price_events_system import PriceEventManager
from merchant_quests_system import MerchantQuestManager
from town_system import TownManager, BuildingType, Building
from inn_system import InnManager, InnUI
from blacksmith_system import BlacksmithManager, BlacksmithUI
from repair_menu_ui import RepairMenuUI
from tavern_system import TavernManager, TavernUI
from temple_system import TempleManager, TempleUI
from bank_system import BankManager, BankUI
from town_hall_system import TownHallManager, TownHallUI
from rumor_system import RumorSystem
from npc_interaction_system import NPCInteractionSystem
from npc_family_system import NPCFamilySystem
from cooking_system import FireManager, CookingUI
from leaderboard_system import LeaderboardSystem
from leaderboard_ui import LeaderboardUI
from gathering_nodes import GatheringNodesManager
from gatherer_npc import GathererNPCManager
from building_interior import BuildingInterior, InteriorObject
from crime_punishment_system import StolenItem, GuardSearchSystem, WantedSystem, TownCooldownSystem, InvestigationSystem, JailWorkSystem, JailEscapeSystem
from break_in_system import BreakInSystem, FencingSystem
from fence_system import FenceManager, FenceNPC
from stealth_system import StealthSystem, VisionCone
from stealth_indicator_ui import get_stealth_indicator_ui
from criminal_underworld_system import (
    ThievesGuild, AssassinsGuild, GangManager, CriminalRankSystem,
    ProtectionRacket, MoneyLaundering, EnterpriseManager, HeistManager, FavorSystem
)
from criminal_underworld_system_part2 import (
    CriminalSkillTree, MarketManipulation, ScammingSystem,
    StolenGoodsAppraiser, CriminalQuestSystem
)
from criminal_ui import get_criminal_ui
from election_system import CampaignPromise, CampaignPromiseSystem, ElectionTimeline, BallotBox, VoterBriberySystem, MayorTermSystem, AnarchySystem
from mayor_powers_system import CurfewSystem, TownEntryFeeSystem, WeaponRestrictionSystem, MayorSalarySystem, MayorAbscondingSystem, EmbargoSystem
from insurance_system import InsuranceSystem, InsurancePolicy
from property_financial_system import MultiplePlotsSystem, NPCFinancesSystem, NPCFinances, TownTreasurySystem, TownTreasury, GuardProtectionFeeSystem, PropertyTaxSystem
from homeless_npc_system import HomelessNPCSystem, HomelessNPC
from npc_housing_system import NPCHousingSystem, NPCResidence
from trade_route_system import TradeRouteSystem, TradeRoute, Caravan, ResourceContract
from npc_skill_switching_system import NPCSkillSwitchingSystem, SkillSwitchRecord
from body_disposal_system import Corpse, Grave, BodyDisposalSystem
from npc_trader_system import NPCTradeEngine, TravelingMerchantNPC, NPCTraderBehavior
from shop_investment_system import InvestmentSystem, StockMarket, NPCInvestor
from town_trade_agreements import TownTradeAgreementSystem, TradeAgreement, NPCDiplomat
from npc_contract_system import NPCContractSystem, NPCContractor, ContractBoard
from wilderness_fighter_npc_system import WildernessFighterNPC, WildernessFighterNPCSystem
from fast_travel_system import FastTravelSystem
from gatherer_dialogue import create_gatherer_dialogue, handle_dialogue_consequence
from skills_ui import SkillsUI, draw_skills_hud
from market_system import initialize_commodities
from market_manager import MarketManager
from market_ui import MarketUI
from trade_route_ui import TradeRouteUI
from stock_market_ui import StockMarketUI
from companion_system import CompanionManager, Companion, CompanionType
from companion_hiring_ui import CompanionHiringUI, CompanionPaymentSystem
from npc_combat_enhancements import NPCCombatManager, NPCCombatAI, NPCLootingSystem, NPCFleeingAI
from merchant_insurance_system import InsuranceProvider, PlayerInsuranceUI
from npc_role_adaptation import NPCRoleAdaptationSystem
from npc_skill_switching_ui import NPCSkillSwitchingUI
from chicken_pet import PetCompanion
from achievement_system import AchievementManager
from achievement_ui import AchievementUI, AchievementPopup
from bestiary import Bestiary
from newspaper_system import NewspaperGenerator, NewspaperDistribution, Newspaper
from newspaper_ui import NewspaperUI
from commodity_exchange_ui import CommodityExchangeUI
from economics_skill_tree import EconomicsSkillTree
from economics_skill_tree_ui import EconomicsSkillTreeUI
from pet_menu import PetMenuUI
from resource_cache import get_cached_surface, get_cached_font
from hotbar_system import HotbarSystem, HotbarSlotType
from hotbar_ui import HotbarUI
from cosmetic_system import CosmeticManager, CosmeticGenerator, CosmeticRarity
from lootbox_ui import LootBoxAnimation
from cosmetic_menu_ui import CosmeticEquipMenu
from max_shop_system import MaxShopInteraction, LootBoxShop, MaxDialogue
# Disease and library systems
from disease_system import DiseaseManager, DISEASE_DEFINITIONS, DiseaseType
from library_system import LibraryManager, Library, LibraryUI
from mage_service_system import MageManager, Mage, MageUI
# Import refactored modules
from game_utils import (
    get_item_icon, get_equipment_slot, get_equipment_comparison,
    format_equipment_tooltip, get_item_rarity_color, is_item_equipped,
    get_font, get_active_set_bonuses, should_auto_loot,
    salvage_equipment, sort_inventory_items, ITEM_ICONS
)
from ui_helpers import (
    toggle_fullscreen, show_help_menu, draw_menu, main_menu,
    character_creation, draw_campaign_menu
)
import os

# Initialize logging - WARNING level only for performance
logging.basicConfig(
    level=logging.INFO,  # Temporarily set to INFO for debugging curfew system
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# REINFORCEMENT LEARNING INTEGRATION - Game Wrapper Class
# ============================================================================

class Game:
    """
    RL-compatible game wrapper for training agents.
    
    Provides a simplified interface with phase-based progression:
    - menu: Game start screen
    - character_creation: Allocate 15 skill points
    - in_game: Full gameplay with movement, combat, trading, quests
    """
    
    def __init__(self, config=None, headless=True):
        self.config = config or Config()
        self.headless = headless  # If True, bypass all UI interactions
        self.world = World(self.config)
        self.game_time = GameTime(cycle_minutes=57)
        
        # Game state machine for RL
        self.phase = "menu"  # Phases: menu, character_creation, in_game
        self.player = None  # Created after character creation
        self.done = False
        
        # Character creation temporary storage
        self.char_name = None
        self.char_color = None
        self.char_skills = {"strength": 0, "stamina": 0, "stealth": 0, "endurance": 0, "magic": 0}
        self.skill_points_left = 15
        self.current_skill_idx = 0
        self.skill_names = ["strength", "stamina", "stealth", "endurance", "magic"]
        
        # Track stats for RL rewards (initialized after player creation)
        self.prev_xp = 0
        self.prev_level = 1
        self.prev_perk_points = 0
        self.prev_skill_levels = {}
        self.prev_gold = 0
        self.prev_health = 100
        
        # Combat simulation state
        self.nearby_enemies = []
        self.combat_cooldown = 0
    
    def reset(self):
        """Reset the game to initial state."""
        self.world = World(self.config)
        self.game_time = GameTime(cycle_minutes=57)
        self.phase = "menu"
        self.player = None
        self.done = False
        
        # Reset character creation storage
        self.char_name = None
        self.char_color = None
        self.char_skills = {"strength": 0, "stamina": 0, "stealth": 0, "endurance": 0, "magic": 0}
        self.skill_points_left = 15
        self.current_skill_idx = 0
        
        # Reset tracking stats
        self.prev_xp = 0
        self.prev_level = 1
        self.prev_perk_points = 0
        self.prev_skill_levels = {}
        self.prev_gold = 0
        self.prev_health = 100
        self.prev_quest_progress = 0
        
        # Reset combat state
        self.nearby_enemies = []
        self.combat_cooldown = 0
        
        return self._get_obs()

    def step(self, action):
        """Execute one step in the game based on current phase.
        
        Action mapping:
        Menu phase (0-1): 0=new game, 1=skip menu
        Character creation phase (0-8): 
            0-4=add point to skill 0-4, 5=remove point from current skill, 
            6=next skill, 7=prev skill, 8=confirm character
        In-game phase (0-8): 
            0=up, 1=down, 2=left, 3=right, 4=attack, 
            5=talk, 6=train skill, 7=pick skill, 8=use perk
        """
        reward = 0
        info = {'phase': self.phase}
        
        # MENU PHASE
        if self.phase == "menu":
            if action == 0 or action == 1:  # Start new game
                self.phase = "character_creation"
                reward = 1  # Small reward for progressing
                info['action'] = 'start_new_game'
            return self._get_obs(), reward, self.done, info
        
        # CHARACTER CREATION PHASE
        elif self.phase == "character_creation":
            if action >= 0 and action <= 4:  # Add point to skill
                if self.skill_points_left > 0:
                    skill_name = self.skill_names[action]
                    self.char_skills[skill_name] += 1
                    self.skill_points_left -= 1
                    reward = 0.5
                    info['action'] = f'add_point_to_{skill_name}'
            elif action == 5:  # Remove point from current skill
                current_skill = self.skill_names[self.current_skill_idx]
                if self.char_skills[current_skill] > 0:
                    self.char_skills[current_skill] -= 1
                    self.skill_points_left += 1
                    info['action'] = f'remove_point_from_{current_skill}'
            elif action == 6:  # Next skill
                self.current_skill_idx = (self.current_skill_idx + 1) % len(self.skill_names)
                info['action'] = 'next_skill'
            elif action == 7:  # Prev skill
                self.current_skill_idx = (self.current_skill_idx - 1) % len(self.skill_names)
                info['action'] = 'prev_skill'
            elif action == 8:  # Confirm character
                if self.skill_points_left == 0:
                    # Generate random name and color if not set
                    import random
                    if not self.char_name:
                        self.char_name = f"Agent{random.randint(1000, 9999)}"
                    if not self.char_color:
                        self.char_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                    
                    # Create player
                    self.player = Player(self.config, self.world, name=self.char_name, 
                                       color=self.char_color, skills=self.char_skills)
                    self.phase = "in_game"
                    reward = 10  # Big reward for completing character creation
                    info['action'] = 'character_confirmed'
                    info['character_created'] = True
                    
                    # Initialize tracking stats
                    self.prev_xp = getattr(self.player, 'xp', 0)
                    self.prev_level = getattr(self.player, 'level', 1)
                    self.prev_perk_points = getattr(self.player, 'perk_points', 0)
                    self.prev_skill_levels = dict(getattr(self.player, 'skills', {}))
                    self.prev_gold = getattr(self.player, 'gold', 0)
                    self.prev_health = getattr(self.player, 'health', 100)
                    self.prev_quest_progress = 0
                else:
                    reward = -1  # Penalty for trying to confirm with points left
                    info['action'] = 'confirm_failed_points_remaining'
            
            return self._get_obs(), reward, self.done, info
        
        # IN-GAME PHASE
        elif self.phase == "in_game":
            reward = -0.1  # Small step penalty
            
            # Update combat cooldown
            if self.combat_cooldown > 0:
                self.combat_cooldown -= 1
            
            if action == 0:
                self.player.y -= self.player.speed
            elif action == 1:
                self.player.y += self.player.speed
            elif action == 2:
                self.player.x -= self.player.speed
            elif action == 3:
                self.player.x += self.player.speed
            elif action == 4:
                # IMPROVED COMBAT SIMULATION
                if self.combat_cooldown == 0:
                    # Spawn enemies near player if none exist
                    if not self.nearby_enemies:
                        if random.random() < 0.3:  # 30% chance to encounter enemy
                            enemy_distance = random.randint(50, 150)
                            enemy_health = random.randint(20, 50)
                            self.nearby_enemies.append({
                                'distance': enemy_distance,
                                'health': enemy_health,
                                'max_health': enemy_health
                            })
                            info['combat'] = 'enemy_appeared'
                    
                    # Attack nearest enemy
                    if self.nearby_enemies:
                        enemy = self.nearby_enemies[0]
                        player_strength = getattr(self.player, 'strength', 0)
                        base_damage = random.randint(5, 15)
                        damage = base_damage + player_strength
                        
                        enemy['health'] -= damage
                        info['combat_damage'] = damage
                        
                        if enemy['health'] <= 0:
                            # Enemy defeated!
                            self.nearby_enemies.pop(0)
                            xp_gain = random.randint(10, 30)
                            gold_gain = random.randint(5, 20)
                            self.player.xp = getattr(self.player, 'xp', 0) + xp_gain
                            self.player.gold = getattr(self.player, 'gold', 0) + gold_gain
                            reward += 15  # Larger reward for defeating enemy
                            info['combat'] = 'enemy_defeated'
                            info['xp_gain'] = xp_gain
                            info['gold_gain'] = gold_gain
                        else:
                            # Enemy survives, takes damage
                            reward += 2
                            info['combat'] = 'enemy_hit'
                            # Enemy counter-attacks
                            enemy_damage = random.randint(3, 10)
                            self.player.health = max(0, getattr(self.player, 'health', 100) - enemy_damage)
                            info['player_damage_taken'] = enemy_damage
                        
                        self.combat_cooldown = 10  # 10-frame cooldown between attacks
                    else:
                        reward -= 0.5  # Small penalty for attacking when no enemies nearby
                        info['combat'] = 'no_enemy'
            elif action == 5:
                # Simulate talking to NPC
                reward += 2  # Reward for social interaction
                info['dialogue'] = 'npc_talked'
            elif action == 6:
                # Simulate breaking tiles / resource gathering
                tile = self.world.get_tile(int(self.player.x), int(self.player.y))
                if tile and hasattr(tile, 'layers'):
                    obj = tile.layers.get('object')
                    if obj in ['tree', 'bush', 'rock_group']:
                        # Successfully gathered resource
                        reward += 3
                        info['gathering'] = f'{obj}_gathered'
                        # Add resources to inventory
                        if obj == 'tree':
                            self.player.inventory['stick'] = self.player.inventory.get('stick', 0) + 1
                        elif obj == 'bush':
                            self.player.inventory['berries'] = self.player.inventory.get('berries', 0) + random.randint(1, 2)
                        elif obj == 'rock_group':
                            self.player.inventory['ore'] = self.player.inventory.get('ore', 0) + random.randint(1, 2)
                        # Remove object
                        tile.layers['object'] = None
                    else:
                        reward -= 0.3
                        info['gathering'] = 'nothing_to_gather'
            elif action == 7:
                # Simulate picking a skill/perk
                self.player.perk_points = getattr(self.player, 'perk_points', 0) + 1
                reward += 5
                info['perk'] = 'perk_point_gained'
            elif action == 8:
                # Simulate using a perk
                if getattr(self.player, 'perk_points', 0) > 0:
                    self.player.perk_points -= 1
                    reward += 7
                    info['perk'] = 'perk_point_used'

            # Reward for leveling up
            new_level = getattr(self.player, 'level', 1)
            if new_level > self.prev_level:
                reward += 20
                info['level_up'] = True
            self.prev_level = new_level

            # Reward for gaining XP
            new_xp = getattr(self.player, 'xp', 0)
            if new_xp > self.prev_xp:
                reward += (new_xp - self.prev_xp) * 0.01
            self.prev_xp = new_xp

            # Reward for skill improvement (all tracked skills)
            for skill, lvl in getattr(self.player, 'skills', {}).items():
                if self.prev_skill_levels.get(skill, 0) < lvl:
                    reward += 2
            self.prev_skill_levels = dict(getattr(self.player, 'skills', {}))

            # Reward for quest progress
            new_quest_progress = getattr(self.player, 'quest_progress', 0)
            if new_quest_progress > self.prev_quest_progress:
                reward += (new_quest_progress - self.prev_quest_progress) * 10
            self.prev_quest_progress = new_quest_progress

            # Reward for gaining gold
            new_gold = getattr(self.player, 'gold', 0)
            if new_gold > self.prev_gold:
                reward += (new_gold - self.prev_gold) * 0.01
            self.prev_gold = new_gold

            # Penalty for losing health
            new_health = getattr(self.player, 'health', 100)
            if new_health < self.prev_health:
                reward -= (self.prev_health - new_health) * 0.5
            self.prev_health = new_health

            # Check for terminal condition
            if self.player.health <= 0:
                self.done = True
                reward -= 50  # Big penalty for dying
                info['death'] = True
                
            return self._get_obs(), reward, self.done, info
        
        return self._get_obs(), reward, self.done, info

    def _get_obs(self):
        """Get observation based on current phase.
        
        Returns observation vector with phase-specific information.
        All skill names use lowercase for consistency (strength, stamina, stealth, endurance, magic).
        """
        if self.phase == "menu":
            # Menu phase: just phase indicator and zeros
            return [0, 0, 100, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 13 zeros representing "waiting"
        
        elif self.phase == "character_creation":
            # Character creation phase: skill allocations and points left
            # [phase_id, skill_pts_left, skill0, skill1, skill2, skill3, skill4, current_skill_idx, ...]
            return [
                1,  # phase indicator
                self.skill_points_left,
                self.char_skills.get("strength", 0),
                self.char_skills.get("stamina", 0),
                self.char_skills.get("stealth", 0),
                self.char_skills.get("endurance", 0),
                self.char_skills.get("magic", 0),
                self.current_skill_idx,
                0, 0, 0, 0, 0  # padding to match observation size
            ]
        
        elif self.phase == "in_game" and self.player:
            # In-game phase: full player state
            skills = getattr(self.player, 'skills', {})
            inventory = getattr(self.player, 'inventory', {})
            item_count = sum(v for k, v in inventory.items() if isinstance(v, int))
            
            # Use lowercase skill names (with fallbacks to capitalized for compatibility)
            strength = skills.get('strength', skills.get('Strength', 0))
            stamina = skills.get('stamina', skills.get('Stamina', 0))
            magic = skills.get('magic', skills.get('Magic', 0))
            stealth = skills.get('stealth', skills.get('Stealth', 0))
            
            return [
                self.player.x,
                self.player.y,
                getattr(self.player, 'health', 100),
                getattr(self.player, 'level', 1),
                getattr(self.player, 'xp', 0),
                getattr(self.player, 'gold', 0),
                getattr(self.player, 'perk_points', 0),
                strength,
                stamina,
                magic,
                stealth,
                item_count,
                getattr(self.player, 'quest_progress', 0)
            ]
        
        # Fallback: return zeros
        return [0] * 13


# ============================================================================
# MAIN GAME FUNCTION
# ============================================================================

"""
RPG Game - Main Entry Point
A comprehensive 2D RPG with extensive systems including towns, dungeons, NPCs, combat, and economy.
"""

import pygame
import sys
import math
import time
import random
import logging
from config import Config
from world import World
from player import Player
from graphics import Graphics
from entities import EntityManager
from utils import save_game, load_game
from save_slot_system import SaveSlotManager, SaveSlot
from save_slot_ui import save_slot_selection_loop
from game_time import GameTime
from performance_manager import get_performance_manager, update_performance_monitoring
from performance_settings_ui import get_performance_settings_ui
from weather import WeatherSystem
from weather_items import apply_weather_effects_to_player, add_weather_protection_methods_to_player
from accessibility_settings import get_accessibility_settings
from accessibility_ui import get_accessibility_ui
from font_settings_ui import get_font_settings_ui
from ai_personality_system import get_personality_manager
from ai_behavior_trees import get_behavior_tree_factory
from ai_settings_ui import get_ai_settings_ui
from inventory_system import Inventory
from equipment import Equipment
import loot
from floating_text import FloatingText, DamageNumber, CombatText
from combat_particles import CombatParticleManager
from combat_log import CombatLog
from enhanced_loot import get_enhanced_loot_system
from loot_ui import get_boss_loot_preview_ui, get_set_bonus_display_ui
from dungeon_variety import get_dungeon_variety_system
from dungeon_variety_ui import (
    get_dungeon_info_ui, get_speed_run_timer_ui, get_trap_warning_ui,
    get_secret_discovered_ui, get_dungeon_modifier_selection_ui
)
from summoning_system import get_summoning_system, initialize_summoning_system, SummonType
from summoning_ui import get_summon_info_ui, get_necromancy_indicator_ui, get_summon_cast_effect_ui
from dropped_equipment import DroppedEquipment
from dungeon_generator import Dungeon, create_dungeon
from town_instance import create_town_instance
from skill_ui import skill_tree_menu
from stats_menu import draw_stats_menu, handle_stats_menu_input, draw_character_sheet, draw_active_trait_indicators
from crime_history_ui import draw_crime_history
from smart_inventory import SmartInventoryManager
from smart_inventory_ui import SmartInventoryUI
from smart_inventory_integration import integrate_smart_inventory_with_player
from spell_combinations import AdvancedSpellSystem
from spellbook_ui import spellbook_menu
from spells import SPELLS, STARTER_SPELLS
from npc_basic import BasicNPC, NPCManager, create_starter_npcs, create_town_guards
from npc_dialogue import DialogueUI as AdvancedDialogueUI, create_elder_sage_npc
from optimization_enhancements import get_frame_limiter, get_spatial_hash
from save_integration import integrate_enhanced_saves
from resource_respawn import ResourceRespawnManager
from enemies import Enemy, spawn_enemy, determine_enemy_rarity, handle_enemy_drops, ENEMY_TYPES
from spell_hud import SpellHUD
from ai_debug_overlay import AIDebugOverlay
from key_bindings import get_key_bindings, MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT
from key_bindings_ui import get_keybindings_ui
from crafting import get_crafting_ui
from repair_system import get_repair_system
from locked_chests import get_chest_manager
from minimap import Minimap
from fullscreen_map import FullscreenMap
from reputation_system import ReputationSystem
from quest_system import QuestManager, ObjectiveType
from quest_ui import QuestLogUI, QuestTrackerUI
from dialogue_system import DialogueManager
from dialogue_ui import DialogueUI, DialogueHistoryUI
from mayor_powers_ui import MayorPowersUI
from shop_system import ShopManager
from shop_ui import ShopUI
from shop_ownership_ui import ShopOwnershipUI
from economic_events_ui import EconomicEventsUI
from trading_menu_ui import TradingMenuUI
from bartering_ui import BarteringUI
from advanced_trading_systems import QualitySystemManager, TimeBasedSalesManager, AppraisalSystem, ConsignmentAuctionManager
from advanced_trading_ui import AdvancedTradingUI
from building_expansions import EquipmentBuybackSystem, TavernFoodTrading, MarketStallSystem, SafetyDepositSystem
from building_expansions_ui import TavernFoodTradingUI, MarketStallUI, SafetyDepositBoxUI
from merchant_reputation_system import MerchantReputationManager
from dynamic_inventory_system import DynamicInventoryManager
from haggling_system import HagglingSystem, BarteringSystem
from special_orders_system import SpecialOrderManager
from trade_routes_system import CaravanManager
from shop_ownership_system import ShopOwnershipManager
from smuggling_system import SmugglingSystem
from price_events_system import PriceEventManager
from merchant_quests_system import MerchantQuestManager
from town_system import TownManager, BuildingType, Building
from inn_system import InnManager, InnUI
from blacksmith_system import BlacksmithManager, BlacksmithUI
from repair_menu_ui import RepairMenuUI
from tavern_system import TavernManager, TavernUI
from temple_system import TempleManager, TempleUI
from bank_system import BankManager, BankUI
from town_hall_system import TownHallManager, TownHallUI
from rumor_system import RumorSystem
from npc_interaction_system import NPCInteractionSystem
from npc_family_system import NPCFamilySystem
from cooking_system import FireManager, CookingUI
from leaderboard_system import LeaderboardSystem
from leaderboard_ui import LeaderboardUI
from gathering_nodes import GatheringNodesManager
from gatherer_npc import GathererNPCManager
from building_interior import BuildingInterior, InteriorObject
from crime_punishment_system import StolenItem, GuardSearchSystem, WantedSystem, TownCooldownSystem, InvestigationSystem, JailWorkSystem, JailEscapeSystem
from break_in_system import BreakInSystem, FencingSystem
from fence_system import FenceManager, FenceNPC
from stealth_system import StealthSystem, VisionCone
from stealth_indicator_ui import get_stealth_indicator_ui
from criminal_underworld_system import (
    ThievesGuild, AssassinsGuild, GangManager, CriminalRankSystem,
    ProtectionRacket, MoneyLaundering, EnterpriseManager, HeistManager, FavorSystem
)
from criminal_underworld_system_part2 import (
    CriminalSkillTree, MarketManipulation, ScammingSystem,
    StolenGoodsAppraiser, CriminalQuestSystem
)
from criminal_ui import get_criminal_ui
from election_system import CampaignPromise, CampaignPromiseSystem, ElectionTimeline, BallotBox, VoterBriberySystem, MayorTermSystem, AnarchySystem
from mayor_powers_system import CurfewSystem, TownEntryFeeSystem, WeaponRestrictionSystem, MayorSalarySystem, MayorAbscondingSystem, EmbargoSystem
from insurance_system import InsuranceSystem, InsurancePolicy
from property_financial_system import MultiplePlotsSystem, NPCFinancesSystem, NPCFinances, TownTreasurySystem, TownTreasury, GuardProtectionFeeSystem, PropertyTaxSystem
from homeless_npc_system import HomelessNPCSystem, HomelessNPC
from npc_housing_system import NPCHousingSystem, NPCResidence
from trade_route_system import TradeRouteSystem, TradeRoute, Caravan, ResourceContract
from npc_skill_switching_system import NPCSkillSwitchingSystem, SkillSwitchRecord
from body_disposal_system import Corpse, Grave, BodyDisposalSystem
from npc_trader_system import NPCTradeEngine, TravelingMerchantNPC, NPCTraderBehavior
from shop_investment_system import InvestmentSystem, StockMarket, NPCInvestor
from town_trade_agreements import TownTradeAgreementSystem, TradeAgreement, NPCDiplomat
from npc_contract_system import NPCContractSystem, NPCContractor, ContractBoard
from wilderness_fighter_npc_system import WildernessFighterNPC, WildernessFighterNPCSystem
from fast_travel_system import FastTravelSystem
from gatherer_dialogue import create_gatherer_dialogue, handle_dialogue_consequence
from skills_ui import SkillsUI, draw_skills_hud
from market_system import initialize_commodities
from market_manager import MarketManager
from market_ui import MarketUI
from trade_route_ui import TradeRouteUI
from stock_market_ui import StockMarketUI
from companion_system import CompanionManager, Companion, CompanionType
from companion_hiring_ui import CompanionHiringUI, CompanionPaymentSystem
from npc_combat_enhancements import NPCCombatManager, NPCCombatAI, NPCLootingSystem, NPCFleeingAI
from merchant_insurance_system import InsuranceProvider, PlayerInsuranceUI
from npc_role_adaptation import NPCRoleAdaptationSystem
from npc_skill_switching_ui import NPCSkillSwitchingUI
from chicken_pet import PetCompanion
from achievement_system import AchievementManager
from achievement_ui import AchievementUI, AchievementPopup
from newspaper_system import NewspaperGenerator, NewspaperDistribution, Newspaper
from newspaper_ui import NewspaperUI
from commodity_exchange_ui import CommodityExchangeUI
from economics_skill_tree import EconomicsSkillTree
from economics_skill_tree_ui import EconomicsSkillTreeUI
from pet_menu import PetMenuUI
from resource_cache import get_cached_surface, get_cached_font
from hotbar_system import HotbarSystem, HotbarSlotType
from hotbar_ui import HotbarUI
from cosmetic_system import CosmeticManager, CosmeticGenerator, CosmeticRarity
from lootbox_ui import LootBoxAnimation
from cosmetic_menu_ui import CosmeticEquipMenu
from max_shop_system import MaxShopInteraction, LootBoxShop, MaxDialogue
# Import refactored modules
from game_utils import (
    get_item_icon, get_equipment_slot, get_equipment_comparison,
    format_equipment_tooltip, get_item_rarity_color, is_item_equipped,
    get_font, get_active_set_bonuses, should_auto_loot,
    salvage_equipment, sort_inventory_items, ITEM_ICONS
)
from ui_helpers import (
    toggle_fullscreen, show_help_menu, draw_menu, main_menu,
    character_creation, draw_campaign_menu
)
import os

# Initialize logging - WARNING level only for performance
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize pygame and config
pygame.init()
config = Config()

# Set up display - fullscreen mode
is_fullscreen = True
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
config.SCREEN_WIDTH = screen.get_width()
config.SCREEN_HEIGHT = screen.get_height()
pygame.display.set_caption(config.GAME_TITLE)
clock = pygame.time.Clock()

# ===== REFACTORED UTILITY FUNCTIONS =====
# The following functions have been moved to separate modules for better organization:
#
# From game_utils.py:
#   - get_item_icon(), get_equipment_slot(), get_equipment_comparison()
#   - format_equipment_tooltip(), get_item_rarity_color(), is_item_equipped()
#   - get_font(), get_active_set_bonuses(), should_auto_loot()
#   - salvage_equipment(), sort_inventory_items()
#   - random_color(), random_name()
#   - ITEM_ICONS constant
#
# From ui_helpers.py:
#   - toggle_fullscreen(), show_help_menu(), draw_menu(), main_menu()
#   - character_creation(), draw_campaign_menu()
#
# This refactoring reduces main.py from ~9000 lines to a more manageable size
# and resolves Pylance analysis errors due to file size.
# ============================================

# NOTE: All old utility function definitions have been removed.
# They are now properly imported from game_utils.py and ui_helpers.py modules.

# Tutorial system imports
from tutorial_manager import TutorialManager
from tutorial_popup_ui import TutorialPopupUI
from tutorial_npc import TutorialNPC
from tutorial_content import *

def main():
    global is_fullscreen, screen
    import math  # Ensure math is available in function scope
    
    # Parse command-line arguments for AI mode
    ai_mode_enabled = False
    if len(sys.argv) > 1 and '--ai-mode' in sys.argv:
        ai_mode_enabled = True
        logger.info("[AI MODE] AI mode enabled via --ai-mode flag")
    
    # Show main menu and get action + save slot + fullscreen state
    # Skip menu if AI mode is enabled
    if ai_mode_enabled:
        # AI mode: Auto-start new game with dedicated save slot
        menu_action = "new"
        selected_save_slot = None  # Will use dedicated AI slot
        # Keep current fullscreen state
    else:
        result = main_menu(screen, config, is_fullscreen)
        if result is None:
            pygame.quit()
            sys.exit()
        
        menu_action, selected_save_slot, is_fullscreen = result
    
    # Load world and player after menu selection
    world = World(config)
    graphics = Graphics(config, screen)
    # Initialize Diablo-style equipment UI
    equipment_ui = EquipmentUI(config, screen)
    
    # Initialize game time system (57-minute day/night cycle)
    game_time = GameTime(cycle_minutes=57)
    
    # Initialize weather system (connected to game time)
    weather_system = WeatherSystem(game_time, seed=42)
    weather_system.advance_weather()  # Generate initial weather
    
    # Initialize resource respawn manager
    respawn_manager = ResourceRespawnManager(game_time, weather_system)
    
    # Initialize performance manager
    perf_manager = get_performance_manager()
    perf_ui = get_performance_settings_ui()
    
    # Initialize accessibility system
    accessibility_settings = get_accessibility_settings()
    accessibility_ui = get_accessibility_ui()
    font_settings_ui = get_font_settings_ui()
    
    # Initialize AI systems
    personality_manager = get_personality_manager()
    behavior_tree_factory = get_behavior_tree_factory()
    ai_settings_ui = get_ai_settings_ui()
    
    # Initialize spell HUD and AI debug overlay
    from spell_hud import SpellHUD  # Ensure SpellHUD is available in function scope
    from ai_player import AIPlayer  # AI player for automated testing
    spell_hud = SpellHUD(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    ai_debug_overlay = AIDebugOverlay()
    ai_player = AIPlayer()
    logger.info("[UI] Spell HUD, AI Debug Overlay, and AI Player initialized")
    
    # OPTIMIZATION: Initialize performance enhancements
    frame_limiter = get_frame_limiter(config.FPS, adaptive=True)
    spatial_hash = get_spatial_hash(cell_size=500)
    
    # Initialize achievement and trait systems (needed for character creation)
    from achievement_system import AchievementManager
    from trait_audio_system import TraitAudioSystem
    achievement_manager = AchievementManager()
    trait_audio_system = TraitAudioSystem()
    logger.info("[INIT] Achievement manager and trait audio system initialized")
    
    # Initialize enhanced save system
    save_integrator = integrate_enhanced_saves(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    # Initialize rumor system
    rumor_system = RumorSystem(game_time)

    # Initialize NPC interaction system
    npc_interaction_system = NPCInteractionSystem(game_time)


    if menu_action == "new":
        # Create fresh respawn manager for new game (clears old harvest data)
        respawn_manager = ResourceRespawnManager(game_time, weather_system)
        respawn_manager.harvested_resources = {}  # Clear any loaded data from previous session
        respawn_manager.save_data()  # Save empty state
        logger.info("[NEW GAME] Cleared resource respawn data")
        
        # Character creation - either AI or human
        if ai_mode_enabled:
            # AI creates its own character using archetypes
            logger.info("[AI MODE] AI creating character...")
            char_data = ai_player.create_character()
            name = char_data['name']
            color = (255, 255, 0)  # Yellow for AI player visibility
            selected_race = char_data['race']
            skin_tone = char_data['skin_tone']
            skills = char_data['stats']
            # Enable AI player immediately
            ai_player.enabled = True
            logger.info("[AI MODE] Character created, AI player enabled")
        else:
            # Human character creation
            name, color, skills, selected_race, skin_tone, is_fullscreen = character_creation(screen, config, is_fullscreen)
        
        # Clear screen after character creation
        screen.fill((0, 0, 0))
        loading_font = get_font(None, 48)
        
        if ai_mode_enabled:
            # AI Mode startup message
            title = loading_font.render("AI MODE ACTIVATED", True, (100, 255, 100))
            screen.blit(title, (config.SCREEN_WIDTH//2 - title.get_width()//2, config.SCREEN_HEIGHT//2 - 100))
            
            info_font = get_font(None, 24)
            messages = [
                f"Character: {name}",
                f"Race: {selected_race.name}",
                "AI will play autonomously",
                "Press / to stop/resume AI",
                "Auto-saves every 5 minutes to slot 99",
                "",
                "Loading game..."
            ]
            y_offset = config.SCREEN_HEIGHT//2 - 30
            for msg in messages:
                text = info_font.render(msg, True, (200, 200, 200))
                screen.blit(text, (config.SCREEN_WIDTH//2 - text.get_width()//2, y_offset))
                y_offset += 32
        else:
            loading_text = loading_font.render("Loading game...", True, (255, 255, 255))
            screen.blit(loading_text, (config.SCREEN_WIDTH//2 - loading_text.get_width()//2, config.SCREEN_HEIGHT//2))
        
        pygame.display.flip()
        
        # Add a brief pause so users can read the AI mode message
        if ai_mode_enabled:
            time.sleep(3)  # 3 second pause to read message
        
        player = Player(config, world, name=name, color=color, skills=skills)
        
        # Apply race to player
        player.race = selected_race
        player.race_id = selected_race.id
        player.skin_tone = skin_tone
        
        # Apply racial stat modifiers
        from race_system import apply_racial_stat_modifiers
        base_stats = {
            'strength': player.strength,
            'defense': player.defense,
            'magic': player.magic,
            'stamina_stat': player.stamina_stat,
            'speed': player.speed,
            'agility': player.agility,
            'willpower': player.willpower,
            'luck': player.luck,
            'intelligence': player.intelligence,
            'talking': player.talking
        }
        modified_stats = apply_racial_stat_modifiers(base_stats, selected_race)
        
        # Apply modified stats back to player
        player.strength = modified_stats['strength']
        player.defense = modified_stats['defense']
        player.magic = modified_stats['magic']
        player.stamina_stat = modified_stats['stamina_stat']
        player.speed = modified_stats['speed']
        player.agility = modified_stats['agility']
        player.willpower = modified_stats['willpower']
        player.luck = modified_stats['luck']
        player.intelligence = modified_stats['intelligence']
        player.talking = modified_stats['talking']
        
        # Apply initial stat allocations from character creation
        if skills:
            stat_mapping = {
                'Strength': 'strength',
                'Defense': 'defense',
                'Magic': 'magic',
                'Stamina': 'stamina_stat',  # Map to correct attribute
                'Speed': 'speed',
                'Agility': 'agility',
                'Willpower': 'willpower',
                'Luck': 'luck',
                'Intelligence': 'intelligence',
                'Talking': 'talking'
            }
            
            logger.info("[NEW GAME] Applying initial stat allocations:")
            for skill_name, points in skills.items():
                attr_name = stat_mapping.get(skill_name)
                if attr_name and points > 0:
                    current = getattr(player, attr_name, 0)
                    setattr(player, attr_name, current + points)
                    logger.info(f"  {skill_name}: {current} + {points} = {getattr(player, attr_name)}")
        
        # Initialize racial trait handler
        from racial_trait_handler import RacialTraitHandler
        player.trait_manager = RacialTraitHandler(player, trait_audio_system, achievement_manager)
        player.racial_traits = selected_race.traits.copy()
        
        logger.info(f"[NEW GAME] Created {selected_race.name} character with {len(player.racial_traits)} racial traits")
        
        # EXPLICITLY reset tree counter for new games (should be 0 from constructor, but ensure it)
        player.trees_broken_count = 0
        # Add respawn manager to player
        player.respawn_manager = respawn_manager
        # Add weather protection methods to player
        add_weather_protection_methods_to_player(player)
        # Initialize inventory and equipment systems
        player.inventory_system = Inventory()
        player.equipment_system = Equipment()
        # Initialize smart inventory manager
        smart_inventory_manager = SmartInventoryManager(player.inventory_system, player)
        smart_inventory_ui = SmartInventoryUI(smart_inventory_manager)
        integrate_smart_inventory_with_player(player, smart_inventory_manager)
        # Initialize recipe discovery system
        from crafting import initialize_player_recipes
        initialize_player_recipes(player)
    else:
        player = Player(config, world)
        # Add respawn manager to player
        player.respawn_manager = respawn_manager
        # Add weather protection methods to player
        add_weather_protection_methods_to_player(player)
        # Initialize inventory and equipment systems
        if not hasattr(player, 'inventory_system'):
            player.inventory_system = Inventory()
        if not hasattr(player, 'equipment_system'):
            player.equipment_system = Equipment()
        # Initialize smart inventory manager
        smart_inventory_manager = SmartInventoryManager(player.inventory_system, player)
        smart_inventory_ui = SmartInventoryUI(smart_inventory_manager)
        # Initialize recipe discovery system (for loaded players)
        from crafting import initialize_player_recipes
        initialize_player_recipes(player)
        integrate_smart_inventory_with_player(player, smart_inventory_manager)
        if menu_action == "load":
            # Use enhanced save system instead of legacy load_game
            from save_system import load_game_enhanced
            slot_id = selected_save_slot.slot_number if hasattr(selected_save_slot, 'slot_number') else 1
            success, message = load_game_enhanced(slot_id, world, player)
            if not success:
                logger.error(f"[LOAD] Failed to load game: {message}")
            
            # Backward compatibility: Initialize race data if not present in save
            if not hasattr(player, 'race_id') or not player.race_id:
                logger.info("[LOAD] Old save detected - initializing default race (Human)")
                from race_system import get_race_by_id
                from racial_trait_handler import RacialTraitHandler
                
                player.race_id = 'human'
                player.race = get_race_by_id('human')
                player.skin_tone = (255, 220, 177)
                player.racial_traits = player.race.traits.copy()
                player.trait_manager = RacialTraitHandler(player, trait_audio_system, achievement_manager)
            
            # Ensure trait manager exists
            if not hasattr(player, 'trait_manager') or not player.trait_manager:
                from race_system import get_race_by_id
                from racial_trait_handler import RacialTraitHandler
                
                race = get_race_by_id(player.race_id)
                if race:
                    player.race = race
                    player.trait_manager = RacialTraitHandler(player, trait_audio_system, achievement_manager)
                    logger.info(f"[LOAD] Initialized trait manager for {race.name}")
            
            # Update trait manager with audio and achievement systems (even if loaded from save)
            if hasattr(player, 'trait_manager') and player.trait_manager:
                player.trait_manager.audio_system = trait_audio_system
                player.trait_manager.achievement_manager = achievement_manager
                logger.info("[LOAD] Updated trait manager with audio and achievement systems")
            
            # Backward compatibility: Initialize dubloons if not present
            if not hasattr(player, 'dubloons'):
                player.dubloons = 0
                logger.info("[LOAD] Old save detected - initialized dubloons to 0")
                # Show error message to user
                error_font = get_font(None, 36)
                error_text = error_font.render(message, True, (255, 80, 80))
                screen.fill((0, 0, 0))
                screen.blit(error_text, (config.SCREEN_WIDTH//2 - error_text.get_width()//2, config.SCREEN_HEIGHT//2))
                
                # Show "Press ESC to return" message
                error_font_small = get_font(None, 24)
                return_text = error_font_small.render("Press ESC to return to main menu", True, (200, 200, 200))
                screen.blit(return_text, (config.SCREEN_WIDTH//2 - return_text.get_width()//2, config.SCREEN_HEIGHT//2 + 50))
                pygame.display.flip()
                
                # Wait for user to press ESC
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            waiting = False
                
                # Return to main menu by restarting main()
                return main()
            else:
                logger.info(f"[LOAD] Successfully loaded game from slot {slot_id}")
            # Restore hotbar system after load
            if hasattr(player, 'hotbar_system'):
                hotbar_system = player.hotbar_system
                logger.info("[HOTBAR] Loaded hotbar from save file")
            
            # Restore tutorial manager state after load
            if hasattr(player, 'tutorials_shown'):
                tutorial_manager.tutorials_shown = player.tutorials_shown
                logger.info("[TUTORIAL] Restored tutorial progress from save file")
    
    # Set game state for save system (after player is created)
    save_integrator.set_game_state(world, player, selected_save_slot)
    
    # Initialize core player stats (if not already set from save file or Player.__init__)
    if not hasattr(player, 'level'):
        player.level = 1
    if not hasattr(player, 'xp'):
        player.xp = 0
    if not hasattr(player, 'dubloons'):
        player.dubloons = 0
    if not hasattr(player, 'max_health'):
        player.max_health = 100
    if not hasattr(player, 'max_stamina'):
        player.max_stamina = 100
    if not hasattr(player, 'max_mana'):
        player.max_mana = 100
    
    # Initialize base attributes (from character creation)
    if not hasattr(player, 'strength'):
        player.strength = player.skills.get('Strength', 0)
    if not hasattr(player, 'agility'):
        player.agility = player.skills.get('Agility', 0)
    if not hasattr(player, 'intelligence'):
        player.intelligence = player.skills.get('Intelligence', 0)
    
    # Initialize combat attributes
    if not hasattr(player, 'last_attack_time'):
        player.last_attack_time = 0
    if not hasattr(player, 'last_contact_damage'):
        player.last_contact_damage = 0
    
    # Initialize movement attributes
    if not hasattr(player, 'is_sprinting'):
        player.is_sprinting = False
    if not hasattr(player, 'last_lshift_state'):
        player.last_lshift_state = False  # Track left shift key state for toggle
    if not hasattr(player, 'last_rshift_state'):
        player.last_rshift_state = False  # Track right shift key state for toggle
    if not hasattr(player, 'is_mayor'):
        player.is_mayor = False
    if not hasattr(player, 'charisma'):
        player.charisma = player.skills.get('Charisma', 0)
    if not hasattr(player, 'endurance'):
        player.endurance = player.skills.get('Endurance', 0)
    
    # Initialize player achievement tracking attributes
    if not hasattr(player, 'ach_enemies_killed'):
        player.ach_enemies_killed = 0
    if not hasattr(player, 'ach_distance_traveled'):
        player.ach_distance_traveled = 0.0
    if not hasattr(player, 'ach_towns_visited'):
        player.ach_towns_visited = 0
    if not hasattr(player, 'ach_dungeons_entered'):
        player.ach_dungeons_entered = 0
    if not hasattr(player, 'ach_quests_completed'):
        player.ach_quests_completed = 0
    if not hasattr(player, 'ach_gold_earned'):
        player.ach_gold_earned = 0
    if not hasattr(player, 'ach_trades_completed'):
        player.ach_trades_completed = 0
    if not hasattr(player, 'ach_meals_cooked'):
        player.ach_meals_cooked = 0
    if not hasattr(player, 'ach_fires_built'):
        player.ach_fires_built = 0
    if not hasattr(player, 'ach_mining_count'):
        player.ach_mining_count = 0
    if not hasattr(player, 'ach_woodcutting_count'):
        player.ach_woodcutting_count = 0
    if not hasattr(player, 'ach_fishing_count'):
        player.ach_fishing_count = 0
    if not hasattr(player, 'ach_deaths'):
        player.ach_deaths = 0
    if not hasattr(player, 'ach_locks_picked'):
        player.ach_locks_picked = 0
    
    # Initialize disease tracking attributes
    if not hasattr(player, 'ach_plague_survived'):
        player.ach_plague_survived = 0  # Boolean 0/1
    if not hasattr(player, 'ach_std_free_years'):
        player.ach_std_free_years = 0  # Count of consecutive years
    if not hasattr(player, 'ach_refugees_saved'):
        player.ach_refugees_saved = 0  # Count of refugees helped
    if not hasattr(player, 'ach_fire_sneeze_arrests'):
        player.ach_fire_sneeze_arrests = 0  # Count of arrests
    if not hasattr(player, 'ach_npcs_cured'):
        player.ach_npcs_cured = 0  # Count of NPCs helped
    if not hasattr(player, 'ach_disease_free_years'):
        player.ach_disease_free_years = 0  # Count of years without disease
    
    # Initialize disease resistance gear tracking
    if not hasattr(player, 'has_plague_doctor_gear'):
        player.has_plague_doctor_gear = False
    if not hasattr(player, 'has_plague_mask'):
        player.has_plague_mask = False
    if not hasattr(player, 'has_plague_robe'):
        player.has_plague_robe = False
    if not hasattr(player, 'has_plague_gloves'):
        player.has_plague_gloves = False
    
    # Initialize disease state tracking
    if not hasattr(player, 'last_std_check'):
        player.last_std_check = 0  # Game day of last STD check
    if not hasattr(player, 'last_disease_day'):
        player.last_disease_day = 0  # Game day of last disease
    
    # Track unique town visits
    if not hasattr(player, 'visited_towns'):
        player.visited_towns = set()
    
    # Give player starting lockpicks (5 for testing lockpicking system)
    if player.inventory.get('lockpick', 0) == 0:
        player.inventory['lockpick'] = 5
        logger.info("[MAIN] Added 5 starting lockpicks to player inventory")
    
    # Helper function to update plague doctor gear status
    def update_plague_doctor_gear_status():
        """Check if player is wearing plague doctor gear and update flags"""
        # Check individual pieces
        head_item = player.equipment.get('head', '')
        chest_item = player.equipment.get('chest', '')
        hands_item = player.equipment.get('hands', '')
        
        # Update individual piece flags
        player.has_plague_mask = ('plague_doctor_mask' in str(head_item))
        player.has_plague_robe = ('plague_doctor_robe' in str(chest_item))
        player.has_plague_gloves = ('plague_doctor_gloves' in str(hands_item))
        
        # Full set bonus: 70% disease resistance when all 3 pieces equipped
        player.has_plague_doctor_gear = (player.has_plague_mask and 
                                          player.has_plague_robe and 
                                          player.has_plague_gloves)
        
        return player.has_plague_doctor_gear
    
    # Initialize spell system (check if attributes exist first for loaded games)
    if not hasattr(player, 'known_spells'):
        player.known_spells = set()
    if not hasattr(player, 'selected_spell'):
        player.selected_spell = None
    if not hasattr(player, 'secondary_spell'):
        player.secondary_spell = None
    if not hasattr(player, 'advanced_spells') or player.advanced_spells is None:
        player.advanced_spells = AdvancedSpellSystem()
    
    # Give player starter spells (only for new games without spells)
    if len(player.known_spells) == 0:
        for spell_id in STARTER_SPELLS:
            player.known_spells.add(spell_id)
        if STARTER_SPELLS:
            player.selected_spell = STARTER_SPELLS[0]
            # Set secondary spell if there are at least 2 starter spells
            if len(STARTER_SPELLS) > 1:
                player.secondary_spell = STARTER_SPELLS[1]

    # Initialize NPC system
    npc_manager = NPCManager()
    starter_npcs = create_starter_npcs()
    for npc in starter_npcs:
        interaction_msg = f"Press E to talk to {npc.name}"
        npc_manager.add_npc(npc, interaction_msg)
    
    # Initialize advanced dialogue system
    advanced_dialogue_ui = AdvancedDialogueUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    # Create Elder Sage tutorial NPC with advanced dialogue
    elder_sage = create_elder_sage_npc(player, start_x=500, start_y=500)
    npc_manager.add_npc(elder_sage, "Press E to talk to Elder Sage")
    logger.info("[DIALOGUE] Advanced dialogue system initialized with Elder Sage NPC")

    # Initialize NPC family system (after interaction system)
    npc_family_system = NPCFamilySystem(game_time, npc_interaction_system)
    
    # Initialize crime and punishment system
    guard_search_system = GuardSearchSystem()
    wanted_system = WantedSystem()
    town_cooldown_system = TownCooldownSystem()
    investigation_system = InvestigationSystem()
    jail_work_system = JailWorkSystem()
    jail_escape_system = JailEscapeSystem()
    player.wanted_level = 0  # Bounty on player's head
    player.crimes_committed = []  # List of crime records
    player.stolen_items = []  # List of stolen items for guard searches
    player.is_wanted = False  # Quick check for wanted status
    player.being_chased_by_guards = False  # Track if guards are actively chasing
    player.in_jail = False  # Track if player is imprisoned
    player.jail_start_day = 0  # Game day when jailed
    player.jail_days = 0  # Number of game days to serve
    player.jail_fine = 0  # Fine to pay for early release
    player.on_the_lamb = False  # Escaped from jail and being hunted
    player.escape_bounty_multiplier = 1.0  # Bounty multiplier for escapees
    logger.info("[CRIME] Crime systems initialized")
    
    # Initialize stealth system (after game_time)
    stealth_system = StealthSystem(game_time)
    stealth_indicator_ui = get_stealth_indicator_ui()
    player.in_stealth_mode = False  # Track stealth mode
    player.detected_by_npcs = []  # List of NPCs that can see player
    logger.info("[STEALTH] Stealth system initialized")
    
    # Initialize break-in and fencing systems
    break_in_system = BreakInSystem()
    fencing_system = FencingSystem()
    fence_manager = FenceManager()
    player.attempting_break_in = False  # Track if player is breaking in
    logger.info("[BREAK-IN] Break-in and fencing systems initialized")
    
    # Initialize comprehensive criminal underworld systems
    thieves_guild = ThievesGuild("Central Town")
    assassins_guild = AssassinsGuild("Eastern Town")
    gang_manager = GangManager()
    gang_manager.initialize_default_gangs()
    criminal_rank_system = CriminalRankSystem()
    protection_racket = ProtectionRacket()
    money_laundering = MoneyLaundering()
    enterprise_manager = EnterpriseManager()
    heist_manager = HeistManager()
    favor_system = FavorSystem()
    criminal_skills = CriminalSkillTree()
    market_manipulation = MarketManipulation()
    scamming_system = ScammingSystem()
    stolen_goods_appraiser = StolenGoodsAppraiser()
    criminal_quests = CriminalQuestSystem()
    
    # Initialize criminal UI and connect systems
    criminal_ui_instance = get_criminal_ui(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    criminal_ui_instance.thieves_guild = thieves_guild
    criminal_ui_instance.assassins_guild = assassins_guild
    criminal_ui_instance.gang_manager = gang_manager
    criminal_ui_instance.criminal_rank_system = criminal_rank_system
    criminal_ui_instance.protection_racket = protection_racket
    criminal_ui_instance.money_laundering = money_laundering
    criminal_ui_instance.enterprise_manager = enterprise_manager
    criminal_ui_instance.heist_manager = heist_manager
    criminal_ui_instance.favor_system = favor_system
    criminal_ui_instance.criminal_skills = criminal_skills
    criminal_ui_instance.market_manipulation = market_manipulation
    criminal_ui_instance.scamming_system = scamming_system
    criminal_ui_instance.stolen_goods_appraiser = stolen_goods_appraiser
    criminal_ui_instance.criminal_quests = criminal_quests
    
    # Player criminal tracking
    player.guild_membership = None  # 'thieves' or 'assassins'
    player.guild_rank = 0  # Rank within guild
    player.criminal_contacts = []  # List of criminal contacts
    player.dirty_money = 0  # Money that needs laundering
    player.underworld_reputation = 0  # Reputation in criminal circles
    logger.info("[CRIMINAL] Comprehensive criminal underworld systems initialized")
    logger.info(f"[CRIMINAL] Thieves Guild: {thieves_guild.name} in {thieves_guild.headquarters_town}")
    logger.info(f"[CRIMINAL] Assassins Guild: {assassins_guild.name} in {assassins_guild.headquarters_town}")
    logger.info(f"[CRIMINAL] Initialized {len(gang_manager.gangs)} gangs")

    
    # CRITICAL FIX: Initialize town system
    town_manager = TownManager()
    
    # Initialize property and financial systems (after town_manager)
    insurance_system = InsuranceSystem(game_time)
    multiple_plots_system = MultiplePlotsSystem(town_manager)
    npc_finances_system = NPCFinancesSystem()
    town_treasury_system = TownTreasurySystem(town_manager)
    guard_protection_fee_system = GuardProtectionFeeSystem()
    property_tax_system = PropertyTaxSystem()
    
    # Initialize player property tracking
    player.owned_properties = []  # List of properties player owns
    player.property_insurance_active = False  # Quick check for insurance
    logger.info("[PROPERTY] Property and financial systems initialized")
    
    # Initialize election system (after town_manager)
    campaign_promise_system = CampaignPromiseSystem()
    election_timeline = ElectionTimeline(game_time)
    ballot_box = BallotBox()
    voter_bribery_system = VoterBriberySystem()
    mayor_term_system = MayorTermSystem()
    anarchy_system = AnarchySystem(mayor_popularity=50)  # Start with neutral popularity
    player.can_vote = True  # Player voting eligibility
    player.voted_this_election = False  # Track if voted in current election
    logger.info("[ELECTION] Election system initialized")
    
    # Initialize mayor powers systems
    curfew_system = CurfewSystem()
    town_entry_fee_system = TownEntryFeeSystem()
    weapon_restriction_system = WeaponRestrictionSystem()
    mayor_salary_system = MayorSalarySystem()
    mayor_absconding_system = MayorAbscondingSystem()
    embargo_system = EmbargoSystem()
    current_mayor = None  # Track current mayor: None, "Player", or NPC reference
    player.curfew_violations = 0  # Track curfew violation count
    player.weapons_stored = []  # Weapons stored during restrictions
    logger.info("[MAYOR] Mayor powers systems initialized")
    
    # Initialize homeless NPC system (after town_manager and npc_family_system)
    homeless_npc_system = HomelessNPCSystem(game_time, town_manager, npc_family_system)
    logger.info("[HOMELESS] Homeless NPC system initialized")
    
    # Initialize NPC housing system (after town_manager)
    npc_housing_system = NPCHousingSystem(game_time, town_manager)
    logger.info("[HOUSING] NPC housing system initialized")
    
    # Initialize NPC skill switching system (after game_time)
    npc_skill_switching_system = NPCSkillSwitchingSystem(game_time)
    logger.info("[SKILL SWITCH] NPC skill switching system initialized")
    
    # Initialize body disposal system
    body_disposal_system = BodyDisposalSystem(game_time)
    player.carrying_body = None  # Track if player is carrying a body
    logger.info("[BODY] Body disposal system initialized")
    
    # Initialize wilderness fighter system
    wilderness_fighter_system = WildernessFighterNPCSystem(config.WORLD_WIDTH, config.WORLD_HEIGHT)
    logger.info("[WILDERNESS] Wilderness fighter system initialized")
    
    # Initialize fast travel system
    fast_travel_system = FastTravelSystem()
    logger.info("[FAST_TRAVEL] Fast travel system initialized")
    
    # Generate 5 towns strategically placed across the world
    # World is 104,000x104,000 pixels, center spawn at (52,000, 52,000)
    # Ocean region starts at ~(69,000, 69,000) in bottom-right
    
    # Central town (near player spawn) - Tutorial/starter area
    main_town = town_manager.create_town("Heartwood Village", 52000, 48000, "medium")
    
    # Northwest town - Forest and lumber region
    northwest_town = town_manager.create_town("Pinecrest Hamlet", 25000, 25000, "small")
    
    # Northeast town - Mountain and mining region
    northeast_town = town_manager.create_town("Stonewatch Outpost", 85000, 25000, "small")
    
    # Southwest town - Plains and farming region
    southwest_town = town_manager.create_town("Meadowbrook Settlement", 25000, 85000, "small")
    
    # Southeast town - Coastal region (near ocean but not on water)
    southeast_town = town_manager.create_town("Wavecrest Harbor", 60000, 60000, "medium")
    
    # Retrofit existing towns with loot box shop if missing (for save compatibility)
    logger.info("[LOOTBOX] Checking towns for MaXxS Silicon Dioxide Shop...")
    for town in town_manager.towns:
        has_lootbox_shop = any(b.type == BuildingType.LOOTBOX_SHOP for b in town.buildings)
        if not has_lootbox_shop:
            # Add the loot box shop
            import random
            angle = random.uniform(0, 3.14159 * 2)
            radius_offset = town.radius * 0.7
            x = town.center_x + int(radius_offset * 0.8 * pygame.math.Vector2(1, 0).rotate_rad(angle).x) - 42
            y = town.center_y + int(radius_offset * 0.8 * pygame.math.Vector2(0, 1).rotate_rad(angle).y) - 47
            
            lootbox_building = Building(BuildingType.LOOTBOX_SHOP, x, y, 85, 95, "MaXxS Silicon Dioxide Shop")
            town.buildings.append(lootbox_building)
            logger.info(f"[LOOTBOX] Added MaXxS Silicon Dioxide Shop to {town.name}")
    
    # Enable curfew for all towns (for testing/gameplay)
    for town in town_manager.towns:
        curfew_system.enable_curfew(town.name)
        logger.info(f"[CURFEW] Enabled curfew for {town.name} (5PM-2AM)")
    
    # Note: Guards will be created after town instances are generated (see below)
    
    # Position NPCs in buildings (main central town)
    # Trader Tom → Shop
    shop_building = main_town.get_building_by_type(BuildingType.SHOP)
    if shop_building and len(starter_npcs) > 1:
        starter_npcs[1].x = shop_building.door_x
        starter_npcs[1].y = shop_building.door_y + 20
        shop_building.npc_id = starter_npcs[1].name
    
    # Elder Sage → Town Hall (or center of town)
    town_hall = main_town.get_building_by_type(BuildingType.TOWN_HALL)
    if town_hall and len(starter_npcs) > 0:
        starter_npcs[0].x = town_hall.door_x if town_hall else main_town.center_x
        starter_npcs[0].y = (town_hall.door_y + 20) if town_hall else main_town.center_y
    
    # NOTE: Max is now created inside the building interior (building_interior.py)
    # via the _place_npcs() method when the interior is generated
    
    logger.info(f"Generated {len(town_manager.towns)} towns across the world with buildings")
    
    # Generate central jail building - far from all towns for maximum security
    # Located in remote northwest corner of map (very far from nearest town)
    jail_x = 8000  # Far northwest - 17,000 pixels from nearest town (Pinecrest Hamlet)
    jail_y = 8000
    jail_building = Building(BuildingType.JAIL, jail_x, jail_y, 150, 180)  # Large imposing structure
    logger.info(f"[JAIL] Created central jail: {jail_building.name} at remote location ({jail_x}, {jail_y})")
    logger.info(f"[JAIL] Nearest town is ~17km away - escaping will be challenging!")
    
    # Initialize market economy system (Level 15+ feature)
    logger.info("Initializing market economy system...")
    initialize_commodities()  # Load all tradeable items
    market_manager = MarketManager(game_time, weather_system)
    
    # Register markets for each town
    for town in town_manager.towns:
        market_manager.register_town_market(town.name)
        logger.info(f"Registered market for {town.name}")
    
    # Initialize with starter supplies
    market_manager.initialize_starter_supplies()
    logger.info(f"Market economy ready - {len(market_manager.town_markets)} markets online")
    
    # Store market_manager reference for save/load
    player.market_manager = market_manager  # Store reference on player for save/load
    
    # Initialize trade route system (after town_manager and market_manager)
    trade_route_system = TradeRouteSystem(game_time, town_manager, market_manager)
    logger.info("[TRADE] Trade route system initialized")

    entities = EntityManager(config, world)
    
    # Enemy system
    enemies_list = []
    enemy_spawn_timer = 0
    enemy_spawn_interval = 8.0  # Spawn enemies every 8 seconds
    MAX_ENEMIES = 100  # Maximum enemies on screen (reduced to prevent overcrowding near towns)
    max_enemies = MAX_ENEMIES  # Keep old variable for compatibility
    dropped_equipment_list = []  # Track dropped items from enemies
    
    # Floating damage numbers system
    floating_texts = []  # Track all floating text (damage numbers, combat events)
    
    # Combat particle effects system
    combat_particles = CombatParticleManager()
    
    # Hit-stop system for impactful attacks
    hit_stop_active = False
    hit_stop_duration = 0.0
    hit_stop_timer = 0.0
    
    # Combat log system
    combat_log = CombatLog(max_entries=15, position="bottom-right")
    combat_log_font = get_font(None, 18)
    
    # Enhanced loot system
    enhanced_loot = get_enhanced_loot_system()
    boss_loot_preview = get_boss_loot_preview_ui()
    set_bonus_display = get_set_bonus_display_ui()
    
    # Boss loot preview state
    pending_dungeon_entry = {
        'active': False,
        'dungeon': None,
        'entrance_pos': None,
        'entrance_coords': None
    }
    
    # Dungeon variety system
    dungeon_variety = get_dungeon_variety_system()
    dungeon_info_ui = get_dungeon_info_ui()
    speed_run_timer_ui = get_speed_run_timer_ui()
    trap_warning_ui = get_trap_warning_ui()
    secret_discovered_ui = get_secret_discovered_ui()
    dungeon_modifier_selection_ui = get_dungeon_modifier_selection_ui()
    
    # Summoning and necromancy system (initialized with body_disposal_system for unified corpse tracking)
    summoning_system = initialize_summoning_system(body_disposal_system)
    summon_info_ui = get_summon_info_ui()
    necromancy_indicator_ui = get_necromancy_indicator_ui()
    summon_cast_effect_ui = get_summon_cast_effect_ui()
    
    # Spell system
    spell_projectiles = []  # Active spell projectiles
    spell_effects = []  # Visual spell effects
    
    # Performance optimization: Tilemap cache
    tilemap_cache = {}
    tilemap_cache_frame = 0
    TILEMAP_CACHE_LIFETIME = 120  # Refresh every 120 frames (2 seconds at 60fps)
    
    # Pre-generate tilemap cache around player spawn to prevent first-attack stutter
    logger.info("[OPTIMIZATION] Pre-generating tilemap cache...")
    player_tile_x = int(player.x // config.TILE_SIZE)
    player_tile_y = int(player.y // config.TILE_SIZE)
    
    # Pre-generate cache in a 100x100 tile radius around player spawn
    for cache_tile_x in range((player_tile_x - 50) // 10, (player_tile_x + 50) // 10 + 1):
        for cache_tile_y in range((player_tile_y - 50) // 10, (player_tile_y + 50) // 10 + 1):
            cache_key = (cache_tile_x, cache_tile_y)
            
            # Calculate center of this cache region
            center_tile_x = cache_tile_x * 10
            center_tile_y = cache_tile_y * 10
            
            # Build local tilemap for this region
            local_tilemap = []
            for ty in range(max(0, center_tile_y - 10), min(world.height // config.TILE_SIZE, center_tile_y + 10)):
                row = []
                for tx in range(max(0, center_tile_x - 10), min(world.width // config.TILE_SIZE, center_tile_x + 10)):
                    tile = world.get_tile(tx * config.TILE_SIZE, ty * config.TILE_SIZE)
                    tile_type = "grass"  # default
                    if tile and "ground" in tile:
                        tile_type = tile["ground"]
                    row.append({"type": tile_type})
                local_tilemap.append(row)
            tilemap_cache[cache_key] = local_tilemap
    
    logger.info(f"[OPTIMIZATION] Pre-generated {len(tilemap_cache)} tilemap cache regions")
    
    # Performance optimization: Status multiplier cache
    cached_status_multipliers = None
    
    # Performance optimization: Entity culling distance
    ENTITY_UPDATE_DISTANCE = 600  # Only update enemies within this distance from player (aggressively reduced for better performance)
    MAX_ACTIVE_ENEMY_UPDATES = 15  # Only run full AI updates for the nearest N enemies per frame
    
    # Performance optimization: Time-based update accumulators (better than frame counters)
    npc_update_accumulator = 0.0  # Accumulate delta time for NPC updates
    gatherer_update_accumulator = 0.0  # Accumulate delta time for gatherer updates
    family_update_accumulator = 0.0  # Accumulate delta time for family updates
    multipliers_cache_time = 0.0
    
    # Update intervals in seconds
    NPC_UPDATE_INTERVAL = 0.033  # ~30 FPS for NPCs (every other frame at 60 FPS)
    GATHERER_UPDATE_INTERVAL = 0.066  # ~15 FPS for gatherers (every 4 frames at 60 FPS)
    FAMILY_UPDATE_INTERVAL = 0.5  # Update family system twice per second
    
    # Initialize camera position (prevents jumping on first attack)
    camera_x = player.x - config.SCREEN_WIDTH // 2
    camera_y = player.y - config.SCREEN_HEIGHT // 2
    
    # Performance optimization: Inflated player rect cache
    cached_player_collision_rect = None
    player_pos_cache = (0, 0)
    
    # Spawn some initial enemies only for new games (not when loading)
    if menu_action == "new":
        for i in range(5):
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(1000, 1500)  # Spawn 1000-1500 pixels away (off-screen)
            spawn_x = player.x + int(distance * math.cos(angle))
            spawn_y = player.y + int(distance * math.sin(angle))
            enemy_type = random.choice(["slime", "wolf", "goblin", "bat", "caterpillar"])
            enemies_list.append(spawn_enemy(spawn_x, spawn_y, enemy_type, player.level))
        logger.info(f"[ENEMY SYSTEM] Spawned {len(enemies_list)} initial enemies for new game")
    else:
        logger.info(f"[ENEMY SYSTEM] Skipping initial enemy spawn for loaded game")
    logger.info(f"[SPELL SYSTEM] Initialized. Primary: {player.selected_spell}, Secondary: {player.secondary_spell}")
    
    # Spawn wilderness fighters in wilderness areas (far from towns)
    for _ in range(8):  # Spawn 8 wilderness fighters across the world
        # Pick random wilderness location far from all towns
        wilderness_found = False
        attempts = 0
        while not wilderness_found and attempts < 20:
            attempts += 1
            fighter_x = random.randint(1000, config.WORLD_WIDTH - 1000)
            fighter_y = random.randint(1000, config.WORLD_HEIGHT - 1000)
            
            # Check distance from all towns - must be at least 5000 units away
            min_town_distance = 5000
            all_towns_far = True
            for town in town_manager.towns:
                town_dist = ((fighter_x - town.center_x) ** 2 + (fighter_y - town.center_y) ** 2) ** 0.5
                if town_dist < min_town_distance:
                    all_towns_far = False
                    break
            
            if all_towns_far:
                wilderness_found = True
                fighter_level = random.randint(5, 15)
                fighter_name = random.choice([
                    "Wilderness Warrior", "Forest Hunter", "Wild Berserker", 
                    "Lone Wanderer", "Mountain Scout", "Desert Outlaw"
                ])
                fighter = wilderness_fighter_system.spawn_fighter(
                    npc_id=f"wilderness_fighter_{_}",
                    name=fighter_name,
                    level=fighter_level
                )
                if fighter:
                    logger.info(f"[WILDERNESS] Spawned {fighter_name} (Lvl {fighter_level}) at camp ({fighter_x}, {fighter_y})")

    # Track previous day for weather updates
    previous_day = game_time.day_count
    weather_message = None
    weather_message_timer = 0
    
    # Level up notification
    level_up_message = None
    level_up_timer = 0
    
    # Death system
    player_died = False
    death_message = None
    death_message_timer = 0
    show_death_screen = False
    death_screen_option = 0  # 0 = Load Save, 1 = Return to Main Menu
    
    # Key bindings system
    key_bindings = get_key_bindings()
    keybindings_ui = get_keybindings_ui(key_bindings)
    
    # Mouse button state tracking for combat actions
    combat_mouse_buttons = {MOUSE_LEFT: False, MOUSE_MIDDLE: False, MOUSE_RIGHT: False}
    # Keyboard attack key state tracking (for event-based detection)
    combat_attack_keys = {}
    
    # FPS text cache (only regenerate when value changes)
    cached_fps_text = {}
    last_cached_fps = -1
    
    # Crafting system
    crafting_ui = get_crafting_ui(config)
    show_crafting_menu = False
    show_repair_menu = False
    
    # Stick equip confirmation system
    stick_confirm_dialog = {'active': False, 'pending_item': None, 'action': None}
    
    # Repair system
    repair_system = get_repair_system()
    
    # Locked chest system
    chest_manager = get_chest_manager()
    # Spawn some initial chests in the world (away from player start)
    for _ in range(8):
        chest_x = random.randint(200, config.WORLD_WIDTH - 200)
        chest_y = random.randint(200, config.WORLD_HEIGHT - 200)
        # Don't spawn too close to player starting position
        if abs(chest_x - config.WORLD_WIDTH // 2) > 300 or abs(chest_y - config.WORLD_HEIGHT // 2) > 300:
            chest_manager.spawn_chest(chest_x, chest_y)
    
    # Locked chest system
    chest_manager = get_chest_manager()
    # Spawn some initial chests in the world
    for _ in range(8):
        chest_x = random.randint(100, config.WORLD_WIDTH - 100)
        chest_y = random.randint(100, config.WORLD_HEIGHT - 100)
        chest_manager.spawn_chest(chest_x, chest_y)
    show_keybindings_menu = False
    
    # Dungeon state
    in_dungeon = False
    current_dungeon = None
    dungeon_entrance_pos = None
    dungeon_entrances = []  # List of (x, y) positions with dungeon entrances
    dungeon_instances = {}  # CRITICAL FIX: Track dungeon instance for each entrance (key: entrance coords)
    
    # Town instance state
    in_town = False
    current_town_instance = None
    town_return_pos = None
    town_gates = {}  # Dict mapping town -> (gate_x, gate_y) on overworld
    town_instances = {}  # Dict mapping town -> town instance
    
    # Generate dungeon entrances near each town (2 dungeons per town = 10 total)
    random.seed(42)  # Consistent dungeon locations
    for town in town_manager.towns:
        # Create 2 dungeons near each town (within 3000-8000 pixel radius)
        for _ in range(2):
            # Random offset from town center
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.randint(3000, 8000)
            dx = int(town.center_x + distance * math.cos(angle))
            dy = int(town.center_y + distance * math.sin(angle))
            
            # Clamp to world boundaries
            dx = max(200, min(config.WORLD_WIDTH - 200, dx))
            dy = max(200, min(config.WORLD_HEIGHT - 200, dy))
            
            entrance_pos = (dx, dy)
            dungeon_entrances.append(entrance_pos)
            # Initialize each dungeon instance as None (will be created on first entry)
            dungeon_instances[entrance_pos] = None
    
    logger.info(f"Generated {len(dungeon_entrances)} dungeon entrances across all towns")
    
    # Generate town gates (just outside south side of each town)
    for town in town_manager.towns:
        # Place gate just outside the south (bottom) edge of town
        gate_x = town.center_x
        gate_y = town.center_y + town.radius + config.TILE_SIZE  # 1 tile outside the town boundary
        town_gates[town.name] = (gate_x, gate_y)
        logger.info(f"Generated gate for {town.name} at ({gate_x}, {gate_y})")
    
    logger.info(f"Generated {len(town_gates)} town gates")
    
    # Pre-create all town instances and initialize their buildings
    logger.info("Pre-creating town instances and initializing services...")
    try:
        for town in town_manager.towns:
            # Determine town size based on radius
            if town.radius > 400:
                town_size = "large"
            elif town.radius > 250:
                town_size = "medium"
            else:
                town_size = "small"
            
            # Create the town instance
            town_instance = create_town_instance(town.name, town_size)
            town_instances[town.name] = town_instance
            logger.info(f"Created town instance: {town.name} ({town_size}) with {len(town_instance.buildings)} buildings")
    except Exception as e:
        logger.error(f"CRITICAL ERROR creating town instances: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info(f"Pre-created {len(town_instances)} town instances")
    
    # Initialize inn system and register all inns from town instances
    inn_manager = InnManager()
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            if building.type == BuildingType.INN:
                inn_manager.register_inn(building, town_name)
    logger.info(f"Registered {len(inn_manager.inns)} inns from town instances")
    
    # Initialize blacksmith system and register all blacksmiths from town instances
    blacksmith_manager = BlacksmithManager()
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            if building.type == BuildingType.BLACKSMITH:
                blacksmith_manager.register_blacksmith(building, town_name)
    logger.info(f"Registered {len(blacksmith_manager.blacksmiths)} blacksmiths from town instances")
    
    # Initialize tavern system and register all taverns from town instances
    tavern_manager = TavernManager()
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            if building.type == BuildingType.TAVERN:
                tavern_manager.register_tavern(building, town_name)
                # Create a fence for each town (near tavern)
                fence_manager.create_fence_for_town(town_name, building.x, building.y)
    logger.info(f"Registered {len(tavern_manager.taverns)} taverns from town instances")
    logger.info(f"Created {len(fence_manager.fences)} fences (undiscovered)")
    
    # Initialize temple system and register all temples from town instances
    temple_manager = TempleManager()
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            if building.type == BuildingType.TEMPLE:
                temple_manager.register_temple(building, town_name)
    logger.info(f"Registered {len(temple_manager.temples)} temples from town instances")
    
    # Initialize mage system and register all mage towers from town instances
    mage_manager = MageManager()
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            if building.type == BuildingType.MAGE_TOWER:
                mage = Mage(building, town_name)
                mage_manager.register_mage(mage)
    logger.info(f"Registered {len(mage_manager.mages)} mage towers from town instances")
    
    # Initialize bank system and register all banks from town instances
    bank_manager = BankManager()
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            if building.type == BuildingType.BANK:
                bank_manager.register_bank(building, town_name)
    logger.info(f"Registered {len(bank_manager.banks)} banks from town instances")
    
    # Initialize library system
    library_manager = LibraryManager()
    library_ui = LibraryUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    # Initialize mage UI
    mage_ui = MageUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    logger.info(f"[MAGE] Mage service UI initialized")
    
    # Create libraries for each town (one per town, near town center)
    for town_name, town_instance in town_instances.items():
        # Find town center (use town hall or first building as reference)
        town_center_x = town_instance.width // 2
        town_center_y = town_instance.height // 2
        
        for building in town_instance.buildings:
            if building.type == BuildingType.TOWN_HALL:
                town_center_x = building.x
                town_center_y = building.y
                break
        
        # Create library near town center
        library_x = town_center_x + random.randint(-150, 150)
        library_y = town_center_y + random.randint(-150, 150)
        library = Library(f"library_{town_name}", town_name, library_x, library_y)
        library_manager.register_library(library)
    logger.info(f"Created {len(library_manager.libraries)} libraries (one per town)")
    
    # Create and add guard NPCs for each town instance (using town instance coordinates)
    town_guards = []
    for town_name, town_instance in town_instances.items():
        # Find town hall in this instance
        town_hall = None
        for building in town_instance.buildings:
            if building.type == BuildingType.TOWN_HALL:
                town_hall = building
                break
        
        if town_hall:
            # Create 2 patrolling guards per town
            import math
            import random
            
            # Define town bounds with margin
            margin = 100
            town_width = town_instance.width
            town_height = town_instance.height
            
            for guard_num in range(2):
                # Create patrol guard starting at random position
                start_x = random.randint(margin, town_width - margin)
                start_y = random.randint(margin, town_height - margin)
                
                guard_name = f"{town_name} Guard {guard_num + 1}" if guard_num > 0 else f"{town_name} Guard"
                patrol_guard = BasicNPC(
                    guard_name, 
                    start_x, 
                    start_y, 
                    "guard", 
                    sprite_color=(150, 50, 50)
                )
                
                # Generate random patrol points distributed across the entire town
                # Each guard gets a unique, unpredictable route
                patrol_points = []
                num_points = random.randint(8, 12)  # Variable number of patrol points
                
                # Divide town into grid sections to ensure good coverage
                grid_size = 3  # 3x3 grid
                sections = []
                for grid_x in range(grid_size):
                    for grid_y in range(grid_size):
                        section_width = town_width // grid_size
                        section_height = town_height // grid_size
                        sections.append((
                            grid_x * section_width,
                            grid_y * section_height,
                            section_width,
                            section_height
                        ))
                
                # Shuffle sections and pick patrol points from different areas
                random.shuffle(sections)
                for i in range(num_points):
                    section = sections[i % len(sections)]
                    sx, sy, sw, sh = section
                    # Random point within this section
                    px = random.randint(sx + margin, min(sx + sw - margin, town_width - margin))
                    py = random.randint(sy + margin, min(sy + sh - margin, town_height - margin))
                    patrol_points.append((px, py))
                
                patrol_guard.set_patrol_points(patrol_points)
                patrol_guard.current_town = town_name
                town_guards.append(patrol_guard)
                npc_manager.add_npc(patrol_guard, f"Press E to talk to {patrol_guard.name}")
                
                # Create vision cone for patrol guard (will update direction as they patrol)
                stealth_system.create_vision_cone(patrol_guard.name, start_x, start_y, direction=0, range_distance=150, angle=90)
    
    logger.info(f"Created {len(town_guards)} guard NPCs for {len(town_instances)} town instances")
    
    # Connect bank manager to player for auto-bank perk (level 75+)
    player.bank_manager = bank_manager
    
    # Initialize shop system and register all shop buildings from town instances
    shop_manager = ShopManager()
    shop_manager.embargo_system = embargo_system  # For embargo fee tracking
    shop_manager.town_treasury_system = town_treasury_system  # For fee deposits
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            if building.type == BuildingType.SHOP:
                shop_manager.register_shop(building, town_name)
                logger.info(f"Registered shop '{building.name}' in {town_name}")
    logger.info(f"Registered {len(shop_manager.shops)} shops from town instances")
    
    # Initialize merchant reputation system
    merchant_reputation_manager = MerchantReputationManager()
    shop_manager.reputation_manager = merchant_reputation_manager  # Connect to shop system
    logger.info("[MAIN] Merchant reputation system initialized")
    
    # Initialize dynamic inventory system
    dynamic_inventory_manager = DynamicInventoryManager()
    for shop_id, shop_data in shop_manager.shops.items():
        town_name = shop_data['town_name']
        dynamic_inventory_manager.register_shop(shop_id, town_name)
    shop_manager.dynamic_inventory = dynamic_inventory_manager
    logger.info("[MAIN] Dynamic inventory system initialized with town specializations")
    
    # Initialize haggling and bartering systems
    haggling_system = HagglingSystem()
    bartering_system = BarteringSystem()
    shop_manager.haggling_system = haggling_system
    shop_manager.bartering_system = bartering_system
    logger.info("[MAIN] Haggling and bartering systems initialized")
    
    # Initialize special orders system
    special_order_manager = SpecialOrderManager()
    shop_manager.special_order_manager = special_order_manager
    logger.info("[MAIN] Special orders and commissions system initialized")
    
    # Initialize trade routes & caravan system
    caravan_manager = CaravanManager()
    # Register town positions for caravan routing (use world map positions from town_manager)
    for town in town_manager.towns:
        caravan_manager.register_town_position(town.name, town.center_x, town.center_y)
    logger.info("[MAIN] Trade routes and caravan system initialized")
    
    # Initialize shop ownership system
    shop_ownership_manager = ShopOwnershipManager()
    # Make some shops available for purchase
    shop_ownership_manager.list_shop_for_sale("player_shop_1", "Heartwood Village", 5000)
    shop_ownership_manager.list_shop_for_sale("player_shop_2", "Wavecrest Harbor", 7000)
    logger.info("[MAIN] Shop ownership system initialized with available shops")
    
    # Initialize smuggling and criminal economy
    smuggling_system = SmugglingSystem()
    # Create some black market vendors
    smuggling_system.create_black_market_vendor(
        "black_market_1", 
        "Shadowy Figure", 
        "Dark alley behind the tavern in Stonewatch Outpost",
        "nightfall"
    )
    smuggling_system.create_black_market_vendor(
        "black_market_2",
        "The Fence",
        "Abandoned warehouse at Wavecrest Harbor docks",
        "goldenkey"
    )
    logger.info("[MAIN] Smuggling and criminal economy system initialized")
    
    # Initialize price fluctuation events
    price_event_manager = PriceEventManager()
    shop_manager.price_event_manager = price_event_manager  # Connect to shop system
    logger.info("[MAIN] Price fluctuation events system initialized")
    
    # Initialize merchant quests and loyalty programs
    merchant_quest_manager = MerchantQuestManager()
    shop_manager.merchant_quest_manager = merchant_quest_manager  # Connect to shop system
    logger.info("[MAIN] Merchant quests and loyalty programs initialized")

    # Initialize minimap
    minimap = Minimap(size=220, position='top-right')
    
    # Initialize full-screen map
    fullscreen_map = FullscreenMap(tile_size=config.TILE_SIZE)
    
    # Initialize quest and reputation systems
    reputation_system = ReputationSystem()
    quest_manager = QuestManager(reputation_system)
    quest_log_ui = QuestLogUI()
    quest_tracker_ui = QuestTrackerUI()
    
    # Initialize town hall system and register all town halls from town instances (requires quest_manager)
    town_hall_manager = TownHallManager(weather_system, game_time, quest_manager)
    for town_name, town_instance in town_instances.items():
        # Get the corresponding town object
        town = next((t for t in town_manager.towns if t.name == town_name), None)
        if town:
            for building in town_instance.buildings:
                if building.type == BuildingType.TOWN_HALL:
                    town_hall_manager.register_town_hall(building, town_name, town)
    logger.info(f"Registered {len(town_hall_manager.town_halls)} town halls from town instances")
    
    # Initialize gathering nodes system (resource nodes for skills)
    gathering_nodes_manager = GatheringNodesManager()
    gathering_nodes_manager.generate_world_nodes(config.WORLD_WIDTH, config.WORLD_HEIGHT, town_manager.towns, world)
    logger.info(f"Generated {gathering_nodes_manager.get_node_count()} gathering nodes")
    
    # Spawn tutorial NPC if tutorial not completed
    tutorial_shack = None  # Will be created dynamically when NPC goes to shelter
    if not player.tutorial_completed:
        # Check if we have saved NPC state (from loaded game)
        if hasattr(player, 'tutorial_npc_saved_state') and player.tutorial_npc_saved_state:
            saved_state = player.tutorial_npc_saved_state
            # Recreate NPC from saved state
            tutorial_npc = TutorialNPC(saved_state['x'], saved_state['y'])
            tutorial_npc.health = saved_state.get('health', 275)
            tutorial_npc.max_health = saved_state.get('max_health', 275)
            tutorial_npc.declined_by_player = saved_state.get('declined_by_player', False)
            tutorial_npc.going_to_shelter = saved_state.get('going_to_shelter', False)
            tutorial_npc.at_shelter = saved_state.get('at_shelter', False)
            tutorial_npc.shack_x = saved_state.get('shack_x', None)
            tutorial_npc.shack_y = saved_state.get('shack_y', None)
            tutorial_npc.in_building = saved_state.get('in_building', None)
            player.tutorial_npc = tutorial_npc
            
            # Recreate the shack if it was created
            if tutorial_npc.shack_x and tutorial_npc.shack_y:
                tutorial_shack = Building(BuildingType.SHACK, 
                                        tutorial_npc.shack_x - 30,
                                        tutorial_npc.shack_y - 40, 
                                        60, 80, name="Wandering Guide's Shack")
                tutorial_shack.is_enterable = True
                
                # Create the shack interior
                shack_interior = BuildingInterior(
                    BuildingType.SHACK,
                    width=400,
                    height=400
                )
                building_interiors["TUTORIAL_SHACK"] = shack_interior
                logger.info(f"[TUTORIAL] Recreated shack at ({tutorial_npc.shack_x}, {tutorial_npc.shack_y})")
            
            logger.info(f"[TUTORIAL] NPC restored from save at ({tutorial_npc.x}, {tutorial_npc.y}), in_building={tutorial_npc.in_building}")
            # Clean up the saved state
            del player.tutorial_npc_saved_state
        else:
            # First time spawning - use default position
            tutorial_npc = TutorialNPC(player.x + 120, player.y - 80)
            player.tutorial_npc = tutorial_npc
            # Restore tutorial stage to NPC
            if hasattr(player, 'tutorial_stage'):
                tutorial_npc.update_tutorial_stage(player.tutorial_stage)
                logger.info(f"[TUTORIAL] Tutorial NPC spawned - Stage: {player.tutorial_stage}")
        
        # Quest will be started when player accepts it in dialogue (not auto-started)
    
    # Initialize economic systems early (needed before NPC registration)
    investment_system = InvestmentSystem(shop_manager, game_time)
    investment_system.initialize_market(shop_manager)
    logger.info(f"[INVESTMENT] Stock market initialized with {len(investment_system.stock_market.stocks)} shops")
    
    town_trade_agreement_system = TownTradeAgreementSystem(town_manager, game_time)
    town_trade_agreement_system.initialize_relationships()
    logger.info(f"[TRADE AGREEMENTS] System initialized for {len(town_manager.towns)} towns")
    
    npc_trade_engine = NPCTradeEngine(shop_manager, market_manager, town_manager)
    logger.info("[NPC TRADE] NPC trade engine initialized")
    
    npc_contract_system = NPCContractSystem(trade_route_system)
    logger.info("[NPC CONTRACTS] Contract system initialized")
    
    # Initialize gatherer NPC system (Phase 1: Basic gathering NPCs)
    gatherer_npc_manager = GathererNPCManager()
    for town in town_manager.towns:
        # OPTIMIZATION: Spawn only 1 gatherer per town instead of 3 for better performance
        gatherer_npc_manager.spawn_gatherers_for_town(town, gathering_nodes_manager, config, max_gatherers=1)
    # Connect bank manager to NPCs
    for npc in gatherer_npc_manager.npcs:
        npc.bank_manager = bank_manager
        npc.world = world  # Give NPCs access to world for tile modification
    logger.info(f"Spawned {len(gatherer_npc_manager.npcs)} gatherer NPCs across {len(town_manager.towns)} towns")
    
    # Register all NPCs with the NPC Finances System for regular payments
    for npc in gatherer_npc_manager.npcs:
        # Check if NPC is a merchant or mayor (for future expansion)
        is_merchant = getattr(npc, 'is_merchant', False)
        is_mayor = getattr(npc, 'is_mayor', False)
        npc_finances_system.add_npc(npc, is_merchant=is_merchant, is_mayor=is_mayor)
    logger.info(f"[PROPERTY] Registered {len(gatherer_npc_manager.npcs)} NPCs with finance system")
    
    # Auto-assign housing to gatherer NPCs
    assigned_count = npc_housing_system.auto_assign_homeless_npcs(gatherer_npc_manager.npcs)
    housing_stats = npc_housing_system.get_housing_stats()
    logger.info(f"[HOUSING] Initial assignments - Housed: {assigned_count}, Homeless: {housing_stats['homeless']}")
    
    # Spawn companions at inns
    companion_count = 0
    for town in town_manager.towns:
        for building in town.buildings:
            if hasattr(building, 'building_type') and building.building_type == 'inn':
                companion_manager.spawn_companions_at_inn(building, town.name)
                companion_count += 5  # 5 companion types per inn
                break  # Only spawn at first inn in town
    logger.info(f"[COMPANION] Spawned {companion_count} companions at {len(town_manager.towns)} inns")
    
    # Register gatherer NPCs with trading system
    for npc in gatherer_npc_manager.npcs:
        npc_trade_engine.register_gatherer_npc(npc)
        investment_system.register_npc_investor(npc)
        npc_contract_system.register_npc(npc)
    
    # Spawn traveling merchants (1-2 per town)
    traveling_merchant_count = 0
    for town in town_manager.towns:
        if random.random() < 0.6:  # 60% chance per town
            merchant = npc_trade_engine.spawn_traveling_merchant(town, config)
            traveling_merchant_count += 1
    
    logger.info(f"[ECONOMY] Registered {len(gatherer_npc_manager.npcs)} NPCs with trading system and {traveling_merchant_count} traveling merchants")
    
    # Establish trade routes between all towns (after towns are set up)
    routes_established = trade_route_system.establish_trade_routes()
    logger.info(f"[TRADE] Established {routes_established} trade routes between towns")
    
    # Initialize dialogue system
    dialogue_manager = DialogueManager(reputation_system, quest_manager)
    dialogue_ui = DialogueUI()
    dialogue_history_ui = DialogueHistoryUI()
    
    # Initialize smoke effect system
    from smoke_effect import SmokeEffect
    smoke_effect = SmokeEffect()
    
    # Initialize tutorial system
    tutorial_manager = TutorialManager()
    tutorial_popup = TutorialPopupUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    tutorial_npc = None  # Will be created if tutorial not completed
    
    # Initialize mayor powers UI
    mayor_powers_ui = MayorPowersUI()
    mayor_powers_ui.curfew_system = curfew_system
    mayor_powers_ui.weapon_restriction_system = weapon_restriction_system
    mayor_powers_ui.town_entry_fee_system = town_entry_fee_system
    mayor_powers_ui.embargo_system = embargo_system
    mayor_powers_ui.town_treasury_system = town_treasury_system
    mayor_powers_ui.game_time = game_time
    logger.info("[MAYOR UI] Mayor powers UI initialized")
    
    # Initialize shop UI
    shop_ui = ShopUI()
    shop_ui.shop_manager = shop_manager  # For looking up town names
    shop_ui.embargo_system = embargo_system  # For embargo fee checks
    shop_ui.town_treasury_system = town_treasury_system  # For fee deposits
    
    # Initialize advanced trading systems
    quality_manager = QualitySystemManager()
    time_sales_manager = TimeBasedSalesManager(game_time)
    appraisal_system = AppraisalSystem()
    consignment_manager = ConsignmentAuctionManager(game_time)
    
    # Initialize building expansion systems
    market_stall_system = MarketStallSystem()
    safety_deposit_system = SafetyDepositSystem()
    
    # Initialize shop ownership UI
    shop_ownership_ui = ShopOwnershipUI()
    
    # Initialize economic events UI
    economic_events_ui = EconomicEventsUI()
    
    # Initialize trading menu UI
    trading_menu_ui = TradingMenuUI()
    
    # Initialize bartering UI
    bartering_ui = BarteringUI()
    
    # Initialize advanced trading UI
    advanced_trading_ui = AdvancedTradingUI()
    
    # Initialize building expansion UIs
    tavern_food_ui = TavernFoodTradingUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    market_stall_ui = MarketStallUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    safety_deposit_ui = SafetyDepositBoxUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    # Initialize advanced trading UI
    advanced_trading_ui = AdvancedTradingUI()
    
    # Create shops for merchant NPCs (for dialogue-based trading)
    for npc in starter_npcs:
        if 'merchant' in npc.name.lower():
            shop = shop_manager.create_shop(npc.name, npc.name, merchant_type="general")
            logger.info(f"Created NPC shop for {npc.name}")
    
    # Initialize inn UI
    inn_ui = InnUI(config)
    
    # Initialize blacksmith UI
    blacksmith_ui = BlacksmithUI(config)
    
    # Initialize repair menu UI
    repair_menu_ui = RepairMenuUI(config, player)
    
    # Initialize tavern UI
    tavern_ui = TavernUI(config)
    tavern_ui.food_trading_ui = tavern_food_ui  # Link food trading UI
    
    # Initialize temple UI
    temple_ui = TempleUI(config)
    
    # Initialize bank UI
    bank_ui = BankUI(config)
    bank_ui.insurance_system = insurance_system  # Make insurance system accessible in bank UI
    bank_ui.multiple_plots_system = multiple_plots_system  # Make property system accessible
    bank_ui.town_treasury_system = town_treasury_system  # Make treasury system accessible
    bank_ui.game_time = game_time  # Make game time accessible for loan system
    bank_ui.safety_deposit_ui = safety_deposit_ui  # Link safety deposit UI
    bank_ui.safety_deposit_system = safety_deposit_system  # Link safety deposit system
    
    # Initialize town hall UI
    town_hall_ui = TownHallUI(config)
    
    # Initialize cooking system
    fire_manager = FireManager()
    cooking_ui = CookingUI(config)
    
    # Initialize leaderboard system
    leaderboard_system = LeaderboardSystem('leaderboards.json')
    leaderboard_ui = LeaderboardUI(config, leaderboard_system)
    
    # Initialize achievement UI (achievement_manager already initialized earlier)
    achievement_ui = AchievementUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    achievement_popup = AchievementPopup()
    
    # Initialize bestiary system
    from enemies import ENEMY_TYPES, ENEMY_RARITIES
    bestiary = Bestiary(ENEMY_TYPES, ENEMY_RARITIES)
    player.bestiary = bestiary  # Attach to player for save/load
    logger.info("[BESTIARY] Bestiary system initialized")
    
    # Set up cooking achievement tracking
    def on_cooking_success():
        player.ach_meals_cooked += 1
        achievement_manager.check_all_survival(
            0,  # days_survived - tracked elsewhere
            player.ach_meals_cooked,
            player.ach_fires_built
        )
        unlocked = achievement_manager.get_recent_unlock()
        if unlocked:
            achievement_popup.show(unlocked)
            logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
    
    cooking_ui.on_cook_success = on_cooking_success
    
    # Initialize pet system with achievements
    pet_companion = PetCompanion()
    pet_companion.achievement_manager = achievement_manager
    pet_menu_ui = PetMenuUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    # Initialize skills UI
    skills_ui = SkillsUI()
    
    # Initialize market UI
    market_ui = MarketUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    market_ui_active_town = None
    
    # Initialize trade route UI
    trade_route_ui = TradeRouteUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    logger.info("[TRADE UI] Trade route UI initialized")
    
    # Initialize stock market UI (economic systems already initialized earlier)
    stock_market_ui = StockMarketUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    stock_market_ui.investment_system = investment_system
    stock_market_ui.town_trade_agreement_system = town_trade_agreement_system
    stock_market_ui.player = player
    logger.info("[STOCK UI] Stock market UI initialized")
    
    # Initialize NPC skill switching UI
    npc_skill_switching_ui = NPCSkillSwitchingUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    # Initialize companion system
    companion_manager = CompanionManager()
    companion_hiring_ui = CompanionHiringUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    companion_hiring_ui.companion_manager = companion_manager
    companion_hiring_ui.player = player
    companion_hiring_ui.game_time = game_time
    logger.info("[MAIN] Companion system initialized")
    logger.info("[COMPANION] Companion system initialized")
    
    # Initialize NPC combat enhancements
    npc_combat_manager = NPCCombatManager()
    logger.info("[MAIN] NPC combat enhancements initialized")
    logger.info("[COMBAT] Combat enhancement system initialized")
    
    # Initialize insurance system
    insurance_provider = InsuranceProvider()
    player_insurance_ui = PlayerInsuranceUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    player_insurance_ui.insurance_provider = insurance_provider
    player_insurance_ui.player = player
    player_insurance_ui.game_time = game_time
    logger.info("[MAIN] Insurance system initialized")
    logger.info("[INSURANCE] Insurance provider initialized")
    
    #Initialize NPC role adaptation system
    npc_role_adaptation = NPCRoleAdaptationSystem()
    logger.info("[MAIN] NPC role adaptation initialized")
    logger.info("[ADAPTATION] Role adaptation system initialized")
    
    # Initialize newspaper system
    newspaper_generator = NewspaperGenerator()
    newspaper_distribution = NewspaperDistribution()
    newspaper_ui = NewspaperUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    current_newspaper = None  # Will be generated daily
    logger.info("[MAIN] Newspaper system initialized")
    logger.info("[NEWSPAPER] Newspaper system ready")
    
    # Initialize disease system
    disease_manager = DiseaseManager()
    logger.info("[MAIN] Disease system initialized")
    logger.info("[DISEASE] Disease manager ready with {} disease definitions".format(len(DISEASE_DEFINITIONS)))
    
    # Store references in player for temple/UI access
    player.disease_manager = disease_manager
    player.game_time = game_time
    
    # Initialize commodity exchange UI
    commodity_exchange_ui = CommodityExchangeUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    commodity_exchange_ui.market_manager = market_manager
    commodity_exchange_ui.player = player
    logger.info("[MAIN] Commodity exchange initialized")
    logger.info("[EXCHANGE] Commodity exchange ready")
    
    # Initialize economics skill tree
    economics_skill_tree = EconomicsSkillTree()
    economics_skill_tree.initialize_player_skills(player)
    economics_skill_tree_ui = EconomicsSkillTreeUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    economics_skill_tree_ui.skill_tree = economics_skill_tree
    economics_skill_tree_ui.player = player
    commodity_exchange_ui.economics_skill_tree = economics_skill_tree
    logger.info("[MAIN] Economics skill tree initialized")
    logger.info("[ECONOMICS] Skill tree ready with {len(economics_skill_tree.skills)} skills")
    
    # Initialize hotbar system
    hotbar_system = HotbarSystem(num_slots=9)
    hotbar_ui = HotbarUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    logger.info("[HOTBAR] Hotbar system initialized with 9 slots")
    
    # Attach hotbar to player for easy save/load
    player.hotbar_system = hotbar_system
    
    # Initialize cosmetic system (loot box parody!)
    cosmetic_manager = CosmeticManager()
    lootbox_shop = LootBoxShop()
    max_shop_interaction = MaxShopInteraction()
    lootbox_animation = LootBoxAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    cosmetic_menu = CosmeticEquipMenu(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    show_cosmetic_menu = False
    logger.info("[COSMETICS] MaXxS Silicon Dioxide Shop system initialized")
    
    # Attach cosmetic manager to player
    player.cosmetic_manager = cosmetic_manager
    player.lootbox_shop = lootbox_shop
    
    # Auto-assign common items to hotbar on first load (NO SPELLS - spells use Q/E keys and spell HUD)
    if not hasattr(player, 'hotbar_initialized'):
        # Auto-assign potions to first slots (if player has them)
        if 'health_potion' in player.inventory and player.inventory.get('health_potion', 0) > 0:
            hotbar_system.set_slot_item(0, 'health_potion', 'Health Potion', HotbarSlotType.ITEM)
            logger.info("[HOTBAR] Auto-assigned Health Potion to slot 1")
        if 'mana_potion' in player.inventory and player.inventory.get('mana_potion', 0) > 0:
            hotbar_system.set_slot_item(1, 'mana_potion', 'Mana Potion', HotbarSlotType.ITEM)
            logger.info("[HOTBAR] Auto-assigned Mana Potion to slot 2")
        
        # NOTE: Spells are NOT added to hotbar - they're managed through spell HUD (bottom-right)
        # Primary spell (Q key), Secondary spell (E key)
        logger.info("[HOTBAR] Spells use Q/E keys and spell HUD panel, not hotbar slots")
        
        player.hotbar_initialized = True
    
    logger.info("[SKILL SWITCH UI] NPC skill switching UI initialized")
    
    # Track active blessings from temples
    active_blessings = []
    

    
    # Add completed_quests to player if it doesn't exist
    if not hasattr(player, 'completed_quests'):
        player.completed_quests = set()
    
    # Town tracking
    current_town = None
    
    # Building interior tracking
    in_building_interior = False
    current_interior = None
    current_interior_building = None
    current_interior_building_id = None
    building_interiors = {}  # Dict of building_id → BuildingInterior instance
    
    # Achievement check counter (check every 60 frames = 1 second)
    achievement_check_counter = 0
    town_message = ""
    town_message_timer = 0
    
    show_equipment = False
    equip_menu_state = {'slot_idx': 0, 'inv_idx': 0, 'mode': 'equip'}
    show_new_equipment_ui = False  # New Diablo-style equipment UI
    show_inventory = False
    curfew_warning_dialog = {'active': False, 'town_name': None}  # Curfew entry warning
    fast_travel_menu = {'active': False, 'selected_idx': 0}
    inn_offer_dialog = {'active': False, 'town_name': None}  # Inn offer when no properties  # Fast travel menu
    stick_stack_confirmation = {'active': False, 'item': None}  # Confirmation dialog for stacking sticks
    show_stats_menu = False
    show_character_sheet = False  # Character equipment sheet (press E)
    show_crime_history = False
    debug_mode = False  # Toggle with F7 for vision cones and other debug visuals
    inventory_menu_state = {'submenu': 0, 'item_idx': 0}
    inventory_sort_mode = 'default'  # Options: 'default', 'rarity', 'level', 'value', 'type'
    inventory_categories = ['Food', 'Weapons', 'Equipment', 'Quest Items', 'Other']
    items_by_cat = {c: [] for c in inventory_categories}  # Built items list for inventory display
    
    # Campaign promise menu
    showing_campaign_menu = False
    campaign_menu_state = {'selected_idx': 0, 'selected_promises': [], 'all_promises': []}
    
    # Auto-loot filter settings
    auto_loot_enabled = True
    auto_loot_min_rarity = 'uncommon'  # Options: 'common', 'uncommon', 'rare', 'epic', 'legendary'
    
    running = True
    inventory_action_msg = ""
    inventory_inspect_item = None
    inventory_inspect_timer = 0
    show_pause_menu = False
    pause_menu_options = [
        "Resume", "Save Game", "Load Game", "Help", "Settings", "Achievements", "Bestiary", "Performance", "Accessibility", "Font Settings", "AI Settings", "Exit to Main Menu", "Quit Game"
    ]
    pause_menu_idx = 0
    pause_menu_rects = []
    pause_menu_mouse_pos = None
    show_settings_menu = False
    show_achievements = False
    show_bestiary = False
    bestiary_selected_enemy = None
    bestiary_scroll_offset = 0
    show_performance_menu = False
    show_accessibility_menu = False
    show_font_settings = False
    show_ai_settings = False
    settings_options = [
        ("Audio Volume", 5, 0, 10),
        ("Music Volume", 5, 0, 10),
        ("Fullscreen", False, [False, True]),
        ("Language", 0, 0, len(config.LANGUAGES)-1),
        ("Font Size", 32, 16, 64),
        ("Equipment Degradation", True, [False, True]),
        ("Auto-Scrap Common/Uncommon", False, [False, True]),
        ("Key Bindings", None, None),
    ]
    settings_idx = 0
    settings_menu_rects = []
    settings_menu_mouse_pos = None
    # Settings state (could be loaded/saved)
    settings_state = {
        "Audio Volume": 5,
        "Music Volume": 5,
        "Fullscreen": False,
        "Language": 0,
        "Font Size": 32,
        "Equipment Degradation": True,
        "Auto-Scrap Common/Uncommon": False,
    }
    
    # Initialize building interiors for all buildings in town instances
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            # Create unique ID for this building
            building_id = f"{town_name}_{building.name}"
            # Generate interior based on building type with economy systems
            # Use smaller size for lootbox shop (560x400 instead of default 1400x1000)
            if building.type == BuildingType.LOOTBOX_SHOP:
                interior = BuildingInterior(
                    building.type,
                    width=560,
                    height=400,
                    town_name=town_name,
                    town_treasury_system=town_treasury_system,
                    bank_manager=bank_manager,
                    weapon_restriction_system=weapon_restriction_system
                )
            else:
                interior = BuildingInterior(
                    building.type,
                    town_name=town_name,
                    town_treasury_system=town_treasury_system,
                    bank_manager=bank_manager,
                    weapon_restriction_system=weapon_restriction_system
                )
            building_interiors[building_id] = interior
    logger.info(f"Generated {len(building_interiors)} building interiors")
    
    # Generate standalone jail building interior
    jail_building_id = f"STANDALONE_{jail_building.name}"
    jail_interior = BuildingInterior(
        jail_building.type,
        town_name="None",  # Jail is not in any town
        town_treasury_system=town_treasury_system,
        bank_manager=bank_manager,
        weapon_restriction_system=weapon_restriction_system
    )
    building_interiors[jail_building_id] = jail_interior
    logger.info(f"[JAIL] Generated interior for standalone jail: {jail_building_id}")
    
    # ===== HELPER FUNCTION: RECORD CRIME =====
    def record_crime_with_rank(crime_type: str, location: str, item: str = None, 
                               witnessed: bool = False, witness: str = None):
        """
        Helper function to record crime and update criminal rank system
        
        Args:
            crime_type: Type of crime ('theft', 'burglary', 'assault', 'murder', 'smuggling', 'extortion')
            location: Where crime occurred
            item: Item involved (for theft/burglary)
            witnessed: Whether crime was witnessed
            witness: Name of witness if applicable
        """
        # Create crime record for existing system
        crime_record = {
            'type': crime_type,
            'location': location,
            'day': game_time.day_count
        }
        if item:
            crime_record['item'] = item
        if witnessed:
            crime_record['witnessed'] = True
            crime_record['witness'] = witness
        
        # Add to player's crime history
        player.crimes_committed.append(crime_record)
        
        # Update criminal rank system
        criminal_rank_system.add_crime(crime_type)
        
        # Check for quest unlocks if this is first time being caught
        if witnessed and criminal_quests:
            unlocked_quests = criminal_quests.unlock_quests_on_caught()
            if unlocked_quests:
                logger.info(f"[QUEST] Unlocked {len(unlocked_quests)} criminal quests from being caught!")
        
        logger.info(f"[CRIME] Recorded {crime_type} at {location} (Total: {criminal_rank_system.crime_count})")
    
    # ===========================================
    
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Death screen event handling (highest priority)
            if show_death_screen:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        death_screen_option = 0
                    elif event.key == pygame.K_DOWN:
                        death_screen_option = 1
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        if death_screen_option == 0:
                            # Load Save
                            show_death_screen = False
                            player_died = False
                            # Reset building interior state (in case player died inside a building)
                            in_building_interior = False
                            current_interior = None
                            current_interior_building = None
                            current_interior_building_id = None
                            save_integrator.open_load_dialog()
                        elif death_screen_option == 1:
                            # Return to Main Menu
                            return main()
                elif event.type == pygame.MOUSEMOTION:
                    # Highlight option on hover
                    mouse_x, mouse_y = event.pos
                    box_x = config.SCREEN_WIDTH // 2 - 400
                    box_y = config.SCREEN_HEIGHT // 2 - 200
                    for i in range(2):
                        y_pos = box_y + 220 + (i * 60)
                        if box_x + 150 <= mouse_x <= box_x + 650 and y_pos <= mouse_y <= y_pos + 40:
                            death_screen_option = i
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Click to select
                    if death_screen_option == 0:
                        show_death_screen = False
                        player_died = False
                        # Reset building interior state (in case player died inside a building)
                        in_building_interior = False
                        current_interior = None
                        current_interior_building = None
                        current_interior_building_id = None
                        save_integrator.open_load_dialog()
                    elif death_screen_option == 1:
                        return main()
                continue  # Block all other input while death screen is active
            
            # Enhanced save system event handling
            if save_integrator.handle_event(event):
                continue  # Event was consumed by save system
            
            # Dialogue UI event handling (high priority - blocks other input)
            if advanced_dialogue_ui.active:
                if advanced_dialogue_ui.handle_input(event):
                    # Update quest marker for NPCs after dialogue ends
                    if advanced_dialogue_ui.current_npc and hasattr(advanced_dialogue_ui.current_npc, 'update_quest_marker'):
                        advanced_dialogue_ui.current_npc.update_quest_marker()
                continue  # Event was consumed by dialogue system
            
            # Tutorial popup event handling (blocks other input when active)
            if tutorial_popup.active:
                if tutorial_popup.handle_input(event, tutorial_manager):
                    continue  # Event was consumed by tutorial popup
            
            # Handle mouse events for pause menu
            if show_pause_menu and event.type == pygame.MOUSEMOTION:
                pause_menu_mouse_pos = event.pos
                for i, rect in enumerate(pause_menu_rects):
                    if rect.collidepoint(pause_menu_mouse_pos):
                        pause_menu_idx = i
                        break
            elif show_pause_menu and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pause_menu_mouse_pos = event.pos
                    for i, rect in enumerate(pause_menu_rects):
                        if rect.collidepoint(pause_menu_mouse_pos):
                            pause_menu_idx = i
                            # Trigger selection
                            fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
                            pygame.event.post(fake_event)
                            break
            
            # Handle mouse events for settings menu
            if show_settings_menu and event.type == pygame.MOUSEMOTION:
                settings_menu_mouse_pos = event.pos
                for i, rect in enumerate(settings_menu_rects):
                    if rect.collidepoint(settings_menu_mouse_pos):
                        settings_idx = i
                        break
            elif show_settings_menu and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click on setting to toggle/select
                    settings_menu_mouse_pos = event.pos
                    for i, rect in enumerate(settings_menu_rects):
                        if rect.collidepoint(settings_menu_mouse_pos):
                            settings_idx = i
                            opt = settings_options[settings_idx]
                            # Toggle boolean options or activate selection
                            if opt[0] in ["Fullscreen", "Equipment Degradation", "Auto-Scrap Common/Uncommon"]:
                                settings_state[opt[0]] = not settings_state[opt[0]]
                                if opt[0] == "Equipment Degradation":
                                    repair_system.enabled = settings_state[opt[0]]
                                elif opt[0] == "Auto-Scrap Common/Uncommon":
                                    repair_system.auto_scrap_enabled = settings_state[opt[0]]
                            elif opt[0] == "Key Bindings":
                                show_keybindings_menu = True
                            break
                pause_menu_mouse_pos = event.pos
                for i, rect in enumerate(pause_menu_rects):
                    if rect.collidepoint(pause_menu_mouse_pos):
                        pause_menu_idx = i
                        break
            elif show_pause_menu and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pause_menu_mouse_pos = event.pos
                    for i, rect in enumerate(pause_menu_rects):
                        if rect.collidepoint(pause_menu_mouse_pos):
                            pause_menu_idx = i
                            # Trigger selection
                            fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
                            pygame.event.post(fake_event)
                            break
            
            # Pet menu UI handles its own input when active
            if pet_menu_ui.active:
                selected_pet = pet_menu_ui.handle_input(event, pet_companion)
                if selected_pet:
                    town_message = f"Pet selected: {selected_pet.title()}!"
                    town_message_timer = 120
                continue
            
            # Market UI handles its own input when active
            if market_ui.active:
                result = market_ui.handle_event(event, market_manager, player)
                if result:
                    if result.get("type") == "buy":
                        buy_result = result["result"]
                        if buy_result[0]:  # success
                            logger.info(f"[MARKET] {buy_result[1]}")
                            # Award merchant XP (1 XP per 10 gold spent)
                            xp_amount = int(buy_result[2] / 10)
                            player.skills_manager.add_xp("Merchant", xp_amount)
                            
                            # Track trading stats
                            player.ach_trades_completed += 1
                            # Buying doesn't earn gold
                            achievement_manager.check_all_economy(player.ach_gold_earned, player.ach_trades_completed)
                            
                            # Check special achievements (merchant skill level)
                            merchant_level = player.skills_manager.get_level('Merchant')
                            achievement_manager.check_special(merchant_level, 0)  # 0 for deathless tracking
                            
                            unlocked = achievement_manager.get_recent_unlock()
                            if unlocked:
                                achievement_popup.show(unlocked)
                                logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                        else:
                            logger.warning(f"[MARKET] {buy_result[1]}")
                    elif result.get("type") == "sell":
                        sell_result = result["result"]
                        if sell_result[0]:  # success
                            logger.info(f"[MARKET] {sell_result[1]}")
                            # Award merchant XP (1 XP per 10 gold earned)
                            xp_amount = int(sell_result[2] / 10)
                            player.skills_manager.add_xp("Merchant", xp_amount)
                            
                            # Track trading stats
                            player.ach_trades_completed += 1
                            player.ach_gold_earned += sell_result[2]  # Gold earned from sale
                            achievement_manager.check_all_economy(player.ach_gold_earned, player.ach_trades_completed)
                            
                            # Check special achievements (merchant skill level)
                            merchant_level = player.skills_manager.get_level('Merchant')
                            achievement_manager.check_special(merchant_level, 0)  # 0 for deathless tracking
                            
                            unlocked = achievement_manager.get_recent_unlock()
                            if unlocked:
                                achievement_popup.show(unlocked)
                                logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                        else:
                            logger.warning(f"[MARKET] {sell_result[1]}")
                    elif result.get("type") == "error":
                        logger.warning(f"[MARKET] {result['message']}")
                continue
            
            # Trade route UI handles its own input when active
            if trade_route_ui.active:
                current_town_name = current_town.name if current_town else None
                result = trade_route_ui.handle_input(event, trade_route_system, player, current_town_name)
                if result:
                    town_message = result
                    town_message_timer = 180
                continue
            
            # NPC skill switching UI handles its own input when active
            if npc_skill_switching_ui.active:
                npc_skill_switching_ui.handle_input(event)
                continue
            
            # Handle curfew warning dialog (highest priority)
            if curfew_warning_dialog['active'] and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Enter town anyway
                    town_name = curfew_warning_dialog['town_name']
                    town_inst = town_instances.get(town_name)
                    if town_inst:
                        # Update global town instance
                        current_town_instance = town_inst
                        town_return_pos = (player.x, player.y)
                        player.is_wanted = wanted_system.get_wanted_status(id(player), game_time)
                        entry_fee = town_entry_fee_system.charge_entry(player, town_treasury_system, town_name)
                        if entry_fee > 0:
                            town_message = f"💰 Entry Fee: {entry_fee}g"
                            town_message_timer = 180
                        in_town = True
                        enemies_list.clear()
                        if weapon_restriction_system.restriction_active:
                            confiscated_weapons = weapon_restriction_system.enforce(player, town_name)
                            if confiscated_weapons:
                                player.weapons_stored = confiscated_weapons
                        player.x = current_town_instance.gate_x
                        player.y = current_town_instance.gate_y
                        town_message = f"⚠️ Entered during curfew! Stay hidden!"
                        town_message_timer = 180
                        logger.info(f"[CURFEW] Player entered {town_name} during curfew")
                    curfew_warning_dialog['active'] = False
                    curfew_warning_dialog['town_name'] = None
                elif event.key == pygame.K_f:
                    # Fast travel - check if player has any property-based locations
                    available_locations = fast_travel_system.get_available_locations()
                    if available_locations:
                        # Player has properties, show fast travel menu
                        fast_travel_menu['active'] = True
                        fast_travel_menu['selected_idx'] = 0
                        curfew_warning_dialog['active'] = False
                        logger.info(f"[CURFEW] Opened fast travel menu")
                    else:
                        # No properties, offer inn travel
                        logger.info(f"[CURFEW] No properties, activating inn offer dialog for {curfew_warning_dialog['town_name']}")
                        inn_offer_dialog['active'] = True
                        inn_offer_dialog['town_name'] = curfew_warning_dialog['town_name']
                        curfew_warning_dialog['active'] = False
                        logger.info(f"[CURFEW] inn_offer_dialog is now active={inn_offer_dialog['active']}, town={inn_offer_dialog['town_name']}")
                    continue
                elif event.key == pygame.K_ESCAPE:
                    curfew_warning_dialog['active'] = False
                    curfew_warning_dialog['town_name'] = None
                    town_message = "Town entry cancelled"
                    town_message_timer = 120
                continue
            
            # Handle inn offer dialog
            if inn_offer_dialog['active'] and event.type == pygame.KEYDOWN:
                logger.info(f"[INN_TELEPORT] Inn offer dialog is active, received keydown event: {event.key}")
                if event.key == pygame.K_y:
                    # Travel to inn
                    town_name = inn_offer_dialog['town_name']
                    logger.info(f"[INN_TELEPORT] Y pressed, attempting teleport to {town_name}")
                    town_inst = town_instances.get(town_name)
                    if town_inst:
                        logger.info(f"[INN_TELEPORT] Town instance found for {town_name}")
                        # Update global town instance
                        current_town_instance = town_inst
                        # Find inn in this town
                        inn_building = None
                        for building in current_town_instance.buildings:
                            if building.type == BuildingType.INN:
                                inn_building = building
                                logger.info(f"[INN_TELEPORT] Found INN: {building.name} at ({building.door_x}, {building.door_y})")
                                break
                        
                        if inn_building:
                            # First, teleport player to town gate (enter town properly)
                            town_return_pos = (player.x, player.y)
                            player.is_wanted = wanted_system.get_wanted_status(id(player), game_time)
                            
                            # Move player to town gate FIRST
                            player.x = current_town_instance.gate_x
                            player.y = current_town_instance.gate_y
                            logger.info(f"[INN_TELEPORT] Moved player to town gate ({player.x}, {player.y})")
                            
                            # Now set in_town after player is positioned
                            in_town = True
                            enemies_list.clear()
                            
                            # Enforce weapon restrictions if active
                            if weapon_restriction_system.restriction_active:
                                confiscated_weapons = weapon_restriction_system.enforce(player, town_name)
                                if confiscated_weapons:
                                    player.weapons_stored = confiscated_weapons
                            
                            # Check if interior exists
                            building_id = f"{town_name}_{inn_building.name}"
                            logger.info(f"[INN_TELEPORT] Checking for interior: {building_id}")
                            if building_id in building_interiors:
                                # Enter the interior
                                in_building_interior = True
                                current_interior = building_interiors[building_id]
                                current_interior_building = inn_building
                                current_interior_building_id = building_id
                                
                                # Reset to floor 1 when entering (fixes multi-floor buildings)
                                current_interior.current_floor = 1
                                
                                # Fix old inn staircases that are in wrong location (legacy save compatibility)
                                if current_interior.num_floors > 1:
                                    for obj in current_interior.objects:
                                        if obj.type == "staircase":
                                            # Check if staircase is in old position (x=300, y=600)
                                            if obj.x == 300 and obj.y == 600:
                                                # Update to new position (near spawn)
                                                new_x = current_interior.width // 2 - 150
                                                new_y = current_interior.height - 280
                                                obj.x = new_x
                                                obj.y = new_y
                                                logger.info(f"[INTERIOR] Updated staircase position from old location to ({new_x}, {new_y})")
                                
                                # Position player at spawn point INSIDE
                                spawn_x, spawn_y = current_interior.get_spawn_position()
                                player.x = spawn_x
                                player.y = spawn_y
                                logger.info(f"[INN_TELEPORT] Positioned player at interior spawn ({spawn_x}, {spawn_y})")
                                
                                town_message = "Fast traveled to the inn interior!"
                                town_message_timer = 180
                            else:
                                # No interior exists - place at inn door in town
                                logger.info(f"[INN_TELEPORT] No interior found, placing at inn door ({inn_building.door_x}, {inn_building.door_y})")
                                player.x = inn_building.door_x
                                player.y = inn_building.door_y
                                town_message = "Fast traveled to the inn!"
                                town_message_timer = 180
                        else:
                            logger.error(f"[INN_TELEPORT] No INN building found in {town_name}!")
                            logger.info(f"[INN_TELEPORT] Buildings in town: {[b.type for b in current_town_instance.buildings]}")
                            town_message = "No inn found! Walk in like a peasant."
                            town_message_timer = 180
                    else:
                        logger.error(f"[INN_TELEPORT] Town instance not found for {town_name}!")
                    inn_offer_dialog['active'] = False
                    inn_offer_dialog['town_name'] = None
                    curfew_warning_dialog['active'] = False
                    curfew_warning_dialog['town_name'] = None
                elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    # Go back to curfew warning
                    curfew_warning_dialog['active'] = True
                    curfew_warning_dialog['town_name'] = inn_offer_dialog['town_name']
                    inn_offer_dialog['active'] = False
                    inn_offer_dialog['town_name'] = None
                continue
            
            # Handle boss loot preview dismissal
            if boss_loot_preview.active and event.type == pygame.KEYDOWN:
                # Any key dismisses the preview and enters the dungeon
                boss_loot_preview.active = False
                
                if pending_dungeon_entry['active']:
                    current_dungeon = pending_dungeon_entry['dungeon']
                    dungeon_entrance_pos = pending_dungeon_entry['entrance_pos']
                    selected_entrance = pending_dungeon_entry['entrance_coords']
                    
                    # Enter dungeon
                    in_dungeon = True
                    
                    # Track dungeon entry for achievements
                    player.ach_dungeons_entered += 1
                    achievement_manager.check_all_exploration(
                        player.ach_towns_visited,
                        player.ach_distance_traveled,
                        player.ach_dungeons_entered
                    )
                    unlocked = achievement_manager.get_recent_unlock()
                    if unlocked:
                        achievement_popup.show(unlocked)
                        logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                    
                    # CRITICAL FIX: Clear overworld enemies and load dungeon enemies
                    enemies_list.clear()
                    if hasattr(current_dungeon, 'enemies'):
                        enemies_list.extend(current_dungeon.enemies)
                        logger.info(f"Loaded {len(current_dungeon.enemies)} dungeon enemies")
                    
                    # CRITICAL FIX: Load dungeon loot
                    dropped_equipment_list.clear()
                    if hasattr(current_dungeon, 'loot'):
                        dropped_equipment_list.extend(current_dungeon.loot)
                        logger.info(f"Loaded {len(current_dungeon.loot)} dungeon loot items")
                    
                    # Move player to dungeon entrance
                    if current_dungeon.entrance:
                        player.x = current_dungeon.entrance[0] * config.TILE_SIZE
                        player.y = current_dungeon.entrance[1] * config.TILE_SIZE
                        logger.info(f"Entered dungeon at entrance {current_dungeon.entrance}")
                    elif hasattr(current_dungeon, 'rooms') and current_dungeon.rooms:
                        start_room = current_dungeon.rooms[0]
                        player.x = (start_room['x'] + start_room['width'] // 2) * config.TILE_SIZE
                        player.y = (start_room['y'] + start_room['height'] // 2) * config.TILE_SIZE
                        logger.info(f"Entered dungeon with {len(current_dungeon.rooms)} rooms")
                    else:
                        player.x = 30 * config.TILE_SIZE
                        player.y = 20 * config.TILE_SIZE
                        logger.info("Entered dungeon (no entrance marker)")
                    
                    # Clear pending state
                    pending_dungeon_entry['active'] = False
                    pending_dungeon_entry['dungeon'] = None
                    pending_dungeon_entry['entrance_pos'] = None
                    pending_dungeon_entry['entrance_coords'] = None
                    
                    logger.info("[LOOT] Boss loot preview dismissed, entering dungeon")
                continue
            
            # Handle fast travel menu
            if fast_travel_menu['active'] and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    fast_travel_menu['active'] = False
                    if curfew_warning_dialog['town_name']:
                        curfew_warning_dialog['active'] = True
                elif event.key == pygame.K_UP:
                    fast_travel_menu['selected_idx'] = max(0, fast_travel_menu['selected_idx'] - 1)
                elif event.key == pygame.K_DOWN:
                    available = fast_travel_system.get_available_locations()
                    fast_travel_menu['selected_idx'] = min(len(available) - 1, fast_travel_menu['selected_idx'] + 1)
                elif event.key == pygame.K_RETURN:
                    available = fast_travel_system.get_available_locations()
                    if available and fast_travel_menu['selected_idx'] < len(available):
                        location_name = available[fast_travel_menu['selected_idx']]
                        success, message, dest_x, dest_y = fast_travel_system.travel_to(player, location_name)
                        if success:
                            player.x = dest_x
                            player.y = dest_y
                            town_message = f"Fast traveled to {location_name}"
                            town_message_timer = 180
                            fast_travel_menu['active'] = False
                            curfew_warning_dialog['active'] = False
                            curfew_warning_dialog['town_name'] = None
                continue
            
            # Handle jail actions (highest priority when in jail)
            if player.in_jail:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        # Pay fine for early release
                        if player.dubloons >= player.jail_fine:
                            player.dubloons -= player.jail_fine
                            player.in_jail = False
                            player.jail_start_day = 0
                            player.jail_days = 0
                            player.wanted_level = 0
                            town_message = f"Paid {player.jail_fine}g fine. You are free to go."
                            town_message_timer = 180
                            paid_amount = player.jail_fine
                            player.jail_fine = 0
                            # Clear jail work record
                            if id(player) in jail_work_system.jail_sentences:
                                del jail_work_system.jail_sentences[id(player)]
                            logger.info(f"[JAIL] Player paid {paid_amount}g fine for early release")
                        else:
                            town_message = "Not enough dubloons for early release!"
                            town_message_timer = 120
                    elif event.key == pygame.K_w:
                        # Work a day to reduce sentence
                        days_served = game_time.day_count - player.jail_start_day
                        days_remaining = player.jail_days - days_served
                        
                        if days_remaining > 0:
                            # Advance time by 1 day
                            game_time.day_count += 1
                            jail_work_system.work_day(id(player))
                            
                            new_days_remaining = player.jail_days - (game_time.day_count - player.jail_start_day)
                            town_message = f"⚒️ You worked hard all day.\nSentence reduced! {new_days_remaining} days remaining."
                            town_message_timer = 240
                            logger.info(f"[JAIL] Player worked a day. Days remaining: {new_days_remaining}")
                        else:
                            town_message = "Your sentence is complete! Walk free."
                            town_message_timer = 180
                    elif event.key == pygame.K_b:
                        # Multi-stage jail escape system!
                        
                        # Check if player already started an escape
                        if id(player) not in jail_escape_system.player_stages:
                            # Start new escape attempt
                            jail_escape_system.start_escape(id(player))
                            town_message = "🔓 Starting escape...\n📍 Stage: CELL DOOR\nAttempting to pick the lock..."
                            town_message_timer = 240
                            logger.info(f"[JAILBREAK] Player started escape attempt")
                        else:
                            # Continue escape attempt - try to advance to next stage
                            current_stage = jail_escape_system.player_stages[id(player)]
                            stage_index = jail_escape_system.escape_stages.index(current_stage)
                            required_skill = jail_escape_system.stage_lockpicking[current_stage]
                            
                            # Calculate success chance based on player level and stage difficulty
                            skill_levels = {'basic': 20, 'improved': 40, 'advanced': 60, 'master': 80}
                            needed_skill = skill_levels[required_skill]
                            player_skill = player.level * 10  # Each level = 10 lockpicking skill
                            
                            # Base 50% chance, +2% per skill point over requirement, -2% per skill point under
                            skill_difference = player_skill - needed_skill
                            success_chance = 50 + (skill_difference * 2)
                            success_chance = max(10, min(90, success_chance))  # Clamp between 10-90%
                            
                            roll = random.randint(1, 100)
                            
                            if roll <= success_chance:
                                # Success! Advance to next stage
                                if stage_index < len(jail_escape_system.escape_stages) - 1:
                                    next_stage = jail_escape_system.escape_stages[stage_index + 1]
                                    jail_escape_system.player_stages[id(player)] = next_stage
                                    
                                    stage_names = {
                                        'cell': 'CELL DOOR',
                                        'block': 'CELL BLOCK',
                                        'entrance': 'JAIL ENTRANCE',
                                        'gate': 'OUTER GATE'
                                    }
                                    
                                    town_message = f"✅ SUCCESS! Passed {stage_names[current_stage]}!\n📍 Next Stage: {stage_names[next_stage]}\nPress B again to continue..."
                                    town_message_timer = 300
                                    logger.info(f"[JAILBREAK] Advanced from {current_stage} to {next_stage}")
                                else:
                                    # Final stage passed - ESCAPE!
                                    del jail_escape_system.player_stages[id(player)]
                                    
                                    player.in_jail = False
                                    player.jail_start_day = 0
                                    player.jail_days = 0
                                    player.jail_fine = 0
                                    
                                    # Now you're ON THE LAMB - wanted with 3x bounty multiplier
                                    player.on_the_lamb = True
                                    player.is_wanted = True
                                    player.escape_bounty_multiplier = 3.0
                                    player.wanted_level = int(player.wanted_level * 3)  # Triple the bounty
                                    wanted_system.set_wanted(id(player), 'jailbreak', game_time)
                                    
                                    # Massive reputation loss for jailbreak
                                    if in_town and current_town_instance:
                                        reputation_system.modify_faction_reputation(current_town_instance.name, -150)
                                        logger.info(f"[REPUTATION] Lost 150 reputation with {current_town_instance.name} for jailbreak")
                                    
                                    # Ban from ALL towns for 7 days after jailbreak
                                    if in_town and current_town_instance:
                                        # Set extended cooldown for jailbreak (7 days instead of 3)
                                        town_cooldown_system.cooldowns[id(player)] = {
                                            'town': 'ALL_TOWNS',  # Special marker for all towns
                                            'end_day': game_time.day_count + 7
                                        }
                                        logger.warning(f"[COOLDOWN] Player banned from ALL TOWNS for 7 days after jailbreak!")
                                    
                                    town_message = f"🚨 JAILBREAK SUCCESSFUL!\nYou escaped but are now ON THE LAMB\nBounty TRIPLED to {player.wanted_level}g!"
                                    town_message_timer = 360
                                    logger.warning(f"[JAILBREAK] Player escaped from jail! Bounty tripled to {player.wanted_level}g")
                                    
                                    # Teleport outside the town hall
                                    for building in current_town_instance.buildings:
                                        if building.type == BuildingType.TOWN_HALL:
                                            player.x = building.x - 150
                                            player.y = building.y - 100
                                            break
                            else:
                                # Failed at this stage - caught!
                                jail_escape_system.caught_escaping(id(player), jail_work_system)
                                
                                # Clear escape progress
                                if id(player) in jail_escape_system.player_stages:
                                    del jail_escape_system.player_stages[id(player)]
                                
                                # Add time to sentence
                                additional_days = 10
                                player.jail_days += additional_days
                                
                                stage_names = {
                                    'cell': 'CELL DOOR',
                                    'block': 'CELL BLOCK',
                                    'entrance': 'JAIL ENTRANCE',
                                    'gate': 'OUTER GATE'
                                }
                                
                                town_message = f"❌ CAUGHT at {stage_names[current_stage]}!\n🚨 Guards found you!\n+{additional_days} days added to sentence"
                                town_message_timer = 300
                                logger.info(f"[JAILBREAK] Escape attempt failed at {current_stage}, +{additional_days} days added")
                continue  # Skip all other input while in jail
            
            # Smart inventory handles its own input when active
            if smart_inventory_ui.active:
                smart_inventory_ui.handle_input(event)
                continue
            
            # Full-screen map handles ALL events (keyboard and mouse) when active
            if fullscreen_map.active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB:
                        fullscreen_map.toggle()
                    elif event.key == pygame.K_m and tutorial_manager.should_show_tutorial('map'):
                        tutorial_popup.show('map', MAP_TUTORIAL)
                        logger.info("[MAP] Closed full-screen map")
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        fullscreen_map.zoom_in()
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                        fullscreen_map.zoom_out()
                    elif event.key == pygame.K_0:
                        fullscreen_map.reset_zoom()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        fullscreen_map.handle_mouse_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        fullscreen_map.handle_mouse_up()
                elif event.type == pygame.MOUSEMOTION:
                    fullscreen_map.handle_mouse_motion(event.pos)
                continue
            
            # Handle hotbar mouse events (drag & drop)
            if not show_inventory and not show_equipment and not smart_inventory_ui.active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    hotbar_ui.handle_mouse_down(event.pos, event.button, hotbar_system)
                elif event.type == pygame.MOUSEBUTTONUP:
                    hotbar_ui.handle_mouse_up(event.pos, event.button, hotbar_system)
                elif event.type == pygame.MOUSEMOTION:
                    hotbar_ui.handle_mouse_motion(event.pos)
            
            # Handle combat mouse button inputs (when not in menus or over UI)
            if not show_inventory and not show_equipment and not show_pause_menu and not show_settings_menu:
                if not smart_inventory_ui.active and not show_cosmetic_menu:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if mouse is over hotbar or other UI elements
                        mouse_pos = pygame.mouse.get_pos()
                        mouse_over_ui = hotbar_ui.is_mouse_over_hotbar(mouse_pos) if hasattr(hotbar_ui, 'is_mouse_over_hotbar') else False
                        
                        if not mouse_over_ui:
                            # Handle combat mouse buttons
                            if event.button == MOUSE_LEFT:
                                # Left click for physical attack
                                combat_mouse_buttons[MOUSE_LEFT] = True
                            elif event.button == MOUSE_RIGHT:
                                # Right click for magic attack
                                combat_mouse_buttons[MOUSE_RIGHT] = True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        # Clear mouse button flags
                        if event.button in combat_mouse_buttons:
                            combat_mouse_buttons[event.button] = False
            
            # Handle keyboard attack keys (KEYDOWN for event-based attack detection)
            if not show_inventory and not show_equipment and not show_pause_menu and not show_settings_menu:
                if not smart_inventory_ui.active and not show_cosmetic_menu and not dialogue_ui.active:
                    if event.type == pygame.KEYDOWN:
                        # Check if this key is bound to attack action
                        attack_keys = key_bindings.get_keys_for_action("attack")
                        for attack_key in attack_keys:
                            if attack_key is not None and attack_key < 512 and event.key == attack_key:
                                combat_attack_keys[attack_key] = True
                                break
                    elif event.type == pygame.KEYUP:
                        # Clear attack key flags
                        if event.key in combat_attack_keys:
                            combat_attack_keys[event.key] = False
            
            # Handle cosmetic menu mouse events
            if show_cosmetic_menu:
                if event.type == pygame.MOUSEMOTION:
                    cosmetic_menu.handle_mouse_motion(event.pos, cosmetic_manager)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        cosmetic_menu.handle_mouse_click(event.pos, cosmetic_manager)
                    elif event.button == 4:  # Mouse wheel up
                        cosmetic_menu.handle_scroll(1, cosmetic_manager)
                    elif event.button == 5:  # Mouse wheel down
                        cosmetic_menu.handle_scroll(-1, cosmetic_manager)
            
            # Handle bestiary mouse clicks
            if show_bestiary and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                list_x = 70
                list_y = 130
                list_width = 250
                list_height = config.SCREEN_HEIGHT - 180
                
                if list_x <= mouse_pos[0] <= list_x + list_width and list_y <= mouse_pos[1] <= list_y + list_height:
                    sorted_enemies = sorted(bestiary.enemy_types.keys())
                    visible_count = list_height // 30
                    clicked_idx = (mouse_pos[1] - list_y) // 30
                    actual_idx = bestiary_scroll_offset + clicked_idx
                    
                    if 0 <= actual_idx < len(sorted_enemies):
                        bestiary_selected_enemy = sorted_enemies[actual_idx]
            
            if event.type == pygame.KEYDOWN:
                # Handle stick confirmation dialog first
                if stick_confirm_dialog['active']:
                    if event.key == pygame.K_y:
                        # User confirmed - proceed with stick action
                        item = stick_confirm_dialog['pending_item']
                        action = stick_confirm_dialog['action']
                        
                        if action == 'equip':
                            # First stick - equip it normally
                            slot = 'weapon' if 'weapon' in player.equipment else 'main_hand'
                            prev = player.equip(item, slot)
                            if prev:
                                player.add_item(prev)
                            # Track tutorial progress
                            if player.tutorial_active and item.name == 'stick':
                                player.tutorial_sticks_equipped = True
                            player.remove_item(item)
                        elif action == 'stack':
                            # Add to existing stick
                            equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
                            if equipped_weapon and hasattr(equipped_weapon, 'stats'):
                                # Increment stack count
                                current_count = equipped_weapon.stats.get('stack_count', 1)
                                equipped_weapon.stats['stack_count'] = current_count + 1
                                # Update damage: base 2 + (count-1) * 0.5
                                equipped_weapon.stats['damage'] = 2 + (equipped_weapon.stats['stack_count'] - 1) * 0.5
                                # Remove the stick from inventory
                                player.remove_item(item)
                        
                        # Close dialog
                        stick_confirm_dialog['active'] = False
                        stick_confirm_dialog['pending_item'] = None
                        stick_confirm_dialog['action'] = None
                        
                    elif event.key == pygame.K_n:
                        # User cancelled - close dialog
                        stick_confirm_dialog['active'] = False
                        stick_confirm_dialog['pending_item'] = None
                        stick_confirm_dialog['action'] = None
                
                elif show_crafting_menu:
                    # Handle crafting menu input
                    action = crafting_ui.handle_input(event, player)
                    if action == "close":
                        show_crafting_menu = False
                elif show_repair_menu:
                    # Handle repair menu input
                    action = repair_menu_ui.handle_input(event)
                    if action == "close":
                        show_repair_menu = False
                elif show_stats_menu:
                    # Handle stats menu input
                    close_menu, message = handle_stats_menu_input(event, player)
                    if close_menu:
                        show_stats_menu = False
                    if message:
                        inventory_action_msg = message
                elif show_character_sheet:
                    # Handle character sheet input (ESC or E to close)
                    if event.key in [pygame.K_e, pygame.K_ESCAPE]:
                        show_character_sheet = False
                        logger.info("[CHARACTER] Closed character sheet")
                elif show_crime_history:
                    # Handle crime history input (ESC or H to close)
                    if event.key in [pygame.K_h, pygame.K_ESCAPE]:
                        show_crime_history = False
                        inventory_inspect_timer = 60
                elif show_pause_menu:
                    if show_keybindings_menu:
                        # Key bindings menu
                        action = keybindings_ui.handle_event(event, screen)
                        if action == "close":
                            show_keybindings_menu = False
                            key_bindings.save_bindings()  # Save when closing
                    elif show_achievements:
                        # Achievements menu navigation
                        achievement_ui.handle_input(event)
                        if event.key == pygame.K_ESCAPE:
                            achievement_ui.active = False
                            show_achievements = False
                    elif show_bestiary:
                        # Bestiary menu navigation
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                            show_bestiary = False
                        elif event.key == pygame.K_UP:
                            sorted_enemies = sorted(bestiary.enemy_types.keys())
                            if bestiary_selected_enemy in sorted_enemies:
                                idx = sorted_enemies.index(bestiary_selected_enemy)
                                if idx > 0:
                                    bestiary_selected_enemy = sorted_enemies[idx - 1]
                                    # Update scroll if needed
                                    if idx - 1 < bestiary_scroll_offset:
                                        bestiary_scroll_offset = max(0, idx - 1)
                        elif event.key == pygame.K_DOWN:
                            sorted_enemies = sorted(bestiary.enemy_types.keys())
                            if bestiary_selected_enemy in sorted_enemies:
                                idx = sorted_enemies.index(bestiary_selected_enemy)
                                if idx < len(sorted_enemies) - 1:
                                    bestiary_selected_enemy = sorted_enemies[idx + 1]
                                    # Update scroll if needed
                                    visible_count = (config.SCREEN_HEIGHT - 180) // 30
                                    if idx + 1 >= bestiary_scroll_offset + visible_count:
                                        bestiary_scroll_offset = min(len(sorted_enemies) - visible_count, idx + 1 - visible_count + 1)
                    elif show_ai_settings:
                        # AI settings menu navigation
                        consumed = ai_settings_ui.handle_input(event)
                        if not consumed and event.key == pygame.K_ESCAPE:
                            show_ai_settings = False
                    elif show_accessibility_menu:
                        # Accessibility menu navigation
                        consumed = accessibility_ui.handle_input(event)
                        if not consumed and event.key == pygame.K_ESCAPE:
                            show_accessibility_menu = False
                    elif show_font_settings:
                        # Font settings menu navigation
                        action = font_settings_ui.handle_event(event)
                        if action == "close" or not font_settings_ui.active:
                            show_font_settings = False
                    elif show_performance_menu:
                        # Performance menu navigation
                        action = perf_ui.handle_event(event)
                        if action == "close" or event.key == pygame.K_ESCAPE:
                            show_performance_menu = False
                    elif show_settings_menu:
                        # Settings menu navigation
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            settings_idx = (settings_idx - 1) % len(settings_options)
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            settings_idx = (settings_idx + 1) % len(settings_options)
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            opt = settings_options[settings_idx]
                            if opt[0] in ["Audio Volume", "Music Volume", "Font Size"]:
                                settings_state[opt[0]] = max(opt[2], settings_state[opt[0]] - 1)
                            elif opt[0] == "Language":
                                settings_state[opt[0]] = (settings_state[opt[0]] - 1) % len(config.LANGUAGES)
                            elif opt[0] in ["Fullscreen", "Equipment Degradation", "Auto-Scrap Common/Uncommon"]:
                                settings_state[opt[0]] = not settings_state[opt[0]]
                                # Apply repair system settings
                                if opt[0] == "Equipment Degradation":
                                    repair_system.enabled = settings_state[opt[0]]
                                elif opt[0] == "Auto-Scrap Common/Uncommon":
                                    repair_system.auto_scrap_enabled = settings_state[opt[0]]
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            opt = settings_options[settings_idx]
                            if opt[0] in ["Audio Volume", "Music Volume", "Font Size"]:
                                settings_state[opt[0]] = min(opt[3], settings_state[opt[0]] + 1)
                            elif opt[0] == "Language":
                                settings_state[opt[0]] = (settings_state[opt[0]] + 1) % len(config.LANGUAGES)
                            elif opt[0] in ["Fullscreen", "Equipment Degradation", "Auto-Scrap Common/Uncommon"]:
                                settings_state[opt[0]] = not settings_state[opt[0]]
                                # Apply repair system settings
                                if opt[0] == "Equipment Degradation":
                                    repair_system.enabled = settings_state[opt[0]]
                                elif opt[0] == "Auto-Scrap Common/Uncommon":
                                    repair_system.auto_scrap_enabled = settings_state[opt[0]]
                        elif event.key in [pygame.K_ESCAPE, pygame.K_p]:
                            show_settings_menu = False
                        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                            # Open Key Bindings submenu
                            if settings_options[settings_idx][0] == "Key Bindings":
                                show_keybindings_menu = True
                    else:
                        # Pause menu navigation
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            pause_menu_idx = (pause_menu_idx - 1) % len(pause_menu_options)
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            pause_menu_idx = (pause_menu_idx + 1) % len(pause_menu_options)
                        elif event.key in [pygame.K_ESCAPE, pygame.K_p]:
                            # Don't allow closing pause menu if player is dead
                            if not player_died:
                                show_pause_menu = False
                        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                            sel = pause_menu_options[pause_menu_idx]
                            if sel == "Resume":
                                # Can't resume if dead
                                if not player_died:
                                    show_pause_menu = False
                            elif sel == "Save Game":
                                # Can't save if dead
                                if not player_died:
                                    save_integrator.open_save_dialog()
                            elif sel == "Load Game":
                                save_integrator.open_load_dialog()
                            elif sel == "Help":
                                show_help_menu()
                            elif sel == "Settings":
                                show_settings_menu = True
                                settings_idx = 0
                            elif sel == "Achievements":
                                show_achievements = True
                                achievement_ui.active = True
                            elif sel == "Bestiary":
                                show_bestiary = True
                                if not bestiary_selected_enemy:
                                    sorted_enemies = sorted(bestiary.enemy_types.keys())
                                    if sorted_enemies:
                                        bestiary_selected_enemy = sorted_enemies[0]
                            elif sel == "Performance":
                                show_performance_menu = True
                            elif sel == "Accessibility":
                                show_accessibility_menu = True
                            elif sel == "Font Settings":
                                show_font_settings = True
                                font_settings_ui.active = True
                            elif sel == "AI Settings":
                                show_ai_settings = True
                            elif sel == "Exit to Main Menu":
                                return main()
                            elif sel == "Quit Game":
                                running = False
                elif stick_stack_confirmation['active']:
                    # Handle stick stacking confirmation
                    if event.key == pygame.K_y:
                        # Confirm stacking
                        item = stick_stack_confirmation['item']
                        if item and hasattr(item, 'name') and item.name == 'stick':
                            # Get currently equipped stick
                            equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
                            if equipped_weapon and hasattr(equipped_weapon, 'name') and equipped_weapon.name == 'stick':
                                # Increase stack count
                                current_stack = equipped_weapon.stats.get('stack_count', 1)
                                equipped_weapon.stats['stack_count'] = current_stack + 1
                                new_damage = 2 + (current_stack) * 0.5
                                equipped_weapon.stats['damage'] = new_damage
                                # Decrease stackable stick count in inventory
                                if 'stick' in player.inventory and player.inventory['stick'] > 0:
                                    player.inventory['stick'] -= 1
                                icon = get_item_icon('stick')
                                inventory_action_msg = f"{icon} Stacked stick! Stack: {current_stack + 1}, Damage: {new_damage:.1f}"
                        stick_stack_confirmation['active'] = False
                        stick_stack_confirmation['item'] = None
                    elif event.key in [pygame.K_n, pygame.K_ESCAPE]:
                        # Cancel stacking
                        stick_stack_confirmation['active'] = False
                        stick_stack_confirmation['item'] = None
                        inventory_action_msg = "Stick stacking cancelled."
                elif show_new_equipment_ui:
                    # Handle new equipment UI
                    result = equipment_ui.handle_input(event)
                    if result == 'close':
                        show_new_equipment_ui = False
                elif show_inventory:
                    if event.key == pygame.K_i:
                        show_inventory = False
                    # Inventory sorting with R key
                    elif event.key == pygame.K_r:
                        # Cycle through sort modes
                        sort_modes = ['default', 'rarity', 'level', 'value', 'type']
                        current_idx = sort_modes.index(inventory_sort_mode)
                        inventory_sort_mode = sort_modes[(current_idx + 1) % len(sort_modes)]
                        inventory_action_msg = f"Sort: {inventory_sort_mode.title()}"
                        inventory_inspect_timer = 60
                    # Inventory menu navigation
                    cat = inventory_categories[inventory_menu_state['submenu']]
                    items_by_cat = {c: [] for c in inventory_categories}
                    # Stackables - categorize by name patterns
                    for k, v in player.inventory.items():
                        if k == 'items':
                            continue
                        # Only include items with quantity > 0
                        if v <= 0:
                            continue
                        # Categorize stackable items
                        item_name = k.lower()
                        if any(food_word in item_name for food_word in ['berry', 'bread', 'meat', 'fish', 'apple', 'cheese', 'stew', 'food']):
                            items_by_cat['Food'].append((k, v))
                        elif any(quest_word in item_name for quest_word in ['scroll', 'letter', 'note', 'map', 'key_', 'quest']):
                            items_by_cat['Quest Items'].append((k, v))
                        elif k == 'fiber':
                            # Fiber goes to Other only
                            items_by_cat['Other'].append((k, v))
                        elif k == 'stick':
                            # Sticks are weapons, show in Weapons category
                            items_by_cat['Weapons'].append((k, v))
                        else:
                            items_by_cat['Other'].append((k, v))
                    # Item objects (weapons, equipment, etc.)
                    for item in player.inventory.get('items', []):
                        if hasattr(item, 'type'):
                            if item.type == 'weapon':
                                items_by_cat['Weapons'].append(item)
                            elif item.type in ['armor', 'accessory', 'shield'] or get_equipment_slot(item) is not None:
                                # Any item that can be equipped goes in Equipment
                                items_by_cat['Equipment'].append(item)
                            else:
                                items_by_cat['Other'].append(item)
                        else:
                            items_by_cat['Other'].append(item)
                    
                    # Apply sorting to items
                    for category in items_by_cat:
                        items_by_cat[category] = sort_inventory_items(items_by_cat[category], inventory_sort_mode)
                    
                    items = items_by_cat[cat]
                    idx = inventory_menu_state['item_idx']
                    # Clamp idx to valid range to prevent index errors
                    if items:
                        idx = min(idx, len(items) - 1)
                        inventory_menu_state['item_idx'] = idx
                    else:
                        idx = 0
                        inventory_menu_state['item_idx'] = 0
                    
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        inventory_menu_state['submenu'] = (inventory_menu_state['submenu'] - 1) % len(inventory_categories)
                        inventory_menu_state['item_idx'] = 0
                        inventory_inspect_item = None  # Close stats when changing tabs
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        inventory_menu_state['submenu'] = (inventory_menu_state['submenu'] + 1) % len(inventory_categories)
                        inventory_menu_state['item_idx'] = 0
                        inventory_inspect_item = None  # Close stats when changing tabs
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        inventory_menu_state['item_idx'] = max(0, inventory_menu_state['item_idx'] - 1)
                        # Update stats if already open
                        if inventory_inspect_item and items and inventory_menu_state['item_idx'] < len(items):
                            inventory_inspect_item = items[inventory_menu_state['item_idx']]
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        inventory_menu_state['item_idx'] = min(len(items)-1, inventory_menu_state['item_idx'] + 1) if items else 0
                        # Update stats if already open
                        if inventory_inspect_item and items and inventory_menu_state['item_idx'] < len(items):
                            inventory_inspect_item = items[inventory_menu_state['item_idx']]
                    elif event.key in [pygame.K_i, pygame.K_ESCAPE]:
                        show_inventory = False
                        inventory_inspect_item = None  # Clear stats when closing inventory
                    elif event.key == pygame.K_e and items and idx < len(items):
                        # Equip/unequip selected item (with bounds check)
                        item = items[idx]
                        if not isinstance(item, tuple) and hasattr(item, 'type'):
                            # Determine equipment slot using helper function
                            slot = get_equipment_slot(item)
                            
                            if slot:
                                # For rings, check both ring slots
                                if slot == 'ring':
                                    ring1_equipped = player.equipment.get('ring1')
                                    ring2_equipped = player.equipment.get('ring2')
                                    
                                    # Check if this specific ring is already equipped
                                    if ring1_equipped == item:
                                        player.unequip('ring1')
                                        icon = get_item_icon(item.name)
                                        inventory_action_msg = f"{icon} Unequipped {item.name} from ring slot 1!"
                                    elif ring2_equipped == item:
                                        player.unequip('ring2')
                                        icon = get_item_icon(item.name)
                                        inventory_action_msg = f"{icon} Unequipped {item.name} from ring slot 2!"
                                    else:
                                        # Equip to available ring slot (handled by player.equip)
                                        prev = player.equip(item, slot)
                                        icon = get_item_icon(item.name)
                                        if prev:
                                            inventory_action_msg = f"{icon} Equipped {item.name}! (Unequipped {prev.name})"
                                        else:
                                            inventory_action_msg = f"{icon} Equipped {item.name}!"
                                else:
                                    # Regular equipment slot
                                    currently_equipped = player.equipment.get(slot)
                                    if currently_equipped == item:
                                        # Unequip
                                        player.unequip(slot)
                                        icon = get_item_icon(item.name)
                                        inventory_action_msg = f"{icon} Unequipped {item.name}!"
                                    else:
                                        # Special handling for sticks - check if trying to stack
                                        if hasattr(item, 'name') and item.name == 'stick':
                                            if currently_equipped and hasattr(currently_equipped, 'name') and currently_equipped.name == 'stick':
                                                # Trying to equip a stick when one is already equipped - show confirmation
                                                stick_stack_confirmation['active'] = True
                                                stick_stack_confirmation['item'] = item
                                                inventory_inspect_item = None
                                            else:
                                                # No stick equipped, equip normally
                                                prev = player.equip(item, slot)
                                                icon = get_item_icon(item.name)
                                                if prev:
                                                    inventory_action_msg = f"{icon} Equipped {item.name}! (Unequipped {prev.name})"
                                                else:
                                                    inventory_action_msg = f"{icon} Equipped {item.name}!"
                                                # Track tutorial progress
                                                if player.tutorial_active and item.name == 'stick':
                                                    player.tutorial_sticks_equipped = True
                                        else:
                                            # Equip (handles swapping automatically)
                                            prev = player.equip(item, slot)
                                            icon = get_item_icon(item.name)
                                            if prev:
                                                inventory_action_msg = f"{icon} Equipped {item.name}! (Unequipped {prev.name})"
                                            else:
                                                inventory_action_msg = f"{icon} Equipped {item.name}!"
                                            # Track tutorial progress
                                            if player.tutorial_active and item.name == 'stick':
                                                player.tutorial_sticks_equipped = True
                                inventory_inspect_item = None
                            else:
                                icon = get_item_icon(item.name)
                                inventory_action_msg = f"{icon} Cannot equip {item.name}!"
                    elif event.key == pygame.K_q and items and idx < len(items):
                        # Quick equip hotkey (same as E but faster workflow)
                        item = items[idx]
                        if not isinstance(item, tuple) and hasattr(item, 'type'):
                            # Determine equipment slot using helper function
                            slot = get_equipment_slot(item)
                            
                            if slot:
                                # For rings, check both ring slots
                                if slot == 'ring':
                                    ring1_equipped = player.equipment.get('ring1')
                                    ring2_equipped = player.equipment.get('ring2')
                                    
                                    # Check if this specific ring is already equipped
                                    if ring1_equipped == item or ring2_equipped == item:
                                        # Already equipped, do nothing or could unequip
                                        icon = get_item_icon(item.name)
                                        inventory_action_msg = f"{icon} {item.name} is already equipped!"
                                    else:
                                        # Equip to available ring slot
                                        prev = player.equip(item, slot)
                                        icon = get_item_icon(item.name)
                                        if prev:
                                            inventory_action_msg = f"⚡ Quick Equipped {item.name}! (Replaced {prev.name})"
                                        else:
                                            inventory_action_msg = f"⚡ Quick Equipped {item.name}!"
                                else:
                                    # Regular equipment slot - only equip, don't unequip
                                    currently_equipped = player.equipment.get(slot)
                                    if currently_equipped == item:
                                        icon = get_item_icon(item.name)
                                        inventory_action_msg = f"{icon} {item.name} is already equipped!"
                                    else:
                                        # Special handling for sticks - check if trying to stack
                                        if hasattr(item, 'name') and item.name == 'stick':
                                            if currently_equipped and hasattr(currently_equipped, 'name') and currently_equipped.name == 'stick':
                                                # Trying to equip a stick when one is already equipped - show confirmation
                                                stick_stack_confirmation['active'] = True
                                                stick_stack_confirmation['item'] = item
                                                inventory_inspect_item = None
                                            else:
                                                # No stick equipped, quick equip normally
                                                prev = player.equip(item, slot)
                                                icon = get_item_icon(item.name)
                                                if prev:
                                                    inventory_action_msg = f"⚡ Quick Equipped {item.name}! (Replaced {prev.name})"
                                                else:
                                                    inventory_action_msg = f"⚡ Quick Equipped {item.name}!"
                                        else:
                                            # Quick equip
                                            prev = player.equip(item, slot)
                                            icon = get_item_icon(item.name)
                                            if prev:
                                                inventory_action_msg = f"⚡ Quick Equipped {item.name}! (Replaced {prev.name})"
                                            else:
                                                inventory_action_msg = f"⚡ Quick Equipped {item.name}!"
                                inventory_inspect_item = None
                            else:
                                icon = get_item_icon(item.name)
                                inventory_action_msg = f"{icon} Cannot equip {item.name}!"
                    elif event.key == pygame.K_u and items and idx < len(items):
                        item = items[idx]
                        if isinstance(item, tuple):
                            name, count = item
                            # Check if this is a recipe scroll
                            if name.startswith('recipe_'):
                                from crafting import use_recipe_scroll
                                if use_recipe_scroll(player, name):
                                    # Successfully learned recipe - remove scroll
                                    player.inventory[name] = max(0, player.inventory[name] - 1)
                                    # Get recipe name for display
                                    from crafting import RECIPE_SCROLLS, get_recipe_by_id
                                    recipe_id = RECIPE_SCROLLS.get(name)
                                    recipe = get_recipe_by_id(recipe_id) if recipe_id else None
                                    recipe_display = recipe.name if recipe else recipe_id
                                    inventory_action_msg = f"📚 Learned recipe: {recipe_display}!"
                                    inventory_inspect_timer = 120
                                else:
                                    inventory_action_msg = "You already know this recipe!"
                                    inventory_inspect_timer = 60
                            else:
                                # Regular consumable item
                                inventory_action_msg = player.use_item(name)
                        else:
                            inventory_action_msg = player.use_item(item)
                        inventory_inspect_item = None
                        inventory_inspect_timer = 60
                    elif event.key == pygame.K_z and items and idx < len(items):
                        # Salvage equipment into materials
                        item = items[idx]
                        if not isinstance(item, tuple) and hasattr(item, 'type'):
                            # Can only salvage equipment items
                            if item.type in ['weapon', 'armor', 'accessory'] or get_equipment_slot(item) is not None:
                                success, message = salvage_equipment(item, player)
                                inventory_action_msg = message
                                inventory_inspect_item = None
                                inventory_inspect_timer = 90
                                # Reset item index if needed
                                if not items:
                                    inventory_menu_state['item_idx'] = 0
                                elif inventory_menu_state['item_idx'] >= len(items):
                                    inventory_menu_state['item_idx'] = len(items) - 1
                            else:
                                inventory_action_msg = "Cannot salvage this item!"
                                inventory_inspect_timer = 60
                        else:
                            inventory_action_msg = "Cannot salvage this item!"
                            inventory_inspect_timer = 60
                    elif event.key == pygame.K_d and items and idx < len(items):
                        item = items[idx]
                        if isinstance(item, tuple):
                            name, count = item
                            if player.inventory[name] > 0:
                                player.inventory[name] -= 1
                                icon = get_item_icon(name)
                                inventory_action_msg = f"{icon} Dropped 1 {name}."
                        else:
                            player.remove_item(item)
                            item_name = getattr(item, 'name', 'item')
                            icon = get_item_icon(item_name)
                            inventory_action_msg = f"{icon} Dropped {item_name}!"
                        inventory_inspect_item = None
                        inventory_inspect_timer = 60
                    elif event.key == pygame.K_SPACE and items and idx < len(items):
                        # Toggle stats display - close if already showing this item, open otherwise
                        if inventory_inspect_item == items[idx]:
                            inventory_inspect_item = None
                        else:
                            inventory_inspect_item = items[idx]
                        inventory_inspect_timer = 120
                    elif event.key == pygame.K_RETURN and items and idx < len(items):
                        # ENTER key: Equip/use item (weapons/equipment get equipped, consumables get used)
                        item = items[idx]
                        if not isinstance(item, tuple) and hasattr(item, 'type'):
                            # Equipment item - try to equip it
                            slot = get_equipment_slot(item)
                            
                            if slot:
                                # For rings, check both ring slots
                                if slot == 'ring':
                                    ring1_equipped = player.equipment.get('ring1')
                                    ring2_equipped = player.equipment.get('ring2')
                                    
                                    # Check if this specific ring is already equipped
                                    if ring1_equipped == item:
                                        player.unequip('ring1')
                                        icon = get_item_icon(item.name)
                                        inventory_action_msg = f"{icon} Unequipped {item.name} from ring slot 1!"
                                    elif ring2_equipped == item:
                                        player.unequip('ring2')
                                        icon = get_item_icon(item.name)
                                        inventory_action_msg = f"{icon} Unequipped {item.name} from ring slot 2!"
                                    else:
                                        # Equip to available ring slot
                                        prev = player.equip(item, slot)
                                        icon = get_item_icon(item.name)
                                        if prev:
                                            inventory_action_msg = f"{icon} Equipped {item.name}! (Unequipped {prev.name})"
                                        else:
                                            inventory_action_msg = f"{icon} Equipped {item.name}!"
                                else:
                                    # Regular equipment slot
                                    currently_equipped = player.equipment.get(slot)
                                    if currently_equipped == item:
                                        # Unequip
                                        player.unequip(slot)
                                        icon = get_item_icon(item.name)
                                        inventory_action_msg = f"{icon} Unequipped {item.name}!"
                                    else:
                                        # Special handling for sticks
                                        if hasattr(item, 'name') and item.name == 'stick':
                                            if currently_equipped and hasattr(currently_equipped, 'name') and currently_equipped.name == 'stick':
                                                # Trying to equip a stick when one is already equipped - show confirmation
                                                stick_stack_confirmation['active'] = True
                                                stick_stack_confirmation['item'] = item
                                                inventory_inspect_item = None
                                            else:
                                                # No stick equipped, equip normally
                                                prev = player.equip(item, slot)
                                                icon = get_item_icon(item.name)
                                                if prev:
                                                    inventory_action_msg = f"{icon} Equipped {item.name}! (Unequipped {prev.name})"
                                                else:
                                                    inventory_action_msg = f"{icon} Equipped {item.name}!"
                                                # Track tutorial progress
                                                if player.tutorial_active and item.name == 'stick':
                                                    player.tutorial_sticks_equipped = True
                                        else:
                                            # Equip (handles swapping automatically)
                                            prev = player.equip(item, slot)
                                            icon = get_item_icon(item.name)
                                            if prev:
                                                inventory_action_msg = f"{icon} Equipped {item.name}! (Unequipped {prev.name})"
                                            else:
                                                inventory_action_msg = f"{icon} Equipped {item.name}!"
                                inventory_inspect_item = None
                            else:
                                icon = get_item_icon(item.name)
                                inventory_action_msg = f"{icon} Cannot equip {item.name}!"
                        elif isinstance(item, tuple):
                            # Stackable item - try to use it
                            name, count = item
                            # Check if this is a recipe scroll
                            if name.startswith('recipe_'):
                                from crafting import use_recipe_scroll
                                if use_recipe_scroll(player, name):
                                    # Successfully learned recipe - remove scroll
                                    player.inventory[name] = max(0, player.inventory[name] - 1)
                                    # Get recipe name for display
                                    from crafting import RECIPE_SCROLLS, get_recipe_by_id
                                    recipe_id = RECIPE_SCROLLS.get(name)
                                    recipe = get_recipe_by_id(recipe_id) if recipe_id else None
                                    recipe_display = recipe.name if recipe else recipe_id
                                    inventory_action_msg = f"📚 Learned recipe: {recipe_display}!"
                                    inventory_inspect_timer = 120
                                else:
                                    inventory_action_msg = "You already know this recipe!"
                                    inventory_inspect_timer = 60
                            elif name == 'stick':
                                # Special handling for sticks - equip as weapon
                                if count > 0:
                                    from item import Item
                                    # Create a stick item to equip
                                    stick_item = Item('stick', 'weapon', {'damage': 2, 'stack_count': 1})
                                    # Check if already equipped
                                    equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
                                    if equipped_weapon and hasattr(equipped_weapon, 'name') and equipped_weapon.name == 'stick':
                                        # Show confirmation for stacking
                                        stick_stack_confirmation['active'] = True
                                        stick_stack_confirmation['item'] = stick_item
                                        inventory_inspect_item = None
                                    else:
                                        # Equip the stick
                                        prev = player.equip(stick_item, 'weapon')
                                        # Decrease stick count
                                        player.inventory['stick'] -= 1
                                        if player.inventory['stick'] <= 0:
                                            player.inventory['stick'] = 0
                                        icon = get_item_icon('stick')
                                        if prev:
                                            inventory_action_msg = f"{icon} Equipped stick! (Unequipped {prev.name})"
                                        else:
                                            inventory_action_msg = f"{icon} Equipped stick!"
                                        # Track tutorial progress
                                        if player.tutorial_active:
                                            player.tutorial_sticks_equipped = True
                                else:
                                    inventory_action_msg = "You don't have any sticks to equip!"
                            else:
                                # Regular consumable item
                                inventory_action_msg = player.use_item(name)
                            inventory_inspect_item = None
                            inventory_inspect_timer = 60
                        else:
                            # Other item type - try to use it
                            inventory_action_msg = player.use_item(item)
                            inventory_inspect_item = None
                            inventory_inspect_timer = 60
                elif showing_campaign_menu:
                    # Campaign promise menu navigation
                    if event.key in [pygame.K_p, pygame.K_ESCAPE]:
                        # Close campaign menu
                        showing_campaign_menu = False
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        # Navigate up
                        campaign_menu_state['selected_idx'] = max(0, campaign_menu_state['selected_idx'] - 1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        # Navigate down
                        num_promises = len(campaign_menu_state['all_promises'])
                        campaign_menu_state['selected_idx'] = min(num_promises - 1, campaign_menu_state['selected_idx'] + 1)
                    elif event.key == pygame.K_RETURN:
                        # Select/deselect promise
                        selected_promises = campaign_menu_state['selected_promises']
                        current_idx = campaign_menu_state['selected_idx']
                        selected_promise = campaign_menu_state['all_promises'][current_idx]
                        
                        if selected_promise in selected_promises:
                            # Deselect promise
                            selected_promises.remove(selected_promise)
                            logger.info(f"[CAMPAIGN] Deselected promise: {selected_promise}")
                        elif len(selected_promises) < 3:
                            # Select promise (max 3)
                            selected_promises.append(selected_promise)
                            logger.info(f"[CAMPAIGN] Selected promise: {selected_promise}")
                            
                            # If 3 promises selected, activate them in the system
                            if len(selected_promises) == 3:
                                # Create promise objects with the selected descriptions
                                selected_promise_objs = [
                                    CampaignPromise(campaign_menu_state['all_promises'].index(desc), desc)
                                    for desc in selected_promises
                                ]
                                campaign_promise_system.active_promises = selected_promise_objs
                                logger.info(f"[CAMPAIGN] Activated 3 campaign promises: {selected_promises}")
                                
                                town_message = (
                                    "✅ CAMPAIGN PROMISES SET!\n"
                                    f"1. {selected_promises[0]}\n"
                                    f"2. {selected_promises[1]}\n"
                                    f"3. {selected_promises[2]}\n\n"
                                    "These are your official campaign promises!"
                                )
                                town_message_timer = 480  # 8 seconds
                                showing_campaign_menu = False
                        else:
                            # Already have 3 promises selected
                            logger.info("[CAMPAIGN] Cannot select more than 3 promises")
                elif dialogue_ui.active:
                    # Handle dialogue UI input
                    result = dialogue_ui.handle_input(event, dialogue_manager, player, game_time)
                    if result == "walked_away":
                        pass  # Already handled by dialogue_ui
                    elif result == "auto_closed":
                        # Dialogue auto-closed after quest acceptance/completion
                        # Check which quest was affected
                        if 'tutorial_basics' in quest_manager.active_quests:
                            town_message = "Quest accepted: First Steps\nFind 3 sticks and defeat 2 enemies!"
                            town_message_timer = 240
                            logger.info("[TUTORIAL] Quest accepted - dialogue auto-closed")
                        elif hasattr(player, 'tutorial_completed') and player.tutorial_completed:
                            town_message = "Quest completed: First Steps\nRewards received!"
                            town_message_timer = 240
                            logger.info("[TUTORIAL] Quest completed - dialogue auto-closed")
                    elif result == "open_shop":
                        # CRITICAL FIX: Open merchant UI
                        if dialogue_ui.current_npc_id:
                            shop = shop_manager.get_shop(dialogue_ui.current_npc_id)
                            if shop:
                                shop_ui.open(shop, dialogue_ui.current_npc_id, player)
                                dialogue_ui.close()
                                logger.info(f"Opened shop for {dialogue_ui.current_npc_id}")
                            else:
                                logger.warning(f"No shop found for {dialogue_ui.current_npc_id}")
                    elif isinstance(result, dict):
                        # Handle different dict-based results
                        result_type = result.get('type')
                        
                        if result_type == 'ended':
                            # Dialogue ended - check which node it ended at for tutorial NPC
                            if hasattr(player, 'tutorial_npc') and player.tutorial_npc:
                                node_id = result.get('node_id')
                                
                                if node_id == "response_rude":
                                    # Player was rude to the tutorial NPC - make it disappear with smoke effect
                                    smoke_effect.create_poof(player.tutorial_npc.x, player.tutorial_npc.y, particle_count=30)
                                    player.tutorial_npc_offended = True
                                    player.tutorial_npc = None
                                    town_message = "The Wandering Guide vanishes in a puff of smoke..."
                                    town_message_timer = 180
                                    logger.info("[TUTORIAL] Player was rude - NPC disappeared with smoke effect")
                                
                                elif node_id in ["response_polite_decline", "quest_declined_polite"]:
                                    # Player politely declined - mark NPC as declined
                                    player.tutorial_npc.declined_by_player = True
                                    logger.info("[TUTORIAL] Player politely declined - NPC marked")
                                
                                # Quest acceptance now handled by ACTION nodes in dialogue tree
                                # No need to handle response_accept here anymore
                        
                        elif result_type == 'gatherer_combat':
                            # Start combat with gatherer NPC
                            town_message = result.get('message', 'Combat started!')
                            town_message_timer = 120
                            logger.info(f"[GATHERER] Combat started with {result['npc'].name}")
                        elif result_type == 'gatherer_warning':
                            # Display warning message
                            town_message = result.get('message', 'Warning issued!')
                            town_message_timer = 180
                            logger.info(f"[GATHERER] Warning issued by {result['npc'].name}")
                        elif result_type == 'gatherer_success':
                            # Display success message
                            town_message = result.get('message', 'Success!')
                            town_message_timer = 180
                            logger.info(f"[GATHERER] {result.get('message', 'Success!')}")
                    
                    # Check if tutorial NPC dialogue ended with rude response
                    if not dialogue_ui.active and hasattr(player, 'tutorial_npc') and player.tutorial_npc:
                        if dialogue_manager.last_visited_node_id == "response_rude":
                            # Player was rude to the tutorial NPC - make it disappear with smoke effect
                            if hasattr(player, 'tutorial_npc') and player.tutorial_npc:
                                # Create smoke poof at NPC location
                                smoke_effect.create_poof(player.tutorial_npc.x, player.tutorial_npc.y, particle_count=30)
                                # Mark NPC as offended and remove it
                                player.tutorial_npc_offended = True
                                player.tutorial_npc = None
                                town_message = "The Wandering Guide vanishes in a puff of smoke..."
                                town_message_timer = 180
                                logger.info("[TUTORIAL] Player was rude - NPC disappeared with smoke")
                                # Clear the last visited node so this doesn't trigger again
                                dialogue_manager.last_visited_node_id = None
                elif shop_ui.active:
                    # CRITICAL FIX: Handle shop UI input
                    result = shop_ui.handle_input(event)
                    if result == "closed":
                        logger.info("Shop closed")
                elif shop_ownership_ui.active:
                    # Handle shop ownership UI input
                    result = shop_ownership_ui.handle_input(event)
                    if result == "close":
                        shop_ownership_ui.close()
                        logger.info("[SHOP OWNERSHIP] Closed shop ownership UI")
                elif economic_events_ui.active:
                    # Handle economic events UI input
                    result = economic_events_ui.handle_input(event)
                    if result == "close":
                        economic_events_ui.close()
                        logger.info("[ECONOMIC EVENTS] Closed economic events UI")
                elif trading_menu_ui.active:
                    # Handle trading menu UI input
                    result = trading_menu_ui.handle_input(event)
                    if result == "close":
                        trading_menu_ui.close()
                        logger.info("[TRADING MENU] Closed trading menu")
                elif bartering_ui.active:
                    # Handle bartering UI input
                    result = bartering_ui.handle_input(event)
                    if result == "close":
                        bartering_ui.close()
                        logger.info("[BARTERING] Closed bartering UI")
                elif advanced_trading_ui.active:
                    # Handle advanced trading UI input
                    result = advanced_trading_ui.handle_input(event)
                    if result == "close":
                        advanced_trading_ui.close()
                        logger.info("[ADVANCED TRADING] Closed advanced trading UI")
                elif inn_ui.active:
                    # Handle inn UI input
                    inn_ui.handle_input(event, player, game_time)
                elif blacksmith_ui.active:
                    # Handle blacksmith UI input
                    blacksmith_ui.handle_input(event, player)
                elif tavern_ui.active:
                    # Handle tavern UI input
                    tavern_ui.handle_input(event, player, game_time)
                elif tavern_food_ui.active:
                    # Handle tavern food trading UI
                    result = tavern_food_ui.handle_input(event, player)
                    if result == "close":
                        tavern_food_ui.close()
                elif market_stall_ui.active:
                    # Handle market stall UI
                    result = market_stall_ui.handle_input(event, player)
                    if result == "close":
                        market_stall_ui.close()
                elif safety_deposit_ui.active:
                    # Handle safety deposit UI
                    result = safety_deposit_ui.handle_input(event, player)
                    if result == "close":
                        safety_deposit_ui.close()
                elif temple_ui.active:
                    # Handle temple UI input
                    new_blessing = temple_ui.handle_input(event, player)
                    if new_blessing:
                        active_blessings.append(new_blessing)
                elif mage_ui.active:
                    # Handle mage UI input
                    result = mage_ui.handle_input(event, player)
                    if result == "close":
                        mage_ui.close()
                elif bank_ui.active:
                    # Handle bank UI input
                    bank_ui.handle_input(event, player)
                elif library_ui.active:
                    # Handle library UI input
                    result = library_ui.handle_input(event, player)
                    if result == "closed":
                        logger.info("[LIBRARY] Closed library UI")
                elif town_hall_ui.active:
                    # Handle town hall UI input
                    result = town_hall_ui.handle_input(event, player)
                    if result:
                        if result.startswith("voted:"):
                            candidate_name = result.split(":")[1]
                            town_message = f"✅ VOTE CAST!\nYou voted for {candidate_name}\nThank you for your civic participation!"
                            town_message_timer = 360
                            logger.info(f"[VOTING] Player successfully voted for {candidate_name}")
                        elif result == "already_voted":
                            town_message = "You have already voted in this election!"
                            town_message_timer = 180
                        elif result == "not_eligible":
                            town_message = "You are not eligible to vote.\n(Voting rights may have been revoked)"
                            town_message_timer = 180
                        elif result.startswith("tax_paid:"):
                            amount = result.split(":")[1]
                            town_message = f"✅ BACK TAXES PAID!\nPaid {amount}g in outstanding property taxes\nYour tax debt has been cleared!"
                            town_message_timer = 360
                            logger.info(f"[TAX PAYMENT] Player paid {amount}g in back taxes")
                        elif result.startswith("tax_failed:"):
                            message = result.split(":", 1)[1]
                            town_message = f"❌ TAX PAYMENT FAILED\n{message}"
                            town_message_timer = 240
                        elif result == "no_taxes":
                            town_message = "No unpaid taxes!\nYou have no outstanding tax debt."
                            town_message_timer = 180
                elif cooking_ui.active:
                    # Handle cooking UI input
                    cooking_ui.handle_input(event, player)
                elif criminal_ui_instance.active:
                    # Handle criminal underworld UI input
                    result = criminal_ui_instance.handle_input(event, player, game_time)
                    if result == "close":
                        criminal_ui_instance.close()
                        logger.info("[CRIMINAL UI] Closed underworld menu")
                elif leaderboard_ui.active:
                    # Handle leaderboard UI input
                    leaderboard_ui.handle_input(event, player.name)
                elif stock_market_ui.active:
                    # Handle stock market UI input
                    stock_market_ui.handle_input(event)
                elif companion_hiring_ui.active:
                    # Handle companion hiring UI input
                    companion_hiring_ui.handle_input(event)
                elif player_insurance_ui.active:
                    # Handle insurance UI input
                    player_insurance_ui.handle_input(event)
                elif newspaper_ui.active:
                    # Handle newspaper UI input
                    if newspaper_ui.handle_input(event):
                        pass  # Event consumed
                elif commodity_exchange_ui.active:
                    # Handle commodity exchange UI input
                    if commodity_exchange_ui.handle_input(event):
                        pass  # Event consumed
                elif economics_skill_tree_ui.active:
                    # Handle economics skill tree UI input
                    if economics_skill_tree_ui.handle_input(event):
                        pass  # Event consumed
                elif skills_ui.active:
                    # Handle skills UI input
                    skills_ui.handle_input(event, player)
                elif dialogue_history_ui.active:
                    # Handle dialogue history input
                    dialogue_history_ui.handle_input(event)
                elif mayor_powers_ui.active:
                    # Handle mayor powers menu input
                    result = mayor_powers_ui.handle_input(event)
                    if result and result != "closed":
                        # Handle mayor action results
                        if result == "curfew_enabled":
                            town_message = f"✅ CURFEW ENABLED\nCitizens must be indoors {curfew_system.curfew_start}:00-{curfew_system.curfew_end}:00\nViolators fined {curfew_system.fine_amount}g"
                            town_message_timer = 300
                            logger.info(f"[MAYOR] Player enabled curfew in {mayor_powers_ui.current_town}")
                        elif result == "curfew_disabled":
                            town_message = "✅ CURFEW DISABLED\nCitizens may move freely"
                            town_message_timer = 240
                            logger.info(f"[MAYOR] Player disabled curfew in {mayor_powers_ui.current_town}")
                        elif result == "weapon_restrictions_enabled":
                            town_message = "⚔️ WEAPON RESTRICTIONS ENABLED\nAll weapons confiscated at gates\nStored in Town Hall"
                            town_message_timer = 300
                            logger.info(f"[MAYOR] Player enabled weapon restrictions")
                        elif result == "weapon_restrictions_disabled":
                            town_message = "✅ WEAPON RESTRICTIONS DISABLED\nCitizens may carry weapons"
                            town_message_timer = 240
                            logger.info(f"[MAYOR] Player disabled weapon restrictions")
                        elif result == "entry_fee_enabled":
                            town_message = f"💰 ENTRY FEE ENABLED\n{town_entry_fee_system.entry_fee}g charged to enter {mayor_powers_ui.current_town}"
                            town_message_timer = 300
                            logger.info(f"[MAYOR] Player enabled entry fee")
                        elif result == "entry_fee_disabled":
                            town_message = "✅ ENTRY FEE DISABLED\nFree entry to town"
                            town_message_timer = 240
                            logger.info(f"[MAYOR] Player disabled entry fee")
                        elif result == "embargo_started":
                            town_message = f"🚫 TRADE EMBARGO STARTED\n{int(embargo_system.embargo_fee_percent*100)}% fee on all sales\nLasts {embargo_system.embargo_duration} days"
                            town_message_timer = 360
                            logger.warning(f"[MAYOR] Player started trade embargo")
                        elif result.startswith("embargo_info:"):
                            days_left = result.split(":")[1]
                            town_message = f"ℹ️ EMBARGO ACTIVE\n{days_left} days remaining"
                            town_message_timer = 240
                        elif result.startswith("treasury_info:"):
                            balance = result.split(":")[1]
                            town_message = f"💰 TOWN TREASURY\n{mayor_powers_ui.current_town}: {balance}g\n(From taxes, fines, fees)"
                            town_message_timer = 300
                elif quest_log_ui.active:
                    # Quest log handles its own input
                    result = quest_log_ui.handle_input(event, quest_manager, player)
                    if result:
                        logger.info(f"[QUEST] {result}")
                elif lootbox_animation.is_showing():
                    # Handle loot box animation input (ENTER to continue after reveal)
                    if event.key == pygame.K_RETURN and lootbox_animation.is_waiting_for_input():
                        lootbox_animation.finish()
                        final_cosmetic = lootbox_animation.get_final_cosmetic()
                        # Check if duplicate and show result
                        if lootbox_animation.is_duplicate:
                            max_shop_interaction.show_result(is_duplicate=True)
                        else:
                            max_shop_interaction.show_result(is_duplicate=False)
                        logger.info(f"[LOOTBOX] Player received: {final_cosmetic.name}")
                elif max_shop_interaction.is_active():
                    # Handle Max's shop dialogue with arrow keys (matching standard dialogue system)
                    if event.key == pygame.K_ESCAPE:
                        max_shop_interaction.close_interaction()
                        logger.info("[LOOTBOX] Player closed Max's shop")
                    elif event.key in [pygame.K_UP, pygame.K_w] and max_shop_interaction.waiting_for_choice:
                        # Move selection up
                        max_shop_interaction.move_selection_up()
                    elif event.key in [pygame.K_DOWN, pygame.K_s] and max_shop_interaction.waiting_for_choice:
                        # Move selection down
                        max_shop_interaction.move_selection_down()
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        if max_shop_interaction.waiting_for_choice:
                            # Player made a choice using arrow keys
                            choice_num = max_shop_interaction.get_selected_choice_number()
                            result = max_shop_interaction.make_choice(choice_num, player, lootbox_shop)
                            if result == "purchase":
                                # Complete the purchase and start animation
                                success, cosmetic, is_duplicate = lootbox_shop.purchase_loot_box(
                                    player, cosmetic_manager, preferred_type="player"
                                )
                                if success:
                                    lootbox_animation.start_animation(cosmetic)
                                    lootbox_animation.is_duplicate = is_duplicate
                                    logger.info(f"[LOOTBOX] Purchase successful. Rarity: {cosmetic.rarity}")
                        elif max_shop_interaction.is_waiting_for_input():
                            # Advance dialogue
                            max_shop_interaction.advance_dialogue(player, lootbox_shop)
                            logger.info(f"[LOOTBOX] Advanced dialogue to index {max_shop_interaction.dialogue_index}, state: {max_shop_interaction.state}")
                elif show_cosmetic_menu:
                    # Handle cosmetic menu input
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_v:
                        show_cosmetic_menu = False
                        logger.info("[COSMETIC] Closed cosmetic menu")
                else:
                    if key_bindings.is_action("pause", event.key):
                        show_pause_menu = True
                    elif key_bindings.is_action("accessibility_settings", event.key):
                        # Quick access to accessibility settings
                        show_pause_menu = True
                        show_accessibility_menu = True
                    elif key_bindings.is_action("performance_settings", event.key):
                        # Quick access to performance settings
                        show_pause_menu = True
                        show_performance_menu = True
                    elif key_bindings.is_action("smart_inventory", event.key):
                        # Toggle smart inventory UI
                        was_closed = not smart_inventory_ui.active
                        smart_inventory_ui.toggle()
                        # Show tutorial if first time opening
                        if was_closed and smart_inventory_ui.active and tutorial_manager.should_show_tutorial('smart_inventory'):
                            from tutorial_content import SMART_INVENTORY_TUTORIAL
                            tutorial_popup.show('smart_inventory', SMART_INVENTORY_TUTORIAL)
                    elif key_bindings.is_action("quick_save", event.key):
                        # Quick save
                        # Save tutorial manager state to player before saving
                        player.tutorials_shown = tutorial_manager.tutorials_shown
                        save_integrator.quick_save()
                    elif key_bindings.is_action("quick_load", event.key):
                        # Quick load
                        save_integrator.quick_load()
                        # Restore tutorial manager state from player after loading
                        if hasattr(player, 'tutorials_shown'):
                            tutorial_manager.tutorials_shown = player.tutorials_shown
                    elif event.key == pygame.K_SLASH:
                        # Toggle AI player (Emergency stop key)
                        ai_player.toggle()
                        if ai_player.enabled:
                            town_message = "🤖 AI PLAYER ENABLED - Press / to stop"
                        else:
                            town_message = "🛑 AI PLAYER DISABLED - Press / to resume"
                        town_message_timer = 180  # 3 seconds
                        logger.info(f"[AI TOGGLE] AI player {'enabled' if ai_player.enabled else 'disabled'} via / key")
                    elif key_bindings.is_action("crafting", event.key):
                        # Toggle crafting menu
                        show_crafting_menu = not show_crafting_menu
                        if show_crafting_menu and tutorial_manager.should_show_tutorial('crafting'):
                            tutorial_popup.show('crafting', CRAFTING_TUTORIAL)
                    elif event.key == pygame.K_r:
                        # Toggle repair menu
                        if show_repair_menu:
                            repair_menu_ui.close()
                            show_repair_menu = False
                        else:
                            repair_menu_ui.open()
                            show_repair_menu = True
                    elif key_bindings.is_action("inventory", event.key):
                        # Toggle inventory (if not already showing)
                        show_inventory = not show_inventory
                        if show_inventory:
                            inventory_menu_state = {'submenu': 0, 'item_idx': 0}
                            inventory_inspect_item = None  # Clear stats when opening inventory
                            # Show tutorial popup if first time
                            if tutorial_manager.should_show_tutorial('inventory'):
                                tutorial_popup.show('inventory', INVENTORY_TUTORIAL)
                    elif key_bindings.is_action("skill_tree", event.key):
                        # Open skill tree menu
                        font = get_font(None, 24)
                        skill_tree_menu(screen, font, player)
                    elif key_bindings.is_action("stats", event.key):
                        # Toggle stats menu
                        show_stats_menu = not show_stats_menu
                        if show_stats_menu and tutorial_manager.should_show_tutorial('stats'):
                            tutorial_popup.show('stats', STATS_TUTORIAL)
                    elif event.key == pygame.K_j:
                        # Toggle crime history viewer
                        show_crime_history = not show_crime_history
                    elif event.key == pygame.K_F7:
                        # Toggle debug mode (shows vision cones, etc.)
                        debug_mode = not debug_mode
                        town_message = f"Debug Mode: {'ON' if debug_mode else 'OFF'}"
                        town_message_timer = 120
                        logger.info(f"[DEBUG] Debug mode {'enabled' if debug_mode else 'disabled'}")
                    elif event.key == pygame.K_F8:
                        # Toggle AI debug overlay
                        ai_debug_overlay.toggle()
                        town_message = f"AI Debug: {'ON' if ai_debug_overlay.enabled else 'OFF'}"
                        town_message_timer = 120
                        logger.info(f"[DEBUG] AI debug overlay {'enabled' if ai_debug_overlay.enabled else 'disabled'}")
                    elif event.key == pygame.K_F9:
                        # Cycle AI debug mode
                        if ai_debug_overlay.enabled:
                            mode = ai_debug_overlay.cycle_detail_mode()
                            town_message = f"AI Debug Mode: {mode.upper()}"
                            town_message_timer = 120
                            logger.info(f"[DEBUG] AI debug mode: {mode}")
                    elif event.key == pygame.K_BACKQUOTE:
                        # Toggle AI player (automated testing) - Backtick/Tilde key (`)
                        is_enabled = ai_player.toggle()
                        town_message = f"AI Player: {'ENABLED' if is_enabled else 'DISABLED'}\n{'Auto-testing game features...' if is_enabled else 'Manual control restored'}"
                        town_message_timer = 180
                        logger.info(f"[AI PLAYER] AI player {'enabled' if is_enabled else 'disabled'}")
                    elif event.key == pygame.K_k:
                        # Check if shift is held - dismiss oldest summon
                        keys_pressed = pygame.key.get_pressed()
                        if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
                            # Dismiss oldest summon
                            active_summons = summoning_system.get_active_summons()
                            if active_summons:
                                summoning_system.dismiss_oldest()
                                logger.info(f"[SUMMON] Dismissed oldest summon ({len(active_summons)-1} remaining)")
                            else:
                                logger.info("[SUMMON] No active summons to dismiss")
                        else:
                            # Toggle skills UI (gathering skills)
                            skills_ui.toggle()
                    elif event.key == pygame.K_l:
                        # Toggle leaderboard
                        leaderboard_ui.toggle()
                        if leaderboard_ui.active:
                            # Update current player's rankings
                            leaderboard_system.update_all_skills(player.name, player.skills_manager)
                            logger.info("[LEADERBOARD] Opened leaderboard")
                    elif event.key == pygame.K_i:
                        # Toggle stock market & investments
                        stock_market_ui.toggle()
                        if stock_market_ui.active:
                            logger.info("[STOCK MARKET] Opened stock market UI")
                    elif event.key == pygame.K_o:
                        # Toggle shop ownership UI
                        if not shop_ownership_ui.active:
                            shop_ownership_ui.open(shop_ownership_manager, player, game_time)
                            logger.info("[SHOP OWNERSHIP] Opened shop ownership UI")
                        else:
                            shop_ownership_ui.close()
                            logger.info("[SHOP OWNERSHIP] Closed shop ownership UI")
                    elif event.key == pygame.K_z:
                        # Toggle new Diablo-style equipment UI (Z for Character sheet)
                        if not show_new_equipment_ui:
                            equipment_ui.open(player)
                            show_new_equipment_ui = True
                            logger.info("[EQUIPMENT] Opened equipment UI")
                        else:
                            equipment_ui.close()
                            show_new_equipment_ui = False
                            logger.info("[EQUIPMENT] Closed equipment UI")
                    elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_SHIFT and not in_building_interior:
                        # Toggle economic events UI (Shift+E only, not inside buildings)
                        current_town_name = current_town.name if current_town else None
                        if not economic_events_ui.active:
                            economic_events_ui.open(price_event_manager, current_town_name, game_time.day_count)
                            logger.info("[ECONOMIC EVENTS] Opened economic events UI")
                        else:
                            economic_events_ui.close()
                            logger.info("[ECONOMIC EVENTS] Closed economic events UI")
                    elif event.key == pygame.K_t and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        # Toggle trading menu (Shift+T)
                        if not trading_menu_ui.active:
                            trading_menu_ui.open(
                                smuggling_system, special_order_manager, merchant_quest_manager,
                                caravan_manager, reputation_system, player, game_time
                            )
                            logger.info("[TRADING MENU] Opened trading menu")
                        else:
                            trading_menu_ui.close()
                            logger.info("[TRADING MENU] Closed trading menu")
                    elif event.key == pygame.K_b:
                        # Open bartering UI (when shop is active)
                        if shop_ui.active and shop_ui.current_shop and shop_ui.current_merchant_id:
                            bartering_ui.open(
                                bartering_system, reputation_manager, player,
                                shop_ui.current_shop, shop_ui.current_merchant_id,
                                shop_ui.current_merchant_id  # Use merchant_id as merchant_name
                            )
                            shop_ui.close()
                            logger.info("[BARTERING] Opened bartering UI")
                        elif not bartering_ui.active:
                            logger.info("[BARTERING] Open a shop first to start bartering (talk to a merchant)")
                    elif event.key == pygame.K_v:
                        # Toggle advanced trading UI (Changed from K_a to avoid movement conflict)
                        if not advanced_trading_ui.active:
                            advanced_trading_ui.open(
                                quality_manager, time_sales_manager, appraisal_system,
                                consignment_manager, player, game_time,
                                shop_ui.current_shop if shop_ui.active else None
                            )
                            logger.info("[ADVANCED TRADING] Opened advanced trading UI")
                        else:
                            advanced_trading_ui.close()
                            logger.info("[ADVANCED TRADING] Closed advanced trading UI")
                    elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_SHIFT and in_town and current_town_instance and not in_building_interior:
                        # Toggle market stall UI (Shift+S only in towns with markets, not inside buildings)
                        if not market_stall_ui.active:
                            market_stall_ui.open(current_town_instance.name, market_stall_system, player)
                            logger.info(f"[MARKET STALL] Opened market stall UI in {current_town_instance.name}")
                        else:
                            market_stall_ui.close()
                            logger.info("[MARKET STALL] Closed market stall UI")
                    elif event.key == pygame.K_g:
                        # Toggle pet menu
                        pet_menu_ui.toggle()
                    elif event.key == pygame.K_v:
                        # Toggle cosmetic menu
                        show_cosmetic_menu = not show_cosmetic_menu
                        if show_cosmetic_menu:
                            logger.info("[COSMETIC] Opened cosmetic menu")
                        else:
                            logger.info("[COSMETIC] Closed cosmetic menu")
                    elif event.key == pygame.K_u:
                        # Check if Shift is held for Underworld menu
                        keys_pressed = pygame.key.get_pressed()
                        if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
                            # Toggle criminal underworld UI
                            if not criminal_ui_instance.active:
                                criminal_ui_instance.open()
                                logger.info("[CRIMINAL UI] Opened underworld menu")
                            else:
                                criminal_ui_instance.close()
                                logger.info("[CRIMINAL UI] Closed underworld menu")
                        else:
                            # Cycle through unlocked pets or toggle off
                            if pet_companion.enabled:
                                # Cycle to next pet
                                unlocked = achievement_manager.unlocked_pets
                                if len(unlocked) > 1:
                                    pet_companion.cycle_pet(unlocked)
                                    town_message = f"Pet changed to: {pet_companion.current_pet.title()}!"
                                else:
                                    pet_companion.toggle(player.x, player.y)
                                    town_message = "Pet disabled!"
                            else:
                                # Enable pet
                                pet_companion.toggle(player.x, player.y)
                                town_message = f"Pet enabled: {pet_companion.current_pet.title()}!"
                            town_message_timer = 120
                    # DISABLED: E key now used for interact only
                    # elif event.key == pygame.K_e:
                    #     # Toggle character sheet (equipment view)
                    #     show_character_sheet = not show_character_sheet
                    #     if show_character_sheet:
                    #         logger.info("[CHARACTER] Opened character sheet")
                    #     else:
                    #         logger.info("[CHARACTER] Closed character sheet")
                    elif event.key == pygame.K_b and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Place cooking fire (Ctrl+B - costs 2 sticks)
                        can_place, message = fire_manager.can_place_fire(player)
                        if can_place:
                            success, fire_message = fire_manager.place_fire(player, game_time)
                            town_message = fire_message
                            town_message_timer = 120 if success else 180
                            
                            if success:
                                # Track fire building for achievements
                                player.ach_fires_built += 1
                                achievement_manager.check_all_survival(
                                    0,  # days_survived - tracked elsewhere
                                    player.ach_meals_cooked,
                                    player.ach_fires_built
                                )
                                unlocked = achievement_manager.get_recent_unlock()
                                if unlocked:
                                    achievement_popup.show(unlocked)
                                    logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                        else:
                            town_message = message
                            town_message_timer = 180
                    elif event.key == pygame.K_x:
                        # Pickup/bury body (X for eXamine/eXtract)
                        if body_disposal_system.body_in_inventory:
                            # Try to bury the body
                            can_bury, bury_reason = body_disposal_system.can_bury_body(player, player.x, player.y)
                            if can_bury:
                                success, bury_msg = body_disposal_system.bury_body(player, player.x, player.y)
                                town_message = bury_msg
                                town_message_timer = 180
                                if success:
                                    logger.info(f"[BODY] {bury_msg}")
                            else:
                                town_message = bury_reason
                                town_message_timer = 180
                        else:
                            # Try to pickup nearby corpse
                            nearby_corpse = body_disposal_system.get_nearby_corpse(player.x, player.y, radius=50)
                            if nearby_corpse:
                                can_pickup, pickup_reason = body_disposal_system.can_pickup_body(player, nearby_corpse)
                                if can_pickup:
                                    success, pickup_msg = body_disposal_system.pickup_body(player, nearby_corpse)
                                    town_message = pickup_msg
                                    town_message_timer = 180
                                    if success:
                                        player.carrying_body = nearby_corpse
                                        logger.info(f"[BODY] {pickup_msg}")
                                else:
                                    town_message = pickup_reason
                                    town_message_timer = 180
                            else:
                                town_message = "No bodies nearby to pick up (press O near a body)"
                                town_message_timer = 120
                    elif event.key == pygame.K_LSHIFT:
                        # Toggle sprint mode with left shift (independent)
                        if not player.last_lshift_state:  # Only toggle on rising edge (key just pressed)
                            player.is_sprinting = not player.is_sprinting
                            if player.is_sprinting:
                                town_message = "Sprint mode ON (uses stamina)"
                            else:
                                town_message = "Sprint mode OFF"
                            town_message_timer = 60
                        player.last_lshift_state = True
                    elif event.key == pygame.K_RSHIFT:
                        # Toggle sprint mode with right shift (independent)
                        if not player.last_rshift_state:  # Only toggle on rising edge (key just pressed)
                            player.is_sprinting = not player.is_sprinting
                            if player.is_sprinting:
                                town_message = "Sprint mode ON (uses stamina)"
                            else:
                                town_message = "Sprint mode OFF"
                            town_message_timer = 60
                        player.last_rshift_state = True
                    elif key_bindings.is_action("dodge", event.key):
                        # Dodge roll - check key bindings
                        keys_pressed = pygame.key.get_pressed()
                        # Get direction from movement keys
                        direction_x = 0
                        direction_y = 0
                        if keys_pressed[pygame.K_w]:
                            direction_y = -1
                        if keys_pressed[pygame.K_s]:
                            direction_y = 1
                        if keys_pressed[pygame.K_a]:
                            direction_x = -1
                        if keys_pressed[pygame.K_d]:
                            direction_x = 1
                        
                        # Attempt dodge roll
                        success, message = player.attempt_dodge_roll(direction_x, direction_y)
                        if success:
                            town_message = "⚡ DODGE ROLL!"
                            town_message_timer = 45
                            logger.info(f"[COMBAT] Player dodged")
                        else:
                            town_message = message
                            town_message_timer = 60
                    elif event.key == pygame.K_LEFTBRACKET:
                        # Toggle auto-loot on/off
                        auto_loot_enabled = not auto_loot_enabled
                        town_message = f"Auto-loot {'ON' if auto_loot_enabled else 'OFF'}"
                        town_message_timer = 90
                    elif event.key == pygame.K_RIGHTBRACKET:
                        # Cycle auto-loot minimum rarity
                        rarity_options = ['common', 'uncommon', 'rare', 'epic', 'legendary']
                        current_idx = rarity_options.index(auto_loot_min_rarity)
                        auto_loot_min_rarity = rarity_options[(current_idx + 1) % len(rarity_options)]
                        town_message = f"Auto-loot: {auto_loot_min_rarity.title()}+"
                        town_message_timer = 90
                    elif event.key == pygame.K_c:
                        # Try to cook at town range (if in town)
                        is_in_town = False
                        for town in town_manager.towns:
                            if town.is_in_town(player.x, player.y):
                                is_in_town = True
                                break
                        
                        if is_in_town:
                            cooking_ui.open(is_town_range=True)
                            logger.info("[COOKING] Opened cooking UI at town range")
                        else:
                            # Check for nearby fire
                            nearby_fire = fire_manager.get_nearby_fire(player.x, player.y, max_distance=60)
                            if nearby_fire:
                                cooking_ui.open(is_town_range=False)
                                logger.info("[COOKING] Opened cooking UI at campfire")
                            else:
                                town_message = "Need to be in town or near fire to cook (Press F to build fire)"
                                town_message_timer = 150
                    elif key_bindings.is_action("spellbook", event.key):
                        # Open spellbook menu
                        font = get_font(None, 24)
                        spellbook_menu(screen, font, player, SPELLS)
                    elif key_bindings.is_action("cast_primary_spell", event.key):
                        # Cast primary spell (Q key)
                        if player.selected_spell:
                            # Get mouse position for targeting (use frame-start camera)
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            target_x = mouse_x + camera_x
                            target_y = mouse_y + camera_y
                            
                            spell_result = player.cast_spell(player.selected_spell, target_x, target_y)
                            if spell_result:
                                # Update spell cooldown in HUD
                                spell_data = SPELLS.get(player.selected_spell)
                                if spell_data:
                                    spell_hud.update_cooldown(player.selected_spell, spell_data.get('cooldown', 1.0))
                                
                                # Get spell data from SPELLS dictionary
                                spell_data = SPELLS[player.selected_spell]
                                spell_type = spell_data.get('type', 'projectile')
                                
                                # Check spell type and handle accordingly
                                if spell_type == 'projectile':
                                    # Projectile spell (fireball, etc.) - add to projectiles list
                                    spell_projectiles.append(spell_result)
                                    logger.info(f"[SPELL] {spell_data.get('name', player.selected_spell)} cast (Primary/Q)")
                                    
                                elif spell_type in ['instant', 'self']:
                                    # Healing or buff spell - execute immediately
                                    from spell_projectile import SpellEffect, InstantSpell
                                    
                                    # Execute the instant spell if it has an execute method
                                    if isinstance(spell_result, InstantSpell) and hasattr(spell_result, 'execute'):
                                        spell_result.execute(player, enemies_list)
                                    
                                    # Create visual effect
                                    effect_color = (100, 255, 100) if spell_type == 'self' else (255, 255, 100)
                                    effect = SpellEffect(player.x, player.y, player.selected_spell, effect_color)
                                    spell_effects.append(effect)
                                    logger.info(f"[SPELL] {spell_data.get('name', player.selected_spell)} cast (Primary/Q)")
                                    
                                elif spell_data.get('type') == 'summon':
                                    # Summon creature
                                    summon_type_str = spell_data.get('summon_type', 'wolf')
                                    duration = spell_data.get('summon_duration', 30)
                                    
                                    # Convert string to SummonType enum
                                    summon_type = SummonType[summon_type_str.upper()]
                                    
                                    # Summon at target position
                                    summon = summoning_system.summon_creature(
                                        summon_type, target_x, target_y, player, duration
                                    )
                                    
                                    if summon:
                                        # Add visual effect
                                        summon_cast_effect_ui.add_effect(target_x, target_y, summon_type_str)
                                        logger.info(f"[SUMMON] Summoned {summon_type_str} at ({target_x}, {target_y})")
                                    else:
                                        logger.warning("[SUMMON] Failed - max summons reached (5)")
                                        
                                elif spell_data.get('type') == 'necromancy':
                                    # Raise dead spell
                                    spell_range = spell_data.get('range', 100)
                                    duration = spell_data.get('summon_duration', 60)
                                    max_raises = spell_data.get('max_raises', 1)
                                    
                                    # Find nearby corpses
                                    nearby_corpses = summoning_system.get_nearby_corpses(player.x, player.y, spell_range)
                                    
                                    if nearby_corpses:
                                        raised_count = 0
                                        for corpse in nearby_corpses[:max_raises]:
                                            undead = summoning_system.raise_dead(corpse, player, duration)
                                            if undead:
                                                summon_cast_effect_ui.add_effect(corpse['x'], corpse['y'], 'necromancy')
                                                raised_count += 1
                                            else:
                                                break  # Max summons reached
                                        
                                        if raised_count > 0:
                                            logger.info(f"[NECROMANCY] Raised {raised_count} undead minion(s)")
                                        else:
                                            logger.warning("[NECROMANCY] Failed - max summons reached")
                                    else:
                                        logger.warning(f"[NECROMANCY] No corpses within {spell_range} units")
                                
                                elif spell_data.get('type') == 'buff':
                                    # Buff spell for summons
                                    duration = spell_data.get('duration', 20)
                                    effects = spell_data.get('effects', [])
                                    
                                    # Apply empower_undead buff
                                    if 'damage_boost' in effects and 'speed_boost' in effects:
                                        count = summoning_system.empower_summons(duration, damage_boost=0.5, speed_boost=0.3)
                                        
                                        if count > 0:
                                            # Visual effect on player
                                            summon_cast_effect_ui.add_effect(player.x, player.y, 'buff')
                                            logger.info(f"[BUFF] Empowered {count} summon(s) for {duration}s (+50% dmg, +30% speed)")
                                        else:
                                            logger.warning("[BUFF] No active summons to empower")
                        else:
                            logger.info("[SPELL] No primary spell selected. Press 'B' to open spellbook.")
                    elif key_bindings.is_action("cast_secondary_spell", event.key):
                        # Cast secondary spell
                        if player.secondary_spell:
                            # Get mouse position for targeting (use frame-start camera)
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            target_x = mouse_x + camera_x
                            target_y = mouse_y + camera_y
                            
                            spell_result = player.cast_spell(player.secondary_spell, target_x, target_y)
                            if spell_result:
                                # Update spell cooldown in HUD
                                spell_data = SPELLS.get(player.secondary_spell)
                                if spell_data:
                                    spell_hud.update_cooldown(player.secondary_spell, spell_data.get('cooldown', 1.0))
                                
                                # Get spell data from SPELLS dictionary
                                spell_data = SPELLS[player.secondary_spell]
                                spell_type = spell_data.get('type', 'projectile')
                                
                                # Check spell type and handle accordingly
                                if spell_type == 'projectile':
                                    # Projectile spell (fireball, etc.) - add to projectiles list
                                    spell_projectiles.append(spell_result)
                                    logger.info(f"[SPELL] {spell_data.get('name', player.secondary_spell)} cast (Secondary/E)")
                                    
                                elif spell_type in ['instant', 'self']:
                                    # Healing or buff spell - execute immediately
                                    from spell_projectile import SpellEffect, InstantSpell
                                    
                                    # Execute the instant spell if it has an execute method
                                    if isinstance(spell_result, InstantSpell) and hasattr(spell_result, 'execute'):
                                        spell_result.execute(player, enemies_list)
                                    
                                    # Create visual effect
                                    effect_color = (100, 255, 100) if spell_type == 'self' else (255, 255, 100)
                                    effect = SpellEffect(player.x, player.y, player.secondary_spell, effect_color)
                                    spell_effects.append(effect)
                                    logger.info(f"[SPELL] {spell_data.get('name', player.secondary_spell)} cast (Secondary/E)")
                                    
                                elif spell_data.get('type') == 'summon':
                                    # Summon creature
                                    summon_type_str = spell_data.get('summon_type', 'wolf')
                                    duration = spell_data.get('summon_duration', 30)
                                    
                                    # Convert string to SummonType enum
                                    summon_type = SummonType[summon_type_str.upper()]
                                    
                                    # Summon at target position
                                    summon = summoning_system.summon_creature(
                                        summon_type, target_x, target_y, player, duration
                                    )
                                    
                                    if summon:
                                        # Add visual effect
                                        summon_cast_effect_ui.add_effect(target_x, target_y, summon_type_str)
                                        logger.info(f"[SUMMON] Summoned {summon_type_str} at ({target_x}, {target_y})")
                                    else:
                                        logger.warning("[SUMMON] Failed - max summons reached (5)")
                                        
                                elif spell_data.get('type') == 'necromancy':
                                    # Raise dead spell
                                    spell_range = spell_data.get('range', 100)
                                    duration = spell_data.get('summon_duration', 60)
                                    max_raises = spell_data.get('max_raises', 1)
                                    
                                    # Find nearby corpses
                                    nearby_corpses = summoning_system.get_nearby_corpses(player.x, player.y, spell_range)
                                    
                                    if nearby_corpses:
                                        raised_count = 0
                                        for corpse in nearby_corpses[:max_raises]:
                                            undead = summoning_system.raise_dead(corpse, player, duration)
                                            if undead:
                                                summon_cast_effect_ui.add_effect(corpse['x'], corpse['y'], 'necromancy')
                                                raised_count += 1
                                            else:
                                                break  # Max summons reached
                                        
                                        if raised_count > 0:
                                            logger.info(f"[NECROMANCY] Raised {raised_count} undead minion(s)")
                                        else:
                                            logger.warning("[NECROMANCY] Failed - max summons reached")
                                    else:
                                        logger.warning(f"[NECROMANCY] No corpses within {spell_range} units")
                                
                                elif spell_data.get('type') == 'buff':
                                    # Buff spell for summons
                                    duration = spell_data.get('duration', 20)
                                    effects = spell_data.get('effects', [])
                                    
                                    # Apply empower_undead buff
                                    if 'damage_boost' in effects and 'speed_boost' in effects:
                                        count = summoning_system.empower_summons(duration, damage_boost=0.5, speed_boost=0.3)
                                        
                                        if count > 0:
                                            # Visual effect on player
                                            summon_cast_effect_ui.add_effect(player.x, player.y, 'buff')
                                            logger.info(f"[BUFF] Empowered {count} summon(s) for {duration}s (+50% dmg, +30% speed)")
                                        else:
                                            logger.warning("[BUFF] No active summons to empower")
                        else:
                            logger.info("[SPELL] No secondary spell selected. Press 'B' to open spellbook.")
                                        
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                      pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        # Check if shift is held - assign item to hotbar from inventory
                        keys_pressed = pygame.key.get_pressed()
                        if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
                            # Shift+number: Assign selected inventory item to hotbar
                            hotbar_slot_id = event.key - pygame.K_1  # 0-8
                            
                            # Get currently selected/hovered item from inventory
                            # For now, we'll add a simple message showing how to use hotbar
                            town_message = f"Drag items to hotbar or use H+{hotbar_slot_id+1} to assign"
                            town_message_timer = 120
                            logger.info(f"[HOTBAR] Shift+{hotbar_slot_id + 1} - Assign to hotbar")
                        else:
                            # Normal hotbar usage
                            hotbar_slot_id = event.key - pygame.K_1  # 0-8
                            
                            # Use hotbar slot
                            game_state = {
                                'spell_projectiles': spell_projectiles,
                                'spell_effects': spell_effects,
                                'player': player,
                                'game_time': game_time
                            }
                            success, message = hotbar_system.use_slot(hotbar_slot_id, player, game_state)
                            
                            if success:
                                # Trigger animation
                                hotbar_ui.trigger_slot_animation(hotbar_slot_id)
                                
                                # Handle spell casting if it was a spell slot
                                slot = hotbar_system.get_slot(hotbar_slot_id)
                                if slot and slot.type == HotbarSlotType.SPELL:
                                    # Cast the spell with mouse targeting (same as Q key)
                                    spell_id = slot.item_id
                                    if spell_id and spell_id in SPELLS:
                                        # Get mouse position for targeting
                                        mouse_x, mouse_y = pygame.mouse.get_pos()
                                        target_x = mouse_x + camera_x
                                        target_y = mouse_y + camera_y
                                        
                                        # Cast the spell
                                        spell_result = player.cast_spell(spell_id, target_x, target_y)
                                        if spell_result:
                                            # Update spell cooldown in HUD
                                            spell_data_temp = SPELLS.get(spell_id)
                                            if spell_data_temp:
                                                spell_hud.update_cooldown(spell_id, spell_data_temp.get('cooldown', 1.0))
                                            
                                            # Get spell data
                                            spell_data = SPELLS[spell_id]
                                            spell_type = spell_data.get('type', 'projectile')
                                            
                                            # Check if it's a projectile spell
                                            if spell_type == 'projectile':
                                                spell_projectiles.append(spell_result)
                                                logger.info(f"[SPELL] {spell_data.get('name', spell_id)} cast from hotbar")
                                            elif spell_type in ['instant', 'self']:
                                                # Healing or buff spell - execute immediately
                                                from spell_projectile import SpellEffect, InstantSpell
                                                
                                                # Execute the instant spell if it has an execute method
                                                if isinstance(spell_result, InstantSpell) and hasattr(spell_result, 'execute'):
                                                    spell_result.execute(player, enemies_list)
                                                
                                                # Create visual effect
                                                effect_color = (100, 255, 100) if spell_type == 'self' else (255, 255, 100)
                                                effect = SpellEffect(player.x, player.y, spell_id, effect_color)
                                                spell_effects.append(effect)
                                                logger.info(f"[SPELL] {spell_data.get('name', spell_id)} cast from hotbar")
                                
                                logger.info(f"[HOTBAR] Slot {hotbar_slot_id + 1}: {message}")
                            else:
                                if message not in ["Empty slot"]:
                                    town_message = message
                                    town_message_timer = 90
                                    logger.debug(f"[HOTBAR] Slot {hotbar_slot_id + 1}: {message}")
                    elif key_bindings.is_action("interact", event.key):
                        # DEBUG: Log E key press with current state
                        logger.info(f"[E KEY PRESSED] in_building_interior={in_building_interior}, current_interior={'exists' if current_interior else 'None'}, player_pos=({player.x}, {player.y})")
                        if in_building_interior and current_interior:
                            logger.info(f"[E KEY PRESSED] Interior details: floor={current_interior.current_floor}, num_floors={current_interior.num_floors}, building={current_interior_building.name if current_interior_building else 'unknown'}")
                        
                        # First check for nearby fire for cooking
                        nearby_fire = fire_manager.get_nearby_fire(player.x, player.y, max_distance=60)
                        if nearby_fire and not player.gathering_node:
                            cooking_ui.open(is_town_range=False)
                            logger.info("[COOKING] Opened cooking UI at campfire")
                        # Check for gathering node (if not currently gathering)
                        elif not player.gathering_node:
                            nearby_node = gathering_nodes_manager.get_nearby_node(player.x, player.y, max_distance=60)
                            if nearby_node:
                                success, message = player.start_gathering(nearby_node)
                                if success:
                                    logger.info(f"[GATHERING] {message}")
                                else:
                                    town_message = message
                                    town_message_timer = 120
                        
                        # FIXED: Check building interior FIRST before overworld NPCs
                        tutorial_npc_interacted = False  # Track if tutorial NPC was found
                        if in_building_interior and current_interior:
                            # Building interior interaction
                            pass  # Will be handled below
                        else:
                            # Tutorial NPC interaction now handled by T key dialogue system (lines ~6195-6260)
                            # No need for E key special handling anymore
                            
                            # Check for nearby overworld NPC if not gathering and NOT in building
                            if not tutorial_npc_interacted:
                                nearby_npc = None
                                if not player.gathering_node:
                                    nearby_npc = npc_manager.get_interactable_npc(player.x, player.y)
                                if nearby_npc:
                                    logger.info(f"Interacted with {nearby_npc.name}")
                                
                                # Check if NPC has advanced dialogue trees (Elder Sage, etc.)
                                if hasattr(nearby_npc, 'dialogue_trees') and nearby_npc.dialogue_trees:
                                    # Use advanced dialogue system
                                    advanced_dialogue_ui.start_dialogue(nearby_npc)
                                    logger.info(f"[DIALOGUE] Started advanced dialogue with {nearby_npc.name}")
                                else:
                                    # Use legacy dialogue system
                                    # Determine dialogue ID based on NPC
                                    if hasattr(nearby_npc, 'dialogue_id'):
                                        dialogue_id = nearby_npc.dialogue_id
                                    else:
                                        # Default dialogue IDs based on NPC name
                                        if 'merchant' in nearby_npc.name.lower():
                                            dialogue_id = 'merchant'
                                        elif 'elder' in nearby_npc.name.lower():
                                            dialogue_id = 'town_elder'
                                        elif 'guard' in nearby_npc.name.lower():
                                            dialogue_id = 'guard'
                                        else:
                                            dialogue_id = 'quest_giver_1'
                                    
                                    # Set dialogue tree ID on NPC and start dialogue
                                    nearby_npc.dialogue_tree_id = dialogue_id
                                    dialogue_manager.start_conversation(nearby_npc, player)
                                    dialogue_ui.start_dialogue(dialogue_manager)
                                    logger.info(f"[DIALOGUE] Started conversation with {nearby_npc.name}")
                                    
                                    # === NPC INTERACTION DISEASE TRANSMISSION ===
                                    # Small chance of catching diseases from NPCs
                                    if random.random() < 0.01:  # 1% chance per interaction
                                        # Check if NPC has diseases (if NPC entity tracking exists)
                                        npc_diseases = disease_manager.get_entity_diseases(nearby_npc.id)
                                        
                                        if npc_diseases:
                                            # Transmit one random disease from NPC
                                            disease_infection = random.choice(npc_diseases)
                                            disease = disease_infection.disease
                                            
                                            # Only transmit certain types (STDs have higher transmission from NPCs)
                                            if disease.type.name in ["STD", "MAGICAL_STD"]:
                                                transmission_chance = 0.3  # 30% if NPC has STD
                                            elif disease.type.name == "COMMON":
                                                transmission_chance = 0.15  # 15% if NPC has common disease
                                            else:
                                                transmission_chance = 0.05  # 5% for other diseases
                                            
                                            modifiers = {
                                                "npc_contact": 1.0,
                                                "has_protective_gear": 0.3 if player.has_plague_doctor_gear else 1.0,
                                                "is_plague_survivor": 0.5 if disease_manager.is_plague_survivor("player") else 1.0
                                            }
                                            
                                            infection_chance = disease_manager.calculate_infection_chance(transmission_chance, modifiers)
                                            
                                            if random.random() < infection_chance:
                                                disease_manager.infect_entity("player", disease.disease_id, f"npc_{nearby_npc.name}")
                                                logger.warning(f"[DISEASE] Player infected with {disease.name} from NPC {nearby_npc.name}")
                                        else:
                                            # Random STD infection from close contact (tavern NPCs, etc.)
                                            if in_town and random.random() < 0.005:  # 0.5% additional chance in towns
                                                std_diseases = ["draining_fever", "mana_sickness", "burden_disease"]
                                                disease_id = random.choice(std_diseases)
                                                
                                                modifiers = {
                                                    "npc_contact": 1.0,
                                                    "has_protective_gear": 0.5 if player.has_plague_doctor_gear else 1.0
                                                }
                                                
                                                disease_def = DISEASE_DEFINITIONS.get(disease_id)
                                                if disease_def:
                                                    infection_chance = disease_manager.calculate_infection_chance(
                                                        disease_def.base_infection_rate, modifiers)
                                                    
                                                    if random.random() < infection_chance:
                                                        disease_manager.infect_entity("player", disease_id, f"npc_{nearby_npc.name}")
                                                        logger.warning(f"[DISEASE] Player infected with {disease_id} from NPC contact")
                        
                        # E key no longer handles building interiors - all moved to F key
                        # Keep E key for gathering, fires, and overworld NPCs only
                        
                        # E key is now free - no building entry logic needed here
                        # All building entries (standalone and town buildings) use F key
                    elif key_bindings.is_action("dungeon_enter", event.key):
                        # F KEY: Handle building entries, building interior interactions, enter/exit dungeons and towns
                        # Check for nearby buildings to enter first (when not in interior/dungeon)
                        if not in_building_interior and not in_dungeon:
                            nearby_building = None
                            nearby_distance = 80
                            
                            # Check town instance buildings if in town
                            if in_town and current_town_instance:
                                for building in current_town_instance.buildings:
                                    dx = player.x - building.door_x
                                    dy = player.y - building.door_y
                                    distance = (dx * dx + dy * dy) ** 0.5
                                    
                                    if distance < nearby_distance:
                                        nearby_distance = distance
                                        nearby_building = building
                            
                            # Check standalone buildings (jail, tutorial shack) when not in town
                            elif not in_town:
                                dx = player.x - jail_building.door_x
                                dy = player.y - jail_building.door_y
                                jail_distance = (dx * dx + dy * dy) ** 0.5
                                
                                if jail_distance < nearby_distance:
                                    nearby_building = jail_building
                                
                                # Check standalone tutorial shack (if exists)
                                if tutorial_shack:
                                    dx = player.x - tutorial_shack.door_x
                                    dy = player.y - tutorial_shack.door_y
                                    shack_distance = (dx * dx + dy * dy) ** 0.5
                                    
                                    if shack_distance < nearby_distance:
                                        nearby_building = tutorial_shack
                            
                            if nearby_building:
                                # Enter the building interior
                                if nearby_building.type == BuildingType.JAIL:
                                    building_id = f"STANDALONE_{nearby_building.name}"
                                elif nearby_building.type == BuildingType.SHACK:
                                    building_id = f"TUTORIAL_SHACK"
                                else:
                                    building_id = f"{current_town_instance.name}_{nearby_building.name}"
                                
                                if building_id in building_interiors:
                                    in_building_interior = True
                                    current_interior = building_interiors[building_id]
                                    current_interior_building = nearby_building
                                    current_interior_building_id = building_id
                                    current_interior.current_floor = 1
                                    
                                    # Fix old inn staircases (legacy save compatibility)
                                    if nearby_building.type == BuildingType.INN and current_interior.num_floors > 1:
                                        for obj in current_interior.objects:
                                            if obj.type == "staircase":
                                                if obj.x == 300 and obj.y == 600:
                                                    new_x = current_interior.width // 2 - 150
                                                    new_y = current_interior.height - 280
                                                    obj.x = new_x
                                                    obj.y = new_y
                                                    logger.info(f"[INTERIOR] Updated staircase position")
                                    
                                    spawn_x, spawn_y = current_interior.get_spawn_position()
                                    player.x = spawn_x
                                    player.y = spawn_y
                                    
                                    logger.info(f"[INTERIOR] Entered {building_id}")
                                    
                                    if current_interior.num_floors > 1:
                                        town_message = f"Entered {nearby_building.name}\nPress F near stairs to change floors\nPress F near door to exit"
                                    else:
                                        town_message = f"Entered {nearby_building.name}\nPress F near door to exit"
                                    town_message_timer = 120
                                else:
                                    logger.warning(f"[INTERIOR] No interior found for {building_id}")
                            
                            # Check for nearby library (special case - no interior, just opens UI)
                            elif not nearby_building and in_town and current_town_instance and nearby_library:
                                # Open library UI if library is open
                                if nearby_library.is_open(game_time.hour):
                                    library_ui.open(nearby_library)
                                    logger.info(f"[LIBRARY] Opened {nearby_library.town_name} Library")
                                else:
                                    town_message = "Library is closed\n(Open 8 AM - 8 PM)"
                                    town_message_timer = 120
                                    logger.info(f"[LIBRARY] Attempted to open closed library")
                            
                            # Check for nearby mage tower (special case - no interior, just opens UI)
                            elif not nearby_building and in_town and current_town_instance and nearby_mage:
                                # Open mage UI
                                mage_ui.open(nearby_mage)
                                logger.info(f"[MAGE] Opened {nearby_mage.name} in {nearby_mage.town_name}")
                            
                            # Check for nearby town gate to enter (when outside town)
                            elif not nearby_building and not in_town and nearby_gate_town:
                                # Enter the town
                                town_inst = town_instances.get(nearby_gate_town)
                                if town_inst:
                                    current_town_instance = town_inst
                                    
                                    # Check for curfew
                                    current_hour, _ = game_time.get_time_hm()
                                    if curfew_system.is_curfew_active(nearby_gate_town) and curfew_system.is_curfew_hours(current_hour):
                                        # Show curfew warning dialog
                                        curfew_warning_dialog['active'] = True
                                        curfew_warning_dialog['town_name'] = nearby_gate_town
                                        logger.info(f"[CURFEW] Warning shown for {nearby_gate_town} (curfew hours: {curfew_system.curfew_start}-{curfew_system.curfew_end})")
                                        continue  # Don't enter yet, wait for player decision
                                    
                                    # Store position before entering town
                                    town_return_pos = (player.x, player.y)
                                    
                                    # Check if player is wanted before entering
                                    player.is_wanted = wanted_system.get_wanted_status(id(player), game_time)
                                    
                                    # Apply town entry fee if lockdown is active
                                    entry_fee = town_entry_fee_system.charge_entry(player, town_treasury_system, current_town_instance.name)
                                    if entry_fee > 0:
                                        town_message = f"💰 Entry Fee Charged: {entry_fee}g (Lockdown Active)"
                                        town_message_timer = 180
                                        logger.info(f"[MAYOR] Charged {entry_fee}g entry fee to player")
                                    
                                    if player.is_wanted:
                                        town_message = "⚠ You are WANTED! Guards will pursue you on sight!"
                                        town_message_timer = 240
                                        logger.warning(f"[WANTED] Player entered {nearby_gate_town} while wanted (bounty: {player.wanted_level}g)")
                                    
                                    in_town = True
                                    
                                    # Clear enemies when entering town (towns are safe zones)
                                    enemies_list.clear()
                                    logger.info("Cleared enemies when entering town")
                                    
                                    # Enforce weapon restrictions if active (mayor powers)
                                    if weapon_restriction_system.restriction_active:
                                        confiscated_weapons = weapon_restriction_system.enforce(player, nearby_gate_town)
                                        if confiscated_weapons:
                                            player.weapons_stored = confiscated_weapons
                                            town_message = f"⚔️ WEAPON RESTRICTION!\n{len(confiscated_weapons)} weapon(s) confiscated\nStored in Town Hall guard locker\n(Can be retrieved when you leave...\nor stolen from the mayor's office)"
                                            town_message_timer = 300
                                            logger.info(f"[MAYOR] Confiscated {len(confiscated_weapons)} weapons from player")
                                    
                                    # Move player to town gate (spawn point)
                                    player.x = current_town_instance.gate_x
                                    player.y = current_town_instance.gate_y
                                    logger.info(f"Entered town: {nearby_gate_town}")
                                else:
                                    logger.error(f"Town instance not found for {nearby_gate_town}")
                            
                            # Check for nearby town exit (when inside town)
                            elif not nearby_building and in_town and near_town_exit:
                                # Return confiscated weapons if any
                                if weapon_restriction_system.restriction_active and hasattr(player, 'weapons_stored') and player.weapons_stored:
                                    weapon_restriction_system.return_weapons(player, player.weapons_stored)
                                    town_message = f"⚔️ Your {len(player.weapons_stored)} confiscated weapon(s) have been returned."
                                    town_message_timer = 180
                                    logger.info(f"[MAYOR] Returned {len(player.weapons_stored)} weapons to player")
                                    player.weapons_stored = []
                                
                                # Stop any guards chasing the player
                                for guard in town_guards:
                                    if guard.state == "chase" and guard.chase_target == player:
                                        guard.chase_target = None
                                        guard.change_state("patrol" if guard.is_patrolling else "idle")
                                
                                if town_return_pos:
                                    player.x, player.y = town_return_pos
                                
                                in_town = False
                                current_town_instance = None
                                logger.info("Exited town - returned to overworld")
                            
                            # Check for nearby dungeon entrance (when outside town)
                            elif not nearby_building and not in_town and nearby_dungeon:
                                # Find the nearby dungeon entrance coordinates
                                selected_entrance = None
                                for entrance_x, entrance_y in dungeon_entrances:
                                    distance = ((player.x - entrance_x) ** 2 + (player.y - entrance_y) ** 2) ** 0.5
                                    if distance < config.TILE_SIZE * 2:
                                        selected_entrance = (entrance_x, entrance_y)
                                        break
                                
                                if selected_entrance:
                                    # Check if dungeon instance exists and needs reset
                                    existing_dungeon = dungeon_instances.get(selected_entrance)
                                    
                                    if existing_dungeon and hasattr(existing_dungeon, 'check_and_reset'):
                                        existing_dungeon.check_and_reset(game_time.day_count)
                                    
                                    # Create new dungeon if none exists or it was reset
                                    if not existing_dungeon or (hasattr(existing_dungeon, 'cleared') and 
                                        existing_dungeon.last_cleared_day and 
                                        game_time.day_count - existing_dungeon.last_cleared_day >= existing_dungeon.reset_days):
                                        
                                        # Generate fresh dungeon with variety system
                                        layout_choice = random.choice(['cave', 'rooms_and_corridors'])
                                        
                                        # Determine difficulty based on player level
                                        if player.level < 5:
                                            difficulty = "normal"
                                        elif player.level < 10:
                                            difficulty = random.choice(["normal", "hard"])
                                        elif player.level < 15:
                                            difficulty = random.choice(["normal", "hard", "nightmare"])
                                        else:
                                            difficulty = random.choice(["hard", "nightmare", "hell"])
                                        
                                        current_dungeon = create_dungeon(
                                            width=60,
                                            height=40,
                                            theme='cave',
                                            layout_style=layout_choice,
                                            difficulty=difficulty,
                                            modifier=None,  # Random modifier rolled in create_dungeon
                                            player_level=player.level
                                        )
                                        dungeon_instances[selected_entrance] = current_dungeon
                                        logger.info(f"Generated new {layout_choice} dungeon with {difficulty} difficulty")
                                    else:
                                        # Use existing dungeon instance
                                        current_dungeon = existing_dungeon
                                        logger.info(f"Entering existing dungeon (cleared: {getattr(current_dungeon, 'cleared', False)})")
                                    
                                    if current_dungeon:
                                        # Check if dungeon has a boss
                                        has_boss = False
                                        boss_type = None
                                        if hasattr(current_dungeon, 'enemies'):
                                            for enemy in current_dungeon.enemies:
                                                if hasattr(enemy, 'boss_type'):
                                                    has_boss = True
                                                    boss_type = enemy.boss_type
                                                    break
                                        
                                        # If dungeon has a boss, show loot preview first
                                        if has_boss and boss_type:
                                            # Store dungeon entry state for after preview
                                            pending_dungeon_entry['active'] = True
                                            pending_dungeon_entry['dungeon'] = current_dungeon
                                            pending_dungeon_entry['entrance_pos'] = (player.x, player.y)
                                            pending_dungeon_entry['entrance_coords'] = selected_entrance
                                            
                                            # Show boss loot preview
                                            loot_preview_data = enhanced_loot.get_boss_loot_preview(boss_type)
                                            boss_loot_preview.show(boss_type, loot_preview_data)
                                            logger.info(f"[LOOT] Showing boss loot preview for {boss_type}")
                                        else:
                                            # No boss or preview already shown - enter dungeon immediately
                                            dungeon_entrance_pos = (player.x, player.y)
                                            in_dungeon = True
                                            
                                            # Track dungeon entry for achievements
                                            player.ach_dungeons_entered += 1
                                            achievement_manager.check_all_exploration(
                                                player.ach_towns_visited,
                                                player.ach_distance_traveled,
                                                player.ach_dungeons_entered
                                            )
                                            unlocked = achievement_manager.get_recent_unlock()
                                            if unlocked:
                                                achievement_popup.show(unlocked)
                                            
                                            # Set player spawn position in dungeon
                                            player.x = current_dungeon.spawn_x
                                            player.y = current_dungeon.spawn_y
                                            enemies_list = current_dungeon.enemies[:]
                                            logger.info(f"[DUNGEON] Entered dungeon with {len(enemies_list)} enemies")
                        
                        elif in_building_interior and current_interior:
                            # Handle building interior interactions (exit doors, stairs, chests, NPCs, etc.)
                            logger.info(f"[F KEY] In building interior, player at ({player.x}, {player.y}), floor={current_interior.current_floor}")
                            
                            # Check for nearby exit door
                            exit_door = current_interior.get_exit_door()
                            if exit_door:
                                dx = player.x - (exit_door.x + exit_door.width / 2)
                                dy = player.y - (exit_door.y + exit_door.height / 2)
                                distance = (dx * dx + dy * dy) ** 0.5
                                
                                logger.info(f"[F KEY] Exit door distance: {distance:.1f} pixels")
                                
                                if distance < 60:
                                    # Exit the interior, return to town
                                    if current_interior_building:
                                        player.x = current_interior_building.door_x
                                        player.y = current_interior_building.door_y + 30  # Place player just outside
                                        in_building_interior = False
                                        current_interior = None
                                        current_interior_building = None
                                        current_interior_building_id = None
                                        logger.info(f"[INTERIOR] Exited building interior")
                                    else:
                                        logger.error("[INTERIOR] No building reference to return to!")
                                else:
                                    # Check for nearby NPCs first
                                    nearby_npc = current_interior.get_nearby_npc(player.x, player.y, max_distance=60)
                                    logger.info(f"[F KEY] Nearby NPC check: {nearby_npc['name'] if nearby_npc else 'None'}")
                                    
                                    if nearby_npc:
                                        # Special handling for Max (lootbox merchant)
                                        if nearby_npc.get('role') == 'lootbox_merchant':
                                            logger.info(f"[LOOTBOX] Player interacting with Max inside shop")
                                            max_shop_interaction.start_interaction(player)
                                            logger.info("[LOOTBOX] Max starts his predatory sales pitch")
                                        
                                        # Special handling for innkeepers - open inn rental menu
                                        elif nearby_npc.get('role') == 'innkeeper':
                                            # Find the inn for this building
                                            if current_interior_building and hasattr(current_interior_building, 'type'):
                                                if current_interior_building.type == BuildingType.INN:
                                                    # Get the inn from the inn manager
                                                    for inn in inn_manager.inns:
                                                        if inn.building == current_interior_building:
                                                            inn_ui.open(inn)
                                                            logger.info(f"[INN] Opened inn menu via innkeeper interaction")
                                                            break
                                                    else:
                                                        town_message = "Innkeeper: Welcome! Unfortunately I can't help you right now."
                                                        town_message_timer = 120
                                        else:
                                            # Start dialogue with NPC
                                            class TempNPC:
                                                def __init__(self, npc_dict):
                                                    self.id = npc_dict.get('role', 'npc')
                                                    self.name = npc_dict.get('name', 'NPC')
                                                    self.dialogue_tree_id = npc_dict.get('role', 'generic')
                                                    self.personality = 'friendly'
                                            
                                            temp_npc = TempNPC(nearby_npc)
                                            success, message = dialogue_manager.start_conversation(temp_npc, player, weather_system.current_weather if weather_system else None)
                                            if success:
                                                dialogue_ui.start_dialogue(dialogue_manager, temp_npc.id)
                                                logger.info(f"[DIALOGUE] Started conversation with {nearby_npc.get('name')}")
                                            else:
                                                town_message = message
                                                town_message_timer = 120
                                    else:
                                        # Check for nearby interactable objects (chests, altars, staircases, etc.)
                                        logger.info(f"[F KEY] No nearby NPC, checking for interactable objects...")
                                        
                                        # Use larger range (200 pixels) to easily find staircases and large objects
                                        nearby_obj = current_interior.get_nearby_interactable(player.x, player.y, max_distance=200)
                                        
                                        if nearby_obj:
                                            logger.info(f"[INTERIOR] Found nearby object: {nearby_obj.name} (type: {nearby_obj.type}) at distance")
                                            if nearby_obj.type == "staircase":
                                                # Floor transition (staircase)
                                                logger.info(f"[STAIRCASE] Detected: {nearby_obj.name}, target_floor={nearby_obj.target_floor}, stair_type={nearby_obj.stair_type}, current_floor={current_interior.current_floor}")
                                                
                                                if nearby_obj.target_floor:
                                                    success = current_interior.change_floor(nearby_obj.target_floor)
                                                    logger.info(f"[STAIRCASE] change_floor returned: {success}")
                                                    
                                                    if success:
                                                        direction = "upstairs" if nearby_obj.stair_type == "up" else "downstairs"
                                                        town_message = f"Went {direction} to Floor {nearby_obj.target_floor}"
                                                        town_message_timer = 120
                                                        logger.info(f"[INTERIOR] Changed to floor {nearby_obj.target_floor}")
                                                    else:
                                                        town_message = "Can't use these stairs"
                                                        town_message_timer = 90
                                                        logger.warning(f"[STAIRCASE] change_floor failed!")
                                                else:
                                                    town_message = "Stairs are blocked"
                                                    town_message_timer = 90
                                            elif nearby_obj.type == "chest":
                                                # CHEST INTERACTION - Full lockpicking and theft system
                                                if nearby_obj.locked:
                                                    # Check if player has lockpicks
                                                    lockpick_count = player.inventory.get('lockpick', 0)
                                                    
                                                    if lockpick_count <= 0:
                                                        town_message = f"{nearby_obj.name} is locked!\nYou need a lockpick to attempt picking this lock."
                                                        town_message_timer = 180
                                                        logger.info(f"[LOCKPICK] No lockpicks found for {nearby_obj.name}")
                                                    else:
                                                        # WITNESS DETECTION - Check if anyone sees the lockpicking attempt
                                                        witnessed = False
                                                        witness_name = None
                                                        
                                                        # Check NPCs inside the building first
                                                        if in_building_interior and current_interior:
                                                            for npc_data in current_interior.npcs:
                                                                dx = abs(player.x - npc_data['x'])
                                                                dy = abs(player.y - npc_data['y'])
                                                                distance = (dx * dx + dy * dy) ** 0.5
                                                                if distance < 250:  # NPC can see the player
                                                                    witnessed = True
                                                                    witness_name = npc_data['name']
                                                                    break
                                                        
                                                        # Also check town NPCs if inside a building in a town
                                                        if not witnessed and in_town and current_town_instance:
                                                            for npc in gatherer_npc_manager.npcs:
                                                                if not hasattr(npc, 'current_town') or npc.current_town != current_town_instance.name:
                                                                    continue
                                                                dx = abs(player.x - npc.x)
                                                                dy = abs(player.y - npc.y)
                                                                distance = (dx * dx + dy * dy) ** 0.5
                                                                if distance < 250:
                                                                    witnessed = True
                                                                    witness_name = npc.name if hasattr(npc, 'name') else "Someone"
                                                                    break
                                                        
                                                        # If witnessed attempting to lockpick owned property, instant wanted!
                                                        if witnessed and nearby_obj.owned:
                                                            bounty_amount = 30  # Bounty for ATTEMPTING to break in
                                                            player.wanted_level += bounty_amount
                                                            wanted_system.set_wanted(id(player), 'theft', game_time)
                                                            player.is_wanted = True
                                                            
                                                            # Reputation penalty for attempted theft
                                                            if in_town and current_town_instance:
                                                                reputation_system.modify_faction_reputation(current_town_instance.name, -25)
                                                                logger.info(f"[REPUTATION] Lost 25 reputation with {current_town_instance.name} for attempted theft")
                                                            
                                                            # Ban from town for 3 days
                                                            if in_town and current_town_instance:
                                                                town_cooldown_system.set_cooldown(id(player), current_town_instance.name, game_time)
                                                                logger.warning(f"[COOLDOWN] Player banned from {current_town_instance.name} for 3 days")
                                                            
                                                            # Record crime with criminal rank system
                                                            record_crime_with_rank(
                                                                crime_type='theft',
                                                                location=f"{current_town_instance.name if current_town_instance else 'Unknown'} - {current_interior_building.name if current_interior_building else 'Unknown'}",
                                                                item=nearby_obj.name,
                                                                witnessed=True,
                                                                witness=witness_name
                                                            )
                                                            
                                                            town_name = current_town_instance.name if current_town_instance else "this town"
                                                            town_message = f"⚠ {witness_name} SAW YOU!\n\"Stop! Thief!\"\nBounty +{bounty_amount}g (Total: {player.wanted_level}g)\n🚫 BANNED from {town_name} for 3 days!"
                                                            town_message_timer = 300
                                                            logger.warning(f"[CRIME] {witness_name} witnessed lockpick attempt! Bounty +{bounty_amount}")
                                                            continue  # Skip the lockpicking, they've been caught!
                                                        
                                                        # Attempt lockpicking
                                                        # Calculate difficulty
                                                        if hasattr(nearby_obj, 'lockpick_difficulty'):
                                                            difficulty = nearby_obj.lockpick_difficulty
                                                        elif "Strongbox" in nearby_obj.name or "Vault" in nearby_obj.name:
                                                            difficulty = 60  # Very hard
                                                        elif "Mayor" in nearby_obj.name:
                                                            difficulty = 40  # Hard
                                                        elif "Records" in nearby_obj.name or "Bank" in nearby_obj.name:
                                                            difficulty = 25  # Medium
                                                        else:
                                                            difficulty = 15  # Easy
                                                        
                                                        # Calculate success chance
                                                        base_chance = 10
                                                        lockpick_bonus = 0
                                                        if hasattr(player, 'acquired_skills'):
                                                            if 'basic_lock_picking' in player.acquired_skills:
                                                                lockpick_bonus += 10
                                                            if 'improved_lock_picking' in player.acquired_skills:
                                                                lockpick_bonus += 15
                                                            if 'advanced_lock_picking' in player.acquired_skills:
                                                                lockpick_bonus += 20
                                                            if 'master_lock_picking' in player.acquired_skills:
                                                                lockpick_bonus += 30
                                                        
                                                        # Add luck bonus
                                                        luck_bonus = 0
                                                        if hasattr(player, 'stats'):
                                                            luck = player.stats.get_stat("Luck")
                                                            luck_bonus = luck // 2
                                                        
                                                        success_chance = base_chance + lockpick_bonus + luck_bonus - difficulty
                                                        success_chance = max(5, min(95, success_chance))
                                                        
                                                        # Roll for success
                                                        roll = random.randint(1, 100)
                                                        
                                                        if roll <= success_chance:
                                                            # SUCCESS!
                                                            nearby_obj.locked = False
                                                            
                                                            # SPECIAL: Check if this is the confiscated weapons chest
                                                            is_confiscated_weapons_chest = getattr(nearby_obj, 'is_confiscated_weapons', False)
                                                            
                                                            if is_confiscated_weapons_chest and current_town_instance:
                                                                # Stealing confiscated weapons back!
                                                                stolen_count, stolen_weapons = weapon_restriction_system.steal_from_town_hall(player, current_town_instance.name)
                                                                
                                                                if stolen_count > 0:
                                                                    logger.info(f"[WEAPON THEFT] Player stole {stolen_count} confiscated weapons")
                                                                    town_message = f"🗡️ WEAPONS RETRIEVED!\nReclaimed {stolen_count} confiscated weapon(s)\nfrom the town guard locker."
                                                                    town_message_timer = 240
                                                                else:
                                                                    logger.info(f"[WEAPON THEFT] No confiscated weapons found")
                                                                    town_message = "The weapons locker is empty.\n(No weapons currently confiscated)"
                                                                    town_message_timer = 180
                                                                
                                                                nearby_obj.opened = True
                                                                continue
                                                            
                                                            # Collect items from chest
                                                            loot_items = []
                                                            total_gold = 0
                                                            is_theft_from_owned = nearby_obj.owned if hasattr(nearby_obj, 'owned') else False
                                                            
                                                            for item_name, count in nearby_obj.items:
                                                                if item_name == "dubloons":
                                                                    player.gold += count
                                                                    total_gold += count
                                                                else:
                                                                    if item_name not in player.inventory:
                                                                        player.inventory[item_name] = 0
                                                                    player.inventory[item_name] += count
                                                                    loot_items.append(f"{item_name} x{count}")
                                                                    
                                                                    # Mark items as stolen
                                                                    if is_theft_from_owned:
                                                                        for _ in range(count):
                                                                            stolen_item = StolenItem(item_name, item_name)
                                                                            player.stolen_items.append(stolen_item)
                                                                            logger.info(f"[THEFT] Marked {item_name} as stolen")
                                                            
                                                            # CRIME DETECTION
                                                            is_theft = False
                                                            if nearby_obj.owned:
                                                                # Check for witnesses again after opening
                                                                witnessed = False
                                                                witness_name = None
                                                                
                                                                if in_building_interior and current_interior:
                                                                    for npc_data in current_interior.npcs:
                                                                        dx = abs(player.x - npc_data['x'])
                                                                        dy = abs(player.y - npc_data['y'])
                                                                        distance = (dx * dx + dy * dy) ** 0.5
                                                                        if distance < 300:
                                                                            witnessed = True
                                                                            witness_name = npc_data['name']
                                                                            break
                                                                
                                                                if not witnessed and in_town and current_town_instance:
                                                                    for npc in gatherer_npc_manager.npcs:
                                                                        if not hasattr(npc, 'current_town') or npc.current_town != current_town_instance.name:
                                                                            continue
                                                                        dx = abs(player.x - npc.x)
                                                                        dy = abs(player.y - npc.y)
                                                                        distance = (dx * dx + dy * dy) ** 0.5
                                                                        if distance < 300:
                                                                            witnessed = True
                                                                            witness_name = npc.name if hasattr(npc, 'name') else "Someone"
                                                                            break
                                                                
                                                                is_theft = True
                                                                record_crime_with_rank(
                                                                    crime_type='theft',
                                                                    location=f"{current_town_instance.name if current_town_instance else 'Unknown'} - {current_interior_building.name if current_interior_building else 'Unknown'}",
                                                                    item=nearby_obj.name,
                                                                    witnessed=witnessed,
                                                                    witness=witness_name if witnessed else None
                                                                )
                                                                
                                                                if witnessed:
                                                                    bounty_amount = 50 + (total_gold // 2)
                                                                    player.wanted_level += bounty_amount
                                                                    wanted_system.set_wanted(id(player), 'theft', game_time)
                                                                    player.is_wanted = True
                                                                    
                                                                    if in_town and current_town_instance:
                                                                        reputation_system.modify_faction_reputation(current_town_instance.name, -40)
                                                                        logger.info(f"[REPUTATION] Lost 40 reputation with {current_town_instance.name} for theft")
                                                                        town_cooldown_system.set_cooldown(id(player), current_town_instance.name, game_time)
                                                                        logger.warning(f"[COOLDOWN] Player banned from {current_town_instance.name} for 3 days")
                                                                    
                                                                    logger.warning(f"[CRIME] Theft witnessed! Bounty +{bounty_amount}")
                                                                else:
                                                                    logger.info(f"[CRIME] Theft unwitnessed from {nearby_obj.name}")
                                                            
                                                            nearby_obj.opened = True
                                                            
                                                            # Create message
                                                            loot_msg = f"Unlocked {nearby_obj.name}!"
                                                            if total_gold > 0:
                                                                loot_msg += f"\nFound: {total_gold} dubloons"
                                                            if loot_items:
                                                                loot_msg += f"\n{', '.join(loot_items)}"
                                                            
                                                            if is_theft:
                                                                if nearby_obj.owner:
                                                                    loot_msg += f"\n[STOLEN from {nearby_obj.owner}]"
                                                                crime_record = player.crimes_committed[-1]
                                                                if crime_record['witnessed']:
                                                                    town_name = current_town_instance.name if current_town_instance else "this town"
                                                                    loot_msg += f"\n⚠ WITNESSED! Bounty: {player.wanted_level}g\n🚫 BANNED from {town_name} for 3 days!"
                                                                else:
                                                                    loot_msg += "\n(Theft undetected)"
                                                            
                                                            town_message = loot_msg
                                                            town_message_timer = 300
                                                            logger.info(f"[LOCKPICK] Successfully picked {nearby_obj.name}")
                                                            
                                                            # Achievement tracking
                                                            if hasattr(player, 'ach_locks_picked'):
                                                                player.ach_locks_picked += 1
                                                            else:
                                                                player.ach_locks_picked = 1
                                                        else:
                                                            # FAILURE
                                                            break_chance = 30 - (lockpick_bonus // 2)
                                                            break_chance = max(5, min(50, break_chance))
                                                            broke_pick = random.randint(1, 100) <= break_chance
                                                            
                                                            if broke_pick:
                                                                player.inventory['lockpick'] = max(0, player.inventory.get('lockpick', 0) - 1)
                                                                remaining_picks = player.inventory.get('lockpick', 0)
                                                                town_message = f"Failed to pick {nearby_obj.name}!\n({success_chance}% chance)\nYour lockpick BROKE! ({remaining_picks} remaining)"
                                                                logger.info(f"[LOCKPICK] Failed and broke lockpick on {nearby_obj.name}")
                                                            else:
                                                                town_message = f"Failed to pick {nearby_obj.name}.\n({success_chance}% chance)\nLockpick intact. ({lockpick_count} remaining)"
                                                                logger.info(f"[LOCKPICK] Failed but lockpick intact")
                                                            
                                                            town_message_timer = 180
                                                else:
                                                    # Chest already unlocked
                                                    if nearby_obj.opened:
                                                        town_message = f"{nearby_obj.name} is empty."
                                                        town_message_timer = 120
                                                    else:
                                                        # SPECIAL: Check if confiscated weapons chest
                                                        is_confiscated_weapons_chest = getattr(nearby_obj, 'is_confiscated_weapons', False)
                                                        
                                                        if is_confiscated_weapons_chest and current_town_instance:
                                                            stolen_count, stolen_weapons = weapon_restriction_system.steal_from_town_hall(player, current_town_instance.name)
                                                            
                                                            if stolen_count > 0:
                                                                logger.info(f"[WEAPON THEFT] Player stole {stolen_count} confiscated weapons")
                                                                town_message = f"🗡️ WEAPONS RETRIEVED!\nReclaimed {stolen_count} confiscated weapon(s)\nfrom the town guard locker."
                                                                town_message_timer = 240
                                                            else:
                                                                logger.info(f"[WEAPON THEFT] No confiscated weapons found")
                                                                town_message = "The weapons locker is empty.\n(No weapons currently confiscated)"
                                                                town_message_timer = 180
                                                            
                                                            nearby_obj.opened = True
                                                            continue
                                                        
                                                        # Unlocked chest - open and collect items
                                                        loot_items = []
                                                        total_gold = 0
                                                        is_theft_from_owned = nearby_obj.owned if hasattr(nearby_obj, 'owned') else False
                                                        
                                                        for item_name, count in nearby_obj.items:
                                                            if item_name == "dubloons":
                                                                player.gold += count
                                                                total_gold += count
                                                            else:
                                                                if item_name not in player.inventory:
                                                                    player.inventory[item_name] = 0
                                                                player.inventory[item_name] += count
                                                                loot_items.append(f"{item_name} x{count}")
                                                                
                                                                if is_theft_from_owned:
                                                                    for _ in range(count):
                                                                        stolen_item = StolenItem(item_name, item_name)
                                                                        player.stolen_items.append(stolen_item)
                                                                        logger.info(f"[THEFT] Marked {item_name} as stolen")
                                                        
                                                        # CRIME DETECTION
                                                        is_theft = False
                                                        if nearby_obj.owned:
                                                            witnessed = False
                                                            witness_name = None
                                                            
                                                            if in_building_interior and current_interior:
                                                                for npc_data in current_interior.npcs:
                                                                    dx = abs(player.x - npc_data['x'])
                                                                    dy = abs(player.y - npc_data['y'])
                                                                    distance = (dx * dx + dy * dy) ** 0.5
                                                                    if distance < 300:
                                                                        witnessed = True
                                                                        witness_name = npc_data['name']
                                                                        break
                                                            
                                                            if not witnessed and in_town and current_town_instance:
                                                                for npc in gatherer_npc_manager.npcs:
                                                                    if not hasattr(npc, 'current_town') or npc.current_town != current_town_instance.name:
                                                                        continue
                                                                    dx = abs(player.x - npc.x)
                                                                    dy = abs(player.y - npc.y)
                                                                    distance = (dx * dx + dy * dy) ** 0.5
                                                                    if distance < 300:
                                                                        witnessed = True
                                                                        witness_name = npc.name if hasattr(npc, 'name') else "Someone"
                                                                        break
                                                            
                                                            is_theft = True
                                                            record_crime_with_rank(
                                                                crime_type='theft',
                                                                location=f"{current_town_instance.name if current_town_instance else 'Unknown'} - {current_interior_building.name if current_interior_building else 'Unknown'}",
                                                                item=nearby_obj.name,
                                                                witnessed=witnessed,
                                                                witness=witness_name if witnessed else None
                                                            )
                                                            
                                                            if witnessed:
                                                                bounty_amount = 30 + (total_gold // 3)
                                                                player.wanted_level += bounty_amount
                                                                wanted_system.set_wanted(id(player), 'theft', game_time)
                                                                player.is_wanted = True
                                                                
                                                                if in_town and current_town_instance:
                                                                    reputation_system.modify_faction_reputation(current_town_instance.name, -30)
                                                                    logger.info(f"[REPUTATION] Lost 30 reputation")
                                                                    town_cooldown_system.set_cooldown(id(player), current_town_instance.name, game_time)
                                                                    logger.warning(f"[COOLDOWN] Player banned for 3 days")
                                                                
                                                                logger.warning(f"[CRIME] Theft witnessed from unlocked chest! Bounty +{bounty_amount}")
                                                            else:
                                                                logger.info(f"[CRIME] Theft unwitnessed from {nearby_obj.name}")
                                                        
                                                        nearby_obj.opened = True
                                                        
                                                        # Create message
                                                        loot_msg = f"Opened {nearby_obj.name}"
                                                        if total_gold > 0:
                                                            loot_msg += f"\nFound: {total_gold} dubloons"
                                                        if loot_items:
                                                            loot_msg += f"\n{', '.join(loot_items)}"
                                                        
                                                        if is_theft:
                                                            if nearby_obj.owner:
                                                                loot_msg += f"\n[STOLEN from {nearby_obj.owner}]"
                                                            crime_record = player.crimes_committed[-1]
                                                            if crime_record['witnessed']:
                                                                town_name = current_town_instance.name if current_town_instance else "this town"
                                                                loot_msg += f"\n⚠ WITNESSED! Bounty: {player.wanted_level}g\n🚫 BANNED from {town_name} for 3 days!"
                                                            else:
                                                                loot_msg += "\n(Theft undetected)"
                                                        
                                                        town_message = loot_msg
                                                        town_message_timer = 240
                                                        logger.info(f"[INTERIOR] Opened unlocked chest: {nearby_obj.name}")
                                            elif nearby_obj.type == "altar":
                                                # Altar interaction - open temple UI for healing options
                                                if current_interior_building and hasattr(current_interior_building, 'type'):
                                                    if current_interior_building.type == BuildingType.TEMPLE:
                                                        # Get the temple from temple_manager
                                                        temple_found = False
                                                        for temple in temple_manager.temples:
                                                            if temple.building == current_interior_building:
                                                                temple_ui.open(temple)
                                                                logger.info(f"[TEMPLE] Opened {temple.name} menu via altar interaction")
                                                                temple_found = True
                                                                break
                                                        
                                                        if not temple_found:
                                                            town_message = "You kneel before the altar..."
                                                            town_message_timer = 120
                                                            logger.warning(f"[TEMPLE] Could not find temple for altar interaction")
                                                    else:
                                                        town_message = "You feel a sacred presence..."
                                                        town_message_timer = 120
                                                else:
                                                    town_message = "You approach the altar..."
                                                    town_message_timer = 120
                                            elif nearby_obj.type == "room_door":
                                                # Individual room door (lockable, part of inn system)
                                                if nearby_obj.locked and not nearby_obj.opened:
                                                    lockpick_count = player.inventory.get('lockpick', 0)
                                                    room_num = nearby_obj.room_number
                                                    
                                                    # Check if this is player's rented room
                                                    player_room = current_interior.get_rented_room(id(player)) if hasattr(current_interior, 'get_rented_room') else None
                                                    
                                                    if player_room == room_num:
                                                        # Player's rented room
                                                        nearby_obj.locked = False
                                                        nearby_obj.opened = True
                                                        nearby_obj.solid = False
                                                        town_message = f"Opened Room {room_num} (your room)"
                                                        town_message_timer = 120
                                                        logger.info(f"[INN] Player opened their rented room {room_num}")
                                                    elif lockpick_count <= 0:
                                                        town_message = f"Room {room_num} is locked!\nNeed lockpick to pick the lock.\n(Or rent at reception)"
                                                        town_message_timer = 180
                                                        logger.info(f"[INN] Room {room_num} locked, no lockpicks")
                                                    else:
                                                        # Attempt to lockpick the room door
                                                        difficulty = nearby_obj.lockpick_difficulty if hasattr(nearby_obj, 'lockpick_difficulty') else 30
                                                        
                                                        # Check for witnesses
                                                        witnessed = False
                                                        witness_name = None
                                                        if current_interior:
                                                            for npc_data in current_interior.npcs:
                                                                # Only check NPCs on same floor
                                                                if npc_data.get('floor', 1) != current_interior.current_floor:
                                                                    continue
                                                                dx = abs(player.x - npc_data['x'])
                                                                dy = abs(player.y - npc_data['y'])
                                                                distance = (dx * dx + dy * dy) ** 0.5
                                                                if distance < 250:
                                                                    witnessed = True
                                                                    witness_name = npc_data['name']
                                                                    break
                                                        
                                                        if witnessed:
                                                            # Caught trying to break into room!
                                                            bounty_amount = 40
                                                            player.wanted_level += bounty_amount
                                                            wanted_system.set_wanted(id(player), 'theft', game_time)
                                                            player.is_wanted = True
                                                            if in_town and current_town_instance:
                                                                reputation_system.modify_faction_reputation(current_town_instance.name, -30)
                                                                town_cooldown_system.set_cooldown(id(player), current_town_instance.name, game_time)
                                                                record_crime_with_rank(
                                                                    crime_type='burglary',
                                                                    location=f"{current_town_instance.name} Inn - Room {room_num}",
                                                                    witnessed=True,
                                                                    witness=witness_name
                                                                )
                                                            town_message = f"⚠ {witness_name} CAUGHT YOU!\n\"Breaking into rooms?!\"\nBounty +{bounty_amount}g\n🚫 BANNED!"
                                                            town_message_timer = 300
                                                            logger.warning(f"[CRIME] Caught breaking into Room {room_num}")
                                                        else:
                                                            # Attempt lockpick
                                                            success_chance = max(10, min(90, 50 - difficulty))
                                                            roll = random.randint(1, 100)
                                                            
                                                            if roll <= success_chance:
                                                                # Success!
                                                                nearby_obj.locked = False
                                                                nearby_obj.opened = True
                                                                nearby_obj.solid = False
                                                                player.inventory['lockpick'] = lockpick_count - 1
                                                                town_message = f"✓ Picked lock! Room {room_num} opened\nLockpick broken ({lockpick_count - 1} left)"
                                                                town_message_timer = 180
                                                                logger.info(f"[LOCKPICK] Successfully picked Room {room_num} door")
                                                            else:
                                                                # Failed
                                                                player.inventory['lockpick'] = lockpick_count - 1
                                                                town_message = f"✗ Lockpick failed!\nRoom {room_num} still locked\nLockpick broken ({lockpick_count - 1} left)"
                                                                town_message_timer = 180
                                                                logger.info(f"[LOCKPICK] Failed to pick Room {room_num} door")
                                                else:
                                                    # Door is unlocked or already opened
                                                    nearby_obj.opened = not nearby_obj.opened
                                                    nearby_obj.solid = not nearby_obj.opened
                                                    state = "Opened" if nearby_obj.opened else "Closed"
                                                    town_message = f"{state} Room {nearby_obj.room_number} door"
                                                    town_message_timer = 90
                                                    logger.info(f"[INN] {state} Room {nearby_obj.room_number} door")
                                            elif nearby_obj.type in ["desk", "shelf", "bed"]:
                                                town_message = f"Interacted with {nearby_obj.name}"
                                                town_message_timer = 120
                                                logger.info(f"[INTERIOR] Interacted with {nearby_obj.name}")
                                            else:
                                                logger.info(f"[INTERIOR] Unknown object type: {nearby_obj.type}")
                                        else:
                                            logger.info("[INTERIOR] No interactable object nearby")
                            else:
                                logger.error("[INTERIOR] No exit door found in interior!")
                        elif in_dungeon:
                            # Exit dungeon
                            if dungeon_entrance_pos:
                                player.x, player.y = dungeon_entrance_pos
                            
                            # CRITICAL FIX: Clear dungeon enemies and loot
                            enemies_list.clear()
                            dropped_equipment_list.clear()
                            
                            in_dungeon = False
                            current_dungeon = None
                            logger.info("Exited dungeon - returned to overworld")
                        elif in_town:
                            # Exit town
                            # Return confiscated weapons when leaving town
                            returned_count = weapon_restriction_system.return_weapons(player)
                            if returned_count > 0:
                                town_message = f"✓ Returned {returned_count} confiscated weapon(s)"
                                town_message_timer = 180
                                logger.info(f"[WEAPON] Returned {returned_count} confiscated weapons to player")
                            
                            # Stop any guard chases when leaving town
                            player.being_chased_by_guards = False
                            for guard in town_guards:
                                if guard.state == "chase" and guard.chase_target == player:
                                    guard.chase_target = None
                                    guard.change_state("patrol" if guard.is_patrolling else "idle")
                            
                            if town_return_pos:
                                player.x, player.y = town_return_pos
                            
                            in_town = False
                            current_town_instance = None
                            logger.info("Exited town - returned to overworld")
                        else:
                            # Check if player is near a dungeon entrance
                            near_entrance = False
                            selected_entrance = None
                            for entrance_x, entrance_y in dungeon_entrances:
                                distance = ((player.x - entrance_x) ** 2 + (player.y - entrance_y) ** 2) ** 0.5
                                if distance < config.TILE_SIZE * 2:  # Within 2 tiles
                                    near_entrance = True
                                    selected_entrance = (entrance_x, entrance_y)
                                    break
                            
                            # Check if player is near a town gate
                            near_gate = False
                            selected_town = None
                            for town_name, (gate_x, gate_y) in town_gates.items():
                                distance = ((player.x - gate_x) ** 2 + (player.y - gate_y) ** 2) ** 0.5
                                if distance < config.TILE_SIZE * 4:  # Within 4 tiles (easier to find)
                                    near_gate = True
                                    selected_town = town_name
                                    logger.info(f"Entering town: {selected_town}")
                                    break
                            
                            if near_entrance and selected_entrance:
                                # CRITICAL FIX: Check if dungeon instance exists and needs reset
                                existing_dungeon = dungeon_instances.get(selected_entrance)
                                
                                if existing_dungeon and hasattr(existing_dungeon, 'check_and_reset'):
                                    existing_dungeon.check_and_reset(game_time.day_count)
                                
                                # Create new dungeon if none exists or it was reset
                                if not existing_dungeon or (hasattr(existing_dungeon, 'cleared') and 
                                    existing_dungeon.last_cleared_day and 
                                    game_time.day_count - existing_dungeon.last_cleared_day >= existing_dungeon.reset_days):
                                    
                                    # Generate fresh dungeon with variety system
                                    layout_choice = random.choice(['cave', 'rooms_and_corridors'])
                                    
                                    # Determine difficulty based on player level
                                    if player.level < 5:
                                        difficulty = "normal"
                                    elif player.level < 10:
                                        difficulty = random.choice(["normal", "hard"])
                                    elif player.level < 15:
                                        difficulty = random.choice(["normal", "hard", "nightmare"])
                                    else:
                                        difficulty = random.choice(["hard", "nightmare", "hell"])
                                    
                                    current_dungeon = create_dungeon(
                                        width=60,
                                        height=40,
                                        theme='cave',
                                        layout_style=layout_choice,
                                        difficulty=difficulty,
                                        modifier=None,  # Random modifier rolled in create_dungeon
                                        player_level=player.level
                                    )
                                    dungeon_instances[selected_entrance] = current_dungeon
                                    logger.info(f"Generated new {layout_choice} dungeon with {difficulty} difficulty")
                                else:
                                    # Use existing dungeon instance
                                    current_dungeon = existing_dungeon
                                    logger.info(f"Entering existing dungeon (cleared: {getattr(current_dungeon, 'cleared', False)})")
                                
                                if current_dungeon:
                                    # Check if dungeon has a boss
                                    has_boss = False
                                    boss_type = None
                                    if hasattr(current_dungeon, 'enemies'):
                                        for enemy in current_dungeon.enemies:
                                            if hasattr(enemy, 'boss_type'):
                                                has_boss = True
                                                boss_type = enemy.boss_type
                                                break
                                    
                                    # If dungeon has a boss, show loot preview first
                                    if has_boss and boss_type:
                                        # Store dungeon entry state for after preview
                                        pending_dungeon_entry['active'] = True
                                        pending_dungeon_entry['dungeon'] = current_dungeon
                                        pending_dungeon_entry['entrance_pos'] = (player.x, player.y)
                                        pending_dungeon_entry['entrance_coords'] = selected_entrance
                                        
                                        # Show boss loot preview
                                        loot_preview_data = enhanced_loot.get_boss_loot_preview(boss_type)
                                        boss_loot_preview.show(boss_type, loot_preview_data)
                                        logger.info(f"[LOOT] Showing boss loot preview for {boss_type}")
                                        continue
                                    
                                    # No boss or preview already shown - enter dungeon immediately
                                    dungeon_entrance_pos = (player.x, player.y)
                                    in_dungeon = True
                                    
                                    # Track dungeon entry for achievements
                                    player.ach_dungeons_entered += 1
                                    achievement_manager.check_all_exploration(
                                        player.ach_towns_visited,
                                        player.ach_distance_traveled,
                                        player.ach_dungeons_entered
                                    )
                                    unlocked = achievement_manager.get_recent_unlock()
                                    if unlocked:
                                        achievement_popup.show(unlocked)
                                        logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                                    
                                    # CRITICAL FIX: Clear overworld enemies and load dungeon enemies
                                    enemies_list.clear()
                                    if hasattr(current_dungeon, 'enemies'):
                                        enemies_list.extend(current_dungeon.enemies)
                                        logger.info(f"Loaded {len(current_dungeon.enemies)} dungeon enemies")
                                    
                                    # CRITICAL FIX: Load dungeon loot
                                    dropped_equipment_list.clear()
                                    if hasattr(current_dungeon, 'loot'):
                                        dropped_equipment_list.extend(current_dungeon.loot)
                                        logger.info(f"Loaded {len(current_dungeon.loot)} dungeon loot items")
                                    
                                    # Move player to dungeon entrance
                                    if current_dungeon.entrance:
                                        player.x = current_dungeon.entrance[0] * config.TILE_SIZE
                                        player.y = current_dungeon.entrance[1] * config.TILE_SIZE
                                        logger.info(f"Entered dungeon at entrance {current_dungeon.entrance}")
                                    elif hasattr(current_dungeon, 'rooms') and current_dungeon.rooms:
                                        start_room = current_dungeon.rooms[0]
                                        player.x = (start_room['x'] + start_room['width'] // 2) * config.TILE_SIZE
                                        player.y = (start_room['y'] + start_room['height'] // 2) * config.TILE_SIZE
                                        logger.info(f"Entered dungeon with {len(current_dungeon.rooms)} rooms")
                                    else:
                                        player.x = 30 * config.TILE_SIZE
                                        player.y = 20 * config.TILE_SIZE
                                        logger.info("Entered dungeon (no entrance marker)")
                            elif near_gate and selected_town:
                                # Get pre-created town instance
                                town_inst = town_instances.get(selected_town)
                                
                                if town_inst:
                                    # Update global town instance
                                    current_town_instance = town_inst
                                    town_return_pos = (player.x, player.y)
                                    
                                    # Check if player is banned from this town
                                    cooldown_info = town_cooldown_system.cooldowns.get(id(player))
                                    if cooldown_info:
                                        # Check for ALL_TOWNS ban (jailbreak) or specific town ban
                                        is_banned = False
                                        days_remaining = 0
                                        
                                        if cooldown_info['town'] == 'ALL_TOWNS':
                                            # Banned from all towns
                                            if game_time.day_count < cooldown_info['end_day']:
                                                is_banned = True
                                                days_remaining = cooldown_info['end_day'] - game_time.day_count
                                        elif cooldown_info['town'] == selected_town:
                                            # Banned from this specific town
                                            if game_time.day_count < cooldown_info['end_day']:
                                                is_banned = True
                                                days_remaining = cooldown_info['end_day'] - game_time.day_count
                                        
                                        if is_banned:
                                            if cooldown_info['town'] == 'ALL_TOWNS':
                                                town_message = f"🚫 You are EXILED from ALL TOWNS!\nJailbreak consequences: {days_remaining} days remaining\nYou are a wanted fugitive everywhere."
                                            else:
                                                town_message = f"🚫 You are BANNED from {selected_town}!\nDays remaining: {days_remaining}\nReturn after your exile."
                                            town_message_timer = 300
                                            logger.warning(f"[COOLDOWN] Player denied entry to {selected_town} - {days_remaining} days remaining")
                                            # Don't enter the town
                                            continue
                                    
                                    # Check for curfew before entering
                                    current_hour, _ = game_time.get_time_hm()
                                    if curfew_system.is_curfew_active(selected_town) and curfew_system.is_curfew_hours(current_hour):
                                        # Show curfew warning dialog
                                        curfew_warning_dialog['active'] = True
                                        curfew_warning_dialog['town_name'] = selected_town
                                        logger.info(f"[CURFEW] Warning shown for {selected_town} (curfew hours: {curfew_system.curfew_start}-{curfew_system.curfew_end})")
                                        continue  # Don't enter yet, wait for player decision
                                    
                                    # Check if player is wanted before entering
                                    player.is_wanted = wanted_system.get_wanted_status(id(player), game_time)
                                    
                                    # Apply town entry fee if lockdown is active
                                    entry_fee = town_entry_fee_system.charge_entry(player, town_treasury_system, current_town_instance.name)
                                    if entry_fee > 0:
                                        town_message = f"💰 Entry Fee Charged: {entry_fee}g (Lockdown Active)"
                                        town_message_timer = 180
                                        logger.info(f"[MAYOR] Charged {entry_fee}g entry fee to player")
                                    
                                    if player.is_wanted:
                                        town_message = "⚠ You are WANTED! Guards will pursue you on sight!"
                                        town_message_timer = 240
                                        logger.warning(f"[WANTED] Player entered {selected_town} while wanted (bounty: {player.wanted_level}g)")
                                    
                                    in_town = True
                                    
                                    # Clear enemies when entering town (towns are safe zones)
                                    enemies_list.clear()
                                    logger.info("Cleared enemies when entering town")
                                    
                                    # Enforce weapon restrictions if active (mayor powers)
                                    if weapon_restriction_system.restriction_active:
                                        confiscated_weapons = weapon_restriction_system.enforce(player, selected_town)
                                        if confiscated_weapons:
                                            player.weapons_stored = confiscated_weapons
                                            town_message = f"⚔️ WEAPON RESTRICTION!\n{len(confiscated_weapons)} weapon(s) confiscated\nStored in Town Hall guard locker\n(Can be retrieved when you leave...\nor stolen from the mayor's office)"
                                            town_message_timer = 300
                                            logger.info(f"[MAYOR] Confiscated {len(confiscated_weapons)} weapons from player")
                                    
                                    # Move player to town gate (spawn point)
                                    player.x = current_town_instance.gate_x
                                    player.y = current_town_instance.gate_y
                                    logger.info(f"Entered town: {selected_town}")
                                else:
                                    logger.error(f"Town instance not found for {selected_town}")
                            else:
                                if not near_entrance and not near_gate:
                                    logger.warning("No dungeon entrance or town gate nearby.")
                    # Full-screen map (Tab key)
                    elif event.key == pygame.K_TAB:
                        fullscreen_map.toggle()
                        logger.info(f"[MAP] Full-screen map {'opened' if fullscreen_map.active else 'closed'}")
                    # Mayor Powers menu (M key when player is mayor)
                    elif event.key == pygame.K_m and hasattr(player, 'is_mayor') and player.is_mayor:
                        # Player is mayor - open mayor powers menu
                        if current_town_instance:
                            mayor_powers_ui.open(current_town_instance.name)
                            logger.info(f"[MAYOR UI] Opened mayor powers for {current_town_instance.name}")
                        else:
                            town_message = "⚠️ Must be in a town to access mayor powers"
                            town_message_timer = 180
                    # Minimap controls
                    elif event.key == pygame.K_m:
                        minimap.toggle()
                        logger.info(f"[MINIMAP] {'Enabled' if minimap.enabled else 'Disabled'}")
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        # Zoom controls work for both minimap and full-screen map
                        if fullscreen_map.active:
                            fullscreen_map.zoom_in()
                            logger.debug(f"[MAP] Zoom: {fullscreen_map.zoom_level:.2f}x")
                        else:
                            minimap.zoom_in()
                            logger.debug(f"[MINIMAP] Zoom: {minimap.zoom_level:.1f}x")
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                        if fullscreen_map.active:
                            fullscreen_map.zoom_out()
                            logger.debug(f"[MAP] Zoom: {fullscreen_map.zoom_level:.2f}x")
                        else:
                            minimap.zoom_out()
                            logger.debug(f"[MINIMAP] Zoom: {minimap.zoom_level:.1f}x")
                    elif event.key == pygame.K_0:
                        if fullscreen_map.active:
                            fullscreen_map.reset_zoom()
                            logger.debug(f"[MAP] Zoom reset to {fullscreen_map.zoom_level:.2f}x")
                        else:
                            minimap.reset_zoom()
                            logger.debug(f"[MINIMAP] Zoom reset to {minimap.zoom_level:.1f}x")
                    # Quest system controls
                    elif event.key == pygame.K_l:
                        quest_log_ui.toggle()
                        logger.debug(f"[QUEST] Quest log {'opened' if quest_log_ui.active else 'closed'}")
                        if quest_log_ui.active and tutorial_manager.should_show_tutorial('quests'):
                            tutorial_popup.show('quests', QUESTS_TUTORIAL)
                    elif event.key == pygame.K_q:
                        quest_tracker_ui.toggle()
                        logger.debug(f"[QUEST] Quest tracker {'enabled' if quest_tracker_ui.enabled else 'disabled'}")
                    # Companion hiring at inns (H key) - CHECK THIS FIRST before dialogue history
                    elif event.key == pygame.K_h and in_building_interior and current_interior and current_interior_building:
                        # Check if this is an inn
                        if hasattr(current_interior_building, 'type') and current_interior_building.type == BuildingType.INN:
                            # Check for nearby innkeeper
                            nearby_npc = current_interior.get_nearby_npc(player.x, player.y, max_distance=60)
                            if nearby_npc and nearby_npc.get('role') == 'innkeeper':
                                companion_hiring_ui.open(current_interior_building)
                                logger.info("[COMPANION] Opened companion hiring UI at inn")
                            else:
                                town_message = "You must be near the innkeeper to hire companions."
                                town_message_timer = 120
                        else:
                            # Not in inn, fallback to dialogue history
                            dialogue_history_ui.toggle()
                            logger.debug(f"[DIALOGUE] History {'opened' if dialogue_history_ui.active else 'closed'}")
                    # Dialogue history (H key when NOT in inn)
                    elif event.key == pygame.K_h:
                        dialogue_history_ui.toggle()
                        logger.debug(f"[DIALOGUE] History {'opened' if dialogue_history_ui.active else 'closed'}")
                    # Hotbar lock toggle (B key for "Bar lock")
                    elif event.key == pygame.K_b:
                        hotbar_system.toggle_lock()
                        lock_state = "LOCKED" if hotbar_system.locked else "UNLOCKED"
                        town_message = f"🔒 Hotbar {lock_state}"
                        town_message_timer = 90
                        logger.info(f"[HOTBAR] Hotbar {lock_state}")
                    # Fullscreen toggle (ESC key when not in menus)
                    elif event.key == pygame.K_ESCAPE:
                        # Only toggle fullscreen if we're not in any menu/UI
                        in_any_menu = (show_inventory or show_equipment or show_stats_menu or 
                                     show_pause_menu or show_settings_menu or show_achievements or 
                                     show_performance_menu or show_accessibility_menu or show_ai_settings or
                                     showing_campaign_menu or show_crime_history or
                                     fullscreen_map.active or quest_log_ui.active or 
                                     dialogue_history_ui.active or smart_inventory_ui.active or
                                     trade_route_ui.active or npc_skill_switching_ui.active or
                                     mayor_powers_ui.active or repair_menu_ui.active or
                                     curfew_warning_dialog['active'] or fast_travel_menu['active'] or
                                     inn_offer_dialog['active'] or stick_stack_confirmation['active'])
                        
                        if not in_any_menu:
                            is_fullscreen, screen = toggle_fullscreen(is_fullscreen, screen, config)
                            mode_text = "FULLSCREEN" if is_fullscreen else "WINDOWED"
                            town_message = f"🖥️ Display mode: {mode_text}"
                            town_message_timer = 120
                    # Trade routes system (R key)
                    elif event.key == pygame.K_r:
                        trade_route_ui.toggle()
                        logger.debug(f"[TRADE UI] Trade route UI {'opened' if trade_route_ui.active else 'closed'}")
                    # Campaign promises (P key) - MUST CHECK FIRST to not conflict with NPC skill switching
                    elif event.key == pygame.K_p and not player.in_jail and election_timeline.state == "campaign":
                        # Toggle campaign menu
                        showing_campaign_menu = not showing_campaign_menu
                        
                        if showing_campaign_menu:
                            # Initialize menu with all available promises
                            campaign_menu_state['all_promises'] = CampaignPromise.PROMISES.copy()
                            campaign_menu_state['selected_idx'] = 0
                            # Keep existing selections if returning to menu
                            if 'selected_promises' not in campaign_menu_state:
                                campaign_menu_state['selected_promises'] = []
                            
                            logger.info(f"[CAMPAIGN] Opened campaign promise menu ({len(campaign_menu_state['selected_promises'])}/3 selected)")
                        else:
                            logger.info(f"[CAMPAIGN] Closed campaign promise menu")
                    # Show feedback if P pressed during non-campaign period
                    elif event.key == pygame.K_p and not player.in_jail and election_timeline.state in ["anarchy", "voting", "results"]:
                        if election_timeline.state == "anarchy":
                            days_left = 7 - election_timeline.days_in_anarchy
                            town_message = f"Campaign period hasn't started yet.\n(Starts in {days_left} days)"
                        elif election_timeline.state == "voting":
                            town_message = "Campaign period is over.\n(Voting has begun)"
                        else:
                            town_message = "No election campaign active.\n(Only available during campaign period)"
                        town_message_timer = 240
                    # NPC skill switching system (P key for Professions) - only when NOT in campaign related states
                    elif event.key == pygame.K_p:
                        npc_skill_switching_ui.toggle()
                        logger.debug(f"[SKILL SWITCH UI] Skill switching UI {'opened' if npc_skill_switching_ui.active else 'closed'}")
                    # NPC interaction (T key to talk to nearby NPC)
                    elif event.key == pygame.K_t:
                        # First check for tutorial NPC (Wandering Guide)
                        tutorial_npc_found = False
                        if hasattr(player, 'tutorial_npc') and player.tutorial_npc:
                            tutorial_npc = player.tutorial_npc
                            # Check if player is near the tutorial NPC (works both in overworld and in buildings)
                            can_interact = False
                            if hasattr(tutorial_npc, 'in_building') and tutorial_npc.in_building:
                                # NPC is in a building - check if player is in same building
                                if in_building_interior and current_interior_building_id == tutorial_npc.in_building:
                                    distance = ((player.x - tutorial_npc.x) ** 2 + (player.y - tutorial_npc.y) ** 2) ** 0.5
                                    if distance < 80:
                                        can_interact = True
                            else:
                                # NPC is in overworld - use existing proximity check
                                if not in_building_interior and tutorial_npc.is_player_nearby(player):
                                    can_interact = True
                            
                            if can_interact:
                                tutorial_npc_found = True
                                # Set dialogue tree ID
                                tutorial_npc.dialogue_tree_id = 'tutorial_guide'
                                
                                # Start conversation - dynamic entry point will handle state
                                dialogue_manager.start_conversation(tutorial_npc, player)
                                dialogue_ui.start_dialogue(dialogue_manager)
                                logger.info(f"[TUTORIAL] Opened dialogue with tutorial NPC")
                                
                                # If player declined before and is talking again, trigger shelter walk
                                if tutorial_npc.declined_by_player and not tutorial_npc.going_to_shelter and not tutorial_npc.at_shelter:
                                    tutorial_npc.going_to_shelter = True
                                    
                                    # Find nearest town and set shack location if not already set
                                    if not tutorial_npc.shack_x:
                                        nearest_town = None
                                        min_distance = float('inf')
                                        for town in town_manager.towns:
                                            dist = math.sqrt((town.center_x - tutorial_npc.x)**2 + (town.center_y - tutorial_npc.y)**2)
                                            if dist < min_distance:
                                                min_distance = dist
                                                nearest_town = town
                                        
                                        if nearest_town:
                                            # Place shack just outside the town (100 pixels away from town center)
                                            tutorial_npc.shack_x = nearest_town.center_x + 150
                                            tutorial_npc.shack_y = nearest_town.center_y - 150
                                            
                                            # Create the shack building
                                            tutorial_shack = Building(BuildingType.SHACK, 
                                                                    tutorial_npc.shack_x - 30,  # Center shack on coordinates
                                                                    tutorial_npc.shack_y - 40, 
                                                                    60, 80, name="Wandering Guide's Shack")
                                            tutorial_shack.is_enterable = True
                                            
                                            # Create the shack interior
                                            shack_interior = BuildingInterior(
                                                BuildingType.SHACK,
                                                town_name="None",  # Shack is standalone
                                                town_treasury_system=town_treasury_system,
                                                bank_manager=bank_manager,
                                                weapon_restriction_system=weapon_restriction_system
                                            )
                                            building_interiors["TUTORIAL_SHACK"] = shack_interior
                                            
                                            logger.info(f"[TUTORIAL] Shack created near {nearest_town.name} at ({tutorial_shack.x}, {tutorial_shack.y})")
                                else:
                                    # Normal first-time dialogue
                                    dialogue_manager.start_conversation(tutorial_npc, player)
                                    dialogue_ui.start_dialogue(dialogue_manager)
                                    logger.info(f"[TUTORIAL] Opened dialogue box with tutorial NPC")



                        
                        # If no tutorial NPC, check for gatherer NPCs (new system)
                        if not tutorial_npc_found:
                            nearby_gatherer = gatherer_npc_manager.get_nearby_npc(player.x, player.y, max_distance=80)
                            
                            if nearby_gatherer:
                                # Use gatherer dialogue system
                                try:
                                    gatherer_dialogue_tree = create_gatherer_dialogue(nearby_gatherer)
                                    # Start dialogue with gatherer NPC
                                    dialogue_manager.start_dialogue(gatherer_dialogue_tree, nearby_gatherer)
                                    dialogue_ui.start_dialogue(dialogue_manager)
                                    logger.info(f"[DIALOGUE] Started conversation with gatherer NPC: {nearby_gatherer.name}")
                                except Exception as e:
                                    logger.error(f"[DIALOGUE] Error creating gatherer dialogue: {e}")
                            else:
                                # Check for regular NPCs
                                nearby_npc = npc_manager.get_interactable_npc(player.x, player.y)
                                
                                if nearby_npc:
                                    # SPECIAL: Check for mayor tracking quest with guards
                                    is_guard = 'guard' in nearby_npc.name.lower()
                                    tracking_info = mayor_absconding_system.get_tracking_info()
                                    
                                    if is_guard and tracking_info['available']:
                                        # Show tracking quest notification
                                        town_message = (
                                            f"🚨 URGENT BOUNTY AVAILABLE!\n"
                                            f"📜 Target: Mayor of {tracking_info['town']}\n"
                                            f"💰 Stolen: {tracking_info['stolen']}g\n"
                                            f"🎯 Reward: {tracking_info['reward']}g (30%)\n\n"
                                            f"Press Y to track the mayor and claim your reward!"
                                        )
                                        town_message_timer = 480  # 8 seconds
                                        logger.info(f"[MAYOR QUEST] Showing tracking quest to player - Town: {tracking_info['town']}, Reward: {tracking_info['reward']}g")
                                    else:
                                        # Normal dialogue flow
                                        if hasattr(nearby_npc, 'dialogue_id'):
                                            dialogue_id = nearby_npc.dialogue_id
                                        else:
                                            # Default dialogue IDs based on NPC type
                                            if 'merchant' in nearby_npc.name.lower():
                                                dialogue_id = 'merchant'
                                            elif 'elder' in nearby_npc.name.lower():
                                                dialogue_id = 'town_elder'
                                            else:
                                                dialogue_id = 'quest_giver_1'
                                        
                                        # Set dialogue tree ID on NPC
                                        nearby_npc.dialogue_tree_id = dialogue_id
                                        dialogue_manager.start_conversation(nearby_npc, player)
                                        dialogue_ui.start_dialogue(dialogue_manager)
                                        logger.info(f"[DIALOGUE] Started conversation with {nearby_npc.name}")
                                else:
                                    logger.warning("[DIALOGUE] No one nearby to talk to")
                    # Buy newspaper at inn (B key)
                    elif event.key == pygame.K_b:
                        # Check if player is in building interior (inn) near innkeeper
                        if in_building_interior and current_interior and current_interior_building:
                            if hasattr(current_interior_building, 'type') and current_interior_building.type == BuildingType.INN:
                                nearby_npc = current_interior.get_nearby_npc(player.x, player.y, max_distance=60)
                                if nearby_npc and nearby_npc.get('role') == 'innkeeper':
                                    # Purchase newspaper
                                    success, message = newspaper_distribution.purchase_newspaper(player)
                                    town_message = message
                                    town_message_timer = 180
                                    logger.info(f"[NEWSPAPER] Purchase attempt: {message}")
                                else:
                                    town_message = "You must be near the innkeeper to buy a newspaper."
                                    town_message_timer = 120
                            else:
                                town_message = "Newspapers are sold at inns."
                                town_message_timer = 120
                        else:
                            town_message = "Newspapers are sold at inns."
                            town_message_timer = 120
                    # Open newspaper (N key)
                    elif event.key == pygame.K_n:
                        # Check if player has a newspaper
                        if current_newspaper:
                            newspaper_ui.open(current_newspaper)
                            logger.info("[NEWSPAPER] Opened newspaper UI")
                        else:
                            town_message = "No newspaper available. Purchase at inns (10g)."
                            town_message_timer = 120
                    # Open commodity exchange (M key)
                    elif event.key == pygame.K_m:
                        commodity_exchange_ui.toggle()
                        logger.info(f"[EXCHANGE] Commodity exchange {'opened' if commodity_exchange_ui.active else 'closed'}")
                    # Open economics skill tree (Ctrl+E key, not in building interiors)
                    elif event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL and not in_building_interior:
                        economics_skill_tree_ui.toggle()
                        logger.info(f"[ECONOMICS] Skill tree {'opened' if economics_skill_tree_ui.active else 'closed'}")
                    # Save/Load with Ctrl modifiers
                    elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Open save dialog
                        save_integrator.open_save_dialog()
                    elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Open load dialog
                        save_integrator.open_load_dialog()
                    # Accept mayor tracking quest (Y key)
                    elif event.key == pygame.K_y:
                        # Check if there's an active tracking quest
                        tracking_info = mayor_absconding_system.get_tracking_info()
                        if tracking_info['available']:
                            # Player accepts and completes the tracking quest
                            reward = mayor_absconding_system.track_mayor(player)
                            if reward > 0:
                                town_message = (
                                    f"✅ MAYOR TRACKED DOWN!\n"
                                    f"🎯 You successfully apprehended\n"
                                    f"the mayor of {tracking_info['town']}!\n"
                                    f"💰 Reward Claimed: {reward}g"
                                )
                                town_message_timer = 360  # 6 seconds
                                logger.info(f"[MAYOR QUEST] Player completed tracking quest - Earned {reward}g reward")
                            else:
                                town_message = "Quest already completed!"
                                town_message_timer = 120
                        else:
                            # No active quest - ignore Y key
                            pass
                    # Bribe voter (V key) - only during elections
                    elif event.key == pygame.K_v:
                        # Check if elections are active (campaign or voting period)
                        is_election_active = election_timeline.state in ["campaign", "voting"]
                        
                        if not is_election_active:
                            # No election happening - inform player
                            town_message = "No election is currently active.\n(Bribery only works during campaign/voting periods)"
                            town_message_timer = 180
                        else:
                            # Election is active - check for nearby NPC
                            nearby_npc = npc_manager.get_interactable_npc(player.x, player.y)
                            
                            if not nearby_npc:
                                # Also check gatherer NPCs
                                nearby_npc = gatherer_npc_manager.get_nearby_npc(player.x, player.y, max_distance=80)
                            
                            if nearby_npc:
                                npc_id = id(nearby_npc)
                                
                                # Check if already bribed
                                if voter_bribery_system.is_bribed(npc_id):
                                    town_message = f"❌ ALREADY BRIBED\n{nearby_npc.name} has already been bribed!\n(Cannot bribe the same NPC twice)"
                                    town_message_timer = 240
                                    logger.info(f"[BRIBERY] Player tried to re-bribe {nearby_npc.name}")
                                else:
                                    # Check if player can afford bribe
                                    bribe_cost = voter_bribery_system.bribe_amount
                                    
                                    if player.dubloons >= bribe_cost:
                                        # Offer bribe
                                        town_message = (
                                            f"🗳️ BRIBE VOTER\n"
                                            f"Target: {nearby_npc.name}\n"
                                            f"Cost: {bribe_cost}g\n\n"
                                            f"⚠️ Corrupt the vote in your favor?\n"
                                            f"Press B to confirm bribe"
                                        )
                                        town_message_timer = 420  # 7 seconds
                                        # Store pending bribe info
                                        player.pending_bribe_npc_id = npc_id
                                        player.pending_bribe_npc_name = nearby_npc.name
                                        logger.info(f"[BRIBERY] Offering to bribe {nearby_npc.name} for {bribe_cost}g")
                                    else:
                                        needed = bribe_cost - player.dubloons
                                        town_message = f"❌ INSUFFICIENT FUNDS\nNeed {needed}g more to bribe voters\n(Bribery costs {bribe_cost}g)"
                                        town_message_timer = 240
                            else:
                                town_message = "No one nearby to bribe.\n(Get close to an NPC and press V)"
                                town_message_timer = 180
                    
                    # Confirm bribe (B key) - requires pending bribe
                    elif event.key == pygame.K_b and not player.in_jail:
                        # Check if player has a pending bribe offer
                        if hasattr(player, 'pending_bribe_npc_id') and player.pending_bribe_npc_id:
                            npc_id = player.pending_bribe_npc_id
                            npc_name = getattr(player, 'pending_bribe_npc_name', 'NPC')
                            
                            # Process the bribe
                            success, new_gold = voter_bribery_system.bribe(
                                npc_id, 
                                player.dubloons, 
                                town_treasury_system, 
                                current_town_instance.name if current_town_instance else None
                            )
                            
                            if success:
                                player.dubloons = new_gold
                                town_message = (
                                    f"✅ BRIBE SUCCESSFUL!\n"
                                    f"{npc_name} has been bribed!\n"
                                    f"💰 Paid {voter_bribery_system.bribe_amount}g\n"
                                    f"(Their vote is now guaranteed)"
                                )
                                town_message_timer = 360  # 6 seconds
                                logger.info(f"[BRIBERY] Player successfully bribed {npc_name} for {voter_bribery_system.bribe_amount}g")
                            else:
                                town_message = "Bribe failed! (Insufficient funds)"
                                town_message_timer = 180
                            
                            # Clear pending bribe
                            player.pending_bribe_npc_id = None
                            player.pending_bribe_npc_name = None
                        else:
                            # No pending bribe - check if attempting break-in
                            if hasattr(player, 'near_closed_building') and player.near_closed_building:
                                # Player is near a closed building - attempt break-in
                                building = player.near_closed_building
                                lockpick_count = player.inventory.get('lockpick', 0)
                                
                                if lockpick_count <= 0:
                                    town_message = "⚠ NO LOCKPICKS!\nYou need lockpicks to break in"
                                    town_message_timer = 180
                                    logger.info("[BREAK-IN] No lockpicks available")
                                else:
                                    # Attempt the break-in!
                                    logger.info(f"[BREAK-IN] Attempting to break into {building.name} ({building.type})")
                                    
                                    # Check for witnesses (guards and NPCs)
                                    witnessed, witness_name, witness_type = break_in_system.check_for_witnesses(
                                        player.x, player.y, npc_manager, town_guards, 
                                        current_town_instance.name if current_town_instance else None,
                                        game_time
                                    )
                                    
                                    if witnessed:
                                        # CAUGHT RED-HANDED!
                                        penalty_info = break_in_system.get_penalty_info(building.type)
                                        bounty_amount = penalty_info['bounty']
                                        jail_days = penalty_info['jail_days']
                                        rep_loss = penalty_info['rep_loss']
                                        
                                        # Apply penalties
                                        player.wanted_level += bounty_amount
                                        wanted_system.set_wanted(id(player), 'burglary', game_time)
                                        player.is_wanted = True
                                        
                                        if current_town_instance:
                                            reputation_system.modify_faction_reputation(current_town_instance.name, rep_loss)
                                            town_cooldown_system.set_cooldown(id(player), current_town_instance.name, game_time)
                                            
                                            # Record crime with criminal rank system
                                            record_crime_with_rank(
                                                crime_type='burglary',
                                                location=f"{current_town_instance.name} - {building.name}",
                                                witnessed=True,
                                                witness=witness_name
                                            )
                                        
                                        detection_time = game_time.get_time_str()
                                        witness_label = "GUARD" if witness_type == 'guard' else "NPC"
                                        
                                        town_message = (
                                            f"🚨 CAUGHT BY {witness_label}!\n"
                                            f"{witness_name} saw you!\n"
                                            f"⚔ Flee or face arrest!\n"
                                            f"Bounty: +{bounty_amount}g\n"
                                            f"Rep: {rep_loss}"
                                        )
                                        town_message_timer = 360
                                        logger.warning(f"[BREAK-IN] Caught by {witness_name} ({witness_type}) at {detection_time}")
                                    else:
                                        # Not witnessed - attempt lockpick
                                        difficulty = break_in_system.get_lockpick_difficulty(building.type)
                                        success_chance = max(10, min(90, 70 - difficulty))
                                        roll = random.randint(1, 100)
                                        lockpick_success = roll <= success_chance
                                        
                                        # Use a lockpick
                                        player.inventory['lockpick'] = lockpick_count - 1
                                        
                                        # Check if alarm triggered
                                        alarm_triggered = break_in_system.check_alarm_triggered(building.type, lockpick_success)
                                        
                                        if alarm_triggered:
                                            # ALARM! Lock failed or alarm engaged
                                            break_in_system.trigger_alarm(id(building), game_time)
                                            penalty_info = break_in_system.get_penalty_info(building.type)
                                            bounty_amount = penalty_info['bounty'] // 2  # Lesser penalty for alarm
                                            
                                            player.wanted_level += bounty_amount
                                            wanted_system.set_wanted(id(player), 'burglary', game_time)
                                            player.is_wanted = True
                                            
                                            town_message = (
                                                f"🔔 ALARM TRIGGERED!\n"
                                                f"Guards alerted!\n"
                                                f"Bounty: +{bounty_amount}g\n"
                                                f"Lockpick broken ({lockpick_count - 1} left)"
                                            )
                                            town_message_timer = 300
                                            logger.warning(f"[BREAK-IN] Alarm triggered at {building.name}")
                                        elif lockpick_success:
                                            # SUCCESS! Generate loot
                                            gold_loot, stolen_items, total_value = break_in_system.generate_loot(
                                                building.type, building.name, player.inventory
                                            )
                                            
                                            # Add gold
                                            player.dubloons += gold_loot
                                            
                                            # Add stolen items to player's stolen items list
                                            player.stolen_items.extend(stolen_items)
                                            
                                            # Mark building as hit
                                            break_in_system.mark_building_hit(id(building), game_time)
                                            
                                            # Crime record (unwitnessed)
                                            if current_town_instance:
                                                # Record crime with criminal rank system
                                                record_crime_with_rank(
                                                    crime_type='burglary',
                                                    location=f"{current_town_instance.name} - {building.name}",
                                                    witnessed=False
                                                )
                                                
                                                # Auto-discover fence after successful burglary
                                                fence_manager.discover_fence(current_town_instance.name)
                                                logger.info(f"[FENCE] Fence discovered in {current_town_instance.name}")
                                            
                                            item_summary = f"{len(stolen_items)} items" if stolen_items else "cash only"
                                            fence_hint = "\n\n💰 Rumor: A fence visits the tavern at night..." if current_town_instance else ""
                                            town_message = (
                                                f"✅ BREAK-IN SUCCESSFUL!\n"
                                                f"💰 Looted {gold_loot}g\n"
                                                f"📦 {item_summary}\n"
                                                f"Total value: ~{total_value}g\n"
                                                f"Lockpick broken ({lockpick_count - 1} left){fence_hint}"
                                            )
                                            town_message_timer = 360
                                            logger.info(f"[BREAK-IN] Successful burglary at {building.name}, looted {total_value}g worth")
                                        else:
                                            # Failed lockpick (no alarm)
                                            town_message = (
                                                f"✗ LOCKPICK FAILED!\n"
                                                f"The lock was too difficult\n"
                                                f"Difficulty: {difficulty}\n"
                                                f"Success rate: {success_chance}%\n"
                                                f"Lockpick broken ({lockpick_count - 1} left)"
                                            )
                                            town_message_timer = 300
                                            logger.info(f"[BREAK-IN] Failed lockpick at {building.name}")
                            else:
                                # No pending action - ignore B key
                                pass
                    
                    # DEBUG: Test status effects with number keys
                    elif key_bindings.is_action("debug_burn", event.key):
                        # Test burn effect
                        player.status_manager.add_status("burn", potency=1.0)
                        logger.info("Applied BURN status effect")
                    elif key_bindings.is_action("debug_freeze", event.key):
                        # Test freeze effect
                        player.status_manager.add_status("freeze", potency=1.0)
                        logger.info("Applied FREEZE status effect")
                    elif key_bindings.is_action("debug_poison", event.key):
                        # Test poison effect
                        player.status_manager.add_status("poison", potency=1.0)
                        logger.info("Applied POISON status effect")
                    elif key_bindings.is_action("debug_blessed", event.key):
                        # Test blessed buff
                        player.status_manager.add_status("blessed", potency=1.0)
                        logger.info("Applied BLESSED status effect")
                    elif key_bindings.is_action("debug_haste", event.key):
                        # Test haste buff
                        player.status_manager.add_status("haste", potency=1.0)
                        logger.info("Applied HASTE status effect")
                    elif key_bindings.is_action("debug_regen", event.key):
                        # Test regeneration
                        player.status_manager.add_status("regeneration", potency=1.0)
                        logger.info("Applied REGENERATION status effect")
                    elif key_bindings.is_action("debug_clear", event.key):
                        # Clear all status effects
                        player.status_manager.active_effects.clear()
                        logger.info("Cleared all status effects")
                    elif event.key == pygame.K_z:
                        # Toggle stealth mode
                        player.in_stealth_mode = not player.in_stealth_mode
                        mode_text = "ENABLED" if player.in_stealth_mode else "DISABLED"
                        logger.info(f"[STEALTH] Stealth mode {mode_text}")
                        town_message = f"Stealth Mode: {mode_text}"
                        town_message_timer = 120
                    
                    elif event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # Sell stolen goods to fence (Shift+F)
                        if in_town and current_town_instance:
                            fence = fence_manager.get_nearby_fence(
                                player.x, player.y, 
                                current_town_instance.name, 
                                game_time,
                                max_distance=120
                            )
                            
                            if fence:
                                # Player is near fence - sell all stolen goods
                                if not player.stolen_items:
                                    town_message = f"💰 {fence.name}: \"You got nothin' for me?\"\nNo stolen goods to sell!"
                                    town_message_timer = 180
                                    logger.info("[FENCE] No stolen goods to sell")
                                else:
                                    total_earned = 0
                                    items_sold = 0
                                    
                                    # Sell all stolen items
                                    for stolen_item in list(player.stolen_items):
                                        gold_paid, success = fence.buy_stolen_item(stolen_item, player)
                                        if success:
                                            total_earned += gold_paid
                                            items_sold += 1
                                    
                                    # Add gold to player
                                    player.dubloons += total_earned
                                    
                                    buy_rate = int(fence.get_buy_rate() * 100)
                                    town_message = (
                                        f"💰 {fence.name}: \"Pleasure doin' business...\"\n"
                                        f"Sold {items_sold} stolen items\n"
                                        f"Earned: {total_earned}g ({buy_rate}% of value)\n"
                                        f"Fence Rep: {fence.reputation}"
                                    )
                                    town_message_timer = 300
                                    logger.info(f"[FENCE] Sold {items_sold} items to {fence.name} for {total_earned}g")
                            else:
                                # Check if fence discovered but not nearby
                                town_fence = fence_manager.get_fence(current_town_instance.name)
                                if town_fence and town_fence.discovered:
                                    if town_fence.is_active(game_time):
                                        town_message = f"💰 The fence is around somewhere...\n(Get closer to the tavern at night)"
                                    else:
                                        hour, _ = game_time.get_time_hm()
                                        town_message = f"💰 The fence only appears late at night\n(10 PM - 4 AM, currently {hour}:00)"
                                    town_message_timer = 180
                                else:
                                    town_message = "No fence available\n(Complete a burglary to discover the fence)"
                                    town_message_timer = 180
                        else:
                            town_message = "No fence here\n(Fences operate in towns only)"
                            town_message_timer = 120
                    
                    elif event.key == pygame.K_n:
                        # Attempt assassination (requires perk and proper positioning)
                        if in_town and current_town_instance:
                            # Find nearest guard
                            nearest_guard = None
                            nearest_distance = 50  # Melee range
                            
                            for guard in town_guards:
                                if hasattr(guard, 'current_town') and guard.current_town == current_town_instance.name:
                                    dx = guard.x - player.x
                                    dy = guard.y - player.y
                                    distance = (dx * dx + dy * dy) ** 0.5
                                    
                                    if distance < nearest_distance:
                                        nearest_distance = distance
                                        nearest_guard = guard
                            
                            if nearest_guard:
                                # Check if can assassinate
                                can_assassinate, reason = stealth_system.can_assassinate(player, nearest_guard)
                                
                                if can_assassinate:
                                    # Perform assassination
                                    success = stealth_system.perform_assassination(nearest_guard)
                                    if success:
                                        logger.warning(f"[ASSASSINATION] Player assassinated {nearest_guard.name}!")
                                        town_message = f"🗡️ Assassinated {nearest_guard.name}!"
                                        town_message_timer = 180
                                        
                                        # Add murder crime with criminal rank system
                                        record_crime_with_rank(
                                            crime_type='murder',
                                            location=f"{player.current_town} - Streets",
                                            witnessed=False  # Assassinations are stealthy
                                        )
                                        
                                        # Remove guard from town
                                        if nearest_guard in town_guards:
                                            town_guards.remove(nearest_guard)
                                        npc_manager.remove_npc(nearest_guard.name)
                                        stealth_system.remove_vision_cone(nearest_guard.name)
                                else:
                                    logger.info(f"[ASSASSINATION] Cannot assassinate: {reason}")
                                    town_message = f"Cannot assassinate: {reason}"
                                    town_message_timer = 120
                            else:
                                logger.info("[ASSASSINATION] No target in range")
                                town_message = "No target in range for assassination"
                                town_message_timer = 120
                    # Accessibility UI handling
                    elif not accessibility_ui.handle_input(event):
                        # Only handle player events if accessibility UI didn't consume it
                        player.handle_event(event)

        if inventory_action_msg:
            inventory_inspect_timer -= 1
            if inventory_inspect_timer <= 0:
                inventory_action_msg = ""
                inventory_inspect_item = None

        # Render logic
        if show_crafting_menu:
            # Render game world behind crafting menu
            graphics.render(world, player, entities, npc_manager=npc_manager)
            # Draw crafting UI on top
            font = get_font(None, 24)
            crafting_ui.draw(screen, font, player)
            pygame.display.flip()
            dt = clock.tick(config.FPS) / 1000.0
            current_fps = clock.get_fps()
            update_performance_monitoring(dt, current_fps)
            continue
        elif show_repair_menu:
            # Render game world behind repair menu
            graphics.render(world, player, entities, npc_manager=npc_manager)
            # Draw repair UI on top
            font = get_font(None, 24)
            repair_menu_ui.update(dt)
            repair_menu_ui.draw(screen, font)
            pygame.display.flip()
            dt = clock.tick(config.FPS) / 1000.0
            current_fps = clock.get_fps()
            update_performance_monitoring(dt, current_fps)
            continue
        elif show_stats_menu:
            # Render game world behind stats menu
            graphics.render(world, player, entities, npc_manager=npc_manager)
            # Draw stats menu on top
            font = get_font(None, 28)
            draw_stats_menu(screen, font, player, reputation_system)
            # Draw action message if any
            if inventory_action_msg and inventory_inspect_timer > 0:
                msg_surf = font.render(inventory_action_msg, True, (255, 255, 100))
                screen.blit(msg_surf, (config.SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, config.SCREEN_HEIGHT - 100))
        elif show_character_sheet:
            # Render game world behind character sheet
            graphics.render(world, player, entities, npc_manager=npc_manager)
            # Draw character sheet on top with mouse position for tooltips
            font = get_font(None, 28)
            mouse_pos = pygame.mouse.get_pos()
            draw_character_sheet(screen, font, player, mouse_pos)
        elif show_crime_history:
            # Render game world behind crime history viewer
            graphics.render(world, player, entities, npc_manager=npc_manager)
            # Draw crime history on top
            font = get_font(None, 24)
            draw_crime_history(screen, font, player, game_time)
            pygame.display.flip()
            dt = clock.tick(config.FPS) / 1000.0
            current_fps = clock.get_fps()
            update_performance_monitoring(dt, current_fps)
            continue
        elif show_pause_menu:
            graphics.render(world, player, entities, npc_manager=npc_manager)
            if show_achievements:
                # Draw achievements UI
                achievement_ui.draw(screen, achievement_manager)
            elif show_bestiary:
                # Draw bestiary UI
                from equipment import EQUIPMENT_DATA
                bestiary_font = get_font(None, 20)
                bestiary.draw(screen, EQUIPMENT_DATA, bestiary_font, bestiary_selected_enemy, bestiary_scroll_offset)
            elif show_ai_settings:
                # Get font for AI settings UI
                font = get_font(None, 24)
                ai_settings_ui.draw(screen, font)
            elif show_accessibility_menu:
                # Get font for accessibility UI
                font = get_font(None, 24)
                accessibility_ui.render(screen, font)
            elif show_font_settings:
                # Get font for font settings UI
                font = get_font(None, 24)
                font_settings_ui.render(screen, font)
            elif show_performance_menu:
                # Get font for performance UI
                font = get_font(None, 28)
                perf_ui.render(screen, font)
            elif show_settings_menu:
                settings_menu_rects = graphics.draw_settings_menu(settings_options, settings_state, settings_idx, config, mouse_pos=settings_menu_mouse_pos)
            elif show_keybindings_menu:
                # Draw key bindings UI
                font = get_font(None, 24)
                keybindings_ui.draw(screen, font)
            else:
                pause_menu_rects = graphics.draw_pause_menu(pause_menu_options, pause_menu_idx, config, player_died=player_died, mouse_pos=pause_menu_mouse_pos)
            
            # Render save/load UI on top of pause menu (must be before display.flip())
            save_integrator.draw(screen)
            
            pygame.display.flip()
            # Calculate delta time and FPS for performance monitoring
            dt = clock.tick(config.FPS) / 1000.0
            current_fps = clock.get_fps()
            update_performance_monitoring(dt, current_fps)
            continue
        elif showing_campaign_menu:
            # Render game world behind campaign menu
            graphics.render(world, player, entities, npc_manager=npc_manager)
            # Draw campaign promise menu on top
            font = get_font(None, 24)
            draw_campaign_menu(screen, font, campaign_menu_state, election_timeline)
            pygame.display.flip()
            dt = clock.tick(config.FPS) / 1000.0
            current_fps = clock.get_fps()
            update_performance_monitoring(dt, current_fps)
            continue

        # Game update logic - advance time
        dt = 1.0 / config.FPS  # Time step in seconds
        
        # CRITICAL: Calculate game_paused state at the START of each frame (before any game logic)
        # This ensures all systems check the same pause state
        game_paused = (show_inventory or show_equipment or show_pause_menu or show_settings_menu or 
                      show_achievements or show_bestiary or show_performance_menu or show_accessibility_menu or
                      show_font_settings or show_ai_settings or show_stats_menu or show_character_sheet or
                      show_crime_history or show_crafting_menu or show_repair_menu or show_cosmetic_menu or
                      show_new_equipment_ui or dialogue_ui.active or shop_ui.active or smart_inventory_ui.active or
                      fullscreen_map.active or quest_log_ui.active or showing_campaign_menu or
                      newspaper_ui.active or save_integrator.ui.active)
        
        print(f"[GAME_PAUSED] Frame start: game_paused={game_paused}, show_inventory={show_inventory}")
        
        # Handle hit-stop (freeze-frame on critical hits)
        if hit_stop_active:
            hit_stop_timer += dt
            if hit_stop_timer >= hit_stop_duration:
                hit_stop_active = False
                hit_stop_timer = 0.0
            # Reduce dt during hit-stop (slow down time)
            dt *= 0.1  # 10% speed during hit-stop
        
        # Update camera position at start of frame (prevents jumping/skipping)
        camera_x = player.x - config.SCREEN_WIDTH // 2
        camera_y = player.y - config.SCREEN_HEIGHT // 2
        
        # Apply screen shake from boss fights
        for enemy in enemies_list:
            if hasattr(enemy, 'screen_shake_intensity') and enemy.screen_shake_intensity > 0:
                import random
                shake_x = random.randint(-enemy.screen_shake_intensity, enemy.screen_shake_intensity)
                shake_y = random.randint(-enemy.screen_shake_intensity, enemy.screen_shake_intensity)
                camera_x += shake_x
                camera_y += shake_y
                break  # Only apply shake from one boss at a time
        
        game_time.advance_time(dt)
        
        # Apply disease effects to player stats
        if not show_pause_menu and not show_death_screen and not player_died:
            active_diseases = disease_manager.get_entity_diseases("player")
            
            # Reset to base stats first (if they exist)
            if not hasattr(player, 'base_max_health'):
                player.base_max_health = player.max_health
            if not hasattr(player, 'base_speed'):
                player.base_speed = player.speed
            if not hasattr(player, 'base_max_stamina'):
                player.base_max_stamina = getattr(player, 'max_stamina', 100)
            if not hasattr(player, 'base_carry_capacity'):
                player.base_carry_capacity = getattr(player, 'carry_capacity', 1000)
            
            # Start with base values
            player.max_health = player.base_max_health
            player.speed = player.base_speed
            player.max_stamina = player.base_max_stamina
            player.carry_capacity = player.base_carry_capacity
            
            # Apply racial movement speed modifiers (Elf +30% forests/grasslands, Halfling +25%)
            if hasattr(player, 'trait_manager') and player.trait_manager:
                # Get player's current terrain type
                try:
                    tile = world.get_tile(int(player.x), int(player.y))
                    terrain_type = tile.get('ground', 'grass') if tile else 'grass'
                    speed_modifier = player.trait_manager.get_movement_speed_modifier(terrain_type)
                    if speed_modifier != 1.0:
                        player.speed *= speed_modifier
                except:
                    pass  # If terrain lookup fails, skip modifier
            
            # Apply all disease effects
            for disease_infection in active_diseases:
                effects = disease_infection.get_current_effects()
                
                # Apply stat reductions
                if "max_hp_reduction" in effects:
                    player.max_health = int(player.max_health * (1 - effects["max_hp_reduction"]))
                
                if "max_stamina_reduction" in effects:
                    player.max_stamina = int(player.max_stamina * (1 - effects["max_stamina_reduction"]))
                
                if "speed_multiplier" in effects:
                    player.speed *= effects["speed_multiplier"]
                
                if "carry_capacity_reduction" in effects:
                    player.carry_capacity = int(player.carry_capacity * (1 - effects["carry_capacity_reduction"]))
                
                # HP/Stamina drains (per frame)
                if "hp_drain_per_minute" in effects:
                    drain = effects["hp_drain_per_minute"] / 3600  # Per frame at 60 FPS
                    player.health -= drain
                
                if "stamina_drain_per_minute" in effects:
                    drain = effects["stamina_drain_per_minute"] / 3600
                    if hasattr(player, 'stamina'):
                        player.stamina -= drain
            
            # Clamp health to max
            player.health = min(player.health, player.max_health)
            
            # Update plague doctor gear status every frame
            update_plague_doctor_gear_status()
        
        # Update AI player (automated testing)
        if ai_player.enabled:
            # Collect game state for AI
            current_hour, _ = game_time.get_time_hm()
            ai_game_state = {
                'towns': town_manager.towns,
                'in_town': in_town,
                'current_town_name': current_town_instance.name if current_town_instance else None,
                'in_building_interior': in_building_interior,
                'current_hour': current_hour,
                'jail_building': jail_building,
                'gathering_nodes': gathering_nodes_manager.nodes,
                'enemies': enemies_list,
                'world': world,  # Add world for tile breaking detection
            }
            
            # Get AI actions for this frame
            ai_actions = ai_player.update(dt, player, ai_game_state)
            
            # AI Mode: Auto-save every 5 minutes
            if ai_mode_enabled and ai_player.enabled:
                if not hasattr(ai_player, 'auto_save_timer'):
                    ai_player.auto_save_timer = 18000  # 5 minutes at 60 FPS
                
                ai_player.auto_save_timer -= 1
                if ai_player.auto_save_timer <= 0:
                    # Save to dedicated AI slot
                    logger.info("[AI MODE] Auto-saving to dedicated AI slot...")
                    from save_system import save_game_enhanced
                    # Use slot 99 as dedicated AI slot
                    player.tutorials_shown = tutorial_manager.tutorials_shown
                    success, message = save_game_enhanced(99, world, player)
                    if success:
                        logger.info("[AI MODE] Auto-save successful")
                    else:
                        logger.error(f"[AI MODE] Auto-save failed: {message}")
                    ai_player.auto_save_timer = 18000  # Reset timer
            
            # Execute AI movement actions with collision detection
            if 'move' in ai_actions:
                # Create key state dict for AI movement
                ai_keys = {
                    pygame.K_w: False,
                    pygame.K_a: False,
                    pygame.K_s: False,
                    pygame.K_d: False,
                    pygame.K_UP: False,
                    pygame.K_DOWN: False,
                    pygame.K_LEFT: False,
                    pygame.K_RIGHT: False,
                    pygame.K_LSHIFT: False,
                    pygame.K_RSHIFT: False,
                    pygame.K_LCTRL: False,
                    pygame.K_RCTRL: False,
                    pygame.K_SPACE: False,
                }
                
                # Set movement keys based on AI direction
                direction = ai_actions['move']
                if direction == 'up':
                    ai_keys[pygame.K_w] = True
                    ai_keys[pygame.K_UP] = True
                elif direction == 'down':
                    ai_keys[pygame.K_s] = True
                    ai_keys[pygame.K_DOWN] = True
                elif direction == 'left':
                    ai_keys[pygame.K_a] = True
                    ai_keys[pygame.K_LEFT] = True
                elif direction == 'right':
                    ai_keys[pygame.K_d] = True
                    ai_keys[pygame.K_RIGHT] = True
                
                # Store old position for collision detection
                old_x = player.x
                old_y = player.y
                
                # Update player with collision detection
                if in_building_interior:
                    # Inside buildings: don't pass world
                    player.update(ai_keys, dt, in_town=False, world=None, enemies_list=[])
                    
                    # Check interior furniture collision
                    if current_interior:
                        player_rect = pygame.Rect(player.x - 16, player.y - 16, 32, 32)
                        collision_obj = current_interior.check_collision(player_rect)
                        if collision_obj:
                            player.x = old_x
                            player.y = old_y
                elif in_town and current_town_instance:
                    # In town: pass world and town bounds
                    player.update(ai_keys, dt, in_town=True, world=world,
                                world_bounds=(current_town_instance.width, current_town_instance.height),
                                enemies_list=enemies_list)
                    
                    # Check building collision
                    player.check_building_collision(current_town_instance.buildings)
                else:
                    # Normal overworld: pass world for terrain collision
                    player.update(ai_keys, dt, in_town=in_town, world=world, enemies_list=enemies_list)
                    
                    # Check collision with standalone buildings (jail, tutorial shack)
                    standalone_buildings = [jail_building]
                    if tutorial_shack:
                        standalone_buildings.append(tutorial_shack)
                    player.check_building_collision(standalone_buildings)
            
            # Handle other key presses via events (e, f, t, i, space for combat)
            if 'press_key' in ai_actions:
                # Simulate key press by creating a fake pygame event
                key_map = {
                    'e': pygame.K_e,
                    'f': pygame.K_f,
                    't': pygame.K_t,
                    'i': pygame.K_i,
                    'space': pygame.K_SPACE,
                }
                key = ai_actions['press_key']
                
                if key == 'right_click':
                    # Simulate right-click for magic attack
                    combat_mouse_buttons[MOUSE_RIGHT] = True
                    logger.info(f"[AI PLAYER] Casting magic spell (right-click)")
                elif key in key_map:
                    fake_event = pygame.event.Event(pygame.KEYDOWN, {'key': key_map[key]})
                    pygame.event.post(fake_event)
            
            # Handle direct tile breaking from AI (bypasses combat system)
            if 'break_tile' in ai_actions and ai_actions['break_tile']:
                prev_stick_count = player.inventory.get('stick', 0)
                result = player.break_tile(world=world)
                if result:
                    logger.info(f"[AI PLAYER] Successfully broke tile at ({player.x}, {player.y})")
                    # Track sticks collected
                    if 'stick' in player.inventory:
                        ai_player.sticks_collected = player.inventory['stick']
                    # Update quest for stick collection
                    new_stick_count = player.inventory.get('stick', 0)
                    if new_stick_count > prev_stick_count:
                        sticks_gained = new_stick_count - prev_stick_count
                        if player.tutorial_active and 'tutorial_basics' in quest_manager.active_quests:
                            quest_manager.update_objective(ObjectiveType.COLLECT, "stick", sticks_gained)
                            print(f"[QUEST UPDATE] Added {sticks_gained} stick(s) to quest progress")
                else:
                    logger.debug(f"[AI PLAYER] Attempted to break tile but nothing broken at ({player.x}, {player.y})")
        
        # Update save system (for auto-save timing)
        save_integrator.update(dt)
        
        # Update AI personality systems
        personality_manager.update_all_personalities(dt)
        
        # Update trade route system (caravan movement)
        trade_route_system.update_caravans(dt)
        
        # Update traveling merchants
        npc_trade_engine.update_traveling_merchants(dt, game_time)
        
        # Update hotbar animations
        hotbar_ui.update(dt)
        
        # Update loot box animation
        lootbox_animation.update(dt)
        
        # Update combat particle effects
        combat_particles.update(dt)
        
        # Update summoning system
        summoning_system.update(dt, enemies_list, player.x, player.y)
        summon_cast_effect_ui.update(dt)
        
        # Update necromancy indicators
        if in_dungeon:
            nearby_corpses = summoning_system.get_nearby_corpses(player.x, player.y, 200)
            necromancy_indicator_ui.update(nearby_corpses, camera_x, camera_y, screen.get_width(), screen.get_height())
        
        # Check if day changed - update weather and check respawns
        if game_time.day_count != previous_day:
            previous_day = game_time.day_count
            weather_system.advance_weather()
            current_weather, intensity = weather_system.get_current_weather()
            weather_message = f"Weather changed to: {current_weather.replace('_', ' ').title()}"
            weather_message_timer = 180  # Show for 3 seconds at 60fps
            
            # Update investigation system - check if any investigations should complete
            completed_investigations = investigation_system.update(game_time, wanted_system)
            for investigation in completed_investigations:
                # Only add bounty if not witnessed (witnessed murders got instant bounty)
                if not investigation.get('witnessed', False):
                    # Add murder bounty (high amount)
                    murder_bounty = 200
                    player.wanted_level += murder_bounty
                    player.is_wanted = True
                    
                    # Show message about investigation completion
                    town_message = f"⚠️ INVESTIGATION COMPLETE!\n👮 The murder of {investigation['victim_name']} in {investigation['location']}\nhas been traced to YOU!\n💰 Bounty: +{murder_bounty}g (Total: {player.wanted_level}g)\n💔 You are now WANTED FOR MURDER!"
                    town_message_timer = 480  # Show for 8 seconds
                    logger.warning(f"[INVESTIGATION] Player found guilty of murdering {investigation['victim_name']}. Bounty +{murder_bounty}g")
                else:
                    # Just log completion for witnessed murders (already had bounty added)
                    logger.info(f"[INVESTIGATION] Witnessed murder investigation of {investigation['victim_name']} completed (bounty already applied)")
            
            # Update election system (daily)
            election_timeline.update()
            if election_timeline.state == "campaign" and election_timeline.days_in_campaign == 0:
                # Campaign just started
                logger.info(f"[ELECTION] Campaign period started! Press P to choose your campaign promises.")
                town_message = "🗳️ CAMPAIGN STARTED!\nPress P to choose your campaign promises!"
                town_message_timer = 420  # 7 seconds
            elif election_timeline.state == "voting":
                # Voting day just started
                if player.voted_this_election:
                    # This is a new election - reset vote flag
                    player.voted_this_election = False
                
                # Reset ballot box and register candidates for this election
                ballot_box.reset_for_election()
                
                # Generate candidate list (NPCs from the town)
                candidates = ["Player"]  # Player is always a candidate
                for npc in gatherer_npc_manager.npcs[:5]:  # Add up to 5 NPCs as candidates
                    if hasattr(npc, 'name'):
                        candidates.append(npc.name)
                
                ballot_box.register_candidates(candidates)
                logger.info(f"[ELECTION] Voting day! Candidates: {candidates}")
                
                # Simulate NPC voting throughout the day
                num_npc_votes = random.randint(10, 30)  # Random number of NPCs vote
                for i in range(num_npc_votes):
                    voter_id = f"npc_{i}"
                    # Random candidate selection (with some bias toward certain candidates)
                    candidate = random.choice(candidates)
                    ballot_box.cast_vote(candidate, voter_id)
                
                logger.info(f"[ELECTION] {num_npc_votes} NPCs cast their votes")
                town_message = "🗳️ VOTING DAY!\nVisit Town Hall to cast your vote!"
                town_message_timer = 420
            elif election_timeline.state == "results":
                # Count votes and determine winner
                if ballot_box.ballots:
                    vote_results = ballot_box.count_votes()
                    winner = vote_results['winner']
                    total_votes = vote_results['total_votes']
                    
                    # Log detailed results
                    logger.info(f"[ELECTION] RESULTS - Total votes: {total_votes}")
                    for candidate, votes in vote_results['results']:
                        logger.info(f"[ELECTION]   {candidate}: {votes} votes ({votes/total_votes*100:.1f}%)")
                    
                    logger.info(f"[ELECTION] WINNER: {winner} with {vote_results['results'][0][1]} votes!")
                    
                    # Clear previous mayor status
                    if current_mayor == "Player":
                        player.is_mayor = False
                    current_mayor = None
                    
                    # Set new mayor
                    if winner == "Player":
                        current_mayor = "Player"
                        player.is_mayor = True
                        town_message = f"🎉 YOU WON THE ELECTION!\n👑 You are now the MAYOR!\nTotal votes: {total_votes}\nYour votes: {vote_results['results'][0][1]}"
                        town_message_timer = 600  # 10 seconds
                        logger.info(f"[ELECTION] Player is now mayor")
                    else:
                        # NPC won - find the NPC reference
                        current_mayor_npc = None
                        for npc in gatherer_npc_manager.npcs:
                            if hasattr(npc, 'name') and npc.name == winner:
                                current_mayor = npc
                                current_mayor_npc = npc
                                logger.info(f"[ELECTION] NPC {winner} is now mayor")
                                break
                        
                        if current_mayor_npc is None:
                            # Fallback: track by name only
                            current_mayor = winner
                            logger.warning(f"[ELECTION] Could not find NPC reference for mayor {winner}")
                        
                        town_message = f"📊 ELECTION RESULTS\n🏆 Winner: {winner}\nTotal votes: {total_votes}"
                        town_message_timer = 480  # 8 seconds
                else:
                    logger.warning("[ELECTION] No votes cast - election void")
                    town_message = "❌ ELECTION VOID\nNo votes were cast!"
                    town_message_timer = 240
            elif election_timeline.state == "inauguration":
                # Inauguration day
                logger.info(f"[ELECTION] Inauguration day! New mayor takes office.")
                town_message = "👑 INAUGURATION!\nNew mayor takes office today!"
                town_message_timer = 240
                election_timeline.state = "normal"  # Reset to normal governance
            
            # Update anarchy system based on mayor popularity
            anarchy_active = anarchy_system.check_anarchy()
            if anarchy_active:
                anarchy_system.apply_anarchy_effects(town_manager)
                logger.warning("[ELECTION] Anarchy! Mayor popularity <= 8, law enforcement disabled!")
            
            # Update insurance system (expire old policies)
            insurance_system.update()
            
            # Update NPC finances (pay NPCs every 3 days)
            total_paid, npcs_paid = npc_finances_system.update_all(game_time)
            if npcs_paid > 0:
                logger.info(f"[PROPERTY] Day {game_time.day_count} - Paid {npcs_paid} NPCs (Total: {total_paid}g)")
            logger.info(f"[PROPERTY] Day {game_time.day_count} - Updated insurance and NPC finances")
            
            # Collect guard protection fees from NPCs (every 7 days per NPC)
            fees_collected = 0
            npcs_charged = 0
            for npc in gatherer_npc_manager.npcs:
                fee = guard_protection_fee_system.charge_fee(id(npc), game_time)
                if fee > 0:
                    if npc.dubloons >= fee:
                        npc.dubloons -= fee
                        fees_collected += fee
                        npcs_charged += 1
                        logger.info(f"[GUARD FEE] Collected {fee}g from {npc.name} (Balance: {npc.dubloons}g)")
                    else:
                        # Can't afford fee - log but don't charge
                        logger.warning(f"[GUARD FEE] {npc.name} cannot afford {fee}g fee (Has: {npc.dubloons}g)")
            
            if npcs_charged > 0:
                logger.info(f"[GUARD FEE] Day {game_time.day_count} - Collected {fees_collected}g from {npcs_charged} NPCs")
            
            # Check for property tax collection (yearly for players with properties)
            property_count = len(getattr(player, 'owned_properties', []))
            if property_count > 0:
                success, message, tax_amount = property_tax_system.collect_tax(player, game_time, property_count)
                if success:
                    town_message = f"💰 PROPERTY TAX\\n{message}\\n({property_count} propert{'y' if property_count == 1 else 'ies'} owned)"
                    town_message_timer = 240
                    logger.info(f"[TAX] Property tax collected: {tax_amount}g from player")
                elif tax_amount > 0:  # Tax was due but couldn't pay
                    town_message = f"⚠️ PROPERTY TAX DUE!\\n{message}\\nUnpaid debt: {property_tax_system.unpaid_taxes.get(id(player), 0)}g"
                    town_message_timer = 300
                    logger.warning(f"[TAX] Player couldn't afford property tax: {tax_amount}g")
            
            # Check for unpaid tax consequences (bounty after 30 days)
            bounty_added, bounty_message = property_tax_system.check_unpaid_consequences(player, game_time)
            if bounty_added:
                town_message = f"⚠️ TAX EVASION!\\n{bounty_message}"
                town_message_timer = 360  # 6 seconds
                logger.warning(f"[TAX] Bounty added for unpaid taxes: {bounty_message}")
            
            # Automatic jail work (reduce sentence by 1 day when day passes naturally)
            if player.in_jail:
                days_served = game_time.day_count - player.jail_start_day
                days_remaining = player.jail_days - days_served
                
                if days_remaining > 0:
                    jail_work_system.work_day(id(player))
                    logger.info(f"[JAIL] Auto-work day completed. Days remaining: {days_remaining - 1}")
                elif days_remaining <= 0:
                    # Sentence complete - auto-release
                    player.in_jail = False
                    player.jail_start_day = 0
                    player.jail_days = 0
                    player.jail_fine = 0
                    if id(player) in jail_work_system.jail_sentences:
                        del jail_work_system.jail_sentences[id(player)]
                    town_message = "⚖️ SENTENCE COMPLETE\nYou are free to go!"
                    town_message_timer = 240
                    logger.info(f"[JAIL] Player auto-released - sentence served")
            
            # Check for overdue loan penalties (daily check)
            penalty_type, penalty_amount = bank_manager.process_overdue_penalties(player, game_time, wanted_system)
            if penalty_type == 'interest_doubled':
                town_message = f"⚠️ LOAN OVERDUE!\n📈 Interest DOUBLED due to late payment!\nAdditional charge: {penalty_amount}g"
                town_message_timer = 300  # 5 seconds
                logger.error(f"[BANK] Player loan overdue - interest doubled, additional {penalty_amount}g")
            elif penalty_type == 'bounty_added':
                town_message = f"🚨 LOAN DEFAULT!\n👮 Bounty added: {penalty_amount}g\n⚠️ You are now WANTED for loan default!"
                town_message_timer = 360  # 6 seconds
                logger.error(f"[BANK] Player defaulted on loan - bounty {penalty_amount}g added")
            
            # Update mayor powers systems (daily)
            # Pay mayor salary (every 4 months = 120 days)
            if current_mayor is not None:
                if current_mayor == "Player":
                    # Pay player mayor
                    salary = mayor_salary_system.pay_salary(player, game_time)
                    if salary > 0:
                        town_message = f"💰 Mayor Salary Payment: {salary}g\n(Paid every 4 months)"
                        town_message_timer = 180
                        logger.info(f"[MAYOR] Paid player mayor salary: {salary}g")
                elif isinstance(current_mayor, str):
                    # Mayor tracked by name only (no NPC reference)
                    salary = mayor_salary_system.check_salary_due(game_time)
                    if salary > 0:
                        logger.info(f"[MAYOR] NPC mayor {current_mayor} salary due: {salary}g (no NPC reference to pay)")
                else:
                    # Pay NPC mayor
                    salary = mayor_salary_system.pay_salary(current_mayor, game_time)
                    if salary > 0:
                        mayor_name = getattr(current_mayor, 'name', 'Unknown')
                        logger.info(f"[MAYOR] Paid NPC mayor {mayor_name} salary: {salary}g")
            
            # Update embargo system (check if embargo expires)
            embargo_system.update(game_time)
            if embargo_system.embargo_active:
                logger.info(f"[MAYOR] Trade embargo active - {embargo_system.embargo_fee_percent*100}% fee on all sales")
            
            # Check for mayor absconding (5% chance per in-game year)
            daily_abscond_chance = 0.05 / 365  # ~0.0137% per day
            if not mayor_absconding_system.absconded and random.random() < daily_abscond_chance:
                # Pick a random town with significant treasury balance
                eligible_towns = []
                for town_name in town_instances.keys():
                    treasury_balance = town_treasury_system.get_balance(town_name)
                    if treasury_balance > 1000:  # Only towns with > 1000g
                        eligible_towns.append((town_name, treasury_balance))
                
                if eligible_towns:
                    # Choose random town
                    abscond_town, stolen_amount = random.choice(eligible_towns)
                    
                    # Mayor absconds with the treasury
                    town_treasury = town_treasury_system.treasuries.get(abscond_town)
                    if town_treasury:
                        # Create dummy mayor for the abscond call
                        class DummyMayor:
                            def __init__(self):
                                self.dubloons = 0
                        
                        dummy_mayor = DummyMayor()
                        mayor_absconding_system.abscond(dummy_mayor, town_treasury, abscond_town)
                        
                        # Show urgent message if player is in that town
                        if in_town and current_town_instance and current_town_instance.name == abscond_town:
                            town_message = f"🚨 BREAKING NEWS!\\n💰 The Mayor has ABSCONDED with {stolen_amount}g!\\n🔍 Talk to town guards to help track them down!"
                            town_message_timer = 480  # 8 seconds
                        
                        logger.error(f"[MAYOR ABSCOND] Mayor of {abscond_town} absconded with {stolen_amount}g treasury!")
            
            # Update homeless NPC system (shelter seeking, adoption)
            homeless_npc_system.update()
            homeless_count = len(homeless_npc_system.get_homeless_npcs())
            sheltered_count = len(homeless_npc_system.get_sheltered_npcs())
            if homeless_count > 0 or sheltered_count > 0:
                logger.info(f"[HOMELESS] Status - Homeless: {homeless_count}, Sheltered: {sheltered_count}")
            
            # Update NPC housing system (rent collection, evictions, auto-assignment)
            # Collect rent from all NPCs
            for npc in gatherer_npc_manager.npcs:
                npc_housing_system.update_rent_collection(npc)
            
            # Try to house any homeless NPCs
            newly_housed = npc_housing_system.auto_assign_homeless_npcs(gatherer_npc_manager.npcs)
            if newly_housed > 0:
                logger.info(f"[HOUSING] Auto-housed {newly_housed} homeless NPCs")
            
            # Log housing statistics
            housing_stats = npc_housing_system.get_housing_stats()
            logger.info(f"[HOUSING] Daily status - Owned: {housing_stats['owned']}, Rented: {housing_stats['rented']}, Inn: {housing_stats['inn']}, Homeless: {housing_stats['homeless']}")
            
            # Update body disposal system (corpse aging, grave visibility)
            body_disposal_system.update()
            corpse_count = len(body_disposal_system.corpses)
            grave_count = len(body_disposal_system.graves)
            
            # Update trade route system (spawn caravans, generate contracts)
            trade_route_system.update_daily()
            trade_stats = trade_route_system.get_trade_stats()
            logger.info(f"[TRADE] Daily status - Routes: {trade_stats['routes']}, Active Caravans: {trade_stats['active_caravans']}, Active Contracts: {trade_stats['active_contracts']}, Completed: {trade_stats['completed_contracts']}")
            
            # Update NPC trading system (NPCs sell resources, buy supplies)
            npc_trade_engine.update_npc_trading(game_time)
            trade_engine_stats = npc_trade_engine.get_statistics()
            logger.info(f"[NPC TRADE] Daily volume: {trade_engine_stats['daily_trade_volume']}g, Total sales: {trade_engine_stats['total_npc_sales']}g, Purchases: {trade_engine_stats['total_npc_purchases']}g")
            
            # Update investment system (stock prices, NPC investors)
            investment_system.update_daily()
            investment_stats = investment_system.get_statistics()
            logger.info(f"[INVESTMENT] Market status: {investment_stats['market_status']}, Daily volume: {investment_stats['daily_volume']} shares")
            
            # Generate daily newspaper
            current_newspaper = newspaper_generator.generate_daily_newspaper(
                game_time, 
                market_manager=market_manager,
                election_system=election_system if 'election_system' in locals() else None,
                family_system=npc_family_system if 'npc_family_system' in locals() else None,
                weather_system=weather_system,
                disease_manager=disease_manager
            )
            newspaper_distribution.publish_edition(current_newspaper)
            article_count = len(current_newspaper.articles)
            logger.info(f"[NEWSPAPER] Published Day {game_time.day_count} edition with {article_count} articles")
            
            # Archive newspaper in all libraries
            library_manager.add_newspaper_to_all_libraries(current_newspaper)
            
            # Update disease infections for player
            messages = disease_manager.update_infections(
                "player",
                {
                    "has_plague_doctor_gear": player.has_plague_doctor_gear,
                    "has_plague_survivor_trait": disease_manager.is_plague_survivor("player"),
                    "has_magic_protection": False  # TODO: Check for magic buffs
                },
                time.time()
            )
            
            # Handle disease progression messages
            for msg in messages:
                if msg == "DEATH_BY_PLAGUE":
                    player_died = True
                    player.health = 0
                    show_death_screen = True
                    death_screen_option = 0
                    logger.warning("[DEATH] Player died from plague!")
                else:
                    town_message = msg
                    town_message_timer = 180
            
            # Check disease achievements daily
            achievement_manager.check_all_disease(
                plague_survived=player.ach_plague_survived,
                std_free_years=player.ach_std_free_years,
                refugees_saved=player.ach_refugees_saved,
                fire_sneeze_arrests=player.ach_fire_sneeze_arrests,
                npcs_cured=player.ach_npcs_cured,
                disease_free_years=player.ach_disease_free_years
            )
            unlocked = achievement_manager.get_recent_unlock()
            if unlocked:
                achievement_popup.show(unlocked)
                logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
            
            # === DISEASE OUTBREAK GENERATION (Daily Checks) ===
            # Random outbreak chance: ~1% per town per week (0.14% per day)
            if random.random() < 0.0014:
                # Select random town for outbreak
                if town_instances:
                    outbreak_town = random.choice(list(town_instances.values()))
                    # Weight disease selection (plague rare, common diseases more frequent)
                    disease_weights = {
                        "plague": 0.05,          # 5% - very rare
                        "flu": 0.30,             # 30% - common
                        "common_cold": 0.40,     # 40% - most common
                        "shadow_plague": 0.10,   # 10% - magical
                        "fire_sneezing": 0.10,   # 10% - magical
                        "fey_fever": 0.05        # 5% - rare magical
                    }
                    
                    diseases = list(disease_weights.keys())
                    weights = list(disease_weights.values())
                    outbreak_disease = random.choices(diseases, weights=weights)[0]
                    
                    # Start the outbreak
                    disease_manager.start_outbreak(outbreak_town.name, outbreak_disease)
                    
                    # Show message if player is near
                    if in_town and current_town_instance and current_town_instance.name == outbreak_town.name:
                        disease_def = DISEASE_DEFINITIONS.get(outbreak_disease)
                        disease_name = disease_def.name if disease_def else outbreak_disease
                        town_message = f"⚠️ OUTBREAK WARNING!\\n{disease_name} is spreading through {outbreak_town.name}!"
                        town_message_timer = 300  # 5 seconds
                    
                    logger.warning(f"[OUTBREAK] {outbreak_disease} outbreak started in {outbreak_town.name}")
            
            # === DISEASE INFECTION TRIGGERS (Daily Checks) ===
            
            # Weather-based infections (cold/flu in winter/rain)
            current_season = weather_system.get_season()
            current_weather = weather_system.current_weather
            
            if current_season == "Winter" or current_weather == "Rain":
                # Higher infection chance in winter/rain
                base_chance = 0.05 if current_season == "Winter" else 0.02
                
                # Apply modifiers
                modifiers = {
                    "weather": 1.5 if current_weather == "Rain" else 1.0,
                    "has_protective_gear": 0.3 if player.has_plague_doctor_gear else 1.0,
                    "is_plague_survivor": 0.5 if disease_manager.is_plague_survivor("player") else 1.0
                }
                
                infection_chance = disease_manager.calculate_infection_chance(base_chance, modifiers)
                
                if random.random() < infection_chance:
                    # Infect with common cold or flu
                    disease_id = random.choice(["common_cold", "flu"])
                    disease_manager.infect_entity("player", disease_id, "weather")
                    town_message = f"You've caught {disease_id.replace('_', ' ')}!"
                    town_message_timer = 180
                    logger.info(f"[DISEASE] Player infected with {disease_id} from weather")
            
            # Town outbreak infections (spread from quarantined towns)
            if in_town and current_town_instance:
                town_name = current_town_instance.name
                
                # Check if current town has outbreak
                outbreaks = disease_manager.get_town_outbreaks(town_name)
                for disease_id in outbreaks:
                    # 10% chance per day in outbreak town
                    modifiers = {
                        "outbreak": 3.0,  # Triple infection rate
                        "has_protective_gear": 0.3 if player.has_plague_doctor_gear else 1.0,
                        "is_plague_survivor": 0.1 if disease_manager.is_plague_survivor("player") else 1.0
                    }
                    
                    disease_def = DISEASE_DEFINITIONS.get(disease_id)
                    if disease_def:
                        infection_chance = disease_manager.calculate_infection_chance(
                            disease_def.base_infection_rate, modifiers)
                        
                        if random.random() < infection_chance:
                            disease_manager.infect_entity("player", disease_id, "outbreak")
                            town_message = f"⚠️ You've been infected with {disease_def.name}!"
                            town_message_timer = 180
                            logger.warning(f"[DISEASE] Player infected with {disease_id} from outbreak in {town_name}")
                            break  # Only one disease per day
            
            # Random dungeon magical disease infections (if in dungeon)
            if in_dungeon:
                # 2% chance per day of magical disease in dungeons
                if random.random() < 0.02:
                    magical_diseases = ["fire_sneezing", "arcane_flu", "shadow_plague", "mana_rot", "fey_fever"]
                    disease_id = random.choice(magical_diseases)
                    
                    modifiers = {
                        "has_magic_protection": 0.5 if hasattr(player, 'has_magic_protection') and player.has_magic_protection else 1.0,
                        "dungeon": 1.5  # 50% higher in dungeons
                    }
                    
                    disease_def = DISEASE_DEFINITIONS.get(disease_id)
                    if disease_def:
                        infection_chance = disease_manager.calculate_infection_chance(
                            disease_def.base_infection_rate, modifiers)
                        
                        if random.random() < infection_chance:
                            disease_manager.infect_entity("player", disease_id, "dungeon")
                            town_message = f"⚠️ Magical infection: {disease_def.name}!"
                            town_message_timer = 180
                            logger.warning(f"[DISEASE] Player infected with magical {disease_id} in dungeon")
            
            # Update town trade agreements (check expirations, NPC proposals)
            town_trade_agreement_system.update_daily()
            agreement_stats = town_trade_agreement_system.get_statistics()
            logger.info(f"[TRADE AGREEMENTS] Active: {agreement_stats['active_agreements']}, Total savings: {agreement_stats['total_savings']}g")
            
            # Update NPC contract system (accept new contracts, fulfill active ones)
            npc_contract_system.update_daily(game_time)
            npc_contract_system.update_fulfillment(game_time)
            contract_stats = npc_contract_system.get_statistics()
            logger.info(f"[NPC CONTRACTS] Active: {contract_stats['active_contracts']}, Completed: {contract_stats['completed_contracts']}, Earnings: {contract_stats['total_earnings']}g")
            
            # Weekly update - pay dividends (every 7 days)
            if game_time.day_count % 7 == 0:
                investment_system.update_weekly()
                logger.info("[INVESTMENT] Weekly dividends paid to shareholders")
            
            # Update NPC skill switching system (complete training, auto-suggestions)
            completed_training = npc_skill_switching_system.update_training()
            for npc_id in completed_training:
                # Find NPC and complete switch
                for npc in gatherer_npc_manager.npcs:
                    if id(npc) == npc_id:
                        success, message = npc_skill_switching_system.complete_profession_switch(npc)
                        if success:
                            logger.info(f"[SKILL SWITCH] {npc.name}: {message}")
                        break
            
            # Auto-suggest profession switches (5% chance per NPC per day)
            switches_suggested = 0
            switches_executed = 0
            for npc in gatherer_npc_manager.npcs:
                suggested = npc_skill_switching_system.auto_suggest_profession_switch(npc, market_manager)
                if suggested:
                    switches_suggested += 1
                    success, message = npc_skill_switching_system.auto_execute_switch(npc, suggested)
                    if success:
                        switches_executed += 1
            
            if switches_suggested > 0:
                logger.info(f"[SKILL SWITCH] Daily auto-suggestions: {switches_suggested} suggested, {switches_executed} accepted")
            
            # Log skill switching statistics
            switch_stats = npc_skill_switching_system.get_stats()
            if switch_stats['active_training'] > 0 or switch_stats['total_switches'] > 0:
                logger.info(f"[SKILL SWITCH] Status - Training: {switch_stats['active_training']}, Cooldowns: {switch_stats['active_cooldowns']}, Total Switches: {switch_stats['total_switches']}")
            
            if corpse_count > 0 or grave_count > 0:
                logger.info(f"[BODY] Status - Corpses: {corpse_count}, Graves: {grave_count}")
            
            # Update wilderness fighter system (patrols, combat)
            wilderness_fighter_system.update()
            active_fighters = len(wilderness_fighter_system.get_active_fighters())
            if active_fighters > 0:
                logger.info(f"[WILDERNESS] Active fighters: {active_fighters}")
            
            # CRITICAL FIX: Check dungeon resets on day change
            dungeons_reset = 0
            for entrance_pos, dungeon in dungeon_instances.items():
                if dungeon and hasattr(dungeon, 'check_and_reset'):
                    was_cleared = getattr(dungeon, 'cleared', False)
                    dungeon.check_and_reset(game_time.day_count)
                    # If it was cleared and now isn't, it was reset
                    if was_cleared and not getattr(dungeon, 'cleared', False):
                        dungeons_reset += 1
            
            if dungeons_reset > 0:
                logger.info(f"Day {game_time.day_count} - {dungeons_reset} dungeon(s) reset and ready for re-exploration!")
            
            # CRITICAL FIX: Restock shops daily
            shop_manager.daily_update(game_time.day_count)
            logger.info(f"Day {game_time.day_count} - Merchant shops restocked")
            
            # Update caravan system
            caravan_manager.daily_update(game_time.day_count)
            
            # Update shop ownership (simulate daily sales)
            shop_ownership_manager.daily_update(game_time.day_count)
            
            # Update price events (check expiry, spawn new events)
            town_names = list(town_instances.keys())
            price_event_manager.update(game_time.day_count, town_names)
            
            # Update merchant quests (check deadlines)
            merchant_quest_manager.update(game_time.day_count)
            
            # === CRIMINAL SYSTEMS DAILY UPDATES ===
            # Run criminal enterprises (passive income)
            enterprise_profits = enterprise_manager.run_daily_operations()
            if enterprise_profits > 0:
                player.gold += enterprise_profits
                logger.info(f"[ENTERPRISE] Daily profits: {enterprise_profits}g from {len(enterprise_manager.enterprises)} enterprises")
            
            # Update money laundering operations
            completed_ops = money_laundering.update_operations()
            for op in completed_ops:
                player.gold += op['clean_amount']
                player.dirty_money -= op['dirty_amount']
                logger.info(f"[LAUNDERING] Completed: {op['clean_amount']}g clean money")
            
            # Update market manipulations (reduce duration)
            market_manipulation.update()
            
            # Slowly reduce criminal heat when no crimes committed
            if criminal_rank_system.heat > 0 and game_time.day_count % 2 == 0:  # Every 2 days
                criminal_rank_system.heat = max(0, criminal_rank_system.heat - 5)
                if criminal_rank_system.heat % 20 == 0:  # Log every 20 heat reduction
                    logger.info(f"[CRIMINAL] Heat decreased to {criminal_rank_system.heat}")
            
            # === END CRIMINAL SYSTEMS UPDATES ===
            
            # Generate daily merchant quests
            merchants_list = [(shop_id, shop['shop'].name) for shop_id, shop in shop_manager.shops.items()]
            merchant_quest_manager.generate_daily_quests(merchants_list)
            
            # Market economy: Update prices twice daily (morning and evening)
            current_hour = game_time.elapsed_time / 3600  # Convert to hours
            if 8 <= current_hour < 9:  # Morning update (8-9 AM)
                market_manager.update_daily_prices(game_time.day_count, 'morning')
                logger.info(f"Day {game_time.day_count} - Morning market prices updated")
            elif 20 <= current_hour < 21:  # Evening update (8-9 PM)
                market_manager.update_daily_prices(game_time.day_count, 'evening')
                logger.info(f"Day {game_time.day_count} - Evening market prices updated")
            
            # Check for resource respawns (pass player position for notifications)
            respawned, nearby_respawned = respawn_manager.check_respawns(world, player.x, player.y)
            if respawned:
                logger.debug(f"[RESPAWN] {len(respawned)} resources respawned")
                
                # Display notification if resources respawned nearby
                if nearby_respawned:
                    # Get the closest one for notification
                    closest = min(nearby_respawned, key=lambda r: r[3])
                    resource_name = closest[2].replace('_', ' ').title()
                    if len(nearby_respawned) == 1:
                        town_message = f"🌱 A {resource_name} has regrown nearby!"
                    else:
                        town_message = f"🌱 {len(nearby_respawned)} resources have regrown nearby!"
                    town_message_timer = 180  # 3 seconds at 60 FPS
        
        # Apply weather effects to player
        current_weather, intensity = weather_system.get_current_weather()
        weather_effect_msg = apply_weather_effects_to_player(player, current_weather, dt)
        if weather_effect_msg:
            weather_message = weather_effect_msg
            weather_message_timer = 180
        
        # Countdown weather message timer
        if weather_message_timer > 0:
            weather_message_timer -= 1
            if weather_message_timer <= 0:
                weather_message = None
        
        # Countdown level-up message timer
        if level_up_timer > 0:
            level_up_timer -= 1
            if level_up_timer <= 0:
                level_up_message = None
        
        # Countdown death message timer
        if death_message_timer > 0:
            death_message_timer -= 1
            if death_message_timer <= 0:
                death_message = None
        
        # CRITICAL FIX: Town enter/exit detection
        if town_message_timer > 0:
            town_message_timer -= 1
            if town_message_timer <= 0:
                town_message = ""
        
        # OLD TOWN DETECTION SYSTEM - DISABLED (using town instances now)
        # Previous code that handled town zones on overworld has been removed
        # Towns are now separate instances accessed via gates
        
        # Enemy spawning system
        if not in_dungeon and not in_town:  # Only spawn in overworld (not in dungeons or towns)
            enemy_spawn_timer += dt
            # Check enemy cap before spawning
            if enemy_spawn_timer >= enemy_spawn_interval and len(enemies_list) < MAX_ENEMIES:
                enemy_spawn_timer = 0
                # Spawn enemies off-screen but not too far (use frame-start camera)
                
                # Choose spawn position outside camera view
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    spawn_x = player.x + random.randint(-400, 400)
                    spawn_y = camera_y - random.randint(100, 200)
                elif side == "bottom":
                    spawn_x = player.x + random.randint(-400, 400)
                    spawn_y = camera_y + config.SCREEN_HEIGHT + random.randint(100, 200)
                elif side == "left":
                    spawn_x = camera_x - random.randint(100, 200)
                    spawn_y = player.y + random.randint(-400, 400)
                else:  # right
                    spawn_x = camera_x + config.SCREEN_WIDTH + random.randint(100, 200)
                    spawn_y = player.y + random.randint(-400, 400)
                
                # Check if spawn position is too close to any town (safe zone)
                too_close_to_town = False
                for town in town_manager.towns:
                    distance_to_town = ((spawn_x - town.center_x) ** 2 + (spawn_y - town.center_y) ** 2) ** 0.5
                    # Don't spawn within town radius + buffer (at least 300 pixels away from town edge)
                    if distance_to_town < (town.radius + 300):
                        too_close_to_town = True
                        break
                
                # Also check if spawn is near any gate
                for gate_x, gate_y in town_gates.values():
                    distance_to_gate = ((spawn_x - gate_x) ** 2 + (spawn_y - gate_y) ** 2) ** 0.5
                    if distance_to_gate < 400:  # 400 pixel buffer around gates
                        too_close_to_town = True
                        break
                
                # Only spawn if not too close to towns
                if not too_close_to_town:
                    # Determine spawn based on time of day
                    night_enemies = ["wolf", "shadow_wolf", "zombie", "bat", "spider"]
                    day_enemies = ["slime", "goblin", "caterpillar", "golem"]
                    
                    if game_time.get_phase() == "night":
                        enemy_type = random.choice(night_enemies)
                    else:
                        enemy_type = random.choice(day_enemies)
                    
                    # Spawn the enemy
                    new_enemy = spawn_enemy(spawn_x, spawn_y, enemy_type, player.level)
                    enemies_list.append(new_enemy)
                    logger.debug(f"[ENEMY SPAWN] {new_enemy.rarity} {enemy_type} spawned at ({spawn_x}, {spawn_y})")

        # Skip game updates if full-screen map is open (pause game)
        if not fullscreen_map.active and not show_equipment and not show_inventory and not show_death_screen and not save_integrator.ui.active:
            
            keys = pygame.key.get_pressed()
            
            # Update shift key states for sprint toggle detection (reset when keys released)
            if not keys[pygame.K_LSHIFT]:
                player.last_lshift_state = False
            if not keys[pygame.K_RSHIFT]:
                player.last_rshift_state = False
            
            # Build custom keys dict with key bindings - OPTIMIZED
            # Create a dict-like object that returns False for missing keys
            class KeyStateDict(dict):
                def __missing__(self, key):
                    return False
            
            remapped_keys = KeyStateDict()
            
            # Add virtual keys for movement actions
            if any(keys[k] for k in key_bindings.get_keys_for_action("move_up") if k is not None):
                remapped_keys[pygame.K_w] = True
                remapped_keys[pygame.K_UP] = True
            if any(keys[k] for k in key_bindings.get_keys_for_action("move_down") if k is not None):
                remapped_keys[pygame.K_s] = True
                remapped_keys[pygame.K_DOWN] = True
            if any(keys[k] for k in key_bindings.get_keys_for_action("move_left") if k is not None):
                remapped_keys[pygame.K_a] = True
                remapped_keys[pygame.K_LEFT] = True
            if any(keys[k] for k in key_bindings.get_keys_for_action("move_right") if k is not None):
                remapped_keys[pygame.K_d] = True
                remapped_keys[pygame.K_RIGHT] = True
            
            # Add sprint keys (Both Left and Right Shift) - track independently for toggle
            remapped_keys[pygame.K_LSHIFT] = keys[pygame.K_LSHIFT]
            remapped_keys[pygame.K_RSHIFT] = keys[pygame.K_RSHIFT]
            
            # Add sneak keys (Both Left and Right Ctrl)
            ctrl_state = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
            remapped_keys[pygame.K_LCTRL] = ctrl_state  # Use LCTRL as the canonical sneak key
            remapped_keys[pygame.K_RCTRL] = ctrl_state  # Also track RCTRL
            
            # Simple attack key mapping - event-based for keyboard, state-based for mouse
            attack_keys_list = key_bindings.get_keys_for_action("attack")
            for k in attack_keys_list:
                # Check keyboard keys (event-based from combat_attack_keys)
                if k is not None and k < 512 and combat_attack_keys.get(k, False):  # Keyboard keys are < 512
                    remapped_keys[k] = True
                # Check mouse buttons (state-based)
                elif k is not None and k in combat_mouse_buttons and combat_mouse_buttons[k]:
                    remapped_keys[k] = True
            
            # Only update player if not dead and not in a building menu
            if not player_died:
                # Track player position before update for distance calculation
                old_x, old_y = player.x, player.y
                
                # Disable movement when building UIs, dialogue, or jail are active
                building_ui_active = (inn_ui.active or blacksmith_ui.active or tavern_ui.active or 
                                     temple_ui.active or bank_ui.active or town_hall_ui.active or 
                                     shop_ui.active or dialogue_ui.active or player.in_jail)
                
                if not building_ui_active:
                    # Store old position before movement for collision revert
                    old_x = player.x
                    old_y = player.y
                    
                    # Check building interior FIRST (takes priority over town checks)
                    if in_building_interior:
                        # Inside buildings: don't pass world to avoid terrain collision checks
                        player.update(remapped_keys, dt, in_town=False, world=None,
                                    enemies_list=[])
                    elif in_town and current_town_instance:
                        # In town but not in building: pass world bounds
                        player.update(remapped_keys, dt, in_town=True, world=world,
                                    world_bounds=(current_town_instance.width, current_town_instance.height),
                                    enemies_list=enemies_list)
                    else:
                        # Normal overworld movement
                        player.update(remapped_keys, dt, in_town=in_town, world=world,
                                    enemies_list=enemies_list)
                
                # Update dungeon variety systems if in dungeon
                if in_dungeon and current_dungeon:
                    # Update speed run timer
                    if hasattr(current_dungeon, 'modifier') and current_dungeon.modifier == 'speed_run':
                        timer_data = dungeon_variety.update_speed_run_timer(dt)
                        speed_run_timer_ui.update(timer_data)
                        if timer_data.get('failed', False):
                            messages.add_message("⏱️ Speed run failed! Time's up!")
                    
                    # Check for trap triggers
                    if hasattr(current_dungeon, 'traps'):
                        triggered_traps = dungeon_variety.check_trap_triggers(player.x, player.y, dt)
                        for trap in triggered_traps:
                            trap_damage = player.take_damage(trap['damage'], damage_type='physical')
                            trap_warning_ui.add_warning(trap['x'], trap['y'], trap['type'])
                            damage_text = DamageNumber(trap['x'], trap['y'], trap_damage, is_crit=False, is_player=True, damage_type="trap")
                            floating_texts.append(damage_text)
                            trap_name = trap['properties'].get('name', 'Trap')
                            combat_log.add_message(f"💥 {trap_name} hit you for {trap_damage} damage!", (255, 150, 50))
                    
                    # Check for secret room discovery
                    if hasattr(current_dungeon, 'secret_rooms'):
                        discovered = dungeon_variety.check_secret_discovery(player.x, player.y, interaction_range=48)
                        if discovered:
                            secret_discovered_ui.show(discovered)
                            messages.add_message(f"✨ Discovered: {discovered.properties.get('name', 'Secret Room')}!")
                    
                    dungeon_info_ui.update(dt)
                
                # Update dungeon variety UI timers
                trap_warning_ui.update(dt)
                secret_discovered_ui.update(dt)
                
                # Check collision based on location
                if in_building_interior and current_interior:
                    # Check interior furniture collision
                    player_rect = pygame.Rect(player.x - 16, player.y - 16, 32, 32)
                    collision_obj = current_interior.check_collision(player_rect)
                    if collision_obj:
                        # Push player out of furniture
                        # Simple pushback based on overlap
                        player.x = old_x
                        player.y = old_y
                elif in_town and current_town_instance:
                    # Check building collision in town instances
                    player.check_building_collision(current_town_instance.buildings)
                elif not in_town:
                    # Check collision with standalone buildings (jail, tutorial shack) in overworld
                    standalone_buildings = [jail_building]
                    if tutorial_shack:
                        standalone_buildings.append(tutorial_shack)
                    player.check_building_collision(standalone_buildings)
                
                # Universal death check (check after any damage source)
                # Skip death check if save/load UI is active
                if player.health <= 0 and not player_died and not save_integrator.ui.active:
                    # Check Halfling death dodge (only in dungeons)
                    dodged_death = False
                    if hasattr(player, 'trait_manager') and player.trait_manager:
                        dodged_death = player.trait_manager.check_death_dodge(in_dungeon=in_dungeon)
                    
                    if dodged_death:
                        player.health = player.max_health * 0.25  # Restore to 25% health
                        logger.info("[TRAIT] Halfling Lucky Escape! Death dodged in dungeon!")
                        town_message = "🍀 Lucky Escape! You narrowly avoided death!"
                        town_message_timer = 180
                    else:
                        player_died = True
                        player.health = 0
                        show_death_screen = True
                        death_screen_option = 0
                        logger.warning("[DEATH] Player has died!")
                        player.ach_deaths += 1
                
                # Reset death state if player is revived (health restored)
                if player_died and player.health > 0:
                    player_died = False
                    show_death_screen = False
                    logger.info("[DEATH] Player revived!")
                
                # Track distance traveled for achievements
                dx = player.x - old_x
                dy = player.y - old_y
                distance = (dx**2 + dy**2) ** 0.5
                player.ach_distance_traveled += distance
                
                # Check and resolve enemy collisions
                player.check_enemy_collision(enemies_list)
                entities.update(player)
                
                # Update floating damage numbers
                for floating_text in floating_texts[:]:
                    floating_text.update(dt, camera_x, camera_y)
                    if not floating_text.alive:
                        floating_texts.remove(floating_text)
                
                # Check for active status effects and add visual particles
                if hasattr(player, 'status_manager') and player.status_manager:
                    active_effects = player.status_manager.active_effects
                    # Add particles for status effects every 0.5 seconds
                    if hasattr(player, '_last_effect_particle_time'):
                        if time.time() - player._last_effect_particle_time >= 0.5:
                            for effect_name, effect_data in active_effects.items():
                                if effect_name in ['burn', 'poison', 'freeze', 'bleed', 'shock']:
                                    combat_particles.add_status_effect(effect_name, (player.x, player.y), (player.rect.width, player.rect.height))
                            player._last_effect_particle_time = time.time()
                    else:
                        player._last_effect_particle_time = time.time()
                
                # OPTIMIZATION: Time-based updates instead of frame-based (smoother performance)
                # Accumulate delta time and update when interval is reached
                npc_update_accumulator += dt
                gatherer_update_accumulator += dt
                family_update_accumulator += dt
                
                # NOTE: game_paused calculation MOVED to start of frame (line ~6910) to fix pause bug
                # Old location caused timing issues where enemies could attack before pause was calculated
                
                # Debug output to track pause state during NPC updates
                if show_inventory or show_equipment or show_pause_menu or game_paused:
                    print(f"[NPC UPDATE SECTION] game_paused={game_paused}, show_inventory={show_inventory}")
                
                # Update gathering nodes at reduced frequency (only if not paused)
                if npc_update_accumulator >= NPC_UPDATE_INTERVAL and not game_paused:
                    # Update gathering nodes (respawn checks with weather/season effects, gathering progress)
                    gathering_nodes_manager.update(npc_update_accumulator, game_time, player, weather_system)
                    
                    # Update town guards at the same interval as NPCs
                    guard_update_count = 0
                    print(f"[DEBUG GUARD SYSTEM] in_town={in_town}, num_guards={len(town_guards)}, dt={npc_update_accumulator:.4f}, paused={game_paused}")
                    for guard in town_guards:
                        if in_town and current_town_instance:
                            # Only update guards in current town
                            if hasattr(guard, 'current_town') and guard.current_town == current_town_instance.name:
                                print(f"[DEBUG] Updating guard {guard.name} in {current_town_instance.name}, state={guard.state}, is_patrolling={guard.is_patrolling}")
                                guard.update(npc_update_accumulator, world, player)
                                guard_update_count += 1
                            else:
                                print(f"[DEBUG] Skipping guard {guard.name} (town={getattr(guard, 'current_town', 'NONE')}, current={current_town_instance.name if current_town_instance else 'NONE'})")
                        else:
                            # Update guards in their own towns when player is in overworld
                            print(f"[DEBUG] Updating guard {guard.name} in overworld mode, state={guard.state}, is_patrolling={guard.is_patrolling}")
                            guard.update(npc_update_accumulator, world, None)
                            guard_update_count += 1
                    
                    if guard_update_count > 0:
                        print(f"[DEBUG] Updated {guard_update_count} guards total")
                    
                    npc_update_accumulator = 0.0
                
                # Update gatherer NPCs even less frequently for better performance (only if not paused)
                if gatherer_update_accumulator >= GATHERER_UPDATE_INTERVAL and not game_paused:
                    # Update gatherer NPCs (AI, gathering, banking, warning timers)
                    gatherer_npc_manager.update_all(gatherer_update_accumulator, game_time, gathering_nodes_manager, player)
                    gatherer_update_accumulator = 0.0
                
                # Check if we need to restore tutorial NPC from loaded save
                if hasattr(player, 'tutorial_npc_saved_state') and player.tutorial_npc_saved_state:
                    saved_state = player.tutorial_npc_saved_state
                    # Recreate NPC from saved state
                    tutorial_npc = TutorialNPC(saved_state['x'], saved_state['y'])
                    tutorial_npc.health = saved_state.get('health', 275)
                    tutorial_npc.max_health = saved_state.get('max_health', 275)
                    tutorial_npc.declined_by_player = saved_state.get('declined_by_player', False)
                    tutorial_npc.going_to_shelter = saved_state.get('going_to_shelter', False)
                    tutorial_npc.at_shelter = saved_state.get('at_shelter', False)
                    tutorial_npc.shack_x = saved_state.get('shack_x', None)
                    tutorial_npc.shack_y = saved_state.get('shack_y', None)
                    tutorial_npc.in_building = saved_state.get('in_building', None)
                    player.tutorial_npc = tutorial_npc
                    
                    # Recreate the shack if it was created
                    if tutorial_npc.shack_x and tutorial_npc.shack_y:
                        tutorial_shack = Building(BuildingType.SHACK, 
                                                tutorial_npc.shack_x - 30,
                                                tutorial_npc.shack_y - 40, 
                                                60, 80, name="Wandering Guide's Shack")
                        tutorial_shack.is_enterable = True
                        
                        # Create the shack interior
                        shack_interior = BuildingInterior(
                            BuildingType.SHACK,
                            width=400,
                            height=400
                        )
                        building_interiors["TUTORIAL_SHACK"] = shack_interior
                        logger.info(f"[TUTORIAL] Recreated shack at ({tutorial_npc.shack_x}, {tutorial_npc.shack_y})")
                    
                    logger.info(f"[TUTORIAL] NPC restored from loaded save at ({tutorial_npc.x}, {tutorial_npc.y}), health={tutorial_npc.health}, in_building={tutorial_npc.in_building}")
                    # Clean up the saved state
                    del player.tutorial_npc_saved_state
                
                # Update tutorial NPC if it exists (only if not paused)
                if hasattr(player, 'tutorial_npc') and player.tutorial_npc and not game_paused:
                    tutorial_npc = player.tutorial_npc
                    
                    # Always update NPC in combat, even when inside buildings
                    if tutorial_npc.combat_target:
                        tutorial_npc.update(dt, player)
                    # Only update for peaceful movement if not inside a building
                    elif not hasattr(tutorial_npc, 'in_building') or not tutorial_npc.in_building:
                        tutorial_npc.update(dt, player)
                        
                        # Check if NPC reached shelter and should enter
                        if tutorial_npc.at_shelter:
                            # NPC enters the shack - mark as inside but keep reference
                            if "TUTORIAL_SHACK" in building_interiors:
                                tutorial_npc.in_building = "TUTORIAL_SHACK"
                                # Position NPC inside the shack interior
                                shack_interior = building_interiors["TUTORIAL_SHACK"]
                                tutorial_npc.x = shack_interior.width // 2 + 50
                                tutorial_npc.y = shack_interior.height // 2 - 100
                                logger.info("[TUTORIAL] NPC entered shack interior")
                            town_message = "The Wandering Guide enters their shack."
                            town_message_timer = 180
                            logger.info("[TUTORIAL] NPC reached shelter and entered shack")
                
                # Update NPC family system periodically
                if family_update_accumulator >= FAMILY_UPDATE_INTERVAL:
                    # Update NPC family system (family schedules, relationships)
                    npc_family_system.update()
                    family_update_accumulator = 0.0
                
                # Check curfew violations if in town (detection-based enforcement)
                # Run every frame when player is in town during curfew hours
                if in_town and current_town_instance:
                    current_hour, _ = game_time.get_time_hm()
                    if curfew_system.is_curfew_active(current_town_instance.name) and curfew_system.is_curfew_hours(current_hour):
                        # Check if player is detected by guards during curfew
                        town_guards_list = [g for g in town_guards if hasattr(g, 'current_town') and g.current_town == current_town_instance.name]
                        if town_guards_list:
                            # First check vision cone-based detection (stealth system)
                            detections = stealth_system.check_player_detection(player, town_guards_list)
                            
                            # FALLBACK: Add proximity-based detection for nearby guards (more reliable for curfew)
                            # Guards automatically notice players within 250 pixels during curfew hours
                            if not detections:
                                for guard in town_guards_list:
                                    dx = guard.x - player.x
                                    dy = guard.y - player.y
                                    distance = math.sqrt(dx * dx + dy * dy)
                                    
                                    if distance <= 250:  # 250 pixel detection radius (5 tiles)
                                        # Guard detected player through proximity
                                        detection_chance = 1.0 - (distance / 250.0)  # Closer = higher chance
                                        detections.append((guard.name, detection_chance, guard))
                                        logger.info(f"[CURFEW] {guard.name} detected player via proximity ({distance:.0f}px away)")
                        
                        if detections:  # Player was detected by at least one guard
                            # Only fine if player hasn't been fined recently (cooldown to prevent spam)
                            if not hasattr(player, 'last_curfew_fine_time'):
                                player.last_curfew_fine_time = 0
                            
                            current_time = time.time()
                            if current_time - player.last_curfew_fine_time >= 10.0:  # 10 second cooldown between fines
                                # Fine player for curfew violation
                                fine = curfew_system.fine_player(player, town_treasury_system, current_town_instance.name)
                                if fine > 0:
                                    player.curfew_violations += 1
                                    player.last_curfew_fine_time = current_time
                                    detecting_guard_id = detections[0][0]  # Get first detecting guard's ID
                                    town_message = f"⚠️ CURFEW VIOLATION!\n👮 Guard spotted you!\n🕐 Curfew: 5PM-2AM\n💰 Fine: {fine}g\n⚖️ Violations: {player.curfew_violations}"
                                    town_message_timer = 240
                                    logger.warning(f"[CURFEW] Guard {detecting_guard_id} caught player during curfew! Fine: {fine}g (total: {player.curfew_violations})")
                                
                                # Make all detecting guards chase the player
                                for guard_id, detection_chance, guard_ref in detections:
                                    # Find the actual guard object and make it chase
                                    for guard in town_guards_list:
                                        if guard.name == guard_id or id(guard) == guard_id:
                                            guard.chase_target = player
                                            guard.change_state("chase")
                                            guard.alert_timer = 600  # Chase for 10 seconds (600 frames at 60fps)
                                            logger.info(f"[CURFEW] {guard.name} is now chasing player for curfew violation!")
                                            break
                
                # Update vision cones for guards (stealth system)
                if in_town and current_town_instance:
                    for guard in town_guards:
                        if hasattr(guard, 'current_town') and guard.current_town == current_town_instance.name:
                            # Calculate direction based on movement or patrol
                            direction = 0  # Default facing right
                            if hasattr(guard, 'facing'):
                                facing_map = {'right': 0, 'down': 90, 'left': 180, 'up': 270}
                                direction = facing_map.get(guard.facing, 0)
                            stealth_system.update_vision_cone(guard.name, guard.x, guard.y, direction)
                    
                    # Check player detection by guards (stealth system)
                    if in_town and current_town_instance:
                        town_guards_list = [g for g in town_guards if hasattr(g, 'current_town') and g.current_town == current_town_instance.name]
                        detections = stealth_system.check_player_detection(player, town_guards_list)
                        player.detected_by_npcs = detections
                        
                        # If player is wanted and detected, guards become hostile
                        if player.is_wanted and detections:
                            for npc_id, detection_chance, guard in detections:
                                # Random detection check based on chance
                                if random.random() < detection_chance:
                                    player.being_chased_by_guards = True
                                    logger.warning(f"[STEALTH] {npc_id} detected wanted player! (chance: {detection_chance:.1%})")
                
                # Check enemy detection (for stealth indicator in overworld/dungeons)
                if not in_town:
                    # Create temporary detection list for enemies that can detect player
                    enemy_detections = []
                    for enemy in enemies_list:
                        if not enemy.alive:
                            continue
                        
                        # CRITICAL: Calculate and store offset for each enemy BEFORE detection check
                        enemy_tile_x = int(enemy.rect.centerx // config.TILE_SIZE)
                        enemy_tile_y = int(enemy.rect.centery // config.TILE_SIZE)
                        tilemap_offset_x = max(0, enemy_tile_x - 10)
                        tilemap_offset_y = max(0, enemy_tile_y - 10)
                        
                        enemy.tilemap_offset = (tilemap_offset_x, tilemap_offset_y)
                        
                        # Calculate distance to player in tiles
                        dx = player.x - enemy.rect.centerx
                        dy = player.y - enemy.rect.centery
                        distance_pixels = math.sqrt(dx * dx + dy * dy)
                        distance_tiles = distance_pixels / 50  # TILE_SIZE = 50
                        
                        # Check if enemy can detect player using the proper detection system
                        if hasattr(enemy, 'can_detect_player'):
                            try:
                                can_detect = enemy.can_detect_player(player, tilemap, distance_tiles)
                                if can_detect:
                                    # Calculate detection chance based on distance from max range
                                    effective_range = enemy.calculate_detection_range(player, tilemap)
                                    if effective_range > 0:
                                        # Closer = higher detection chance
                                        detection_chance = 1.0 - (distance_tiles / effective_range)
                                        detection_chance = max(0.3, min(0.95, detection_chance))
                                    else:
                                        detection_chance = 0.5
                                    
                                    enemy_detections.append((getattr(enemy, 'type', 'Enemy'), detection_chance, enemy))
                            except Exception as e:
                                # Fallback: if in aggro state, they can see you
                                if hasattr(enemy, 'state') and enemy.state == 'aggro':
                                    detection_chance = 0.8
                                    enemy_detections.append((getattr(enemy, 'type', 'Enemy'), detection_chance, enemy))
                    
                    player.detected_by_npcs = enemy_detections
            
                # Update fire manager (check expiration, animate fire)
                fire_manager.update(dt, game_time)
                
                # Update chicken pet (following, animation)
                player_moving = (remapped_keys.get(pygame.K_w, False) or 
                                remapped_keys.get(pygame.K_s, False) or 
                                remapped_keys.get(pygame.K_a, False) or 
                                remapped_keys.get(pygame.K_d, False))
                pet_companion.update(dt, player.x, player.y, player_moving)
                
                # Update smoke effects (particles)
                smoke_effect.update(dt)
                
                # OPTIMIZATION: Cache player collision rect when position changes
                if player_pos_cache != (player.x, player.y):
                    cached_player_collision_rect = player.rect.inflate(10, 10)
                    player_pos_cache = (player.x, player.y)
                
                # OPTIMIZATION: Periodic achievement checking (every 3 seconds instead of 1)
                achievement_check_counter += 1
                if achievement_check_counter >= 180:  # 180 frames = 3 seconds at 60fps (reduced frequency)
                    achievement_check_counter = 0
                    # Check exploration achievements (distance-based)
                    achievement_manager.check_all_exploration(
                        player.ach_towns_visited,
                        player.ach_distance_traveled,
                        player.ach_dungeons_entered
                    )
                    unlocked = achievement_manager.get_recent_unlock()
                    if unlocked:
                        achievement_popup.show(unlocked)
                        logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                    
                    # OPTIMIZATION: Cache status multipliers once per frame
                    cached_status_multipliers = player.status_manager.get_stat_multipliers()
                
                # Update enemies (with aggressive cleanup) - only if not paused
                enemies_to_remove = []
                
                # Initialize enemy distance list (empty when paused to prevent attacks)
                alive_enemies_with_distances = []
                
                # Skip enemy updates if game is paused
                if not game_paused:
                    # OPTIMIZATION: Calculate distances for all alive enemies and sort by proximity
                    for enemy in enemies_list:
                        if not enemy.alive:
                            enemies_to_remove.append(enemy)
                            # Create corpse when enemy dies
                            enemy_name = getattr(enemy, 'name', f"{enemy.type.capitalize()}")
                            body_disposal_system.create_corpse(
                                npc_id=id(enemy),
                                name=enemy_name,
                                x=enemy.rect.centerx,
                                y=enemy.rect.centery,
                                cause_of_death="Slain in battle",
                                age=random.randint(5, 30),
                                birth_date="Unknown",
                                inventory={},
                                equipment={}
                            )
                            logger.info(f"[BODY] Created corpse for {enemy_name} at ({enemy.rect.centerx}, {enemy.rect.centery})")
                            # Corpse is now available for necromancy through unified body_disposal_system
                            
                            continue
                        
                        distance_to_player = ((enemy.rect.centerx - player.x)**2 + (enemy.rect.centery - player.y)**2) ** 0.5
                        if distance_to_player <= ENTITY_UPDATE_DISTANCE:
                            alive_enemies_with_distances.append((distance_to_player, enemy))
                
                # Sort by distance (closest first) and limit full AI updates to nearest enemies
                alive_enemies_with_distances.sort(key=lambda x: x[0])
                
                # Update only the nearest MAX_ACTIVE_ENEMY_UPDATES enemies with full AI
                for idx, (distance_to_player, enemy) in enumerate(alive_enemies_with_distances):
                    # CRITICAL: Calculate offset for ALL enemies (even beyond active update limit)
                    # because they still need it for detection checks
                    enemy_tile_x = int(enemy.rect.centerx // config.TILE_SIZE)
                    enemy_tile_y = int(enemy.rect.centery // config.TILE_SIZE)
                    
                    # Cache key based on enemy's tile region
                    cache_key = (enemy_tile_x // 10, enemy_tile_y // 10)
                    
                    # Check if we need to refresh cache
                    if tilemap_cache_frame % TILEMAP_CACHE_LIFETIME == 0 or cache_key not in tilemap_cache:
                        # Create small local tilemap around enemy region
                        local_tilemap = []
                        world_height_tiles = world.height // config.TILE_SIZE
                        world_width_tiles = world.width // config.TILE_SIZE
                        # Calculate tilemap offset for cache creation
                        cache_offset_x = max(0, enemy_tile_x - 10)
                        cache_offset_y = max(0, enemy_tile_y - 10)
                        for ty in range(cache_offset_y, min(world_height_tiles, enemy_tile_y + 11)):
                            row = []
                            for tx in range(cache_offset_x, min(world_width_tiles, enemy_tile_x + 11)):
                                tile = world.get_tile(tx * config.TILE_SIZE, ty * config.TILE_SIZE)
                                # Include all tile properties for line-of-sight checks
                                if tile:
                                    row.append({
                                        "type": tile.get("ground", "grass"),
                                        "ground": tile.get("ground", "grass"),
                                        "object": tile.get("object", "")
                                    })
                                else:
                                    row.append({"type": "grass", "ground": "grass", "object": ""})
                            local_tilemap.append(row)
                        # Store ONLY tilemap array - offset calculated per-enemy
                        tilemap_cache[cache_key] = local_tilemap
                    else:
                        # Retrieve cached tilemap
                        local_tilemap = tilemap_cache.get(cache_key, [])
                    
                    # CRITICAL FIX: Calculate offset for THIS specific enemy, not from cache
                    # This ensures each enemy has correct offset for its position
                    tilemap_offset_x = max(0, enemy_tile_x - 10)
                    tilemap_offset_y = max(0, enemy_tile_y - 10)
                    
                    # Store tilemap offset in enemy for LOS calculations
                    enemy.tilemap_offset = (tilemap_offset_x, tilemap_offset_y)
                    
                    # Skip full AI update for enemies beyond the active limit (but they still have their offset set)
                    if idx >= MAX_ACTIVE_ENEMY_UPDATES:
                        continue
                    
                    # Check if enemy is inside a town zone and push them out
                    for town in town_manager.towns:
                        if town.is_in_town(enemy.rect.centerx, enemy.rect.centery):
                            # Enemy is in town - push them out
                            dx = enemy.rect.centerx - town.center_x
                            dy = enemy.rect.centery - town.center_y
                            distance = (dx * dx + dy * dy) ** 0.5
                            if distance < 1:
                                distance = 1
                            # Push to edge of town + buffer
                            push_distance = town.radius + 100 - distance
                            if push_distance > 0:
                                nx = dx / distance
                                ny = dy / distance
                                enemy.rect.centerx += int(nx * push_distance)
                                enemy.rect.centery += int(ny * push_distance)
                                break
                
                    # Get active companions for threat assessment
                    player_companions = companion_manager.get_employer_companions(player)
                    
                    # Update enemy AI (full update for nearest enemies only)
                    enemy.update(player, local_tilemap, dt=dt, all_enemies=enemies_list,

                                dropped_equipment_list=dropped_equipment_list,
                                companions=player_companions)
                
                # Combat checks: Process ALL alive enemies within range (not just AI-updated ones)
                if len(alive_enemies_with_distances) > 0:
                    print(f"[ENEMY ATTACK] Checking {len(alive_enemies_with_distances)} enemies, game_paused={game_paused}")
                if not player_died and not in_town and not game_paused:  # Enemies can't attack when game is paused
                    # Check if enemies attack player
                    for distance_to_player, enemy in alive_enemies_with_distances:
                        if enemy.state == "aggro" and enemy.rect.colliderect(cached_player_collision_rect):
                            if time.time() - enemy.last_attack_time >= enemy.attack_cooldown:
                                # OPTIMIZATION: Use cached status multipliers
                                multipliers = cached_status_multipliers if cached_status_multipliers is not None else player.status_manager.get_stat_multipliers()
                                
                                # Apply defense multiplier and damage reduction
                                damage = enemy.damage / multipliers["defense"]  # Defense buffs reduce damage
                                damage = damage * (1.0 - multipliers["damage_reduction"])  # Additional flat reduction
                                damage = int(damage)
                                
                                # Check if player dodged (invincibility frames or racial dodge)
                                actual_damage = player.take_damage(damage, attacker=enemy, damage_type='physical')
                                
                                if actual_damage == 0 and player.dodge_invulnerable:
                                    # Player dodged the attack with invincibility frames!
                                    floating_texts.append(DamageNumber(0, (player.x, player.y - 30), is_dodge=True))
                                    logger.info(f"[COMBAT] Player dodged {enemy.rarity} {enemy.type} attack!")
                                elif actual_damage == 0:
                                    # Racial dodge (Halfling Lucky Escape)!
                                    floating_texts.append(DamageNumber(0, (player.x, player.y - 30), is_dodge=True))
                                    logger.info(f"[COMBAT] Player dodged {enemy.rarity} {enemy.type} attack with racial trait!")
                                    # Show special message
                                    town_message = "🍀 Lucky dodge!"
                                    town_message_timer = 90
                                elif actual_damage > 0:
                                    # Damage was taken - add impact effect
                                    floating_texts.append(DamageNumber(actual_damage, (player.x, player.y - 30), is_crit=False))
                                    combat_particles.add_hit_impact((player.x, player.y - 10), is_crit=False, impact_type="normal")
                                    enemy.last_attack_time = time.time()
                                    logger.info(f"[COMBAT] {enemy.rarity} {enemy.type} hit player for {actual_damage} damage!")
                                
                                # OPTIMIZATION: Degrade equipped armor only when repair system is enabled
                                if actual_damage > 0 and repair_system.enabled and hasattr(player, 'equipment'):
                                    repair_skill = 1 if (hasattr(player, 'acquired_skills') and 'repair_mastery' in player.acquired_skills) else 0
                                    # Check all armor slots for degradation
                                    for slot in ['head', 'chest', 'legs', 'feet', 'hands', 'off_hand']:
                                        item = player.equipment.get(slot)
                                        if item and hasattr(item, 'durability'):
                                            item_rarity = getattr(item, 'rarity', 'common')
                                            repair_system.degrade_equipment(item, item_rarity, repair_skill)
                                
                                # Check if player died
                                # Skip death check if save/load UI is active
                                if player.health <= 0 and not player_died and not save_integrator.ui.active:
                                    # Check Halfling death dodge (only in dungeons)
                                    dodged_death = False
                                    if hasattr(player, 'trait_manager') and player.trait_manager:
                                        dodged_death = player.trait_manager.check_death_dodge(in_dungeon=in_dungeon)
                                    
                                    if dodged_death:
                                        player.health = player.max_health * 0.25  # Restore to 25% health
                                        logger.info("[TRAIT] Halfling Lucky Escape! Death dodged in dungeon!")
                                        town_message = "🍀 Lucky Escape! You narrowly avoided death!"
                                        town_message_timer = 180
                                    else:
                                        player_died = True
                                        player.health = 0  # Ensure health doesn't go negative
                                        show_death_screen = True
                                        death_screen_option = 0
                                        logger.warning("[DEATH] Player has died!")
                                        
                                        # Track death for achievements
                                        player.ach_deaths += 1
                        
                    # Check if gatherer NPCs attack player (only if player is alive and game not paused)
                    print(f"[NPC ATTACK] Checking gatherer NPCs, player_died={player_died}, game_paused={game_paused}")
                    if not player_died and not game_paused:
                        for gatherer_npc in gatherer_npc_manager.npcs:
                            if gatherer_npc.combat_target == player and not gatherer_npc.is_recovering:
                                # Check if in range
                                distance = math.sqrt((gatherer_npc.x - player.x)**2 + (gatherer_npc.y - player.y)**2)
                                if distance <= gatherer_npc.attack_range:
                                    # Try to attack (respects cooldown internally)
                                    if gatherer_npc.attack_target(player, time.time()):
                                        logger.info(f"[COMBAT] {gatherer_npc.name} attacked player for {gatherer_npc.get_damage()} damage!")
                        
                        # Check if tutorial NPC attacks player (if provoked)
                        if hasattr(player, 'tutorial_npc') and player.tutorial_npc:
                            tutorial_npc = player.tutorial_npc
                            # Only process combat if NPC is in same location as player
                            npc_accessible = False
                            if hasattr(tutorial_npc, 'in_building') and tutorial_npc.in_building:
                                # NPC in building - check if player is in same building
                                if in_building_interior and current_interior_building_id == tutorial_npc.in_building:
                                    npc_accessible = True
                            else:
                                # NPC in overworld
                                if not in_building_interior:
                                    npc_accessible = True
                            
                            if npc_accessible and tutorial_npc.combat_target == player:
                                # Check if in range
                                distance = math.sqrt((tutorial_npc.x - player.x)**2 + (tutorial_npc.y - player.y)**2)
                                if distance <= tutorial_npc.attack_range:
                                    # Try to attack (respects cooldown internally)
                                    if tutorial_npc.attack_target(player, time.time()):
                                        # Add floating damage number
                                        floating_texts.append(DamageNumber(tutorial_npc.damage, (player.x, player.y - 20), is_crit=False))
                                        # Add to combat log
                                        combat_log.add_damage(tutorial_npc.name, "You", tutorial_npc.damage, is_crit=False)
                                        logger.info(f"[COMBAT] {tutorial_npc.name} attacked player for {tutorial_npc.damage} damage!")
            else:
                # Game is paused - skip all enemy updates and combat
                pass
            
            # Handle magic attacks with right-click (only if player is alive and not in dialogue)
            if not player_died and not dialogue_ui.active and combat_mouse_buttons.get(MOUSE_RIGHT, False):
                # Right-click to cast magic
                if hasattr(player, 'secondary_spell') and player.secondary_spell:
                    # Get mouse position for targeting
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    target_x = mouse_x + camera_x
                    target_y = mouse_y + camera_y
                    
                    # Cast the spell
                    spell_result = player.cast_spell(player.secondary_spell, target_x, target_y)
                    if spell_result:
                        # Get spell data
                        if player.secondary_spell in SPELLS:
                            spell_data = SPELLS[player.secondary_spell]
                            spell_type = spell_data.get('type', 'projectile')
                            logger.info(f"[SPELL] Cast {player.secondary_spell} at ({target_x}, {target_y})")
                            
                            # Handle different spell types
                            if spell_type == 'summon':
                                summon_type_str = spell_data.get('summon_type', 'wolf')
                                duration = spell_data.get('summon_duration', 30)
                                summon_type = SummonType[summon_type_str.upper()]
                                companion_manager.add_summon(
                                    summon_type, target_x, target_y, duration, player
                                )
                            elif spell_type == 'projectile':
                                # Add projectile to list
                                spell_projectiles.append(spell_result)
                            elif spell_type in ['instant', 'self']:
                                # Execute instant spell and create visual effect
                                from spell_projectile import SpellEffect, InstantSpell
                                if isinstance(spell_result, InstantSpell) and hasattr(spell_result, 'execute'):
                                    spell_result.execute(player, enemies_list)
                                effect_color = (100, 255, 100) if spell_type == 'self' else (255, 255, 100)
                                effect = SpellEffect(player.x, player.y, player.secondary_spell, effect_color)
                                spell_effects.append(effect)
                else:
                    # No spell equipped
                    town_message = "No magic spell equipped! Press 'B' to select a spell"
                    town_message_timer = 90
            
            # Check if player attacks enemy or gatherer NPC (only if player is alive and not in dialogue)
            if not player_died and not dialogue_ui.active:
                attack_keys = key_bindings.get_keys_for_action("attack")
                # Physical attack: check for spacebar or left-click (not right-click)
                attack_pressed = False
                for k in attack_keys:
                    if k is not None and k != MOUSE_RIGHT:  # Exclude right-click (magic attack)
                        if remapped_keys.get(k, False):
                            attack_pressed = True
                            break  # Found a pressed attack key, stop searching
                
                if attack_pressed:  # Physical attack key or left-click
                    attack_range = 60
                    
                    # First check if attacking the tutorial NPC
                    tutorial_npc_hit = False
                    if hasattr(player, 'tutorial_npc') and player.tutorial_npc:
                        tutorial_npc = player.tutorial_npc
                        # Only allow attack if NPC is in same location as player
                        npc_accessible = False
                        if hasattr(tutorial_npc, 'in_building') and tutorial_npc.in_building:
                            # NPC in building - check if player is in same building
                            if in_building_interior and current_interior_building_id == tutorial_npc.in_building:
                                npc_accessible = True
                        else:
                            # NPC in overworld
                            if not in_building_interior:
                                npc_accessible = True
                        
                        if npc_accessible:
                            tutorial_npc_rect = pygame.Rect(tutorial_npc.x - tutorial_npc.size//2, 
                                                           tutorial_npc.y - tutorial_npc.size//2, 
                                                           tutorial_npc.size, 
                                                           tutorial_npc.size)
                            if tutorial_npc_rect.colliderect(player.rect.inflate(attack_range, attack_range)):
                                attack_cooldown = player.get_attack_cooldown()
                                if time.time() - player.last_attack_time >= attack_cooldown:
                                    # Calculate player damage
                                    multipliers = cached_status_multipliers if cached_status_multipliers is not None else player.status_manager.get_stat_multipliers()
                                    player_damage = 20 + (player.level * 5)
                                    player_damage = int(player_damage * multipliers["damage"])
                                    
                                    # Add weapon damage
                                    equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
                                    if equipped_weapon:
                                        if hasattr(equipped_weapon, 'damage'):
                                            player_damage += equipped_weapon.damage
                                        elif hasattr(equipped_weapon, 'stats') and 'damage' in equipped_weapon.stats:
                                            player_damage += int(equipped_weapon.stats['damage'])
                                    
                                    # Attack tutorial NPC (make it fight back)
                                    tutorial_npc.take_damage(player_damage, attacker=player)
                                    player.last_attack_time = time.time()
                                    logger.info(f"[COMBAT] Player attacked {tutorial_npc.name} for {player_damage} damage (HP: {tutorial_npc.health}/{tutorial_npc.max_health})")
                                    
                                    # Add floating damage number
                                    floating_texts.append(DamageNumber(player_damage, (tutorial_npc.x, tutorial_npc.y - 20), is_crit=False))
                                    
                                    # Add to combat log
                                    combat_log.add_damage("You", tutorial_npc.name, player_damage, is_crit=False)
                                    
                                    # Check if NPC died
                                    if tutorial_npc.health <= 0:
                                        logger.info(f"[COMBAT] Killed {tutorial_npc.name}!")
                                        town_message = "The Wandering Guide falls, clutching his compass. 'May you... never lose your way...' he whispers before fading."
                                        town_message_timer = 300
                                        
                                        # === LOOT DROPS ===
                                        import random
                                        from equipment import EQUIPMENT_DATA
                                        
                                        # Always drop gold and experience
                                        gold_drop = random.randint(150, 250)
                                        xp_drop = random.randint(200, 300)
                                        player.inventory['Gold'] = player.inventory.get('Gold', 0) + gold_drop
                                        player.experience += xp_drop
                                        logger.info(f"[LOOT] Dropped {gold_drop} gold and {xp_drop} XP")
                                        
                                        # Common supplies (always drops)
                                        player.inventory['Bread'] = player.inventory.get('Bread', 0) + 1
                                        player.inventory['Water'] = player.inventory.get('Water', 0) + 1
                                        player.inventory['Basic Healing Herbs'] = player.inventory.get('Basic Healing Herbs', 0) + 1
                                        logger.info("[LOOT] Dropped common supplies")
                                        
                                        # Legendary drops (8% chance for EACH item)
                                        legendary_drops = []
                                        if random.random() < 0.08:  # 8% chance
                                            from item import Item
                                            compass_item = Item("Guide's Compass", "accessory", stats={'charisma': 5, 'willpower': 3})
                                            player.add_item(compass_item)
                                            legendary_drops.append("Guide's Compass")
                                            logger.info("[LOOT] LEGENDARY DROP: Guide's Compass!")
                                        
                                        if random.random() < 0.08:  # 8% chance
                                            from item import Item
                                            staff_item = Item("Wayfarer's Staff", "weapon", stats={'damage': 18, 'magic_damage': 5, 'stamina': 5, 'dexterity': 3})
                                            player.add_item(staff_item)
                                            legendary_drops.append("Wayfarer's Staff")
                                            logger.info("[LOOT] LEGENDARY DROP: Wayfarer's Staff!")
                                        
                                        # Alternative legendary drops (8% chance for EACH)
                                        if random.random() < 0.08:  # 8% chance
                                            from item import Item
                                            badge_item = Item("Tutorial Master's Badge", "accessory", stats={'willpower': 3, 'charisma': 2})
                                            player.add_item(badge_item)
                                            legendary_drops.append("Tutorial Master's Badge")
                                            logger.info("[LOOT] LEGENDARY DROP: Tutorial Master's Badge!")
                                        
                                        if random.random() < 0.08:  # 8% chance
                                            from item import Item
                                            map_item = Item("Map of the Ancients", "consumable", stats={})
                                            player.add_item(map_item)
                                            legendary_drops.append("Map of the Ancients")
                                            logger.info("[LOOT] LEGENDARY DROP: Map of the Ancients!")
                                        
                                        # Epic/Rare drops (12% chance for category)
                                        if random.random() < 0.12:  # 12% chance to get this category
                                            # Then 10% for cloak, 15% for potions
                                            if random.random() < 0.10:  # 10% within category
                                                from item import Item
                                                cloak_item = Item("Traveler's Cloak", "armor", stats={'defense': 10, 'charisma': 5, 'agility': 2})
                                                player.add_item(cloak_item)
                                                logger.info("[LOOT] EPIC DROP: Traveler's Cloak!")
                                            elif random.random() < 0.15:  # 15% within category
                                                potion_count = random.randint(3, 5)
                                                player.inventory['Health Potion'] = player.inventory.get('Health Potion', 0) + potion_count
                                                logger.info(f"[LOOT] RARE DROP: {potion_count} Health Potions!")
                                        
                                        # Show loot message
                                        if legendary_drops:
                                            town_message += f"\\n\\n✨ LEGENDARY DROPS: {', '.join(legendary_drops)}!"
                                            town_message_timer = 450
                                        
                                        # === REPUTATION LOSS ===
                                        reputation_system.modify_faction_reputation("Travelers Guild", -50)
                                        logger.info("[REPUTATION] -50 reputation with Travelers Guild for killing the Wandering Guide")
                                        
                                        # === ACHIEVEMENT UNLOCK ===
                                        achievement_manager.check_achievement("special_kill_tutorial", 1)
                                        
                                        # Remove NPC permanently (no respawn)
                                        player.tutorial_npc = None
                                    
                                    tutorial_npc_hit = True
                    
                    # Then check if attacking a gatherer NPC
                    gatherer_npc_hit = False
                    enemy_hit = False
                    if not tutorial_npc_hit:
                        for gatherer_npc in gatherer_npc_manager.npcs:
                            if gatherer_npc.rect.colliderect(player.rect.inflate(attack_range, attack_range)):
                                # Use player's dynamic attack cooldown based on weapon
                                attack_cooldown = player.get_attack_cooldown()
                                time_since_last_attack = time.time() - player.last_attack_time
                                logger.info(f"[COMBAT DEBUG] Attack attempt on NPC: cooldown={attack_cooldown:.2f}s, time_since_last={time_since_last_attack:.2f}s, can_attack={time_since_last_attack >= attack_cooldown}")
                                if time.time() - player.last_attack_time >= attack_cooldown:
                                    if not gatherer_npc.is_recovering:
                                        # Calculate player damage
                                        multipliers = cached_status_multipliers if cached_status_multipliers is not None else player.status_manager.get_stat_multipliers()
                                        player_damage = 20 + (player.level * 5)  # Base damage scales with level
                                        player_damage = int(player_damage * multipliers["damage"])
                                        
                                        # Add weapon damage
                                        equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
                                        if equipped_weapon:
                                            if hasattr(equipped_weapon, 'damage'):
                                                player_damage += equipped_weapon.damage
                                            elif hasattr(equipped_weapon, 'stats') and 'damage' in equipped_weapon.stats:
                                                # For stick weapons that use stats dict
                                                player_damage += int(equipped_weapon.stats['damage'])
                                        
                                        # Attack gatherer NPC
                                        gatherer_npc.take_damage(player_damage, player)
                                        player.last_attack_time = time.time()
                                        logger.info(f"[COMBAT] Player attacked {gatherer_npc.name} for {player_damage} damage (HP: {gatherer_npc.health}/{gatherer_npc.max_health}) - last_attack_time updated to {player.last_attack_time:.2f}")
                                        
                                        # Add floating damage number
                                        floating_texts.append(DamageNumber(player_damage, (gatherer_npc.x, gatherer_npc.y - 20), is_crit=False))
                                        
                                        # Add to combat log
                                        combat_log.add_damage("You", gatherer_npc.name, player_damage, is_crit=False)
                                        
                                        # Check if NPC died (items already dropped by die() method)
                                        if gatherer_npc.health <= 0:
                                            logger.info(f"[COMBAT] Defeated {gatherer_npc.name}! Permanent death.")
                                            
                                            # Player loots defeated NPC
                                            looted = NPCLootingSystem.loot_defeated_npc(player, gatherer_npc)
                                            
                                            # Add loot value to companion earnings (30%)
                                            player_companions = companion_manager.get_employer_companions(player)
                                            if player_companions:
                                                loot_value = NPCLootingSystem.calculate_loot_value(looted)
                                                for companion in player_companions:
                                                    companion.add_earnings(loot_value / len(player_companions))
                                            
                                            # Register vacant role for adaptation
                                            if hasattr(gatherer_npc, 'gatherer_type'):
                                                npc_role_adaptation.register_vacant_role(
                                                    gatherer_npc.gatherer_type, gatherer_npc.town, "combat_death"
                                                )
                                            
                                            # Create corpse for NPC
                                            npc_age = getattr(gatherer_npc, 'age', random.randint(20, 60))
                                            npc_birth = getattr(gatherer_npc, 'birth_date', "Unknown")
                                            body_disposal_system.create_corpse(
                                                npc_id=id(gatherer_npc),
                                                name=gatherer_npc.name,
                                                x=gatherer_npc.x,
                                                y=gatherer_npc.y,
                                                cause_of_death="Slain by player",
                                                age=npc_age,
                                                birth_date=npc_birth,
                                                inventory={},  # Already looted
                                                equipment=getattr(gatherer_npc, 'equipment', {})
                                            )
                                            logger.info(f"[BODY] Created corpse for {gatherer_npc.name} at ({gatherer_npc.x}, {gatherer_npc.y})")
                                            
                                            # Record death for newspaper obituaries
                                            npc_type = getattr(gatherer_npc, 'gatherer_type', 'resident')
                                            newspaper_generator.record_death(
                                                gatherer_npc.name,
                                                npc_type,
                                                gatherer_npc.town,
                                                "combat_death",
                                                npc_age
                                            )
                                            
                                            # PERMADEATH - remove from manager
                                            gatherer_npc_manager.npcs.remove(gatherer_npc)
                                            logger.info(f"[PERMADEATH] {gatherer_npc.name} permanently removed from game")
                                            
                                            # Start investigation if near a town
                                            if in_town and current_town_instance:
                                                # Check for witnesses (other NPCs nearby)
                                                witnessed = False
                                                witness_name = None
                                                witness_distance = 200  # Detection radius
                                                
                                                for other_npc in gatherer_npc_manager.npcs:
                                                    if other_npc != gatherer_npc and other_npc.health > 0:
                                                        dist = ((other_npc.x - player.x) ** 2 + (other_npc.y - player.y) ** 2) ** 0.5
                                                        if dist <= witness_distance:
                                                            witnessed = True
                                                            witness_name = other_npc.name if hasattr(other_npc, 'name') else "Someone"
                                                            break
                                                
                                                body_id = f"gatherer_{gatherer_npc.name}_{game_time.day_count}"
                                                investigation_system.start_investigation(
                                                    body_id, 
                                                    id(player), 
                                                    game_time,
                                                    victim_name=gatherer_npc.name,
                                                    location=current_town_instance.name,
                                                    witnessed=witnessed
                                                )
                                                logger.warning(f"[INVESTIGATION] Started investigation for death of {gatherer_npc.name} in {current_town_instance.name} (Witnessed: {witnessed})")
                                                
                                                # Instant massive bounty if witnessed murder
                                                if witnessed:
                                                    murder_bounty = 300  # Even higher for witnessed
                                                    player.wanted_level += murder_bounty
                                                    player.is_wanted = True
                                                    wanted_system.set_wanted(id(player), 'murder', game_time)
                                                    
                                                    # Massive reputation loss for witnessed murder
                                                    reputation_system.modify_faction_reputation(current_town_instance.name, -100)
                                                    logger.info(f"[REPUTATION] Lost 100 reputation with {current_town_instance.name} for murder")
                                                    
                                                    town_message = f"🔪 You killed {gatherer_npc.name}!\n👁️ {witness_name} SAW EVERYTHING!\n🚨 WANTED FOR MURDER! Bounty: +{murder_bounty}g\n(Total: {player.wanted_level}g)"
                                                    town_message_timer = 480
                                                else:
                                                    # Reputation loss for unwitnessed murder (discovered later)
                                                    reputation_system.modify_faction_reputation(current_town_instance.name, -75)
                                                    logger.info(f"[REPUTATION] Lost 75 reputation with {current_town_instance.name} for murder")
                                                    
                                                    town_message = f"🔪 You killed {gatherer_npc.name}!\n⚠️ Investigation started...\nAuthorities will investigate in 1 day."
                                                    town_message_timer = 360
                                                
                                                # Record the crime with criminal rank system
                                                record_crime_with_rank(
                                                    crime_type='murder',
                                                    location=current_town_instance.name,
                                                    witnessed=witnessed,
                                                    witness=witness_name if witnessed else None
                                                )
                                    else:
                                        logger.debug(f"[COMBAT] {gatherer_npc.name} is recovering and cannot be attacked.")
                                    gatherer_npc_hit = True
                                    break
                    
                    # Only check enemies if didn't hit a gatherer NPC
                    if not gatherer_npc_hit:
                        for distance_to_player, enemy in alive_enemies_with_distances:
                            if enemy.rect.colliderect(player.rect.inflate(attack_range, attack_range)):
                                # Use player's dynamic attack cooldown based on weapon
                                attack_cooldown = player.get_attack_cooldown()
                                time_since_last_attack = time.time() - player.last_attack_time
                                logger.info(f"[COMBAT] Attack attempt: cooldown={attack_cooldown:.2f}s, time_since_last={time_since_last_attack:.2f}s, can_attack={time_since_last_attack >= attack_cooldown}")
                                if time.time() - player.last_attack_time >= attack_cooldown:
                                    # Calculate critical hit chance (base 10% + player stats)
                                    crit_chance = 0.10  # Base 10% crit chance
                                    
                                    # Apply racial crit bonus (Halfling: +5%)
                                    if hasattr(player, 'trait_manager') and player.trait_manager:
                                        crit_chance += player.trait_manager.get_critical_hit_bonus()
                                    
                                    is_critical = random.random() < crit_chance
                                    
                                    # OPTIMIZATION: Use cached status multipliers
                                    multipliers = cached_status_multipliers if cached_status_multipliers is not None else player.status_manager.get_stat_multipliers()
                                    
                                    player_damage = 20 + (player.level * 5)  # Base damage scales with level
                                    player_damage = int(player_damage * multipliers["damage"])  # Apply damage buffs
                                    
                                    # Add weapon damage
                                    equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
                                    if equipped_weapon:
                                        if hasattr(equipped_weapon, 'damage'):
                                            player_damage += equipped_weapon.damage
                                        elif hasattr(equipped_weapon, 'stats') and 'damage' in equipped_weapon.stats:
                                            # For stick weapons that use stats dict
                                            player_damage += int(equipped_weapon.stats['damage'])
                                    
                                    if is_critical:
                                        player_damage = int(player_damage * 1.5)  # 50% bonus damage
                                        logger.info(f"[COMBAT] CRITICAL HIT!")
                                        # Activate hit-stop for critical hits
                                        hit_stop_active = True
                                        hit_stop_duration = 0.15  # 150ms freeze
                                        hit_stop_timer = 0.0
                                    
                                    # Get weapon type for slash effect
                                    weapon_type = "sword"  # Default
                                    weapon_color = (255, 255, 255)
                                    if equipped_weapon:
                                        weapon_name = getattr(equipped_weapon, 'name', '').lower()
                                        if 'axe' in weapon_name:
                                            weapon_type = "axe"
                                            weapon_color = (200, 100, 50)
                                        elif 'dagger' in weapon_name or 'knife' in weapon_name:
                                            weapon_type = "dagger"
                                            weapon_color = (180, 180, 255)
                                        elif 'hammer' in weapon_name or 'mace' in weapon_name:
                                            weapon_type = "hammer"
                                            weapon_color = (150, 150, 150)
                                        elif 'spear' in weapon_name or 'pike' in weapon_name:
                                            weapon_type = "spear"
                                            weapon_color = (200, 150, 100)
                                    
                                    # Calculate attack direction
                                    dx = enemy.rect.centerx - player.x
                                    dy = enemy.rect.centery - player.y
                                    attack_direction = math.atan2(dy, dx)
                                    
                                    # Add weapon slash effect
                                    combat_particles.add_weapon_slash(weapon_type, (player.x, player.y), 
                                                                     attack_direction, weapon_color)
                                    
                                    # Degrade weapon on critical hit
                                    if is_critical and repair_system.enabled and hasattr(player, 'equipment'):
                                        repair_skill = 1 if (hasattr(player, 'acquired_skills') and 'repair_mastery' in player.acquired_skills) else 0
                                        weapon_slot = 'weapon' if 'weapon' in player.equipment else 'main_hand'
                                        if weapon_slot in player.equipment and player.equipment[weapon_slot]:
                                            weapon = player.equipment[weapon_slot]
                                            if hasattr(weapon, 'durability'):
                                                weapon_rarity = getattr(weapon, 'rarity', 'common')
                                                repair_system.degrade_equipment(weapon, weapon_rarity, repair_skill)
                                    
                                    # Add floating damage number
                                    floating_texts.append(DamageNumber(player_damage, (enemy.rect.centerx, enemy.rect.top - 20), is_crit=is_critical))
                                    
                                    # Add hit impact effect
                                    impact_type = "heavy" if weapon_type in ["hammer", "axe"] else "normal"
                                    combat_particles.add_hit_impact((enemy.rect.centerx, enemy.rect.centery), 
                                                                   is_crit=is_critical, impact_type=impact_type)
                                    
                                    enemy.take_damage(player_damage, player=player, all_enemies=enemies_list,
                                                    dropped_equipment_list=dropped_equipment_list, floating_texts=floating_texts)
                                    player.last_attack_time = time.time()
                                    logger.info(f"[COMBAT] Player attacked enemy for {player_damage} damage - last_attack_time updated to {player.last_attack_time:.2f}")
                                    
                                    # Add to combat log with weapon type
                                    enemy_name = f"{enemy.rarity} {enemy.type}" if enemy.rarity != "Common" else enemy.type.title()
                                    combat_log.add_damage("You", enemy_name, player_damage, 
                                                        is_crit=is_critical, weapon_type=weapon_type)
                                    
                                    if not enemy.alive:
                                        # Enemy died - give XP and drops
                                        xp_reward = enemy.xp_reward
                                        
                                        # Apply racial XP multiplier (Human: +5% all XP)
                                        if hasattr(player, 'trait_manager') and player.trait_manager:
                                            xp_reward = player.trait_manager.apply_xp_modifier(xp_reward, 'combat')
                                        
                                        player.xp += int(xp_reward)
                                        logger.info(f"[COMBAT] Killed {enemy.rarity} {enemy.type}! +{int(xp_reward)} XP")
                                        
                                        # Check for Halfling double loot
                                        loot_multiplier = 1
                                        if hasattr(player, 'trait_manager') and player.trait_manager:
                                            if player.trait_manager.check_double_loot():
                                                loot_multiplier = 2
                                                town_message = "🍀 Lucky! Double loot!"
                                                town_message_timer = 120
                                        
                                        # Add kill to combat log
                                        combat_log.add_kill("You", enemy_name, enemy.xp_reward)
                                        # Corpse is now available for necromancy through unified body_disposal_system
                                        
                                        # Track achievement stats
                                        player.ach_enemies_killed += 1
                                        
                                        # Record kill in bestiary
                                        bestiary.record_kill(enemy.type, enemy.rarity)
                                        
                                        # Check combat achievements
                                        achievement_manager.check_all_combat(player.ach_enemies_killed, player.level)
                                        unlocked = achievement_manager.get_recent_unlock()
                                        if unlocked:
                                            achievement_popup.show(unlocked)
                                            logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                                        
                                        # CRITICAL FIX: Check if boss was defeated in dungeon
                                        if in_dungeon and current_dungeon and hasattr(enemy, 'is_boss') and enemy.is_boss:
                                            current_dungeon.cleared = True
                                            current_dungeon.last_cleared_day = game_time.day
                                            logger.info(f"🎉 DUNGEON CLEARED! Boss {enemy.type} defeated!")
                                            level_up_message = f"DUNGEON CLEARED! Boss defeated!"
                                            level_up_timer = 240  # Show for 4 seconds
                                        
                                        # Update quest objectives for kill quests
                                        completed_quests = quest_manager.update_objective(ObjectiveType.KILL, enemy.type, 1)
                                        
                                        # Track tutorial quest progress
                                        if player.tutorial_active and 'tutorial_basics' in quest_manager.active_quests:
                                            player.tutorial_enemies_killed += 1
                                            if player.tutorial_enemies_killed >= 2:
                                                player.tutorial_stage = 'combat_complete'
                                                logger.info("[TUTORIAL] Combat objective complete!")
                                        
                                        for quest_name in completed_quests:
                                            logger.info(f"[QUEST] Quest completed: {quest_name}")
                                            
                                            # Reputation bonus for completing quests
                                            if in_town and current_town_instance:
                                                reputation_system.modify_faction_reputation(current_town_instance.name, 50)
                                                logger.info(f"[REPUTATION] Gained 50 reputation with {current_town_instance.name} for quest completion")
                                            
                                            # Track quest completion for achievements
                                            player.ach_quests_completed += 1
                                            achievement_manager.check_all_quests(player.ach_quests_completed)
                                            unlocked = achievement_manager.get_recent_unlock()
                                            if unlocked:
                                                achievement_popup.show(unlocked)
                                                logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                                        
                                        # Check for level up
                                        if player.check_level_up():
                                            # Show level up notification
                                            level_up_message = f"LEVEL UP! Now Level {player.level}!"
                                            level_up_timer = 180  # Show for 3 seconds at 60fps
                                            
                                            # Check deathless achievement (reach level 15 without dying)
                                            if player.ach_deaths == 0:
                                                achievement_manager.check_special(0, player.level)
                                                unlocked = achievement_manager.get_recent_unlock()
                                                if unlocked:
                                                    achievement_popup.show(unlocked)
                                                    logger.info(f"[ACHIEVEMENT] Unlocked: {unlocked.name}")
                                        
                                        # Handle loot drops
                                        class SimpleMessageList:
                                            def __init__(self):
                                                self.messages = []
                                            def add_message(self, msg):
                                                self.messages.append((msg, time.time()))
                                                logger.info(f"[LOOT] {msg}")
                                            def append(self, msg_tuple):
                                                self.messages.append(msg_tuple)
                                                logger.info(f"[LOOT] {msg_tuple[0]}")
                                        
                                        messages = SimpleMessageList()
                                        handle_enemy_drops(enemy, player, messages, dropped_equipment_list)
                                        enemy_hit = True
                                        break  # Only attack one enemy per key press
                                    else:
                                        logger.debug(f"[COMBAT] Hit {enemy.rarity} {enemy.type} for {player_damage} damage! ({enemy.health}/{enemy.max_health} HP)")
                                        enemy_hit = True
                                        break  # Only attack one enemy per key press
                    
                    # If no enemies or NPCs were hit, try to break tiles
                    if not gatherer_npc_hit and not enemy_hit:
                        prev_stick_count = player.inventory.get('stick', 0)
                        player.break_tile(world=world)
                        # Update quest for stick collection
                        new_stick_count = player.inventory.get('stick', 0)
                        if new_stick_count > prev_stick_count:
                            sticks_gained = new_stick_count - prev_stick_count
                            if player.tutorial_active and 'tutorial_basics' in quest_manager.active_quests:
                                quest_manager.update_objective(ObjectiveType.COLLECT, "stick", sticks_gained)
                                print(f"[QUEST UPDATE] Added {sticks_gained} stick(s) to quest progress")
            
            # OPTIMIZATION: Clean up dead enemies in batch
            enemies_list = [enemy for enemy in enemies_list if enemy.alive]
            
            # OPTIMIZATION: Remove enemies that are too far away (> 2500 pixels)
            # This prevents the list from growing unbounded as enemies wander off
            enemies_list = [enemy for enemy in enemies_list 
                          if ((enemy.rect.centerx - player.x)**2 + (enemy.rect.centery - player.y)**2) < 2500**2]
            
            # OPTIMIZATION: Limit dropped equipment to 50 items max (remove oldest)
            if len(dropped_equipment_list) > 50:
                dropped_equipment_list = dropped_equipment_list[-50:]
            
            # Auto-loot system: automatically pick up items based on rarity filter
            if auto_loot_enabled:
                auto_pickup_range = 100  # pixels
                for dropped in dropped_equipment_list[:]:
                    if hasattr(dropped, "rect"):
                        distance = math.sqrt((dropped.rect.centerx - player.x)**2 + (dropped.rect.centery - player.y)**2)
                        
                        if distance <= auto_pickup_range:
                            # Check if item meets rarity filter
                            item_rarity = getattr(dropped, 'rarity', 'common')
                            
                            if should_auto_loot(item_rarity, auto_loot_min_rarity):
                                # Auto-pickup the item (same logic as manual pickup)
                                if hasattr(dropped, "amount"):  # Dubloons
                                    player.dubloons = getattr(player, "dubloons", 0) + dropped.amount
                                    logger.info(f"[AUTO-LOOT] Picked up {dropped.amount} dubloons!")
                                    dropped_equipment_list.remove(dropped)
                                elif hasattr(dropped, "equipment_id"):  # Dropped equipment
                                    from item import Item
                                    equipment_data = dropped.data
                                    
                                    # Build stats dict for the Item
                                    item_stats = {}
                                    if 'base_damage' in equipment_data:
                                        item_stats['damage'] = equipment_data['base_damage']
                                    # Check both 'defense' and 'base_defense' field names
                                    if 'defense' in equipment_data:
                                        item_stats['Defense'] = equipment_data['defense']
                                    elif 'base_defense' in equipment_data:
                                        item_stats['Defense'] = equipment_data['base_defense']
                                    # Add stat bonuses (combine with existing stats, not overwrite)
                                    if 'stat_bonuses' in equipment_data:
                                        for stat_name, stat_value in equipment_data['stat_bonuses'].items():
                                            if stat_name in item_stats:
                                                item_stats[stat_name] += stat_value  # Add to existing
                                            else:
                                                item_stats[stat_name] = stat_value  # Create new
                                    
                                    # Create Item object
                                    equipment_item = Item(
                                        name=equipment_data['name'],
                                        item_type=equipment_data.get('type', 'weapon'),
                                        stats=item_stats,
                                        durability=equipment_data.get('durability', 100),
                                        max_durability=equipment_data.get('durability', 100)
                                    )
                                    
                                    # Add rarity attribute
                                    if hasattr(dropped, 'rarity'):
                                        equipment_item.rarity = dropped.rarity
                                    
                                    player.add_item(equipment_item)
                                    logger.info(f"[AUTO-LOOT] Picked up {equipment_data['name']} ({item_rarity})!")
                                    dropped_equipment_list.remove(dropped)
            
            # Update dropped equipment (items on ground)
            for dropped in dropped_equipment_list[:]:
                # Check if player picks up item
                if hasattr(dropped, "rect") and dropped.rect.colliderect(player.rect):
                    # Add to inventory
                    if hasattr(dropped, "amount"):  # Dubloons
                        player.dubloons = getattr(player, "dubloons", 0) + dropped.amount
                        icon = get_item_icon('dubloon')
                        logger.info(f"[PICKUP] Picked up {dropped.amount} dubloons!")
                    elif hasattr(dropped, "equipment_id"):  # Dropped equipment
                        # Create an Item object from the DroppedEquipment data
                        from item import Item
                        equipment_data = dropped.data
                        
                        icon = get_item_icon(dropped.equipment_id)
                        logger.info(f"[PICKUP] Dropped equipment_id: {dropped.equipment_id}")
                        
                        # Build stats dict for the Item
                        item_stats = {}
                        if 'base_damage' in equipment_data:
                            item_stats['damage'] = equipment_data['base_damage']
                        # Check both 'defense' and 'base_defense' field names
                        if 'defense' in equipment_data:
                            item_stats['Defense'] = equipment_data['defense']
                        elif 'base_defense' in equipment_data:
                            item_stats['Defense'] = equipment_data['base_defense']
                        # Add stat bonuses (combine with existing stats, not overwrite)
                        if 'stat_bonuses' in equipment_data:
                            for stat_name, stat_value in equipment_data['stat_bonuses'].items():
                                if stat_name in item_stats:
                                    item_stats[stat_name] += stat_value  # Add to existing
                                else:
                                    item_stats[stat_name] = stat_value  # Create new
                        
                        # Create Item object
                        equipment_item = Item(
                            name=equipment_data['name'],
                            item_type=equipment_data.get('type', 'weapon'),
                            stats=item_stats,
                            durability=equipment_data.get('durability', 100),
                            max_durability=equipment_data.get('durability', 100)
                        )
                        
                        # Add to inventory
                        player.add_item(equipment_item)
                        logger.info(f"[PICKUP] Picked up {equipment_data['name']} ({dropped.rarity})!")
                    elif hasattr(dropped, "item"):  # Item object (legacy)
                        item_name = getattr(dropped.item, "name", "item")
                        player.add_item(dropped.item)
                        logger.info(f"[PICKUP] Picked up {item_name}!")
                    else:  # Other items (fallback to legacy system)
                        # Try multiple attributes to find the item name
                        item_name = getattr(dropped, "item_type", None) or getattr(dropped, "type", None) or getattr(dropped, "name", None) or getattr(dropped, "item_id", "item")
                        # Add to player inventory as count
                        player.inventory[item_name] = player.inventory.get(item_name, 0) + 1
                        logger.info(f"[PICKUP] Picked up {item_name}!")
                    dropped_equipment_list.remove(dropped)
            
            # Update spell projectiles with memory leak protection
            for projectile in spell_projectiles[:]:
                if projectile.alive:
                    projectile.update(dt, enemies_list, player)
                else:
                    spell_projectiles.remove(projectile)
            
            # OPTIMIZATION: Enforce maximum projectile limit to prevent memory leaks
            # Remove oldest projectiles if list grows too large
            MAX_PROJECTILES = 100
            if len(spell_projectiles) > MAX_PROJECTILES:
                excess = len(spell_projectiles) - MAX_PROJECTILES
                # Remove oldest projectiles (from the front of the list)
                for i in range(excess):
                    if spell_projectiles:
                        oldest = spell_projectiles[0]
                        oldest.alive = False
                        spell_projectiles.pop(0)
                logger.warning(f"[SPELL] Projectile limit exceeded, removed {excess} old projectiles")
            
            # Update spell effects
            for effect in spell_effects[:]:
                if effect.alive:
                    effect.update(dt)
                else:
                    spell_effects.remove(effect)
            
            # OPTIMIZATION: Enforce maximum effect limit to prevent memory leaks
            MAX_EFFECTS = 150
            if len(spell_effects) > MAX_EFFECTS:
                excess = len(spell_effects) - MAX_EFFECTS
                for i in range(excess):
                    if spell_effects:
                        oldest = spell_effects[0]
                        oldest.alive = False
                        spell_effects.pop(0)
                logger.warning(f"[SPELL] Effect limit exceeded, removed {excess} old effects")
            
            # OPTIMIZATION: Update NPCs at reduced frequency using time accumulator
            if npc_update_accumulator >= NPC_UPDATE_INTERVAL:
                npc_manager.update(npc_update_accumulator, world)
                
                # Update guard chase logic if in town and player is wanted
                if in_town and player.is_wanted and current_town_instance:
                    import math
                    for guard in town_guards:
                        # Only guards in the CURRENT town should chase
                        if not hasattr(guard, 'current_town') or guard.current_town != current_town_instance.name:
                            continue
                        
                        # Check if guard should chase player
                        if guard.npc_type == "guard":
                            dx = guard.x - player.x
                            dy = guard.y - player.y
                            distance = math.sqrt(dx * dx + dy * dy)
                            
                            # If player is ON THE LAMB (escaped), guards are MORE aggressive
                            detection_range = guard.detection_radius
                            if player.on_the_lamb:
                                detection_range = guard.detection_radius * 2.5  # Much larger detection radius
                            
                            # If guard sees wanted player within detection range
                            if distance < detection_range:
                                if guard.state != "chase":
                                    guard.chase_target = player
                                    guard.change_state("chase")
                                    player.being_chased_by_guards = True
                                    if player.on_the_lamb:
                                        town_message = f"🚨 {guard.name} spotted the ESCAPEE!"
                                    else:
                                        town_message = f"⚠ {guard.name} is pursuing you!"
                                    town_message_timer = 120
                                    logger.info(f"[GUARD CHASE] {guard.name} started chasing wanted player (on_the_lamb={player.on_the_lamb})")
                            
                            # Update guard position if chasing
                            if guard.state == "chase" and guard.chase_target == player:
                                # Guards move FASTER when chasing escapees
                                chase_speed_multiplier = 1.5 if player.on_the_lamb else 1.0
                                guard._update_chase(dt * 2 * chase_speed_multiplier, player)
                                
                                # Check if guard caught player (arrest)
                                if distance < 40:
                                    # ARREST!
                                    player.being_chased_by_guards = False
                                    guard.chase_target = None
                                    guard.change_state("patrol" if guard.is_patrolling else "idle")
                                    
                                    # Calculate jail time and fine based on bounty
                                    fine_amount = int(player.wanted_level * player.escape_bounty_multiplier)
                                    jail_days = player.wanted_level // 10  # 1 day per 10 gold bounty, NO MAX
                                    if jail_days < 1:
                                        jail_days = 1  # Minimum 1 day
                                    
                                    # Guard searches player and confiscates stolen items
                                    stolen_found = guard_search_system.search_player(player, leaving_town_hall=False)
                                    confiscated_value = 0
                                    if stolen_found:
                                        # Remove stolen items from inventory and clear stolen list
                                        for stolen_item in stolen_found:
                                            item_name = stolen_item.item_id
                                            if item_name in player.inventory and player.inventory[item_name] > 0:
                                                player.inventory[item_name] -= 1
                                                if player.inventory[item_name] <= 0:
                                                    del player.inventory[item_name]
                                                confiscated_value += 10  # Estimate 10g per confiscated item
                                        player.stolen_items = []  # Clear stolen items list
                                        logger.info(f"[ARREST] Confiscated {len(stolen_found)} stolen items worth ~{confiscated_value}g")
                                    
                                    # Put player in jail
                                    player.in_jail = True
                                    player.jail_start_day = game_time.day_count
                                    player.jail_days = jail_days
                                    player.jail_fine = fine_amount
                                    
                                    # Initialize jail work tracking
                                    jail_work_system.set_sentence(id(player), player.jail_days)
                                    
                                    # Clear wanted and on the lamb status after arrest
                                    player.is_wanted = False
                                    player.on_the_lamb = False
                                    player.escape_bounty_multiplier = 1.0
                                    wanted_system.wanted_players.pop(id(player), None)
                                    
                                    days_text = "day" if jail_days == 1 else "days"
                                    town_message = f"⚔ ARRESTED! Sentence: {jail_days} {days_text} or pay {fine_amount}g fine"
                                    if confiscated_value > 0:
                                        town_message += f"\n{len(stolen_found)} stolen items confiscated (~{confiscated_value}g)"
                                    town_message_timer = 300
                                    logger.info(f"[ARREST] Player arrested by {guard.name}, {jail_days} day sentence or {fine_amount}g fine")
                                    
                                    # Teleport player to central jail building (far from all towns)
                                    player.x = jail_building.x + jail_building.width // 2
                                    player.y = jail_building.y + jail_building.height // 2
                                    logger.info(f"[ARREST] Player teleported to {jail_building.name} at ({player.x}, {player.y})")
                                    
                                    # Reset town state when teleported to jail
                                    in_town = False
                                    current_town_instance = None
                
                # Reset NPC update accumulator after updating NPCs and guards
                npc_update_accumulator = 0.0
            
            # Update jail status if player is imprisoned
            if player.in_jail:
                days_served = game_time.day_count - player.jail_start_day
                if days_served >= player.jail_days:
                    # Release player from jail - sentence completed
                    player.in_jail = False
                    player.jail_start_day = 0
                    player.jail_days = 0
                    player.wanted_level = 0  # Clear bounty after serving time
                    player.jail_fine = 0
                    town_message = "You have been released from jail. Your debt to society is paid."
                    town_message_timer = 180
                    logger.info("[JAIL] Player released after serving full sentence")
            
            # Update dialogue text reveal animation
            if dialogue_ui.active:
                dialogue_ui.update(dialogue_manager)
            
            # Update shop UI (for haggling timers)
            if shop_ui.active:
                shop_ui.update()
            
            # Update shop ownership UI (for message timers)
            if shop_ownership_ui.active:
                shop_ownership_ui.update()
            
            # Update trading menu UI (for message timers)
            if trading_menu_ui.active:
                trading_menu_ui.update()
            
            # Update bartering UI (for message timers)
            if bartering_ui.active:
                bartering_ui.update()
            
            # OPTIMIZATION: Increment cache time counters
            tilemap_cache_frame += 1
            multipliers_cache_time += dt
            
            # Clear old cache entries every 5 seconds
            if tilemap_cache_frame % 300 == 0:
                tilemap_cache.clear()
            
        
        # Check for nearby NPC to show interaction prompt (only in town, outside buildings)
        nearby_npc = None
        if in_town and not in_building_interior:
            nearby_npc = npc_manager.get_interactable_npc(player.x, player.y)
        
        # Check for nearby building in town instances (only when outside)
        nearby_building = None
        if in_town and current_town_instance and not in_building_interior:
            nearby_distance = 80
            for building in current_town_instance.buildings:
                dx = player.x - building.door_x
                dy = player.y - building.door_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance < nearby_distance:
                    nearby_distance = distance
                    nearby_building = building
        
        # Check for nearby library in town
        nearby_library = None
        if in_town and current_town_instance and not in_building_interior:
            library = library_manager.get_library_in_town(current_town_instance.name)
            if library:
                dx = player.x - library.x
                dy = player.y - library.y
                library_distance = (dx * dx + dy * dy) ** 0.5
                if library_distance < 80:  # Same distance as other buildings
                    nearby_library = library
        
        # Check for nearby mage tower in town
        nearby_mage = None
        if in_town and current_town_instance and not in_building_interior:
            mage = mage_manager.get_nearby_mage(player.x, player.y)
            if mage:
                nearby_mage = mage
        
        # Check for nearby town gate
        nearby_gate_town = None
        if not in_town and not in_dungeon:
            for town_name, (gate_x, gate_y) in town_gates.items():
                distance = ((player.x - gate_x) ** 2 + (player.y - gate_y) ** 2) ** 0.5
                if distance < config.TILE_SIZE * 4:
                    nearby_gate_town = town_name
                    break
        
        # Check for nearby jail building (standalone, not in any town)
        nearby_jail_building = None
        if not in_town and not in_dungeon and not in_building_interior:
            dx = player.x - jail_building.door_x
            dy = player.y - jail_building.door_y
            jail_distance = (dx * dx + dy * dy) ** 0.5
            if jail_distance < 80:  # Same distance as other buildings
                nearby_jail_building = jail_building
        
        # Check for nearby tutorial shack (standalone)
        nearby_tutorial_shack = None
        if tutorial_shack and not in_town and not in_dungeon and not in_building_interior:
            dx = player.x - tutorial_shack.door_x
            dy = player.y - tutorial_shack.door_y
            shack_distance = (dx * dx + dy * dy) ** 0.5
            if shack_distance < 80:
                nearby_tutorial_shack = tutorial_shack
        
        # Check if near gate exit inside town
        near_town_exit = False
        if in_town and current_town_instance:
            gate_distance = ((player.x - current_town_instance.gate_x) ** 2 + 
                           (player.y - current_town_instance.gate_y) ** 2) ** 0.5
            if gate_distance < config.TILE_SIZE * 4:
                near_town_exit = True
        
        # Check for nearby dungeon entrance
        nearby_dungeon = False
        if not in_town and not in_dungeon:
            for entrance_x, entrance_y in dungeon_entrances:
                distance = ((player.x - entrance_x) ** 2 + (player.y - entrance_y) ** 2) ** 0.5
                if distance < config.TILE_SIZE * 2:
                    nearby_dungeon = True
                    break

        # Build inventory items categorization before rendering (for display sync)
        if show_inventory:
            items_by_cat = {c: [] for c in inventory_categories}
            # Stackables - categorize by name patterns
            for k, v in player.inventory.items():
                if k == 'items':
                    continue
                # Only include items with quantity > 0
                if v <= 0:
                    continue
                # Categorize stackable items
                item_name = k.lower()
                if any(food_word in item_name for food_word in ['berry', 'bread', 'meat', 'fish', 'apple', 'cheese', 'stew', 'food']):
                    items_by_cat['Food'].append((k, v))
                elif any(quest_word in item_name for quest_word in ['scroll', 'letter', 'note', 'map', 'key_', 'quest']):
                    items_by_cat['Quest Items'].append((k, v))
                elif k == 'fiber':
                    # Fiber goes to Other only
                    items_by_cat['Other'].append((k, v))
                elif k == 'stick':
                    # Sticks are weapons, show in Weapons category
                    items_by_cat['Weapons'].append((k, v))
                else:
                    items_by_cat['Other'].append((k, v))
            # Item objects (weapons, equipment, etc.)
            for item in player.inventory.get('items', []):
                if hasattr(item, 'type'):
                    if item.type == 'weapon':
                        items_by_cat['Weapons'].append(item)
                    elif item.type in ['armor', 'accessory', 'shield'] or get_equipment_slot(item) is not None:
                        # Any item that can be equipped goes in Equipment
                        items_by_cat['Equipment'].append(item)
                    else:
                        items_by_cat['Other'].append(item)
                else:
                    items_by_cat['Other'].append(item)
            # Apply sorting to items
            for category in items_by_cat:
                items_by_cat[category] = sort_inventory_items(items_by_cat[category], inventory_sort_mode)
        
        # Rendering happens regardless of death screen state
        graphics.render(world, player, entities,
                        show_inventory=show_inventory,
                        inventory_menu_state=inventory_menu_state if show_inventory else None,
                        inventory_categories=inventory_categories if show_inventory else None,
                        inventory_action_msg=inventory_action_msg if show_inventory else None,
                        inventory_inspect_item=inventory_inspect_item if show_inventory else None,
                        inventory_items_by_cat=items_by_cat if show_inventory else None,
                        npc_manager=npc_manager)
        
        # Draw vision cones for debugging (press F7 to toggle debug mode)
        if debug_mode and in_town:
            camera_x = player.x - config.SCREEN_WIDTH // 2
            camera_y = player.y - config.SCREEN_HEIGHT // 2
            stealth_system.draw_vision_cones(screen, camera_x, camera_y, debug=True)
        
        # Draw corpses and graves (always visible, not just in debug mode)
        camera_x = player.x - config.SCREEN_WIDTH // 2
        camera_y = player.y - config.SCREEN_HEIGHT // 2
        body_disposal_system.draw_corpses(screen, camera_x, camera_y)
        body_disposal_system.draw_graves(screen, camera_x, camera_y)
        
        # Draw wilderness fighters (simple colored squares for now)
        if not in_town and not in_dungeon:
            for fighter in wilderness_fighter_system.get_active_fighters():
                # Only draw if within render distance
                distance_to_player = ((fighter.current_x - player.x) ** 2 + (fighter.current_y - player.y) ** 2) ** 0.5
                if distance_to_player <= 800:  # Render distance
                    screen_x = int(fighter.current_x - camera_x)
                    screen_y = int(fighter.current_y - camera_y)
                    
                    # Draw fighter as red square with black border
                    fighter_rect = pygame.Rect(screen_x - 16, screen_y - 16, 32, 32)
                    pygame.draw.rect(screen, (180, 50, 50), fighter_rect)
                    pygame.draw.rect(screen, (0, 0, 0), fighter_rect, 2)
                    
                    # Draw name label
                    font = get_font(None, 16)
                    name_surface = font.render(fighter.name, True, (255, 255, 255))
                    screen.blit(name_surface, (screen_x - name_surface.get_width() // 2, screen_y - 25))
                    
                    # Draw level indicator
                    level_surface = font.render(f"Lvl {fighter.level}", True, (255, 255, 0))
                    screen.blit(level_surface, (screen_x - level_surface.get_width() // 2, screen_y + 20))
        
        # Render curfew warning dialog (highest priority overlay)
        if curfew_warning_dialog['active']:
            # Semi-transparent overlay
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Dialog box
            dialog_width = 600
            dialog_height = 300
            dialog_x = (config.SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (config.SCREEN_HEIGHT - dialog_height) // 2
            
            pygame.draw.rect(screen, (40, 40, 50), (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(screen, (200, 50, 50), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
            
            # Title
            title_font = get_font(None, 36)
            title = title_font.render("⚠️ CURFEW IN EFFECT ⚠️", True, (255, 200, 50))
            screen.blit(title, (dialog_x + (dialog_width - title.get_width()) // 2, dialog_y + 20))
            
            # Message
            msg_font = get_font(None, 24)
            town_name = curfew_warning_dialog['town_name']
            messages = [
                f"{town_name} has an active curfew!",
                f"Curfew Hours: 5PM - 2AM",
                "",
                "If you enter, you risk being fined 300g",
                "if guards spot you during curfew hours.",
                "",
                "What would you like to do?"
            ]
            
            y_offset = dialog_y + 70
            for msg in messages:
                text = msg_font.render(msg, True, (220, 220, 220))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, y_offset))
                y_offset += 30
            
            # Options
            option_font = get_font(None, 22)
            options = [
                "[ENTER] Enter anyway (stay hidden from guards)",
                "[F] Fast Travel to safe location",
                "[ESC] Cancel"
            ]
            
            y_offset += 10
            for option in options:
                text = option_font.render(option, True, (100, 255, 100))
                screen.blit(text, (dialog_x + 20, y_offset))
                y_offset += 25
        
        # Render fast travel menu
        elif fast_travel_menu['active']:
            # Semi-transparent overlay
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Dialog box
            dialog_width = 500
            dialog_height = 400
            dialog_x = (config.SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (config.SCREEN_HEIGHT - dialog_height) // 2
            
            pygame.draw.rect(screen, (40, 40, 50), (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(screen, (100, 150, 255), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
            
            # Title
            title_font = get_font(None, 36)
            title = title_font.render("Fast Travel", True, (100, 200, 255))
            screen.blit(title, (dialog_x + (dialog_width - title.get_width()) // 2, dialog_y + 20))
            
            # Locations
            available_locations = fast_travel_system.get_available_locations()
            if available_locations:
                y_offset = dialog_y + 80
                for idx, location_name in enumerate(available_locations):
                    location_info = fast_travel_system.get_location_info(location_name)
                    is_selected = (idx == fast_travel_menu['selected_idx'])
                    
                    # Highlight selected
                    if is_selected:
                        pygame.draw.rect(screen, (80, 80, 100), (dialog_x + 20, y_offset - 5, dialog_width - 40, 35))
                    
                    # Location name
                    loc_font = get_font(None, 26)
                    color = (255, 255, 100) if is_selected else (220, 220, 220)
                    text = loc_font.render(f"> {location_name}", True, color)
                    screen.blit(text, (dialog_x + 30, y_offset))
                    
                    # Description
                    if location_info and location_info.get('description'):
                        desc_font = get_font(None, 18)
                        desc_text = desc_font.render(location_info['description'], True, (180, 180, 180))
                        screen.blit(desc_text, (dialog_x + 50, y_offset + 22))
                    
                    y_offset += 50
            else:
                no_loc_font = get_font(None, 24)
                text = no_loc_font.render("No locations available", True, (200, 100, 100))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, dialog_y + 150))
            
            # Controls
            controls_font = get_font(None, 20)
            controls = [
                "[↑/↓] Select   [ENTER] Travel   [ESC] Cancel"
            ]
            y_offset = dialog_y + dialog_height - 40
            for control in controls:
                text = controls_font.render(control, True, (150, 150, 150))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, y_offset))
        
        # Only render game elements if not in a full-screen menu
        elif not show_inventory:
            # Render enemies on screen (use frame-start camera)
            
            # Draw overworld elements (not in dungeon or town)
            if not in_dungeon and not in_town:
                # Don't draw town buildings on overworld anymore - they're in instances
                # town_manager.draw_all(screen, camera_x, camera_y)
                
                # Draw gathering nodes (resource nodes)
                gathering_nodes_manager.draw(screen, camera_x, camera_y)
                
                # Draw gatherer NPCs (with distance culling for performance)
                class SimpleCamera:
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y
                # OPTIMIZATION: Only draw gatherers near player
                visible_gatherers = [npc for npc in gatherer_npc_manager.npcs 
                                   if abs(npc.x - player.x) < 800 and abs(npc.y - player.y) < 800]
                if visible_gatherers:
                    # Temporarily replace npcs list for drawing
                    original_npcs = gatherer_npc_manager.npcs
                    gatherer_npc_manager.npcs = visible_gatherers
                    gatherer_npc_manager.draw_all(screen, SimpleCamera(camera_x, camera_y))
                    gatherer_npc_manager.npcs = original_npcs
                
                # Draw tutorial NPC (if exists and visible, and not in a building)
                if hasattr(player, 'tutorial_npc') and player.tutorial_npc:
                    tutorial_npc = player.tutorial_npc
                    # Only draw if not in a building and near player
                    if not hasattr(tutorial_npc, 'in_building') or not tutorial_npc.in_building:
                        distance_to_player = ((tutorial_npc.x - player.x) ** 2 + (tutorial_npc.y - player.y) ** 2) ** 0.5
                        if distance_to_player < 1000:
                            tutorial_npc.draw(screen, camera_x, camera_y)
                            
                            # Draw health bar if damaged or in combat
                            if tutorial_npc.health < tutorial_npc.max_health or tutorial_npc.combat_target:
                                screen_x = tutorial_npc.x - camera_x
                                screen_y = tutorial_npc.y - camera_y
                                # Health bar dimensions
                                bar_width = 60
                                bar_height = 6
                                bar_x = screen_x - bar_width // 2
                                bar_y = screen_y - tutorial_npc.size - 15
                                
                                # Background
                                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                                # Health
                                health_ratio = tutorial_npc.health / tutorial_npc.max_health
                                pygame.draw.rect(screen, (200, 50, 50), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
                                # Border
                                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
                                
                                # Level indicator
                                level_font = get_font(None, 16)
                                level_text = level_font.render(f"Lv{tutorial_npc.level}", True, (255, 255, 255))
                                screen.blit(level_text, (bar_x - 30, bar_y - 2))
                
                # Draw tutorial shack (if it exists)
                if tutorial_shack:
                    # Only draw if near player
                    distance_to_player = ((tutorial_shack.x - player.x) ** 2 + (tutorial_shack.y - player.y) ** 2) ** 0.5
                    if distance_to_player < 1000:
                        tutorial_shack.draw(screen, camera_x, camera_y)
                
                # Draw wilderness fighter NPCs
                wilderness_fighter_system.draw(screen, camera_x, camera_y)
                
                # Draw player's campfire
                fire_manager.draw(screen, SimpleCamera(camera_x, camera_y))
                
                # Draw pet companion (only if enabled)
                if pet_companion.enabled:
                    pet_companion.draw(screen, camera_x, camera_y)
                
                # Draw smoke effects (particles for disappearing NPCs, etc)
                smoke_effect.draw(screen, camera_x, camera_y)
                
                # Update and draw achievement popup
                achievement_popup.update(dt)
                
                # Draw town gates on overworld (visible entrances)
                for town_name, (gate_x, gate_y) in town_gates.items():
                    # Only draw if near player (within visible range)
                    distance_to_player = ((gate_x - player.x) ** 2 + (gate_y - player.y) ** 2) ** 0.5
                    if distance_to_player < 1000:  # Visible range
                        screen_x = int(gate_x - camera_x)
                        screen_y = int(gate_y - camera_y)
                        
                        # Only draw if on screen
                        if -100 < screen_x < config.SCREEN_WIDTH + 100 and -100 < screen_y < config.SCREEN_HEIGHT + 100:
                            # Draw gate structure (stone archway style)
                            gate_color = (120, 100, 80)  # Stone color
                            gate_width = 64
                            gate_height = 80
                            
                            # Left pillar
                            pygame.draw.rect(screen, gate_color, (screen_x - gate_width // 2, screen_y - gate_height // 2, 16, gate_height))
                            pygame.draw.rect(screen, (80, 70, 60), (screen_x - gate_width // 2, screen_y - gate_height // 2, 16, gate_height), 2)
                            
                            # Right pillar
                            pygame.draw.rect(screen, gate_color, (screen_x + gate_width // 2 - 16, screen_y - gate_height // 2, 16, gate_height))
                            pygame.draw.rect(screen, (80, 70, 60), (screen_x + gate_width // 2 - 16, screen_y - gate_height // 2, 16, gate_height), 2)
                            
                            # Top arch
                            pygame.draw.rect(screen, gate_color, (screen_x - gate_width // 2, screen_y - gate_height // 2, gate_width, 12))
                            pygame.draw.rect(screen, (80, 70, 60), (screen_x - gate_width // 2, screen_y - gate_height // 2, gate_width, 12), 2)
                            
                            # Draw town icon in center (house emoji)
                            icon_font = get_font(None, 40)
                            town_icon = icon_font.render("🏘️", True, (255, 255, 255))
                            screen.blit(town_icon, (screen_x - town_icon.get_width() // 2, screen_y - town_icon.get_height() // 2))
                            
                            # Draw town name below gate
                            name_font = get_font(None, 18)
                            name_surface = name_font.render(town_name, True, (255, 255, 255))
                            name_bg = pygame.Surface((name_surface.get_width() + 10, name_surface.get_height() + 6))
                            name_bg.fill((0, 0, 0))
                            name_bg.set_alpha(180)
                            screen.blit(name_bg, (screen_x - name_surface.get_width() // 2 - 5, screen_y + gate_height // 2 + 5))
                            screen.blit(name_surface, (screen_x - name_surface.get_width() // 2, screen_y + gate_height // 2 + 8))
                            
                            # Draw pulsing glow if player is nearby
                            distance = ((gate_x - player.x) ** 2 + (gate_y - player.y) ** 2) ** 0.5
                            if distance < config.TILE_SIZE * 4:
                                pulse = abs(math.sin(pygame.time.get_ticks() / 500.0))
                                glow_color = (100, 200, 255, int(100 + 100 * pulse))
                                glow_surface = get_cached_surface((gate_width + 20, gate_height + 20), pygame.SRCALPHA, True)
                                pygame.draw.rect(glow_surface, glow_color, (0, 0, gate_width + 20, gate_height + 20), 3)
                                screen.blit(glow_surface, (screen_x - (gate_width + 20) // 2, screen_y - (gate_height + 20) // 2), special_flags=pygame.BLEND_RGBA_ADD)
                
                # Draw dungeon entrances on overworld
                for entrance_x, entrance_y in dungeon_entrances:
                    # Only draw if near player (within visible range)
                    distance_to_player = ((entrance_x - player.x) ** 2 + (entrance_y - player.y) ** 2) ** 0.5
                    if distance_to_player < 1000:  # Visible range
                        screen_x = int(entrance_x - camera_x)
                        screen_y = int(entrance_y - camera_y)
                        
                        # Only draw if on screen
                        if -100 < screen_x < config.SCREEN_WIDTH + 100 and -100 < screen_y < config.SCREEN_HEIGHT + 100:
                            # Draw cave entrance (dark opening with rocks)
                            entrance_width = 48
                            entrance_height = 56
                            
                            # Cave opening (dark)
                            pygame.draw.ellipse(screen, (20, 20, 30), (screen_x - entrance_width // 2, screen_y - entrance_height // 2, entrance_width, entrance_height))
                            pygame.draw.ellipse(screen, (40, 40, 50), (screen_x - entrance_width // 2, screen_y - entrance_height // 2, entrance_width, entrance_height), 3)
                            
                            # Rock texture around entrance
                            rock_color = (90, 80, 70)
                            # Top rocks
                            pygame.draw.circle(screen, rock_color, (screen_x - 20, screen_y - 25), 12)
                            pygame.draw.circle(screen, rock_color, (screen_x + 18, screen_y - 22), 10)
                            pygame.draw.circle(screen, rock_color, (screen_x, screen_y - 30), 14)
                            
                            # Bottom rocks
                            pygame.draw.rect(screen, rock_color, (screen_x - 25, screen_y + 15, 15, 15))
                            pygame.draw.rect(screen, rock_color, (screen_x + 10, screen_y + 18, 18, 12))
                            
                            # Add dark borders to rocks
                            pygame.draw.circle(screen, (60, 55, 50), (screen_x - 20, screen_y - 25), 12, 2)
                            pygame.draw.circle(screen, (60, 55, 50), (screen_x + 18, screen_y - 22), 10, 2)
                            pygame.draw.circle(screen, (60, 55, 50), (screen_x, screen_y - 30), 14, 2)
                            
                            # Draw dungeon icon (skull emoji)
                            icon_font = get_font(None, 32)
                            dungeon_icon = icon_font.render("⚔️", True, (255, 200, 100))
                            screen.blit(dungeon_icon, (screen_x - dungeon_icon.get_width() // 2, screen_y - dungeon_icon.get_height() // 2))
                            
                            # Draw ominous glow if player is nearby
                            distance = ((entrance_x - player.x) ** 2 + (entrance_y - player.y) ** 2) ** 0.5
                            if distance < config.TILE_SIZE * 2:
                                pulse = abs(math.sin(pygame.time.get_ticks() / 400.0))
                                glow_color = (150, 50, 50, int(80 + 80 * pulse))
                                glow_radius = int(entrance_width // 2 + 10 + pulse * 8)
                                glow_surface = get_cached_surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA, True)
                                pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                                screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)
                                
                                # Draw "Press F to Enter" prompt
                                prompt_font = get_font(None, 16)
                                prompt_text = prompt_font.render("Press F to Enter", True, (255, 255, 255))
                                prompt_bg = pygame.Surface((prompt_text.get_width() + 10, prompt_text.get_height() + 6))
                                prompt_bg.fill((0, 0, 0))
                                prompt_bg.set_alpha(200)
                                screen.blit(prompt_bg, (screen_x - prompt_text.get_width() // 2 - 5, screen_y + entrance_height // 2 + 10))
                                screen.blit(prompt_text, (screen_x - prompt_text.get_width() // 2, screen_y + entrance_height // 2 + 13))
            
            # Draw town buildings when player is in a town instance (not in building interior)
            if in_town and current_town_instance and not in_building_interior:
                camera_x = player.x - config.SCREEN_WIDTH // 2
                camera_y = player.y - config.SCREEN_HEIGHT // 2
                
                # Draw the town instance tiles and buildings
                current_town_instance.draw(screen, camera_x, camera_y)
                
                # Draw the player at center of screen (after town tiles so player is visible)
                player_width = (config.TILE_SIZE - 4) // 2  # Half width for 50% size
                player_height = int((config.TILE_SIZE - 4) * 0.75)  # Taller than wide for person shape
                cx = config.SCREEN_WIDTH // 2
                cy = config.SCREEN_HEIGHT // 2
                
                # Draw equipped weapon before player
                graphics.draw_equipped_weapon(player, cx, cy, player_width, player_height)
                
                pygame.draw.rect(screen, player.color, (cx - player_width//2, cy - player_height//2, player_width, player_height))
                pygame.draw.rect(screen, (255,255,255), (cx - player_width//2, cy - player_height//2, player_width, player_height), 2)
                
                # Draw direction indicator arrow
                arrow_color = (255, 255, 100)  # Yellow arrow
                arrow_size = 12
                if player.facing_direction == 'up':
                    arrow_points = [(cx, cy - player_height//2 - 15), (cx - arrow_size//2, cy - player_height//2 - 5), (cx + arrow_size//2, cy - player_height//2 - 5)]
                elif player.facing_direction == 'down':
                    arrow_points = [(cx, cy + player_height//2 + 15), (cx - arrow_size//2, cy + player_height//2 + 5), (cx + arrow_size//2, cy + player_height//2 + 5)]
                elif player.facing_direction == 'left':
                    arrow_points = [(cx - player_width//2 - 15, cy), (cx - player_width//2 - 5, cy - arrow_size//2), (cx - player_width//2 - 5, cy + arrow_size//2)]
                elif player.facing_direction == 'right':
                    arrow_points = [(cx + player_width//2 + 15, cy), (cx + player_width//2 + 5, cy - arrow_size//2), (cx + player_width//2 + 5, cy + arrow_size//2)]
                pygame.draw.polygon(screen, arrow_color, arrow_points)
                pygame.draw.polygon(screen, (200, 200, 0), arrow_points, 2)
                
                # Also draw the gate exit marker
                gate_screen_x = int(current_town_instance.gate_x - camera_x)
                gate_screen_y = int(current_town_instance.gate_y - camera_y)
                
                # Only draw if on screen
                if -100 < gate_screen_x < config.SCREEN_WIDTH + 100 and -100 < gate_screen_y < config.SCREEN_HEIGHT + 100:
                    # Draw exit gate (different style from entrance)
                    gate_width = 64
                    gate_height = 80
                    
                    # Gate posts (wooden style)
                    post_color = (100, 70, 40)
                    pygame.draw.rect(screen, post_color, (gate_screen_x - gate_width // 2, gate_screen_y - gate_height // 2, 18, gate_height))
                    pygame.draw.rect(screen, (70, 50, 30), (gate_screen_x - gate_width // 2, gate_screen_y - gate_height // 2, 18, gate_height), 2)
                    
                    pygame.draw.rect(screen, post_color, (gate_screen_x + gate_width // 2 - 18, gate_screen_y - gate_height // 2, 18, gate_height))
                    pygame.draw.rect(screen, (70, 50, 30), (gate_screen_x + gate_width // 2 - 18, gate_screen_y - gate_height // 2, 18, gate_height), 2)
                    
                    # Top beam
                    pygame.draw.rect(screen, post_color, (gate_screen_x - gate_width // 2, gate_screen_y - gate_height // 2, gate_width, 14))
                    pygame.draw.rect(screen, (70, 50, 30), (gate_screen_x - gate_width // 2, gate_screen_y - gate_height // 2, gate_width, 14), 2)
                    
                    # Exit icon (door with arrow)
                    icon_font = get_font(None, 36)
                    exit_icon = icon_font.render("🚪", True, (255, 255, 255))
                    screen.blit(exit_icon, (gate_screen_x - exit_icon.get_width() // 2, gate_screen_y - exit_icon.get_height() // 2))
                    
                    # Draw pulsing glow if player is nearby
                    distance = ((current_town_instance.gate_x - player.x) ** 2 + (current_town_instance.gate_y - player.y) ** 2) ** 0.5
                    if distance < config.TILE_SIZE * 4:
                        pulse = abs(math.sin(pygame.time.get_ticks() / 500.0))
                        glow_color = (255, 200, 100, int(100 + 100 * pulse))
                        glow_surface = get_cached_surface((gate_width + 20, gate_height + 20), pygame.SRCALPHA, True)
                        pygame.draw.rect(glow_surface, glow_color, (0, 0, gate_width + 20, gate_height + 20), 3)
                        screen.blit(glow_surface, (gate_screen_x - (gate_width + 20) // 2, gate_screen_y - (gate_height + 20) // 2), special_flags=pygame.BLEND_RGBA_ADD)
                        
                        # Draw "Press F to Exit" prompt
                        prompt_font = get_font(None, 16)
                        prompt_text = prompt_font.render("Press F to Exit Town", True, (255, 255, 255))
                        prompt_bg = pygame.Surface((prompt_text.get_width() + 10, prompt_text.get_height() + 6))
                        prompt_bg.fill((0, 0, 0))
                        prompt_bg.set_alpha(200)
                        screen.blit(prompt_bg, (gate_screen_x - prompt_text.get_width() // 2 - 5, gate_screen_y + gate_height // 2 + 10))
                        screen.blit(prompt_text, (gate_screen_x - prompt_text.get_width() // 2, gate_screen_y + gate_height // 2 + 13))
            
            # Draw building interior when player is inside a building
            elif in_building_interior and current_interior:
                camera_x = player.x - config.SCREEN_WIDTH // 2
                camera_y = player.y - config.SCREEN_HEIGHT // 2
                
                # Draw the building interior
                current_interior.draw(screen, camera_x, camera_y)
                
                # Draw tutorial NPC if they're in this building
                if hasattr(player, 'tutorial_npc') and player.tutorial_npc:
                    tutorial_npc = player.tutorial_npc
                    if hasattr(tutorial_npc, 'in_building') and tutorial_npc.in_building == current_interior_building_id:
                        # Draw tutorial NPC in interior
                        screen_x = tutorial_npc.x - camera_x
                        screen_y = tutorial_npc.y - camera_y
                        
                        # Draw NPC
                        tutorial_npc.draw(screen, camera_x, camera_y)
                        
                        # Draw health bar if damaged or in combat
                        if tutorial_npc.health < tutorial_npc.max_health or tutorial_npc.combat_target:
                            bar_width = 60
                            bar_height = 6
                            bar_x = screen_x - bar_width // 2
                            bar_y = screen_y - tutorial_npc.size - 15
                            
                            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                            health_ratio = tutorial_npc.health / tutorial_npc.max_health
                            health_width = int(bar_width * health_ratio)
                            health_color = (255, 0, 0) if health_ratio < 0.3 else (255, 255, 0) if health_ratio < 0.6 else (0, 255, 0)
                            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
                            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
                            
                            # Draw level indicator
                            level_font = get_font(None, 16)
                            level_text = level_font.render(f"Lv{tutorial_npc.level}", True, (255, 255, 255))
                            level_bg = pygame.Surface((level_text.get_width() + 6, level_text.get_height() + 2))
                            level_bg.fill((0, 0, 0))
                            level_bg.set_alpha(180)
                            screen.blit(level_bg, (screen_x - level_text.get_width() // 2 - 3, bar_y - 22))
                            screen.blit(level_text, (screen_x - level_text.get_width() // 2, bar_y - 20))
                
                # Draw the player at center of screen
                player_width = (config.TILE_SIZE - 4) // 2  # Half width for 50% size
                player_height = int((config.TILE_SIZE - 4) * 0.75)  # Taller than wide for person shape
                cx = config.SCREEN_WIDTH // 2
                cy = config.SCREEN_HEIGHT // 2
                
                # Draw equipped weapon before player
                graphics.draw_equipped_weapon(player, cx, cy, player_width, player_height)
                
                pygame.draw.rect(screen, player.color, (cx - player_width//2, cy - player_height//2, player_width, player_height))
                pygame.draw.rect(screen, (255,255,255), (cx - player_width//2, cy - player_height//2, player_width, player_height), 2)
                
                # Draw direction indicator arrow
                arrow_color = (255, 255, 100)  # Yellow arrow
                arrow_size = 12
                if player.facing_direction == 'up':
                    arrow_points = [(cx, cy - player_height//2 - 15), (cx - arrow_size//2, cy - player_height//2 - 5), (cx + arrow_size//2, cy - player_height//2 - 5)]
                elif player.facing_direction == 'down':
                    arrow_points = [(cx, cy + player_height//2 + 15), (cx - arrow_size//2, cy + player_height//2 + 5), (cx + arrow_size//2, cy + player_height//2 + 5)]
                elif player.facing_direction == 'left':
                    arrow_points = [(cx - player_width//2 - 15, cy), (cx - player_width//2 - 5, cy - arrow_size//2), (cx - player_width//2 - 5, cy + arrow_size//2)]
                elif player.facing_direction == 'right':
                    arrow_points = [(cx + player_width//2 + 15, cy), (cx + player_width//2 + 5, cy - arrow_size//2), (cx + player_width//2 + 5, cy + arrow_size//2)]
                pygame.draw.polygon(screen, arrow_color, arrow_points)
                pygame.draw.polygon(screen, (200, 200, 0), arrow_points, 2)
            
            # Draw enemies
            for enemy in enemies_list:
                if enemy.alive:
                    enemy.draw(screen, (camera_x, camera_y), player=player, current_weather=current_weather, tilemap=None)
                    
                    # Add status effect particles for enemies with status effects
                    if hasattr(enemy, 'status_manager') and enemy.status_manager:
                        # Initialize timer if not exists
                        if not hasattr(enemy, '_last_effect_particle_time'):
                            enemy._last_effect_particle_time = time.time()
                        
                        # Add particles every 0.5 seconds
                        if time.time() - enemy._last_effect_particle_time >= 0.5:
                            active_effects = enemy.status_manager.active_effects
                            for effect_name in active_effects.keys():
                                if effect_name in ['burn', 'poison', 'freeze', 'bleed', 'shock']:
                                    combat_particles.add_status_effect(
                                        effect_name, 
                                        (enemy.rect.centerx, enemy.rect.centery),
                                        (enemy.rect.width, enemy.rect.height)
                                    )
                            enemy._last_effect_particle_time = time.time()
            
            # Render locked chests
            chest_manager = get_chest_manager()
            for chest in chest_manager.chests:
                chest_screen_x = chest.x - camera_x
                chest_screen_y = chest.y - camera_y
                
                # Only draw if on screen
                if -50 < chest_screen_x < config.SCREEN_WIDTH + 50 and -50 < chest_screen_y < config.SCREEN_HEIGHT + 50:
                    # Draw chest base
                    chest_color = chest.get_color() if not chest.opened else (100, 100, 100)
                    pygame.draw.rect(screen, chest_color, (chest_screen_x - 16, chest_screen_y - 16, 32, 32))
                    pygame.draw.rect(screen, (0, 0, 0), (chest_screen_x - 16, chest_screen_y - 16, 32, 32), 2)
                    
                    # Draw lock icon if not opened
                    if not chest.opened:
                        lock_color = (255, 215, 0) if not chest.jammed else (255, 0, 0)
                        pygame.draw.circle(screen, lock_color, (int(chest_screen_x), int(chest_screen_y)), 6)
                        pygame.draw.circle(screen, (0, 0, 0), (int(chest_screen_x), int(chest_screen_y)), 6, 1)
                    elif chest.opened:
                        # Draw open chest indicator (lid open)
                        pygame.draw.line(screen, (200, 200, 200), 
                                       (chest_screen_x - 10, chest_screen_y - 5),
                                       (chest_screen_x + 10, chest_screen_y - 5), 3)
            
            # Render dropped equipment (loot on ground)
            for dropped in dropped_equipment_list:
                if hasattr(dropped, "draw"):
                    # Calculate screen position for culling
                    drop_x = dropped.x if hasattr(dropped, 'x') else dropped.rect.x
                    drop_y = dropped.y if hasattr(dropped, 'y') else dropped.rect.y
                    screen_x = drop_x - camera_x
                    screen_y = drop_y - camera_y
                    
                    # OPTIMIZATION: Render culling - skip off-screen items (with buffer for glow effects)
                    if not (-200 < screen_x < config.SCREEN_WIDTH + 200 and -200 < screen_y < config.SCREEN_HEIGHT + 200):
                        continue
                    
                    # Get item rarity for glow effect
                    item_rarity = getattr(dropped, 'rarity', 'common')
                    
                    # Draw colored glow based on rarity (before the item itself)
                    if hasattr(dropped, 'rect'):
                        glow_colors = {
                            'common': None,  # No glow for common
                            'uncommon': (100, 255, 100, 100),  # Green glow
                            'rare': (100, 100, 255, 150),  # Blue glow
                            'epic': (200, 100, 255, 180),  # Purple glow
                            'legendary': (255, 200, 50, 220),  # Gold glow
                            'artifact': (255, 128, 0, 220),  # Orange glow
                            'set': (255, 215, 0, 220)  # Bright gold glow
                        }
                        
                        glow_color = glow_colors.get(item_rarity)
                        if glow_color:
                            # Draw vertical beam for epic+ items
                            if item_rarity in ['epic', 'legendary', 'artifact', 'set']:
                                beam_alpha = int(100 + 50 * abs(math.sin(pygame.time.get_ticks() / 300.0)))
                                beam_color = (*glow_color[:3], beam_alpha)
                                beam_width = 6 if item_rarity in ['legendary', 'artifact', 'set'] else 4
                                
                                # Create beam surface
                                beam_height = 200
                                beam_surface = get_cached_surface((beam_width * 4, beam_height), pygame.SRCALPHA, True)
                                
                                # Draw gradient beam (wider at bottom)
                                for i in range(beam_height):
                                    alpha_factor = (beam_height - i) / beam_height
                                    width_factor = 1 + (i / beam_height) * 2
                                    current_width = int(beam_width * width_factor)
                                    current_alpha = int(beam_alpha * alpha_factor)
                                    color = (*glow_color[:3], current_alpha)
                                    center_x = beam_width * 2
                                    pygame.draw.line(beam_surface, color, 
                                                   (center_x - current_width // 2, i),
                                                   (center_x + current_width // 2, i))
                                
                                # Draw beam
                                beam_x = screen_x - beam_width * 2
                                beam_y = screen_y - beam_height
                                screen.blit(beam_surface, (beam_x, beam_y), special_flags=pygame.BLEND_RGBA_ADD)
                            
                            # Draw pulsing glow circles
                            pulse = abs(math.sin(pygame.time.get_ticks() / 500.0))
                            glow_radius = int(25 + pulse * 10)
                            
                            # Create glow surface with alpha
                            glow_surface = get_cached_surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA, True)
                            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                            screen.blit(glow_surface, (screen_x - glow_radius, screen_y - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)
                            
                            # Add rarity text above rare+ items
                            if item_rarity in ['rare', 'epic', 'legendary', 'artifact', 'set']:
                                rarity_font = get_font(None, 14)
                                rarity_text = item_rarity.upper()
                                rarity_surface = rarity_font.render(rarity_text, True, glow_color[:3])
                                text_x = screen_x - rarity_surface.get_width() // 2
                                text_y = screen_y - 50
                                screen.blit(rarity_surface, (text_x, text_y))
                    
                    dropped.draw(screen, (camera_x, camera_y))
                    
                    # Add emoji icon above the dropped item
                    item_name = None
                    if hasattr(dropped, "item_type"):
                        item_name = dropped.item_type
                    elif hasattr(dropped, "type") and dropped.type != "dubloon":
                        item_name = dropped.type
                    elif hasattr(dropped, "name"):
                        item_name = dropped.name
                    elif hasattr(dropped, "equipment_id"):
                        item_name = dropped.equipment_id
                    
                    if item_name:
                        icon = get_item_icon(item_name)
                        icon_font = get_font(None, 32)
                        icon_surface = icon_font.render(icon, True, (255, 255, 255))
                        
                        # Handle different coordinate attribute structures
                        drop_x = dropped.x if hasattr(dropped, 'x') else dropped.rect.x
                        drop_y = dropped.y if hasattr(dropped, 'y') else dropped.rect.y
                        
                        icon_x = drop_x - camera_x - icon_surface.get_width() // 2
                        icon_y = drop_y - camera_y - 35
                        
                        # Draw shadow for better visibility
                        shadow_surface = icon_font.render(icon, True, (0, 0, 0))
                        screen.blit(shadow_surface, (icon_x + 2, icon_y + 2))
                        screen.blit(icon_surface, (icon_x, icon_y))
            
            # Render spell projectiles
            for projectile in spell_projectiles:
                if projectile.alive:
                    # OPTIMIZATION: Render culling - only draw projectiles on screen
                    proj_screen_x = projectile.x - camera_x
                    proj_screen_y = projectile.y - camera_y
                    if -100 < proj_screen_x < config.SCREEN_WIDTH + 100 and -100 < proj_screen_y < config.SCREEN_HEIGHT + 100:
                        projectile.draw(screen, (camera_x, camera_y))
            
            # Render spell effects
            for effect in spell_effects:
                if effect.alive:
                    # OPTIMIZATION: Render culling - only draw effects on screen
                    effect_screen_x = effect.x - camera_x
                    effect_screen_y = effect.y - camera_y
                    if -100 < effect_screen_x < config.SCREEN_WIDTH + 100 and -100 < effect_screen_y < config.SCREEN_HEIGHT + 100:
                        effect.draw(screen, (camera_x, camera_y))
            
            # Show selected spells (removed overlapping UI text)
            
            if player.secondary_spell:
                spell_info = SPELLS.get(player.secondary_spell, {})
                spell_name = spell_info.get("name", player.secondary_spell)
                spell_ui_font = get_font(None, 20)
                secondary_text = spell_ui_font.render(f"R: {spell_name}", True, (200, 150, 255))
                screen.blit(secondary_text, (10, 135))
            
            # Update and display active blessings
            active_blessings[:] = [b for b in active_blessings if not b.update(dt)]
            
            if active_blessings:
                blessing_y = 150
                blessing_font = get_font(None, 24)
                
                for blessing in active_blessings:
                    # Blessing background
                    blessing_width = 220
                    blessing_height = 50
                    blessing_bg = get_cached_surface((blessing_width, blessing_height), pygame.SRCALPHA, True)
                    blessing_bg.fill((50, 40, 80, 200))
                    pygame.draw.rect(blessing_bg, (200, 180, 255), (0, 0, blessing_width, blessing_height), 2)
                    screen.blit(blessing_bg, (config.SCREEN_WIDTH - blessing_width - 10, blessing_y))
                    
                    # Blessing name
                    name_text = blessing_font.render(blessing.name, True, (220, 210, 255))
                    screen.blit(name_text, (config.SCREEN_WIDTH - blessing_width - 5 + (blessing_width - name_text.get_width()) // 2, blessing_y + 8))
                    
                    # Time remaining
                    time_text = blessing_font.render(blessing.get_time_remaining_text(), True, (150, 255, 150))
                    screen.blit(time_text, (config.SCREEN_WIDTH - blessing_width - 5 + (blessing_width - time_text.get_width()) // 2, blessing_y + 28))
                    
                    blessing_y += 55
            
            # Display auto-loot status indicator
            if auto_loot_enabled:
                loot_indicator_font = get_font(None, 18)
                loot_text = f"🔍 Auto-Loot: {auto_loot_min_rarity.title()}+"
                loot_surf = loot_indicator_font.render(loot_text, True, (150, 255, 150))
                screen.blit(loot_surf, (config.SCREEN_WIDTH - loot_surf.get_width() - 10, 10))
            
            # Render NPCs (guards and other town NPCs - only when outside buildings)
            if in_town and not in_building_interior:
                npc_manager.draw(screen, camera_x, camera_y)
            
            # Show NPC interaction prompt if nearby (only in towns, outside buildings)
            if nearby_npc and not smart_inventory_ui.active and in_town and not in_building_interior:
                npc_manager.show_interaction_prompt(screen, nearby_npc)
            
            # Show building interaction prompt if nearby in town
            if nearby_building and not smart_inventory_ui.active and in_town and not in_building_interior:
                # Draw visual indicator above the building door
                door_screen_x = int(nearby_building.door_x - camera_x)
                door_screen_y = int(nearby_building.door_y - camera_y)
                
                # Only draw if on screen
                if 0 < door_screen_x < config.SCREEN_WIDTH and 0 < door_screen_y < config.SCREEN_HEIGHT:
                    # Draw glowing indicator above door
                    pulse = abs(math.sin(pygame.time.get_ticks() / 400.0))
                    indicator_color = (255, 255, 100, int(150 + 100 * pulse))
                    indicator_size = 8
                    glow_surface = get_cached_surface((indicator_size * 4, indicator_size * 4), pygame.SRCALPHA, True)
                    pygame.draw.circle(glow_surface, indicator_color, (indicator_size * 2, indicator_size * 2), int(indicator_size * 2))
                    screen.blit(glow_surface, (door_screen_x - indicator_size * 2, door_screen_y - 60), special_flags=pygame.BLEND_RGBA_ADD)
                    
                    # Draw arrow pointing down to door
                    arrow_font = get_font(None, 32)
                    arrow = arrow_font.render("▼", True, (255, 255, 100))
                    screen.blit(arrow, (door_screen_x - arrow.get_width() // 2, door_screen_y - 50))
                
                # Draw interaction prompt at bottom of screen
                font = get_font(None, 24)
                building_actions = {
                    BuildingType.INN: "Press F to rest at",
                    BuildingType.SHOP: "Press F to browse",
                    BuildingType.BLACKSMITH: "Press F to visit",
                    BuildingType.MARKET: "Press F to trade at",
                    BuildingType.BANK: "Press F to access",
                    BuildingType.TAVERN: "Press F to enter",
                    BuildingType.TEMPLE: "Press F to pray at",
                    BuildingType.MAGE_TOWER: "Press F to visit",
                    BuildingType.TOWN_HALL: "Press F to visit",
                    BuildingType.GUARD_TOWER: "Guard Tower (speak to guards)",
                    BuildingType.HOUSE: "Press F to knock on",
                    BuildingType.JAIL: "Press F to enter"
                }
                action = building_actions.get(nearby_building.type, "Press F to enter")
                prompt_text = f"{action} {nearby_building.name}"
                text_surf = font.render(prompt_text, True, (200, 200, 255))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = config.SCREEN_HEIGHT - 120
                # Draw background
                padding = 10
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                pygame.draw.rect(screen, (150, 150, 255), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show library interaction prompt if nearby
            if nearby_library and not smart_inventory_ui.active:
                font = get_font(None, 24)
                # Check if library is open
                is_open = nearby_library.is_open(game_time.hour)
                if is_open:
                    prompt_text = f"Press F to enter {nearby_library.town_name} Library"
                    text_surf = font.render(prompt_text, True, (180, 220, 255))
                else:
                    prompt_text = f"Library is closed (Open 8 AM - 8 PM)"
                    text_surf = font.render(prompt_text, True, (150, 150, 150))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = config.SCREEN_HEIGHT - 80
                # Draw background
                padding = 10
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                if is_open:
                    pygame.draw.rect(screen, (120, 160, 255), bg_rect, 2)
                else:
                    pygame.draw.rect(screen, (100, 100, 100), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show mage tower interaction prompt if nearby
            if nearby_mage and not smart_inventory_ui.active:
                font = get_font(None, 24)
                prompt_text = f"Press F to visit {nearby_mage.name}"
                text_surf = font.render(prompt_text, True, (200, 180, 255))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = config.SCREEN_HEIGHT - 80
                # Draw background
                padding = 10
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                pygame.draw.rect(screen, (150, 120, 200), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show town gate interaction prompt if nearby
            if nearby_gate_town and not smart_inventory_ui.active:
                font = get_font(None, 24)
                prompt_text = f"Press F to enter {nearby_gate_town}"
                text_surf = font.render(prompt_text, True, (255, 255, 150))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = config.SCREEN_HEIGHT - 120
                # Draw background
                padding = 10
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                pygame.draw.rect(screen, (255, 200, 100), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show standalone jail building prompt if nearby (NOT in town)
            if nearby_jail_building and not smart_inventory_ui.active and not in_town:
                # Draw visual indicator above the jail door
                door_screen_x = int(nearby_jail_building.door_x - camera_x)
                door_screen_y = int(nearby_jail_building.door_y - camera_y)
                
                # Only draw if on screen
                if 0 < door_screen_x < config.SCREEN_WIDTH and 0 < door_screen_y < config.SCREEN_HEIGHT:
                    # Draw ominous red pulsing indicator
                    pulse = abs(math.sin(pygame.time.get_ticks() / 400.0))
                    indicator_color = (255, 50, 50, int(150 + 100 * pulse))
                    indicator_size = 10
                    glow_surface = get_cached_surface((indicator_size * 4, indicator_size * 4), pygame.SRCALPHA, True)
                    pygame.draw.circle(glow_surface, indicator_color, (indicator_size * 2, indicator_size * 2), int(indicator_size * 2))
                    screen.blit(glow_surface, (door_screen_x - indicator_size * 2, door_screen_y - 60), special_flags=pygame.BLEND_RGBA_ADD)
                    
                    # Draw arrow
                    arrow_font = get_font(None, 32)
                    arrow = arrow_font.render("▼", True, (255, 50, 50))
                    screen.blit(arrow, (door_screen_x - arrow.get_width() // 2, door_screen_y - 50))
                
                font = get_font(None, 24)
                prompt_text = f"Press F to enter {nearby_jail_building.name} ⚠️"
                text_surf = font.render(prompt_text, True, (255, 100, 100))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = config.SCREEN_HEIGHT - 120
                # Draw background with red tint
                padding = 10
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (30, 0, 0, 200), bg_rect)
                pygame.draw.rect(screen, (255, 50, 50), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show tutorial shack prompt if nearby
            if nearby_tutorial_shack and not smart_inventory_ui.active:
                # Draw visual indicator above the shack door
                door_screen_x = int(nearby_tutorial_shack.door_x - camera_x)
                door_screen_y = int(nearby_tutorial_shack.door_y - camera_y)
                
                # Only draw if on screen
                if 0 < door_screen_x < config.SCREEN_WIDTH and 0 < door_screen_y < config.SCREEN_HEIGHT:
                    # Draw friendly green pulsing indicator
                    pulse = abs(math.sin(pygame.time.get_ticks() / 400.0))
                    indicator_color = (100, 255, 100, int(150 + 100 * pulse))
                    indicator_size = 8
                    glow_surface = get_cached_surface((indicator_size * 4, indicator_size * 4), pygame.SRCALPHA, True)
                    pygame.draw.circle(glow_surface, indicator_color, (indicator_size * 2, indicator_size * 2), int(indicator_size * 2))
                    screen.blit(glow_surface, (door_screen_x - indicator_size * 2, door_screen_y - 60), special_flags=pygame.BLEND_RGBA_ADD)
                    
                    # Draw arrow
                    arrow_font = get_font(None, 32)
                    arrow = arrow_font.render("▼", True, (100, 255, 100))
                    screen.blit(arrow, (door_screen_x - arrow.get_width() // 2, door_screen_y - 50))
                
                font = get_font(None, 24)
                prompt_text = f"Press F to enter {nearby_tutorial_shack.name} 🏠"
                text_surf = font.render(prompt_text, True, (100, 255, 100))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = config.SCREEN_HEIGHT - 120
                # Draw background with green tint
                padding = 10
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (0, 30, 0, 200), bg_rect)
                pygame.draw.rect(screen, (100, 255, 100), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show dungeon entrance prompt if nearby
            if nearby_dungeon and not smart_inventory_ui.active:
                font = get_font(None, 24)
                prompt_text = "Press F to enter Dungeon"
                text_surf = font.render(prompt_text, True, (255, 150, 150))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = config.SCREEN_HEIGHT - 120
                # Draw background
                padding = 10
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                pygame.draw.rect(screen, (139, 90, 43), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show town exit prompt if inside town near gate
            if near_town_exit and not smart_inventory_ui.active:
                font = get_font(None, 24)
                prompt_text = "Press F to exit to Overworld"
                text_surf = font.render(prompt_text, True, (150, 255, 150))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = config.SCREEN_HEIGHT - 120
                # Draw background
                padding = 10
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                pygame.draw.rect(screen, (100, 180, 100), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show dungeon exit prompt if inside dungeon
            if in_dungeon and not smart_inventory_ui.active:
                font = get_font(None, 20)
                prompt_text = "Press F to exit Dungeon"
                text_surf = font.render(prompt_text, True, (200, 200, 200))
                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                text_y = 20
                # Draw background
                padding = 8
                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                    text_surf.get_width() + padding * 2, 
                                    text_surf.get_height() + padding * 2)
                pygame.draw.rect(screen, (0, 0, 0, 150), bg_rect)
                pygame.draw.rect(screen, (100, 100, 100), bg_rect, 2)
                screen.blit(text_surf, (text_x, text_y))
            
            # Show building interior interaction prompts
            if in_building_interior and current_interior and not smart_inventory_ui.active:
                # Check for nearby exit door
                exit_door = current_interior.get_exit_door()
                if exit_door:
                    dx = player.x - (exit_door.x + exit_door.width / 2)
                    dy = player.y - (exit_door.y + exit_door.height / 2)
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    if distance < 60:
                        font = get_font(None, 24)
                        prompt_text = "Press F to exit building"
                        text_surf = font.render(prompt_text, True, (255, 255, 150))
                        text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                        text_y = config.SCREEN_HEIGHT - 120
                        # Draw background
                        padding = 10
                        bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                            text_surf.get_width() + padding * 2, 
                                            text_surf.get_height() + padding * 2)
                        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                        pygame.draw.rect(screen, (150, 150, 255), bg_rect, 2)
                        screen.blit(text_surf, (text_x, text_y))
                    else:
                        # Check for nearby NPCs first
                        nearby_npc = current_interior.get_nearby_npc(player.x, player.y, max_distance=60)
                        if nearby_npc:
                            font = get_font(None, 24)
                            # Special message for innkeepers
                            if nearby_npc.get('role') == 'innkeeper':
                                prompt_text = f"Press E to rent room | H to hire companions | B to buy newspaper"
                            else:
                                prompt_text = f"Press E to talk to {nearby_npc.get('name', 'NPC')}"
                            prompt_color = (150, 255, 200)  # Light green
                            text_surf = font.render(prompt_text, True, prompt_color)
                            text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                            text_y = config.SCREEN_HEIGHT - 120
                            # Draw background
                            padding = 10
                            bg_rect = pygame.Rect(text_x - padding, text_y - padding,
                                                text_surf.get_width() + padding * 2,
                                                text_surf.get_height() + padding * 2)
                            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                            pygame.draw.rect(screen, (150, 255, 150), bg_rect, 2)
                            screen.blit(text_surf, (text_x, text_y))
                        else:
                            # Check for nearby interactable objects
                            nearby_obj = current_interior.get_nearby_interactable(player.x, player.y, max_distance=60)
                            if nearby_obj:
                                font = get_font(None, 24)
                                
                                # Create appropriate prompt based on object type
                                if nearby_obj.type == "chest":
                                    if nearby_obj.locked:
                                        lockpick_count = player.inventory.get('lockpick', 0)
                                        if lockpick_count > 0:
                                            prompt_text = f"Press E to pick lock ({lockpick_count} lockpicks)"
                                            prompt_color = (255, 215, 0)  # Gold
                                        else:
                                            prompt_text = "Locked (need lockpick)"
                                            prompt_color = (255, 100, 100)  # Red
                                    elif nearby_obj.opened:
                                        prompt_text = f"{nearby_obj.name} (empty)"
                                        prompt_color = (150, 150, 150)  # Gray
                                    else:
                                        prompt_text = f"Press E to open {nearby_obj.name}"
                                        prompt_color = (150, 255, 150)  # Green
                                else:
                                    prompt_text = f"Press E to interact with {nearby_obj.name}"
                                    prompt_color = (200, 200, 255)  # Light blue
                                
                                text_surf = font.render(prompt_text, True, prompt_color)
                                text_x = config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                                text_y = config.SCREEN_HEIGHT - 120
                                # Draw background
                                padding = 10
                                bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                                    text_surf.get_width() + padding * 2, 
                                                    text_surf.get_height() + padding * 2)
                                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
                                pygame.draw.rect(screen, (100, 100, 100), bg_rect, 2)
                                screen.blit(text_surf, (text_x, text_y))
        
        # End of conditional: game elements only shown when not in full-screen menu
        
        # Render smart inventory UI on top of everything
        if smart_inventory_ui.active:
            font = get_font(None, 20)
            smart_inventory_ui.render(screen, font)
        
        # Render equipment comparison tooltip when inspecting items
        if show_inventory and inventory_inspect_item and not isinstance(inventory_inspect_item, tuple):
            comparison = get_equipment_comparison(inventory_inspect_item, player)
            if comparison:
                tooltip_lines = format_equipment_tooltip(comparison, font_size=18)
                
                # Position tooltip on the right side of the screen
                tooltip_x = config.SCREEN_WIDTH - 350
                tooltip_y = 100
                tooltip_padding = 15
                line_height = 22
                
                # Calculate tooltip size
                tooltip_width = 330
                tooltip_height = len(tooltip_lines) * line_height + tooltip_padding * 2
                
                # Draw tooltip background
                tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
                pygame.draw.rect(screen, (20, 20, 30), tooltip_rect)
                pygame.draw.rect(screen, (100, 100, 120), tooltip_rect, 2)
                
                # Draw tooltip lines
                font = get_font(None, 18)
                y_offset = tooltip_y + tooltip_padding
                for line_text, color in tooltip_lines:
                    if line_text:  # Skip empty lines for spacing
                        text_surface = font.render(line_text, True, color)
                        screen.blit(text_surface, (tooltip_x + tooltip_padding, y_offset))
                    y_offset += line_height
                
                # Draw action hints at bottom
                hint_font = get_font(None, 14)
                hint_y = tooltip_y + tooltip_height - 65
                
                # Check if item is equipped
                is_equipped = comparison['currently_equipped'] == inventory_inspect_item
                
                if is_equipped:
                    hint_text = "Press E to Unequip"
                else:
                    hint_text = "Press Q/E to Equip"
                    
                hint_surface = hint_font.render(hint_text, True, (150, 255, 150))
                screen.blit(hint_surface, (tooltip_x + tooltip_padding, hint_y))
                
                # Salvage hint
                salvage_hint = "Press Z to Salvage"
                salvage_surface = hint_font.render(salvage_hint, True, (255, 200, 100))
                screen.blit(salvage_surface, (tooltip_x + tooltip_padding, hint_y + 18))
                
                # Drop hint
                drop_hint = "Press X to Drop"
                drop_surface = hint_font.render(drop_hint, True, (255, 150, 150))
                screen.blit(drop_surface, (tooltip_x + tooltip_padding, hint_y + 36))
        
        # Render market UI on top of everything
        if market_ui.active:
            market_ui.draw(screen, market_manager, player)
        
        # Render trade route UI
        if trade_route_ui.active:
            current_town_name = current_town.name if current_town else None
            trade_route_ui.draw(screen, font, trade_route_system, current_town_name)
        
        # Render NPC skill switching UI
        if npc_skill_switching_ui.active:
            npc_skill_switching_ui.draw(screen, font, npc_skill_switching_system, gatherer_npc_manager)
        
        # Render achievement UI
        if achievement_ui.active:
            achievement_ui.draw(screen, achievement_manager)
        
        # Render bestiary UI
        if show_bestiary:
            from equipment import EQUIPMENT_DATA
            bestiary_font = get_font(None, 20)
            bestiary.draw(screen, EQUIPMENT_DATA, bestiary_font, bestiary_selected_enemy, bestiary_scroll_offset)
        
        # Render pet menu UI
        if pet_menu_ui.active:
            pet_menu_ui.draw(screen, pet_companion)
        
        # Render achievement popup
        achievement_popup.draw(screen, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        
        # Draw AI player status indicator (if AI is enabled)
        if ai_player.enabled:
            # AI active indicator in top-right corner
            ai_font = get_font(None, 24)
            ai_status_bg = pygame.Surface((250, 80))
            ai_status_bg.fill((40, 40, 60))
            ai_status_bg.set_alpha(200)
            screen.blit(ai_status_bg, (config.SCREEN_WIDTH - 260, 10))
            
            # Pulsing effect for visibility
            import math
            pulse = abs(math.sin(pygame.time.get_ticks() / 500.0))
            pulse_color = (100 + int(155 * pulse), 255, 100 + int(155 * pulse))
            
            ai_title = ai_font.render("🤖 AI ACTIVE", True, pulse_color)
            screen.blit(ai_title, (config.SCREEN_WIDTH - 245, 15))
            
            # Current goal
            ai_goal_font = get_font(None, 18)
            goal_text = f"Goal: {ai_player.current_goal or 'None'}"
            goal_render = ai_goal_font.render(goal_text, True, (200, 200, 200))
            screen.blit(goal_render, (config.SCREEN_WIDTH - 245, 42))
            
            # Emergency stop hint
            stop_hint_font = get_font(None, 16)
            stop_hint = stop_hint_font.render("Press / to stop", True, (255, 100, 100))
            screen.blit(stop_hint, (config.SCREEN_WIDTH - 245, 64))
        
        # Draw advanced dialogue UI (highest priority overlay - blocks game input)
        if advanced_dialogue_ui.active:
            advanced_dialogue_ui.draw(screen)
        
        # Draw spell HUD (above hotbar)
        spell_hud.draw(screen, player)
        
        # Draw AI debug overlay (if enabled with F8)
        if ai_debug_overlay.enabled:
            ai_debug_overlay.draw(screen, enemies_list, player, camera_x, camera_y, personality_manager)
        
        # Render save/load UI and messages (on top of everything)
        save_integrator.draw(screen)
        
        # Only render minimap and quest tracker if not in full-screen menu
        if not show_inventory and not show_equipment:
            # Render minimap (on top of everything else)
            minimap.draw(screen, player, entities, dungeon_entrances=dungeon_entrances, 
                        chests=chest_manager.chests, quest_manager=quest_manager,
                        towns=town_manager.towns, world=world, enemies=enemies_list)
            
            # Render quest tracker (below minimap)
            if not quest_log_ui.active:  # Don't show tracker when log is open
                quest_tracker_font = get_font(None, 20)
                quest_tracker_ui.draw(screen, quest_tracker_font, quest_manager)
        
        # Render quest log (on top of everything)
        if quest_log_ui.active:
            quest_log_font = get_font(None, 24)
            quest_log_ui.draw(screen, quest_log_font, quest_manager, player)
        
        # Render Max's Shop interaction (on top of everything) - Using standard dialogue UI style
        if max_shop_interaction.is_active() and not lootbox_animation.is_showing():
            # Full-screen semi-transparent overlay (matching dialogue_ui.py)
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Main dialogue panel (bottom 40% of screen - matching dialogue_ui.py)
            panel_height = int(config.SCREEN_HEIGHT * 0.45)
            panel_y = config.SCREEN_HEIGHT - panel_height
            panel_margin = 40
            panel_width = config.SCREEN_WIDTH - (panel_margin * 2)
            panel_x = panel_margin
            
            # Draw panel background (matching dialogue_ui.py colors)
            panel_color = (30, 30, 50)
            border_color = (100, 100, 150)
            pygame.draw.rect(screen, panel_color, 
                            (panel_x, panel_y, panel_width, panel_height), 
                            border_radius=15)
            pygame.draw.rect(screen, border_color, 
                            (panel_x, panel_y, panel_width, panel_height), 
                            3, border_radius=15)
            
            # NPC Portrait area (left side)
            portrait_size = 180
            portrait_x = panel_x + 30
            portrait_y = panel_y + 30
            
            # Draw portrait background
            pygame.draw.rect(screen, (40, 40, 60), 
                            (portrait_x, portrait_y, portrait_size, portrait_size), 
                            border_radius=10)
            pygame.draw.rect(screen, border_color, 
                            (portrait_x, portrait_y, portrait_size, portrait_size), 
                            2, border_radius=10)
            
            # Draw Max's portrait (hot pink for Max's signature color in the circle)
            portrait_color = (255, 20, 147)  # Max's signature hot pink
            center_x = portrait_x + portrait_size // 2
            center_y = portrait_y + portrait_size // 2
            pygame.draw.circle(screen, portrait_color, (center_x, center_y), portrait_size // 3)
            
            # Draw Max initials
            initial_font = get_font(None, 72)
            initials = "M"
            initial_text = initial_font.render(initials, True, (255, 255, 255))
            screen.blit(initial_text, 
                       (center_x - initial_text.get_width()//2, 
                        center_y - initial_text.get_height()//2))
            
            # NPC Name below portrait
            name_font = get_font(None, 28)
            npc_name_color = (255, 255, 180)
            npc_name_text = name_font.render("Max", True, npc_name_color)
            screen.blit(npc_name_text, 
                       (portrait_x + portrait_size//2 - npc_name_text.get_width()//2, 
                        portrait_y + portrait_size + 10))
            
            # Subtitle below name
            subtitle_font = get_font(None, 18)
            subtitle_text = subtitle_font.render("Neutral", True, (200, 200, 200))
            screen.blit(subtitle_text, 
                       (portrait_x + portrait_size//2 - subtitle_text.get_width()//2, 
                        portrait_y + portrait_size + 35))
            
            # Dialogue text area (right side)
            text_x = portrait_x + portrait_size + 40
            text_y = panel_y + 30
            text_width = panel_width - (portrait_size + 100)
            text_color = (255, 255, 255)
            
            # Get dialogue lines
            all_lines = max_shop_interaction.get_all_visible_lines()
            
            # Display dialogue text (excluding choices)
            dialogue_font = get_font(None, 24)  # Slightly smaller for text wrapping
            line_y = text_y
            max_text_width = text_width - 20
            
            # Show non-choice dialogue
            non_choice_lines = [l for l in all_lines if not (l.startswith("[1]") or l.startswith("[2]") or l.startswith("[A]") or l.startswith("[D]"))]
            
            for line in non_choice_lines[:7]:  # Max 7 lines
                # Word wrap long lines
                words = line.split(' ')
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    test_surface = dialogue_font.render(test_line, True, text_color)
                    
                    if test_surface.get_width() > max_text_width:
                        if current_line:
                            line_surface = dialogue_font.render(current_line.strip(), True, text_color)
                            screen.blit(line_surface, (text_x, line_y))
                            line_y += 28
                        current_line = word + " "
                    else:
                        current_line = test_line
                
                if current_line:
                    line_surface = dialogue_font.render(current_line.strip(), True, text_color)
                    screen.blit(line_surface, (text_x, line_y))
                    line_y += 28
            
            # Display player choices (if waiting for choice)
            if max_shop_interaction.waiting_for_choice and max_shop_interaction.choice_options:
                choice_y = panel_y + panel_height - 260
                choice_font = get_font(None, 24)
                choice_color = (220, 220, 220)
                choice_selected_color = (255, 255, 100)
                
                # Draw "Your Response:" label
                response_label = choice_font.render("Your Response:", True, npc_name_color)
                screen.blit(response_label, (text_x, choice_y - 30))
                
                # Remove the [1], [2], [A], [D] prefixes for cleaner display
                for i, choice_text in enumerate(max_shop_interaction.choice_options):
                    # Strip the prefix markers
                    clean_text = choice_text.replace("[1] ", "").replace("[2] ", "").replace("[A] ", "").replace("[D] ", "")
                    
                    choice_y_pos = choice_y + i * 32
                    
                    # Choice background (if selected)
                    if i == max_shop_interaction.selected_choice_index:
                        choice_bg_color = (60, 60, 100)
                        pygame.draw.rect(screen, choice_bg_color, 
                                       (text_x - 5, choice_y_pos - 2, text_width, 28), 
                                       border_radius=5)
                        color = choice_selected_color
                        prefix = "► "
                    else:
                        color = choice_color
                        prefix = "  "
                    
                    # Draw choice text
                    choice_render = choice_font.render(prefix + clean_text, True, color)
                    screen.blit(choice_render, (text_x, choice_y_pos))
                
                # Controls hint (matching dialogue_ui.py style)
                controls_font = get_font(None, 20)
                controls_text = controls_font.render("[↑↓] Select | [SPACE/ENTER] Choose | [ESC] Walk away", 
                                                    True, (180, 180, 180))
                screen.blit(controls_text, (panel_x + panel_width - controls_text.get_width() - 30, 
                                           panel_y + panel_height - 30))
            else:
                # Not waiting for choice - show continue prompt
                continue_font = get_font(None, 20)
                continue_text = continue_font.render("[SPACE] Continue", True, (180, 180, 180))
                screen.blit(continue_text, (panel_x + panel_width - continue_text.get_width() - 30, 
                                           panel_y + panel_height - 30))
        
        # Render loot box animation (on top of Max's dialogue)
        if lootbox_animation.is_showing():
            lootbox_animation.draw(screen, get_font(None, 24))
        
        # Render cosmetic equip menu
        if show_cosmetic_menu:
            cosmetic_menu.draw(screen, get_font(None, 22), cosmetic_manager)
        
        # Render dialogue UI (on top of everything)
        if dialogue_ui.active:
            dialogue_ui.draw(screen, dialogue_manager, player)
        
        # Render tutorial NPC (if active)
        if hasattr(player, 'tutorial_npc') and player.tutorial_npc and not in_dungeon and not in_building_interior:
            player.tutorial_npc.update(0.016, player)  # ~60 FPS
            player.tutorial_npc.draw(screen, camera_x, camera_y)
        
        # Render tutorial popup (on top of most UI elements)
        if tutorial_popup.active:
            tutorial_popup.draw(screen)
        
        # Render jail UI (if player is imprisoned)
        if player.in_jail:
            # Draw dark overlay
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Draw jail message box (bigger for more info)
            jail_box_width = 600
            jail_box_height = 350
            jail_box_x = config.SCREEN_WIDTH // 2 - jail_box_width // 2
            jail_box_y = config.SCREEN_HEIGHT // 2 - jail_box_height // 2
            
            pygame.draw.rect(screen, (40, 40, 40), (jail_box_x, jail_box_y, jail_box_width, jail_box_height))
            pygame.draw.rect(screen, (255, 0, 0), (jail_box_x, jail_box_y, jail_box_width, jail_box_height), 3)
            
            # Draw jail text
            jail_font = get_font(None, 32)
            if player.on_the_lamb:
                title_text = jail_font.render("🚨 RE-IMPRISONED 🚨", True, (255, 0, 0))
            else:
                title_text = jail_font.render("🔒 IMPRISONED 🔒", True, (255, 0, 0))
            screen.blit(title_text, (config.SCREEN_WIDTH // 2 - title_text.get_width() // 2, jail_box_y + 20))
            
            # Sentence info
            info_font = get_font(None, 22)
            days_served = game_time.day_count - player.jail_start_day
            days_remaining = player.jail_days - days_served
            days_text = "day" if days_remaining == 1 else "days"
            
            sentence_text = info_font.render(f"Sentence: {player.jail_days} days", True, (255, 255, 255))
            screen.blit(sentence_text, (config.SCREEN_WIDTH // 2 - sentence_text.get_width() // 2, jail_box_y + 70))
            
            served_text = info_font.render(f"Days Served: {days_served}", True, (200, 200, 200))
            screen.blit(served_text, (config.SCREEN_WIDTH // 2 - served_text.get_width() // 2, jail_box_y + 100))
            
            remaining_text = info_font.render(f"Days Remaining: {days_remaining} {days_text}", True, (255, 100, 100))
            screen.blit(remaining_text, (config.SCREEN_WIDTH // 2 - remaining_text.get_width() // 2, jail_box_y + 130))
            
            # Current day
            day_info = info_font.render(f"Current Day: {game_time.day_count}", True, (150, 150, 255))
            screen.blit(day_info, (config.SCREEN_WIDTH // 2 - day_info.get_width() // 2, jail_box_y + 160))
            
            # Fine amount
            fine_text = info_font.render(f"Early Release Fine: {player.jail_fine} dubloons", True, (255, 215, 0))
            screen.blit(fine_text, (config.SCREEN_WIDTH // 2 - fine_text.get_width() // 2, jail_box_y + 195))
            
            # Your dubloons
            gold_text = info_font.render(f"Your Dubloons: {player.dubloons}", True, (200, 200, 200))
            screen.blit(gold_text, (config.SCREEN_WIDTH // 2 - gold_text.get_width() // 2, jail_box_y + 225))
            
            # Instructions
            instr_font = get_font(None, 20)
            if player.dubloons >= player.jail_fine:
                instr1_text = instr_font.render("Press F to pay fine and leave", True, (100, 255, 100))
            else:
                instr1_text = instr_font.render("Not enough dubloons to pay fine", True, (255, 100, 100))
            screen.blit(instr1_text, (config.SCREEN_WIDTH // 2 - instr1_text.get_width() // 2, jail_box_y + 265))
            
            # Work option
            if days_remaining > 0:
                work_text = instr_font.render("Press W to work (advances 1 day, reduces sentence)", True, (150, 200, 255))
                screen.blit(work_text, (config.SCREEN_WIDTH // 2 - work_text.get_width() // 2, jail_box_y + 287))
            
            # Multi-stage escape status and option
            if id(player) in jail_escape_system.player_stages:
                current_stage = jail_escape_system.player_stages[id(player)]
                stage_names = {
                    'cell': 'CELL DOOR',
                    'block': 'CELL BLOCK',
                    'entrance': 'JAIL ENTRANCE',
                    'gate': 'OUTER GATE'
                }
                stage_display = stage_names.get(current_stage, current_stage.upper())
                
                # Show current escape progress
                escape_progress = instr_font.render(f"🔓 Escape in progress: {stage_display}", True, (255, 200, 100))
                screen.blit(escape_progress, (config.SCREEN_WIDTH // 2 - escape_progress.get_width() // 2, jail_box_y + 309))
                
                instr2_text = instr_font.render("Press B to continue escape (4 stages total)", True, (255, 150, 50))
                screen.blit(instr2_text, (config.SCREEN_WIDTH // 2 - instr2_text.get_width() // 2, jail_box_y + 331))
            else:
                instr2_text = instr_font.render("Press B to start escape attempt (multi-stage)", True, (255, 150, 50))
                screen.blit(instr2_text, (config.SCREEN_WIDTH // 2 - instr2_text.get_width() // 2, jail_box_y + 309))
            
            warn_text = get_font(None, 16).render("Warning: Each stage requires skill check. Failure = caught, +10 days", True, (255, 50, 50))
            screen.blit(warn_text, (config.SCREEN_WIDTH // 2 - warn_text.get_width() // 2, jail_box_y + 353))
        
        # CRITICAL FIX: Render shop UI (on top of dialogue)
        if shop_ui.active:
            shop_font = get_font(None, 24)
            shop_ui.draw(screen, shop_font)
        
        # Draw Diablo-style equipment UI (over everything but pause menu)
        if show_new_equipment_ui:
            equipment_ui.update(dt)
            equipment_ui.draw()
        
        # Render shop ownership UI
        if shop_ownership_ui.active:
            shop_ownership_ui.draw(screen)
        
        # Render economic events UI
        if economic_events_ui.active:
            economic_events_ui.draw(screen)
        
        # Render trading menu UI
        if trading_menu_ui.active:
            trading_menu_ui.draw(screen)
        
        # Render bartering UI
        if bartering_ui.active:
            bartering_ui.draw(screen)
        
        # Render advanced trading UI
        if advanced_trading_ui.active:
            advanced_trading_ui.draw(screen)
        
        # Render inn UI (on top of dialogue)
        if inn_ui.active:
            inn_ui.draw(screen, player)
        
        # Render blacksmith UI (on top of dialogue)
        if blacksmith_ui.active:
            blacksmith_ui.draw(screen, player)
        
        # Render tavern UI (on top of dialogue)
        if tavern_ui.active:
            tavern_ui.draw(screen, player)
        
        # Render tavern food trading UI
        if tavern_food_ui.active:
            tavern_food_ui.draw(screen, player)
        
        # Render market stall UI
        if market_stall_ui.active:
            market_stall_ui.draw(screen, player)
        
        # Render safety deposit UI
        if safety_deposit_ui.active:
            safety_deposit_ui.draw(screen, player)
        
        # Render temple UI (on top of dialogue)
        if temple_ui.active:
            temple_ui.draw(screen, player)
        
        # Render mage UI (on top of dialogue)
        if mage_ui.active:
            main_font = get_font(None, 24)
            title_font = get_font(None, 36)
            mage_ui.draw(screen, main_font, title_font)
        
        # Render bank UI (on top of dialogue)
        if bank_ui.active:
            bank_ui.draw(screen, player)
        
        # Render library UI (on top of dialogue)
        if library_ui.active:
            main_font = get_font(None, 24)
            title_font = get_font(None, 36)
            library_ui.draw(screen, main_font, title_font)
        
        # Render town hall UI (on top of dialogue)
        if town_hall_ui.active:
            town_hall_ui.draw(screen, player)
        
        # Render cooking UI (on top of dialogue)
        if cooking_ui.active:
            cooking_ui.draw(screen, player)
        
        # Render criminal underworld UI
        if criminal_ui_instance.active:
            criminal_ui_instance.draw(screen, player, game_time)
        
        # Render skills UI (gathering skills - on top of dialogue)
        if skills_ui.active:
            skills_ui.draw(screen, player)
        
        # Render leaderboard UI (on top of dialogue)
        if leaderboard_ui.active:
            leaderboard_ui.draw(screen, player.name)
        
        # Render stock market UI (on top of dialogue)
        if stock_market_ui.active:
            stock_market_ui.draw(screen, main_font)
        
        # Render companion hiring UI
        if companion_hiring_ui.active:
            companion_hiring_ui.draw(screen, main_font)
        
        # Render insurance UI
        if player_insurance_ui.active:
            player_insurance_ui.draw(screen, main_font)
        
        # Render newspaper UI
        if newspaper_ui.active:
            newspaper_ui.draw(screen, main_font)
        
        # Render commodity exchange UI
        if commodity_exchange_ui.active:
            commodity_exchange_ui.draw(screen, main_font)
        
        # Render economics skill tree UI
        if economics_skill_tree_ui.active:
            economics_skill_tree_ui.draw(screen, main_font)
        
        # Draw companions
        companion_manager.draw_all(screen, camera_x, camera_y)
        
        # Draw skills HUD (gathering progress bar)
        if not skills_ui.active:  # Don't show HUD when menu is open
            draw_skills_hud(screen, player)
        
        # Render dialogue history (on top of everything)
        if dialogue_history_ui.active:
            history_font = get_font(None, 24)
            dialogue_history_ui.draw(screen, history_font, dialogue_manager)
        
        # Render mayor powers UI (on top of everything)
        if mayor_powers_ui.active:
            mayor_powers_ui.draw(screen, main_font)
        
        # Render loot box animation (priority over everything except dialogs)
        if lootbox_animation.is_showing():
            lootbox_font = get_font(None, 24)
            lootbox_animation.draw(screen, lootbox_font)
        
        # Render cosmetic menu (on top of everything)
        if show_cosmetic_menu:
            cosmetic_font = get_font(None, 24)
            cosmetic_menu.draw(screen, cosmetic_font, cosmetic_manager)
        
        # Display AI player status if enabled (on top of everything)
        if ai_player.enabled:
            ai_font = get_font(None, 20)
            ai_status = ai_player.get_status()
            ai_status_surf = ai_font.render(ai_status, True, (100, 255, 255))
            screen.blit(ai_status_surf, (10, 10))
            
            # Display recent AI actions (log)
            recent_actions = ai_player.get_recent_log(3)
            y_offset = 35
            for action in recent_actions:
                action_surf = ai_font.render(f"  {action[:60]}", True, (150, 200, 255))
                screen.blit(action_surf, (10, y_offset))
                y_offset += 22
        
        # Render stick confirmation dialog (on top of everything else)
        if stick_confirm_dialog['active']:
            # Semi-transparent overlay
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Dialog box
            dialog_width = 600
            dialog_height = 200
            dialog_x = config.SCREEN_WIDTH // 2 - dialog_width // 2
            dialog_y = config.SCREEN_HEIGHT // 2 - dialog_height // 2
            
            pygame.draw.rect(screen, (40, 40, 60), (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(screen, (200, 200, 200), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
            
            # Dialog text
            dialog_font = get_font(None, 32)
            small_font = get_font(None, 24)
            
            if stick_confirm_dialog['action'] == 'equip':
                title_text = dialog_font.render("Equip Stick", True, (255, 255, 255))
                warning_text = small_font.render("Sticks are used for crafting and other functions.", True, (255, 200, 100))
                question_text = dialog_font.render("Are you sure you want to equip this stick?", True, (255, 255, 255))
            else:  # stack
                title_text = dialog_font.render("Add Stick to Weapon", True, (255, 255, 255))
                warning_text = small_font.render("Sticks are used for crafting and other functions.", True, (255, 200, 100))
                question_text = dialog_font.render("Add this stick to your equipped stick?", True, (255, 255, 255))
            
            choice_text = dialog_font.render("Press Y (Yes) or N (No)", True, (100, 255, 100))
            
            screen.blit(title_text, (dialog_x + dialog_width // 2 - title_text.get_width() // 2, dialog_y + 20))
            screen.blit(warning_text, (dialog_x + dialog_width // 2 - warning_text.get_width() // 2, dialog_y + 60))
            screen.blit(question_text, (dialog_x + dialog_width // 2 - question_text.get_width() // 2, dialog_y + 95))
            screen.blit(choice_text, (dialog_x + dialog_width // 2 - choice_text.get_width() // 2, dialog_y + 145))
        
        # OPTIMIZATION: Display simple FPS counter with text caching
        current_fps = frame_limiter.get_current_fps()
        if current_fps > 0:
            fps_int = int(current_fps)
            # FPS counter removed for cleaner UI
        
        # Draw full-screen map (on top of everything)
        if fullscreen_map.active:
            fullscreen_map.draw(screen, world, player, minimap.explored_tiles,
                              entities=entities, dungeon_entrances=dungeon_entrances,
                              chests=chest_manager.chests, quest_manager=quest_manager,
                              towns=town_manager.towns)
        
        # Draw floating damage numbers (on top of everything except UI)
        for floating_text in floating_texts:
            if floating_text.alive:
                floating_text.draw(screen, camera_x, camera_y)
        
        # Draw combat particle effects (weapon slashes, impacts, status effects)
        combat_particles.draw(screen, camera_x, camera_y)
        
        # Draw summons
        summoning_system.draw(screen, camera_x, camera_y)
        summon_cast_effect_ui.draw(screen, camera_x, camera_y)
        
        # Draw necromancy indicators
        if in_dungeon:
            necromancy_indicator_ui.draw(screen)
        
        # Draw combat log (on top of everything)
        if not show_inventory and not show_equipment and not smart_inventory_ui.active:
            combat_log.draw(screen, combat_log_font)
        
        # Draw player status bars (health, mana, stamina)
        if not show_inventory and not show_equipment and not smart_inventory_ui.active:
            # Create font for status bars
            small_font = get_font(None, 20)
            
            bar_x = 20
            bar_y = 20
            bar_width = 200
            bar_height = 24
            bar_spacing = 30
            
            # Health bar (red)
            health_ratio = player.health / player.max_health if player.max_health > 0 else 0
            pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (220, 20, 20), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
            hp_text = small_font.render(f"HP: {int(player.health)}/{int(player.max_health)}", True, (255, 255, 255))
            screen.blit(hp_text, (bar_x + 5, bar_y + 3))
            
            # Mana bar (blue)
            if hasattr(player, 'mana') and hasattr(player, 'max_mana'):
                mana_ratio = player.mana / player.max_mana if player.max_mana > 0 else 0
                pygame.draw.rect(screen, (0, 0, 60), (bar_x, bar_y + bar_spacing, bar_width, bar_height))
                pygame.draw.rect(screen, (20, 100, 220), (bar_x, bar_y + bar_spacing, int(bar_width * mana_ratio), bar_height))
                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y + bar_spacing, bar_width, bar_height), 2)
                mana_text = small_font.render(f"MP: {int(player.mana)}/{int(player.max_mana)}", True, (255, 255, 255))
                screen.blit(mana_text, (bar_x + 5, bar_y + bar_spacing + 3))
            
            # Stamina bar (green)
            if hasattr(player, 'stamina') and hasattr(player, 'max_stamina'):
                stamina_ratio = player.stamina / player.max_stamina if player.max_stamina > 0 else 0
                pygame.draw.rect(screen, (0, 60, 0), (bar_x, bar_y + bar_spacing * 2, bar_width, bar_height))
                pygame.draw.rect(screen, (20, 220, 20), (bar_x, bar_y + bar_spacing * 2, int(bar_width * stamina_ratio), bar_height))
                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y + bar_spacing * 2, bar_width, bar_height), 2)
                stamina_text = small_font.render(f"Stamina: {int(player.stamina)}/{int(player.max_stamina)}", True, (255, 255, 255))
                screen.blit(stamina_text, (bar_x + 5, bar_y + bar_spacing * 2 + 3))
                
                # Sprint indicator
                if hasattr(player, 'is_sprinting') and player.is_sprinting:
                    sprint_text = small_font.render("🏃 SPRINTING", True, (255, 255, 100))
                    screen.blit(sprint_text, (bar_x + bar_width + 10, bar_y + bar_spacing * 2 + 3))
            
            # Draw active racial trait indicators (right side of health bars)
            if hasattr(player, 'trait_manager') and player.trait_manager:
                trait_indicators_x = bar_x + bar_width + 20
                trait_indicators_y = bar_y
                draw_active_trait_indicators(screen, small_font, player, trait_indicators_x, trait_indicators_y)
            
            # Draw status effects display (below stamina bar)
            if hasattr(player, 'status_manager') and player.status_manager:
                active_effects = player.status_manager.get_active_effects_display()
                if active_effects:
                    # Status effects display settings
                    effect_size = 40  # Size of each effect icon
                    effect_spacing = 45  # Spacing between effects
                    effect_start_x = bar_x
                    effect_start_y = bar_y + bar_spacing * 3 + 10  # Below stamina bar
                    
                    # Create very small font for timers
                    timer_font = get_font(None, 14)
                    effect_font = get_font(None, 16)
                    
                    # Status effect type emojis
                    effect_emojis = {
                        "Burning": "🔥",
                        "Poisoned": "☠️",
                        "Bleeding": "💉",
                        "Frozen": "❄️",
                        "Slowed": "🐌",
                        "Cursed": "👿",
                        "Blinded": "👁️",
                        "Blessed": "✨",
                        "Enraged": "😡",
                        "Magic Shield": "🛡️",
                        "Haste": "⚡",
                        "Regenerating": "💚",
                        "Strength Boost": "💪",
                        "Defense Boost": "🛡️",
                        "Invisible": "👻",
                        "Fire Resistance": "🔥",
                        "Torch Light": "🔦",
                        "Rope Escape": "🪢",
                        "Map Vision": "🗺️"
                    }
                    
                    for i, effect in enumerate(active_effects[:8]):  # Limit to 8 effects to avoid overflow
                        effect_x = effect_start_x + (i * effect_spacing)
                        effect_y = effect_start_y
                        
                        # Draw effect background (slightly transparent)
                        effect_bg = pygame.Surface((effect_size, effect_size))
                        effect_bg.set_alpha(180)
                        effect_bg.fill(effect["color"])
                        screen.blit(effect_bg, (effect_x, effect_y))
                        
                        # Draw border
                        pygame.draw.rect(screen, (255, 255, 255), (effect_x, effect_y, effect_size, effect_size), 2)
                        
                        # Draw effect emoji/icon
                        emoji = effect_emojis.get(effect["name"], "●")
                        try:
                            emoji_text = effect_font.render(emoji, True, (255, 255, 255))
                            emoji_rect = emoji_text.get_rect(center=(effect_x + effect_size // 2, effect_y + effect_size // 2 - 5))
                            screen.blit(emoji_text, emoji_rect)
                        except:
                            # Fallback: draw colored circle if emoji fails
                            pygame.draw.circle(screen, (255, 255, 255), (effect_x + effect_size // 2, effect_y + effect_size // 2 - 5), 8)
                        
                        # Draw remaining time
                        remaining = max(0, effect["remaining_time"])
                        time_text = timer_font.render(f"{remaining:.1f}s", True, (255, 255, 255))
                        time_rect = time_text.get_rect(center=(effect_x + effect_size // 2, effect_y + effect_size - 8))
                        
                        # Draw black outline for better readability
                        outline_positions = [(-1,-1), (-1,1), (1,-1), (1,1)]
                        for dx, dy in outline_positions:
                            outline_text = timer_font.render(f"{remaining:.1f}s", True, (0, 0, 0))
                            screen.blit(outline_text, (time_rect.x + dx, time_rect.y + dy))
                        
                        screen.blit(time_text, time_rect)
                        
                        # Draw effect name on hover
                        mouse_pos = pygame.mouse.get_pos()
                        if effect_x <= mouse_pos[0] <= effect_x + effect_size and effect_y <= mouse_pos[1] <= effect_y + effect_size:
                            # Draw tooltip
                            tooltip_font = get_font(None, 16)
                            tooltip_lines = [
                                effect["name"],
                                effect["description"]
                            ]
                            
                            # Calculate tooltip size
                            max_width = max([tooltip_font.size(line)[0] for line in tooltip_lines]) + 20
                            tooltip_height = len(tooltip_lines) * 22 + 10
                            
                            # Position tooltip above effect icon
                            tooltip_x = effect_x - (max_width - effect_size) // 2
                            tooltip_y = effect_y - tooltip_height - 5
                            
                            # Keep tooltip on screen
                            tooltip_x = max(5, min(tooltip_x, screen.get_width() - max_width - 5))
                            tooltip_y = max(5, tooltip_y)
                            
                            # Draw tooltip background
                            tooltip_bg = pygame.Surface((max_width, tooltip_height))
                            tooltip_bg.set_alpha(230)
                            tooltip_bg.fill((30, 30, 30))
                            screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
                            
                            # Draw tooltip border
                            pygame.draw.rect(screen, effect["color"], (tooltip_x, tooltip_y, max_width, tooltip_height), 2)
                            
                            # Draw tooltip text
                            for j, line in enumerate(tooltip_lines):
                                line_color = effect["color"] if j == 0 else (200, 200, 200)
                                line_text = tooltip_font.render(line, True, line_color)
                                screen.blit(line_text, (tooltip_x + 10, tooltip_y + 5 + j * 22))
            
            # === DISEASE STATUS DISPLAY (Below status effects) ===
            if hasattr(player, 'disease_manager'):
                active_diseases = disease_manager.get_entity_diseases("player")
                if active_diseases:
                    # Disease display settings
                    disease_size = 40
                    disease_spacing = 45
                    disease_start_x = bar_x
                    disease_start_y = bar_y + bar_spacing * 3 + 65  # Below status effects
                    
                    disease_font = get_font(None, 16)
                    disease_timer_font = get_font(None, 14)
                    
                    # Disease type emojis and colors
                    disease_display = {
                        "COMMON": {"emoji": "🤧", "color": (100, 200, 100)},
                        "DEADLY": {"emoji": "☠️", "color": (200, 50, 50)},
                        "STD": {"emoji": "💔", "color": (200, 100, 200)},
                        "MAGICAL": {"emoji": "✨", "color": (100, 100, 255)},
                        "MAGICAL_STD": {"emoji": "💜", "color": (150, 50, 200)}
                    }
                    
                    # Stage colors (green → yellow → red)
                    stage_colors = {
                        "INCUBATION": (100, 200, 100),
                        "STAGE_1": (150, 200, 50),
                        "STAGE_2": (200, 200, 50),
                        "STAGE_3": (255, 150, 50),
                        "STAGE_4": (255, 50, 50),
                        "RECOVERY": (100, 150, 255)
                    }
                    
                    for i, disease_infection in enumerate(active_diseases[:6]):  # Max 6 diseases
                        disease = disease_infection.disease
                        disease_x = disease_start_x + (i * disease_spacing)
                        disease_y = disease_start_y
                        
                        # Get display info
                        disease_type = disease.type.name
                        stage_name = disease_infection.current_stage.name
                        display_info = disease_display.get(disease_type, {"emoji": "🦠", "color": (150, 150, 150)})
                        stage_color = stage_colors.get(stage_name, (150, 150, 150))
                        
                        # Draw disease background (stage-based color)
                        disease_bg = pygame.Surface((disease_size, disease_size))
                        disease_bg.set_alpha(200)
                        disease_bg.fill(stage_color)
                        screen.blit(disease_bg, (disease_x, disease_y))
                        
                        # Draw border (type-based color)
                        pygame.draw.rect(screen, display_info["color"], 
                                       (disease_x, disease_y, disease_size, disease_size), 3)
                        
                        # Draw emoji
                        emoji_text = disease_font.render(display_info["emoji"], True, (255, 255, 255))
                        emoji_rect = emoji_text.get_rect(center=(disease_x + disease_size // 2, disease_y + disease_size // 2))
                        screen.blit(emoji_text, emoji_rect)
                        
                        # Draw stage indicator (small text at bottom)
                        stage_num = stage_name.split("_")[-1] if "STAGE_" in stage_name else stage_name[:3]
                        stage_text = disease_timer_font.render(stage_num, True, (255, 255, 255))
                        stage_rect = stage_text.get_rect(center=(disease_x + disease_size // 2, disease_y + disease_size - 8))
                        screen.blit(stage_text, stage_rect)
                        
                        # Tooltip on hover
                        mouse_pos = pygame.mouse.get_pos()
                        if (disease_x <= mouse_pos[0] <= disease_x + disease_size and 
                            disease_y <= mouse_pos[1] <= disease_y + disease_size):
                            
                            # Create detailed tooltip
                            tooltip_lines = [
                                disease.name,
                                f"Stage: {stage_name}",
                                f"Day {disease_infection.days_elapsed}/{disease.total_duration_days}"
                            ]
                            
                            # Add current effects
                            effects = disease_infection.get_current_effects()
                            if effects:
                                tooltip_lines.append("Effects:")
                                for effect_name, effect_value in list(effects.items())[:3]:  # Max 3 effects
                                    effect_str = effect_name.replace("_", " ").title()
                                    if isinstance(effect_value, float) and effect_value < 1:
                                        effect_str += f": -{int(effect_value * 100)}%"
                                    elif isinstance(effect_value, (int, float)):
                                        effect_str += f": {effect_value}"
                                    tooltip_lines.append(f"  {effect_str}")
                            
                            # Add cure info
                            if disease.is_curable:
                                cure_methods = ", ".join(disease.cures[:2])
                                tooltip_lines.append(f"Cure: {cure_methods}")
                            else:
                                tooltip_lines.append("⚠️ INCURABLE")
                            
                            tooltip_font = get_font(None, 18)
                            max_width = max(tooltip_font.size(line)[0] for line in tooltip_lines) + 20
                            tooltip_height = len(tooltip_lines) * 22 + 10
                            
                            tooltip_x = disease_x + disease_size + 5
                            tooltip_y = disease_y - 10
                            
                            # Keep tooltip on screen
                            if tooltip_x + max_width > config.SCREEN_WIDTH:
                                tooltip_x = disease_x - max_width - 5
                            if tooltip_y + tooltip_height > config.SCREEN_HEIGHT:
                                tooltip_y = config.SCREEN_HEIGHT - tooltip_height
                            
                            # Draw tooltip background
                            tooltip_bg = pygame.Surface((max_width, tooltip_height))
                            tooltip_bg.set_alpha(240)
                            tooltip_bg.fill((20, 20, 20))
                            screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
                            
                            # Draw tooltip border
                            pygame.draw.rect(screen, display_info["color"], 
                                           (tooltip_x, tooltip_y, max_width, tooltip_height), 2)
                            
                            # Draw tooltip text
                            for j, line in enumerate(tooltip_lines):
                                line_color = display_info["color"] if j == 0 else (200, 200, 200)
                                line_text = tooltip_font.render(line, True, line_color)
                                screen.blit(line_text, (tooltip_x + 10, tooltip_y + 5 + j * 22))
        
        # Draw stealth indicator (when in stealth mode) - positioned right of health bars
        if not show_inventory and not show_equipment and not smart_inventory_ui.active:
            detections = getattr(player, 'detected_by_npcs', [])
            # Position to the right of health/mana/stamina bars (which end around x=220)
            stealth_indicator_ui.draw(screen, player, detections, offset_x=240, offset_y=20)
        
        # Draw hotbar (always visible unless in menu)
        if not show_inventory and not show_equipment and not smart_inventory_ui.active and not show_crafting_menu:
            hotbar_font = get_font(None, 18)
            hotbar_ui.draw(screen, hotbar_system, hotbar_font)
            
            # Draw hotbar tooltip on hover
            mouse_pos = pygame.mouse.get_pos()
            hotbar_ui.draw_tooltip(screen, hotbar_system, hotbar_font, mouse_pos)
            
            # Draw experience bar below hotbar
            xp_bar_height = 12
            xp_bar_y = config.SCREEN_HEIGHT - 100  # Below hotbar (hotbar is at -90)
            xp_bar_width = 400
            xp_bar_x = (config.SCREEN_WIDTH - xp_bar_width) // 2
            
            # Calculate XP progress
            xp_needed = player.level * 100
            xp_ratio = min(1.0, player.xp / xp_needed if xp_needed > 0 else 0)
            
            # Draw XP bar background (dark gray)
            pygame.draw.rect(screen, (40, 40, 40), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
            
            # Draw XP bar fill (subtle gold gradient)
            if xp_ratio > 0:
                fill_width = int(xp_bar_width * xp_ratio)
                pygame.draw.rect(screen, (180, 140, 60), (xp_bar_x, xp_bar_y, fill_width, xp_bar_height))
            
            # Draw XP bar border
            pygame.draw.rect(screen, (100, 100, 100), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), 1)
            
            # Draw XP text (small, subtle)
            xp_font = get_font(None, 14)
            xp_text = f"Level {player.level} - XP: {int(player.xp)}/{xp_needed}"
            xp_surface = xp_font.render(xp_text, True, (200, 200, 200))
            xp_text_x = xp_bar_x + (xp_bar_width - xp_surface.get_width()) // 2
            xp_text_y = xp_bar_y - 18
            screen.blit(xp_surface, (xp_text_x, xp_text_y))
        
        # Draw set bonus display (always visible when bonuses are active)
        if not show_inventory and not show_equipment and not smart_inventory_ui.active and not boss_loot_preview.active:
            try:
                # Calculate active set bonuses from equipped items
                active_bonuses = enhanced_loot.apply_set_bonuses(player, player.equipment)
                if active_bonuses:
                    set_bonus_display.draw(screen, active_bonuses)
            except Exception as e:
                logger.error(f"[LOOT] Error drawing set bonuses: {e}")
        
        # Draw boss loot preview (highest priority, blocks all input)
        if boss_loot_preview.active:
            boss_loot_preview.draw(screen)
        
        # Draw dungeon variety UI elements
        if in_dungeon and current_dungeon:
            # Draw dungeon info (modifier and difficulty)
            if not show_inventory and not show_equipment and not smart_inventory_ui.active:
                dungeon_info_font = get_font(None, 20)
                dungeon_info_ui.draw(screen, current_dungeon, dungeon_info_font)
            
            # Draw speed run timer
            speed_run_timer_ui.draw(screen)
            
            # Draw trap warnings
            trap_warning_ui.draw(screen, camera_x, camera_y)
            
            # Draw secret discovery message
            secret_discovered_ui.draw(screen)
        
        # Draw summon info UI
        if not show_inventory and not show_equipment and not smart_inventory_ui.active:
            active_summons = summoning_system.get_active_summons()
            summon_font = get_font(None, 18)
            summon_info_ui.draw(screen, active_summons, summon_font)
        
        # Draw inn offer dialog (highest priority)
        if inn_offer_dialog['active']:
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            dialog_width = 650
            dialog_height = 350
            dialog_x = (config.SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (config.SCREEN_HEIGHT - dialog_height) // 2
            
            pygame.draw.rect(screen, (40, 40, 50), (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(screen, (200, 150, 50), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
            
            title_font = get_font(None, 36)
            title = title_font.render("💸 NO PROPERTY OWNED 💸", True, (255, 200, 50))
            screen.blit(title, (dialog_x + (dialog_width - title.get_width()) // 2, dialog_y + 20))
            
            msg_font = get_font(None, 24)
            messages = [
                "You do not currently own any property.",
                "WOW how poor of you!",
                "",
                "We can send your ass to the inn,",
                "maybe you can try your luck there.",
                "",
                "Travel to the Inn?"
            ]
            
            y_offset = dialog_y + 80
            for msg in messages:
                text = msg_font.render(msg, True, (220, 220, 220))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, y_offset))
                y_offset += 35
            
            option_font = get_font(None, 26)
            options = [
                "[Y] Yes, send me to the inn",
                "[N] No, go back"
            ]
            
            y_offset += 10
            for option in options:
                text = option_font.render(option, True, (100, 255, 100))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, y_offset))
                y_offset += 30
        
        # Draw curfew warning dialog (highest priority overlay)
        elif curfew_warning_dialog['active']:
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            dialog_width = 600
            dialog_height = 300
            dialog_x = (config.SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (config.SCREEN_HEIGHT - dialog_height) // 2
            
            pygame.draw.rect(screen, (40, 40, 50), (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(screen, (200, 50, 50), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
            
            title_font = get_font(None, 36)
            title = title_font.render("⚠️ CURFEW IN EFFECT ⚠️", True, (255, 200, 50))
            screen.blit(title, (dialog_x + (dialog_width - title.get_width()) // 2, dialog_y + 20))
            
            msg_font = get_font(None, 24)
            town_name = curfew_warning_dialog['town_name']
            messages = [
                f"{town_name} has an active curfew!",
                f"Curfew Hours: 5PM - 2AM",
                "",
                "If you enter, guards may spot you and",
                "fine you 300g for curfew violation.",
                "",
                "What would you like to do?"
            ]
            
            y_offset = dialog_y + 70
            for msg in messages:
                text = msg_font.render(msg, True, (220, 220, 220))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, y_offset))
                y_offset += 30
            
            option_font = get_font(None, 22)
            options = [
                "[ENTER] Enter anyway (stay hidden from guards)",
                "[F] Fast Travel to safe location",
                "[ESC] Cancel"
            ]
            
            y_offset += 10
            for option in options:
                text = option_font.render(option, True, (100, 255, 100))
                screen.blit(text, (dialog_x + 20, y_offset))
                y_offset += 25
        
        # Draw stick stacking confirmation dialog
        if stick_stack_confirmation['active']:
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            dialog_width = 550
            dialog_height = 250
            dialog_x = (config.SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (config.SCREEN_HEIGHT - dialog_height) // 2
            
            pygame.draw.rect(screen, (40, 35, 30), (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(screen, (200, 150, 50), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
            
            title_font = get_font(None, 32)
            title = title_font.render("⚠️ Stack Stick? ⚠️", True, (255, 200, 50))
            screen.blit(title, (dialog_x + (dialog_width - title.get_width()) // 2, dialog_y + 20))
            
            msg_font = get_font(None, 22)
            equipped_weapon = player.equipment.get('weapon') or player.equipment.get('main_hand')
            current_stack = equipped_weapon.stats.get('stack_count', 1) if equipped_weapon and hasattr(equipped_weapon, 'stats') else 1
            new_stack = current_stack + 1
            current_damage = 2 + (current_stack - 1) * 0.5
            new_damage = 2 + current_stack * 0.5
            
            messages = [
                f"Current: {current_stack} stick(s) - {current_damage:.1f} damage",
                f"After stacking: {new_stack} sticks - {new_damage:.1f} damage",
                "",
                "⚠️ Warning: This permanently combines the sticks!",
                "Sticks are also used in many crafting recipes.",
                "Are you sure you want to stack this stick?"
            ]
            
            y_offset = dialog_y + 70
            for message in messages:
                text = msg_font.render(message, True, (220, 220, 220))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, y_offset))
                y_offset += 28
            
            # Options
            option_font = get_font(None, 24)
            options_text = ["[Y] Yes, stack the stick", "[N] No, keep it separate"]
            y_offset += 10
            for option in options_text:
                text = option_font.render(option, True, (100, 255, 100))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, y_offset))
                y_offset += 30
        
        # Draw fast travel menu
        elif fast_travel_menu['active']:
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            dialog_width = 500
            dialog_height = 400
            dialog_x = (config.SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (config.SCREEN_HEIGHT - dialog_height) // 2
            
            pygame.draw.rect(screen, (40, 40, 50), (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(screen, (100, 150, 255), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
            
            title_font = get_font(None, 36)
            title = title_font.render("Fast Travel", True, (100, 200, 255))
            screen.blit(title, (dialog_x + (dialog_width - title.get_width()) // 2, dialog_y + 20))
            
            available_locations = fast_travel_system.get_available_locations()
            if available_locations:
                y_offset = dialog_y + 80
                for idx, location_name in enumerate(available_locations):
                    location_info = fast_travel_system.get_location_info(location_name)
                    is_selected = (idx == fast_travel_menu['selected_idx'])
                    
                    if is_selected:
                        pygame.draw.rect(screen, (80, 80, 100), (dialog_x + 20, y_offset - 5, dialog_width - 40, 35))
                    
                    loc_font = get_font(None, 26)
                    color = (255, 255, 100) if is_selected else (220, 220, 220)
                    text = loc_font.render(f"> {location_name}", True, color)
                    screen.blit(text, (dialog_x + 30, y_offset))
                    
                    if location_info and location_info.get('description'):
                        desc_font = get_font(None, 18)
                        desc_text = desc_font.render(location_info['description'], True, (180, 180, 180))
                        screen.blit(desc_text, (dialog_x + 50, y_offset + 22))
                    
                    y_offset += 50
            else:
                no_loc_font = get_font(None, 24)
                text = no_loc_font.render("No locations available", True, (200, 100, 100))
                screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, dialog_y + 150))
            
            controls_font = get_font(None, 20)
            controls = "[↑/↓] Select   [ENTER] Travel   [ESC] Cancel"
            text = controls_font.render(controls, True, (150, 150, 150))
            screen.blit(text, (dialog_x + (dialog_width - text.get_width()) // 2, dialog_y + dialog_height - 40))
        
        # Apply nighttime darkness overlay (GLOBAL - applies to entire world, towns, and building interiors)
        current_hour, current_minute = game_time.get_time_hm()
        
        # Nighttime is 5PM (17:00) to 2AM (02:00)
        if current_hour >= 17 or current_hour <= 2:
            # Calculate darkness intensity based on time of night
            # Darkest at midnight (0:00), lighter at dusk/dawn
            if current_hour >= 17:
                # Evening: 17:00 to 23:59
                # Gradually get darker from 17:00 to 23:00
                progress = (current_hour - 17) / 6.0  # 0.0 at 5PM, 1.0 at 11PM
            else:
                # Early morning: 00:00 to 02:00
                # Gradually get lighter from 00:00 to 02:00
                progress = 1.0 - (current_hour + (current_minute / 60.0)) / 2.0  # 1.0 at midnight, 0.0 at 2AM
            
            # Darkness ranges from 100 (dusk/dawn) to 180 (midnight) - increased for more visible darkness
            darkness_alpha = int(100 + (progress * 80))
            
            # Create semi-transparent dark overlay
            night_overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            night_overlay.set_alpha(darkness_alpha)
            night_overlay.fill((0, 0, 30))  # Dark blue-black tint
            screen.blit(night_overlay, (0, 0))
        
        # Draw death screen (on top of everything)
        if show_death_screen:
            # Dark overlay
            overlay = get_cached_surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Death message box
            box_width = 800
            box_height = 400
            box_x = config.SCREEN_WIDTH // 2 - box_width // 2
            box_y = config.SCREEN_HEIGHT // 2 - box_height // 2
            
            death_box = pygame.Surface((box_width, box_height))
            death_box.fill((40, 20, 20))
            pygame.draw.rect(death_box, (150, 30, 30), (0, 0, box_width, box_height), 4)
            screen.blit(death_box, (box_x, box_y))
            
            # Death message
            death_font = get_font(None, 48)
            death_text = death_font.render("You have died", True, (200, 50, 50))
            screen.blit(death_text, (config.SCREEN_WIDTH // 2 - death_text.get_width() // 2, box_y + 60))
            
            insult_font = get_font(None, 32)
            insult_text = insult_font.render("you worthless, weak, pathetic fool", True, (180, 80, 80))
            screen.blit(insult_text, (config.SCREEN_WIDTH // 2 - insult_text.get_width() // 2, box_y + 120))
            
            # Options
            option_font = get_font(None, 36)
            options = ["Load Save", "Return to Main Menu"]
            
            for i, option in enumerate(options):
                y_pos = box_y + 220 + (i * 60)
                color = (255, 255, 100) if i == death_screen_option else (200, 200, 200)
                
                # Selection indicator
                if i == death_screen_option:
                    indicator = option_font.render(">", True, (255, 255, 100))
                    screen.blit(indicator, (box_x + 150, y_pos))
                
                option_text = option_font.render(option, True, color)
                screen.blit(option_text, (box_x + 200, y_pos))
            
            # Instructions
            inst_font = get_font(None, 24)
            inst_text = inst_font.render("Use ARROW KEYS to select, ENTER to confirm", True, (150, 150, 150))
            screen.blit(inst_text, (config.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 40))
        
        pygame.display.flip()
        
        # OPTIMIZATION: Use adaptive frame limiter instead of fixed clock.tick()
        frame_dt = frame_limiter.update(clock)
        
        # Update performance monitoring
        update_performance_monitoring(frame_dt, current_fps)

    # Save on exit using enhanced save system (auto-save slot)
    # Save tutorial manager state before saving
    player.tutorials_shown = tutorial_manager.tutorials_shown
    save_integrator.quick_save()
    
    # Update and save leaderboards on exit
    leaderboard_system.update_all_skills(player.name, player.skills_manager)
    leaderboard_system.save()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Game closed by user")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        # Critical error wrapper - catch all exceptions to prevent silent crashes
        logger.critical(f"Fatal error in main game loop: {type(e).__name__}: {e}", exc_info=True)
        
        # Try to show error dialog to user
        try:
            import traceback
            error_msg = f"A critical error occurred:\n\n{type(e).__name__}: {str(e)}\n\nCheck logs for details."
            print("\n" + "="*60)
            print("FATAL ERROR")
            print("="*60)
            print(error_msg)
            print("\nFull traceback:")
            traceback.print_exc()
            print("="*60)
            
            # Try to display pygame error screen if pygame is initialized
            try:
                pygame.init()
                screen = pygame.display.set_mode((800, 600))
                font = pygame.font.SysFont('arial', 16)
                screen.fill((40, 40, 40))
                
                # Draw error message
                y = 50
                title_font = pygame.font.SysFont('arial', 24, bold=True)
                title = title_font.render("Critical Error - Game Crashed", True, (255, 100, 100))
                screen.blit(title, (400 - title.get_width()//2, y))
                y += 60
                
                lines = [
                    f"Error Type: {type(e).__name__}",
                    f"Error Message: {str(e)[:100]}",
                    "",
                    "The game has crashed due to an unexpected error.",
                    "Please check the game logs for detailed information.",
                    "",
                    "Press any key or close this window to exit."
                ]
                
                for line in lines:
                    text = font.render(line, True, (255, 255, 255))
                    screen.blit(text, (50, y))
                    y += 25
                
                pygame.display.flip()
                
                # Wait for user to acknowledge
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                            waiting = False
            except:
                pass  # If pygame error screen fails, just print to console
        except:
            pass  # If error display fails, just exit
        
        # Clean up and exit
        try:
            pygame.quit()
        except:
            pass
        sys.exit(1)

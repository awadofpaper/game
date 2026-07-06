"""
Disease System - Comprehensive illness simulation with realistic spread mechanics
Includes: Common diseases, plague, STDs, magical diseases, NPC behaviors, quarantine
"""

import random
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DiseaseType(Enum):
    """Categories of diseases"""
    COMMON = "common"          # Cold, flu
    DEADLY = "deadly"          # Plague, severe infections
    STD = "std"                # Sexually transmitted
    MAGICAL = "magical"        # Fire sneezing, arcane flu
    MAGICAL_STD = "magical_std"  # Magical sexually transmitted


class DiseaseStage(Enum):
    """Disease progression stages"""
    INCUBATION = "incubation"  # Infected but no symptoms yet
    STAGE_1 = "stage_1"        # Mild symptoms
    STAGE_2 = "stage_2"        # Moderate symptoms
    STAGE_3 = "stage_3"        # Severe symptoms
    STAGE_4 = "stage_4"        # Critical/deadly (plague only)
    RECOVERY = "recovery"       # Healing phase


class Disease:
    """Defines a disease with all its properties"""
    
    def __init__(self, disease_id: str, name: str, disease_type: DiseaseType,
                 base_infection_rate: float, mortality_rate: float,
                 total_duration_days: float, stages: int,
                 symptoms: Dict, cures: List[str], cure_cost: int = 0,
                 requires_ingredients: bool = False, is_curable: bool = True,
                 incubation_days: float = 0.0):
        self.disease_id = disease_id
        self.name = name
        self.type = disease_type
        self.base_infection_rate = base_infection_rate  # Base chance to catch
        self.mortality_rate = mortality_rate  # Chance to die if untreated
        self.total_duration_days = total_duration_days
        self.stages = stages
        self.stage_duration = total_duration_days / stages if stages > 0 else total_duration_days
        self.symptoms = symptoms  # Dict of stage -> effects
        self.cures = cures  # List of cure methods: 'rest', 'potion', 'temple', 'mage', 'time'
        self.cure_cost = cure_cost  # Dubloons to cure
        self.requires_ingredients = requires_ingredients  # Need dungeon loot?
        self.is_curable = is_curable  # Can it be cured or only survived?
        self.incubation_days = incubation_days  # Days before symptoms appear
        
    def get_stage_effects(self, stage: DiseaseStage) -> Dict:
        """Get effects for a specific stage"""
        return self.symptoms.get(stage, {})


# Disease Definitions - Based on real-world data scaled to game time

DISEASE_DEFINITIONS = {
    # ===== COMMON DISEASES =====
    "common_cold": Disease(
        disease_id="common_cold",
        name="Common Cold",
        disease_type=DiseaseType.COMMON,
        base_infection_rate=0.05,  # 5% base chance in cold weather
        mortality_rate=0.0,  # Non-lethal
        total_duration_days=9.0,  # 9 days like real life
        stages=3,
        incubation_days=1.0,  # 1 day before symptoms
        symptoms={
            DiseaseStage.INCUBATION: {},
            DiseaseStage.STAGE_1: {
                "max_hp_reduction": 0.05,  # -5% max HP
                "stamina_regen_reduction": 0.10,  # -10% stamina regen
                "visual_tint": (255, 250, 245),  # Slight pale
                "cough_chance": 0.02,  # 2% chance per second to cough
                "description": "Mild sniffles and fatigue"
            },
            DiseaseStage.STAGE_2: {
                "max_hp_reduction": 0.10,  # -10% max HP
                "stamina_regen_reduction": 0.20,  # -20% stamina regen
                "speed_multiplier": 0.95,  # -5% movement speed
                "visual_tint": (250, 245, 240),
                "cough_chance": 0.05,
                "description": "Persistent cough and weakness"
            },
            DiseaseStage.STAGE_3: {
                "max_hp_reduction": 0.15,  # -15% max HP
                "stamina_regen_reduction": 0.25,  # -25% stamina regen
                "speed_multiplier": 0.90,  # -10% movement speed
                "visual_tint": (245, 240, 235),
                "cough_chance": 0.08,
                "description": "Severe cold symptoms, gradually improving"
            },
            DiseaseStage.RECOVERY: {
                "max_hp_reduction": 0.05,
                "description": "Recovering from cold"
            }
        },
        cures=["rest", "herbs", "time"],  # Passes naturally
        cure_cost=50,  # Herbs cost
        is_curable=True
    ),
    
    "flu": Disease(
        disease_id="flu",
        name="Flu",
        disease_type=DiseaseType.COMMON,
        base_infection_rate=0.02,  # 2% base chance in cold weather
        mortality_rate=0.001,  # 0.1% mortality (real-world rate)
        total_duration_days=5.0,  # 5 days
        stages=3,
        incubation_days=1.5,  # 1-2 days before symptoms
        symptoms={
            DiseaseStage.INCUBATION: {},
            DiseaseStage.STAGE_1: {
                "max_hp_reduction": 0.10,  # -10% max HP
                "stamina_regen_reduction": 0.30,  # -30% stamina regen
                "max_stamina_reduction": 0.15,  # -15% max stamina
                "speed_multiplier": 0.85,  # -15% movement speed
                "visual_tint": (245, 240, 230),
                "cough_chance": 0.10,
                "description": "Fever, body aches, and fatigue"
            },
            DiseaseStage.STAGE_2: {
                "max_hp_reduction": 0.20,  # -20% max HP
                "stamina_regen_reduction": 0.50,  # -50% stamina regen
                "max_stamina_reduction": 0.25,  # -25% max stamina
                "speed_multiplier": 0.75,  # -25% movement speed
                "attack_fumble_chance": 0.05,  # 5% chance to fumble attacks
                "visual_tint": (240, 235, 220),
                "cough_chance": 0.15,
                "description": "Severe flu symptoms, high fever"
            },
            DiseaseStage.STAGE_3: {
                "max_hp_reduction": 0.15,  # -15% max HP
                "stamina_regen_reduction": 0.30,  # -30% stamina regen
                "max_stamina_reduction": 0.15,  # -15% max stamina
                "speed_multiplier": 0.85,  # -15% movement speed
                "visual_tint": (245, 240, 230),
                "cough_chance": 0.08,
                "description": "Flu symptoms subsiding"
            }
        },
        cures=["special_food", "potion", "temple", "time"],
        cure_cost=200,
        is_curable=True
    ),
    
    # ===== PLAGUE (Not Curable, Only Survivable) =====
    "plague": Disease(
        disease_id="plague",
        name="The Plague",
        disease_type=DiseaseType.DEADLY,
        base_infection_rate=0.001,  # 0.1% random event base
        mortality_rate=0.30,  # 30% base mortality (Black Death rate)
        total_duration_days=7.0,  # 7 days to death or survival
        stages=4,
        incubation_days=2.0,  # 2 days before symptoms
        symptoms={
            DiseaseStage.INCUBATION: {
                "description": "Infected but no symptoms yet"
            },
            DiseaseStage.STAGE_1: {
                "max_hp_reduction": 0.10,  # -10% max HP
                "stamina_regen_reduction": 0.30,
                "visual_tint": (240, 250, 240),  # Slight green tint
                "cough_chance": 0.05,
                "description": "Mild fever and weakness"
            },
            DiseaseStage.STAGE_2: {
                "max_hp_reduction": 0.25,  # -25% max HP
                "stamina_regen_reduction": 0.50,
                "max_stamina_reduction": 0.20,
                "speed_multiplier": 0.80,
                "visual_tint": (220, 240, 220),  # Moderate green tint
                "cough_chance": 0.12,
                "description": "Fever, painful swellings (buboes)"
            },
            DiseaseStage.STAGE_3: {
                "max_hp_reduction": 0.50,  # -50% max HP
                "stamina_regen_reduction": 0.70,
                "max_stamina_reduction": 0.40,
                "speed_multiplier": 0.60,
                "attack_fumble_chance": 0.10,
                "visual_tint": (200, 230, 200),  # Strong green tint
                "cough_chance": 0.20,
                "description": "Severe plague symptoms, very sick"
            },
            DiseaseStage.STAGE_4: {
                "max_hp_reduction": 0.75,  # -75% max HP
                "stamina_regen_reduction": 0.90,
                "max_stamina_reduction": 0.60,
                "speed_multiplier": 0.40,
                "attack_fumble_chance": 0.20,
                "hp_drain_per_minute": 2.0,  # Constant HP drain
                "visual_tint": (180, 220, 180),  # Very green/sickly
                "cough_chance": 0.30,
                "description": "Critical condition - death imminent without survival"
            }
        },
        cures=[],  # No cure, only protective gear and survival chance
        cure_cost=0,
        is_curable=False  # Cannot be cured, must survive or die
    ),
    
    # ===== STDs (Sexually Transmitted Diseases) =====
    "draining_fever": Disease(
        disease_id="draining_fever",
        name="Draining Fever",
        disease_type=DiseaseType.STD,
        base_infection_rate=0.08,  # 8% initial population
        mortality_rate=0.0,  # Not deadly but permanent if untreated long-term
        total_duration_days=999.0,  # Permanent until cured
        stages=2,
        incubation_days=3.0,  # 3 days before symptoms
        symptoms={
            DiseaseStage.INCUBATION: {},
            DiseaseStage.STAGE_1: {
                "stamina_drain_per_minute": 0.5,  # Constant stamina drain
                "stamina_regen_reduction": 0.20,
                "description": "Persistent fatigue and weakness"
            },
            DiseaseStage.STAGE_2: {
                "stamina_drain_per_minute": 1.0,  # Worse drain
                "stamina_regen_reduction": 0.40,
                "max_stamina_reduction": 0.15,
                "permanent_risk": True,  # Long-term = permanent effects
                "description": "Chronic exhaustion (untreated may become permanent)"
            }
        },
        cures=["temple_night"],  # Temple at night only
        cure_cost=300,
        is_curable=True
    ),
    
    "mana_sickness": Disease(
        disease_id="mana_sickness",
        name="Mana Sickness",
        disease_type=DiseaseType.STD,
        base_infection_rate=0.08,
        mortality_rate=0.0,
        total_duration_days=999.0,
        stages=2,
        incubation_days=3.0,
        symptoms={
            DiseaseStage.INCUBATION: {},
            DiseaseStage.STAGE_1: {
                "mana_drain_per_minute": 0.5,
                "mana_regen_reduction": 0.20,
                "description": "Mana feels unstable"
            },
            DiseaseStage.STAGE_2: {
                "mana_drain_per_minute": 1.0,
                "mana_regen_reduction": 0.40,
                "max_mana_reduction": 0.15,
                "permanent_risk": True,
                "description": "Severe mana instability (may become permanent)"
            }
        },
        cures=["temple_night"],
        cure_cost=300,
        is_curable=True
    ),
    
    "burden_disease": Disease(
        disease_id="burden_disease",
        name="Burden Disease",
        disease_type=DiseaseType.STD,
        base_infection_rate=0.08,
        mortality_rate=0.0,
        total_duration_days=999.0,
        stages=2,
        incubation_days=3.0,
        symptoms={
            DiseaseStage.INCUBATION: {},
            DiseaseStage.STAGE_1: {
                "carry_capacity_reduction": 0.15,  # -15% carry capacity
                "speed_multiplier": 0.95,
                "description": "Everything feels heavier"
            },
            DiseaseStage.STAGE_2: {
                "carry_capacity_reduction": 0.30,  # -30% carry capacity
                "speed_multiplier": 0.90,
                "max_stamina_reduction": 0.10,
                "permanent_risk": True,
                "description": "Chronic weakness (may become permanent)"
            }
        },
        cures=["temple_night"],
        cure_cost=300,
        is_curable=True
    ),
    
    # ===== MAGICAL DISEASES =====
    "fire_sneezing": Disease(
        disease_id="fire_sneezing",
        name="Fire Sneezing Curse",
        disease_type=DiseaseType.MAGICAL,
        base_infection_rate=0.005,  # Rare magical disease
        mortality_rate=0.0,
        total_duration_days=14.0,  # 2 weeks
        stages=1,
        incubation_days=0.5,
        symptoms={
            DiseaseStage.STAGE_1: {
                "fire_sneeze_chance": 0.001,  # 0.1% chance per second to sneeze fire
                "fire_sneeze_damage": 15,  # Damage to nearby NPCs/entities
                "fire_sneeze_radius": 100,  # Pixels
                "crime_on_hit": True,  # Counts as assault if hits NPC
                "visual_effect": "fire_particle",
                "description": "Uncontrollable fire sneezing - avoid crowds!"
            }
        },
        cures=["mage", "dungeon_ingredient"],
        cure_cost=1000,
        requires_ingredients=True,
        is_curable=True
    ),
    
    "arcane_flu": Disease(
        disease_id="arcane_flu",
        name="Arcane Flu",
        disease_type=DiseaseType.MAGICAL,
        base_infection_rate=0.005,
        mortality_rate=0.0,
        total_duration_days=10.0,
        stages=1,
        incubation_days=1.0,
        symptoms={
            DiseaseStage.STAGE_1: {
                "float_on_sleep": True,  # Float during any sleep
                "fall_damage_percent": 0.30,  # 30% max HP fall damage
                "mana_regen_reduction": 0.30,
                "visual_effect": "float_particle",
                "description": "Magical instability causes floating during sleep"
            }
        },
        cures=["mage", "dungeon_ingredient"],
        cure_cost=1000,
        requires_ingredients=True,
        is_curable=True
    ),
    
    "shadow_plague": Disease(
        disease_id="shadow_plague",
        name="Shadow Plague",
        disease_type=DiseaseType.MAGICAL,
        base_infection_rate=0.003,
        mortality_rate=0.10,  # 10% mortality if untreated
        total_duration_days=12.0,
        stages=3,
        incubation_days=1.0,
        symptoms={
            DiseaseStage.STAGE_1: {
                "max_hp_reduction": 0.15,
                "visual_tint": (200, 200, 220),  # Dark purple tint
                "shadow_aura": True,
                "description": "Shadows seem to cling to you"
            },
            DiseaseStage.STAGE_2: {
                "max_hp_reduction": 0.30,
                "max_mana_reduction": 0.20,
                "visual_tint": (180, 180, 210),
                "shadow_aura": True,
                "light_sensitivity": True,  # Take damage in bright light
                "description": "Becoming one with shadows"
            },
            DiseaseStage.STAGE_3: {
                "max_hp_reduction": 0.50,
                "max_mana_reduction": 0.40,
                "visual_tint": (160, 160, 200),
                "shadow_aura": True,
                "light_sensitivity": True,
                "hp_drain_per_minute": 1.0,
                "description": "Critical shadow corruption"
            }
        },
        cures=["mage", "dungeon_ingredient"],
        cure_cost=1500,
        requires_ingredients=True,
        is_curable=True
    ),
    
    "mana_rot": Disease(
        disease_id="mana_rot",
        name="Mana Rot",
        disease_type=DiseaseType.MAGICAL,
        base_infection_rate=0.002,
        mortality_rate=0.05,
        total_duration_days=15.0,
        stages=3,
        incubation_days=2.0,
        symptoms={
            DiseaseStage.STAGE_1: {
                "max_mana_reduction": 0.20,
                "mana_regen_reduction": 0.40,
                "spell_cost_increase": 0.15,  # Spells cost 15% more mana
                "description": "Mana feels corrupted"
            },
            DiseaseStage.STAGE_2: {
                "max_mana_reduction": 0.40,
                "mana_regen_reduction": 0.70,
                "spell_cost_increase": 0.30,
                "spell_backfire_chance": 0.05,  # 5% chance spells backfire
                "description": "Mana is rotting away"
            },
            DiseaseStage.STAGE_3: {
                "max_mana_reduction": 0.70,
                "mana_regen_reduction": 0.90,
                "spell_cost_increase": 0.50,
                "spell_backfire_chance": 0.15,
                "mana_drain_per_minute": 2.0,
                "description": "Critical mana corruption"
            }
        },
        cures=["mage", "dungeon_ingredient"],
        cure_cost=2000,
        requires_ingredients=True,
        is_curable=True
    ),
    
    "fey_fever": Disease(
        disease_id="fey_fever",
        name="Fey Fever",
        disease_type=DiseaseType.MAGICAL,
        base_infection_rate=0.004,
        mortality_rate=0.0,
        total_duration_days=8.0,
        stages=2,
        incubation_days=0.5,
        symptoms={
            DiseaseStage.STAGE_1: {
                "hallucination_chance": 0.02,  # Visual hallucinations
                "random_teleport_chance": 0.001,  # Tiny chance to randomly teleport short distance
                "visual_tint": (255, 220, 255),  # Pink tint
                "description": "Reality feels unstable"
            },
            DiseaseStage.STAGE_2: {
                "hallucination_chance": 0.05,
                "random_teleport_chance": 0.003,
                "speed_multiplier": 1.10,  # Actually faster (fey energy)
                "attack_fumble_chance": 0.10,  # But less control
                "visual_tint": (255, 200, 255),
                "description": "Touched by fey magic - chaotic effects"
            }
        },
        cures=["mage", "dungeon_ingredient"],
        cure_cost=1200,
        requires_ingredients=True,
        is_curable=True
    ),
    
    # ===== MAGICAL STDs =====
    "soul_binding_sickness": Disease(
        disease_id="soul_binding_sickness",
        name="Soul Binding Sickness",
        disease_type=DiseaseType.MAGICAL_STD,
        base_infection_rate=0.03,  # 3% of magical population
        mortality_rate=0.0,
        total_duration_days=999.0,
        stages=2,
        incubation_days=5.0,
        symptoms={
            DiseaseStage.STAGE_1: {
                "max_hp_reduction": 0.10,
                "max_mana_reduction": 0.10,
                "soul_link_effect": True,  # Share damage with infected partner
                "description": "Souls becoming entwined"
            },
            DiseaseStage.STAGE_2: {
                "max_hp_reduction": 0.20,
                "max_mana_reduction": 0.20,
                "soul_link_effect": True,
                "permanent_risk": True,
                "description": "Dangerous soul bond (may become permanent)"
            }
        },
        cures=["mage", "temple_night"],
        cure_cost=500,
        requires_ingredients=False,
        is_curable=True
    ),
}


class ActiveDisease:
    """Represents an active disease infection on an entity"""
    
    def __init__(self, disease: Disease, infected_time: float):
        self.disease = disease
        self.infected_time = infected_time  # Game time when infected
        self.current_stage = DiseaseStage.INCUBATION if disease.incubation_days > 0 else DiseaseStage.STAGE_1
        self.stage_start_time = infected_time
        self.days_infected = 0.0
        self.has_been_treated = False
        self.will_survive = None  # For plague: None until determined, True/False after
        
    def update(self, current_time: float, time_multiplier: float = 1.0):
        """Update disease progression"""
        elapsed_days = (current_time - self.infected_time) * time_multiplier
        self.days_infected = elapsed_days
        
        # Check for stage progression
        if self.current_stage == DiseaseStage.INCUBATION:
            if elapsed_days >= self.disease.incubation_days:
                self.current_stage = DiseaseStage.STAGE_1
                self.stage_start_time = current_time
                logger.info(f"[DISEASE] {self.disease.name} symptoms appearing")
        
        elif self.current_stage == DiseaseStage.STAGE_1:
            if elapsed_days >= self.disease.incubation_days + self.disease.stage_duration:
                if self.disease.stages >= 2:
                    self.current_stage = DiseaseStage.STAGE_2
                    self.stage_start_time = current_time
        
        elif self.current_stage == DiseaseStage.STAGE_2:
            if elapsed_days >= self.disease.incubation_days + (self.disease.stage_duration * 2):
                if self.disease.stages >= 3:
                    self.current_stage = DiseaseStage.STAGE_3
                    self.stage_start_time = current_time
        
        elif self.current_stage == DiseaseStage.STAGE_3:
            if elapsed_days >= self.disease.incubation_days + (self.disease.stage_duration * 3):
                if self.disease.stages >= 4:
                    self.current_stage = DiseaseStage.STAGE_4
                    self.stage_start_time = current_time
                elif "time" in self.disease.cures:
                    # Natural recovery
                    self.current_stage = DiseaseStage.RECOVERY
                    self.stage_start_time = current_time
        
        elif self.current_stage == DiseaseStage.STAGE_4:
            # Critical stage - check for death/survival
            if elapsed_days >= self.disease.total_duration_days:
                # Plague resolution - live or die
                if self.will_survive is None:
                    logger.warning(f"[DISEASE] {self.disease.name} reached critical stage!")
                return True  # Signal resolution needed
        
        return False
    
    def get_current_effects(self) -> Dict:
        """Get current stage effects"""
        return self.disease.get_stage_effects(self.current_stage)
    
    def is_expired(self) -> bool:
        """Check if disease has run its course"""
        if "time" in self.disease.cures:
            # Natural recovery diseases
            return self.days_infected >= self.disease.total_duration_days
        return False


class DiseaseManager:
    """Manages disease spread, infection, and progression"""
    
    def __init__(self):
        self.infected_entities = {}  # entity_id: List[ActiveDisease]
        self.town_outbreak_status = {}  # town_name: {disease_id: outbreak_data}
        self.quarantine_zones = {}  # town_name: is_quarantined
        self.plague_survivors = set()  # entity_ids that survived plague
        self.global_infection_stats = {
            "total_infections": 0,
            "total_deaths": 0,
            "total_cures": 0,
            "active_outbreaks": 0
        }
        
    def infect_entity(self, entity_id: str, disease_id: str, source: str = "unknown") -> bool:
        """Infect an entity with a disease"""
        if disease_id not in DISEASE_DEFINITIONS:
            logger.error(f"[DISEASE] Unknown disease: {disease_id}")
            return False
        
        disease = DISEASE_DEFINITIONS[disease_id]
        
        # Check if already infected with this disease
        if entity_id in self.infected_entities:
            for active in self.infected_entities[entity_id]:
                if active.disease.disease_id == disease_id:
                    logger.debug(f"[DISEASE] {entity_id} already infected with {disease_id}")
                    return False
        
        # Create active infection
        active_disease = ActiveDisease(disease, time.time())
        
        if entity_id not in self.infected_entities:
            self.infected_entities[entity_id] = []
        
        self.infected_entities[entity_id].append(active_disease)
        self.global_infection_stats["total_infections"] += 1
        
        logger.info(f"[DISEASE] {entity_id} infected with {disease.name} from {source}")
        return True
    
    def cure_disease(self, entity_id: str, disease_id: str, cure_method: str) -> bool:
        """Cure a specific disease"""
        if entity_id not in self.infected_entities:
            return False
        
        infections = self.infected_entities[entity_id]
        for i, active in enumerate(infections):
            if active.disease.disease_id == disease_id:
                # Check if cure method is valid
                if cure_method not in active.disease.cures and cure_method != "force":
                    logger.warning(f"[DISEASE] Invalid cure method {cure_method} for {disease_id}")
                    return False
                
                # Remove infection
                infections.pop(i)
                self.global_infection_stats["total_cures"] += 1
                logger.info(f"[DISEASE] {entity_id} cured of {active.disease.name} via {cure_method}")
                
                # Clean up if no more infections
                if not infections:
                    del self.infected_entities[entity_id]
                
                return True
        
        return False
    
    def update_infections(self, entity_id: str, entity_data: Dict, current_time: float) -> List[str]:
        """Update all infections for an entity and return messages"""
        if entity_id not in self.infected_entities:
            return []
        
        messages = []
        infections_to_remove = []
        
        for active in self.infected_entities[entity_id]:
            resolution_needed = active.update(current_time)
            
            # Check for plague resolution
            if resolution_needed and active.disease.disease_id == "plague":
                if active.will_survive is None:
                    # Determine survival
                    survival_chance = 1.0 - active.disease.mortality_rate
                    
                    # Modify by protective gear
                    if entity_data.get("has_plague_doctor_gear", False):
                        survival_chance += 0.20  # +20% with gear
                    
                    # Modify by plague survivor trait
                    if entity_data.get("has_plague_survivor_trait", False):
                        survival_chance += 0.06  # +6% for survivors
                    
                    # Modify by magic protection
                    if entity_data.get("has_magic_protection", False):
                        survival_chance += 0.15  # +15% with magic
                    
                    # Roll for survival
                    active.will_survive = random.random() < survival_chance
                    
                    if active.will_survive:
                        messages.append(f"🎗️ Survived the plague! You are one of the fortunate.")
                        self.plague_survivors.add(entity_id)
                        infections_to_remove.append(active)
                    else:
                        messages.append(f"💀 The plague has claimed you...")
                        # Entity should die - handled by caller
                        return ["DEATH_BY_PLAGUE"]
            
            # Check for natural expiration
            if active.is_expired():
                messages.append(f"✅ {active.disease.name} has passed")
                infections_to_remove.append(active)
        
        # Remove expired infections
        for active in infections_to_remove:
            self.infected_entities[entity_id].remove(active)
        
        # Clean up if no infections
        if entity_id in self.infected_entities and not self.infected_entities[entity_id]:
            del self.infected_entities[entity_id]
        
        return messages
    
    def get_entity_diseases(self, entity_id: str) -> List[ActiveDisease]:
        """Get all active diseases for an entity"""
        return self.infected_entities.get(entity_id, [])
    
    def has_disease(self, entity_id: str, disease_id: str = None) -> bool:
        """Check if entity has any disease or specific disease"""
        if entity_id not in self.infected_entities:
            return False
        
        if disease_id is None:
            return len(self.infected_entities[entity_id]) > 0
        
        for active in self.infected_entities[entity_id]:
            if active.disease.disease_id == disease_id:
                return True
        
        return False
    
    def is_plague_survivor(self, entity_id: str) -> bool:
        """Check if entity survived plague"""
        return entity_id in self.plague_survivors
    
    def start_outbreak(self, town_name: str, disease_id: str):
        """Start a disease outbreak in a town"""
        if town_name not in self.town_outbreak_status:
            self.town_outbreak_status[town_name] = {}
        
        self.town_outbreak_status[town_name][disease_id] = {
            "start_time": time.time(),
            "infected_count": 0,
            "death_count": 0,
            "active": True
        }
        
        self.global_infection_stats["active_outbreaks"] += 1
        logger.warning(f"[DISEASE] Outbreak of {disease_id} started in {town_name}!")
    
    def end_outbreak(self, town_name: str, disease_id: str):
        """End an outbreak"""
        if town_name in self.town_outbreak_status:
            if disease_id in self.town_outbreak_status[town_name]:
                self.town_outbreak_status[town_name][disease_id]["active"] = False
                self.global_infection_stats["active_outbreaks"] = max(0, self.global_infection_stats["active_outbreaks"] - 1)
                logger.info(f"[DISEASE] Outbreak of {disease_id} ended in {town_name}")
    
    def get_town_outbreaks(self, town_name: str) -> list:
        """Get all active disease outbreaks in a town"""
        outbreaks = []
        if town_name in self.town_outbreak_status:
            for disease_id, status in self.town_outbreak_status[town_name].items():
                if status.get("active", False):
                    outbreaks.append(disease_id)
        return outbreaks
    
    def quarantine_town(self, town_name: str):
        """Quarantine a town"""
        self.quarantine_zones[town_name] = True
        logger.info(f"[DISEASE] {town_name} is now quarantined")
    
    def lift_quarantine(self, town_name: str):
        """Lift quarantine from a town"""
        if town_name in self.quarantine_zones:
            del self.quarantine_zones[town_name]
            logger.info(f"[DISEASE] Quarantine lifted from {town_name}")
    
    def is_town_quarantined(self, town_name: str) -> bool:
        """Check if town is quarantined"""
        return self.quarantine_zones.get(town_name, False)
    
    def get_town_outbreak_status(self, town_name: str) -> Dict:
        """Get outbreak status for a town"""
        return self.town_outbreak_status.get(town_name, {})
    
    def calculate_infection_chance(self, base_rate: float, modifiers: Dict) -> float:
        """Calculate actual infection chance with modifiers"""
        chance = base_rate
        
        # Weather modifier
        if modifiers.get("is_cold_weather", False):
            chance *= 1.5  # +50% in cold weather
        
        if modifiers.get("is_raining", False):
            chance *= 1.3  # +30% in rain
        
        # Proximity to sick NPCs
        if modifiers.get("near_sick_npc", False):
            chance *= 2.0  # +100% near sick people
        
        # Protective gear
        if modifiers.get("has_plague_doctor_gear", False):
            chance *= 0.30  # -70% with full gear
        elif modifiers.get("has_plague_mask", False):
            chance *= 0.60  # -40% with mask only
        
        # Racial modifiers
        racial_multiplier = modifiers.get("racial_disease_resistance", 1.0)
        chance *= racial_multiplier
        
        return min(1.0, chance)  # Cap at 100%
    
    def get_infection_stats(self) -> Dict:
        """Get global infection statistics"""
        return self.global_infection_stats.copy()

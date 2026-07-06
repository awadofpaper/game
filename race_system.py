"""
Race System - Character races with unique traits and stat modifiers

Provides 6 playable races with distinct advantages and flavor.
"""

from typing import Dict, List, Tuple, Optional, Any


class RacialTrait:
    """A passive trait that provides bonuses or special effects"""
    
    def __init__(self, trait_id: str, name: str, description: str, effects: Dict[str, Any]):
        self.id = trait_id
        self.name = name
        self.description = description
        self.effects = effects  # Dict of effect_type -> value
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for saving"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'effects': self.effects
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RacialTrait':
        """Deserialize from save data"""
        return RacialTrait(
            data['id'],
            data['name'],
            data['description'],
            data['effects']
        )


class Race:
    """A playable character race with unique characteristics"""
    
    def __init__(self, race_id: str, name: str, description: str,
                 stat_modifiers: Dict[str, int],
                 traits: List[RacialTrait],
                 skin_tones: List[Tuple[int, int, int]],
                 skin_tone_names: List[str],
                 special_ability: Optional[Dict[str, Any]] = None):
        self.id = race_id
        self.name = name
        self.description = description
        self.stat_modifiers = stat_modifiers  # Dict of stat_name -> modifier value
        self.traits = traits  # List of RacialTrait objects
        self.skin_tones = skin_tones  # List of RGB tuples
        self.skin_tone_names = skin_tone_names  # Names for each skin tone
        self.special_ability = special_ability  # Optional special ability (future use)
        
    def get_trait_descriptions(self) -> List[str]:
        """Get formatted trait descriptions for display"""
        return [f"{trait.name}: {trait.description}" for trait in self.traits]
    
    def get_stat_summary(self) -> str:
        """Get a summary of stat modifiers"""
        positive = []
        negative = []
        for stat, value in self.stat_modifiers.items():
            if value > 0:
                positive.append(f"+{value} {stat.title()}")
            elif value < 0:
                negative.append(f"{value} {stat.title()}")
        
        parts = []
        if positive:
            parts.append(", ".join(positive))
        if negative:
            parts.append(", ".join(negative))
        
        return " | ".join(parts) if parts else "No modifiers"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for saving"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stat_modifiers': self.stat_modifiers,
            'traits': [trait.to_dict() for trait in self.traits],
            'skin_tones': self.skin_tones,
            'skin_tone_names': self.skin_tone_names,
            'special_ability': self.special_ability
        }


# ============================================================
# RACE DEFINITIONS
# ============================================================

# HUMAN - Balanced and adaptable
HUMAN_TRAITS = [
    RacialTrait(
        'human_jack_of_all_trades',
        'Jack of All Trades',
        '+5% XP gain in ALL systems (combat, gathering, crafting). Gain +1 extra stat point per level.',
        {'xp_multiplier': 1.05, 'bonus_stat_points': 1}
    ),
    RacialTrait(
        'human_diplomatic_mastery',
        'Diplomatic Mastery',
        '-15% prices when buying, +15% when selling. Quest rewards +10% gold. NPCs start with +15 reputation.',
        {'shop_discount': 0.15, 'shop_selling_bonus': 0.15, 'quest_gold_bonus': 0.10, 'reputation_bonus': 15}
    )
]

HUMAN = Race(
    race_id='human',
    name='Human',
    description='Versatile and adaptable. Humans excel at learning and diplomacy, making them well-rounded adventurers.',
    stat_modifiers={
        'strength': -2,
        'defense': 0,
        'magic': -2,
        'stamina_stat': 0,
        'speed': 0,
        'agility': 0,
        'willpower': 2,
        'luck': 0,
        'intelligence': 0,
        'talking': 2
    },
    traits=HUMAN_TRAITS,
    skin_tones=[
        (255, 220, 177),  # Light
        (241, 194, 125),  # Fair
        (224, 172, 105),  # Medium
        (198, 134, 66),   # Tan
        (141, 85, 36),    # Brown
        (92, 64, 51),     # Dark brown
        (58, 48, 42),     # Deep
        (0, 0, 255),      # Blue
    ],
    skin_tone_names=[
        'Light', 'Fair', 'Medium', 'Tan', 'Brown', 'Dark Brown', 'Deep', 'Blue'
    ]
)

# ELF - Agile and magical
ELF_TRAITS = [
    RacialTrait(
        'elf_eternal_mana_flow',
        'Eternal Mana Flow',
        'Passive mana regeneration: 0.8% of max mana per second. +20% mana regen from resting/potions.',
        {'passive_mana_regen_percent': 0.008, 'mana_regen_bonus': 0.20}
    ),
    RacialTrait(
        'elf_woodland_grace',
        'Woodland Grace',
        '+30% movement speed in forests/grasslands. Enemies detect you at -40% range. +50% gathering XP for herbs/wood.',
        {'movement_speed_bonus': 0.30, 'terrain_types': ['forest', 'grassland'], 'detection_reduction': 0.40, 'gathering_xp_bonus': 0.50}
    )
]

ELF = Race(
    race_id='elf',
    name='Elf',
    description='Graceful and attuned to magic. Elves are quick, perceptive, and have a natural connection to nature.',
    stat_modifiers={
        'strength': -3,
        'defense': -2,
        'magic': 3,
        'stamina_stat': 0,
        'speed': 0,
        'agility': 2,
        'willpower': 0,
        'luck': 0,
        'intelligence': 0,
        'talking': 0
    },
    traits=ELF_TRAITS,
    skin_tones=[
        (250, 240, 230),  # Pale moonlight
        (255, 235, 215),  # Ivory
        (238, 213, 183),  # Fair
        (210, 180, 140),  # Tan
        (139, 90, 60),    # Dark wood
        (180, 150, 170),  # Dusk (purple-ish)
        (210, 210, 235),  # Silvery
        (255, 255, 255),  # White
    ],
    skin_tone_names=[
        'Pale Moonlight', 'Ivory', 'Fair', 'Tan', 'Dark Wood', 'Dusk', 'Silvery', 'White'
    ]
)

# DWARF - Hardy and strong
DWARF_TRAITS = [
    RacialTrait(
        'dwarf_stone_skin',
        'Stone Skin',
        '+12% physical damage reduction. +25% armor effectiveness. Immune to knockback effects.',
        {'physical_damage_reduction': 0.12, 'armor_effectiveness_bonus': 0.25, 'knockback_immunity': True}
    ),
    RacialTrait(
        'dwarf_master_smith',
        'Master Smith',
        'Repair items FREE at blacksmiths. Crafted equipment +20% durability. Mining XP +100%.',
        {'free_repairs': True, 'crafting_durability_bonus': 0.20, 'mining_xp_multiplier': 2.0}
    )
]

DWARF = Race(
    race_id='dwarf',
    name='Dwarf',
    description='Stout and resilient. Dwarves are master craftsmen with unmatched endurance and strength.',
    stat_modifiers={
        'strength': 3,
        'defense': 3,
        'magic': 0,
        'stamina_stat': 0,
        'speed': -3,
        'agility': -3,
        'willpower': 0,
        'luck': 0,
        'intelligence': 0,
        'talking': 0
    },
    traits=DWARF_TRAITS,
    skin_tones=[
        (255, 219, 172),  # Light
        (228, 179, 140),  # Fair
        (204, 153, 102),  # Tan
        (186, 140, 99),   # Ruddy
        (161, 102, 73),   # Bronze
        (133, 88, 63),    # Deep
        (255, 140, 0),    # Orange
    ],
    skin_tone_names=[
        'Light', 'Fair', 'Tan', 'Ruddy', 'Bronze', 'Deep', 'Orange'
    ]
)

# ORC - Warrior and intimidating
ORC_TRAITS = [
    RacialTrait(
        'orc_dual_titan_weapons',
        'Dual Titan Weapons',
        'Can equip TWO two-handed weapons at once. +15% melee damage. -20% attack speed when dual-wielding 2H.',
        {'dual_wield_2h': True, 'melee_damage_bonus': 0.15, 'dual_2h_attack_speed_penalty': 0.20}
    ),
    RacialTrait(
        'orc_unstoppable_rage',
        'Unstoppable Rage',
        'When HP drops below 40%: +30% damage, +20% attack speed, -10% damage taken. Lasts 12s after HP recovers.',
        {'rage_hp_threshold': 0.40, 'rage_damage_bonus': 0.30, 'rage_attack_speed_bonus': 0.20, 'rage_damage_reduction': 0.10, 'rage_duration': 12.0}
    )
]

ORC = Race(
    race_id='orc',
    name='Orc',
    description='Fierce and powerful. Orcs are natural warriors who strike fear into their enemies.',
    stat_modifiers={
        'strength': 4,
        'defense': 0,
        'magic': -3,
        'stamina_stat': 2,
        'speed': 0,
        'agility': 0,
        'willpower': 0,
        'luck': 0,
        'intelligence': -3,
        'talking': 0
    },
    traits=ORC_TRAITS,
    skin_tones=[
        (120, 160, 90),   # Green
        (90, 130, 70),    # Dark green
        (100, 140, 80),   # Moss
        (140, 150, 110),  # Pale green
        (140, 115, 85),   # Brown
        (160, 160, 140),  # Pale gray
        (85, 105, 75),    # Deep forest
        (255, 0, 0),      # Red
    ],
    skin_tone_names=[
        'Green', 'Dark Green', 'Moss', 'Pale Green', 'Brown', 'Pale Gray', 'Deep Forest', 'Red'
    ]
)

# HALFLING - Lucky and stealthy
HALFLING_TRAITS = [
    RacialTrait(
        'halfling_miraculous_fortune',
        'Miraculous Fortune',
        '8% chance to dodge any attack. 12% chance to find double loot. +5% critical hit chance.',
        {'dodge_chance': 0.08, 'double_loot_chance': 0.12, 'crit_chance_bonus': 0.05}
    ),
    RacialTrait(
        'halfling_small_and_swift',
        'Small & Swift',
        '+25% movement speed. Enemies detect you at -50% range. -10% stamina cost for sprinting.',
        {'movement_speed_bonus': 0.25, 'detection_reduction': 0.50, 'sprint_stamina_reduction': 0.10}
    )
]

HALFLING = Race(
    race_id='halfling',
    name='Halfling',
    description='Small but fortunate. Halflings rely on luck, stealth, and quick reflexes to survive.',
    stat_modifiers={
        'strength': -3,
        'defense': -3,
        'magic': 0,
        'stamina_stat': 0,
        'speed': 0,
        'agility': 3,
        'willpower': 0,
        'luck': 3,
        'intelligence': 0,
        'talking': 0
    },
    traits=HALFLING_TRAITS,
    skin_tones=[
        (255, 228, 196),  # Light
        (245, 210, 180),  # Fair
        (230, 190, 160),  # Rosy
        (215, 175, 140),  # Tan
        (190, 150, 120),  # Bronze
        (165, 130, 100),  # Brown
        (255, 255, 0),    # Yellow
    ],
    skin_tone_names=[
        'Light', 'Fair', 'Rosy', 'Tan', 'Bronze', 'Brown', 'Yellow'
    ]
)

# TIEFLING - Magical and cunning
TIEFLING_TRAITS = [
    RacialTrait(
        'tiefling_infernal_mastery',
        'Infernal Mastery',
        'ALL spells cost -15% mana. +25% spell damage. Fire spells: -30% mana cost, +40% damage.',
        {'spell_cost_reduction': 0.15, 'spell_damage_bonus': 0.25, 'fire_spell_cost_reduction': 0.30, 'fire_spell_damage_bonus': 0.40}
    ),
    RacialTrait(
        'tiefling_hellborn_resistance',
        'Hellborn Resistance',
        '-15% magic damage, -25% fire damage taken. +30% status effect resistance. Status duration -40%.',
        {'magic_damage_reduction': 0.15, 'fire_damage_reduction': 0.25, 'status_resistance': 0.30, 'status_duration_reduction': 0.40}
    )
]

TIEFLING = Race(
    race_id='tiefling',
    name='Tiefling',
    description='Infernal heritage. Tieflings wield dark magic and resist supernatural harm with ease.',
    stat_modifiers={
        'strength': -3,
        'defense': -3,
        'magic': 3,
        'stamina_stat': 0,
        'speed': 0,
        'agility': 0,
        'willpower': 3,
        'luck': 0,
        'intelligence': 0,
        'talking': 0
    },
    traits=TIEFLING_TRAITS,
    skin_tones=[
        (255, 200, 200),  # Light pink
        (220, 100, 100),  # Red
        (180, 80, 80),    # Deep red
        (200, 150, 180),  # Purple-pink
        (160, 120, 140),  # Dusky purple
        (120, 90, 110),   # Dark purple
        (200, 180, 160),  # Ashen
        (140, 140, 160),  # Gray-blue
        (128, 0, 128),    # Purple
    ],
    skin_tone_names=[
        'Light Pink', 'Red', 'Deep Red', 'Purple-Pink', 'Dusky Purple', 'Dark Purple', 'Ashen', 'Gray-Blue', 'Purple'
    ]
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

# Registry of all available races
ALL_RACES = {
    'human': HUMAN,
    'elf': ELF,
    'dwarf': DWARF,
    'orc': ORC,
    'halfling': HALFLING,
    'tiefling': TIEFLING
}


def get_race_by_id(race_id: str) -> Optional[Race]:
    """Get a race by its ID"""
    return ALL_RACES.get(race_id)


def get_all_races() -> List[Race]:
    """Get list of all playable races"""
    return [HUMAN, ELF, DWARF, ORC, HALFLING, TIEFLING]


def get_race_names() -> List[str]:
    """Get list of all race names"""
    return [race.name for race in get_all_races()]


def apply_racial_stat_modifiers(base_stats: Dict[str, int], race: Race) -> Dict[str, int]:
    """Apply racial stat modifiers to base stats"""
    modified_stats = base_stats.copy()
    
    for stat, modifier in race.stat_modifiers.items():
        if stat in modified_stats:
            modified_stats[stat] += modifier
        else:
            modified_stats[stat] = modifier
    
    return modified_stats

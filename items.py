# items.py
# All item types for the RPG game: Consumables, Spells, Debuff Coatings, Enchantments
# Scaling effects by player level

LEVEL_TIERS = [
    (1, 19),
    (20, 49),
    (50, 89),
    (90, 999)
]

def get_level_tier(level):
    """
    Return the (min, max) tuple for the player's level tier.
    """
    for tier in LEVEL_TIERS:
        if tier[0] <= level <= tier[1]:
            return tier
    return LEVEL_TIERS[-1]

class Item:
    """
    Base class for all items.
    """
    def __init__(self, name, weight=1):
        self.name = name
        self.weight = weight  # in lbs

    def use(self, player, target=None):
        raise NotImplementedError("You must implement use() in subclasses.")

class Consumable(Item):
    """
    Potions, medicine, etc. One-time use, scales by player level.
    """
    def __init__(self, name, effect_by_tier):
        super().__init__(name)
        self.effect_by_tier = effect_by_tier  # Dict[Tuple[int,int], Dict]

    def use(self, player, target=None):
        tier = get_level_tier(player.level)
        effect = self.effect_by_tier[tier]
        player.apply_effect(effect)
        player.remove_item(self)
        print(f"{player.name} uses {self.name}: {effect}")

class Spell(Item):
    """
    Single-use spell scrolls, like Fireball, Lightning Bolt, etc.
    """
    def __init__(self, name, effect_by_tier):
        super().__init__(name)
        self.effect_by_tier = effect_by_tier

    def use(self, player, target):
        tier = get_level_tier(player.level)
        effect = self.effect_by_tier[tier]
        target.apply_effect(effect)
        player.remove_item(self)
        print(f"{player.name} casts {self.name} on {target.name}: {effect}")

class DebuffCoating(Item):
    """
    One-time use coatings, grant temporary debuff effect to weapon.
    """
    def __init__(self, name, effect_by_tier):
        super().__init__(name)
        self.effect_by_tier = effect_by_tier

    def use(self, player, weapon):
        tier = get_level_tier(player.level)
        effect = self.effect_by_tier[tier]
        if weapon.debuff_uses_left > 0:
            print(f"{weapon.name} already has a debuff coating active!")
            return
        weapon.debuff = effect
        weapon.debuff_uses_left = effect.get("attacks", 1)
        player.remove_item(self)
        print(f"{player.name} applies {self.name} to {weapon.name}: {effect}")

class Enchantment(Item):
    """
    Permanent weapon upgrades. Only one per weapon.
    """
    def __init__(self, name, effect_by_tier):
        super().__init__(name)
        self.effect_by_tier = effect_by_tier

    def use(self, player, weapon):
        if weapon.enchantment is not None:
            print(f"{weapon.name} already has an enchantment!")
            return
        tier = get_level_tier(player.level)
        effect = self.effect_by_tier[tier]
        weapon.enchantment = effect
        player.remove_item(self)
        print(f"{player.name} enchants {weapon.name} with {self.name}: {effect}")

# --- Example Item Definitions ---

health_elixir_effects = {
    (1, 19): {"heal_hp": 2},
    (20, 49): {"heal_hp": 5},
    (50, 89): {"heal_hp": 12},
    (90, 999): {"heal_hp": 25},
}

mana_elixir_effects = {
    (1, 19): {"heal_mp": 2},
    (20, 49): {"heal_mp": 5},
    (50, 89): {"heal_mp": 12},
    (90, 999): {"heal_mp": 25},
}

potion_swiftness_effects = {
    (1, 19): {"speed_pct": 10, "duration": 30},
    (20, 49): {"speed_pct": 15, "duration": 45},
    (50, 89): {"speed_pct": 25, "duration": 60},
    (90, 999): {"speed_pct": 50, "duration": 90},
}

herbal_medicine_effects = {
    (1, 19): {"heal_hp": 2, "cure_status": 1},
    (20, 49): {"heal_hp": 5, "cure_status": 2},
    (50, 89): {"heal_hp": 12, "cure_status": "all"},
    (90, 999): {"heal_hp": 25, "cure_status": "all"},
}

fireball_spell_effects = {
    (1, 19): {"fire_damage": 5, "area": "single"},
    (20, 49): {"fire_damage": 12, "area": "small"},
    (50, 89): {"fire_damage": 25, "area": "medium", "ignite_chance": 50},
    (90, 999): {"fire_damage": 50, "area": "large", "ignite": True},
}

ice_shard_spell_effects = {
    (1, 19): {"ice_damage": 5, "slow": "minor"},
    (20, 49): {"ice_damage": 12, "slow": "moderate"},
    (50, 89): {"ice_damage": 25, "slow": "strong", "freeze_chance": 50},
    (90, 999): {"ice_damage": 50, "slow": "strong", "freeze": True},
}

lightning_bolt_spell_effects = {
    (1, 19): {"lightning_damage": 6, "targets": 1},
    (20, 49): {"lightning_damage": 15, "targets": 2},
    (50, 89): {"lightning_damage": 30, "targets": 3},
    (90, 999): {"lightning_damage": 60, "targets": 5},
}

poison_coating_effects = {
    (1, 19): {"attacks": 1, "poison_damage": 2, "duration": 10},
    (20, 49): {"attacks": 2, "poison_damage": 5, "duration": 15},
    (50, 89): {"attacks": 3, "poison_damage": 12, "duration": 20},
    (90, 999): {"attacks": 5, "poison_damage": 25, "duration": 30},
}

slowing_tincture_effects = {
    (1, 19): {"attacks": 1, "slow_pct": 10, "duration": 10},
    (20, 49): {"attacks": 2, "slow_pct": 20, "duration": 15},
    (50, 89): {"attacks": 3, "slow_pct": 35, "duration": 20},
    (90, 999): {"attacks": 5, "slow_pct": 60, "duration": 30},
}

weakening_oil_effects = {
    (1, 19): {"attacks": 1, "enemy_damage_reduction": 10, "duration": 10},
    (20, 49): {"attacks": 2, "enemy_damage_reduction": 20, "duration": 15},
    (50, 89): {"attacks": 3, "enemy_damage_reduction": 30, "duration": 20},
    (90, 999): {"attacks": 5, "enemy_damage_reduction": 50, "duration": 30},
}

flaming_enchantment_effects = {
    (1, 19): {"fire_damage": 1},
    (20, 49): {"fire_damage": 3},
    (50, 89): {"fire_damage": 7},
    (90, 999): {"fire_damage": 15},
}

toxic_enchantment_effects = {
    (1, 19): {"poison_damage": 1, "duration": 3},
    (20, 49): {"poison_damage": 3, "duration": 4},
    (50, 89): {"poison_damage": 7, "duration": 5},
    (90, 999): {"poison_damage": 15, "duration": 6},
}

arcane_enchantment_effects = {
    (1, 19): {"magic_damage": 1, "ignore_resistance": 1},
    (20, 49): {"magic_damage": 3, "ignore_resistance": 2},
    (50, 89): {"magic_damage": 7, "ignore_resistance": 4},
    (90, 999): {"magic_damage": 15, "ignore_resistance": 8},
}

crushing_enchantment_effects = {
    (1, 19): {"physical_damage": 1, "stun_chance": 5},
    (20, 49): {"physical_damage": 3, "stun_chance": 10},
    (50, 89): {"physical_damage": 7, "stun_chance": 20},
    (90, 999): {"physical_damage": 15, "stun_chance": 40},
}

def create_health_elixir():
    return Consumable("Health Elixir", health_elixir_effects)

def create_mana_elixir():
    return Consumable("Mana Elixir", mana_elixir_effects)

def create_potion_swiftness():
    return Consumable("Potion of Swiftness", potion_swiftness_effects)

def create_herbal_medicine():
    return Consumable("Herbal Medicine", herbal_medicine_effects)

def create_fireball_spell():
    return Spell("Fireball Spell", fireball_spell_effects)

def create_ice_shard_spell():
    return Spell("Ice Shard Spell", ice_shard_spell_effects)

def create_lightning_bolt_spell():
    return Spell("Lightning Bolt Spell", lightning_bolt_spell_effects)

def create_poison_coating():
    return DebuffCoating("Poison Coating", poison_coating_effects)

def create_slowing_tincture():
    return DebuffCoating("Slowing Tincture", slowing_tincture_effects)

def create_weakening_oil():
    return DebuffCoating("Weakening Oil", weakening_oil_effects)

def create_flaming_enchantment():
    return Enchantment("Flaming Enchantment", flaming_enchantment_effects)

def create_toxic_enchantment():
    return Enchantment("Toxic Enchantment", toxic_enchantment_effects)

def create_arcane_enchantment():
    return Enchantment("Arcane Enchantment", arcane_enchantment_effects)

def create_crushing_enchantment():
    return Enchantment("Crushing Enchantment", crushing_enchantment_effects)
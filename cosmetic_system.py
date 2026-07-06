"""
Cosmetic System - A parody of predatory microtransaction loot boxes

Features ridiculous rarity tiers with lottery-odds for the best items.
All cosmetics are purely visual and provide no gameplay advantage.
"""

import random
import math
from typing import Dict, List, Tuple, Any, Optional


class CosmeticRarity:
    """Rarity tiers with hilariously skewed drop rates"""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"
    MYTHIC = "Mythic"
    ULTRA_RARE = "Ultra Rare"
    LITERALLY_IMPOSSIBLE = "Literally Impossible"  # 0.0001% chance
    
    # Drop rates (must sum to 100.0)
    RATES = {
        COMMON: 60.0,          # 60%
        UNCOMMON: 25.0,        # 25%
        RARE: 10.0,            # 10%
        EPIC: 3.5,             # 3.5%
        LEGENDARY: 1.0,        # 1%
        MYTHIC: 0.4,           # 0.4%
        ULTRA_RARE: 0.099,     # 0.099%
        LITERALLY_IMPOSSIBLE: 0.001  # 0.001% - same as winning lottery
    }
    
    # Visual colors for rarity display
    COLORS = {
        COMMON: (150, 150, 150),
        UNCOMMON: (100, 255, 100),
        RARE: (100, 150, 255),
        EPIC: (200, 100, 255),
        LEGENDARY: (255, 200, 50),
        MYTHIC: (255, 100, 255),
        ULTRA_RARE: (255, 50, 50),
        LITERALLY_IMPOSSIBLE: (255, 255, 255)
    }


class PatternType:
    """Available pattern types"""
    SOLID = "solid"
    STRIPES_HORIZONTAL = "stripes_h"
    STRIPES_VERTICAL = "stripes_v"
    STRIPES_DIAGONAL = "stripes_d"
    POLKA_DOTS = "polka_dots"
    CHECKERBOARD = "checkerboard"
    GRADIENT_H = "gradient_h"
    GRADIENT_V = "gradient_v"
    GRADIENT_RADIAL = "gradient_radial"
    WAVE = "wave"
    ZIGZAG = "zigzag"
    STARS = "stars"
    HEARTS = "hearts"
    SPIRAL = "spiral"
    HEXAGONS = "hexagons"
    TRIANGLES = "triangles"
    CIRCLES = "circles"
    DIAMONDS = "diamonds"
    RAINBOW = "rainbow"
    GALAXY = "galaxy"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    TOXIC = "toxic"
    GLITCH = "glitch"
    MATRIX = "matrix"
    NEON = "neon"


class Cosmetic:
    """A single cosmetic item"""
    
    def __init__(self, cosmetic_id: str, name: str, rarity: str, 
                 primary_color: Tuple[int, int, int],
                 secondary_color: Optional[Tuple[int, int, int]],
                 pattern: str,
                 applies_to: str = "player"):
        self.id = cosmetic_id
        self.name = name
        self.rarity = rarity
        self.primary_color = primary_color
        self.secondary_color = secondary_color or primary_color
        self.pattern = pattern
        self.applies_to = applies_to  # player, pet, armor, weapon
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for saving"""
        return {
            'id': self.id,
            'name': self.name,
            'rarity': self.rarity,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'pattern': self.pattern,
            'applies_to': self.applies_to
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Cosmetic':
        """Deserialize from save data"""
        return Cosmetic(
            cosmetic_id=data['id'],
            name=data['name'],
            rarity=data['rarity'],
            primary_color=tuple(data['primary_color']),
            secondary_color=tuple(data['secondary_color']) if data['secondary_color'] else None,
            pattern=data['pattern'],
            applies_to=data.get('applies_to', 'player')
        )


class CosmeticGenerator:
    """Generates random cosmetics with appropriate rarity"""
    
    # Color palettes by rarity
    COMMON_COLORS = [
        (139, 69, 19), (105, 105, 105), (128, 128, 128),
        (160, 82, 45), (112, 128, 144), (119, 136, 153)
    ]
    
    UNCOMMON_COLORS = [
        (0, 128, 0), (0, 0, 255), (255, 0, 0),
        (255, 255, 0), (255, 165, 0), (75, 0, 130)
    ]
    
    RARE_COLORS = [
        (0, 255, 255), (255, 0, 255), (255, 20, 147),
        (50, 205, 50), (255, 215, 0), (138, 43, 226)
    ]
    
    EPIC_COLORS = [
        (255, 105, 180), (0, 191, 255), (255, 140, 0),
        (148, 0, 211), (220, 20, 60), (0, 250, 154)
    ]
    
    LEGENDARY_COLORS = [
        (255, 215, 0), (255, 69, 0), (218, 165, 32),
        (255, 140, 0), (255, 99, 71), (255, 127, 80)
    ]
    
    MYTHIC_COLORS = [
        (138, 43, 226), (147, 112, 219), (186, 85, 211),
        (153, 50, 204), (148, 0, 211), (139, 0, 139)
    ]
    
    ULTRA_RARE_COLORS = [
        (255, 20, 147), (255, 105, 180), (199, 21, 133),
        (219, 112, 147), (255, 182, 193), (255, 105, 97)
    ]
    
    LITERALLY_IMPOSSIBLE_COLORS = [
        (255, 255, 255), (240, 248, 255), (255, 250, 250),
        (245, 255, 250), (248, 248, 255), (255, 255, 240)
    ]
    
    PATTERN_ADJECTIVES = {
        PatternType.SOLID: ["Solid", "Pure", "Plain", "Basic"],
        PatternType.STRIPES_HORIZONTAL: ["Horizontal Striped", "H-Striped", "Lined"],
        PatternType.STRIPES_VERTICAL: ["Vertical Striped", "V-Striped", "Barred"],
        PatternType.STRIPES_DIAGONAL: ["Diagonal Striped", "Slanted", "Angled"],
        PatternType.POLKA_DOTS: ["Polka Dot", "Dotted", "Spotted"],
        PatternType.CHECKERBOARD: ["Checkered", "Checked", "Tiled"],
        PatternType.GRADIENT_H: ["Gradient", "Fading", "Ombré"],
        PatternType.GRADIENT_V: ["Vertical Gradient", "Rising", "Cascading"],
        PatternType.GRADIENT_RADIAL: ["Radial", "Burst", "Sunburst"],
        PatternType.WAVE: ["Wavy", "Flowing", "Rippled"],
        PatternType.ZIGZAG: ["Zigzag", "Chevron", "Angular"],
        PatternType.STARS: ["Starry", "Stellar", "Constellation"],
        PatternType.HEARTS: ["Lovely", "Romantic", "Heartfelt"],
        PatternType.SPIRAL: ["Spiral", "Swirled", "Twisted"],
        PatternType.HEXAGONS: ["Honeycomb", "Hexagonal", "Geometric"],
        PatternType.TRIANGLES: ["Triangular", "Pointed", "Sharp"],
        PatternType.CIRCLES: ["Circular", "Bubbly", "Orbed"],
        PatternType.DIAMONDS: ["Diamond", "Crystalline", "Prismatic"],
        PatternType.RAINBOW: ["Rainbow", "Prismatic", "Spectrum"],
        PatternType.GALAXY: ["Galactic", "Cosmic", "Nebula"],
        PatternType.FIRE: ["Fiery", "Blazing", "Inferno"],
        PatternType.ICE: ["Frozen", "Glacial", "Frosty"],
        PatternType.LIGHTNING: ["Electric", "Shocking", "Voltaic"],
        PatternType.TOXIC: ["Toxic", "Radioactive", "Hazardous"],
        PatternType.GLITCH: ["Glitched", "Corrupted", "Digital"],
        PatternType.MATRIX: ["Matrix", "Binary", "Coded"],
        PatternType.NEON: ["Neon", "Glowing", "Luminous"]
    }
    
    COLOR_NAMES = {
        (255, 0, 0): "Red", (0, 255, 0): "Green", (0, 0, 255): "Blue",
        (255, 255, 0): "Yellow", (255, 0, 255): "Magenta", (0, 255, 255): "Cyan",
        (255, 165, 0): "Orange", (128, 0, 128): "Purple", (255, 192, 203): "Pink",
        (165, 42, 42): "Brown", (128, 128, 128): "Gray", (0, 0, 0): "Black",
        (255, 255, 255): "White", (255, 215, 0): "Gold", (192, 192, 192): "Silver",
        (75, 0, 130): "Indigo", (255, 20, 147): "Deep Pink", (0, 128, 128): "Teal",
        (255, 69, 0): "Crimson", (50, 205, 50): "Lime", (138, 43, 226): "Violet"
    }
    
    @staticmethod
    def get_color_name(color: Tuple[int, int, int]) -> str:
        """Get closest color name"""
        # Check exact matches first
        if color in CosmeticGenerator.COLOR_NAMES:
            return CosmeticGenerator.COLOR_NAMES[color]
        
        # Find closest match
        min_dist = float('inf')
        closest_name = "Unknown"
        for known_color, name in CosmeticGenerator.COLOR_NAMES.items():
            dist = sum((a - b) ** 2 for a, b in zip(color, known_color))
            if dist < min_dist:
                min_dist = dist
                closest_name = name
        
        return closest_name
    
    @staticmethod
    def roll_rarity() -> str:
        """Roll for rarity based on drop rates"""
        roll = random.uniform(0, 100)
        cumulative = 0.0
        
        for rarity, rate in CosmeticRarity.RATES.items():
            cumulative += rate
            if roll <= cumulative:
                return rarity
        
        return CosmeticRarity.COMMON  # Fallback
    
    @staticmethod
    def get_patterns_for_rarity(rarity: str) -> List[str]:
        """Get available patterns for this rarity tier"""
        if rarity == CosmeticRarity.COMMON:
            return [PatternType.SOLID, PatternType.STRIPES_HORIZONTAL, PatternType.STRIPES_VERTICAL]
        elif rarity == CosmeticRarity.UNCOMMON:
            return [PatternType.POLKA_DOTS, PatternType.CHECKERBOARD, PatternType.STRIPES_DIAGONAL]
        elif rarity == CosmeticRarity.RARE:
            return [PatternType.GRADIENT_H, PatternType.GRADIENT_V, PatternType.WAVE, PatternType.ZIGZAG]
        elif rarity == CosmeticRarity.EPIC:
            return [PatternType.STARS, PatternType.HEXAGONS, PatternType.TRIANGLES, PatternType.CIRCLES]
        elif rarity == CosmeticRarity.LEGENDARY:
            return [PatternType.GRADIENT_RADIAL, PatternType.RAINBOW, PatternType.DIAMONDS, PatternType.SPIRAL]
        elif rarity == CosmeticRarity.MYTHIC:
            return [PatternType.GALAXY, PatternType.FIRE, PatternType.ICE, PatternType.LIGHTNING]
        elif rarity == CosmeticRarity.ULTRA_RARE:
            return [PatternType.TOXIC, PatternType.GLITCH, PatternType.MATRIX, PatternType.NEON]
        else:  # LITERALLY_IMPOSSIBLE
            return [PatternType.HEARTS, PatternType.GALAXY, PatternType.RAINBOW, PatternType.NEON]
    
    @staticmethod
    def generate_cosmetic(applies_to: str = "player", force_rarity: Optional[str] = None) -> Cosmetic:
        """Generate a random cosmetic"""
        # Roll rarity
        rarity = force_rarity or CosmeticGenerator.roll_rarity()
        
        # Get color palette for rarity
        if rarity == CosmeticRarity.COMMON:
            colors = CosmeticGenerator.COMMON_COLORS
        elif rarity == CosmeticRarity.UNCOMMON:
            colors = CosmeticGenerator.UNCOMMON_COLORS
        elif rarity == CosmeticRarity.RARE:
            colors = CosmeticGenerator.RARE_COLORS
        elif rarity == CosmeticRarity.EPIC:
            colors = CosmeticGenerator.EPIC_COLORS
        elif rarity == CosmeticRarity.LEGENDARY:
            colors = CosmeticGenerator.LEGENDARY_COLORS
        elif rarity == CosmeticRarity.MYTHIC:
            colors = CosmeticGenerator.MYTHIC_COLORS
        elif rarity == CosmeticRarity.ULTRA_RARE:
            colors = CosmeticGenerator.ULTRA_RARE_COLORS
        else:
            colors = CosmeticGenerator.LITERALLY_IMPOSSIBLE_COLORS
        
        # Pick colors
        primary_color = random.choice(colors)
        secondary_color = random.choice(colors)
        
        # Pick pattern
        available_patterns = CosmeticGenerator.get_patterns_for_rarity(rarity)
        pattern = random.choice(available_patterns)
        
        # Generate name
        pattern_adj = random.choice(CosmeticGenerator.PATTERN_ADJECTIVES.get(pattern, ["Mysterious"]))
        primary_name = CosmeticGenerator.get_color_name(primary_color)
        
        if pattern == PatternType.SOLID:
            name = f"{primary_name} {pattern_adj}"
        else:
            secondary_name = CosmeticGenerator.get_color_name(secondary_color)
            name = f"{pattern_adj} {primary_name}/{secondary_name}"
        
        # Add rarity prefix for high rarities
        if rarity in [CosmeticRarity.MYTHIC, CosmeticRarity.ULTRA_RARE, CosmeticRarity.LITERALLY_IMPOSSIBLE]:
            name = f"[{rarity}] {name}"
        
        # Generate unique ID
        cosmetic_id = f"{applies_to}_{pattern}_{primary_color}_{secondary_color}_{random.randint(1000, 9999)}"
        
        return Cosmetic(
            cosmetic_id=cosmetic_id,
            name=name,
            rarity=rarity,
            primary_color=primary_color,
            secondary_color=secondary_color,
            pattern=pattern,
            applies_to=applies_to
        )


class CosmeticManager:
    """Manages player's unlocked cosmetics and equipped items"""
    
    def __init__(self):
        self.unlocked_cosmetics: Dict[str, Cosmetic] = {}
        self.equipped: Dict[str, Optional[str]] = {
            'player': None,
            'pet': None,
            'armor': None,
            'weapon': None
        }
        
    def unlock_cosmetic(self, cosmetic: Cosmetic) -> bool:
        """
        Unlock a cosmetic
        
        Returns:
            bool: True if newly unlocked, False if duplicate
        """
        if cosmetic.id in self.unlocked_cosmetics:
            return False  # Duplicate
        
        self.unlocked_cosmetics[cosmetic.id] = cosmetic
        return True
    
    def equip_cosmetic(self, cosmetic_id: str) -> bool:
        """Equip a cosmetic"""
        if cosmetic_id not in self.unlocked_cosmetics:
            return False
        
        cosmetic = self.unlocked_cosmetics[cosmetic_id]
        self.equipped[cosmetic.applies_to] = cosmetic_id
        return True
    
    def unequip_cosmetic(self, applies_to: str) -> bool:
        """Unequip cosmetic from slot"""
        if applies_to in self.equipped:
            self.equipped[applies_to] = None
            return True
        return False
    
    def get_equipped(self, applies_to: str) -> Optional[Cosmetic]:
        """Get currently equipped cosmetic for slot"""
        cosmetic_id = self.equipped.get(applies_to)
        if cosmetic_id and cosmetic_id in self.unlocked_cosmetics:
            return self.unlocked_cosmetics[cosmetic_id]
        return None
    
    def get_unlocked_by_type(self, applies_to: str) -> List[Cosmetic]:
        """Get all unlocked cosmetics for a specific type"""
        return [c for c in self.unlocked_cosmetics.values() if c.applies_to == applies_to]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for saving"""
        return {
            'unlocked': {cid: c.to_dict() for cid, c in self.unlocked_cosmetics.items()},
            'equipped': self.equipped
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CosmeticManager':
        """Deserialize from save data"""
        manager = CosmeticManager()
        
        unlocked_data = data.get('unlocked', {})
        for cid, c_data in unlocked_data.items():
            manager.unlocked_cosmetics[cid] = Cosmetic.from_dict(c_data)
        
        manager.equipped = data.get('equipped', {
            'player': None,
            'pet': None,
            'armor': None,
            'weapon': None
        })
        
        return manager

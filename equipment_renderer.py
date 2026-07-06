"""
Equipment Renderer Module
Shared equipment rendering system for all entity types (Player, NPCs, Enemies)
"""

import pygame
import math
import time
from equipment import EQUIPMENT_DATA, EQUIPMENT_RARITY, WEAPON_VISUALS


class EquipmentRenderer:
    """
    Handles visual rendering of equipment on any entity type.
    Supports different visual styles for different entity types.
    """
    
    # Visual style configurations for different entity types
    ENTITY_STYLES = {
        "player": {
            "armor_slots": {
                "head": {"shape": "circle", "offset": (0, -18), "size": 16},
                "body": {"shape": "rect", "offset": (0, 0), "size": (24, 28)},
                "arms": {"shape": "rect", "offset": (0, -5), "size": (28, 12)},  # Shoulder armor
                "hands": {"shape": "rect", "offset": (0, 12), "size": (18, 10)},  # Gloves
                "legs": {"shape": "rect", "offset": (0, 18), "size": (20, 16)},
                "feet": {"shape": "rect", "offset": (0, 32), "size": (16, 8)},
                "necklace": {"shape": "circle", "offset": (0, -8), "size": 4},  # Small circle at neck
                "ring1": {"shape": "circle", "offset": (-8, 15), "size": 3},  # Small circle at hand
                "ring2": {"shape": "circle", "offset": (8, 15), "size": 3},  # Small circle at hand
            },
            "weapon_scale": 1.0,
            "outline_width": 2,
            "glow_effect": True,
            "detail_level": "high",
        },
        "npc": {
            "armor_slots": {
                "head": {"shape": "circle", "offset": (0, -14), "size": 12},
                "body": {"shape": "rect", "offset": (0, 0), "size": (18, 20)},
                "chest": {"shape": "rect", "offset": (0, 0), "size": (18, 20)},
                "arms": {"shape": "rect", "offset": (0, -4), "size": (22, 10)},
                "hands": {"shape": "rect", "offset": (0, 10), "size": (14, 8)},
                "legs": {"shape": "rect", "offset": (0, 14), "size": (16, 12)},
                "feet": {"shape": "rect", "offset": (0, 24), "size": (14, 6)},
                "necklace": {"shape": "circle", "offset": (0, -6), "size": 3},
                "ring1": {"shape": "circle", "offset": (-6, 12), "size": 2},
                "ring2": {"shape": "circle", "offset": (6, 12), "size": 2},
            },
            "weapon_scale": 0.8,
            "outline_width": 2,
            "glow_effect": False,
            "detail_level": "medium",
        },
        "enemy": {
            "armor_slots": {
                "head": {"shape": "circle", "offset": (0, -22), "size": 18},
                "body": {"shape": "rect", "offset": (0, 0), "size": (28, 32)},
                "chest": {"shape": "rect", "offset": (0, 0), "size": (28, 32)},
                "arms": {"shape": "rect", "offset": (0, -6), "size": (32, 14)},
                "hands": {"shape": "rect", "offset": (0, 14), "size": (20, 12)},
                "legs": {"shape": "rect", "offset": (0, 22), "size": (22, 18)},
                "feet": {"shape": "rect", "offset": (0, 38), "size": (18, 10)},
                "necklace": {"shape": "circle", "offset": (0, -10), "size": 4},
                "ring1": {"shape": "circle", "offset": (-10, 18), "size": 3},
                "ring2": {"shape": "circle", "offset": (10, 18), "size": 3},
            },
            "weapon_scale": 1.0,
            "outline_width": 2,
            "glow_effect": False,
            "detail_level": "high",
        }
    }
    
    def __init__(self):
        """Initialize the equipment renderer"""
        pass
    
    @staticmethod
    def draw_equipment(screen, entity, center_pos, entity_type="enemy", equipped_items=None):
        """
        Draw equipment on an entity at the given center position.
        
        Args:
            screen: Pygame surface to draw on
            entity: Entity object (has equipment attribute)
            center_pos: (x, y) tuple for center position on screen
            entity_type: "player", "npc", or "enemy" - determines visual style
            equipped_items: Optional dict of equipped items, or will use entity.equipment
        """
        cx, cy = center_pos
        
        # Get visual style for this entity type
        style = EquipmentRenderer.ENTITY_STYLES.get(entity_type, EquipmentRenderer.ENTITY_STYLES["enemy"])
        
        # Get equipped items
        if equipped_items is None:
            if hasattr(entity, 'equipment') and isinstance(entity.equipment, dict):
                equipped_items = entity.equipment
            elif hasattr(entity, 'equipment') and hasattr(entity.equipment, 'equipped'):
                equipped_items = entity.equipment.equipped
            else:
                equipped_items = {}
        
        # Draw armor pieces
        EquipmentRenderer._draw_armor(screen, equipped_items, cx, cy, style)
        
        # Draw main hand weapon (check both 'weapon' and 'main_hand' slots)
        weapon = equipped_items.get("weapon") or equipped_items.get("main_hand")
        EquipmentRenderer._draw_weapon(screen, weapon, cx, cy, style, entity, hand="main")
        
        # Draw off-hand (shield/second weapon)
        EquipmentRenderer._draw_weapon(screen, equipped_items.get("off_hand"), cx, cy, 
                                      style, entity, hand="off")
    
    @staticmethod
    def _normalize_item_name(item_name):
        """Convert display name to equipment data key format.
        Example: 'Leather Armor' -> 'leather_armor'
        """
        return item_name.lower().replace(' ', '_').replace("'", "")
    
    @staticmethod
    def _draw_armor(screen, equipped_items, cx, cy, style):
        """Draw armor pieces on the entity"""
        armor_slots = style["armor_slots"]
        outline_width = style["outline_width"]
        detail_level = style["detail_level"]
        
        for slot, info in armor_slots.items():
            equipped = equipped_items.get(slot)
            
            # Handle both Item objects and string names
            if equipped:
                if isinstance(equipped, str):
                    item_name = equipped
                elif hasattr(equipped, 'name'):
                    item_name = equipped.name
                else:
                    continue
                
                # Normalize the name to match EQUIPMENT_DATA keys
                item_key = EquipmentRenderer._normalize_item_name(item_name)
                
                if item_key not in EQUIPMENT_DATA:
                    continue
                    
                item_data = EQUIPMENT_DATA[item_key]
                rarity = item_data.get("rarity", "common")
                color = EQUIPMENT_RARITY[rarity]["color"]
                
                # Check for custom color in item data
                if "color" in item_data:
                    color = item_data["color"]
                
                ox, oy = info["offset"]
                
                # Draw the armor piece
                if info["shape"] == "circle":
                    # Draw glow effect for legendary+ armor
                    if style.get("glow_effect") and rarity in ["legendary", "artifact"]:
                        glow_color = (*color, 100)
                        glow_surface = pygame.Surface((info["size"]*3, info["size"]*3), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surface, glow_color, 
                                         (info["size"]*3//2, info["size"]*3//2), info["size"]*1.5)
                        screen.blit(glow_surface, (cx + ox - info["size"]*1.5, cy + oy - info["size"]*1.5))
                    
                    pygame.draw.circle(screen, color, (cx + ox, cy + oy), info["size"])
                    pygame.draw.circle(screen, (0, 0, 0), (cx + ox, cy + oy), info["size"], outline_width)
                    
                    # Add detail for high detail level (player)
                    if detail_level == "high" and slot == "head":
                        # Add visor line for helmets
                        pygame.draw.line(screen, (0, 0, 0), 
                                       (cx + ox - info["size"]//2, cy + oy), 
                                       (cx + ox + info["size"]//2, cy + oy), 2)
                
                elif info["shape"] == "rect":
                    w, h = info["size"]
                    rect = pygame.Rect(cx + ox - w // 2, cy + oy - h // 2, w, h)
                    
                    # Draw glow effect for legendary+ armor
                    if style.get("glow_effect") and rarity in ["legendary", "artifact"]:
                        glow_color = (*color, 100)
                        glow_surface = pygame.Surface((w+20, h+20), pygame.SRCALPHA)
                        glow_rect = pygame.Rect(0, 0, w+20, h+20)
                        pygame.draw.rect(glow_surface, glow_color, glow_rect)
                        screen.blit(glow_surface, (rect.x - 10, rect.y - 10))
                    
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, outline_width)
                    
                    # Add detail for high detail level
                    if detail_level == "high":
                        # Add decorative lines based on slot
                        if slot in ["chest", "body"]:
                            # Add chest plate line
                            pygame.draw.line(screen, (0, 0, 0), 
                                           (rect.centerx, rect.top), 
                                           (rect.centerx, rect.bottom), 1)
                        elif slot == "legs":
                            # Add leg separation
                            pygame.draw.line(screen, (0, 0, 0), 
                                           (rect.centerx, rect.top), 
                                           (rect.centerx, rect.bottom), 1)
    
    @staticmethod
    def _draw_weapon(screen, weapon, cx, cy, style, entity, hand="main"):
        """Draw weapon on the entity"""
        if not weapon:
            return
        
        # Handle both Item objects and string names
        weapon_name = weapon
        if not isinstance(weapon, str):
            # Assume it's an Item object with a 'name' attribute
            if hasattr(weapon, 'name'):
                weapon_name = weapon.name
            else:
                return
        
        # Normalize the name to match EQUIPMENT_DATA keys
        weapon_key = EquipmentRenderer._normalize_item_name(weapon_name)
        
        # Check if weapon exists in equipment data
        if weapon_key not in EQUIPMENT_DATA:
            return
        
        weapon_data = EQUIPMENT_DATA[weapon_key]
        rarity = weapon_data.get("rarity", "common")
        blade_color = weapon_data.get("blade_color", (180, 180, 180))
        handle_color = weapon_data.get("handle_color", (80, 60, 40))
        scale = style["weapon_scale"]
        outline_width = style["outline_width"]
        
        # Position offset based on hand
        if hand == "off":
            x_offset = 22
        else:
            x_offset = 0
        
        # Draw based on weapon type
        weapon_lower = weapon_name.lower()
        
        if "stick" in weapon_lower:
            EquipmentRenderer._draw_stick(screen, cx + x_offset, cy, handle_color, 
                                         scale, outline_width, entity)
        elif "sword" in weapon_lower:
            EquipmentRenderer._draw_sword(screen, cx + x_offset, cy, blade_color, handle_color, 
                                         scale, outline_width)
        elif "axe" in weapon_lower:
            EquipmentRenderer._draw_axe(screen, cx + x_offset, cy, blade_color, handle_color, 
                                       scale, outline_width)
        elif "staff" in weapon_lower or "wand" in weapon_lower:
            EquipmentRenderer._draw_staff(screen, cx + x_offset, cy, blade_color, handle_color, 
                                         scale, outline_width, is_wand="wand" in weapon_lower)
        elif "shield" in weapon_lower:
            EquipmentRenderer._draw_shield(screen, cx + x_offset, cy, blade_color, 
                                          scale, outline_width, hand)
        elif "dagger" in weapon_lower:
            EquipmentRenderer._draw_dagger(screen, cx + x_offset, cy, blade_color, handle_color, 
                                          scale, outline_width)
        elif "spear" in weapon_lower:
            EquipmentRenderer._draw_spear(screen, cx + x_offset, cy, blade_color, handle_color, 
                                         scale, outline_width)
        elif "bow" in weapon_lower:
            EquipmentRenderer._draw_bow(screen, cx + x_offset, cy, blade_color, scale, outline_width)
        elif "mace" in weapon_lower or "club" in weapon_lower:
            EquipmentRenderer._draw_mace(screen, cx + x_offset, cy, blade_color, handle_color, 
                                        scale, outline_width)
    
    # ===== WEAPON DRAWING METHODS =====
    
    @staticmethod
    def _draw_sword(screen, cx, cy, blade_color, handle_color, scale, outline_width):
        """Draw a sword"""
        blade_length = int(28 * scale)
        handle_length = int(10 * scale)
        width = int(6 * scale)
        
        # Blade
        pygame.draw.line(screen, blade_color, (cx, cy), (cx, cy - blade_length), width)
        pygame.draw.line(screen, (0, 0, 0), (cx, cy), (cx, cy - blade_length), outline_width)
        
        # Handle
        pygame.draw.line(screen, handle_color, (cx, cy), (cx, cy + handle_length), width)
        pygame.draw.line(screen, (0, 0, 0), (cx, cy), (cx, cy + handle_length), outline_width)
        
        # Crossguard
        guard_size = int(12 * scale)
        pygame.draw.line(screen, blade_color, (cx - guard_size, cy), (cx + guard_size, cy), width)
    
    @staticmethod
    def _draw_axe(screen, cx, cy, blade_color, handle_color, scale, outline_width):
        """Draw an axe"""
        handle_length = int(18 * scale)
        blade_height = int(20 * scale)
        blade_width = int(10 * scale)
        
        # Handle
        pygame.draw.line(screen, handle_color, (cx, cy), (cx, cy + handle_length), int(6 * scale))
        pygame.draw.line(screen, (0, 0, 0), (cx, cy), (cx, cy + handle_length), outline_width)
        
        # Blade (triangle)
        pygame.draw.polygon(screen, blade_color, 
                          [(cx - blade_width, cy - 8), (cx + blade_width, cy - 8), (cx, cy - blade_height)])
        pygame.draw.polygon(screen, (0, 0, 0), 
                          [(cx - blade_width, cy - 8), (cx + blade_width, cy - 8), (cx, cy - blade_height)], 
                          outline_width)
    
    @staticmethod
    def _draw_staff(screen, cx, cy, orb_color, handle_color, scale, outline_width, is_wand=False):
        """Draw a staff or wand"""
        if is_wand:
            staff_length = int(22 * scale)
            orb_size = int(5 * scale)
        else:
            staff_length = int(32 * scale)
            orb_size = int(7 * scale)
        
        # Staff shaft
        pygame.draw.line(screen, handle_color, (cx, cy), (cx, cy - staff_length), int(5 * scale))
        pygame.draw.line(screen, (0, 0, 0), (cx, cy), (cx, cy - staff_length), outline_width)
        
        # Orb at top
        pygame.draw.circle(screen, orb_color, (cx, cy - staff_length), orb_size)
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy - staff_length), orb_size, outline_width)
    
    @staticmethod
    def _draw_shield(screen, cx, cy, color, scale, outline_width, hand):
        """Draw a shield"""
        size = int(14 * scale)
        x_pos = cx - 22 if hand == "main" else cx + 22
        
        # Shield circle
        pygame.draw.circle(screen, color, (x_pos, cy), size)
        pygame.draw.circle(screen, (0, 0, 0), (x_pos, cy), size, outline_width)
        
        # Shield boss (center decoration)
        pygame.draw.circle(screen, (100, 100, 100), (x_pos, cy), int(size * 0.3))
    
    @staticmethod
    def _draw_dagger(screen, cx, cy, blade_color, handle_color, scale, outline_width):
        """Draw a dagger"""
        blade_length = int(18 * scale)
        handle_length = int(6 * scale)
        width = int(4 * scale)
        
        # Blade
        pygame.draw.line(screen, blade_color, (cx, cy), (cx, cy - blade_length), width)
        pygame.draw.line(screen, (0, 0, 0), (cx, cy), (cx, cy - blade_length), outline_width)
        
        # Handle
        pygame.draw.line(screen, handle_color, (cx, cy), (cx, cy + handle_length), width)
        pygame.draw.line(screen, (0, 0, 0), (cx, cy), (cx, cy + handle_length), outline_width)
    
    @staticmethod
    def _draw_spear(screen, cx, cy, blade_color, handle_color, scale, outline_width):
        """Draw a spear"""
        shaft_length = int(38 * scale)
        tip_length = int(10 * scale)
        
        # Shaft
        pygame.draw.line(screen, blade_color, (cx, cy), (cx, cy - shaft_length), int(4 * scale))
        pygame.draw.line(screen, (0, 0, 0), (cx, cy), (cx, cy - shaft_length), outline_width)
        
        # Spear tip
        tip_width = int(4 * scale)
        pygame.draw.polygon(screen, blade_color, 
                          [(cx - tip_width, cy - shaft_length), 
                           (cx + tip_width, cy - shaft_length), 
                           (cx, cy - shaft_length - tip_length)])
        pygame.draw.polygon(screen, (0, 0, 0), 
                          [(cx - tip_width, cy - shaft_length), 
                           (cx + tip_width, cy - shaft_length), 
                           (cx, cy - shaft_length - tip_length)], 
                          outline_width)
    
    @staticmethod
    def _draw_bow(screen, cx, cy, color, scale, outline_width):
        """Draw a bow"""
        bow_height = int(24 * scale)
        bow_width = int(10 * scale)
        
        # Bow arc (two curved lines)
        pygame.draw.arc(screen, color, (cx - bow_width, cy - bow_height, bow_width*2, bow_height*2), 
                       -math.pi/2, math.pi/2, int(4 * scale))
        
        # Bowstring
        pygame.draw.line(screen, (200, 200, 200), (cx + bow_width, cy - bow_height), 
                        (cx + bow_width, cy + bow_height), 2)
    
    @staticmethod
    def _draw_mace(screen, cx, cy, head_color, handle_color, scale, outline_width):
        """Draw a mace or club"""
        handle_length = int(20 * scale)
        head_size = int(8 * scale)
        
        # Handle
        pygame.draw.line(screen, handle_color, (cx, cy), (cx, cy - handle_length), int(6 * scale))
        pygame.draw.line(screen, (0, 0, 0), (cx, cy), (cx, cy - handle_length), outline_width)
        
        # Mace head
        pygame.draw.circle(screen, head_color, (cx, cy - handle_length), head_size)
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy - handle_length), head_size, outline_width)
        
        # Spikes (for mace)
        spike_count = 4
        for i in range(spike_count):
            angle = (i / spike_count) * 2 * math.pi
            spike_x = cx + int(math.cos(angle) * head_size * 1.3)
            spike_y = cy - handle_length + int(math.sin(angle) * head_size * 1.3)
            pygame.draw.line(screen, head_color, (cx, cy - handle_length), (spike_x, spike_y), 3)
    
    @staticmethod
    def _draw_stick(screen, cx, cy, wood_color, scale, outline_width, entity=None):
        """Draw a simple stick with floating position and swing animation"""
        # Double the length as requested
        stick_length = int(44 * scale)
        stick_width = int(5 * scale)
        
        # Use a nice brown color
        brown_color = (139, 90, 43)  # Medium brown
        dark_brown = (101, 67, 33)  # Darker brown for grain
        
        # Position stick to the side and make it "float"
        side_offset = 25  # Position to the right side
        float_offset = -10  # Float up a bit
        
        # Calculate swing animation based on last attack time
        rotation_angle = 0
        if entity and hasattr(entity, 'last_attack_time'):
            time_since_attack = time.time() - entity.last_attack_time
            # Swing animation lasts 0.3 seconds
            if time_since_attack < 0.3:
                # Swing from 90 degrees down to 0 (forward)
                progress = time_since_attack / 0.3
                # Smooth easing function
                ease_progress = 1 - (1 - progress) ** 3
                rotation_angle = math.radians(90 - (90 * ease_progress))
        
        # Calculate stick endpoints with rotation
        start_x = cx + side_offset
        start_y = cy + float_offset
        
        # Calculate end point with rotation
        end_x = start_x + int(math.sin(rotation_angle) * stick_length)
        end_y = start_y - int(math.cos(rotation_angle) * stick_length)
        
        # Draw the stick as a thick line
        pygame.draw.line(screen, brown_color, (start_x, start_y), (end_x, end_y), stick_width)
        pygame.draw.line(screen, (0, 0, 0), (start_x, start_y), (end_x, end_y), outline_width)
        
        # Add wood grain detail lines (perpendicular to stick)
        if stick_length > 10:
            for i in range(1, 4):
                grain_progress = i / 4.0
                grain_x = start_x + int(math.sin(rotation_angle) * stick_length * grain_progress)
                grain_y = start_y - int(math.cos(rotation_angle) * stick_length * grain_progress)
                
                # Draw small perpendicular grain line
                grain_offset = 2
                grain_x1 = grain_x + int(math.cos(rotation_angle) * grain_offset)
                grain_y1 = grain_y + int(math.sin(rotation_angle) * grain_offset)
                grain_x2 = grain_x - int(math.cos(rotation_angle) * grain_offset)
                grain_y2 = grain_y - int(math.sin(rotation_angle) * grain_offset)
                pygame.draw.line(screen, dark_brown, (grain_x1, grain_y1), (grain_x2, grain_y2), 1)


# Convenience function for easy access
def draw_entity_equipment(screen, entity, center_pos, entity_type="enemy"):
    """
    Convenience function to draw equipment on any entity.
    
    Args:
        screen: Pygame surface
        entity: Entity with equipment
        center_pos: (x, y) center position
        entity_type: "player", "npc", or "enemy"
    """
    renderer = EquipmentRenderer()
    renderer.draw_equipment(screen, entity, center_pos, entity_type)

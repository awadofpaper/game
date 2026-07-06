"""
Sprite Renderer Module
Handles visual character and equipment sprites with pixel-art style graphics
Can use procedurally generated graphics or load from image files
"""

import pygame
import math
from equipment import EQUIPMENT_DATA, EQUIPMENT_RARITY


class SpriteRenderer:
    """
    Renders character sprites with equipment overlays.
    Supports both procedurally generated pixel art and image files.
    """
    
    # Cache for generated sprites
    _sprite_cache = {}
    _equipment_cache = {}
    
    @staticmethod
    def draw_player_sprite(screen, player, center_pos, camera_offset=(0, 0)):
        """
        Draw the player character with equipment overlays
        
        Args:
            screen: Pygame surface to draw on
            player: Player object
            center_pos: (x, y) tuple for center position on screen
            camera_offset: Optional camera offset for animations
        """
        cx, cy = center_pos
        
        # Draw base character sprite
        SpriteRenderer._draw_base_character(screen, cx, cy, player.color)
        
        # Draw equipped items as overlays
        if hasattr(player, 'equipment') and isinstance(player.equipment, dict):
            SpriteRenderer._draw_equipment_overlays(screen, cx, cy, player.equipment, "player")
    
    @staticmethod
    def draw_npc_sprite(screen, npc, center_pos):
        """Draw NPC character with equipment"""
        cx, cy = center_pos
        
        # Draw base character
        npc_color = getattr(npc, 'color', (100, 150, 200))
        SpriteRenderer._draw_base_character(screen, cx, cy, npc_color, scale=0.85)
        
        # Draw equipment
        if hasattr(npc, 'equipment'):
            equipped = npc.equipment if isinstance(npc.equipment, dict) else {}
            SpriteRenderer._draw_equipment_overlays(screen, cx, cy, equipped, "npc")
    
    @staticmethod
    def draw_enemy_sprite(screen, enemy, center_pos):
        """Draw enemy character with equipment"""
        cx, cy = center_pos
        
        # Draw base character (larger for enemies)
        enemy_color = getattr(enemy, 'color', (200, 50, 50))
        SpriteRenderer._draw_base_character(screen, cx, cy, enemy_color, scale=1.1)
        
        # Draw equipment
        if hasattr(enemy, 'equipment'):
            equipped = enemy.equipment if isinstance(enemy.equipment, dict) else {}
            SpriteRenderer._draw_equipment_overlays(screen, cx, cy, equipped, "enemy")
    
    @staticmethod
    def _draw_base_character(screen, cx, cy, color, scale=1.0):
        """
        Draw a pixel-art style humanoid character
        """
        # Scale dimensions
        s = scale
        
        # Character dimensions
        head_size = int(10 * s)
        body_width = int(12 * s)
        body_height = int(16 * s)
        arm_width = int(4 * s)
        arm_length = int(14 * s)
        leg_width = int(5 * s)
        leg_length = int(14 * s)
        
        # Skin tone (lighter version of color)
        skin_color = tuple(min(255, c + 50) for c in color)
        outline_color = (0, 0, 0)
        
        # === HEAD ===
        head_y = cy - body_height//2 - head_size
        pygame.draw.circle(screen, skin_color, (cx, head_y), head_size)
        pygame.draw.circle(screen, outline_color, (cx, head_y), head_size, 2)
        
        # Eyes
        eye_offset = int(4 * s)
        eye_size = int(2 * s)
        pygame.draw.circle(screen, (0, 0, 0), (cx - eye_offset, head_y - 2), eye_size)
        pygame.draw.circle(screen, (0, 0, 0), (cx + eye_offset, head_y - 2), eye_size)
        
        # === BODY ===
        body_rect = pygame.Rect(cx - body_width//2, cy - body_height//2, body_width, body_height)
        pygame.draw.rect(screen, color, body_rect)
        pygame.draw.rect(screen, outline_color, body_rect, 2)
        
        # === ARMS ===
        # Left arm
        left_arm_x = cx - body_width//2 - arm_width//2
        arm_y_start = cy - body_height//2 + 4
        left_arm = pygame.Rect(left_arm_x - arm_width//2, arm_y_start, arm_width, arm_length)
        pygame.draw.rect(screen, skin_color, left_arm)
        pygame.draw.rect(screen, outline_color, left_arm, 2)
        
        # Right arm
        right_arm_x = cx + body_width//2 + arm_width//2
        right_arm = pygame.Rect(right_arm_x - arm_width//2, arm_y_start, arm_width, arm_length)
        pygame.draw.rect(screen, skin_color, right_arm)
        pygame.draw.rect(screen, outline_color, right_arm, 2)
        
        # === LEGS ===
        leg_y_start = cy + body_height//2
        
        # Left leg
        left_leg_x = cx - leg_width//2 - 1
        left_leg = pygame.Rect(left_leg_x - leg_width//2, leg_y_start, leg_width, leg_length)
        pygame.draw.rect(screen, color, left_leg)
        pygame.draw.rect(screen, outline_color, left_leg, 2)
        
        # Right leg
        right_leg_x = cx + leg_width//2 + 1
        right_leg = pygame.Rect(right_leg_x - leg_width//2, leg_y_start, leg_width, leg_length)
        pygame.draw.rect(screen, color, right_leg)
        pygame.draw.rect(screen, outline_color, right_leg, 2)
    
    @staticmethod
    def _draw_equipment_overlays(screen, cx, cy, equipped_items, entity_type="player"):
        """Draw equipment pieces as overlays on the character"""
        scale = 1.0 if entity_type == "player" else (0.85 if entity_type == "npc" else 1.1)
        
        # Draw in proper layer order (back to front)
        layer_order = ['legs', 'feet', 'chest', 'main_hand', 'off_hand', 'head']
        
        for slot in layer_order:
            item = equipped_items.get(slot)
            if item:
                SpriteRenderer._draw_equipment_piece(screen, cx, cy, slot, item, scale)
    
    @staticmethod
    def _draw_equipment_piece(screen, cx, cy, slot, item, scale=1.0):
        """Draw a specific equipment piece"""
        # Get item data
        item_name = item if isinstance(item, str) else getattr(item, 'name', None)
        if not item_name or item_name not in EQUIPMENT_DATA:
            return
        
        item_data = EQUIPMENT_DATA[item_name]
        rarity = item_data.get("rarity", "common")
        equip_color = item_data.get("color", EQUIPMENT_RARITY[rarity]["color"])
        
        outline_color = (0, 0, 0)
        s = scale
        
        if slot == "head":
            SpriteRenderer._draw_helmet(screen, cx, cy, equip_color, outline_color, s)
        elif slot == "chest":
            SpriteRenderer._draw_chest_armor(screen, cx, cy, equip_color, outline_color, s)
        elif slot == "legs":
            SpriteRenderer._draw_leg_armor(screen, cx, cy, equip_color, outline_color, s)
        elif slot == "feet":
            SpriteRenderer._draw_boots(screen, cx, cy, equip_color, outline_color, s)
        elif slot == "main_hand":
            SpriteRenderer._draw_weapon(screen, cx, cy, item_name, item_data, equip_color, outline_color, s, "right")
        elif slot == "off_hand":
            SpriteRenderer._draw_weapon(screen, cx, cy, item_name, item_data, equip_color, outline_color, s, "left")
    
    # === ARMOR PIECE RENDERERS ===
    
    @staticmethod
    def _draw_helmet(screen, cx, cy, color, outline, scale):
        """Draw helmet on character's head"""
        head_y = cy - int(24 * scale)
        head_size = int(11 * scale)
        
        # Helmet dome
        pygame.draw.circle(screen, color, (cx, head_y), head_size)
        pygame.draw.circle(screen, outline, (cx, head_y), head_size, 2)
        
        # Visor/face guard
        visor_width = int(14 * scale)
        visor_height = int(6 * scale)
        visor_rect = pygame.Rect(cx - visor_width//2, head_y - 2, visor_width, visor_height)
        pygame.draw.rect(screen, (50, 50, 50), visor_rect)
        pygame.draw.rect(screen, outline, visor_rect, 1)
        
        # Helmet detail lines
        pygame.draw.line(screen, outline, (cx - head_size, head_y), (cx + head_size, head_y), 1)
    
    @staticmethod
    def _draw_chest_armor(screen, cx, cy, color, outline, scale):
        """Draw chest armor/breastplate"""
        width = int(14 * scale)
        height = int(18 * scale)
        y_offset = int(-8 * scale)
        
        armor_rect = pygame.Rect(cx - width//2, cy + y_offset - height//2, width, height)
        
        # Main armor plate
        pygame.draw.rect(screen, color, armor_rect)
        pygame.draw.rect(screen, outline, armor_rect, 2)
        
        # Armor details
        # Center line
        pygame.draw.line(screen, outline, (cx, armor_rect.top), (cx, armor_rect.bottom), 1)
        
        # Shoulder guards
        shoulder_size = int(6 * scale)
        pygame.draw.circle(screen, color, (armor_rect.left, armor_rect.top + 4), shoulder_size//2)
        pygame.draw.circle(screen, outline, (armor_rect.left, armor_rect.top + 4), shoulder_size//2, 1)
        pygame.draw.circle(screen, color, (armor_rect.right, armor_rect.top + 4), shoulder_size//2)
        pygame.draw.circle(screen, outline, (armor_rect.right, armor_rect.top + 4), shoulder_size//2, 1)
    
    @staticmethod
    def _draw_leg_armor(screen, cx, cy, color, outline, scale):
        """Draw leg armor/greaves"""
        leg_width = int(6 * scale)
        leg_height = int(16 * scale)
        y_offset = int(10 * scale)
        spacing = int(3 * scale)
        
        # Left leg armor
        left_rect = pygame.Rect(cx - spacing - leg_width, cy + y_offset, leg_width, leg_height)
        pygame.draw.rect(screen, color, left_rect)
        pygame.draw.rect(screen, outline, left_rect, 2)
        
        # Knee guard
        pygame.draw.circle(screen, color, (left_rect.centerx, left_rect.centery), int(4 * scale))
        pygame.draw.circle(screen, outline, (left_rect.centerx, left_rect.centery), int(4 * scale), 1)
        
        # Right leg armor
        right_rect = pygame.Rect(cx + spacing, cy + y_offset, leg_width, leg_height)
        pygame.draw.rect(screen, color, right_rect)
        pygame.draw.rect(screen, outline, right_rect, 2)
        
        # Knee guard
        pygame.draw.circle(screen, color, (right_rect.centerx, right_rect.centery), int(4 * scale))
        pygame.draw.circle(screen, outline, (right_rect.centerx, right_rect.centery), int(4 * scale), 1)
    
    @staticmethod
    def _draw_boots(screen, cx, cy, color, outline, scale):
        """Draw boots on character's feet"""
        boot_width = int(6 * scale)
        boot_height = int(8 * scale)
        y_offset = int(26 * scale)
        spacing = int(3 * scale)
        
        # Left boot
        left_boot = pygame.Rect(cx - spacing - boot_width, cy + y_offset, boot_width, boot_height)
        pygame.draw.rect(screen, color, left_boot)
        pygame.draw.rect(screen, outline, left_boot, 2)
        
        # Right boot
        right_boot = pygame.Rect(cx + spacing, cy + y_offset, boot_width, boot_height)
        pygame.draw.rect(screen, color, right_boot)
        pygame.draw.rect(screen, outline, right_boot, 2)
    
    # === WEAPON RENDERERS ===
    
    @staticmethod
    def _draw_weapon(screen, cx, cy, weapon_name, weapon_data, color, outline, scale, hand="right"):
        """Draw weapon in character's hand"""
        # Hand position
        hand_x_offset = int(14 * scale) if hand == "right" else int(-14 * scale)
        hand_y = cy - int(4 * scale)
        hand_x = cx + hand_x_offset
        
        blade_color = weapon_data.get("blade_color", color)
        handle_color = weapon_data.get("handle_color", (80, 60, 40))
        
        weapon_lower = weapon_name.lower()
        
        if "sword" in weapon_lower:
            SpriteRenderer._draw_sword_detailed(screen, hand_x, hand_y, blade_color, handle_color, outline, scale)
        elif "axe" in weapon_lower:
            SpriteRenderer._draw_axe_detailed(screen, hand_x, hand_y, blade_color, handle_color, outline, scale)
        elif "staff" in weapon_lower:
            SpriteRenderer._draw_staff_detailed(screen, hand_x, hand_y, blade_color, handle_color, outline, scale)
        elif "shield" in weapon_lower:
            SpriteRenderer._draw_shield_detailed(screen, hand_x, hand_y, blade_color, outline, scale)
        elif "dagger" in weapon_lower:
            SpriteRenderer._draw_dagger_detailed(screen, hand_x, hand_y, blade_color, handle_color, outline, scale)
        elif "bow" in weapon_lower:
            SpriteRenderer._draw_bow_detailed(screen, hand_x, hand_y, blade_color, outline, scale)
        elif "spear" in weapon_lower:
            SpriteRenderer._draw_spear_detailed(screen, hand_x, hand_y, blade_color, handle_color, outline, scale)
        elif "mace" in weapon_lower or "club" in weapon_lower:
            SpriteRenderer._draw_mace_detailed(screen, hand_x, hand_y, blade_color, handle_color, outline, scale)
        elif "wand" in weapon_lower:
            SpriteRenderer._draw_wand_detailed(screen, hand_x, hand_y, blade_color, handle_color, outline, scale)
    
    @staticmethod
    def _draw_sword_detailed(screen, x, y, blade_color, handle_color, outline, scale):
        """Draw a detailed sword"""
        blade_length = int(24 * scale)
        blade_width = int(6 * scale)
        handle_length = int(8 * scale)
        guard_width = int(12 * scale)
        
        # Blade (tapered)
        blade_points = [
            (x - blade_width//2, y - 4),
            (x + blade_width//2, y - 4),
            (x + blade_width//4, y - blade_length + 4),
            (x - blade_width//4, y - blade_length + 4)
        ]
        pygame.draw.polygon(screen, blade_color, blade_points)
        pygame.draw.polygon(screen, outline, blade_points, 2)
        
        # Tip
        tip_points = [
            (x - blade_width//4, y - blade_length + 4),
            (x + blade_width//4, y - blade_length + 4),
            (x, y - blade_length - 4)
        ]
        pygame.draw.polygon(screen, blade_color, tip_points)
        pygame.draw.polygon(screen, outline, tip_points, 2)
        
        # Guard (crossguard)
        guard_rect = pygame.Rect(x - guard_width//2, y - 6, guard_width, 4)
        pygame.draw.rect(screen, blade_color, guard_rect)
        pygame.draw.rect(screen, outline, guard_rect, 1)
        
        # Handle
        handle_rect = pygame.Rect(x - 3, y - 2, 6, handle_length)
        pygame.draw.rect(screen, handle_color, handle_rect)
        pygame.draw.rect(screen, outline, handle_rect, 1)
        
        # Pommel
        pygame.draw.circle(screen, handle_color, (x, y + handle_length), 4)
        pygame.draw.circle(screen, outline, (x, y + handle_length), 4, 1)
    
    @staticmethod
    def _draw_axe_detailed(screen, x, y, blade_color, handle_color, outline, scale):
        """Draw a detailed axe"""
        handle_length = int(20 * scale)
        blade_size = int(12 * scale)
        
        # Handle
        handle_rect = pygame.Rect(x - 3, y, 6, handle_length)
        pygame.draw.rect(screen, handle_color, handle_rect)
        pygame.draw.rect(screen, outline, handle_rect, 2)
        
        # Blade (asymmetric)
        blade_points = [
            (x - 2, y - 4),
            (x + 2, y - 4),
            (x + blade_size, y + blade_size//2),
            (x + 2, y + blade_size)
        ]
        pygame.draw.polygon(screen, blade_color, blade_points)
        pygame.draw.polygon(screen, outline, blade_points, 2)
    
    @staticmethod
    def _draw_staff_detailed(screen, x, y, orb_color, wood_color, outline, scale):
        """Draw a detailed staff"""
        staff_length = int(32 * scale)
        
        # Staff shaft
        pygame.draw.line(screen, wood_color, (x, y - 8), (x, y + staff_length - 8), 5)
        pygame.draw.line(screen, outline, (x, y - 8), (x, y + staff_length - 8), 1)
        
        # Top orb/crystal
        orb_size = int(6 * scale)
        pygame.draw.circle(screen, orb_color, (x, y - 12), orb_size)
        pygame.draw.circle(screen, outline, (x, y - 12), orb_size, 2)
        
        # Glow effect
        glow_surface = pygame.Surface((orb_size * 3, orb_size * 3), pygame.SRCALPHA)
        glow_color = (*orb_color[:3], 80)
        pygame.draw.circle(glow_surface, glow_color, (orb_size * 3 // 2, orb_size * 3 // 2), orb_size * 1.5)
        screen.blit(glow_surface, (x - orb_size * 1.5, y - 12 - orb_size * 1.5))
    
    @staticmethod
    def _draw_shield_detailed(screen, x, y, shield_color, outline, scale):
        """Draw a detailed shield"""
        width = int(10 * scale)
        height = int(16 * scale)
        
        # Shield body (kite shield shape)
        shield_points = [
            (x - width//2, y - height//2),
            (x + width//2, y - height//2),
            (x + width//2, y + height//4),
            (x, y + height//2),
            (x - width//2, y + height//4)
        ]
        pygame.draw.polygon(screen, shield_color, shield_points)
        pygame.draw.polygon(screen, outline, shield_points, 2)
        
        # Shield boss (center)
        pygame.draw.circle(screen, (150, 150, 150), (x, y), 4)
        pygame.draw.circle(screen, outline, (x, y), 4, 1)
        
        # Cross design
        pygame.draw.line(screen, outline, (x, y - height//3), (x, y + height//3), 2)
        pygame.draw.line(screen, outline, (x - width//3, y), (x + width//3, y), 2)
    
    @staticmethod
    def _draw_dagger_detailed(screen, x, y, blade_color, handle_color, outline, scale):
        """Draw a detailed dagger"""
        blade_length = int(12 * scale)
        handle_length = int(6 * scale)
        
        # Blade (small and pointed)
        blade_points = [
            (x - 2, y),
            (x + 2, y),
            (x, y - blade_length)
        ]
        pygame.draw.polygon(screen, blade_color, blade_points)
        pygame.draw.polygon(screen, outline, blade_points, 1)
        
        # Guard
        pygame.draw.line(screen, blade_color, (x - 6, y), (x + 6, y), 3)
        
        # Handle
        handle_rect = pygame.Rect(x - 2, y, 4, handle_length)
        pygame.draw.rect(screen, handle_color, handle_rect)
        pygame.draw.rect(screen, outline, handle_rect, 1)
    
    @staticmethod
    def _draw_bow_detailed(screen, x, y, bow_color, outline, scale):
        """Draw a detailed bow"""
        bow_height = int(20 * scale)
        
        # Bow arc (curve)
        pygame.draw.arc(screen, bow_color, (x - 8, y - bow_height//2, 16, bow_height), 
                       -math.pi/2 - 0.5, math.pi/2 + 0.5, 3)
        
        # Bowstring
        pygame.draw.line(screen, (200, 200, 200), (x - 6, y - bow_height//2 + 2), 
                        (x - 6, y + bow_height//2 - 2), 1)
    
    @staticmethod
    def _draw_spear_detailed(screen, x, y, blade_color, handle_color, outline, scale):
        """Draw a detailed spear"""
        shaft_length = int(28 * scale)
        spearhead_length = int(10 * scale)
        
        # Shaft
        pygame.draw.line(screen, handle_color, (x, y), (x, y + shaft_length), 4)
        pygame.draw.line(screen, outline, (x, y), (x, y + shaft_length), 1)
        
        # Spearhead (triangle)
        head_points = [
            (x - 4, y - 2),
            (x + 4, y - 2),
            (x, y - spearhead_length)
        ]
        pygame.draw.polygon(screen, blade_color, head_points)
        pygame.draw.polygon(screen, outline, head_points, 2)
    
    @staticmethod
    def _draw_mace_detailed(screen, x, y, head_color, handle_color, outline, scale):
        """Draw a detailed mace"""
        handle_length = int(16 * scale)
        head_size = int(8 * scale)
        
        # Handle
        pygame.draw.line(screen, handle_color, (x, y), (x, y + handle_length), 5)
        pygame.draw.line(screen, outline, (x, y), (x, y + handle_length), 1)
        
        # Mace head (spiked)
        pygame.draw.circle(screen, head_color, (x, y - head_size//2), head_size)
        pygame.draw.circle(screen, outline, (x, y - head_size//2), head_size, 2)
        
        # Spikes
        spike_offsets = [(-head_size, 0), (head_size, 0), (0, -head_size), (0, head_size)]
        for dx, dy in spike_offsets:
            spike_x = x + dx
            spike_y = y - head_size//2 + dy
            pygame.draw.line(screen, outline, (x + dx//2, y - head_size//2 + dy//2), 
                           (spike_x, spike_y), 2)
    
    @staticmethod
    def _draw_wand_detailed(screen, x, y, tip_color, wood_color, outline, scale):
        """Draw a detailed wand"""
        wand_length = int(16 * scale)
        
        # Wand shaft (thinner than staff)
        pygame.draw.line(screen, wood_color, (x, y), (x, y + wand_length), 3)
        pygame.draw.line(screen, outline, (x, y), (x, y + wand_length), 1)
        
        # Magical tip (small star)
        tip_size = 4
        pygame.draw.circle(screen, tip_color, (x, y - 4), tip_size)
        pygame.draw.circle(screen, outline, (x, y - 4), tip_size, 1)
        
        # Sparkle effect
        pygame.draw.line(screen, tip_color, (x - tip_size - 2, y - 4), (x + tip_size + 2, y - 4), 1)
        pygame.draw.line(screen, tip_color, (x, y - 4 - tip_size - 2), (x, y - 4 + tip_size + 2), 1)

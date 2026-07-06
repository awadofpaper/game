"""
Equipment Repair and Degradation System
Handles durability loss, repair mechanics, and equipment maintenance
"""

import pygame
import random
from equipment import EQUIPMENT_RARITY, EQUIPMENT_DATA

class RepairSystem:
    """Manages equipment durability and repair mechanics"""
    
    # Degradation rates by rarity (per action)
    DEGRADATION_RATES = {
        "common": 1.0,
        "uncommon": 0.8,
        "rare": 0.6,
        "epic": 0.4,
        "legendary": 0.4,
        "artifact": 0.4,
        "set": 0.4
    }
    
    # Repair percentages when using equipment as scrap
    REPAIR_PERCENTAGES = {
        "same": 0.50,      # Same rarity as equipped item
        "lower": 0.25,     # Lower rarity than equipped item
        "higher": 0.75,    # Higher rarity than equipped item
        "material": 0.15   # Basic materials (stick/fiber)
    }
    
    def __init__(self):
        self.enabled = True  # Can be toggled in settings
        self.auto_scrap_enabled = False  # Auto-scrap common/uncommon drops
        
    def get_degradation_amount(self, item_rarity, player_repair_skill=0):
        """Calculate degradation amount based on rarity and player's repair skill"""
        base_rate = self.DEGRADATION_RATES.get(item_rarity, 1.0)
        
        # Repair skill reduces degradation (each level reduces by 2%, max 50% reduction at level 25)
        skill_reduction = min(0.50, player_repair_skill * 0.02)
        
        final_rate = base_rate * (1.0 - skill_reduction)
        return max(0.1, final_rate)  # Minimum 0.1 durability loss
    
    def degrade_equipment(self, item, item_rarity, player_repair_skill=0):
        """Degrade an item's durability"""
        if not self.enabled or not hasattr(item, 'durability'):
            return
        
        degradation = self.get_degradation_amount(item_rarity, player_repair_skill)
        item.degrade(degradation)
        
    def is_broken(self, item):
        """Check if item is broken (0 durability)"""
        if not hasattr(item, 'durability'):
            return False
        return item.durability <= 0
    
    def get_durability_percentage(self, item):
        """Get durability as percentage"""
        if not hasattr(item, 'durability') or not hasattr(item, 'max_durability'):
            return 100.0
        if item.max_durability <= 0:
            return 100.0
        return (item.durability / item.max_durability) * 100
    
    def get_stat_multiplier(self, item):
        """Get stat multiplier based on durability (broken = 5%)"""
        durability_pct = self.get_durability_percentage(item)
        
        if durability_pct <= 0:
            return 0.05  # Broken equipment gives 5% stats
        return 1.0  # Full stats if not broken
    
    def calculate_repair_amount(self, equipped_item, scrap_item, equipped_rarity, scrap_rarity, player_repair_skill=0):
        """Calculate how much durability to restore when using scrap"""
        if not hasattr(equipped_item, 'max_durability'):
            return 0
        
        # Get rarity levels for comparison
        rarity_order = ["common", "uncommon", "rare", "epic", "legendary", "artifact", "set"]
        equipped_level = rarity_order.index(equipped_rarity) if equipped_rarity in rarity_order else 0
        scrap_level = rarity_order.index(scrap_rarity) if scrap_rarity in rarity_order else 0
        
        # Determine repair percentage
        if equipped_level == scrap_level:
            repair_pct = self.REPAIR_PERCENTAGES["same"]
        elif scrap_level < equipped_level:
            repair_pct = self.REPAIR_PERCENTAGES["lower"]
        else:
            repair_pct = self.REPAIR_PERCENTAGES["higher"]
        
        # Repair skill increases effectiveness (each level adds 1%, max 25% bonus at level 25)
        skill_bonus = min(0.25, player_repair_skill * 0.01)
        final_repair_pct = min(1.0, repair_pct + skill_bonus)
        
        # Calculate repair amount
        repair_amount = equipped_item.max_durability * final_repair_pct
        return repair_amount
    
    def repair_with_materials(self, equipped_item, material_type, material_count, player_repair_skill=0):
        """Repair using basic materials (stick/fiber)"""
        if not hasattr(equipped_item, 'max_durability'):
            return 0, 0
        
        # Each material restores 15% base (modified by skill)
        base_pct = self.REPAIR_PERCENTAGES["material"]
        skill_bonus = min(0.25, player_repair_skill * 0.01)
        repair_pct_per_material = base_pct + skill_bonus
        
        # Calculate total repair
        total_repair_pct = repair_pct_per_material * material_count
        repair_amount = equipped_item.max_durability * total_repair_pct
        
        # How many materials to use (don't over-repair)
        durability_needed = equipped_item.max_durability - equipped_item.durability
        materials_needed = min(material_count, int(durability_needed / (equipped_item.max_durability * repair_pct_per_material)) + 1)
        
        actual_repair = min(repair_amount, durability_needed)
        
        return actual_repair, materials_needed
    
    def should_show_warning(self, item):
        """Check if durability warning should be shown"""
        durability_pct = self.get_durability_percentage(item)
        return durability_pct <= 25.0  # Show warning at 25% or below
    
    def get_warning_color(self, item):
        """Get warning color based on durability"""
        durability_pct = self.get_durability_percentage(item)
        
        if durability_pct <= 10.0:
            return (255, 0, 0)  # Red at 10%
        elif durability_pct <= 25.0:
            return (255, 255, 0)  # Yellow at 25%
        return (255, 255, 255)  # White (no warning)
    
    def can_auto_scrap(self, item_rarity):
        """Check if item rarity should be auto-scrapped"""
        if not self.auto_scrap_enabled:
            return False
        # Only auto-scrap common and uncommon
        return item_rarity in ["common", "uncommon"]
    
    def find_best_item_to_repair(self, equipped_items):
        """Find the equipped item with lowest durability and highest rarity to prioritize repair"""
        rarity_priority = {"artifact": 6, "legendary": 5, "epic": 4, "rare": 3, "uncommon": 2, "common": 1, "set": 7}
        
        items_with_priority = []
        for slot, item in equipped_items.items():
            if item and hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                durability_pct = self.get_durability_percentage(item)
                if durability_pct < 100:  # Only consider items that need repair
                    item_rarity = getattr(item, 'rarity', 'common')
                    rarity_score = rarity_priority.get(item_rarity, 0)
                    # Sort by: highest rarity first, then lowest durability
                    items_with_priority.append((slot, item, rarity_score, durability_pct))
        
        if not items_with_priority:
            return None, None
        
        # Sort: highest rarity (descending), then lowest durability (ascending)
        items_with_priority.sort(key=lambda x: (-x[2], x[3]))
        
        return items_with_priority[0][0], items_with_priority[0][1]


class RepairUI:
    """UI for equipment repair in the equipment menu"""
    
    def __init__(self, repair_system):
        self.repair_system = repair_system
        self.selected_slot = None
        self.selected_scrap_idx = 0
        self.mode = "select_item"  # "select_item" or "select_scrap"
        
    def draw_repair_panel(self, screen, font, player, equipped_items, x, y, width, height):
        """Draw repair panel in equipment menu"""
        # Panel background
        pygame.draw.rect(screen, (40, 40, 50), (x, y, width, height))
        pygame.draw.rect(screen, (100, 100, 120), (x, y, width, height), 2)
        
        # Title
        title_font = pygame.font.SysFont(None, 28)
        title = title_font.render("Equipment Repair", True, (255, 215, 0))
        screen.blit(title, (x + 10, y + 5))
        
        current_y = y + 40
        
        # Show equipped items that need repair
        repair_text = font.render("Items needing repair:", True, (200, 200, 200))
        screen.blit(repair_text, (x + 10, current_y))
        current_y += 25
        
        items_needing_repair = []
        for slot, item in equipped_items.items():
            if item and hasattr(item, 'durability'):
                durability_pct = self.repair_system.get_durability_percentage(item)
                if durability_pct < 100:
                    items_needing_repair.append((slot, item, durability_pct))
        
        if not items_needing_repair:
            no_repair_text = font.render("All equipment in good condition!", True, (100, 255, 100))
            screen.blit(no_repair_text, (x + 20, current_y))
        else:
            for slot, item, durability_pct in items_needing_repair:
                color = self.repair_system.get_warning_color(item)
                item_name = getattr(item, 'name', slot)
                dur_text = font.render(f"{item_name}: {durability_pct:.0f}%", True, color)
                screen.blit(dur_text, (x + 20, current_y))
                
                # Draw durability bar
                bar_width = 100
                bar_height = 8
                bar_x = x + 220
                bar_y = current_y + 4
                
                # Background
                pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
                # Filled portion
                filled_width = int(bar_width * (durability_pct / 100))
                pygame.draw.rect(screen, color, (bar_x, bar_y, filled_width, bar_height))
                # Border
                pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 1)
                
                current_y += 22
        
        # Instructions
        current_y += 10
        help_font = pygame.font.SysFont(None, 20)
        
        if self.repair_system.enabled:
            help1 = help_font.render("Use equipment items to repair in Equipment Menu", True, (180, 180, 180))
            screen.blit(help1, (x + 10, current_y))
            current_y += 20
            
            help2 = help_font.render("Materials: Stick/Fiber restore 15% durability", True, (180, 180, 180))
            screen.blit(help2, (x + 10, current_y))
        else:
            disabled_text = help_font.render("Equipment Degradation: DISABLED", True, (150, 150, 150))
            screen.blit(disabled_text, (x + 10, current_y))


# Global instance
_repair_system = None

def get_repair_system():
    """Get singleton instance of repair system"""
    global _repair_system
    if _repair_system is None:
        _repair_system = RepairSystem()
    return _repair_system

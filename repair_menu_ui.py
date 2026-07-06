# repair_menu_ui.py
"""
Comprehensive Repair System
- Material-based repair (wood, iron ore, cloth, leather)
- Equipment-to-equipment repair (Fallout 3 style)
- Equipment scrapping system
- Skill tree integration
"""

import pygame
import logging

logger = logging.getLogger(__name__)


# Material Mapping: What materials can repair what items
MATERIAL_REPAIR_MAP = {
    # Wooden items
    'wood': ['wooden', 'wood', 'stick'],
    
    # Metal items (iron tier)
    'iron_ore': ['iron', 'steel', 'metal'],
    'iron': ['iron', 'steel', 'metal'],
    
    # Higher tier metals
    'steel_ore': ['steel', 'mithril'],
    'mithril_ore': ['mithril', 'adamantite'],
    
    # Leather/Cloth
    'leather': ['leather'],
    'cloth': ['cloth', 'fabric', 'linen'],
    'fiber': ['cloth', 'fabric']
}


# Material costs for different item rarities
RARITY_MATERIAL_MULTIPLIER = {
    'common': 1,
    'uncommon': 2,
    'rare': 3,
    'epic': 5,
    'legendary': 8
}


class RepairMenuUI:
    """UI for repairing equipment using materials or other equipment"""
    
    def __init__(self, config, player):
        self.config = config
        self.player = player
        self.active = False
        
        # UI state
        self.selected_item_idx = 0
        self.scroll_offset = 0
        self.max_visible_items = 10
        self.repair_mode = "material"  # "material" or "equipment"
        self.show_equipment_list = False  # When right-click is pressed
        self.selected_repair_item_idx = 0
        self.repair_scroll_offset = 0
        
        # Confirmation state
        self.show_confirmation = False
        self.confirmation_message = ""
        self.pending_repair_action = None
        
        # Messages
        self.message = ""
        self.message_timer = 0
        
    def open(self):
        """Open the repair menu"""
        self.active = True
        self.selected_item_idx = 0
        self.scroll_offset = 0
        self.show_equipment_list = False
        self.show_confirmation = False
        logger.info("[REPAIR MENU] Opened")
    
    def close(self):
        """Close the repair menu"""
        self.active = False
        self.show_equipment_list = False
        self.show_confirmation = False
        logger.info("[REPAIR MENU] Closed")
    
    def get_repairable_items(self):
        """Get list of equipped items that need repair"""
        repairable = []
        
        for slot, item in self.player.equipment.items():
            if item and hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                if item.durability < item.max_durability:
                    repairable.append((slot, item))
        
        return repairable
    
    def get_material_requirements(self, item):
        """Calculate what materials are needed to repair an item"""
        if not hasattr(item, 'name') or not hasattr(item, 'durability'):
            return {}
        
        # Determine item material type from name
        item_name_lower = item.name.lower()
        item_material = self._get_item_material_type(item_name_lower)
        
        if not item_material:
            logger.warning(f"[REPAIR] Could not determine material for {item.name}")
            return {}
        
        # Calculate how many materials needed (1 material = 10% repair)
        damage_percent = 1.0 - (item.durability / item.max_durability)
        base_materials_needed = int((damage_percent * 10) + 0.5)  # Round up
        
        # Apply rarity multiplier
        rarity = getattr(item, 'rarity', 'common')
        material_multiplier = RARITY_MATERIAL_MULTIPLIER.get(rarity, 1)
        total_materials = max(1, base_materials_needed * material_multiplier)
        
        # Apply skill bonuses (reduce material cost)
        if hasattr(self.player, 'skills_manager'):
            repair_level = self.player.skills_manager.get_level('repair')
            # 1% reduction per level, max 50% reduction at level 50
            reduction = min(0.50, repair_level * 0.01)
            total_materials = max(1, int(total_materials * (1.0 - reduction)))
        
        return {item_material: total_materials}
    
    def _get_item_material_type(self, item_name):
        """Determine what material type an item is made from"""
        # Check for wooden items
        if any(word in item_name for word in ['wooden', 'wood', 'stick']):
            return 'wood'
        
        # Check for steel/high tier
        if any(word in item_name for word in ['steel', 'mithril', 'adamantite']):
            if 'mithril' in item_name:
                return 'mithril_ore'
            elif 'adamantite' in item_name:
                return 'mithril_ore'  # Use mithril for adamantite too
            else:
                return 'steel_ore'
        
        # Check for iron/metal
        if any(word in item_name for word in ['iron', 'metal', 'bronze', 'copper']):
            return 'iron_ore'
        
        # Check for leather
        if 'leather' in item_name:
            return 'leather'
        
        # Check for cloth/fabric
        if any(word in item_name for word in ['cloth', 'robe', 'tunic', 'linen']):
            return 'cloth'
        
        # Default to iron for weapons, leather for armor
        if any(word in item_name for word in ['sword', 'axe', 'mace', 'hammer', 'dagger']):
            return 'iron_ore'
        if any(word in item_name for word in ['armor', 'helmet', 'boots', 'gloves']):
            return 'leather'
        
        return None
    
    def get_compatible_equipment(self, target_item):
        """Get list of inventory items that can repair the target item"""
        compatible = []
        
        if not target_item:
            return compatible
        
        target_name = target_item.name.lower()
        target_type = getattr(target_item, 'type', 'unknown')
        
        # Check all inventory items
        for item in self.player.inventory.get('items', []):
            if item == target_item:
                continue  # Can't repair with itself
            
            if not hasattr(item, 'durability'):
                continue  # Not equipment
            
            # Check if compatible based on type or name similarity
            item_name = item.name.lower()
            item_type = getattr(item, 'type', 'unknown')
            
            # Same exact item
            if item.name == target_item.name:
                compatible.append(item)
                continue
            
            # Same type (weapon/armor)
            if item_type == target_type and target_type in ['weapon', 'armor']:
                compatible.append(item)
                continue
            
            # Similar material
            target_material = self._get_item_material_type(target_name)
            item_material = self._get_item_material_type(item_name)
            if target_material and target_material == item_material:
                compatible.append(item)
        
        return compatible
    
    def calculate_equipment_repair_amount(self, repair_item, target_item):
        """
        Calculate how much durability the repair item will restore.
        Based on durability % of repair item and quality comparison.
        """
        if not repair_item or not target_item:
            return 0
        
        # Get repair item's durability percentage
        repair_durability_percent = repair_item.durability / repair_item.max_durability
        
        # Base repair amounts based on durability
        if repair_durability_percent >= 0.50:
            base_repair = 20  # 20%
        elif repair_durability_percent >= 0.25:
            base_repair = 12  # 12%
        else:
            base_repair = 8   # 8%
        
        # Check quality/rarity comparison
        target_rarity = getattr(target_item, 'rarity', 'common')
        repair_rarity = getattr(repair_item, 'rarity', 'common')
        
        rarity_order = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        target_tier = rarity_order.index(target_rarity) if target_rarity in rarity_order else 0
        repair_tier = rarity_order.index(repair_rarity) if repair_rarity in rarity_order else 0
        
        # Higher quality item gives +10% bonus
        if repair_tier > target_tier:
            base_repair += 10
        
        # Apply skill bonuses
        if hasattr(self.player, 'skills_manager'):
            repair_level = self.player.skills_manager.get_level('repair')
            # 0.5% bonus per level, max +25% at level 50
            bonus = min(25, repair_level * 0.5)
            base_repair += int(bonus)
        
        # Field repair cap (90% unless master perks)
        max_repair = 90
        if hasattr(self.player, 'skills_manager'):
            # Check for master repair perk
            if hasattr(self.player.skills_manager, 'has_perk'):
                if self.player.skills_manager.has_perk('master_repair'):
                    max_repair = 100
        
        return min(base_repair, max_repair)
    
    def can_afford_material_repair(self, item):
        """Check if player has enough materials to repair item"""
        requirements = self.get_material_requirements(item)
        
        for material, amount in requirements.items():
            player_amount = self.player.inventory.get(material, 0)
            if player_amount < amount:
                return False, f"Need {amount} {material} (have {player_amount})"
        
        return True, ""
    
    def repair_with_materials(self, item):
        """Repair an item using materials from inventory"""
        requirements = self.get_material_requirements(item)
        
        # Check if affordable
        can_afford, error_msg = self.can_afford_material_repair(item)
        if not can_afford:
            self.message = error_msg
            self.message_timer = 120
            logger.warning(f"[REPAIR] Cannot afford: {error_msg}")
            return False
        
        # Consume materials
        for material, amount in requirements.items():
            self.player.inventory[material] -= amount
        
        # Calculate repair amount (10% per material unit base)
        damage_percent = 1.0 - (item.durability / item.max_durability)
        base_repair = int(item.max_durability * damage_percent)
        
        # Apply skill bonuses
        if hasattr(self.player, 'skills_manager'):
            repair_level = self.player.skills_manager.get_level('repair')
            # 0.5% bonus per level
            bonus = min(0.25, repair_level * 0.005)
            base_repair = int(base_repair * (1.0 + bonus))
        
        # Apply field repair cap (90% max unless master perks)
        max_durability_field = int(item.max_durability * 0.90)
        if hasattr(self.player, 'skills_manager'):
            if hasattr(self.player.skills_manager, 'has_perk'):
                if self.player.skills_manager.has_perk('master_repair'):
                    max_durability_field = item.max_durability
        
        # Apply repair
        new_durability = min(max_durability_field, item.durability + base_repair)
        actual_repair = new_durability - item.durability
        item.durability = new_durability
        
        # Grant skill XP
        if hasattr(self.player, 'skills_manager'):
            xp_gain = 10 * len(requirements)  # 10 XP per material type used
            self.player.skills_manager.add_experience('repair', xp_gain)
        
        materials_used = ", ".join([f"{amt} {mat}" for mat, amt in requirements.items()])
        self.message = f"Repaired {item.name} using {materials_used} (+{actual_repair} durability)"
        self.message_timer = 180
        logger.info(f"[REPAIR] Material repair: {item.name} +{actual_repair} durability")
        return True
    
    def repair_with_equipment(self, target_item, repair_item):
        """Repair target item using another piece of equipment"""
        if not target_item or not repair_item:
            return False
        
        # Calculate repair amount
        repair_percent = self.calculate_equipment_repair_amount(repair_item, target_item)
        repair_amount = int(target_item.max_durability * (repair_percent / 100.0))
        
        # Apply field repair cap
        max_durability_field = int(target_item.max_durability * 0.90)
        if hasattr(self.player, 'skills_manager'):
            if hasattr(self.player.skills_manager, 'has_perk'):
                if self.player.skills_manager.has_perk('master_repair'):
                    max_durability_field = target_item.max_durability
        
        new_durability = min(max_durability_field, target_item.durability + repair_amount)
        actual_repair = new_durability - target_item.durability
        target_item.durability = new_durability
        
        # Consume the repair item
        self.player.inventory['items'].remove(repair_item)
        
        # Grant skill XP
        if hasattr(self.player, 'skills_manager'):
            xp_gain = 15  # Flat XP for equipment repair
            self.player.skills_manager.add_experience('repair', xp_gain)
        
        self.message = f"Repaired {target_item.name} with {repair_item.name} (+{actual_repair} durability, +{repair_percent}%)"
        self.message_timer = 180
        logger.info(f"[REPAIR] Equipment repair: {target_item.name} +{repair_percent}%")
        return True
    
    def scrap_equipment(self, item):
        """Break down equipment into base materials"""
        if not item:
            return False
        
        # Determine what materials to return
        material_type = self._get_item_material_type(item.name.lower())
        if not material_type:
            self.message = f"Cannot scrap {item.name} - unknown material type"
            self.message_timer = 120
            return False
        
        # Base scrap return: 1 material
        scrap_amount = 1
        
        # Apply skill bonuses
        if hasattr(self.player, 'skills_manager'):
            repair_level = self.player.skills_manager.get_level('repair')
            # Every 10 levels adds +1 material return
            scrap_amount += repair_level // 10
        
        # Bonus materials for higher rarity
        rarity = getattr(item, 'rarity', 'common')
        if rarity == 'uncommon':
            scrap_amount += 1
        elif rarity == 'rare':
            scrap_amount += 2
        elif rarity == 'epic':
            scrap_amount += 3
            # 20% chance for rare component
            import random
            if random.random() < 0.20:
                self.player.inventory['rare_component'] = self.player.inventory.get('rare_component', 0) + 1
        elif rarity == 'legendary':
            scrap_amount += 5
            # Guaranteed rare components
            self.player.inventory['rare_component'] = self.player.inventory.get('rare_component', 0) + 2
        
        # Give materials to player
        self.player.inventory[material_type] = self.player.inventory.get(material_type, 0) + scrap_amount
        
        # Remove item from inventory
        self.player.inventory['items'].remove(item)
        
        # Grant skill XP
        if hasattr(self.player, 'skills_manager'):
            xp_gain = 5
            self.player.skills_manager.add_experience('repair', xp_gain)
        
        self.message = f"Scrapped {item.name} → {scrap_amount} {material_type}"
        self.message_timer = 180
        logger.info(f"[REPAIR] Scrapped {item.name} → {scrap_amount} {material_type}")
        return True
    
    def handle_input(self, event):
        """Handle keyboard and mouse input"""
        if not self.active:
            return None
        
        # Handle confirmation dialog
        if self.show_confirmation:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_y]:
                    # Confirm action
                    if self.pending_repair_action:
                        self.pending_repair_action()
                    self.show_confirmation = False
                    self.pending_repair_action = None
                    return "confirmed"
                elif event.key in [pygame.K_ESCAPE, pygame.K_n]:
                    # Cancel
                    self.show_confirmation = False
                    self.pending_repair_action = None
                    self.message = "Cancelled"
                    self.message_timer = 60
                    return "cancelled"
            return None
        
        # Handle equipment selection list
        if self.show_equipment_list:
            repairable = self.get_repairable_items()
            if not repairable:
                return None
            
            target_item = repairable[self.selected_item_idx][1]
            compatible = self.get_compatible_equipment(target_item)
            
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_repair_item_idx = max(0, self.selected_repair_item_idx - 1)
                    return "navigate"
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_repair_item_idx = min(len(compatible) - 1, self.selected_repair_item_idx + 1)
                    return "navigate"
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    # Select this repair item
                    if compatible:
                        repair_item = compatible[self.selected_repair_item_idx]
                        repair_percent = self.calculate_equipment_repair_amount(repair_item, target_item)
                        
                        # Check if using higher quality item
                        target_rarity = getattr(target_item, 'rarity', 'common')
                        repair_rarity = getattr(repair_item, 'rarity', 'common')
                        rarity_order = ['common', 'uncommon', 'rare', 'epic', 'legendary']
                        target_tier = rarity_order.index(target_rarity) if target_rarity in rarity_order else 0
                        repair_tier = rarity_order.index(repair_rarity) if repair_rarity in rarity_order else 0
                        
                        if repair_tier > target_tier:
                            self.confirmation_message = f"WARNING: Using {repair_rarity} {repair_item.name} to repair{target_rarity} {target_item.name}!\nThis will repair {repair_percent}% but consume the higher quality item.\nContinue? (Y/N)"
                        else:
                            self.confirmation_message = f"Repair {target_item.name} with {repair_item.name}?\nWill restore {repair_percent}% durability.\nContinue? (Y/N)"
                        
                        self.show_confirmation = True
                        self.pending_repair_action = lambda: self.repair_with_equipment(target_item, repair_item)
                        return "confirm_prompt"
                elif event.key == pygame.K_ESCAPE:
                    self.show_equipment_list = False
                    self.selected_repair_item_idx = 0
                    return "back"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - back
                    self.show_equipment_list = False
                    self.selected_repair_item_idx = 0
                    return "back"
            
            return None
        
        # Normal repair menu navigation
        repairable = self.get_repairable_items()
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_item_idx = max(0, self.selected_item_idx - 1)
                if self.selected_item_idx < self.scroll_offset:
                    self.scroll_offset = self.selected_item_idx
                return "navigate"
            
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_item_idx = min(len(repairable) - 1, self.selected_item_idx + 1)
                if self.selected_item_idx >= self.scroll_offset + self.max_visible_items:
                    self.scroll_offset = self.selected_item_idx - self.max_visible_items + 1
                return "navigate"
            
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                # Repair with materials
                if repairable:
                    item = repairable[self.selected_item_idx][1]
                    can_afford, error = self.can_afford_material_repair(item)
                    requirements = self.get_material_requirements(item)
                    
                    if can_afford:
                        materials_list = ", ".join([f"{amt} {mat}" for mat, amt in requirements.items()])
                        self.confirmation_message = f"Repair {item.name} using {materials_list}?\nContinue? (Y/N)"
                        self.show_confirmation = True
                        self.pending_repair_action = lambda: self.repair_with_materials(item)
                        return "confirm_prompt"
                    else:
                        self.message = error
                        self.message_timer = 120
                return "repair_attempt"
            
            elif event.key == pygame.K_ESCAPE:
                self.close()
                return "close"
            
            elif event.key == pygame.K_x:
                # Scrap selected item
                if repairable:
                    item = repairable[self.selected_item_idx][1]
                    self.confirmation_message = f"Scrap {item.name} for materials?\nThis will destroy the item!\nContinue? (Y/N)"
                    self.show_confirmation = True
                    self.pending_repair_action = lambda: self.scrap_equipment(item)
                    return "scrap_prompt"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right click - show equipment repair list
                if repairable:
                    self.show_equipment_list = True
                    self.selected_repair_item_idx = 0
                    return "show_equipment_list"
        
        return None
    
    def update(self, dt):
        """Update UI state"""
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""
    
    def draw(self, screen, font):
        """Draw the repair menu UI"""
        if not self.active:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.SysFont(None, 56)
        title_text = title_font.render("Equipment Repair", True, (255, 215, 0))
        screen.blit(title_text, (self.config.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
        
        # Instructions
        inst_font = pygame.font.SysFont(None, 24)
        instructions = [
            "WASD/Arrows: Select Item | Enter: Repair with Materials",
            "Right-Click: View Equipment Repair Options | X: Scrap Item | ESC: Close"
        ]
        inst_y = 90
        for inst in instructions:
            inst_text = inst_font.render(inst, True, (200, 200, 200))
            screen.blit(inst_text, (self.config.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, inst_y))
            inst_y += 25
        
        # Handle confirmation dialog
        if self.show_confirmation:
            self._draw_confirmation_dialog(screen, font)
            return
        
        # Handle equipment selection list
        if self.show_equipment_list:
            self._draw_equipment_list(screen, font)
            return
        
        # Main repair panel
        panel_x = 50
        panel_y = 150
        panel_width = self.config.SCREEN_WIDTH - 100
        panel_height = self.config.SCREEN_HEIGHT - 200
        
        pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (100, 100, 100), (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Get repairable items
        repairable = self.get_repairable_items()
        
        if not repairable:
            no_items_text = font.render("No items need repair!", True, (200, 200, 200))
            screen.blit(no_items_text, (panel_x + panel_width // 2 - no_items_text.get_width() // 2, panel_y + 50))
            return
        
        # Draw item list (left side)
        list_x = panel_x + 10
        list_y = panel_y + 10
        list_width = panel_width // 2 - 20
        
        item_font = pygame.font.SysFont(None, 28)
        
        visible_items = repairable[self.scroll_offset:self.scroll_offset + self.max_visible_items]
        
        for i, (slot, item) in enumerate(visible_items):
            idx = i + self.scroll_offset
            item_y = list_y + i * 45
            
            # Highlight selected
            if idx == self.selected_item_idx:
                pygame.draw.rect(screen, (80, 80, 120), (list_x, item_y, list_width, 40))
                pygame.draw.rect(screen, (150, 150, 200), (list_x, item_y, list_width, 40), 2)
            
            # Item name
            item_name = f"{item.name} ({slot})"
            item_text = item_font.render(item_name, True, (255, 255, 255))
            screen.blit(item_text, (list_x + 5, item_y + 5))
            
            # Durability bar
            dur_percent = item.durability / item.max_durability
            bar_width = list_width - 10
            bar_height = 8
            bar_y = item_y + 28
            
            # Background
            pygame.draw.rect(screen, (60, 60, 60), (list_x + 5, bar_y, bar_width, bar_height))
            
            # Durability fill
            if dur_percent > 0.7:
                color = (0, 255, 0)
            elif dur_percent > 0.3:
                color = (255, 255, 0)
            else:
                color = (255, 0, 0)
            
            pygame.draw.rect(screen, color, (list_x + 5, bar_y, int(bar_width * dur_percent), bar_height))
            pygame.draw.rect(screen, (100, 100, 100), (list_x + 5, bar_y, bar_width, bar_height), 1)
            
            # Durability text
            dur_text = f"{int(item.durability)}/{int(item.max_durability)}"
            dur_render = pygame.font.SysFont(None, 20).render(dur_text, True, (200, 200, 200))
            screen.blit(dur_render, (list_x + bar_width - dur_render.get_width() + 5, bar_y - 1))
        
        # Draw selected item details (right side)
        if repairable:
            selected_item = repairable[self.selected_item_idx][1]
            self._draw_item_details(screen, font, selected_item, panel_x + panel_width // 2 + 10, panel_y + 10)
        
        # Draw message
        if self.message and self.message_timer > 0:
            msg_font = pygame.font.SysFont(None, 32)
            msg_text = msg_font.render(self.message, True, (255, 255, 0))
            msg_bg = pygame.Surface((msg_text.get_width() + 20, msg_text.get_height() + 10), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 180))
            msg_x = self.config.SCREEN_WIDTH // 2 - msg_text.get_width() // 2 - 10
            msg_y = self.config.SCREEN_HEIGHT - 100
            screen.blit(msg_bg, (msg_x, msg_y))
            screen.blit(msg_text, (msg_x + 10, msg_y + 5))
    
    def _draw_item_details(self, screen, font, item, x, y):
        """Draw detailed information about selected item"""
        detail_font = pygame.font.SysFont(None, 28)
        small_font = pygame.font.SysFont(None, 24)
        
        # Item name
        name_text = detail_font.render(f"Selected: {item.name}", True, (255, 215, 0))
        screen.blit(name_text, (x, y))
        y += 35
        
        # Durability
        dur_percent = (item.durability / item.max_durability) * 100
        dur_text = small_font.render(f"Durability: {int(item.durability)}/{int(item.max_durability)} ({dur_percent:.1f}%)", True, (200, 200, 200))
        screen.blit(dur_text, (x, y))
        y += 30
        
        # Material requirements
        y += 10
        req_title = detail_font.render("Material Requirements:", True, (100, 255, 100))
        screen.blit(req_title, (x, y))
        y += 30
        
        requirements = self.get_material_requirements(item)
        can_afford, error = self.can_afford_material_repair(item)
        
        for material, amount in requirements.items():
            player_amount = self.player.inventory.get(material, 0)
            has_enough = player_amount >= amount
            color = (0, 255, 0) if has_enough else (255, 100, 100)
            
            req_text = small_font.render(f"• {material}: {amount} (have: {player_amount})", True, color)
            screen.blit(req_text, (x + 10, y))
            y += 25
        
        if not can_afford:
            error_text = small_font.render(error, True, (255, 0, 0))
            screen.blit(error_text, (x, y))
            y += 30
        
        # Equipment repair info
        y += 20
        equip_title = detail_font.render("Equipment Repair:", True, (100, 200, 255))
        screen.blit(equip_title, (x, y))
        y += 30
        
        compatible = self.get_compatible_equipment(item)
        if compatible:
            equip_text = small_font.render(f"{len(compatible)} compatible items in inventory", True, (200, 200, 200))
            screen.blit(equip_text, (x + 10, y))
            y += 25
            hint_text = small_font.render("Right-click to view list", True, (150, 150, 150))
            screen.blit(hint_text, (x + 10, y))
        else:
            no_equip_text = small_font.render("No compatible equipment", True, (150, 150, 150))
            screen.blit(no_equip_text, (x + 10, y))
    
    def _draw_equipment_list(self, screen, font):
        """Draw list of compatible equipment for repair"""
        repairable = self.get_repairable_items()
        if not repairable:
            return
        
        target_item = repairable[self.selected_item_idx][1]
        compatible = self.get_compatible_equipment(target_item)
        
        # Panel
        panel_width = 600
        panel_height = 500
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(screen, (30, 30, 30), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (150, 150, 200), (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title
        title_font = pygame.font.SysFont(None, 36)
        title_text = title_font.render(f"Select Item to Repair {target_item.name}", True, (255, 215, 0))
        screen.blit(title_text, (panel_x + panel_width // 2 - title_text.get_width() // 2, panel_y + 10))
        
        # Item list
        list_y = panel_y + 50
        item_font = pygame.font.SysFont(None, 26)
        small_font = pygame.font.SysFont(None, 22)
        
        if not compatible:
            no_items = font.render("No compatible items in inventory", True, (200, 200, 200))
            screen.blit(no_items, (panel_x + panel_width // 2 - no_items.get_width() // 2, list_y + 100))
            return
        
        for i, item in enumerate(compatible):
            item_y = list_y + i * 50
            
            if item_y > panel_y + panel_height - 60:
                break  # Don't draw off panel
            
            # Highlight selected
            if i == self.selected_repair_item_idx:
                pygame.draw.rect(screen, (70, 70, 100), (panel_x + 10, item_y, panel_width - 20, 45))
                pygame.draw.rect(screen, (150, 150, 200), (panel_x + 10, item_y, panel_width - 20, 45), 2)
            
            # Item name and durability
            dur_percent = (item.durability / item.max_durability) * 100
            item_name = f"{item.name} - {dur_percent:.0f}% durability"
            item_text = item_font.render(item_name, True, (255, 255, 255))
            screen.blit(item_text, (panel_x + 20, item_y + 5))
            
            # Repair amount
            repair_percent = self.calculate_equipment_repair_amount(item, target_item)
            repair_text = item_font.render(f"Will repair: +{repair_percent}%", True, (100, 255, 100))
            screen.blit(repair_text, (panel_x + 20, item_y + 25))
            
            # Quality warning
            target_rarity = getattr(target_item, 'rarity', 'common')
            repair_rarity = getattr(item, 'rarity', 'common')
            rarity_order = ['common', 'uncommon', 'rare', 'epic', 'legendary']
            target_tier = rarity_order.index(target_rarity) if target_rarity in rarity_order else 0
            repair_tier = rarity_order.index(repair_rarity) if repair_rarity in rarity_order else 0
            
            if repair_tier > target_tier:
                warning = small_font.render(f"⚠ Higher quality ({repair_rarity})", True, (255, 200, 0))
                screen.blit(warning, (panel_x + panel_width - warning.get_width() - 20, item_y + 15))
        
        # Instructions
        inst_font = pygame.font.SysFont(None, 22)
        instructions = "Enter: Select | ESC/Left-Click: Back"
        inst_text = inst_font.render(instructions, True, (180, 180, 180))
        screen.blit(inst_text, (panel_x + panel_width // 2 - inst_text.get_width() // 2, panel_y + panel_height - 30))
    
    def _draw_confirmation_dialog(self, screen, font):
        """Draw confirmation dialog"""
        # Panel
        panel_width = 600
        panel_height = 250
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (255, 200, 0), (panel_x, panel_y, panel_width, panel_height), 4)
        
        # Message (multi-line)
        msg_font = pygame.font.SysFont(None, 28)
        lines = self.confirmation_message.split('\n')
        msg_y = panel_y + 30
        
        for line in lines:
            line_text = msg_font.render(line, True, (255, 255, 255))
            screen.blit(line_text, (panel_x + panel_width // 2 - line_text.get_width() // 2, msg_y))
            msg_y += 35
        
        # Buttons
        btn_font = pygame.font.SysFont(None, 32, bold=True)
        yes_text = btn_font.render("[Y] YES", True, (100, 255, 100))
        no_text = btn_font.render("[N] NO", True, (255, 100, 100))
        
        btn_y = panel_y + panel_height - 60
        screen.blit(yes_text, (panel_x + panel_width // 3 - yes_text.get_width() // 2, btn_y))
        screen.blit(no_text, (panel_x + 2 * panel_width // 3 - no_text.get_width() // 2, btn_y))

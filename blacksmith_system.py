"""
Blacksmith System
Provides equipment repair, upgrades, and crafting services
"""

import pygame
import logging
from equipment import Equipment
from skills_system import MINING_TOOLS, WOODCUTTING_TOOLS, FISHING_TOOLS
from building_expansions import EquipmentBuybackSystem

logger = logging.getLogger(__name__)


class BlacksmithService:
    """Individual service offered at a blacksmith"""
    def __init__(self, name, description, cost_multiplier=1.0, service_type="repair"):
        self.name = name
        self.description = description
        self.cost_multiplier = cost_multiplier
        self.service_type = service_type  # repair, upgrade, sharpen


class Blacksmith:
    """Represents a blacksmith with various services"""
    def __init__(self, building, town_name):
        self.building = building
        self.town_name = town_name
        self.name = building.name
        
        # Define available services
        self.services = [
            BlacksmithService(
                "Sell Equipment",
                "Sell weapons, armor, and tools for dubloons",
                cost_multiplier=1.0,
                service_type="sell_equipment"
            ),
            BlacksmithService(
                "Craft Tools",
                "Craft gathering tools (pickaxes, axes, fishing gear)",
                cost_multiplier=1.0,
                service_type="craft_tools"
            ),
            BlacksmithService(
                "Quick Repair",
                "Restore 50% durability to one item",
                cost_multiplier=0.3,
                service_type="repair_partial"
            ),
            BlacksmithService(
                "Full Repair",
                "Restore 100% durability to one item",
                cost_multiplier=0.5,
                service_type="repair_full"
            ),
            BlacksmithService(
                "Repair All Equipment",
                "Repair all worn equipment to full",
                cost_multiplier=1.5,
                service_type="repair_all"
            ),
            BlacksmithService(
                "Sharpen Weapon",
                "Increase weapon damage (+10%)",
                cost_multiplier=2.0,
                service_type="sharpen"
            ),
            BlacksmithService(
                "Reinforce Armor",
                "Increase armor defense (+10%)",
                cost_multiplier=2.0,
                service_type="reinforce"
            ),
        ]
        
        # Equipment buyback system
        self.equipment_buyback = EquipmentBuybackSystem()
    
    def calculate_repair_cost(self, item, service):
        """Calculate repair cost based on item value and damage"""
        if not hasattr(item, 'durability') or not hasattr(item, 'max_durability'):
            return 0
        
        # Base cost on item rarity and max durability
        rarity_multiplier = {
            'common': 1.0,
            'uncommon': 1.5,
            'rare': 2.5,
            'epic': 4.0,
            'legendary': 6.0
        }
        
        item_rarity = getattr(item, 'rarity', 'common')
        base_cost = item.max_durability * rarity_multiplier.get(item_rarity, 1.0)
        
        # Calculate damage percentage
        damage_percent = 1.0 - (item.durability / item.max_durability)
        
        # Apply service multiplier
        final_cost = int(base_cost * damage_percent * service.cost_multiplier)
        
        return max(1, final_cost)  # Minimum 1 dubloon
    
    def apply_racial_repair_modifier(self, cost, player):
        """Apply racial modifiers to repair cost (Dwarf: free repairs)"""
        if hasattr(player, 'trait_manager') and player.trait_manager:
            modifier = player.trait_manager.get_repair_cost_modifier()
            modified_cost = int(cost * modifier)
            if modified_cost != cost:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[RACIAL TRAIT] Repair cost: {cost} → {modified_cost} (Dwarf free repairs!)")
            return modified_cost
        return cost
    
    def calculate_upgrade_cost(self, item, service):
        """Calculate upgrade cost based on item value"""
        rarity_multiplier = {
            'common': 50,
            'uncommon': 100,
            'rare': 200,
            'epic': 400,
            'legendary': 800
        }
        
        item_rarity = getattr(item, 'rarity', 'common')
        base_cost = rarity_multiplier.get(item_rarity, 50)
        
        return int(base_cost * service.cost_multiplier)
    
    def get_repairable_items(self, player):
        """Get list of items that need repair"""
        repairable = []
        
        # Check equipped items
        for slot, item in player.equipment.items():
            if item and hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                if item.durability < item.max_durability:
                    repairable.append((slot, item, True))  # True = equipped
        
        return repairable
    
    def get_upgradeable_weapons(self, player):
        """Get list of weapons that can be upgraded"""
        weapons = []
        
        # Check equipped weapon
        if player.equipment.get('weapon') and hasattr(player.equipment['weapon'], 'damage'):
            weapons.append(('weapon', player.equipment['weapon'], True))
        
        # Check inventory for weapons
        for item in player.inventory.get('items', []):
            if hasattr(item, 'type') and item.type == 'weapon' and hasattr(item, 'damage'):
                weapons.append(('inventory', item, False))
        
        return weapons
    
    def get_upgradeable_armor(self, player):
        """Get list of armor that can be upgraded"""
        armor = []
        
        # Check equipped armor
        for slot in ['helmet', 'chest', 'legs', 'boots', 'gloves']:
            item = player.equipment.get(slot)
            if item and hasattr(item, 'defense'):
                armor.append((slot, item, True))
        
        # Check inventory for armor
        for item in player.inventory.get('items', []):
            if hasattr(item, 'type') and item.type in ['helmet', 'chest', 'legs', 'boots', 'gloves'] and hasattr(item, 'defense'):
                armor.append(('inventory', item, False))
        
        return armor
    
    def get_craftable_tools(self, player):
        """Get list of tools that can be crafted based on player's level and materials"""
        craftable = []
        
        # Check mining tools
        for tool_name, tool_data in MINING_TOOLS.items():
            can_craft, reason = self._check_craft_requirements(player, tool_name, tool_data, 'Mining')
            craftable.append({
                'name': tool_name,
                'type': 'mining',
                'data': tool_data,
                'can_craft': can_craft,
                'reason': reason
            })
        
        # Check woodcutting tools
        for tool_name, tool_data in WOODCUTTING_TOOLS.items():
            can_craft, reason = self._check_craft_requirements(player, tool_name, tool_data, 'Woodcutting')
            craftable.append({
                'name': tool_name,
                'type': 'woodcutting',
                'data': tool_data,
                'can_craft': can_craft,
                'reason': reason
            })
        
        # Check fishing tools (no craft level, just need materials)
        for tool_name, tool_data in FISHING_TOOLS.items():
            # Fishing tools don't have craft requirements in the current system
            # For now, mark them as not craftable through blacksmith
            craftable.append({
                'name': tool_name,
                'type': 'fishing',
                'data': tool_data,
                'can_craft': False,
                'reason': 'Purchase from fishing shop'
            })
        
        return craftable
    
    def _check_craft_requirements(self, player, tool_name, tool_data, skill_name):
        """Check if player meets requirements to craft a tool"""
        # Check if player already has the tool
        if tool_name in player.inventory:
            return False, "Already owned"
        
        # Check mining level requirement
        craft_level = tool_data.get('craft_level', 1)
        player_level = player.skills_manager.get_level('Mining')
        if player_level < craft_level:
            return False, f"Need Mining {craft_level}"
        
        # Check materials
        materials = tool_data.get('materials', {})
        for material, amount in materials.items():
            player_amount = player.inventory.get(material, 0)
            if player_amount < amount:
                return False, f"Need {amount} {material}"
        
        return True, "Can craft!"
    
    def craft_tool(self, player, tool_name, tool_data):
        """Craft a tool, consuming materials from player inventory"""
        # Double-check requirements
        materials = tool_data.get('materials', {})
        for material, amount in materials.items():
            player_amount = player.inventory.get(material, 0)
            if player_amount < amount:
                return False, f"Not enough {material}"
        
        craft_level = tool_data.get('craft_level', 1)
        player_level = player.skills_manager.get_level('Mining')
        if player_level < craft_level:
            return False, f"Need Mining level {craft_level}"
        
        # Consume materials
        for material, amount in materials.items():
            player.inventory[material] -= amount
            if player.inventory[material] <= 0:
                del player.inventory[material]
        
        # Add tool to inventory
        player.inventory[tool_name] = 1
        
        # Give small Mining XP for crafting
        xp_reward = craft_level * 5
        levels_gained = player.skills_manager.add_xp('Mining', xp_reward)
        
        logger.info(f"[BLACKSMITH] Crafted {tool_name} for player")
        return True, f"Crafted {tool_name}! (+{xp_reward} Mining XP)"


class BlacksmithManager:
    """Manages all blacksmiths in the game world"""
    def __init__(self):
        self.blacksmiths = []
    
    def register_blacksmith(self, building, town_name):
        """Register a building as a blacksmith"""
        blacksmith = Blacksmith(building, town_name)
        self.blacksmiths.append(blacksmith)
        logger.info(f"[BLACKSMITH] Registered: {blacksmith.name}")
        return blacksmith
    
    def get_nearby_blacksmith(self, player_x, player_y, max_distance=80):
        """Find the nearest blacksmith within interaction range"""
        nearest = None
        nearest_distance = max_distance
        
        for blacksmith in self.blacksmiths:
            door_x = blacksmith.building.x + blacksmith.building.width // 2
            door_y = blacksmith.building.y + blacksmith.building.height
            
            dx = player_x - door_x
            dy = player_y - door_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest = blacksmith
        
        return nearest


class BlacksmithUI:
    """UI for blacksmith interactions"""
    def __init__(self, config):
        self.config = config
        self.active = False
        self.current_blacksmith = None
        self.selected_service = 0
        self.selected_item = 0
        self.view_mode = "services"  # services, items
        self.service_selected = None
        self.message = ""
        self.message_timer = 0
    
    def open(self, blacksmith):
        """Open the blacksmith menu"""
        self.active = True
        self.current_blacksmith = blacksmith
        self.selected_service = 0
        self.selected_item = 0
        self.view_mode = "services"
        self.service_selected = None
        self.message = ""
        self.message_timer = 0
        logger.info(f"[BLACKSMITH UI] Opened {blacksmith.name}")
    
    def close(self):
        """Close the blacksmith menu"""
        self.active = False
        self.current_blacksmith = None
        self.view_mode = "services"
        self.service_selected = None
        logger.info("[BLACKSMITH UI] Closed")
    
    def handle_input(self, event, player):
        """Handle keyboard input for blacksmith menu"""
        if not self.active or not self.current_blacksmith:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                if self.view_mode == "items":
                    # Go back to service selection
                    self.view_mode = "services"
                    self.service_selected = None
                else:
                    self.close()
            
            elif event.key == pygame.K_UP:
                if self.view_mode == "services":
                    self.selected_service = (self.selected_service - 1) % len(self.current_blacksmith.services)
                else:
                    items = self._get_items_for_service(player)
                    if items:
                        self.selected_item = (self.selected_item - 1) % len(items)
            
            elif event.key == pygame.K_DOWN:
                if self.view_mode == "services":
                    self.selected_service = (self.selected_service + 1) % len(self.current_blacksmith.services)
                else:
                    items = self._get_items_for_service(player)
                    if items:
                        self.selected_item = (self.selected_item + 1) % len(items)
            
            elif event.key == pygame.K_RETURN:
                if self.view_mode == "services":
                    # Select service, move to item selection
                    service = self.current_blacksmith.services[self.selected_service]
                    self.service_selected = service
                    
                    # Check if service needs item selection
                    if service.service_type in ["repair_partial", "repair_full", "sharpen", "reinforce", "sell_equipment"]:
                        self.view_mode = "items"
                        self.selected_item = 0
                    elif service.service_type == "craft_tools":
                        # Open crafting menu
                        self.view_mode = "craft_tools"
                        self.selected_item = 0
                    elif service.service_type == "repair_all":
                        # Repair all directly
                        self._repair_all_equipment(player)
                else:
                    # Execute service on selected item
                    items = self._get_items_for_service(player)
                    if items and self.selected_item < len(items):
                        if self.view_mode == "craft_tools":
                            self._craft_selected_tool(player, items[self.selected_item])
                        else:
                            self._execute_service(player, items[self.selected_item])
    
    def _get_items_for_service(self, player):
        """Get items available for selected service"""
        if not self.service_selected:
            return []
        
        if self.service_selected.service_type in ["repair_partial", "repair_full"]:
            return self.current_blacksmith.get_repairable_items(player)
        elif self.service_selected.service_type == "sharpen":
            return self.current_blacksmith.get_upgradeable_weapons(player)
        elif self.service_selected.service_type == "reinforce":
            return self.current_blacksmith.get_upgradeable_armor(player)
        elif self.service_selected.service_type == "craft_tools":
            return self.current_blacksmith.get_craftable_tools(player)
        elif self.service_selected.service_type == "sell_equipment":
            return self.current_blacksmith.equipment_buyback.get_equipment_list(player)
        
        return []
    
    def _repair_all_equipment(self, player):
        """Repair all equipped items"""
        repairable = self.current_blacksmith.get_repairable_items(player)
        
        if not repairable:
            self.message = "No damaged equipment to repair!"
            self.message_timer = 120
            return
        
        # Calculate total cost
        total_cost = 0
        for slot, item, equipped in repairable:
            service = self.current_blacksmith.services[2]  # Repair all service
            cost = self.current_blacksmith.calculate_repair_cost(item, service)
            cost = self.current_blacksmith.apply_racial_repair_modifier(cost, player)  # Dwarf free repairs
            total_cost += cost
        
        if player.dubloons < total_cost:
            self.message = f"Not enough dubloons! Need {total_cost}db"
            self.message_timer = 120
            return
        
        # Repair all items
        player.dubloons -= total_cost
        repaired_count = 0
        for slot, item, equipped in repairable:
            item.durability = item.max_durability
            repaired_count += 1
        
        self.message = f"Repaired {repaired_count} items for {total_cost}g!"
        self.message_timer = 180
        logger.info(f"[BLACKSMITH] Repaired all equipment for {total_cost}g")
    
    def _execute_service(self, player, item_data):
        """Execute service on selected item"""
        service = self.service_selected
        
        # Handle sell equipment separately
        if service.service_type == "sell_equipment":
            slot_name, item, is_equipped, item_type = item_data
            price = self.current_blacksmith.equipment_buyback.calculate_sell_price(item, item_type)
            success, message = self.current_blacksmith.equipment_buyback.sell_equipment(
                player, slot_name, item, is_equipped, price
            )
            self.message = message
            self.message_timer = 180
            # Stay in sell view to allow selling more items
            return
        
        slot, item, equipped = item_data
        
        # Calculate cost
        if service.service_type in ["repair_partial", "repair_full"]:
            cost = self.current_blacksmith.calculate_repair_cost(item, service)
            cost = self.current_blacksmith.apply_racial_repair_modifier(cost, player)  # Dwarf free repairs
        else:
            cost = self.current_blacksmith.calculate_upgrade_cost(item, service)
        
        # Check if player can afford
        if player.dubloons < cost:
            self.message = f"Not enough dubloons! Need {cost}db"
            self.message_timer = 120
            return
        
        # Apply service
        player.dubloons -= cost
        
        if service.service_type == "repair_partial":
            restored = int(item.max_durability * 0.5)
            item.durability = min(item.max_durability, item.durability + restored)
            self.message = f"Partially repaired {item.name} for {cost}g"
        
        elif service.service_type == "repair_full":
            item.durability = item.max_durability
            self.message = f"Fully repaired {item.name} for {cost}g"
        
        elif service.service_type == "sharpen":
            if hasattr(item, 'damage'):
                bonus = int(item.damage * 0.1)
                item.damage += bonus
                self.message = f"Sharpened {item.name}! +{bonus} damage ({cost}g)"
        
        elif service.service_type == "reinforce":
            if hasattr(item, 'defense'):
                bonus = int(item.defense * 0.1)
                item.defense += bonus
                self.message = f"Reinforced {item.name}! +{bonus} defense ({cost}g)"
        
        self.message_timer = 180
        logger.info(f"[BLACKSMITH] {service.name} on {item.name} for {cost}g")
        
        # Go back to service selection
        self.view_mode = "services"
        self.service_selected = None
    
    def _craft_selected_tool(self, player, tool_info):
        """Craft the selected tool"""
        tool_name = tool_info['name']
        tool_data = tool_info['data']
        can_craft = tool_info['can_craft']
        
        if not can_craft:
            self.message = f"Cannot craft: {tool_info['reason']}"
            self.message_timer = 120
            return
        
        # Attempt to craft
        success, message = self.current_blacksmith.craft_tool(player, tool_name, tool_data)
        
        if success:
            self.message = message
            self.message_timer = 180
            # Stay in crafting view to allow crafting more tools
        else:
            self.message = f"Crafting failed: {message}"
            self.message_timer = 120
    
    def draw(self, screen, player):
        """Draw the blacksmith menu"""
        if not self.active or not self.current_blacksmith:
            return
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        # Semi-transparent background
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Menu dimensions
        menu_width = 700
        menu_height = 550
        menu_x = (self.config.SCREEN_WIDTH - menu_width) // 2
        menu_y = (self.config.SCREEN_HEIGHT - menu_height) // 2
        
        # Menu background
        menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_bg.fill((30, 25, 20, 240))
        pygame.draw.rect(menu_bg, (180, 140, 80), (0, 0, menu_width, menu_height), 4)
        screen.blit(menu_bg, (menu_x, menu_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render(self.current_blacksmith.name, True, (255, 180, 80))
        screen.blit(title, (menu_x + menu_width // 2 - title.get_width() // 2, menu_y + 20))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 24)
        if self.view_mode == "services":
            subtitle_text = "Select a service"
        else:
            subtitle_text = f"Select item for: {self.service_selected.name}"
        subtitle = subtitle_font.render(subtitle_text, True, (200, 180, 150))
        screen.blit(subtitle, (menu_x + menu_width // 2 - subtitle.get_width() // 2, menu_y + 70))
        
        # Player dubloons
        gold_font = pygame.font.SysFont(None, 28)
        gold_text = gold_font.render(f"Your Dubloons: {player.dubloons}db", True, (255, 215, 0))
        screen.blit(gold_text, (menu_x + 20, menu_y + 110))
        
        # Content area
        content_y = menu_y + 150
        
        if self.view_mode == "services":
            self._draw_services(screen, menu_x, content_y, menu_width, player)
        elif self.view_mode == "craft_tools":
            self._draw_craftable_tools(screen, menu_x, content_y, menu_width, player)
        else:
            self._draw_items(screen, menu_x, content_y, menu_width, player)
        
        # Instructions
        instr_y = menu_y + menu_height - 60
        instr_font = pygame.font.SysFont(None, 24)
        if self.view_mode == "services":
            instructions = ["↑↓: Select", "ENTER: Choose", "ESC/B: Close"]
        else:
            instructions = ["↑↓: Select item", "ENTER: Confirm", "ESC: Back"]
        
        instr_x = menu_x + 20
        for instruction in instructions:
            instr = instr_font.render(instruction, True, (200, 180, 150))
            screen.blit(instr, (instr_x, instr_y))
            instr_x += 220
        
        # Message
        if self.message:
            msg_font = pygame.font.SysFont(None, 32)
            msg_color = (100, 255, 100) if "!" in self.message and "Not enough" not in self.message else (255, 100, 100)
            msg_surf = msg_font.render(self.message, True, msg_color)
            
            msg_x = (self.config.SCREEN_WIDTH - msg_surf.get_width()) // 2
            msg_y = menu_y + menu_height + 20
            
            msg_bg = pygame.Surface((msg_surf.get_width() + 40, msg_surf.get_height() + 20), pygame.SRCALPHA)
            msg_bg.fill((20, 20, 20, 220))
            pygame.draw.rect(msg_bg, msg_color, (0, 0, msg_bg.get_width(), msg_bg.get_height()), 2)
            
            screen.blit(msg_bg, (msg_x - 20, msg_y - 10))
            screen.blit(msg_surf, (msg_x, msg_y))
    
    def _draw_services(self, screen, menu_x, start_y, menu_width, player):
        """Draw service list"""
        service_font = pygame.font.SysFont(None, 32)
        desc_font = pygame.font.SysFont(None, 22)
        
        for i, service in enumerate(self.current_blacksmith.services):
            is_selected = (i == self.selected_service)
            
            y_pos = start_y + i * 75
            
            # Service background
            bg_color = (80, 60, 40, 200) if is_selected else (50, 40, 30, 150)
            bg = pygame.Surface((menu_width - 40, 70), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                pygame.draw.rect(bg, (255, 180, 80), (0, 0, menu_width - 40, 70), 3)
            
            screen.blit(bg, (menu_x + 20, y_pos))
            
            # Service name
            name = service_font.render(service.name, True, (255, 255, 255))
            screen.blit(name, (menu_x + 35, y_pos + 10))
            
            # Service description
            desc = desc_font.render(service.description, True, (200, 180, 150))
            screen.blit(desc, (menu_x + 35, y_pos + 42))
    
    def _draw_items(self, screen, menu_x, start_y, menu_width, player):
        """Draw item list for selected service"""
        items = self._get_items_for_service(player)
        
        if not items:
            no_items_font = pygame.font.SysFont(None, 36)
            no_items = no_items_font.render("No items available for this service", True, (200, 150, 100))
            screen.blit(no_items, (menu_x + menu_width // 2 - no_items.get_width() // 2, start_y + 100))
            return
        
        item_font = pygame.font.SysFont(None, 28)
        detail_font = pygame.font.SysFont(None, 22)
        
        # Check if this is selling equipment (different data structure)
        is_selling = self.service_selected.service_type == "sell_equipment"
        
        for i, item_data in enumerate(items):
            if i >= 4:  # Limit display
                break
            
            # Unpack data based on service type
            if is_selling:
                slot, item, equipped, item_type = item_data
            else:
                slot, item, equipped = item_data
            
            is_selected = (i == self.selected_item)
            y_pos = start_y + i * 85
            
            # Item background
            bg_color = (80, 60, 40, 200) if is_selected else (50, 40, 30, 150)
            bg = pygame.Surface((menu_width - 40, 80), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                pygame.draw.rect(bg, (255, 180, 80), (0, 0, menu_width - 40, 80), 3)
            
            screen.blit(bg, (menu_x + 20, y_pos))
            
            # Item name
            if isinstance(item, dict):
                item_name = item.get('name', slot)
            else:
                item_name = item.name if hasattr(item, 'name') else str(item)
            equipped_tag = " [EQUIPPED]" if equipped else ""
            name = item_font.render(f"{item_name}{equipped_tag}", True, (255, 255, 255))
            screen.blit(name, (menu_x + 35, y_pos + 10))
            
            # Item details
            details = []
            if hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                durability_pct = int((item.durability / item.max_durability) * 100)
                details.append(f"Durability: {item.durability}/{item.max_durability} ({durability_pct}%)")
            if hasattr(item, 'damage'):
                details.append(f"Damage: {item.damage}")
            if hasattr(item, 'defense'):
                details.append(f"Defense: {item.defense}")
            
            detail_text = " | ".join(details)
            detail = detail_font.render(detail_text, True, (200, 180, 150))
            screen.blit(detail, (menu_x + 35, y_pos + 40))
            
            # Cost/Price
            if is_selling:
                # Show sell price in green
                price = self.current_blacksmith.equipment_buyback.calculate_sell_price(item, item_type)
                price_color = (100, 255, 100)  # Green for earning money
                price_text = item_font.render(f"+{price}g", True, price_color)
            else:
                # Show repair/upgrade cost
                if self.service_selected.service_type in ["repair_partial", "repair_full"]:
                    cost = self.current_blacksmith.calculate_repair_cost(item, self.service_selected)
                    cost = self.current_blacksmith.apply_racial_repair_modifier(cost, player)  # Dwarf free repairs
                else:
                    cost = self.current_blacksmith.calculate_upgrade_cost(item, self.service_selected)
                
                cost_color = (255, 215, 0) if player.dubloons >= cost else (255, 100, 100)
                price_text = item_font.render(f"{cost}g", True, cost_color)
            
            screen.blit(price_text, (menu_x + menu_width - 100, y_pos + 25))
    
    def _draw_craftable_tools(self, screen, menu_x, start_y, menu_width, player):
        """Draw craftable tools list"""
        tools = self._get_items_for_service(player)
        
        if not tools:
            return
        
        tool_font = pygame.font.SysFont(None, 28)
        detail_font = pygame.font.SysFont(None, 20)
        small_font = pygame.font.SysFont(None, 18)
        
        # Calculate scroll offset to show 5 tools at a time
        visible_count = 5
        scroll_offset = max(0, self.selected_item - visible_count + 1)
        
        for i in range(scroll_offset, min(scroll_offset + visible_count, len(tools))):
            tool_info = tools[i]
            is_selected = (i == self.selected_item)
            
            y_pos = start_y + (i - scroll_offset) * 75
            
            # Tool background
            if tool_info['can_craft']:
                bg_color = (60, 80, 40, 200) if is_selected else (40, 50, 30, 150)
            else:
                bg_color = (80, 60, 60, 200) if is_selected else (50, 40, 40, 150)
            
            bg = pygame.Surface((menu_width - 40, 70), pygame.SRCALPHA)
            bg.fill(bg_color)
            
            if is_selected:
                border_color = (100, 255, 100) if tool_info['can_craft'] else (255, 100, 100)
                pygame.draw.rect(bg, border_color, (0, 0, menu_width - 40, 70), 3)
            
            screen.blit(bg, (menu_x + 20, y_pos))
            
            # Tool name with type badge
            tool_display_name = tool_info['name'].replace('_', ' ').title()
            type_badge = f"[{tool_info['type'].upper()}]"
            
            name = tool_font.render(tool_display_name, True, (255, 255, 255))
            screen.blit(name, (menu_x + 35, y_pos + 8))
            
            badge = small_font.render(type_badge, True, (150, 150, 150))
            screen.blit(badge, (menu_x + 35 + name.get_width() + 10, y_pos + 12))
            
            # Requirements
            tool_data = tool_info['data']
            materials = tool_data.get('materials', {})
            craft_level = tool_data.get('craft_level', 0)
            
            # Materials list
            materials_text = ", ".join([f"{amt} {mat}" for mat, amt in materials.items()])
            if craft_level > 0:
                req_text = f"Req: Mining {craft_level} | Materials: {materials_text}"
            else:
                req_text = f"Materials: {materials_text}"
            
            req = detail_font.render(req_text, True, (200, 180, 150))
            screen.blit(req, (menu_x + 35, y_pos + 35))
            
            # Status
            if tool_info['can_craft']:
                status_text = "READY TO CRAFT"
                status_color = (100, 255, 100)
            else:
                status_text = tool_info['reason']
                status_color = (255, 150, 100)
            
            status = detail_font.render(status_text, True, status_color)
            screen.blit(status, (menu_x + menu_width - status.get_width() - 30, y_pos + 25))

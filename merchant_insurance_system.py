"""
Traveling Merchant Insurance System
Merchants can purchase insurance for 20% reimbursement on lost inventory
Prevents exploitation while providing some protection
"""

import random
from npc_combat_enhancements import NPCLootingSystem


class InsurancePolicy:
    """Insurance policy for a traveling merchant"""
    
    def __init__(self, merchant_id, merchant_name, premium, coverage_percentage=0.20):
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name
        self.premium = premium  # Cost of insurance
        self.coverage_percentage = coverage_percentage  # 20% by default
        self.active = True
        self.purchase_time = 0
        self.claims_made = 0
        self.total_payout = 0
    
    def calculate_payout(self, lost_inventory_value):
        """Calculate insurance payout (20% of lost value)"""
        payout = int(lost_inventory_value * self.coverage_percentage)
        return payout
    
    def file_claim(self, lost_inventory_value):
        """File insurance claim and get payout"""
        if not self.active:
            return 0, "Policy is not active"
        
        payout = self.calculate_payout(lost_inventory_value)
        self.claims_made += 1
        self.total_payout += payout
        
        # Rate increases after claims (not implemented yet but tracked)
        
        return payout, f"Insurance paid out {payout}g (20% of {lost_inventory_value}g loss)"


class InsuranceProvider:
    """Manages insurance policies for traveling merchants"""
    
    def __init__(self):
        self.policies = {}  # {merchant_id: InsurancePolicy}
        self.total_premiums_collected = 0
        self.total_claims_paid = 0
        self.premium_base_cost = 100  # Base cost per policy
        
    def calculate_premium(self, merchant, inventory_value):
        """
        Calculate premium cost based on merchant risk profile
        """
        base_premium = self.premium_base_cost
        
        # Factor in inventory value (higher value = higher premium)
        value_factor = (inventory_value / 1000) * 0.1  # 10% per 1000g value
        
        # Factor in merchant level (higher level = lower premium)
        if hasattr(merchant, 'level'):
            level_discount = merchant.level * 0.01  # 1% discount per level
        else:
            level_discount = 0
        
        # Factor in equipment quality
        equipment_bonus = 0
        if hasattr(merchant, 'weapon') and merchant.weapon:
            equipment_bonus += 0.05  # 5% discount if armed
        if hasattr(merchant, 'armor') and merchant.armor:
            equipment_bonus += 0.05  # 5% discount if armored
        
        # Calculate final premium
        premium = base_premium * (1 + value_factor) * (1 - level_discount - equipment_bonus)
        premium = max(50, int(premium))  # Minimum 50g
        
        return premium
    
    def purchase_insurance(self, merchant, game_time):
        """
        Merchant purchases insurance policy
        """
        merchant_id = id(merchant)
        
        # Check if already insured
        if merchant_id in self.policies and self.policies[merchant_id].active:
            return False, "Already insured"
        
        # Calculate premium
        inventory_value = NPCLootingSystem.calculate_loot_value(
            getattr(merchant, 'inventory', {})
        )
        premium = self.calculate_premium(merchant, inventory_value)
        
        # Check if merchant can afford
        if getattr(merchant, 'dubloons', 0) < premium:
            return False, f"Cannot afford premium ({premium}g)"
        
        # Purchase insurance
        merchant.dubloons -= premium
        policy = InsurancePolicy(merchant_id, merchant.name, premium)
        policy.purchase_time = getattr(game_time, 'total_hours', 0)
        self.policies[merchant_id] = policy
        
        self.total_premiums_collected += premium
        
        print(f"[INSURANCE] {merchant.name} purchased insurance for {premium}g")
        return True, f"Insurance purchased for {premium}g"
    
    def process_death_claim(self, merchant, lost_inventory, game_time):
        """
        Process insurance claim when merchant dies
        Returns payout amount
        """
        merchant_id = id(merchant)
        
        # Check if insured
        if merchant_id not in self.policies:
            return 0, "No active insurance policy"
        
        policy = self.policies[merchant_id]
        if not policy.active:
            return 0, "Policy not active"
        
        # Calculate lost value
        lost_value = NPCLootingSystem.calculate_loot_value(lost_inventory)
        
        # File claim
        payout, message = policy.file_claim(lost_value)
        
        # Pay merchant
        if hasattr(merchant, 'dubloons'):
            merchant.dubloons += payout
        
        self.total_claims_paid += payout
        
        # Deactivate policy (need to rebuy after death)
        policy.active = False
        
        print(f"[INSURANCE] {message}")
        return payout, message
    
    def auto_insure_merchants(self, merchant_list, game_time):
        """
        Automatically purchase insurance for eligible merchants
        Merchants with high value inventory and enough money will buy insurance
        """
        insured_count = 0
        
        for merchant in merchant_list:
            # Skip if already insured
            merchant_id = id(merchant)
            if merchant_id in self.policies and self.policies[merchant_id].active:
                continue
            
            # Check if merchant should buy insurance
            if hasattr(merchant, 'inventory') and hasattr(merchant, 'dubloons'):
                inventory_value = NPCLootingSystem.calculate_loot_value(merchant.inventory)
                
                # Buy insurance if:
                # 1. Inventory value > 500g
                # 2. Has enough money for premium + buffer
                # 3. Random chance (50%)
                if inventory_value > 500 and random.random() < 0.5:
                    premium = self.calculate_premium(merchant, inventory_value)
                    if merchant.dubloons >= premium * 2:  # 2x premium buffer
                        success, msg = self.purchase_insurance(merchant, game_time)
                        if success:
                            insured_count += 1
        
        if insured_count > 0:
            print(f"[INSURANCE] {insured_count} merchants purchased insurance this cycle")
        
        return insured_count
    
    def get_policy_info(self, merchant):
        """Get insurance policy info for merchant"""
        merchant_id = id(merchant)
        if merchant_id not in self.policies:
            return None
        
        policy = self.policies[merchant_id]
        return {
            'active': policy.active,
            'premium': policy.premium,
            'coverage': f"{int(policy.coverage_percentage * 100)}%",
            'claims': policy.claims_made,
            'total_payout': policy.total_payout
        }
    
    def get_statistics(self):
        """Get insurance system statistics"""
        active_policies = sum(1 for p in self.policies.values() if p.active)
        total_policies = len(self.policies)
        
        return {
            'active_policies': active_policies,
            'total_policies': total_policies,
            'premiums_collected': self.total_premiums_collected,
            'claims_paid': self.total_claims_paid,
            'profit': self.total_premiums_collected - self.total_claims_paid
        }


class PlayerInsuranceUI:
    """UI for player to view and purchase insurance"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        
        # UI dimensions
        self.panel_width = 600
        self.panel_height = 400
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # References
        self.insurance_provider = None
        self.player = None
        self.game_time = None
    
    def open(self):
        """Open insurance UI"""
        self.active = True
    
    def close(self):
        """Close insurance UI"""
        self.active = False
    
    def toggle(self):
        """Toggle UI"""
        if self.active:
            self.close()
        else:
            self.open()
    
    def handle_input(self, event):
        """Handle input"""
        if not self.active:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
            elif event.key == pygame.K_b:
                # Buy insurance
                self._purchase_insurance()
    
    def _purchase_insurance(self):
        """Player purchases insurance"""
        if not self.insurance_provider or not self.player:
            return
        
        success, message = self.insurance_provider.purchase_insurance(self.player, self.game_time)
        print(f"[INSURANCE] {message}")
    
    def draw(self, screen, font):
        """Draw insurance UI"""
        if not self.active or not self.insurance_provider:
            return
        
        # Draw panel
        panel = pygame.Surface((self.panel_width, self.panel_height))
        panel.set_alpha(240)
        panel.fill((20, 20, 30))
        pygame.draw.rect(panel, (100, 100, 120), (0, 0, self.panel_width, self.panel_height), 3)
        
        # Title
        title_font = pygame.font.SysFont(None, 32)
        title = title_font.render("🛡️ TRAVEL INSURANCE", True, (255, 215, 0))
        title_rect = title.get_rect(center=(self.panel_width // 2, 30))
        panel.blit(title, title_rect)
        
        # Policy info
        y_offset = 80
        if self.player:
            policy_info = self.insurance_provider.get_policy_info(self.player)
            
            if policy_info and policy_info['active']:
                # Show active policy
                status = font.render("Status: INSURED ✓", True, (0, 255, 0))
                panel.blit(status, (50, y_offset))
                
                y_offset += 30
                coverage = font.render(f"Coverage: {policy_info['coverage']} of lost inventory", True, (200, 200, 200))
                panel.blit(coverage, (50, y_offset))
                
                y_offset += 25
                premium = font.render(f"Premium Paid: {policy_info['premium']}g", True, (200, 200, 200))
                panel.blit(premium, (50, y_offset))
                
            else:
                # No insurance
                status = font.render("Status: NOT INSURED", True, (255, 100, 100))
                panel.blit(status, (50, y_offset))
                
                y_offset += 40
                info1 = font.render("Insurance covers 20% of inventory lost on death", True, (200, 200, 200))
                panel.blit(info1, (50, y_offset))
                
                y_offset += 25
                info2 = font.render("Premium based on inventory value and risk", True, (200, 200, 200))
                panel.blit(info2, (50, y_offset))
                
                # Calculate quote
                inventory_value = NPCLootingSystem.calculate_loot_value(self.player.inventory)
                premium_cost = self.insurance_provider.calculate_premium(self.player, inventory_value)
                
                y_offset += 40
                quote = font.render(f"Current Quote: {premium_cost}g", True, (255, 215, 0))
                panel.blit(quote, (50, y_offset))
        
        # Controls
        controls_y = self.panel_height - 40
        controls = font.render("B: Buy Insurance | ESC: Close", True, (150, 150, 150))
        controls_rect = controls.get_rect(center=(self.panel_width // 2, controls_y))
        panel.blit(controls, controls_rect)
        
        # Blit to screen
        screen.blit(panel, (self.panel_x, self.panel_y))


# Quick import for pygame in UI
import pygame

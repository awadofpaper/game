"""
Bank System
Provides item storage and gold management services
"""

import pygame
import logging

logger = logging.getLogger(__name__)


class BankService:
    """Individual service offered at a bank"""
    def __init__(self, name, description, cost, service_type):
        self.name = name
        self.description = description
        self.cost = cost
        self.service_type = service_type  # deposit_gold, withdraw_gold, store_item, retrieve_item, upgrade_storage


class StorageTier:
    """Storage tier with capacity and rental cost"""
    def __init__(self, name, slots, rental_cost, description):
        self.name = name
        self.slots = slots
        self.rental_cost = rental_cost  # Cost per rental period
        self.description = description


class Bank:
    """Represents a bank with storage and gold services"""
    def __init__(self, building, town_name):
        self.building = building
        self.town_name = town_name
        self.name = building.name
        
        # Storage tiers available
        self.storage_tiers = [
            StorageTier("Basic Vault", 10, 0, "Free storage (10 slots)"),
            StorageTier("Standard Vault", 25, 100, "Expanded storage (25 slots) - 100g"),
            StorageTier("Premium Vault", 50, 300, "Large storage (50 slots) - 300g"),
            StorageTier("Master Vault", 100, 1000, "Massive storage (100 slots) - 1000g"),
        ]
        
        # Define available services
        self.services = [
            BankService(
                "Deposit Dubloons",
                "Store dubloons safely in your account",
                cost=0,
                service_type="deposit_gold"
            ),
            BankService(
                "Withdraw Dubloons",
                "Take dubloons from your account",
                cost=0,
                service_type="withdraw_gold"
            ),
            BankService(
                "Store Item",
                "Place an item in your vault",
                cost=0,
                service_type="store_item"
            ),
            BankService(
                "Retrieve Item",
                "Take an item from your vault",
                cost=0,
                service_type="retrieve_item"
            ),
            BankService(
                "Upgrade Storage",
                "Expand your vault capacity",
                cost=0,
                service_type="upgrade_storage"
            ),
            BankService(
                "Take Loan",
                "Borrow dubloons (100-5000db, 15% interest, 30 days)",
                cost=0,
                service_type="take_loan"
            ),
            BankService(
                "Repay Loan",
                "Pay back your outstanding loan",
                cost=0,
                service_type="repay_loan"
            ),
            BankService(
                "Buy Property",
                "Purchase available plots in this town",
                cost=0,
                service_type="buy_property"
            ),
            BankService(
                "Sell Property",
                "Sell your owned properties",
                cost=0,
                service_type="sell_property"
            ),
            BankService(
                "Safety Deposit Box",
                "Secure item storage (rent a box)",
                cost=0,
                service_type="safety_deposit"
            ),
            BankService(
                "Purchase Insurance",
                "Buy property insurance (300g, 2 years)",
                cost=300,
                service_type="purchase_insurance"
            ),
            BankService(
                "View Policies",
                "View your active insurance policies",
                cost=0,
                service_type="view_policies"
            ),
        ]
    
    def get_storage_tier(self, tier_level):
        """Get storage tier by level"""
        if 0 <= tier_level < len(self.storage_tiers):
            return self.storage_tiers[tier_level]
        return self.storage_tiers[0]


class BankManager:
    """Manages all banks in the game world"""
    def __init__(self):
        self.banks = []
        # Global player bank data (shared across all banks)
        self.player_storage = []  # List of stored items
        self.player_bank_gold = 0  # Dubloons stored in bank
        self.player_storage_tier = 0  # Current storage tier level (0 = basic)
        
        # Bank revenue tracking (for vault loot)
        self.bank_revenue = 0  # Total revenue from interest, fees, etc.
        
        # Loan system
        self.active_loans = []  # List of active loans
        self.loan_interest_rate = 0.15  # 15% interest
        self.loan_duration_days = 30  # 30 day loan term
    
    def register_bank(self, building, town_name):
        """Register a building as a bank"""
        bank = Bank(building, town_name)
        self.banks.append(bank)
        logger.info(f"[BANK] Registered: {bank.name}")
        return bank
    
    def get_nearby_bank(self, player_x, player_y, max_distance=80):
        """Find the nearest bank within interaction range"""
        nearest = None
        nearest_distance = max_distance
        
        for bank in self.banks:
            door_x = bank.building.x + bank.building.width // 2
            door_y = bank.building.y + bank.building.height
            
            dx = player_x - door_x
            dy = player_y - door_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest = bank
        
        return nearest
    
    def get_max_storage_slots(self):
        """Get maximum storage slots based on current tier"""
        tier = self.player_storage_tier
        # Default storage tiers (in case no banks are registered yet)
        default_tier_slots = [10, 25, 50, 100]
        
        # If banks exist, use their storage tiers
        if self.banks and len(self.banks) > 0:
            if tier < len(self.banks[0].storage_tiers):
                return self.banks[0].storage_tiers[tier].slots
        
        # Otherwise use default slots
        if tier < len(default_tier_slots):
            return default_tier_slots[tier]
        return 10
    
    def can_store_item(self):
        """Check if player can store more items"""
        return len(self.player_storage) < self.get_max_storage_slots()
    
    def store_item(self, item):
        """Store an item in the bank"""
        if self.can_store_item():
            self.player_storage.append(item)
            logger.info(f"[BANK] Stored item: {item}")
            return True
        return False
    
    def retrieve_item(self, index):
        """Retrieve an item from storage"""
        if 0 <= index < len(self.player_storage):
            item = self.player_storage.pop(index)
            logger.info(f"[BANK] Retrieved item: {item}")
            return item
        return None
    
    def deposit_gold(self, amount):
        """Deposit dubloons into bank account"""
        if amount > 0:
            self.player_bank_gold += amount
            # Bank revenue: 1% of deposits goes to bank
            deposit_fee = int(amount * 0.01)
            self.bank_revenue += deposit_fee
            logger.info(f"[BANK] Deposited {amount}g (Total: {self.player_bank_gold}g, Bank fee: {deposit_fee}g)")
            return True
        return False
    
    def withdraw_gold(self, amount):
        """Withdraw dubloons from bank account"""
        if amount > 0 and amount <= self.player_bank_gold:
            self.player_bank_gold -= amount
            logger.info(f"[BANK] Withdrew {amount}g (Remaining: {self.player_bank_gold}g)")
            return True
        return False
    
    def upgrade_storage_tier(self, player):
        """Upgrade to next storage tier"""
        current_tier = self.player_storage_tier
        
        # Check if banks exist
        if not self.banks or len(self.banks) == 0:
            return False, "No banks available!"
        
        if current_tier >= len(self.banks[0].storage_tiers) - 1:
            return False, "Already at maximum storage tier!"
        
        next_tier = self.banks[0].storage_tiers[current_tier + 1]
        
        if player.dubloons < next_tier.rental_cost:
            return False, f"Not enough dubloons! Need {next_tier.rental_cost}db"
        
        player.dubloons -= next_tier.rental_cost
        # Bank revenue from storage upgrades
        self.bank_revenue += next_tier.rental_cost
        self.player_storage_tier += 1
        logger.info(f"[BANK] Upgraded storage to {next_tier.name}")
        return True, f"Upgraded to {next_tier.name}!"
    
    def take_loan(self, player, amount, game_time):
        """Take out a loan from the bank"""
        if amount < 100:
            return False, "Minimum loan amount is 100g"
        if amount > 5000:
            return False, "Maximum loan amount is 5000g"
        
        # Check if player already has an active loan
        for loan in self.active_loans:
            if loan['player_id'] == id(player) and not loan['repaid']:
                return False, "You already have an active loan!"
        
        # Give player the loan amount
        player.dubloons += amount
        
        # Calculate repayment amount with interest
        repayment_amount = int(amount * (1 + self.loan_interest_rate))
        
        # Create loan record
        loan = {
            'player_id': id(player),
            'amount': amount,
            'repayment_amount': repayment_amount,
            'due_day': game_time.day_count + self.loan_duration_days,
            'repaid': False,
            'overdue_start_day': None,  # Set when loan becomes overdue
            'interest_doubled': False,  # Track if interest already doubled
            'bounty_added': False  # Track if bounty already added
        }
        self.active_loans.append(loan)
        
        logger.info(f"[BANK] Loan issued: {amount}g, repay {repayment_amount}g by day {loan['due_day']}")
        return True, f"Loan approved! {amount}g received. Repay {repayment_amount}g within {self.loan_duration_days} days."
    
    def repay_loan(self, player):
        """Repay active loan"""
        for loan in self.active_loans:
            if loan['player_id'] == id(player) and not loan['repaid']:
                if player.dubloons >= loan['repayment_amount']:
                    player.dubloons -= loan['repayment_amount']
                    loan['repaid'] = True
                    # Bank revenue from interest
                    interest_earned = loan['repayment_amount'] - loan['amount']
                    self.bank_revenue += interest_earned
                    logger.info(f"[BANK] Loan repaid: {loan['repayment_amount']}g (Interest: {interest_earned}g)")
                    return True, f"Loan repaid! {loan['repayment_amount']}g paid."
                else:
                    return False, f"Not enough dubloons! Need {loan['repayment_amount']}db to repay loan."
        return False, "No active loan to repay."
    
    def check_overdue_loans(self, player, game_time):
        """Check if player has overdue loans"""
        for loan in self.active_loans:
            if loan['player_id'] == id(player) and not loan['repaid']:
                if game_time.day_count > loan['due_day']:
                    return True, loan
        return False, None
    
    def process_overdue_penalties(self, player, game_time, wanted_system):
        """Process penalties for overdue loans (called daily)"""
        for loan in self.active_loans:
            if loan['player_id'] == id(player) and not loan['repaid']:
                # Check if loan is overdue
                if game_time.day_count > loan['due_day']:
                    # Set overdue start day if not already set
                    if loan['overdue_start_day'] is None:
                        loan['overdue_start_day'] = game_time.day_count
                        logger.warning(f"[BANK] Loan is now OVERDUE! Due day: {loan['due_day']}, Current: {game_time.day_count}")
                    
                    days_overdue = game_time.day_count - loan['overdue_start_day']
                    
                    # After 30 days overdue: double interest rate (15% -> 30%)
                    if days_overdue >= 30 and not loan['interest_doubled']:
                        old_repayment = loan['repayment_amount']
                        # Recalculate with doubled interest (30% instead of 15%)
                        loan['repayment_amount'] = int(loan['amount'] * 1.30)
                        loan['interest_doubled'] = True
                        logger.error(f"[BANK] PENALTY: Interest doubled! Repayment increased from {old_repayment}g to {loan['repayment_amount']}g")
                        return 'interest_doubled', loan['repayment_amount'] - old_repayment
                    
                    # After 60 days total (30 days past interest doubling): add wanted bounty
                    if days_overdue >= 60 and not loan['bounty_added']:
                        bounty_amount = loan['amount']  # Bounty equals original loan amount
                        player.wanted_level = getattr(player, 'wanted_level', 0) + bounty_amount
                        player.is_wanted = True
                        loan['bounty_added'] = True
                        
                        # Add to wanted system with 90 day duration
                        wanted_system.set_wanted(id(player), 'loan_default', game_time, escape_days=90)
                        
                        logger.error(f"[BANK] LOAN DEFAULT: {loan['amount']}g bounty added! Total wanted: {player.wanted_level}g")
                        return 'bounty_added', bounty_amount
        
        return None, 0


class BankUI:
    """UI for bank interactions"""
    def __init__(self, config):
        self.config = config
        self.active = False
        self.current_bank = None
        self.bank_manager = None
        self.selected_index = 0
        self.message = ""
        self.message_timer = 0
        
        # UI modes
        self.mode = "main"  # main, deposit, withdraw, store, retrieve, upgrade, take_loan, repay_loan, buy_property, sell_property, purchase_insurance, view_policies
        self.input_amount = ""
        self.selected_item_index = 0
        self.selected_property_index = 0
        
        # Scrolling for item lists
        self.scroll_offset = 0
        
        # Game time reference (set by main.py)
        self.game_time = None
    
    def open(self, bank, bank_manager):
        """Open the bank menu"""
        self.active = True
        self.current_bank = bank
        self.bank_manager = bank_manager
        self.selected_index = 0
        self.mode = "main"
        self.message = ""
        self.message_timer = 0
        self.input_amount = ""
        self.scroll_offset = 0
        logger.info(f"[BANK UI] Opened {bank.name}")
    
    def close(self):
        """Close the bank menu"""
        self.active = False
        self.current_bank = None
        self.mode = "main"
        logger.info("[BANK UI] Closed")
    
    def handle_input(self, event, player):
        """Handle keyboard input for bank menu"""
        if not self.active or not self.current_bank:
            return
        
        if event.type == pygame.KEYDOWN:
            # Handle amount input modes
            if self.mode in ["deposit", "withdraw", "take_loan"]:
                if event.key == pygame.K_ESCAPE:
                    self.mode = "main"
                    self.input_amount = ""
                elif event.key == pygame.K_RETURN:
                    if self.mode == "take_loan":
                        self._process_loan_transaction(player)
                    else:
                        self._process_gold_transaction(player)
                elif event.key == pygame.K_BACKSPACE:
                    self.input_amount = self.input_amount[:-1]
                elif event.unicode.isdigit() and len(self.input_amount) < 8:
                    self.input_amount += event.unicode
                return
            
            # Handle item selection modes
            if self.mode == "store":
                if event.key == pygame.K_ESCAPE:
                    self.mode = "main"
                elif event.key == pygame.K_UP:
                    self.selected_item_index = max(0, self.selected_item_index - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_item_index = min(len(player.inventory['items']) - 1, self.selected_item_index + 1)
                elif event.key == pygame.K_RETURN:
                    self._store_selected_item(player)
                return
            
            if self.mode == "retrieve":
                if event.key == pygame.K_ESCAPE:
                    self.mode = "main"
                elif event.key == pygame.K_UP:
                    self.selected_item_index = max(0, self.selected_item_index - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_item_index = min(len(self.bank_manager.player_storage) - 1, self.selected_item_index + 1)
                elif event.key == pygame.K_RETURN:
                    self._retrieve_selected_item(player)
                return
            
            # Property buy/sell modes
            if self.mode == "buy_property":
                if event.key == pygame.K_ESCAPE:
                    self.mode = "main"
                elif event.key == pygame.K_UP:
                    available = self.multiple_plots_system.get_available_plots(self.current_bank.town_name)
                    self.selected_property_index = max(0, self.selected_property_index - 1)
                elif event.key == pygame.K_DOWN:
                    available = self.multiple_plots_system.get_available_plots(self.current_bank.town_name)
                    self.selected_property_index = min(len(available) - 1, self.selected_property_index + 1)
                elif event.key == pygame.K_RETURN:
                    self._process_property_purchase(player)
                return
            
            if self.mode == "sell_property":
                if event.key == pygame.K_ESCAPE:
                    self.mode = "main"
                elif event.key == pygame.K_UP:
                    owned = self._get_player_properties(player)
                    self.selected_property_index = max(0, self.selected_property_index - 1)
                elif event.key == pygame.K_DOWN:
                    owned = self._get_player_properties(player)
                    self.selected_property_index = min(len(owned) - 1, self.selected_property_index + 1)
                elif event.key == pygame.K_RETURN:
                    self._sell_selected_property(player)
                return
            
            if self.mode == "purchase_insurance":
                if event.key == pygame.K_ESCAPE:
                    self.mode = "main"
                elif event.key == pygame.K_y:
                    self._purchase_insurance(player)
                elif event.key == pygame.K_n:
                    self.mode = "main"
                return
            
            if self.mode == "view_policies":
                if event.key == pygame.K_ESCAPE:
                    self.mode = "main"
                elif event.key == pygame.K_UP:
                    owned = self._get_player_properties(player)
                    self.selected_property_index = max(0, self.selected_property_index - 1)
                elif event.key == pygame.K_DOWN:
                    owned = self._get_player_properties(player)
                    self.selected_property_index = min(len(owned) - 1, self.selected_property_index + 1)
                elif event.key == pygame.K_RETURN:
                    self._process_property_sale(player)
                return
            
            # Main menu controls
            if event.key == pygame.K_ESCAPE:
                self.close()
            
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.current_bank.services)
            
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.current_bank.services)
            
            elif event.key == pygame.K_RETURN:
                self._activate_service(player)
    
    def _activate_service(self, player):
        """Activate the selected service"""
        service = self.current_bank.services[self.selected_index]
        
        if service.service_type == "deposit_gold":
            self.mode = "deposit"
            self.input_amount = ""
        elif service.service_type == "withdraw_gold":
            self.mode = "withdraw"
            self.input_amount = ""
        elif service.service_type == "store_item":
            if len(player.inventory['items']) == 0:
                self.message = "No items to store!"
                self.message_timer = 120
            else:
                self.mode = "store"
                self.selected_item_index = 0
        elif service.service_type == "retrieve_item":
            if len(self.bank_manager.player_storage) == 0:
                self.message = "No items in storage!"
                self.message_timer = 120
            else:
                self.mode = "retrieve"
                self.selected_item_index = 0
        elif service.service_type == "upgrade_storage":
            success, message = self.bank_manager.upgrade_storage_tier(player)
            self.message = message
            self.message_timer = 180
        elif service.service_type == "safety_deposit":
            # Open safety deposit UI
            if hasattr(self, 'safety_deposit_ui') and hasattr(self, 'safety_deposit_system'):
                self.safety_deposit_ui.open(self.current_bank.town_name, self.safety_deposit_system, player)
                self.close()  # Close bank main menu
            else:
                self.message = "Safety deposit system not available!"
                self.message_timer = 120
        elif service.service_type == "take_loan":
            # Check if already has a loan
            has_loan = False
            for loan in self.bank_manager.active_loans:
                if loan['player_id'] == id(player) and not loan['repaid']:
                    has_loan = True
                    break
            
            if has_loan:
                self.message = "You already have an active loan!"
                self.message_timer = 120
            else:
                self.mode = "take_loan"
                self.input_amount = ""
        elif service.service_type == "repay_loan":
            if not self.game_time:
                self.message = "Error: Game time not available!"
                self.message_timer = 120
                return
            
            success, message = self.bank_manager.repay_loan(player)
            self.message = message
            self.message_timer = 180
        elif service.service_type == "buy_property":
            if not hasattr(self, 'multiple_plots_system') or not self.multiple_plots_system:
                self.message = "Property system not available!"
                self.message_timer = 120
                return
            
            available = self.multiple_plots_system.get_available_plots(self.current_bank.town_name)
            if len(available) == 0:
                self.message = f"No properties available in {self.current_bank.town_name}!"
                self.message_timer = 180
            else:
                self.mode = "buy_property"
                self.selected_property_index = 0
        elif service.service_type == "sell_property":
            if not hasattr(self, 'multiple_plots_system') or not self.multiple_plots_system:
                self.message = "Property system not available!"
                self.message_timer = 120
                return
            
            owned = self._get_player_properties(player)
            if len(owned) == 0:
                self.message = "You don't own any properties!"
                self.message_timer = 180
            else:
                self.mode = "sell_property"
                self.selected_property_index = 0
        elif service.service_type == "purchase_insurance":
            if not hasattr(self, 'insurance_system') or not self.insurance_system:
                self.message = "Insurance system not available!"
                self.message_timer = 120
                return
            
            self.mode = "purchase_insurance"
        elif service.service_type == "view_policies":
            if not hasattr(self, 'insurance_system') or not self.insurance_system:
                self.message = "Insurance system not available!"
                self.message_timer = 120
                return
            
            policies = self.insurance_system.get_all_policies(player.name)
            if len(policies) == 0:
                self.message = "You have no insurance policies!"
                self.message_timer = 180
            else:
                self.mode = "view_policies"
    
    def _process_gold_transaction(self, player):
        """Process dubloon deposit or withdrawal"""
        try:
            amount = int(self.input_amount)
            if amount <= 0:
                self.message = "Invalid amount!"
                self.message_timer = 60
                return
            
            if self.mode == "deposit":
                if player.dubloons >= amount:
                    player.dubloons -= amount
                    self.bank_manager.deposit_gold(amount)
                    self.message = f"Deposited {amount}g successfully!"
                    self.message_timer = 120
                    self.mode = "main"
                else:
                    self.message = "Not enough dubloons!"
                    self.message_timer = 60
            
            elif self.mode == "withdraw":
                if self.bank_manager.withdraw_gold(amount):
                    player.dubloons += amount
                    self.message = f"Withdrew {amount}g successfully!"
                    self.message_timer = 120
                    self.mode = "main"
                else:
                    self.message = "Not enough dubloons in bank!"
                    self.message_timer = 60
        
        except ValueError:
            self.message = "Invalid amount!"
            self.message_timer = 60
    
    def _store_selected_item(self, player):
        """Store the selected item from player inventory"""
        if self.selected_item_index < len(player.inventory['items']):
            if not self.bank_manager.can_store_item():
                self.message = "Storage full! Upgrade vault or retrieve items."
                self.message_timer = 120
                return
            
            item = player.inventory['items'][self.selected_item_index]
            self.bank_manager.store_item(item)
            player.inventory['items'].pop(self.selected_item_index)
            self.message = f"Stored {item.name}!"
            self.message_timer = 120
            
            # Adjust selection if needed
            if self.selected_item_index >= len(player.inventory['items']) and self.selected_item_index > 0:
                self.selected_item_index -= 1
            
            if len(player.inventory['items']) == 0:
                self.mode = "main"
    
    def _retrieve_selected_item(self, player):
        """Retrieve the selected item from bank storage"""
        if self.selected_item_index < len(self.bank_manager.player_storage):
            item = self.bank_manager.retrieve_item(self.selected_item_index)
            if item:
                player.inventory['items'].append(item)
                self.message = f"Retrieved {item.name}!"
                self.message_timer = 120
                
                # Adjust selection if needed
                if self.selected_item_index >= len(self.bank_manager.player_storage) and self.selected_item_index > 0:
                    self.selected_item_index -= 1
                
                if len(self.bank_manager.player_storage) == 0:
                    self.mode = "main"
    
    def _process_loan_transaction(self, player):
        """Process loan request"""
        if not self.game_time:
            self.message = "Error: Game time not available!"
            self.message_timer = 120
            return
        
        try:
            amount = int(self.input_amount)
            if amount <= 0:
                self.message = "Invalid amount!"
                self.message_timer = 60
                return
            
            success, message = self.bank_manager.take_loan(player, amount, self.game_time)
            self.message = message
            self.message_timer = 180
            if success:
                self.mode = "main"
        
        except ValueError:
            self.message = "Invalid amount!"
            self.message_timer = 60
    
    def _get_player_properties(self, player):
        """Get list of properties owned by player in current town"""
        if not hasattr(self, 'multiple_plots_system') or not self.multiple_plots_system:
            return []
        
        owned_properties = []
        town_plots = self.multiple_plots_system.plots.get(self.current_bank.town_name, [])
        for plot in town_plots:
            if plot.owner_id == id(player):
                owned_properties.append(plot)
        return owned_properties
    
    def _process_property_purchase(self, player):
        """Process property purchase transaction"""
        if not hasattr(self, 'multiple_plots_system') or not self.multiple_plots_system:
            self.message = "Property system not available!"
            self.message_timer = 120
            return
        
        available = self.multiple_plots_system.get_available_plots(self.current_bank.town_name)
        if self.selected_property_index >= len(available):
            self.message = "Invalid property selection!"
            self.message_timer = 120
            return
        
        selected_plot = available[self.selected_property_index]
        purchase_price = selected_plot.value
        
        if player.dubloons >= purchase_price:
            # Purchase the plot
            plot = self.multiple_plots_system.buy_plot(self.current_bank.town_name, id(player), purchase_price)
            if plot:
                player.dubloons -= purchase_price
                
                # Add to player's owned properties list
                if not hasattr(player, 'owned_properties'):
                    player.owned_properties = []
                player.owned_properties.append(plot.plot_id)
                
                self.message = f"✓ Purchased {plot.plot_id} for {purchase_price}g!"
                self.message_timer = 200
                logger.info(f"[BANK] Player purchased property {plot.plot_id} for {purchase_price}g")
                
                # Check if more properties available
                available = self.multiple_plots_system.get_available_plots(self.current_bank.town_name)
                if len(available) == 0:
                    self.mode = "main"
                else:
                    self.selected_property_index = min(self.selected_property_index, len(available) - 1)
            else:
                self.message = "Purchase failed!"
                self.message_timer = 120
        else:
            needed = purchase_price - player.dubloons
            self.message = f"Not enough dubloons! Need {needed}db more."
            self.message_timer = 150
    
    def _process_property_sale(self, player):
        """Process property sale transaction"""
        if not hasattr(self, 'multiple_plots_system') or not self.multiple_plots_system:
            self.message = "Property system not available!"
            self.message_timer = 120
            return
        
        owned = self._get_player_properties(player)
        if self.selected_property_index >= len(owned):
            self.message = "Invalid property selection!"
            self.message_timer = 120
            return
        
        selected_plot = owned[self.selected_property_index]
        sale_value = self.multiple_plots_system.sell_plot(self.current_bank.town_name, id(player))
        
        if sale_value > 0:
            player.dubloons += sale_value
            
            # Remove from player's owned properties list
            if hasattr(player, 'owned_properties') and selected_plot.plot_id in player.owned_properties:
                player.owned_properties.remove(selected_plot.plot_id)
            
            self.message = f"✓ Sold {selected_plot.plot_id} for {sale_value}g!"
            self.message_timer = 200
            logger.info(f"[BANK] Player sold property {selected_plot.plot_id} for {sale_value}g")
            
            # Check if more properties owned
            owned = self._get_player_properties(player)
            if len(owned) == 0:
                self.mode = "main"
            else:
                self.selected_property_index = min(self.selected_property_index, len(owned) - 1)
        else:
            self.message = "Sale failed!"
            self.message_timer = 120
    
    def _purchase_insurance(self, player):
        """Process insurance purchase transaction"""
        if not hasattr(self, 'insurance_system') or not self.insurance_system:
            self.message = "Insurance system not available!"
            self.message_timer = 120
            return
        
        success, message, policy = self.insurance_system.purchase_property_insurance(player)
        
        if success:
            self.message = f"✓ {message}"
            self.message_timer = 240
            logger.info(f"[BANK] Player purchased insurance: {policy.policy_id}")
            self.mode = "main"
        else:
            self.message = f"✗ {message}"
            self.message_timer = 200
    
    def draw(self, screen, player):
        """Draw the bank menu"""
        if not self.active or not self.current_bank:
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
        
        # Draw based on mode
        if self.mode == "main":
            self._draw_main_menu(screen, player)
        elif self.mode in ["deposit", "withdraw"]:
            self._draw_gold_input(screen, player)
        elif self.mode == "take_loan":
            self._draw_loan_input(screen, player)
        elif self.mode == "store":
            self._draw_item_selection(screen, player, "Store Item - Select from Inventory")
        elif self.mode == "retrieve":
            self._draw_storage_view(screen, player)
        elif self.mode == "buy_property":
            self._draw_property_buy_view(screen, player)
        elif self.mode == "sell_property":
            self._draw_property_sell_view(screen, player)
        elif self.mode == "purchase_insurance":
            self._draw_insurance_purchase_view(screen, player)
        elif self.mode == "view_policies":
            self._draw_policies_view(screen, player)
        
        # Draw message
        if self.message:
            self._draw_message(screen)
    
    def _draw_main_menu(self, screen, player):
        """Draw the main bank menu"""
        menu_width = 700
        menu_height = 600
        menu_x = (self.config.SCREEN_WIDTH - menu_width) // 2
        menu_y = (self.config.SCREEN_HEIGHT - menu_height) // 2
        
        # Menu background - gold/green colors for bank
        menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_bg.fill((25, 40, 25, 240))
        pygame.draw.rect(menu_bg, (180, 150, 50), (0, 0, menu_width, menu_height), 4)
        screen.blit(menu_bg, (menu_x, menu_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render(self.current_bank.name, True, (220, 190, 80))
        screen.blit(title, (menu_x + menu_width // 2 - title.get_width() // 2, menu_y + 20))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 24)
        subtitle = subtitle_font.render("Secure Storage & Dubloon Management", True, (180, 160, 100))
        screen.blit(subtitle, (menu_x + menu_width // 2 - subtitle.get_width() // 2, menu_y + 70))
        
        # Account info
        info_y = menu_y + 110
        info_font = pygame.font.SysFont(None, 26)
        
        current_tier = self.bank_manager.get_max_storage_slots()
        
        # Get tier name safely
        tier_name = "Basic Vault"  # Default
        if self.current_bank and self.bank_manager.player_storage_tier < len(self.current_bank.storage_tiers):
            tier_name = self.current_bank.storage_tiers[self.bank_manager.player_storage_tier].name
        
        gold_text = info_font.render(f"Purse: {player.dubloons}db", True, (255, 215, 0))
        bank_text = info_font.render(f"Bank: {self.bank_manager.player_bank_gold}db", True, (180, 220, 180))
        storage_text = info_font.render(f"Storage: {len(self.bank_manager.player_storage)}/{current_tier}", True, (150, 200, 255))
        tier_text = info_font.render(f"Tier: {tier_name}", True, (200, 180, 120))
        
        screen.blit(gold_text, (menu_x + 30, info_y))
        screen.blit(bank_text, (menu_x + 200, info_y))
        screen.blit(storage_text, (menu_x + 30, info_y + 30))
        screen.blit(tier_text, (menu_x + 300, info_y + 30))
        
        # Services list
        service_y = menu_y + 190
        service_font = pygame.font.SysFont(None, 30)
        desc_font = pygame.font.SysFont(None, 22)
        
        for i, service in enumerate(self.current_bank.services):
            is_selected = (i == self.selected_index)
            
            # Service background
            service_height = 60
            service_bg_color = (50, 70, 50, 220) if is_selected else (35, 50, 35, 180)
            service_bg = pygame.Surface((menu_width - 40, service_height), pygame.SRCALPHA)
            service_bg.fill(service_bg_color)
            
            if is_selected:
                pygame.draw.rect(service_bg, (180, 150, 50), (0, 0, menu_width - 40, service_height), 3)
            
            screen.blit(service_bg, (menu_x + 20, service_y))
            
            # Service name
            name_text = service_font.render(service.name, True, (230, 220, 180))
            screen.blit(name_text, (menu_x + 35, service_y + 8))
            
            # Service description
            desc_text = desc_font.render(service.description, True, (180, 170, 140))
            screen.blit(desc_text, (menu_x + 35, service_y + 38))
            
            service_y += service_height + 5
        
        # Instructions
        instruction_y = menu_y + menu_height - 50
        instruction_font = pygame.font.SysFont(None, 24)
        instructions = ["↑↓: Select", "ENTER: Confirm", "ESC: Exit"]
        
        instruction_x = menu_x + 30
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (200, 180, 120))
            screen.blit(instr_text, (instruction_x, instruction_y))
            instruction_x += 220
    
    def _draw_gold_input(self, screen, player):
        """Draw dubloon deposit/withdraw input"""
        panel_width = 450
        panel_height = 200
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((35, 50, 35, 250))
        pygame.draw.rect(panel_bg, (180, 150, 50), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 36)
        title_text = "Deposit Dubloons" if self.mode == "deposit" else "Withdraw Dubloons"
        title = title_font.render(title_text, True, (220, 190, 80))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Current amounts
        info_font = pygame.font.SysFont(None, 24)
        if self.mode == "deposit":
            info_text = info_font.render(f"Available: {player.dubloons}db", True, (200, 180, 120))
        else:
            info_text = info_font.render(f"In Bank: {self.bank_manager.player_bank_gold}db", True, (200, 180, 120))
        screen.blit(info_text, (panel_x + panel_width // 2 - info_text.get_width() // 2, panel_y + 60))
        
        # Input field
        input_font = pygame.font.SysFont(None, 48)
        input_text = self.input_amount if self.input_amount else "0"
        input_surf = input_font.render(input_text + "g", True, (255, 215, 0))
        
        input_bg = pygame.Surface((panel_width - 60, 50), pygame.SRCALPHA)
        input_bg.fill((20, 30, 20, 220))
        pygame.draw.rect(input_bg, (255, 215, 0), (0, 0, panel_width - 60, 50), 2)
        
        screen.blit(input_bg, (panel_x + 30, panel_y + 95))
        screen.blit(input_surf, (panel_x + 40, panel_y + 103))
        
        # Instructions
        instr_font = pygame.font.SysFont(None, 20)
        instr = instr_font.render("ENTER: Confirm | ESC: Cancel", True, (180, 170, 140))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, panel_y + 160))
    
    def _draw_loan_input(self, screen, player):
        """Draw loan request input"""
        panel_width = 500
        panel_height = 300
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((35, 50, 35, 250))
        pygame.draw.rect(panel_bg, (180, 150, 50), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 36)
        title = title_font.render("Request Loan", True, (220, 190, 80))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Loan info
        info_font = pygame.font.SysFont(None, 22)
        loan_info = [
            "MIN: 100g | MAX: 5000g",
            "Interest: 15% (must repay 115%)",
            "Term: 30 days to repay",
            ""
        ]
        
        info_y = panel_y + 65
        for line in loan_info:
            if line:  # Skip empty lines
                text = info_font.render(line, True, (200, 180, 120))
                screen.blit(text, (panel_x + panel_width // 2 - text.get_width() // 2, info_y))
            info_y += 25
        
        # Input field
        input_font = pygame.font.SysFont(None, 48)
        input_text = self.input_amount if self.input_amount else "0"
        input_surf = input_font.render(input_text + "g", True, (255, 215, 0))
        
        input_bg = pygame.Surface((panel_width - 60, 50), pygame.SRCALPHA)
        input_bg.fill((20, 30, 20, 220))
        pygame.draw.rect(input_bg, (255, 215, 0), (0, 0, panel_width - 60, 50), 2)
        
        screen.blit(input_bg, (panel_x + 30, panel_y + 170))
        screen.blit(input_surf, (panel_x + 40, panel_y + 178))
        
        # Calculate repayment amount
        if self.input_amount and self.input_amount.isdigit():
            amount = int(self.input_amount)
            repayment = int(amount * 1.15)
            repay_font = pygame.font.SysFont(None, 20)
            repay_text = repay_font.render(f"You will repay: {repayment}g", True, (255, 150, 150))
            screen.blit(repay_text, (panel_x + panel_width // 2 - repay_text.get_width() // 2, panel_y + 230))
        
        # Instructions
        instr_font = pygame.font.SysFont(None, 20)
        instr = instr_font.render("ENTER: Request Loan | ESC: Cancel", True, (180, 170, 140))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, panel_y + 260))
    
    def _draw_item_selection(self, screen, player, title_text):
        """Draw item selection from player inventory"""
        panel_width = 600
        panel_height = 500
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((35, 50, 35, 250))
        pygame.draw.rect(panel_bg, (180, 150, 50), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 32)
        title = title_font.render(title_text, True, (220, 190, 80))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 15))
        
        # Item list
        item_y = panel_y + 60
        item_font = pygame.font.SysFont(None, 26)
        
        items = player.inventory['items']
        max_visible = 12
        
        for i in range(max_visible):
            idx = i + self.scroll_offset
            if idx >= len(items):
                break
            
            item = items[idx]
            is_selected = (idx == self.selected_item_index)
            
            # Item background
            item_bg_color = (50, 70, 50, 220) if is_selected else (30, 45, 30, 150)
            item_bg = pygame.Surface((panel_width - 40, 30), pygame.SRCALPHA)
            item_bg.fill(item_bg_color)
            
            if is_selected:
                pygame.draw.rect(item_bg, (180, 150, 50), (0, 0, panel_width - 40, 30), 2)
            
            screen.blit(item_bg, (panel_x + 20, item_y))
            
            # Item name and type
            item_text = item_font.render(f"{item.name} ({item.type})", True, (220, 210, 180))
            screen.blit(item_text, (panel_x + 30, item_y + 3))
            
            item_y += 32
        
        # Instructions
        instr_y = panel_y + panel_height - 40
        instr_font = pygame.font.SysFont(None, 22)
        instr = instr_font.render("↑↓: Select | ENTER: Store | ESC: Cancel", True, (180, 170, 140))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, instr_y))
    
    def _draw_storage_view(self, screen, player):
        """Draw items in bank storage"""
        panel_width = 600
        panel_height = 500
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((35, 50, 35, 250))
        pygame.draw.rect(panel_bg, (180, 150, 50), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 32)
        title = title_font.render("Bank Vault - Retrieve Item", True, (220, 190, 80))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 15))
        
        # Storage info
        info_font = pygame.font.SysFont(None, 22)
        max_slots = self.bank_manager.get_max_storage_slots()
        info = info_font.render(f"Storage: {len(self.bank_manager.player_storage)}/{max_slots} items", True, (180, 200, 180))
        screen.blit(info, (panel_x + panel_width // 2 - info.get_width() // 2, panel_y + 45))
        
        # Item list
        item_y = panel_y + 80
        item_font = pygame.font.SysFont(None, 26)
        
        items = self.bank_manager.player_storage
        max_visible = 12
        
        for i in range(max_visible):
            idx = i + self.scroll_offset
            if idx >= len(items):
                break
            
            item = items[idx]
            is_selected = (idx == self.selected_item_index)
            
            # Item background
            item_bg_color = (50, 70, 50, 220) if is_selected else (30, 45, 30, 150)
            item_bg = pygame.Surface((panel_width - 40, 30), pygame.SRCALPHA)
            item_bg.fill(item_bg_color)
            
            if is_selected:
                pygame.draw.rect(item_bg, (180, 150, 50), (0, 0, panel_width - 40, 30), 2)
            
            screen.blit(item_bg, (panel_x + 20, item_y))
            
            # Item name and type
            item_text = item_font.render(f"{item.name} ({item.type})", True, (220, 210, 180))
            screen.blit(item_text, (panel_x + 30, item_y + 3))
            
            item_y += 32
        
        # Instructions
        instr_y = panel_y + panel_height - 40
        instr_font = pygame.font.SysFont(None, 22)
        instr = instr_font.render("↑↓: Select | ENTER: Retrieve | ESC: Cancel", True, (180, 170, 140))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, instr_y))
    
    def _draw_message(self, screen):
        """Draw status message"""
        message_font = pygame.font.SysFont(None, 32)
        
        # Determine color
        if "success" in self.message.lower() or "upgraded" in self.message.lower() or "deposited" in self.message.lower() or "withdrew" in self.message.lower() or "stored" in self.message.lower() or "retrieved" in self.message.lower():
            message_color = (150, 255, 150)
        elif "not enough" in self.message.lower() or "full" in self.message.lower() or "invalid" in self.message.lower():
            message_color = (255, 100, 100)
        else:
            message_color = (220, 190, 80)
        
        message_surf = message_font.render(self.message, True, message_color)
        
        msg_x = (self.config.SCREEN_WIDTH - message_surf.get_width()) // 2
        msg_y = self.config.SCREEN_HEIGHT - 100
        
        msg_bg = pygame.Surface((message_surf.get_width() + 40, message_surf.get_height() + 20), pygame.SRCALPHA)
        msg_bg.fill((20, 30, 20, 230))
        pygame.draw.rect(msg_bg, message_color, (0, 0, msg_bg.get_width(), msg_bg.get_height()), 2)
        
        screen.blit(msg_bg, (msg_x - 20, msg_y - 10))
        screen.blit(message_surf, (msg_x, msg_y))
    
    def _draw_property_buy_view(self, screen, player):
        """Draw property purchase selection"""
        panel_width = 700
        panel_height = 550
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((35, 50, 35, 250))
        pygame.draw.rect(panel_bg, (180, 150, 50), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 36)
        title = title_font.render(f"Buy Property - {self.current_bank.town_name}", True, (220, 190, 80))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Player dubloons info
        info_font = pygame.font.SysFont(None, 24)
        gold_text = info_font.render(f"Your Dubloons: {player.dubloons}db", True, (255, 215, 0))
        screen.blit(gold_text, (panel_x + 30, panel_y + 65))
        
        # Property list
        available = self.multiple_plots_system.get_available_plots(self.current_bank.town_name)
        
        if len(available) == 0:
            no_props_font = pygame.font.SysFont(None, 28)
            no_props = no_props_font.render("No properties available for purchase", True, (200, 150, 100))
            screen.blit(no_props, (panel_x + panel_width // 2 - no_props.get_width() // 2, panel_y + 200))
        else:
            prop_y = panel_y + 100
            prop_font = pygame.font.SysFont(None, 26)
            
            for i, plot in enumerate(available):
                is_selected = (i == self.selected_property_index)
                
                # Property background
                prop_bg_color = (50, 70, 50, 220) if is_selected else (30, 45, 30, 150)
                prop_bg = pygame.Surface((panel_width - 60, 60), pygame.SRCALPHA)
                prop_bg.fill(prop_bg_color)
                
                if is_selected:
                    pygame.draw.rect(prop_bg, (180, 150, 50), (0, 0, panel_width - 60, 60), 2)
                
                screen.blit(prop_bg, (panel_x + 30, prop_y))
                
                # Property details
                prop_name = prop_font.render(f"📍 {plot.plot_id}", True, (220, 210, 180))
                screen.blit(prop_name, (panel_x + 45, prop_y + 8))
                
                price_text = prop_font.render(f"Price: {plot.value}g", True, (255, 215, 0))
                screen.blit(price_text, (panel_x + 45, prop_y + 32))
                
                # Affordability indicator
                if player.dubloons >= plot.value:
                    afford_text = prop_font.render("✓ Can afford", True, (150, 255, 150))
                else:
                    afford_text = prop_font.render("✗ Not enough dubloons", True, (255, 100, 100))
                screen.blit(afford_text, (panel_x + panel_width - 220, prop_y + 20))
                
                prop_y += 70
        
        # Instructions
        instr_y = panel_y + panel_height - 45
        instr_font = pygame.font.SysFont(None, 22)
        instr = instr_font.render("↑↓: Select | ENTER: Buy | ESC: Cancel", True, (180, 170, 140))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, instr_y))
    
    def _draw_property_sell_view(self, screen, player):
        """Draw property sale selection"""
        panel_width = 700
        panel_height = 550
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((35, 50, 35, 250))
        pygame.draw.rect(panel_bg, (180, 150, 50), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 36)
        title = title_font.render(f"Sell Property - {self.current_bank.town_name}", True, (220, 190, 80))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 20))
        
        # Player dubloons info
        info_font = pygame.font.SysFont(None, 24)
        gold_text = info_font.render(f"Your Dubloons: {player.dubloons}db", True, (255, 215, 0))
        screen.blit(gold_text, (panel_x + 30, panel_y + 65))
        
        # Sale info
        sale_info = info_font.render("Properties sell for 80% of purchase value", True, (200, 180, 120))
        screen.blit(sale_info, (panel_x + panel_width - sale_info.get_width() - 30, panel_y + 65))
        
        # Property list
        owned = self._get_player_properties(player)
        
        if len(owned) == 0:
            no_props_font = pygame.font.SysFont(None, 28)
            no_props = no_props_font.render("You don't own any properties in this town", True, (200, 150, 100))
            screen.blit(no_props, (panel_x + panel_width // 2 - no_props.get_width() // 2, panel_y + 200))
        else:
            prop_y = panel_y + 105
            prop_font = pygame.font.SysFont(None, 26)
            
            for i, plot in enumerate(owned):
                is_selected = (i == self.selected_property_index)
                sale_value = int(plot.value * 0.8)
                
                # Property background
                prop_bg_color = (50, 70, 50, 220) if is_selected else (30, 45, 30, 150)
                prop_bg = pygame.Surface((panel_width - 60, 60), pygame.SRCALPHA)
                prop_bg.fill(prop_bg_color)
                
                if is_selected:
                    pygame.draw.rect(prop_bg, (180, 150, 50), (0, 0, panel_width - 60, 60), 2)
                
                screen.blit(prop_bg, (panel_x + 30, prop_y))
                
                # Property details
                prop_name = prop_font.render(f"📍 {plot.plot_id}", True, (220, 210, 180))
                screen.blit(prop_name, (panel_x + 45, prop_y + 8))
                
                value_text = prop_font.render(f"Purchased: {plot.value}g → Sell: {sale_value}g", True, (255, 215, 0))
                screen.blit(value_text, (panel_x + 45, prop_y + 32))
                
                prop_y += 70
        
        # Instructions
        instr_y = panel_y + panel_height - 45
        instr_font = pygame.font.SysFont(None, 22)
        instr = instr_font.render("↑↓: Select | ENTER: Sell | ESC: Cancel", True, (180, 170, 140))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, instr_y))
    
    def _draw_insurance_purchase_view(self, screen, player):
        """Draw insurance purchase confirmation"""
        panel_width = 700
        panel_height = 500
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((35, 50, 35, 250))
        pygame.draw.rect(panel_bg, (180, 150, 50), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 40)
        title = title_font.render("🛡️ Property Insurance", True, (220, 190, 80))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 25))
        
        # Player dubloons info
        info_font = pygame.font.SysFont(None, 26)
        gold_text = info_font.render(f"Your Dubloons: {player.dubloons}db", True, (255, 215, 0))
        screen.blit(gold_text, (panel_x + 50, panel_y + 80))
        
        # Check if can purchase
        if hasattr(self, 'insurance_system') and self.insurance_system:
            can_purchase, reason = self.insurance_system.can_purchase_property_insurance(player)
        else:
            can_purchase = False
            reason = "Insurance system not available"
        
        # Policy details section
        details_y = panel_y + 125
        detail_font = pygame.font.SysFont(None, 24)
        
        details = [
            ("Cost:", "300 dubloons", (255, 215, 0)),
            ("Duration:", "2 years (730 days)", (200, 200, 200)),
            ("Coverage:", "50,000 wood rebuild cost", (150, 220, 150)),
            ("", "All items in house protected", (150, 220, 150)),
            ("", "Fire & destruction covered", (150, 220, 150)),
        ]
        
        for label, value, color in details:
            if label:
                label_surf = detail_font.render(label, True, (200, 180, 150))
                screen.blit(label_surf, (panel_x + 80, details_y))
                value_surf = detail_font.render(value, True, color)
                screen.blit(value_surf, (panel_x + 250, details_y))
            else:
                value_surf = detail_font.render(value, True, color)
                screen.blit(value_surf, (panel_x + 250, details_y))
            details_y += 32
        
        # Status/error message
        if not can_purchase:
            error_font = pygame.font.SysFont(None, 26)
            error_bg = pygame.Surface((panel_width - 100, 60), pygame.SRCALPHA)
            error_bg.fill((120, 30, 30, 200))
            pygame.draw.rect(error_bg, (200, 60, 60), (0, 0, panel_width - 100, 60), 2)
            screen.blit(error_bg, (panel_x + 50, panel_y + 335))
            
            error_text = error_font.render(f"❌ Cannot Purchase: {reason}", True, (255, 220, 220))
            screen.blit(error_text, (panel_x + panel_width // 2 - error_text.get_width() // 2, panel_y + 355))
        else:
            confirm_font = pygame.font.SysFont(None, 28)
            confirm_text = confirm_font.render("Purchase this insurance policy?", True, (220, 220, 180))
            screen.blit(confirm_text, (panel_x + panel_width // 2 - confirm_text.get_width() // 2, panel_y + 350))
        
        # Instructions
        instr_y = panel_y + panel_height - 50
        instr_font = pygame.font.SysFont(None, 24)
        if can_purchase:
            instr = instr_font.render("Y: Confirm Purchase | N/ESC: Cancel", True, (180, 170, 140))
        else:
            instr = instr_font.render("ESC: Cancel", True, (180, 170, 140))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, instr_y))
    
    def _draw_policies_view(self, screen, player):
        """Draw active insurance policies list"""
        panel_width = 750
        panel_height = 550
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_bg.fill((35, 50, 35, 250))
        pygame.draw.rect(panel_bg, (180, 150, 50), (0, 0, panel_width, panel_height), 3)
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 40)
        title = title_font.render("📋 Your Insurance Policies", True, (220, 190, 80))
        screen.blit(title, (panel_x + panel_width // 2 - title.get_width() // 2, panel_y + 25))
        
        # Get policies
        if hasattr(self, 'insurance_system') and self.insurance_system:
            policies = self.insurance_system.get_all_policies(player.name)
            current_time = self.insurance_system.game_time.day_count if self.insurance_system.game_time else 0
        else:
            policies = []
            current_time = 0
        
        if len(policies) == 0:
            no_policies_font = pygame.font.SysFont(None, 28)
            no_policies = no_policies_font.render("You have no insurance policies", True, (200, 150, 100))
            screen.blit(no_policies, (panel_x + panel_width // 2 - no_policies.get_width() // 2, panel_y + 250))
        else:
            policy_y = panel_y + 85
            policy_font = pygame.font.SysFont(None, 24)
            detail_font = pygame.font.SysFont(None, 20)
            
            for policy in policies:
                is_active = policy.is_active(current_time)
                days_left = policy.days_remaining(current_time)
                
                # Policy background
                if is_active:
                    policy_bg_color = (40, 70, 40, 220)
                    border_color = (100, 180, 100)
                    status_text = f"✓ ACTIVE ({days_left} days remaining)"
                    status_color = (150, 255, 150)
                else:
                    policy_bg_color = (60, 40, 40, 200)
                    border_color = (150, 80, 80)
                    status_text = "✗ EXPIRED"
                    status_color = (255, 150, 150)
                
                policy_bg = pygame.Surface((panel_width - 60, 110), pygame.SRCALPHA)
                policy_bg.fill(policy_bg_color)
                pygame.draw.rect(policy_bg, border_color, (0, 0, panel_width - 60, 110), 2)
                screen.blit(policy_bg, (panel_x + 30, policy_y))
                
                # Policy details
                policy_id_text = policy_font.render(f"Policy: {policy.policy_id}", True, (220, 210, 180))
                screen.blit(policy_id_text, (panel_x + 45, policy_y + 10))
                
                status_surf = policy_font.render(status_text, True, status_color)
                screen.blit(status_surf, (panel_x + panel_width - status_surf.get_width() - 45, policy_y + 10))
                
                type_text = detail_font.render(f"Type: {policy.policy_type.title()} Insurance", True, (200, 190, 170))
                screen.blit(type_text, (panel_x + 45, policy_y + 40))
                
                cost_text = detail_font.render(f"Cost: {policy.cost}g", True, (255, 215, 0))
                screen.blit(cost_text, (panel_x + 45, policy_y + 62))
                
                if 'rebuild_cost' in policy.coverage:
                    coverage_text = detail_font.render(f"Coverage: {policy.coverage['rebuild_cost']:,} wood rebuild", True, (150, 200, 150))
                    screen.blit(coverage_text, (panel_x + 45, policy_y + 84))
                
                policy_y += 120
                
                # Limit display to 3 policies to fit screen
                if policy_y > panel_y + 430:
                    break
        
        # Instructions
        instr_y = panel_y + panel_height - 50
        instr_font = pygame.font.SysFont(None, 22)
        instr = instr_font.render("ESC: Back to Menu", True, (180, 170, 140))
        screen.blit(instr, (panel_x + panel_width // 2 - instr.get_width() // 2, instr_y))



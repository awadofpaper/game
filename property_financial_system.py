"""
Property & Financial System
Handles multiple plots, house sales, NPC finances, town treasury, guard protection fees, and resource contracts.
"""
import random
import time

class Plot:
    def __init__(self, plot_id, town_name, owner_id=None, value=10000):
        self.plot_id = plot_id
        self.town_name = town_name
        self.owner_id = owner_id
        self.value = value
        self.for_sale = False
        self.sale_price = value

class MultiplePlotsSystem:
    def __init__(self, town_manager):
        self.town_manager = town_manager
        self.plots = {}  # {town_name: [Plot]}
        self.max_plots_per_town = 5
        self.init_plots()

    def init_plots(self):
        for town in self.town_manager.towns:
            self.plots[town.name] = [Plot(f"{town.name}-P{i+1}", town.name) for i in range(self.max_plots_per_town)]

    def get_available_plots(self, town_name):
        return [p for p in self.plots.get(town_name, []) if p.owner_id is None]

    def buy_plot(self, town_name, buyer_id, price):
        available = self.get_available_plots(town_name)
        if available:
            plot = available[0]
            plot.owner_id = buyer_id
            plot.value = price
            return plot
        return None

    def sell_plot(self, town_name, owner_id):
        for plot in self.plots.get(town_name, []):
            if plot.owner_id == owner_id:
                loss = int(plot.value * 0.8)
                plot.owner_id = None
                plot.value = 10000
                plot.for_sale = True
                plot.sale_price = int(plot.value * 0.2)
                return loss
        return 0

class NPCFinances:
    def __init__(self, npc_ref, is_merchant=False, is_mayor=False):
        self.npc_ref = npc_ref  # Store actual NPC reference
        self.is_merchant = is_merchant
        self.is_mayor = is_mayor
        self.starting_balance = 700000 if is_merchant else 500000
        if is_merchant and is_mayor:
            self.starting_balance = 500000
        self.last_paid_day = None
        self.total_paid = 0  # Track total amount paid to this NPC

    def pay(self, amount):
        # Actually add money to the NPC's dubloons
        if self.npc_ref and hasattr(self.npc_ref, 'dubloons'):
            self.npc_ref.dubloons = getattr(self.npc_ref, 'dubloons', 0) + amount
            self.total_paid += amount
            return True
        return False

    def deduct(self, amount):
        if self.npc_ref and hasattr(self.npc_ref, 'dubloons'):
            current = getattr(self.npc_ref, 'dubloons', 0)
            self.npc_ref.dubloons = max(0, current - amount)
            return True
        return False

    def update_payment(self, game_time):
        if self.last_paid_day is None or game_time.day_count - self.last_paid_day >= 3:
            success = self.pay(1000)
            if success:
                self.last_paid_day = game_time.day_count
                return 1000
        return 0

class NPCFinancesSystem:
    def __init__(self):
        self.npc_finances = {}  # {npc_id: NPCFinances}

    def add_npc(self, npc, is_merchant=False, is_mayor=False):
        """Register an NPC to receive regular payments"""
        npc_id = id(npc)
        self.npc_finances[npc_id] = NPCFinances(npc, is_merchant, is_mayor)

    def update_all(self, game_time):
        """Update all NPC finances, paying them every 3 days"""
        total_paid = 0
        npcs_paid = 0
        for finance in self.npc_finances.values():
            amount = finance.update_payment(game_time)
            if amount > 0:
                total_paid += amount
                npcs_paid += 1
        return total_paid, npcs_paid
    
    def get_npc_finance_info(self, npc):
        """Get finance info for a specific NPC"""
        npc_id = id(npc)
        if npc_id in self.npc_finances:
            finance = self.npc_finances[npc_id]
            return {
                'registered': True,
                'total_paid': finance.total_paid,
                'last_paid_day': finance.last_paid_day,
                'is_merchant': finance.is_merchant,
                'is_mayor': finance.is_mayor
            }
        return {'registered': False}

class TownTreasury:
    def __init__(self, town_name):
        self.town_name = town_name
        self.balance = 0
        self.transactions = []

    def deposit(self, amount, reason):
        self.balance += amount
        self.transactions.append((time.time(), amount, reason))

    def withdraw(self, amount, reason):
        self.balance = max(0, self.balance - amount)
        self.transactions.append((time.time(), -amount, reason))

class TownTreasurySystem:
    def __init__(self, town_manager):
        self.town_manager = town_manager
        self.treasuries = {town.name: TownTreasury(town.name) for town in town_manager.towns}

    def deposit(self, town_name, amount, reason):
        if town_name in self.treasuries:
            self.treasuries[town_name].deposit(amount, reason)

    def withdraw(self, town_name, amount, reason):
        if town_name in self.treasuries:
            self.treasuries[town_name].withdraw(amount, reason)

    def get_balance(self, town_name):
        return self.treasuries[town_name].balance if town_name in self.treasuries else 0

class GuardProtectionFeeSystem:
    def __init__(self):
        self.fees_due = {}  # {npc_id: next_due_day}
        self.fee_amount = 1000
        self.fee_interval = 7  # days

    def charge_fee(self, npc_id, game_time):
        next_due = self.fees_due.get(npc_id, 0)
        if game_time.day_count >= next_due:
            self.fees_due[npc_id] = game_time.day_count + self.fee_interval
            return self.fee_amount
        return 0

class ResourceContractSystem:
    def __init__(self):
        self.contracts = {}  # {mayor_id: contract_paid}
        self.contract_amount = 300

    def pay_contract(self, mayor_id):
        if mayor_id not in self.contracts:
            self.contracts[mayor_id] = True
            return self.contract_amount
        return 0

class PropertyTaxSystem:
    """Manages yearly property taxes for players with property"""
    def __init__(self):
        self.tax_amount = 500  # Flat yearly tax for ALL properties combined
        self.tax_interval = 365  # Days (1 year)
        self.last_tax_day = {}  # {player_id: last_tax_day}
        self.unpaid_taxes = {}  # {player_id: unpaid_amount}
        self.unpaid_start_day = {}  # {player_id: day_count when debt started}
        self.bounty_added = {}  # {player_id: bool} - track if bounty already added
        self.bounty_threshold_days = 30  # Add bounty after 30 days of unpaid debt
    
    def check_tax_due(self, player_id, game_time, property_count):
        """Check if tax is due for this player"""
        if property_count <= 0:
            return False, 0  # No properties, no tax
        
        last_tax = self.last_tax_day.get(player_id, 0)
        days_since_tax = game_time.day_count - last_tax
        
        if days_since_tax >= self.tax_interval:
            return True, self.tax_amount
        return False, 0
    
    def collect_tax(self, player, game_time, property_count):
        """Attempt to collect tax from player"""
        player_id = id(player)
        
        if property_count <= 0:
            return False, "No properties owned - no tax due", 0
        
        # Check if tax is due
        is_due, tax_amount = self.check_tax_due(player_id, game_time, property_count)
        
        if not is_due:
            return False, "Tax not due yet", 0
        
        # Try to collect
        if player.dubloons >= tax_amount:
            player.dubloons -= tax_amount
            self.last_tax_day[player_id] = game_time.day_count
            return True, f"Property tax paid: {tax_amount}g", tax_amount
        else:
            # Can't afford tax - add to unpaid
            self.unpaid_taxes[player_id] = self.unpaid_taxes.get(player_id, 0) + tax_amount
            # Track when unpaid debt started
            if player_id not in self.unpaid_start_day:
                self.unpaid_start_day[player_id] = game_time.day_count
            self.last_tax_day[player_id] = game_time.day_count  # Still update last tax day to avoid daily charges
            return False, f"Cannot afford property tax! {tax_amount}g added to debt.", tax_amount
    
    def check_unpaid_consequences(self, player, game_time):
        """Check and apply consequences for unpaid taxes (called daily)"""
        player_id = id(player)
        
        # No unpaid debt - nothing to do
        if player_id not in self.unpaid_taxes or self.unpaid_taxes[player_id] <= 0:
            return False, None
        
        unpaid_amount = self.unpaid_taxes[player_id]
        debt_start = self.unpaid_start_day.get(player_id, game_time.day_count)
        days_unpaid = game_time.day_count - debt_start
        
        # After threshold days, add bounty (if not already added)
        if days_unpaid >= self.bounty_threshold_days and not self.bounty_added.get(player_id, False):
            bounty_amount = unpaid_amount  # Bounty = unpaid debt
            player.bounty = getattr(player, 'bounty', 0) + bounty_amount
            self.bounty_added[player_id] = True
            return True, f"Tax evasion bounty added: {bounty_amount}g\n(Unpaid taxes: {unpaid_amount}g for {days_unpaid} days)"
        
        return False, None
    
    def pay_back_taxes(self, player):
        """Allow player to pay off accumulated tax debt"""
        player_id = id(player)
        
        unpaid_amount = self.unpaid_taxes.get(player_id, 0)
        if unpaid_amount <= 0:
            return False, "No unpaid taxes", 0
        
        if player.dubloons >= unpaid_amount:
            player.dubloons -= unpaid_amount
            self.unpaid_taxes[player_id] = 0
            # Reset tracking
            if player_id in self.unpaid_start_day:
                del self.unpaid_start_day[player_id]
            if player_id in self.bounty_added:
                del self.bounty_added[player_id]
            return True, f"Back taxes paid: {unpaid_amount}g", unpaid_amount
        else:
            return False, f"Cannot afford back taxes (Need: {unpaid_amount}g, Have: {player.dubloons}g)", 0

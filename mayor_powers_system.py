"""
Mayor Powers System
Handles curfew, entry fees, weapon restrictions, mayor salary, absconding, and embargo mechanics.
"""
import random
import time

class CurfewSystem:
    def __init__(self):
        self.curfew_start = 17  # 5PM
        self.curfew_end = 2     # 2AM
        self.fine_amount = 300
        self.active_towns = set()  # Towns with active curfew
        self.player_warned = {}  # {player_id: last_warning_day}
        
    def enable_curfew(self, town_name):
        """Enable curfew for a specific town"""
        self.active_towns.add(town_name)
        
    def disable_curfew(self, town_name):
        """Disable curfew for a specific town"""
        self.active_towns.discard(town_name)
        
    def is_curfew_active(self, town_name):
        """Check if curfew is active for a town"""
        return town_name in self.active_towns

    def is_curfew_hours(self, current_hour):
        """Check if current time is during curfew hours
        
        Handles wraparound for curfews that span midnight (e.g., 17:00 to 02:00).
        
        Args:
            current_hour: Integer hour (0-23)
            
        Returns:
            bool: True if current hour is within curfew period
        """
        # Validate input
        if not isinstance(current_hour, (int, float)):
            return False
        
        # Normalize hour to 0-23 range
        current_hour = int(current_hour) % 24
        
        # Handle wraparound case (e.g., 17:00 to 02:00 spans midnight)
        if self.curfew_start > self.curfew_end:
            # Curfew spans midnight: check if hour >= start OR hour < end
            return current_hour >= self.curfew_start or current_hour < self.curfew_end
        else:
            # Normal case: check if hour is between start and end
            return self.curfew_start <= current_hour < self.curfew_end

    def fine_player(self, player, town_treasury_system=None, town_name=None):
        """Apply curfew fine to player (only called when detected by guards)"""
        player.gold = max(0, player.gold - self.fine_amount)
        # Deposit fine into town treasury
        if town_treasury_system and town_name:
            town_treasury_system.deposit(town_name, self.fine_amount, "Curfew Fine")
        return self.fine_amount

class TownEntryFeeSystem:
    def __init__(self):
        self.lockdown_active = False
        self.entry_fee = 20

    def charge_entry(self, player, town_treasury_system=None, town_name=None):
        if self.lockdown_active:
            player.dubloons = max(0, player.dubloons - self.entry_fee)
            # Deposit entry fee into town treasury
            if town_treasury_system and town_name:
                town_treasury_system.deposit(town_name, self.entry_fee, "Entry Fee")
            return self.entry_fee
        return 0

class WeaponRestrictionSystem:
    def __init__(self):
        self.restriction_active = False
        self.stored_weapons = []  # Temporary storage during enforcement
        self.perk_melee_allowed = False
        self.town_hall_storage = {}  # {town_name: [weapons]} - for stealing

    def enforce(self, player, town_name=None):
        """Confiscate weapons when entering town with restrictions"""
        if self.restriction_active:
            confiscated = []
            for item in player.inventory.get('items', []):
                if getattr(item, 'type', None) == 'weapon':
                    # Check if player can keep basic melee weapons (skill check)
                    if getattr(item, 'subtype', None) == 'melee':
                        weapon_name = getattr(item, 'name', '').lower()
                        is_basic = any(basic in weapon_name for basic in ['knife', 'bat', 'dagger', 'club'])
                        
                        if is_basic:
                            # Skill check: STR or DEX >= 15 to keep basic melee
                            player_str = getattr(player, 'strength', 10)
                            player_dex = getattr(player, 'dexterity', 10)
                            if player_str >= 15 or player_dex >= 15:
                                # Passed skill check, keep the weapon
                                continue
                        
                        # Allow if perk enabled
                        if self.perk_melee_allowed:
                            continue
                    
                    # Confiscate weapon
                    confiscated.append(item)
                    player.inventory['items'].remove(item)
            
            # Store confiscated weapons
            self.stored_weapons.extend(confiscated)
            
            # Also store in town hall chest for stealing
            if town_name and confiscated:
                if town_name not in self.town_hall_storage:
                    self.town_hall_storage[town_name] = []
                self.town_hall_storage[town_name].extend(confiscated)
            
            return confiscated
        return []
    
    def return_weapons(self, player):
        """Return all confiscated weapons to player when leaving town"""
        if self.stored_weapons:
            if 'items' not in player.inventory:
                player.inventory['items'] = []
            
            for weapon in self.stored_weapons:
                player.inventory['items'].append(weapon)
            
            returned_count = len(self.stored_weapons)
            self.stored_weapons = []  # Clear storage
            return returned_count
        return 0
    
    def steal_from_town_hall(self, player, town_name):
        """Attempt to steal confiscated weapons from town hall"""
        if town_name in self.town_hall_storage and self.town_hall_storage[town_name]:
            if 'items' not in player.inventory:
                player.inventory['items'] = []
            
            stolen_items = self.town_hall_storage[town_name].copy()
            for weapon in stolen_items:
                player.inventory['items'].append(weapon)
            
            stolen_count = len(stolen_items)
            self.town_hall_storage[town_name] = []  # Clear town hall storage
            return stolen_count, stolen_items
        return 0, []

class MayorSalarySystem:
    def __init__(self):
        self.salary_amount = 500
        self.salary_interval = 120  # 4 months in days
        self.last_paid_day = None

    def pay_salary(self, mayor, game_time):
        if self.last_paid_day is None or game_time.day_count - self.last_paid_day >= self.salary_interval:
            mayor.dubloons = getattr(mayor, 'dubloons', 0) + self.salary_amount
            self.last_paid_day = game_time.day_count
            return self.salary_amount
        return 0
    
    def check_salary_due(self, game_time):
        """Check if salary payment is due without actually paying"""
        if self.last_paid_day is None or game_time.day_count - self.last_paid_day >= self.salary_interval:
            if self.last_paid_day is not None:  # Only update if we've paid before
                self.last_paid_day = game_time.day_count
            return self.salary_amount
        return 0

class MayorAbscondingSystem:
    def __init__(self):
        self.absconded = False
        self.treasury_stolen = 0
        self.reward_percent = 0.3
        self.tracked = False
        self.absconded_town = None  # Track which town it happened in

    def abscond(self, mayor, town_treasury, town_name=None):
        self.absconded = True
        self.treasury_stolen = town_treasury.balance
        self.absconded_town = town_name
        mayor.dubloons = getattr(mayor, 'dubloons', 0) + self.treasury_stolen
        town_treasury.balance = 0

    def track_mayor(self, player):
        if self.absconded and not self.tracked:
            reward = int(self.treasury_stolen * self.reward_percent)
            player.dubloons = getattr(player, 'dubloons', 0) + reward
            self.tracked = True
            # Auto-reset after tracking is complete to allow future abscond events
            self.reset()
            return reward
        return 0
    
    def reset(self):
        """Reset the absconding system to allow new abscond events"""
        self.absconded = False
        self.treasury_stolen = 0
        self.tracked = False
        self.absconded_town = None
    
    def get_tracking_info(self):
        """Returns info about active tracking quest if available"""
        if self.absconded and not self.tracked:
            return {
                'available': True,
                'town': self.absconded_town,
                'stolen': self.treasury_stolen,
                'reward': int(self.treasury_stolen * self.reward_percent)
            }
        return {'available': False}

class EmbargoSystem:
    def __init__(self):
        self.embargo_active = False
        self.embargo_fee_percent = 0.3
        self.embargo_duration = 30  # days
        self.embargo_start_day = None

    def start_embargo(self, game_time):
        self.embargo_active = True
        self.embargo_start_day = game_time.day_count

    def update(self, game_time):
        if self.embargo_active and game_time.day_count - self.embargo_start_day >= self.embargo_duration:
            self.embargo_active = False
            self.embargo_start_day = None

    def apply_embargo_fee(self, sale_amount):
        if self.embargo_active:
            fee = int(sale_amount * self.embargo_fee_percent)
            return fee
        return 0

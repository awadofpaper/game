"""
Inn Rental System
Handles room rentals, monthly payments, late fees, and storage
"""

import time


class InnRental:
    """Represents a player's rental at an inn"""
    
    def __init__(self, player_name, inn_id, inn_name, start_time, monthly_cost=100):
        """
        Initialize an inn rental
        
        Args:
            player_name: Name of the player renting
            inn_id: Unique identifier for the inn
            inn_name: Name of the inn
            start_time: Game time when rental started (in days)
            monthly_cost: Cost per month (default 100 dubloons)
        """
        self.player_name = player_name
        self.inn_id = inn_id
        self.inn_name = inn_name
        self.start_time = start_time
        self.monthly_cost = monthly_cost
        
        # Payment tracking
        self.last_payment_month = self.get_month_from_days(start_time)
        self.rent_due = False
        self.rent_due_time = None
        self.days_late = 0
        self.late_fee = 0
        
        # Eviction tracking
        self.evicted = False
        self.eviction_time = None
        
        # Storage
        self.storage = {}  # {item_name: quantity}
        self.storage_locked = False
        
        # Re-rental
        self.re_rental_fee = 1000
        self.can_re_rent = True
    
    def get_month_from_days(self, day_count):
        """Convert day count to month number"""
        # Assuming 30 days per month
        return day_count // 30
    
    def get_day_of_month(self, day_count):
        """Get day of month (1-30)"""
        return (day_count % 30) + 1
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'player_name': self.player_name,
            'inn_id': self.inn_id,
            'inn_name': self.inn_name,
            'start_time': self.start_time,
            'monthly_cost': self.monthly_cost,
            'last_payment_month': self.last_payment_month,
            'rent_due': self.rent_due,
            'rent_due_time': self.rent_due_time,
            'days_late': self.days_late,
            'late_fee': self.late_fee,
            'evicted': self.evicted,
            'eviction_time': self.eviction_time,
            'storage': self.storage,
            'storage_locked': self.storage_locked,
            're_rental_fee': self.re_rental_fee,
            'can_re_rent': self.can_re_rent
        }
    
    @staticmethod
    def from_dict(data):
        """Deserialize from dictionary"""
        rental = InnRental(
            data['player_name'],
            data['inn_id'],
            data['inn_name'],
            data['start_time'],
            data.get('monthly_cost', 100)
        )
        rental.last_payment_month = data.get('last_payment_month', rental.last_payment_month)
        rental.rent_due = data.get('rent_due', False)
        rental.rent_due_time = data.get('rent_due_time')
        rental.days_late = data.get('days_late', 0)
        rental.late_fee = data.get('late_fee', 0)
        rental.evicted = data.get('evicted', False)
        rental.eviction_time = data.get('eviction_time')
        rental.storage = data.get('storage', {})
        rental.storage_locked = data.get('storage_locked', False)
        rental.re_rental_fee = data.get('re_rental_fee', 1000)
        rental.can_re_rent = data.get('can_re_rent', True)
        return rental


class InnRentalSystem:
    """Manages inn rentals and payments"""
    
    MONTHLY_COST = 100  # Dubloons per month
    LATE_FEE_PER_DAY = 100  # Extra fee per day late
    MAX_LATE_DAYS = 3  # Maximum days before eviction
    RE_RENTAL_FEE = 1000  # Cost to re-rent after eviction
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.rentals = {}  # {player_name: InnRental}
        self.rent_notifications = []  # List of messages to show player
        self.last_checked_day = -1
    
    def can_rent_room(self, player, inn_id):
        """
        Check if player can rent a room at inn
        
        Args:
            player: Player object
            inn_id: ID of the inn
            
        Returns:
            tuple: (can_rent: bool, reason: str, cost: int)
        """
        player_name = player.name
        
        # Check if player already renting
        if player_name in self.rentals:
            rental = self.rentals[player_name]
            if rental.evicted:
                # Must pay re-rental fee
                player_gold = player.inventory.get('gold', 0)
                total_cost = self.RE_RENTAL_FEE + self.MONTHLY_COST
                if player_gold < total_cost:
                    return False, f"Need {total_cost} dubloons (re-rental fee + first month)", total_cost
                return True, "Can re-rent (includes re-rental fee)", total_cost
            else:
                return False, f"Already renting at {rental.inn_name}", 0
        
        # Check if player has enough money for first month
        player_gold = player.inventory.get('gold', 0)
        if player_gold < self.MONTHLY_COST:
            return False, f"Need {self.MONTHLY_COST} dubloons", self.MONTHLY_COST
        
        return True, "Can rent room", self.MONTHLY_COST
    
    def rent_room(self, player, inn_id, inn_name):
        """
        Player rents a room at an inn
        
        Args:
            player: Player object
            inn_id: ID of the inn
            inn_name: Name of the inn
            
        Returns:
            tuple: (success: bool, message: str)
        """
        can_rent, reason, cost = self.can_rent_room(player, inn_id)
        if not can_rent:
            return False, reason
        
        player_name = player.name
        current_time = self.game_time.day_count if self.game_time else 0
        
        # Check if re-renting after eviction
        if player_name in self.rentals and self.rentals[player_name].evicted:
            # Pay re-rental fee + first month
            player.inventory['gold'] -= self.RE_RENTAL_FEE + self.MONTHLY_COST
            
            # Unlock storage
            self.rentals[player_name].evicted = False
            self.rentals[player_name].storage_locked = False
            self.rentals[player_name].days_late = 0
            self.rentals[player_name].late_fee = 0
            self.rentals[player_name].last_payment_month = self.get_month_from_days(current_time)
            
            return True, f"Re-rented room at {inn_name}! Storage unlocked."
        
        # New rental
        player.inventory['gold'] -= self.MONTHLY_COST
        
        rental = InnRental(player_name, inn_id, inn_name, current_time, self.MONTHLY_COST)
        self.rentals[player_name] = rental
        
        return True, f"Rented room at {inn_name} for {self.MONTHLY_COST} dubloons/month"
    
    def get_month_from_days(self, day_count):
        """Convert day count to month number"""
        return day_count // 30
    
    def get_day_of_month(self, day_count):
        """Get day of month (1-30)"""
        return (day_count % 30) + 1
    
    def get_hour_of_day(self):
        """Get current hour"""
        if self.game_time:
            return self.game_time.hour
        return 0
    
    def check_rent_due(self, player):
        """
        Check if rent is due and process payment
        Called every frame
        
        Args:
            player: Player object
        """
        if player.name not in self.rentals:
            return
        
        rental = self.rentals[player.name]
        if rental.evicted:
            return
        
        current_time = self.game_time.day_count if self.game_time else 0
        current_month = self.get_month_from_days(current_time)
        current_day = self.get_day_of_month(current_time)
        current_hour = self.get_hour_of_day()
        
        # Check at midnight on 1st of month
        if current_day == 1 and current_hour == 0:
            if current_month != rental.last_payment_month:
                # Rent is due!
                rental.rent_due = True
                rental.rent_due_time = current_time
                
                # Check if player is at inn (simplified - check if near inn)
                player_at_inn = self.is_player_at_inn(player, rental.inn_id)
                
                if player_at_inn:
                    # Automatic deduction
                    success, message = self.pay_rent(player, rental)
                    if success:
                        self.rent_notifications.append(f"Rent auto-paid: {rental.monthly_cost} dubloons")
                    else:
                        # Can't pay - mark as late
                        self.rent_notifications.append(
                            "RENT DUE! Unable to auto-pay. You have until noon to pay or face late fees."
                        )
                else:
                    # Send notification
                    self.rent_notifications.append(
                        "Well its everyone's favourite day RENT DAY! Pay your damn rent, you have until noon."
                    )
        
        # Check for late payments
        if rental.rent_due and not rental.evicted:
            hours_since_due = (current_time - rental.rent_due_time) * 24 + current_hour
            days_late = hours_since_due // 24
            
            # Calculate late fees
            if hours_since_due >= 12:  # After noon
                rental.days_late = min(days_late, self.MAX_LATE_DAYS)
                rental.late_fee = rental.days_late * self.LATE_FEE_PER_DAY
                
                # Eviction after 3 days
                if rental.days_late >= self.MAX_LATE_DAYS:
                    self.evict_player(player, rental)
    
    def pay_rent(self, player, rental=None):
        """
        Player pays rent (manual or automatic)
        
        Args:
            player: Player object
            rental: InnRental object (optional, will look up)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if rental is None:
            if player.name not in self.rentals:
                return False, "Not renting a room"
            rental = self.rentals[player.name]
        
        if rental.evicted:
            return False, "Evicted - must pay re-rental fee"
        
        if not rental.rent_due:
            return False, "Rent not due yet"
        
        # Calculate total cost (rent + late fees)
        total_cost = rental.monthly_cost + rental.late_fee
        
        player_gold = player.inventory.get('gold', 0)
        if player_gold < total_cost:
            return False, f"Need {total_cost} dubloons (have {player_gold})"
        
        # Pay rent
        player.inventory['gold'] -= total_cost
        rental.rent_due = False
        rental.rent_due_time = None
        rental.days_late = 0
        rental.late_fee = 0
        
        current_time = self.game_time.day_count if self.game_time else 0
        rental.last_payment_month = self.get_month_from_days(current_time)
        
        late_msg = f" (including {rental.late_fee} dubloons late fee)" if rental.late_fee > 0 else ""
        return True, f"Rent paid: {total_cost} dubloons{late_msg}"
    
    def evict_player(self, player, rental):
        """
        Evict player for non-payment
        
        Args:
            player: Player object
            rental: InnRental object
        """
        rental.evicted = True
        rental.storage_locked = True
        rental.rent_due = False
        
        current_time = self.game_time.day_count if self.game_time else 0
        rental.eviction_time = current_time
        
        self.rent_notifications.append(
            f"EVICTED from {rental.inn_name}! Storage locked. Pay {self.RE_RENTAL_FEE} dubloons to re-rent and access inventory."
        )
    
    def is_player_at_inn(self, player, inn_id):
        """Check if player is currently at the inn (simplified distance check)"""
        # In full implementation, check distance to inn building
        # For now, simplified check
        return False  # Will be implemented when integrated with town system
    
    def can_access_storage(self, player_name):
        """Check if player can access their inn storage"""
        if player_name not in self.rentals:
            return False, "Not renting a room"
        
        rental = self.rentals[player_name]
        if rental.storage_locked:
            return False, f"Storage locked due to eviction. Pay {self.RE_RENTAL_FEE} dubloons to re-rent."
        
        return True, "Storage accessible"
    
    def store_item(self, player_name, item_name, quantity):
        """Store item at inn"""
        can_access, reason = self.can_access_storage(player_name)
        if not can_access:
            return False, reason
        
        rental = self.rentals[player_name]
        if item_name not in rental.storage:
            rental.storage[item_name] = 0
        rental.storage[item_name] += quantity
        
        return True, f"Stored {quantity}x {item_name}"
    
    def retrieve_item(self, player_name, item_name, quantity):
        """Retrieve item from inn storage"""
        can_access, reason = self.can_access_storage(player_name)
        if not can_access:
            return False, reason
        
        rental = self.rentals[player_name]
        if item_name not in rental.storage or rental.storage[item_name] < quantity:
            return False, f"Not enough {item_name} in storage"
        
        rental.storage[item_name] -= quantity
        if rental.storage[item_name] == 0:
            del rental.storage[item_name]
        
        return True, f"Retrieved {quantity}x {item_name}"
    
    def get_rental_info(self, player_name):
        """Get rental information for player"""
        if player_name not in self.rentals:
            return None
        
        rental = self.rentals[player_name]
        current_time = self.game_time.day_count if self.game_time else 0
        
        info = {
            'inn_name': rental.inn_name,
            'monthly_cost': rental.monthly_cost,
            'rent_due': rental.rent_due,
            'days_late': rental.days_late,
            'late_fee': rental.late_fee,
            'evicted': rental.evicted,
            'storage_locked': rental.storage_locked,
            'storage_items': len(rental.storage),
            're_rental_fee': rental.re_rental_fee if rental.evicted else 0
        }
        
        return info
    
    def get_notifications(self):
        """Get and clear rent notifications"""
        notifications = self.rent_notifications.copy()
        self.rent_notifications.clear()
        return notifications
    
    def update(self, player):
        """Update rental system each frame"""
        self.check_rent_due(player)
    
    def to_dict(self):
        """Serialize all rentals"""
        return {
            'rentals': {
                player_name: rental.to_dict()
                for player_name, rental in self.rentals.items()
            }
        }
    
    def from_dict(self, data):
        """Deserialize all rentals"""
        rentals_data = data.get('rentals', {})
        for player_name, rental_data in rentals_data.items():
            self.rentals[player_name] = InnRental.from_dict(rental_data)

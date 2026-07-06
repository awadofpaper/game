"""
Insurance System
Handles property insurance for houses and items
"""

import time


class InsurancePolicy:
    """Represents an insurance policy"""
    
    def __init__(self, policy_id, owner_name, policy_type, purchase_time, duration_days, cost, coverage):
        """
        Initialize an insurance policy
        
        Args:
            policy_id: Unique identifier
            owner_name: Name of the policyholder
            policy_type: Type of insurance (e.g., "property")
            purchase_time: Game time when purchased (in days)
            duration_days: How long policy lasts (in days)
            cost: Cost of the policy
            coverage: Dict describing what's covered
        """
        self.policy_id = policy_id
        self.owner_name = owner_name
        self.policy_type = policy_type
        self.purchase_time = purchase_time
        self.duration_days = duration_days
        self.cost = cost
        self.coverage = coverage
        self.expiration_time = purchase_time + duration_days
        self.active = True
        self.claims_made = []  # List of claims filed
    
    def is_active(self, current_time):
        """Check if policy is still active"""
        return self.active and current_time < self.expiration_time
    
    def days_remaining(self, current_time):
        """Get days remaining on policy"""
        if not self.is_active(current_time):
            return 0
        return max(0, self.expiration_time - current_time)
    
    def file_claim(self, claim_type, claim_details, claim_time):
        """File an insurance claim"""
        claim = {
            'type': claim_type,
            'details': claim_details,
            'time': claim_time,
            'processed': False,
            'payout': 0
        }
        self.claims_made.append(claim)
        return claim
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'policy_id': self.policy_id,
            'owner_name': self.owner_name,
            'policy_type': self.policy_type,
            'purchase_time': self.purchase_time,
            'duration_days': self.duration_days,
            'cost': self.cost,
            'coverage': self.coverage,
            'expiration_time': self.expiration_time,
            'active': self.active,
            'claims_made': self.claims_made
        }
    
    @staticmethod
    def from_dict(data):
        """Deserialize from dictionary"""
        policy = InsurancePolicy(
            data['policy_id'],
            data['owner_name'],
            data['policy_type'],
            data['purchase_time'],
            data['duration_days'],
            data['cost'],
            data['coverage']
        )
        policy.expiration_time = data.get('expiration_time', policy.expiration_time)
        policy.active = data.get('active', True)
        policy.claims_made = data.get('claims_made', [])
        return policy


class InsuranceSystem:
    """Manages insurance policies and claims"""
    
    # Policy types and costs
    PROPERTY_INSURANCE_COST = 300  # Cost for 2 years of property insurance
    PROPERTY_INSURANCE_DURATION = 730  # 2 years = 730 days
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.policies = {}  # {player_name: [InsurancePolicy]}
        self.next_policy_id = 1
    
    def can_purchase_property_insurance(self, player):
        """
        Check if player can purchase property insurance
        
        Args:
            player: Player object
            
        Returns:
            tuple: (can_purchase: bool, reason: str)
        """
        # Check if player has enough money
        if not hasattr(player, 'inventory'):
            return False, "No inventory"
        
        player_gold = player.inventory.get('gold', 0)
        if player_gold < self.PROPERTY_INSURANCE_COST:
            return False, f"Need {self.PROPERTY_INSURANCE_COST} dubloons (have {player_gold})"
        
        # Check if player already has active property insurance
        player_name = player.name
        if player_name in self.policies:
            current_time = self.game_time.day_count if self.game_time else 0
            for policy in self.policies[player_name]:
                if policy.policy_type == "property" and policy.is_active(current_time):
                    days_left = policy.days_remaining(current_time)
                    return False, f"Already have active property insurance ({days_left} days remaining)"
        
        # Check if player owns property
        if not hasattr(player, 'owned_properties') or not player.owned_properties:
            return False, "Must own property to purchase insurance"
        
        return True, "Can purchase property insurance"
    
    def purchase_property_insurance(self, player):
        """
        Purchase property insurance for player
        
        Args:
            player: Player object
            
        Returns:
            tuple: (success: bool, message: str, policy: InsurancePolicy or None)
        """
        can_purchase, reason = self.can_purchase_property_insurance(player)
        if not can_purchase:
            return False, reason, None
        
        # Deduct cost
        player.inventory['gold'] -= self.PROPERTY_INSURANCE_COST
        
        # Create policy
        current_time = self.game_time.day_count if self.game_time else 0
        policy_id = f"PROP-{self.next_policy_id}"
        self.next_policy_id += 1
        
        coverage = {
            'rebuild_cost': 50000,  # 50K wood equivalent
            'items_covered': True,  # All items in house covered
            'fire': True,
            'destruction': True
        }
        
        policy = InsurancePolicy(
            policy_id,
            player.name,
            "property",
            current_time,
            self.PROPERTY_INSURANCE_DURATION,
            self.PROPERTY_INSURANCE_COST,
            coverage
        )
        
        # Store policy
        if player.name not in self.policies:
            self.policies[player.name] = []
        self.policies[player.name].append(policy)
        
        return True, f"Property insurance purchased! Policy: {policy_id} (Valid for 2 years)", policy
    
    def has_active_property_insurance(self, player_name):
        """Check if player has active property insurance"""
        if player_name not in self.policies:
            return False
        
        current_time = self.game_time.day_count if self.game_time else 0
        for policy in self.policies[player_name]:
            if policy.policy_type == "property" and policy.is_active(current_time):
                return True
        
        return False
    
    def get_active_property_policy(self, player_name):
        """Get active property insurance policy for player"""
        if player_name not in self.policies:
            return None
        
        current_time = self.game_time.day_count if self.game_time else 0
        for policy in self.policies[player_name]:
            if policy.policy_type == "property" and policy.is_active(current_time):
                return policy
        
        return None
    
    def file_property_claim(self, player_name, claim_details):
        """
        File a property insurance claim
        
        Args:
            player_name: Name of player filing claim
            claim_details: Details of the claim (what was lost)
            
        Returns:
            tuple: (success: bool, message: str, payout: dict or None)
        """
        policy = self.get_active_property_policy(player_name)
        if not policy:
            return False, "No active property insurance", None
        
        current_time = self.game_time.day_count if self.game_time else 0
        
        # Create claim
        claim = policy.file_claim("property_damage", claim_details, current_time)
        
        # Process claim immediately
        payout = {
            'wood': policy.coverage['rebuild_cost'],  # 50K wood
            'items': claim_details.get('lost_items', [])  # All lost items
        }
        
        claim['processed'] = True
        claim['payout'] = payout
        
        return True, "Insurance claim approved! Funds will be provided for rebuild.", payout
    
    def process_insurance_payout(self, player, payout):
        """
        Apply insurance payout to player
        
        Args:
            player: Player object
            payout: Payout dictionary from claim
            
        Returns:
            bool: Success
        """
        if not payout:
            return False
        
        # Add wood for rebuild
        if 'wood' in payout:
            if 'wood' not in player.inventory:
                player.inventory['wood'] = 0
            player.inventory['wood'] += payout['wood']
        
        # Restore lost items
        if 'items' in payout:
            for item_name, quantity in payout['items'].items():
                if item_name not in player.inventory:
                    player.inventory[item_name] = 0
                player.inventory[item_name] += quantity
        
        return True
    
    def get_all_policies(self, player_name):
        """Get all policies for a player"""
        return self.policies.get(player_name, [])
    
    def update(self):
        """Update insurance system each frame"""
        # Expire old policies
        current_time = self.game_time.day_count if self.game_time else 0
        
        for player_name, policies in self.policies.items():
            for policy in policies:
                if policy.active and current_time >= policy.expiration_time:
                    policy.active = False
    
    def to_dict(self):
        """Serialize all policies"""
        return {
            'policies': {
                player_name: [policy.to_dict() for policy in policies]
                for player_name, policies in self.policies.items()
            },
            'next_policy_id': self.next_policy_id
        }
    
    def from_dict(self, data):
        """Deserialize all policies"""
        self.next_policy_id = data.get('next_policy_id', 1)
        
        policies_data = data.get('policies', {})
        for player_name, policy_list in policies_data.items():
            self.policies[player_name] = [
                InsurancePolicy.from_dict(policy_data)
                for policy_data in policy_list
            ]

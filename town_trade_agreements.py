"""
Town Trade Agreement System
- Towns can strike trade agreements with each other
- Agreements provide bonuses (reduced prices, increased profits, exclusive goods)
- NPCs and players benefit from active agreements
- Agreements can expire or be renegotiated
- Diplomatic relationships affect agreement terms
"""

import random
from logger_config import logger


class TradeAgreementType:
    """Types of trade agreements"""
    TARIFF_REDUCTION = "tariff_reduction"  # -10% prices on all goods
    BULK_DISCOUNT = "bulk_discount"        # Bonus on large transactions
    EXCLUSIVE_GOODS = "exclusive_goods"     # Access to rare items
    PROFIT_SHARING = "profit_sharing"       # Both towns share profits
    RESOURCE_PRIORITY = "resource_priority" # Priority access to resources


class TradeAgreement:
    """Agreement between two towns"""
    
    def __init__(self, town_a, town_b, agreement_type, duration_days=30):
        self.town_a = town_a
        self.town_b = town_b
        self.agreement_type = agreement_type
        self.duration_days = duration_days
        self.start_day = None
        self.active = False
        
        # Benefits
        self.benefits = self._initialize_benefits()
        
        # Performance tracking
        self.trade_volume = 0
        self.total_savings = 0
        self.revenue_generated = 0
        
        # Negotiation
        self.negotiated_by = None  # NPC or player who negotiated
        self.renewal_count = 0
    
    def _initialize_benefits(self):
        """Initialize benefits based on agreement type"""
        benefits = {}
        
        if self.agreement_type == TradeAgreementType.TARIFF_REDUCTION:
            benefits['price_discount'] = 0.10  # 10% discount
            benefits['applies_to'] = 'all_goods'
        
        elif self.agreement_type == TradeAgreementType.BULK_DISCOUNT:
            benefits['bulk_threshold'] = 10  # Buy 10+ items
            benefits['bulk_discount'] = 0.15  # 15% discount
        
        elif self.agreement_type == TradeAgreementType.EXCLUSIVE_GOODS:
            benefits['unlocked_items'] = ['rare_herb', 'exotic_spice', 'fine_cloth']
            benefits['price_modifier'] = 0.9  # 10% cheaper
        
        elif self.agreement_type == TradeAgreementType.PROFIT_SHARING:
            benefits['profit_share'] = 0.05  # 5% of profits shared
            benefits['revenue_bonus'] = 1.10  # 10% more revenue
        
        elif self.agreement_type == TradeAgreementType.RESOURCE_PRIORITY:
            benefits['supply_bonus'] = 1.20  # 20% more resources available
            benefits['priority_items'] = ['iron_ore', 'wood', 'fish']
        
        return benefits
    
    def activate(self, start_day):
        """Activate the agreement"""
        self.active = True
        self.start_day = start_day
        logger.info(f"[TRADE AGREEMENT] Activated {self.agreement_type} between {self.town_a} and {self.town_b}")
    
    def is_expired(self, current_day):
        """Check if agreement has expired"""
        if not self.active or self.start_day is None:
            return False
        
        return (current_day - self.start_day) >= self.duration_days
    
    def extend(self, additional_days):
        """Extend the agreement duration"""
        self.duration_days += additional_days
        self.renewal_count += 1
        logger.info(f"[TRADE AGREEMENT] Extended agreement between {self.town_a} and {self.town_b} by {additional_days} days")
    
    def applies_to_route(self, origin_town, dest_town):
        """Check if agreement applies to a trade route"""
        return (origin_town == self.town_a and dest_town == self.town_b) or \
               (origin_town == self.town_b and dest_town == self.town_a)
    
    def get_price_modifier(self, quantity=1):
        """Get price modifier based on agreement benefits"""
        if not self.active:
            return 1.0
        
        if self.agreement_type == TradeAgreementType.TARIFF_REDUCTION:
            return 1.0 - self.benefits['price_discount']
        
        elif self.agreement_type == TradeAgreementType.BULK_DISCOUNT:
            if quantity >= self.benefits['bulk_threshold']:
                return 1.0 - self.benefits['bulk_discount']
        
        elif self.agreement_type == TradeAgreementType.EXCLUSIVE_GOODS:
            return self.benefits['price_modifier']
        
        return 1.0
    
    def record_trade(self, value):
        """Record a trade that benefited from this agreement"""
        self.trade_volume += value
        
        # Calculate savings
        if self.agreement_type == TradeAgreementType.TARIFF_REDUCTION:
            savings = value * self.benefits['price_discount']
            self.total_savings += savings
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'town_a': self.town_a,
            'town_b': self.town_b,
            'type': self.agreement_type,
            'active': self.active,
            'duration_days': self.duration_days,
            'days_remaining': max(0, self.duration_days - (0 if not self.start_day else 0)),
            'trade_volume': self.trade_volume,
            'total_savings': self.total_savings,
            'benefits': self.benefits
        }


class TownDiplomacy:
    """Manages diplomatic relationships between towns"""
    
    def __init__(self):
        # Relationship scores {(town_a, town_b): score}
        # Score: 0 = hostile, 50 = neutral, 100 = allied
        self.relationships = {}
        
        # Historical interactions
        self.interaction_history = []
    
    def get_relationship(self, town_a, town_b):
        """Get relationship score between two towns"""
        key = tuple(sorted([town_a, town_b]))
        return self.relationships.get(key, 50)  # Default: neutral
    
    def set_relationship(self, town_a, town_b, score):
        """Set relationship score"""
        key = tuple(sorted([town_a, town_b]))
        self.relationships[key] = max(0, min(100, score))
    
    def modify_relationship(self, town_a, town_b, change):
        """Modify relationship score"""
        current = self.get_relationship(town_a, town_b)
        new_score = current + change
        self.set_relationship(town_a, town_b, new_score)
        
        logger.info(f"[DIPLOMACY] {town_a} <-> {town_b} relationship: {current} -> {new_score}")
    
    def record_interaction(self, town_a, town_b, interaction_type, impact):
        """Record diplomatic interaction"""
        self.interaction_history.append({
            'towns': (town_a, town_b),
            'type': interaction_type,
            'impact': impact,
            'timestamp': None  # Will be set by game time
        })
        
        # Limit history size
        if len(self.interaction_history) > 100:
            self.interaction_history.pop(0)
    
    def can_negotiate_agreement(self, town_a, town_b):
        """Check if towns can negotiate a trade agreement"""
        relationship = self.get_relationship(town_a, town_b)
        
        # Need at least neutral relationship (40+)
        return relationship >= 40
    
    def get_agreement_quality(self, town_a, town_b):
        """Determine quality of potential agreement based on relationship"""
        relationship = self.get_relationship(town_a, town_b)
        
        if relationship >= 80:
            return "excellent"  # Best terms, longest duration
        elif relationship >= 60:
            return "good"       # Good terms, normal duration
        elif relationship >= 40:
            return "fair"       # Basic terms, shorter duration
        else:
            return "poor"       # Cannot negotiate


class TownTradeAgreementSystem:
    """Central system managing all trade agreements between towns"""
    
    def __init__(self, town_manager, game_time):
        self.town_manager = town_manager
        self.game_time = game_time
        
        # All active agreements
        self.agreements = []
        
        # Diplomacy system
        self.diplomacy = TownDiplomacy()
        
        # NPC negotiators
        self.npc_negotiators = []
        
        logger.info("[TRADE AGREEMENTS] System initialized")
    
    def initialize_relationships(self):
        """Initialize diplomatic relationships between all towns"""
        towns = self.town_manager.towns
        
        for i, town_a in enumerate(towns):
            for town_b in towns[i+1:]:
                # Start with neutral to slightly positive relationships
                initial_score = random.randint(45, 65)
                self.diplomacy.set_relationship(town_a.name, town_b.name, initial_score)
        
        logger.info(f"[TRADE AGREEMENTS] Initialized relationships for {len(towns)} towns")
    
    def propose_agreement(self, town_a_name, town_b_name, agreement_type, proposer_id=None):
        """Propose a trade agreement between two towns"""
        # Check if relationship allows negotiation
        if not self.diplomacy.can_negotiate_agreement(town_a_name, town_b_name):
            return False, "Towns have poor relations - cannot negotiate agreement"
        
        # Check if agreement already exists
        for agreement in self.agreements:
            if agreement.applies_to_route(town_a_name, town_b_name) and agreement.active:
                return False, "Active agreement already exists between these towns"
        
        # Determine agreement quality and duration
        quality = self.diplomacy.get_agreement_quality(town_a_name, town_b_name)
        
        duration_map = {
            "excellent": random.randint(60, 90),
            "good": random.randint(30, 60),
            "fair": random.randint(15, 30),
            "poor": 0
        }
        
        duration = duration_map.get(quality, 30)
        
        if duration == 0:
            return False, "Relationship too poor to establish agreement"
        
        # Create agreement
        agreement = TradeAgreement(town_a_name, town_b_name, agreement_type, duration)
        agreement.negotiated_by = proposer_id
        agreement.activate(self.game_time.day_count)
        
        self.agreements.append(agreement)
        
        # Improve relationship from successful negotiation
        self.diplomacy.modify_relationship(town_a_name, town_b_name, 5)
        self.diplomacy.record_interaction(town_a_name, town_b_name, "agreement_signed", "positive")
        
        logger.info(f"[TRADE AGREEMENT] Established {agreement_type} between {town_a_name} and {town_b_name}")
        return True, f"Agreement established! Duration: {duration} days, Quality: {quality}"
    
    def get_active_agreement(self, town_a_name, town_b_name):
        """Get active agreement between two towns"""
        for agreement in self.agreements:
            if agreement.applies_to_route(town_a_name, town_b_name) and agreement.active:
                return agreement
        return None
    
    def calculate_trade_bonus(self, origin_town, dest_town, base_price, quantity=1):
        """Calculate price after applying trade agreement bonuses"""
        agreement = self.get_active_agreement(origin_town, dest_town)
        
        if not agreement:
            return base_price, 0
        
        # Apply price modifier
        modifier = agreement.get_price_modifier(quantity)
        final_price = base_price * modifier
        savings = base_price - final_price
        
        # Record trade in agreement
        agreement.record_trade(base_price)
        
        return final_price, savings
    
    def update_daily(self):
        """Daily update for trade agreements"""
        current_day = self.game_time.day_count
        
        # Check for expired agreements
        for agreement in self.agreements[:]:
            if agreement.is_expired(current_day):
                agreement.active = False
                logger.info(f"[TRADE AGREEMENT] Expired: {agreement.agreement_type} between {agreement.town_a} and {agreement.town_b}")
                
                # Chance to auto-renew if successful
                if agreement.trade_volume > 5000:  # Successful agreement
                    if random.random() < 0.7:  # 70% chance to renew
                        agreement.extend(agreement.duration_days)
                        agreement.activate(current_day)
                        self.diplomacy.modify_relationship(agreement.town_a, agreement.town_b, 3)
        
        # NPCs propose new agreements
        self._npc_propose_agreements()
    
    def _npc_propose_agreements(self):
        """NPCs randomly propose trade agreements"""
        if random.random() > 0.05:  # 5% chance per day
            return
        
        towns = self.town_manager.towns
        if len(towns) < 2:
            return
        
        # Pick two random towns
        town_a = random.choice(towns)
        town_b = random.choice([t for t in towns if t != town_a])
        
        # Check if they can negotiate
        if not self.diplomacy.can_negotiate_agreement(town_a.name, town_b.name):
            return
        
        # Check if agreement already exists
        if self.get_active_agreement(town_a.name, town_b.name):
            return
        
        # Pick random agreement type
        agreement_types = [
            TradeAgreementType.TARIFF_REDUCTION,
            TradeAgreementType.BULK_DISCOUNT,
            TradeAgreementType.EXCLUSIVE_GOODS,
            TradeAgreementType.PROFIT_SHARING,
            TradeAgreementType.RESOURCE_PRIORITY
        ]
        
        agreement_type = random.choice(agreement_types)
        
        # Propose (NPC negotiator ID would be set here)
        self.propose_agreement(town_a.name, town_b.name, agreement_type, proposer_id="NPC_AUTO")
    
    def get_all_agreements(self):
        """Get all agreements (active and expired)"""
        return [agreement.to_dict() for agreement in self.agreements]
    
    def get_active_agreements(self):
        """Get only active agreements"""
        return [agreement.to_dict() for agreement in self.agreements if agreement.active]
    
    def get_agreements_for_town(self, town_name):
        """Get all agreements involving a specific town"""
        return [
            agreement.to_dict() for agreement in self.agreements 
            if (agreement.town_a == town_name or agreement.town_b == town_name) and agreement.active
        ]
    
    def get_statistics(self):
        """Get system statistics"""
        active_count = sum(1 for a in self.agreements if a.active)
        total_savings = sum(a.total_savings for a in self.agreements)
        total_volume = sum(a.trade_volume for a in self.agreements)
        
        return {
            'active_agreements': active_count,
            'total_agreements': len(self.agreements),
            'total_savings': total_savings,
            'total_trade_volume': total_volume,
            'avg_relationship': sum(self.diplomacy.relationships.values()) / max(1, len(self.diplomacy.relationships))
        }


class NPCDiplomat:
    """NPC that negotiates trade agreements"""
    
    def __init__(self, npc, home_town):
        self.npc = npc
        self.home_town = home_town
        self.successful_negotiations = 0
        self.failed_negotiations = 0
        self.last_negotiation_day = 0
        
        # Negotiation skill
        self.negotiation_skill = random.uniform(0.3, 1.0)
    
    def should_negotiate(self, game_time):
        """Check if NPC should attempt to negotiate"""
        if game_time.day_count - self.last_negotiation_day < 14:  # Wait 2 weeks between attempts
            return False
        
        # Chance based on skill
        return random.random() < (self.negotiation_skill * 0.2)
    
    def attempt_negotiation(self, trade_agreement_system, town_manager, game_time):
        """Attempt to negotiate a trade agreement"""
        if not self.should_negotiate(game_time):
            return
        
        # Pick target town (not home town)
        towns = [t for t in town_manager.towns if t.name != self.home_town]
        if not towns:
            return
        
        target_town = random.choice(towns)
        
        # Pick agreement type based on what would benefit home town
        agreement_type = self._choose_best_agreement_type()
        
        # Attempt to propose
        success, message = trade_agreement_system.propose_agreement(
            self.home_town,
            target_town.name,
            agreement_type,
            proposer_id=id(self.npc)
        )
        
        self.last_negotiation_day = game_time.day_count
        
        if success:
            self.successful_negotiations += 1
            logger.info(f"[DIPLOMAT] {self.npc.name} successfully negotiated agreement with {target_town.name}")
        else:
            self.failed_negotiations += 1
    
    def _choose_best_agreement_type(self):
        """Choose most beneficial agreement type"""
        # Weighted selection based on common needs
        types = [
            (TradeAgreementType.TARIFF_REDUCTION, 0.3),
            (TradeAgreementType.BULK_DISCOUNT, 0.2),
            (TradeAgreementType.EXCLUSIVE_GOODS, 0.15),
            (TradeAgreementType.PROFIT_SHARING, 0.20),
            (TradeAgreementType.RESOURCE_PRIORITY, 0.15)
        ]
        
        return random.choices([t[0] for t in types], weights=[t[1] for t in types])[0]

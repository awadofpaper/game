"""
NPC Contract System
- NPCs can fulfill ResourceContracts from trade_route_system
- NPCs compete with players for profitable contracts
- NPCs deliver gathered resources to fulfill contracts
- Contract completion affects NPC reputation and wealth
"""

import random
from logger_config import logger


class NPCContractor:
    """NPC that fulfills resource contracts"""
    
    def __init__(self, npc):
        self.npc = npc
        self.active_contracts = []  # Contracts currently working on
        self.completed_contracts = 0
        self.failed_contracts = 0
        self.total_contract_earnings = 0
        
        # Contract preferences
        self.preferred_resource = self._determine_preferred_resource()
        self.min_profit_margin = random.uniform(0.15, 0.35)  # Won't take contract unless 15-35% profit
        self.max_active_contracts = 2
        
    def _determine_preferred_resource(self):
        """Determine which resources NPC prefers based on their type"""
        if hasattr(self.npc, 'gatherer_type'):
            type_map = {
                'miner': ['iron_ore', 'coal', 'gold_ore', 'ore'],
                'woodcutter': ['wood', 'oak', 'willow', 'yew'],
                'fisher': ['fish', 'raw_shrimp', 'raw_sardine', 'raw_salmon']
            }
            return type_map.get(self.npc.gatherer_type, [])
        return []
    
    def can_accept_contract(self):
        """Check if NPC can accept a new contract"""
        return len(self.active_contracts) < self.max_active_contracts
    
    def is_contract_suitable(self, contract):
        """Check if contract matches NPC's capabilities"""
        # Check if resource type matches NPC's specialty
        if self.preferred_resource:
            if contract.resource_type not in self.preferred_resource:
                return False
        
        # Check if NPC has or can gather the required resources
        return True
    
    def calculate_contract_profitability(self, contract, market_price):
        """Calculate if contract is profitable"""
        if market_price == 0:
            return 0.0
        
        # Profit margin = (contract_price - market_price) / market_price
        profit_margin = (contract.price_per_unit - market_price) / market_price
        return profit_margin
    
    def evaluate_contract(self, contract, market_price=None):
        """Evaluate if NPC should accept a contract"""
        if not self.can_accept_contract():
            return False, "Already at max contracts"
        
        if not self.is_contract_suitable(contract):
            return False, "Resource type doesn't match specialty"
        
        # Check profitability
        if market_price:
            profit_margin = self.calculate_contract_profitability(contract, market_price)
            if profit_margin < self.min_profit_margin:
                return False, f"Not profitable enough ({profit_margin * 100:.1f}% < {self.min_profit_margin * 100:.1f}%)"
        
        # Check deadline is reasonable
        if contract.deadline_days < 7:
            return False, "Deadline too tight"
        
        return True, "Contract acceptable"
    
    def accept_contract(self, contract):
        """Accept a contract"""
        self.active_contracts.append(contract)
        logger.info(f"[CONTRACT] {self.npc.name} accepted contract {contract.contract_id}")
    
    def can_fulfill_contract(self, contract):
        """Check if NPC has resources to fulfill contract"""
        if not hasattr(self.npc, 'inventory'):
            return False, 0
        
        available = self.npc.inventory.get(contract.resource_type, 0)
        can_deliver = min(available, contract.quantity - contract.delivered_quantity)
        
        return can_deliver > 0, can_deliver
    
    def attempt_fulfillment(self, contract, trade_route_system):
        """Attempt to fulfill a contract"""
        can_fulfill, quantity = self.can_fulfill_contract(contract)
        
        if not can_fulfill:
            return False, 0, "No resources available"
        
        # Remove resources from NPC inventory
        self.npc.inventory[contract.resource_type] -= quantity
        if self.npc.inventory[contract.resource_type] <= 0:
            del self.npc.inventory[contract.resource_type]
        
        # Deliver to contract
        delivered = contract.deliver(quantity)
        
        # Calculate payment
        payment = delivered * contract.price_per_unit
        
        # Pay NPC
        if hasattr(self.npc, 'dubloons'):
            self.npc.dubloons += payment
            self.total_contract_earnings += payment
        
        # Check if contract completed
        if contract.status == "completed":
            self.active_contracts.remove(contract)
            self.completed_contracts += 1
            logger.info(f"[CONTRACT] {self.npc.name} completed contract {contract.contract_id} for {payment}g")
            return True, payment, f"Contract completed! Earned {payment}g"
        else:
            logger.info(f"[CONTRACT] {self.npc.name} delivered {delivered} units for {payment}g ({contract.get_completion_percentage()}% complete)")
            return True, payment, f"Delivered {delivered} units for {payment}g"


class NPCContractSystem:
    """Central system managing NPC contract participation"""
    
    def __init__(self, trade_route_system):
        self.trade_route_system = trade_route_system
        self.npc_contractors = {}  # {npc_id: NPCContractor}
        
        # Statistics
        self.total_npc_contract_earnings = 0
        self.contracts_completed_by_npcs = 0
        
        logger.info("[NPC CONTRACTS] System initialized")
    
    def register_npc(self, npc):
        """Register an NPC as a potential contractor"""
        npc_id = id(npc)
        if npc_id not in self.npc_contractors:
            self.npc_contractors[npc_id] = NPCContractor(npc)
            logger.info(f"[NPC CONTRACTS] Registered {npc.name} as contractor")
    
    def update_daily(self, game_time):
        """Daily update - NPCs check and accept new contracts"""
        if not hasattr(self.trade_route_system, 'contracts'):
            return
        
        # Get available contracts
        available_contracts = [c for c in self.trade_route_system.contracts if c.status == "active"]
        
        if not available_contracts:
            return
        
        # Each NPC evaluates contracts
        for npc_id, contractor in self.npc_contractors.items():
            if not contractor.can_accept_contract():
                continue
            
            # Random chance to check contracts (30% per day)
            if random.random() > 0.3:
                continue
            
            # Evaluate each contract
            for contract in available_contracts:
                # Skip if already working on this contract
                if contract in contractor.active_contracts:
                    continue
                
                # Evaluate
                acceptable, reason = contractor.evaluate_contract(contract, market_price=20)
                
                if acceptable:
                    contractor.accept_contract(contract)
                    break  # Only accept one per update
    
    def update_fulfillment(self, game_time):
        """Update NPCs attempting to fulfill their contracts"""
        for npc_id, contractor in list(self.npc_contractors.items()):
            # Check each active contract
            for contract in contractor.active_contracts[:]:
                # Check if contract expired
                if contract.is_expired(game_time.day_count):
                    contractor.active_contracts.remove(contract)
                    contractor.failed_contracts += 1
                    logger.warning(f"[CONTRACT] {contractor.npc.name} failed to complete contract {contract.contract_id} (expired)")
                    continue
                
                # Try to fulfill
                can_fulfill, quantity = contractor.can_fulfill_contract(contract)
                
                if can_fulfill:
                    # Attempt fulfillment
                    success, payment, message = contractor.attempt_fulfillment(contract, self.trade_route_system)
                    
                    if success:
                        self.total_npc_contract_earnings += payment
                        
                        if contract.status == "completed":
                            self.contracts_completed_by_npcs += 1
    
    def get_npc_contract_info(self, npc):
        """Get contract information for an NPC"""
        npc_id = id(npc)
        if npc_id not in self.npc_contractors:
            return None
        
        contractor = self.npc_contractors[npc_id]
        
        return {
            'active_contracts': len(contractor.active_contracts),
            'completed': contractor.completed_contracts,
            'failed': contractor.failed_contracts,
            'total_earnings': contractor.total_contract_earnings,
            'preferred_resources': contractor.preferred_resource
        }
    
    def get_statistics(self):
        """Get system statistics"""
        total_active = sum(len(c.active_contracts) for c in self.npc_contractors.values())
        total_completed = sum(c.completed_contracts for c in self.npc_contractors.values())
        total_failed = sum(c.failed_contracts for c in self.npc_contractors.values())
        
        return {
            'registered_contractors': len(self.npc_contractors),
            'active_contracts': total_active,
            'completed_contracts': total_completed,
            'failed_contracts': total_failed,
            'total_earnings': self.total_npc_contract_earnings
        }
    
    def get_contract_competition(self, contract):
        """Get list of NPCs competing for a contract"""
        competitors = []
        
        for npc_id, contractor in self.npc_contractors.items():
            if contract in contractor.active_contracts:
                competitors.append(contractor.npc.name)
        
        return competitors


class ContractBoard:
    """Public board displaying available contracts for players and NPCs"""
    
    def __init__(self, trade_route_system):
        self.trade_route_system = trade_route_system
    
    def get_available_contracts(self):
        """Get all available contracts"""
        if not hasattr(self.trade_route_system, 'contracts'):
            return []
        
        return [c for c in self.trade_route_system.contracts if c.status == "active"]
    
    def get_contract_details(self, contract):
        """Get detailed information about a contract"""
        return {
            'contract_id': contract.contract_id,
            'resource': contract.resource_type,
            'quantity': contract.quantity,
            'delivered': contract.delivered_quantity,
            'price_per_unit': contract.price_per_unit,
            'total_value': contract.total_value,
            'deadline_days': contract.deadline_days,
            'created_day': contract.created_day,
            'completion_percentage': contract.get_completion_percentage(),
            'supplier_town': contract.supplier_town,
            'buyer_town': contract.buyer_town,
            'status': contract.status
        }
    
    def get_high_value_contracts(self, min_value=1000):
        """Get contracts worth more than specified value"""
        contracts = self.get_available_contracts()
        return [c for c in contracts if c.total_value >= min_value]
    
    def get_contracts_for_resource(self, resource_type):
        """Get all contracts for a specific resource"""
        contracts = self.get_available_contracts()
        return [c for c in contracts if c.resource_type == resource_type]
    
    def get_urgent_contracts(self, days_threshold=7):
        """Get contracts expiring soon"""
        from game_time import GameTime
        contracts = self.get_available_contracts()
        urgent = []
        
        for contract in contracts:
            if contract.created_day is not None:
                # Calculate days remaining
                # This would need actual current_day from game_time
                # For now, mark contracts with short deadlines
                if contract.deadline_days <= days_threshold:
                    urgent.append(contract)
        
        return urgent


class ContractNotificationSystem:
    """Notifies players and NPCs of new contracts"""
    
    def __init__(self):
        self.last_contract_count = 0
        self.new_contract_notifications = []
    
    def check_new_contracts(self, trade_route_system):
        """Check for new contracts and create notifications"""
        if not hasattr(trade_route_system, 'contracts'):
            return []
        
        current_count = len(trade_route_system.contracts)
        
        if current_count > self.last_contract_count:
            # New contract(s) added
            new_contracts = trade_route_system.contracts[self.last_contract_count:]
            
            for contract in new_contracts:
                notification = f"New Contract: Deliver {contract.quantity}x {contract.resource_type} to {contract.buyer_town} for {contract.total_value}g"
                self.new_contract_notifications.append(notification)
                logger.info(f"[CONTRACT NOTIFICATION] {notification}")
        
        self.last_contract_count = current_count
        return self.new_contract_notifications[:]
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.new_contract_notifications.clear()

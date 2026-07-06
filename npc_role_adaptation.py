"""
NPC Role Adaptation System
NPCs dynamically adapt to world changes - change careers, move towns, open shops, take over vacant roles
Creates organic world evolution as NPCs die and opportunities arise
"""

import random
import math


class NPCOpportunity:
    """Represents an opportunity for an NPC to change roles"""
    
    def __init__(self, opportunity_type, description, location, requirements, reward):
        self.opportunity_type = opportunity_type  # 'caravan', 'shop', 'move', 'skill_change'
        self.description = description
        self.location = location # Town or position
        self.requirements = requirements  # Dict of required stats/money
        self.reward = reward  # Potential income or benefit
        self.claimed = False
        self.created_time = 0
    
    def is_qualified(self, npc):
        """Check if NPC meets requirements for this opportunity"""
        # Check money requirement
        if 'money' in self.requirements:
            if getattr(npc, 'dubloons', 0) < self.requirements['money']:
                return False
        
        # Check level requirement
        if 'level' in self.requirements:
            if getattr(npc, 'level', 0) < self.requirements['level']:
                return False
        
        # Check skill requirements
        if 'skills' in self.requirements:
            if hasattr(npc, 'skills_manager'):
                for skill, min_level in self.requirements['skills'].items():
                    if npc.skills_manager.get_skill_level(skill) < min_level:
                        return False
        
        return True


class NPCRoleAdaptationSystem:
    """
    Manages dynamic NPC role changes
    NPCs can change careers, move towns, open shops, take over vacant positions
    """
    
    def __init__(self):
        self.opportunities = []  # List of available opportunities
        self.role_changes = []  # History of role changes
        self.vacant_roles = []  # Roles left vacant by death
        
    def register_vacant_role(self, role_type, location, reason="death"):
        """
        Register a vacant role (usually due to NPC death)
        """
        opportunity = {
            'role_type': role_type,
            'location': location,
            'reason': reason,
            'registered_time': 0
        }
        self.vacant_roles.append(opportunity)
        print(f"[ADAPTATION] Vacant role registered: {role_type} at {location.name if hasattr(location, 'name') else 'location'}")
    
    def create_caravan_opportunity(self, start_town, dead_caravan_npc=None):
        """
        Create opportunity for NPC to become traveling merchant
        Usually triggered when a caravan NPC dies
        """
        requirements = {
            'money': 1000,  # Need starting capital
            'level': 10
        }
        
        description = f"Take over caravan route from {start_town.name}"
        if dead_caravan_npc:
            description = f"Take over {dead_caravan_npc.name}'s caravan business"
        
        opportunity = NPCOpportunity(
            opportunity_type='caravan',
            description=description,
            location=start_town,
            requirements=requirements,
            reward={'income_potential': 500}  # Potential profit per cycle
        )
        
        self.opportunities.append(opportunity)
        print(f"[ADAPTATION] Caravan opportunity created at {start_town.name}")
        return opportunity
    
    def create_shop_opportunity(self, town, shop_type='general'):
        """
        Create opportunity for NPC to open a shop
        """
        requirements = {
            'money': 2000,  # Need capital to start shop
            'level': 15
        }
        
        opportunity = NPCOpportunity(
            opportunity_type='shop',
            description=f"Open {shop_type} shop in {town.name}",
            location=town,
            requirements=requirements,
            reward={'income_potential': 300}
        )
        
        self.opportunities.append(opportunity)
        print(f"[ADAPTATION] Shop opportunity created in {town.name}")
        return opportunity
    
    def create_skill_change_opportunity(self, npc, new_skill):
        """
        NPC wants to change profession (miner -> woodcutter, etc)
        """
        requirements = {
            'money': 100  # Cost of new tools
        }
        
        opportunity = NPCOpportunity(
            opportunity_type='skill_change',
            description=f"Become {new_skill}",
            location=npc.town if hasattr(npc, 'town') else None,
            requirements=requirements,
            reward={'new_skill': new_skill}
        )
        
        return opportunity
    
    def create_relocation_opportunity(self, npc, target_town, reason="better_opportunity"):
        """
        NPC wants to move to a different town
        """
        requirements = {
            'money': 300  # Moving costs
        }
        
        opportunity = NPCOpportunity(
            opportunity_type='relocation',
            description=f"Move to {target_town.name}",
            location=target_town,
            requirements=requirements,
            reward={'reason': reason}
        )
        
        return opportunity
    
    def evaluate_opportunities_for_npc(self, npc):
        """
        Check if NPC should pursue any available opportunities
        Returns best opportunity or None
        """
        if not npc.alive or npc.is_recovering:
            return None
        
        qualified_opportunities = []
        
        for opp in self.opportunities:
            if not opp.claimed and opp.is_qualified(npc):
                qualified_opportunities.append(opp)
        
        if not qualified_opportunities:
            return None
        
        # Choose best opportunity based on reward potential
        best_opp = max(qualified_opportunities, key=lambda o: o.reward.get('income_potential', 0))
        
        # Random chance to pursue (30% per check)
        if random.random() < 0.3:
            return best_opp
        
        return None
    
    def execute_role_change(self, npc, opportunity, game_time, npc_trade_engine=None, town_manager=None):
        """
        Execute role change for NPC
        """
        if not opportunity or opportunity.claimed:
            return False, "Opportunity not available"
        
        if not opportunity.is_qualified(npc):
            return False, "NPC not qualified"
        
        opportunity_type = opportunity.opportunity_type
        
        if opportunity_type == 'caravan':
            return self._execute_caravan_takeover(npc, opportunity, game_time, npc_trade_engine)
        
        elif opportunity_type == 'shop':
            return self._execute_shop_opening(npc, opportunity, game_time, town_manager)
        
        elif opportunity_type == 'skill_change':
            return self._execute_skill_change(npc, opportunity)
        
        elif opportunity_type == 'relocation':
            return self._execute_relocation(npc, opportunity, town_manager)
        
        return False, "Unknown opportunity type"
    
    def _execute_caravan_takeover(self, npc, opportunity, game_time, npc_trade_engine):
        """NPC becomes traveling merchant"""
        if not npc_trade_engine:
            return False, "Trading engine not available"
        
        # Remove from gatherer system
        npc.state = "retired"  # Mark as no longer gathering
        
        # Deduct starting costs
        cost = opportunity.requirements.get('money', 0)
        npc.dubloons -= cost
        
        # Spawn as traveling merchant
        from npc_trader_system import TravelingMerchantNPC
        new_merchant = TravelingMerchantNPC(
            name=f"{npc.name} (Merchant)",
            start_town=opportunity.location,
            config=npc.config if hasattr(npc, 'config') else None
        )
        
        # Transfer some wealth
        new_merchant.dubloons = npc.dubloons
        
        # Mark opportunity as claimed
        opportunity.claimed = True
        
        # Record role change
        self.role_changes.append({
            'npc': npc.name,
            'from': 'gatherer',
            'to': 'merchant',
            'time': game_time.total_hours if game_time else 0
        })
        
        print(f"[ADAPTATION] {npc.name} became a traveling merchant!")
        return True, f"{npc.name} is now a traveling merchant"
    
    def _execute_shop_opening(self, npc, opportunity, game_time, town_manager):
        """NPC opens a shop (placeholder - needs shop system integration)"""
        cost = opportunity.requirements.get('money', 0)
        npc.dubloons -= cost
        
        opportunity.claimed = True
        
        self.role_changes.append({
            'npc': npc.name,
            'from': 'gatherer',
            'to': 'shopkeeper',
            'location': opportunity.location.name if hasattr(opportunity.location, 'name') else 'unknown',
            'time': game_time.total_hours if game_time else 0
        })
        
        print(f"[ADAPTATION] {npc.name} opened a shop!")
        
        # Actually create shop in town
        if hasattr(self, 'shop_manager') and self.shop_manager:
            # Determine shop type from opportunity or NPC traits
            shop_type = opportunity.reward.get('shop_type', 'general')
            merchant_name = f"{npc.name}'s Shop"
            
            # Create the shop
            shop = self.shop_manager.create_shop(id(npc), merchant_name, shop_type)
            
            # Link NPC to shop
            npc.role = 'shopkeeper'
            npc.shop_id = id(npc)
            
            print(f"[ADAPTATION] Created {shop_type} shop for {npc.name}")
            return True, f"{npc.name} opened a {shop_type} shop: {merchant_name}"
        else:
            # Fallback: just change role
            npc.role = 'shopkeeper'
            return True, f"{npc.name} opened a shop"
    
    def _execute_skill_change(self, npc, opportunity):
        """NPC changes profession"""
        new_skill = opportunity.reward.get('new_skill')
        if not new_skill:
            return False, "No new skill specified"
        
        # Deduct tool costs
        cost = opportunity.requirements.get('money', 0)
        npc.dubloons -= cost
        
        # Change gatherer type
        old_type = npc.gatherer_type if hasattr(npc, 'gatherer_type') else 'unknown'
        
        from gatherer_npc import GathererType
        skill_map = {
            'mining': GathererType.MINER,
            'woodcutting': GathererType.WOODCUTTER,
            'fishing': GathererType.FISHER
        }
        
        if new_skill in skill_map:
            npc.gatherer_type = skill_map[new_skill]
            npc.tool = npc._get_starting_tool()
            
            self.role_changes.append({
                'npc': npc.name,
                'from': old_type,
                'to': new_skill,
                'type': 'skill_change'
            })
            
            print(f"[ADAPTATION] {npc.name} changed profession to {new_skill}")
            return True, f"{npc.name} is now a {new_skill}"
        
        return False, "Invalid skill"
    
    def _execute_relocation(self, npc, opportunity, town_manager):
        """NPC moves to different town"""
        cost = opportunity.requirements.get('money', 0)
        npc.dubloons -= cost
        
        old_town = npc.town if hasattr(npc, 'town') else None
        new_town = opportunity.location
        
        # Move NPC
        if new_town:
            npc.town = new_town
            npc.x = new_town.center_x + random.randint(-100, 100)
            npc.y = new_town.center_y + random.randint(-100, 100)
            npc.respawn_x = npc.x
            npc.respawn_y = npc.y
            
            # Find new bank
            npc.home_bank = npc.find_home_bank()
            
            self.role_changes.append({
                'npc': npc.name,
                'from': old_town.name if old_town else 'unknown',
                'to': new_town.name,
                'type': 'relocation'
            })
            
            print(f"[ADAPTATION] {npc.name} moved from {old_town.name if old_town else 'unknown'} to {new_town.name}")
            return True, f"{npc.name} moved to {new_town.name}"
        
        return False, "Invalid destination"
    
    def update_daily(self, all_npcs, game_time, npc_trade_engine=None, town_manager=None):
        """
        Daily update - check if NPCs want to pursue opportunities
        """
        changes_made = 0
        
        # Small random pool of NPCs check opportunities each day (5%)
        for npc in random.sample(all_npcs, min(len(all_npcs), max(1, len(all_npcs) // 20))):
            if not npc.alive or npc.is_recovering:
                continue
            
            # Check for opportunities
            best_opp = self.evaluate_opportunities_for_npc(npc)
            
            if best_opp:
                success, message = self.execute_role_change(
                    npc, best_opp, game_time, 
                    npc_trade_engine, town_manager
                )
                
                if success:
                    changes_made += 1
        
        # Occasionally create new random opportunities
        if random.random() < 0.1 and town_manager:  # 10% chance per day
            # Create shop opportunity in random town
            if town_manager.towns:
                random_town = random.choice(town_manager.towns)
                self.create_shop_opportunity(random_town)
        
        return changes_made
    
    def get_statistics(self):
        """Get adaptation statistics"""
        return {
            'available_opportunities': len([o for o in self.opportunities if not o.claimed]),
            'total_opportunities': len(self.opportunities),
            'role_changes': len(self.role_changes),
            'vacant_roles': len(self.vacant_roles)
        }
    
    def get_recent_changes(self, limit=10):
        """Get recent role changes"""
        return self.role_changes[-limit:]

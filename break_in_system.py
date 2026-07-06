"""
Building Break-In System
Handles burglary mechanics, loot generation, detection, and alarms
"""
import random
from crime_punishment_system import StolenItem

class BreakInSystem:
    """Manages breaking into closed buildings"""
    
    # Building security levels (lockpick difficulty)
    SECURITY_LEVELS = {
        'tavern': 20,
        'shop': 25,
        'blacksmith': 40,
        'temple': 35,
        'bank': 70,
        'bank_vault': 90,
        'town_hall': 50
    }
    
    # Crime penalties by building type
    CRIME_PENALTIES = {
        'shop': {'bounty': 100, 'jail_days': 10, 'rep_loss': -50},
        'blacksmith': {'bounty': 120, 'jail_days': 12, 'rep_loss': -60},
        'bank': {'bounty': 300, 'jail_days': 20, 'rep_loss': -100},
        'bank_vault': {'bounty': 500, 'jail_days': 30, 'rep_loss': -150},
        'tavern': {'bounty': 80, 'jail_days': 8, 'rep_loss': -40},
        'temple': {'bounty': 250, 'jail_days': 15, 'rep_loss': -200},
        'town_hall': {'bounty': 200, 'jail_days': 15, 'rep_loss': -120}
    }
    
    # Alarm chances (0-100%)
    ALARM_CHANCES = {
        'shop': 10,
        'blacksmith': 5,
        'bank': 60,
        'bank_vault': 90,
        'tavern': 0,
        'temple': 20,
        'town_hall': 40
    }
    
    def __init__(self):
        self.buildings_broken_into = {}  # Track which buildings have been hit
        self.active_alarms = {}  # {building_id: game_time when triggered}
        
    def get_lockpick_difficulty(self, building_type, is_vault_room=False):
        """Get lockpick difficulty for building type"""
        if is_vault_room:
            return self.SECURITY_LEVELS.get('bank_vault', 90)
        return self.SECURITY_LEVELS.get(building_type, 30)
    
    def get_detection_modifier(self, game_time):
        """
        Calculate detection chance modifier based on time of day
        Returns multiplier (0.5 = half chance, 2.0 = double chance)
        """
        hour, _ = game_time.get_time_hm()
        
        # Midnight to 5am: Very low detection (0.3x)
        if 0 <= hour < 5:
            return 0.3
        # 5am to 8am: Low detection (0.5x)
        elif 5 <= hour < 8:
            return 0.5
        # 8am to 6pm: High detection during business hours (1.5x)
        elif 8 <= hour < 18:
            return 1.5
        # 6pm to midnight: Medium detection (0.7x)
        else:
            return 0.7
    
    def check_for_witnesses(self, player_x, player_y, npc_manager, guard_npcs, current_town_name, game_time):
        """
        Check if any NPCs or guards witness the break-in attempt
        Returns (witnessed, witness_name, witness_type)
        """
        detection_modifier = self.get_detection_modifier(game_time)
        witness_range = int(200 * detection_modifier)  # Range affected by time of day
        
        # Check guard NPCs first (they're more alert)
        for guard in guard_npcs:
            if hasattr(guard, 'town') and guard.town == current_town_name:
                dx = abs(player_x - guard.x)
                dy = abs(player_y - guard.y)
                distance = (dx * dx + dy * dy) ** 0.5
                if distance < witness_range:
                    # Guards have higher detection chance
                    if random.random() < 0.8 * detection_modifier:
                        return True, guard.name, 'guard'
        
        # Check regular NPCs
        for npc in npc_manager.npcs:
            # Skip sleeping NPCs (nighttime)
            if game_time.is_npc_sleeping():
                continue
            
            dx = abs(player_x - npc.x)
            dy = abs(player_y - npc.y)
            distance = (dx * dx + dy * dy) ** 0.5
            if distance < witness_range:
                # Regular NPCs have lower detection chance
                if random.random() < 0.4 * detection_modifier:
                    return True, npc.name, 'npc'
        
        return False, None, None
    
    def check_alarm_triggered(self, building_type, lockpick_success):
        """
        Check if alarm is triggered during break-in
        More likely to trigger on failed lockpick attempts
        """
        base_chance = self.ALARM_CHANCES.get(building_type, 0)
        
        # Failed lockpicks are louder and more likely to trigger alarms
        if not lockpick_success:
            base_chance *= 2
        
        return random.random() * 100 < base_chance
    
    def trigger_alarm(self, building_id, game_time):
        """Trigger an alarm at a building"""
        self.active_alarms[building_id] = game_time.day_count
        
    def is_alarm_active(self, building_id, game_time):
        """Check if alarm is still active (alarms last 1 in-game day)"""
        if building_id not in self.active_alarms:
            return False
        days_since = game_time.day_count - self.active_alarms[building_id]
        return days_since < 1
    
    def generate_loot(self, building_type, building_name, player_inventory, is_vault_room=False):
        """
        Generate loot for successful break-in
        Returns (gold_amount, items_list, total_value)
        """
        gold = 0
        items = []
        
        if building_type == 'shop':
            # Cash register + random shop items
            gold = random.randint(50, 200)
            
            # Random potions/items (better loot variety)
            possible_items = [
                ('health_potion', random.randint(2, 5)),
                ('mana_potion', random.randint(1, 3)),
                ('stamina_potion', random.randint(1, 3)),
                ('lockpick', random.randint(1, 2)),  # Ironic - steal lockpicks
                ('rope', random.randint(1, 2)),
                ('torch', random.randint(2, 4)),
            ]
            items = random.sample(possible_items, random.randint(2, 4))
            
        elif building_type == 'blacksmith':
            # Less gold, but valuable equipment and materials
            gold = random.randint(30, 100)
            
            # Equipment and materials  
            possible_items = [
                ('iron_ore', random.randint(5, 12)),
                ('steel_ingot', random.randint(3, 8)),
                ('repair_kit', random.randint(2, 4)),
                ('iron_sword', 1),  # Chance of weapon
                ('iron_armor', 1),
                ('steel_sword', 1),
            ]
            # Higher chance of materials, lower for weapons
            items = random.sample(possible_items[:3], random.randint(2, 3))
            if random.random() < 0.3:  # 30% chance of weapon
                items.append(random.choice(possible_items[3:]))
            
        elif building_type == 'bank':
            if is_vault_room:
                # Vault room has massive loot
                gold = random.randint(1000, 2500)
                # Rare chance of finding deposited valuables
                possible_items = [
                    ('diamond', random.randint(1, 3)),
                    ('ruby', random.randint(2, 5)),
                    ('gold_bar', random.randint(1, 2)),
                ]
                if random.random() < 0.5:  # 50% chance of gems
                    items = random.sample(possible_items, random.randint(1, 2))
            else:
                # Teller area has moderate gold
                gold = random.randint(500, 1200)
                # Might find some paperwork
                if random.random() < 0.3:
                    items = [('bank_records', 1)]
            
        elif building_type == 'tavern':
            # Small cash + food/drink
            gold = random.randint(30, 80)
            
            possible_items = [
                ('ale', random.randint(4, 8)),
                ('wine', random.randint(2, 4)),
                ('bread', random.randint(3, 6)),
                ('cheese', random.randint(2, 5)),
                ('cooked_meat', random.randint(1, 3)),
            ]
            items = random.sample(possible_items, random.randint(2, 4))
            
        elif building_type == 'temple':
            # Donation box money (moral choice! Big reputation hit)
            gold = random.randint(80, 200)
            
            # Rare chance of finding holy items
            if random.random() < 0.2:  # 20% chance
                items = [('holy_relic', 1)]  # Could be valuable or cursed!
            
        elif building_type == 'town_hall':
            # Town treasury
            gold = random.randint(300, 600)
            
            # Always find town records (useful for blackmail/quests)
            possible_items = [
                ('town_records', 1),
                ('tax_ledger', 1),
                ('election_documents', 1),
            ]
            items = random.sample(possible_items, random.randint(1, 2))
        
        # Mark all items as stolen
        stolen_items = []
        for item_name, quantity in items:
            for _ in range(quantity):
                stolen_item = StolenItem(id(item_name), item_name)
                stolen_items.append(stolen_item)
                # Add to player inventory
                current = player_inventory.get(item_name, 0)
                player_inventory[item_name] = current + 1
        
        total_value = gold + sum(self._estimate_item_value(name) * qty for name, qty in items)
        
        return gold, stolen_items, total_value
    
    def _estimate_item_value(self, item_name):
        """Estimate gold value of an item"""
        values = {
            'health_potion': 20,
            'mana_potion': 25,
            'stamina_potion': 15,
            'iron_ore': 10,
            'steel_ingot': 30,
            'repair_kit': 40,
            'ale': 5,
            'wine': 12,
            'bread': 3,
            'cheese': 8,
            'cooked_meat': 15,
            'town_records': 100,
            'bank_records': 80,
            'tax_ledger': 120,
            'election_documents': 150,
            'lockpick': 25,
            'rope': 10,
            'torch': 5,
            'iron_sword': 100,
            'iron_armor': 120,
            'steel_sword': 200,
            'diamond': 500,
            'ruby': 300,
            'gold_bar': 400,
            'holy_relic': 250,
        }
        return values.get(item_name, 10)
    
    def get_penalty_info(self, building_type, is_vault_room=False):
        """Get crime penalties for breaking into building"""
        key = 'bank_vault' if is_vault_room else building_type
        return self.CRIME_PENALTIES.get(key, {
            'bounty': 100,
            'jail_days': 10,
            'rep_loss': -50
        })
    
    def mark_building_hit(self, building_id, game_time):
        """Mark that a building has been broken into"""
        self.buildings_broken_into[building_id] = game_time.day_count
    
    def was_recently_hit(self, building_id, game_time, days=7):
        """Check if building was broken into recently"""
        if building_id not in self.buildings_broken_into:
            return False
        days_since = game_time.day_count - self.buildings_broken_into[building_id]
        return days_since < days


class FencingSystem:
    """Manages selling stolen goods to black market fences"""
    
    def __init__(self):
        self.fence_locations = {}  # {town_name: (x, y)}
        self.fence_discovered = {}  # {town_name: bool}
        
    def discover_fence(self, town_name, x, y):
        """Player discovers a fence location"""
        self.fence_locations[town_name] = (x, y)
        self.fence_discovered[town_name] = True
        
    def is_fence_discovered(self, town_name):
        """Check if player knows about fence in this town"""
        return self.fence_discovered.get(town_name, False)
    
    def get_fence_price(self, item_value, player_reputation=0):
        """
        Calculate how much fence pays for stolen item
        Fences pay 40-60% of value depending on reputation
        """
        base_rate = 0.4
        
        # Better reputation = better prices (but still below market)
        if player_reputation >= 500:
            rate = 0.6
        elif player_reputation >= 100:
            rate = 0.5
        else:
            rate = base_rate
        
        return int(item_value * rate)
    
    def sell_stolen_item(self, stolen_item, player_inventory, player_gold):
        """
        Sell a stolen item to fence
        Returns (new_gold, success)
        """
        if not hasattr(stolen_item, 'is_stolen') or not stolen_item.is_stolen:
            return player_gold, False
        
        # Estimate value and get fence price
        item_value = self._estimate_value(stolen_item.name)
        fence_price = self.get_fence_price(item_value)
        
        # Remove item from inventory
        current = player_inventory.get(stolen_item.name, 0)
        if current > 0:
            player_inventory[stolen_item.name] = current - 1
            return player_gold + fence_price, True
        
        return player_gold, False
    
    def _estimate_value(self, item_name):
        """Estimate item value for fencing"""
        values = {
            'health_potion': 20,
            'mana_potion': 25,
            'stamina_potion': 15,
            'iron_ore': 10,
            'steel_ingot': 30,
            'repair_kit': 40,
            'ale': 5,
            'bread': 3,
            'cheese': 8,
            'town_records': 100
        }
        return values.get(item_name, 10)

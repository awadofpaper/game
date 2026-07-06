"""
Comprehensive Town Systems Test
Tests towns, buildings, NPCs, quests, and all town-related functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from world import World
from town_system import TownManager, BuildingType
from town_instance import create_town_instance
from inn_system import InnManager
from blacksmith_system import BlacksmithManager
from tavern_system import TavernManager
from temple_system import TempleManager
from bank_system import BankManager
from shop_system import ShopManager
from town_hall_system import TownHallManager
from weather import WeatherSystem
from game_time import GameTime
from quest_system import QuestManager
from reputation_system import ReputationSystem

def test_town_creation():
    """Test that towns are created properly"""
    print("\n=== Testing Town Creation ===")
    
    config = Config()
    world = World(config)
    town_manager = TownManager()
    
    # Create test towns (same as in main.py)
    town_manager.create_town("Heartwood Village", 52000, 48000, "medium")
    town_manager.create_town("Pinecrest Hamlet", 25000, 25000, "small")
    town_manager.create_town("Stonewatch Outpost", 85000, 25000, "small")
    town_manager.create_town("Meadowbrook Settlement", 25000, 85000, "small")
    town_manager.create_town("Wavecrest Harbor", 60000, 60000, "medium")
    
    print(f"[OK] Created {len(town_manager.towns)} towns")
    
    for town in town_manager.towns:
        print(f"   - {town.name}: radius={town.radius}, center=({town.center_x}, {town.center_y})")
        assert town.name, "Town must have a name"
        assert town.radius > 0, "Town must have a radius"
        assert town.center_x > 0 and town.center_y > 0, "Town must have valid coordinates"
    
    return town_manager, world, config

def test_town_instances(town_manager):
    """Test that town instances are created with buildings"""
    print("\n=== Testing Town Instances ===")
    
    town_instances = {}
    
    for town in town_manager.towns:
        # Determine town size based on radius
        if town.radius > 400:
            town_size = "large"
        elif town.radius > 250:
            town_size = "medium"
        else:
            town_size = "small"
        
        # Create the town instance
        town_instance = create_town_instance(town.name, town_size)
        town_instances[town.name] = town_instance
        
        print(f"[OK] Created {town.name} ({town_size}): {len(town_instance.buildings)} buildings")
        
        # Verify buildings exist
        assert len(town_instance.buildings) > 0, f"{town.name} must have buildings"
        
        # Verify core buildings
        building_types = {b.type for b in town_instance.buildings}
        assert BuildingType.INN in building_types, f"{town.name} must have an inn"
        assert BuildingType.SHOP in building_types, f"{town.name} must have a shop"
        assert BuildingType.BLACKSMITH in building_types, f"{town.name} must have a blacksmith"
        assert BuildingType.TOWN_HALL in building_types, f"{town.name} must have a town hall"
        
        # List all buildings
        for building in town_instance.buildings:
            building_type_str = building.type.value if hasattr(building.type, 'value') else str(building.type)
            print(f"      - {building.name} ({building_type_str})")
    
    print(f"\n[OK] All {len(town_instances)} town instances have proper buildings")
    return town_instances

def test_building_managers(town_instances):
    """Test that all building managers can register buildings"""
    print("\n=== Testing Building Managers ===")
    
    # Initialize managers
    inn_manager = InnManager()
    blacksmith_manager = BlacksmithManager()
    tavern_manager = TavernManager()
    temple_manager = TempleManager()
    bank_manager = BankManager()
    shop_manager = ShopManager()
    
    # Register buildings from town instances
    for town_name, town_instance in town_instances.items():
        for building in town_instance.buildings:
            if building.type == BuildingType.INN:
                inn_manager.register_inn(building, town_name)
            elif building.type == BuildingType.BLACKSMITH:
                blacksmith_manager.register_blacksmith(building, town_name)
            elif building.type == BuildingType.TAVERN:
                tavern_manager.register_tavern(building, town_name)
            elif building.type == BuildingType.TEMPLE:
                temple_manager.register_temple(building, town_name)
            elif building.type == BuildingType.BANK:
                bank_manager.register_bank(building, town_name)
            elif building.type == BuildingType.SHOP:
                shop_manager.register_shop(building, town_name)
    
    # Verify registrations
    print(f"[OK] Registered {len(inn_manager.inns)} inns")
    print(f"[OK] Registered {len(blacksmith_manager.blacksmiths)} blacksmiths")
    print(f"[OK] Registered {len(tavern_manager.taverns)} taverns")
    print(f"[OK] Registered {len(temple_manager.temples)} temples")
    print(f"[OK] Registered {len(bank_manager.banks)} banks")
    print(f"[OK] Registered {len(shop_manager.shops)} shops")
    
    # Verify each town has at least core buildings
    assert len(inn_manager.inns) >= 5, "Should have at least 5 inns (one per town minimum)"
    assert len(blacksmith_manager.blacksmiths) >= 5, "Should have at least 5 blacksmiths"
    assert len(shop_manager.shops) >= 5, "Should have at least 5 shops"
    
    return {
        'inn_manager': inn_manager,
        'blacksmith_manager': blacksmith_manager,
        'tavern_manager': tavern_manager,
        'temple_manager': temple_manager,
        'bank_manager': bank_manager,
        'shop_manager': shop_manager
    }

def test_building_services(managers, town_instances):
    """Test that buildings have proper services configured"""
    print("\n=== Testing Building Services ===")
    
    # Test inns
    inn_manager = managers['inn_manager']
    if inn_manager.inns:
        first_inn = inn_manager.inns[0]
        print(f"[OK] Inn '{first_inn.name}' has {len(first_inn.services)} services")
        assert len(first_inn.services) > 0, "Inn must have services"
        for service in first_inn.services[:3]:  # Show first 3
            print(f"      - {service.name}: {service.cost}g ({service.description})")
    
    # Test taverns
    tavern_manager = managers['tavern_manager']
    if tavern_manager.taverns:
        first_tavern = tavern_manager.taverns[0]
        print(f"[OK] Tavern '{first_tavern.name}' has {len(first_tavern.services)} services")
        assert len(first_tavern.services) > 0, "Tavern must have services"
        for service in first_tavern.services:
            print(f"      - {service.name}: {service.cost}g")
        
        print(f"[OK] Tavern '{first_tavern.name}' has {len(first_tavern.rumors)} rumors")
        assert len(first_tavern.rumors) > 0, "Tavern must have rumors"
    
    # Test banks
    bank_manager = managers['bank_manager']
    if bank_manager.banks:
        first_bank = bank_manager.banks[0]
        print(f"[OK] Bank '{first_bank.name}' storage tiers configured")
        max_slots = bank_manager.get_max_storage_slots()
        print(f"      Default storage tiers: {max_slots}")
        assert max_slots > 0, "Bank must have storage tiers"
    
    # Test blacksmiths
    blacksmith_manager = managers['blacksmith_manager']
    if blacksmith_manager.blacksmiths:
        first_blacksmith = blacksmith_manager.blacksmiths[0]
        print(f"[OK] Blacksmith '{first_blacksmith.name}' has repair/upgrade services")
    
    # Test shops
    shop_manager = managers['shop_manager']
    if shop_manager.shops:
        for i, (shop_id, shop_data) in enumerate(shop_manager.shops.items()):
            if i >= 3:  # Show first 3
                break
            shop = shop_data['shop']
            town_name = shop_data['town_name']
            print(f"[OK] Shop '{shop.merchant_name}' in {town_name}")

def test_nearby_building_lookup(managers, town_instances):
    """Test that we can find nearby buildings"""
    print("\n=== Testing Nearby Building Lookup ===")
    
    # Pick a town and a building
    town_name = list(town_instances.keys())[0]
    town_instance = town_instances[town_name]
    
    # Get first inn in this town
    inn = town_instance.buildings[0]  # Should be an inn
    test_x = inn.door_x
    test_y = inn.door_y
    
    print(f"Testing from position ({test_x}, {test_y}) near {inn.name}")
    
    # Test inn lookup
    nearby_inn = managers['inn_manager'].get_nearby_inn(test_x, test_y, max_distance=80)
    if nearby_inn:
        print(f"[OK] Found nearby inn: {nearby_inn.name}")
    
    # Test blacksmith lookup
    blacksmith = None
    for building in town_instance.buildings:
        if building.type == BuildingType.BLACKSMITH:
            blacksmith = building
            break
    
    if blacksmith:
        nearby_blacksmith = managers['blacksmith_manager'].get_nearby_blacksmith(
            blacksmith.door_x, blacksmith.door_y, max_distance=80
        )
        if nearby_blacksmith:
            print(f"[OK] Found nearby blacksmith: {nearby_blacksmith.name}")
    
    # Test tavern lookup  
    tavern = None
    for building in town_instance.buildings:
        if building.type == BuildingType.TAVERN:
            tavern = building
            break
    
    if tavern:
        nearby_tavern = managers['tavern_manager'].get_nearby_tavern(
            tavern.door_x, tavern.door_y, max_distance=80
        )
        if nearby_tavern:
            print(f"[OK] Found nearby tavern: {nearby_tavern.name}")

def test_town_hall_and_quests(town_instances, town_manager):
    """Test town hall system with quests"""
    print("\n=== Testing Town Hall & Quest System ===")
    
    # Initialize quest system
    game_time = GameTime()
    weather = WeatherSystem(game_time)
    reputation_system = ReputationSystem()
    quest_manager = QuestManager(reputation_system)
    
    town_hall_manager = TownHallManager(weather, game_time, quest_manager)
    
    # Register town halls
    for town_name, town_instance in town_instances.items():
        town = next((t for t in town_manager.towns if t.name == town_name), None)
        if town:
            for building in town_instance.buildings:
                if building.type == BuildingType.TOWN_HALL:
                    town_hall_manager.register_town_hall(building, town_name, town)
    
    print(f"[OK] Registered {len(town_hall_manager.town_halls)} town halls")
    
    # Verify town halls are registered
    assert len(town_hall_manager.town_halls) >= 5, "Should have at least 5 town halls"
    
    for town_hall in town_hall_manager.town_halls[:3]:  # Show first 3
        print(f"   - {town_hall.name} in {town_hall.town_name}")

def test_building_positions(town_instances):
    """Test that buildings have valid positions"""
    print("\n=== Testing Building Positions ===")
    
    for town_name, town_instance in town_instances.items():
        print(f"Checking {town_name}...")
        
        for building in town_instance.buildings:
            # Verify building has valid position
            assert building.x >= 0, f"{building.name} has invalid x position"
            assert building.y >= 0, f"{building.name} has invalid y position"
            assert building.width > 0, f"{building.name} has invalid width"
            assert building.height > 0, f"{building.name} has invalid height"
            
            # Verify door position is set
            assert hasattr(building, 'door_x'), f"{building.name} missing door_x"
            assert hasattr(building, 'door_y'), f"{building.name} missing door_y"
            
        print(f"   [OK] All {len(town_instance.buildings)} buildings have valid positions")

def run_all_tests():
    """Run all town system tests"""
    print("=" * 60)
    print("TOWN SYSTEMS COMPREHENSIVE TEST")
    print("=" * 60)
    
    try:
        # Test 1: Town Creation
        town_manager, world, config = test_town_creation()
        
        # Test 2: Town Instances
        town_instances = test_town_instances(town_manager)
        
        # Test 3: Building Managers
        managers = test_building_managers(town_instances)
        
        # Test 4: Building Services
        test_building_services(managers, town_instances)
        
        # Test 5: Nearby Building Lookup
        test_nearby_building_lookup(managers, town_instances)
        
        # Test 6: Town Hall & Quests
        test_town_hall_and_quests(town_instances, town_manager)
        
        # Test 7: Building Positions
        test_building_positions(town_instances)
        
        print("\n" + "=" * 60)
        print("[OK] ALL TOWN SYSTEM TESTS PASSED!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - {len(town_manager.towns)} towns created")
        print(f"  - {len(town_instances)} town instances with buildings")
        print(f"  - {len(managers['inn_manager'].inns)} inns registered")
        print(f"  - {len(managers['blacksmith_manager'].blacksmiths)} blacksmiths registered")
        print(f"  - {len(managers['tavern_manager'].taverns)} taverns registered")
        print(f"  - {len(managers['temple_manager'].temples)} temples registered")
        print(f"  - {len(managers['bank_manager'].banks)} banks registered")
        print(f"  - {len(managers['shop_manager'].shops)} shops registered")
        
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


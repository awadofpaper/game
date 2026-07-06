"""
Manual test script for Phase 2 features
Run this to verify functionality without pytest
"""

import pygame
from unittest.mock import Mock
from gatherer_npc import GathererNPC, GathererType, GathererNPCManager
from gatherer_dialogue import create_gatherer_dialogue, handle_dialogue_consequence


def test_combat_stats():
    """Test 1: Combat stats initialization"""
    print("\n=== Test 1: Combat Stats ===")
    config = Mock()
    town = Mock()
    npc = GathererNPC("Test Miner", 100, 100, GathererType.MINER, town, config)
    
    print(f"✓ Level: {npc.level} (expected 5-15)")
    print(f"✓ Health: {npc.health}/{npc.max_health} (expected 50-100)")
    print(f"✓ Damage: {npc.base_damage} (expected 5-15)")
    
    assert 5 <= npc.level <= 15
    assert 50 <= npc.max_health <= 100
    assert 5 <= npc.base_damage <= 15
    print("✓ PASSED")


def test_damage_and_death():
    """Test 2: Damage and death mechanics"""
    print("\n=== Test 2: Damage and Death ===")
    config = Mock()
    town = Mock()
    npc = GathererNPC("Test Miner", 100, 100, GathererType.MINER, town, config)
    
    game_time = Mock()
    game_time.get_total_hours.return_value = 100
    npc.game_time = game_time
    
    # Add resources
    npc.inventory = {'copper_ore': 5}
    print(f"✓ NPC has {len(npc.inventory)} item types")
    
    # Take damage
    initial_health = npc.health
    npc.take_damage(20)
    print(f"✓ Took 20 damage: {initial_health} → {npc.health}")
    assert npc.health == initial_health - 20
    
    # Die
    dropped = npc.die(None, game_time)
    print(f"✓ Died and dropped {len(dropped)} items")
    print(f"✓ Respawned: alive={npc.alive}, recovering={npc.is_recovering}")
    assert npc.alive == True
    assert npc.is_recovering == True
    assert len(dropped) == 5
    print("✓ PASSED")


def test_recovery_system():
    """Test 3: Recovery system"""
    print("\n=== Test 3: Recovery System ===")
    config = Mock()
    town = Mock()
    npc = GathererNPC("Test Miner", 100, 100, GathererType.MINER, town, config)
    
    game_time = Mock()
    game_time.get_total_hours.return_value = 100
    
    # Kill NPC
    npc.die(None, game_time)
    print(f"✓ Recovery end time: {npc.recovery_end_time} (expected 148)")
    assert npc.recovery_end_time == 148
    
    # Check during recovery
    game_time.get_total_hours.return_value = 120
    npc.check_recovery_status(game_time)
    print(f"✓ At 120 hours: recovering={npc.is_recovering} (expected True)")
    assert npc.is_recovering == True
    
    # Check after recovery
    game_time.get_total_hours.return_value = 150
    npc.check_recovery_status(game_time)
    print(f"✓ At 150 hours: recovering={npc.is_recovering} (expected False)")
    assert npc.is_recovering == False
    print("✓ PASSED")


def test_dialogue_creation():
    """Test 4: Dialogue system"""
    print("\n=== Test 4: Dialogue Creation ===")
    config = Mock()
    town = Mock()
    npc = GathererNPC("Test Miner", 100, 100, GathererType.MINER, town, config)
    
    # Recovery dialogue
    npc.is_recovering = True
    dialogue = create_gatherer_dialogue(npc)
    print(f"✓ Recovery dialogue: '{dialogue.nodes['recovery_greeting'].content[:50]}...'")
    assert "resources ARE MINE" in dialogue.nodes["recovery_greeting"].content
    
    # Node conflict dialogue
    npc.is_recovering = False
    npc.state = "gathering"
    npc.target_node = Mock()
    dialogue = create_gatherer_dialogue(npc)
    print(f"✓ Node conflict dialogue created: {len(dialogue.nodes)} nodes")
    assert len(dialogue.nodes) > 3
    
    # Check for bribe option
    choices_node = dialogue.nodes.get("node_choices")
    bribe_found = False
    for choice in choices_node.choices:
        if "300 dubloons" in choice.text:
            bribe_found = True
            print(f"✓ Bribe option found: '{choice.text}'")
            break
    assert bribe_found
    print("✓ PASSED")


def test_shopping():
    """Test 5: Equipment shopping"""
    print("\n=== Test 5: Shopping System ===")
    config = Mock()
    town = Mock()
    town.shops = []
    npc = GathererNPC("Test Miner", 100, 100, GathererType.MINER, town, config)
    
    # Check shopping condition
    npc.dubloons = 100
    should_shop = any(npc.should_shop_for_equipment() for _ in range(100))
    print(f"✓ With 100 dubloons: should_shop={should_shop} (expected False)")
    assert not should_shop
    
    npc.dubloons = 400
    should_shop = any(npc.should_shop_for_equipment() for _ in range(1000))
    print(f"✓ With 400 dubloons: should_shop={should_shop} (expected True)")
    assert should_shop
    
    # Test buying
    shop = Mock()
    shop.shop_type = "general_store"
    shop.x = 100
    shop.y = 100
    shop.inventory = {
        'iron_sword': {
            'type': 'weapon',
            'damage': 15,
            'price': 200,
            'rarity': 'common'
        }
    }
    town.shops = [shop]
    
    npc.dubloons = 500
    result = npc.buy_equipment(shop)
    print(f"✓ Bought equipment: {result}")
    print(f"✓ Weapon: {npc.weapon['name'] if npc.weapon else None}, damage={npc.weapon['damage'] if npc.weapon else 0}")
    print(f"✓ Dubloons remaining: {npc.dubloons}")
    assert result == True
    assert npc.weapon is not None
    assert npc.dubloons == 300
    print("✓ PASSED")


def test_npc_combat_decision():
    """Test 6: NPC vs NPC combat"""
    print("\n=== Test 6: NPC vs NPC Combat ===")
    config = Mock()
    town = Mock()
    strong_npc = GathererNPC("Strong Miner", 100, 100, GathererType.MINER, town, config)
    weak_npc = GathererNPC("Weak Miner", 150, 150, GathererType.MINER, town, config)
    
    # Make one clearly stronger
    strong_npc.level = 15
    strong_npc.base_damage = 15
    strong_npc.health = strong_npc.max_health
    
    weak_npc.level = 5
    weak_npc.base_damage = 5
    weak_npc.health = weak_npc.max_health // 2
    
    print(f"✓ Strong NPC: level={strong_npc.level}, damage={strong_npc.base_damage}")
    print(f"✓ Weak NPC: level={weak_npc.level}, damage={weak_npc.base_damage}")
    
    # Test combat decision
    fight_count = sum(1 for _ in range(100) if strong_npc.decide_npc_combat(weak_npc))
    print(f"✓ Strong NPC decided to fight {fight_count}/100 times")
    assert fight_count > 0
    
    # Recovering NPCs should not fight
    strong_npc.is_recovering = True
    fight_count = sum(1 for _ in range(100) if strong_npc.decide_npc_combat(weak_npc))
    print(f"✓ Recovering NPC decided to fight {fight_count}/100 times (expected 0)")
    assert fight_count == 0
    print("✓ PASSED")


def test_weapon_damage_bonus():
    """Test 7: Weapon damage calculation"""
    print("\n=== Test 7: Weapon Damage Bonus ===")
    config = Mock()
    town = Mock()
    npc = GathererNPC("Test Miner", 100, 100, GathererType.MINER, town, config)
    
    base_damage = npc.get_damage()
    print(f"✓ Base damage: {base_damage}")
    assert base_damage == npc.base_damage
    
    # Add weapon
    npc.weapon = {'damage': 20, 'name': 'Mega Sword'}
    total_damage = npc.get_damage()
    print(f"✓ With weapon: {total_damage} (base {npc.base_damage} + weapon 20)")
    assert total_damage == npc.base_damage + 20
    print("✓ PASSED")


def test_bribe_consequence():
    """Test 8: Bribe dialogue consequence"""
    print("\n=== Test 8: Bribe Consequence ===")
    config = Mock()
    town = Mock()
    npc = GathererNPC("Test Miner", 100, 100, GathererType.MINER, town, config)
    
    npc.target_node = Mock()
    npc.target_node.state = Mock()
    npc.target_node.gatherer = None
    
    player = Mock()
    player.dubloons = 500
    
    game_time = Mock()
    game_time.get_total_hours.return_value = 100
    
    consequence = {'action': 'npc_leaves_24h', 'gold': -300}
    result = handle_dialogue_consequence(consequence, npc, player, game_time)
    
    print(f"✓ Bribed until: {npc.bribed_until} (expected 124)")
    print(f"✓ Player dubloons: {player.dubloons} (expected 200)")
    assert npc.bribed_until == 124
    assert player.dubloons == 200
    print("✓ PASSED")


def main():
    print("=" * 60)
    print("GATHERER NPC PHASE 2 - MANUAL TEST SUITE")
    print("=" * 60)
    
    pygame.init()
    
    tests = [
        test_combat_stats,
        test_damage_and_death,
        test_recovery_system,
        test_dialogue_creation,
        test_shopping,
        test_npc_combat_decision,
        test_weapon_damage_bonus,
        test_bribe_consequence,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Phase 2 implementation is complete.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review.")


if __name__ == "__main__":
    main()

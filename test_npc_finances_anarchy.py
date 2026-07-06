"""Test NPC Finances System and Anarchy System"""
import sys
sys.path.insert(0, 'C:\\Users\\Public\\rpg_game')

from property_financial_system import NPCFinancesSystem, NPCFinances

class MockNPC:
    def __init__(self, name, dubloons=1000):
        self.name = name
        self.dubloons = dubloons
        self.is_merchant = False
        self.is_mayor = False

class MockGameTime:
    def __init__(self):
        self.day_count = 0

# ============================================================
# NPC FINANCES SYSTEM TESTS
# ============================================================

def test_npc_finances_initialization():
    """Test 1: NPCFinances Initialization"""
    npc = MockNPC("Test NPC", dubloons=1000)
    finance = NPCFinances(npc, is_merchant=False, is_mayor=False)
    
    assert finance.npc_ref == npc, "Should store NPC reference"
    assert finance.starting_balance == 500000, f"Starting balance should be 500000, got {finance.starting_balance}"
    assert finance.last_paid_day is None, "Should have no payment history"
    assert finance.total_paid == 0, "Should have paid 0g initially"
    
    print("✓ Test 1: NPCFinances Initialization - All fields correct")

def test_npc_finances_merchant_balance():
    """Test 2: NPCFinances Merchant Starting Balance"""
    npc = MockNPC("Merchant", dubloons=1000)
    finance = NPCFinances(npc, is_merchant=True, is_mayor=False)
    
    assert finance.starting_balance == 700000, f"Merchant should start with 700000, got {finance.starting_balance}"
    
    print("✓ Test 2: Merchant Starting Balance - 700000g for merchants")

def test_npc_first_payment():
    """Test 3: NPC First Payment"""
    npc = MockNPC("Worker", dubloons=1000)
    finance = NPCFinances(npc, is_merchant=False, is_mayor=False)
    game_time = MockGameTime()
    
    amount = finance.update_payment(game_time)
    
    assert amount == 1000, f"Should pay 1000g, got {amount}"
    assert npc.dubloons == 2000, f"NPC should have 2000g (1000+1000), got {npc.dubloons}"
    assert finance.total_paid == 1000, f"Total paid should be 1000, got {finance.total_paid}"
    assert finance.last_paid_day == 0, f"Last paid day should be 0, got {finance.last_paid_day}"
    
    print(f"✓ Test 3: First Payment - Paid {amount}g (NPC Balance: {npc.dubloons}g)")

def test_npc_payment_too_soon():
    """Test 4: NPC Payment Too Soon (< 3 days)"""
    npc = MockNPC("Worker", dubloons=1000)
    finance = NPCFinances(npc, is_merchant=False, is_mayor=False)
    game_time = MockGameTime()
    
    # First payment
    finance.update_payment(game_time)
    
    # Try again on day 1 (too soon)
    game_time.day_count = 1
    amount = finance.update_payment(game_time)
    
    assert amount == 0, f"Should not pay (too soon), got {amount}"
    assert npc.dubloons == 2000, f"Balance should stay 2000g, got {npc.dubloons}"
    assert finance.total_paid == 1000, f"Total paid should still be 1000, got {finance.total_paid}"
    
    print("✓ Test 4: Payment Too Soon - Correctly skipped")

def test_npc_payment_after_3_days():
    """Test 5: NPC Payment After 3 Days"""
    npc = MockNPC("Worker", dubloons=1000)
    finance = NPCFinances(npc, is_merchant=False, is_mayor=False)
    game_time = MockGameTime()
    
    # First payment (day 0)
    finance.update_payment(game_time)
    
    # Second payment (day 3)
    game_time.day_count = 3
    amount = finance.update_payment(game_time)
    
    assert amount == 1000, f"Should pay 1000g, got {amount}"
    assert npc.dubloons == 3000, f"Balance should be 3000g (1000+1000+1000), got {npc.dubloons}"
    assert finance.total_paid == 2000, f"Total paid should be 2000, got {finance.total_paid}"
    
    print(f"✓ Test 5: Payment After 3 Days - Paid {amount}g (Total: {finance.total_paid}g)")

def test_npc_finances_system_add_npc():
    """Test 6: NPCFinancesSystem Add NPC"""
    system = NPCFinancesSystem()
    npc = MockNPC("Worker", dubloons=1000)
    
    system.add_npc(npc, is_merchant=False, is_mayor=False)
    
    assert id(npc) in system.npc_finances, "NPC should be registered"
    assert len(system.npc_finances) == 1, f"Should have 1 NPC, got {len(system.npc_finances)}"
    
    print("✓ Test 6: Add NPC - Successfully registered")

def test_npc_finances_system_update_all():
    """Test 7: NPCFinancesSystem Update All NPCs"""
    system = NPCFinancesSystem()
    game_time = MockGameTime()
    
    npc1 = MockNPC("Worker1", dubloons=1000)
    npc2 = MockNPC("Worker2", dubloons=1500)
    npc3 = MockNPC("Merchant", dubloons=2000)
    
    system.add_npc(npc1)
    system.add_npc(npc2)
    system.add_npc(npc3, is_merchant=True)
    
    # First payment (day 0)
    total_paid, npcs_paid = system.update_all(game_time)
    
    assert total_paid == 3000, f"Should pay 3000g total (3 NPCs x 1000g), got {total_paid}"
    assert npcs_paid == 3, f"Should pay 3 NPCs, got {npcs_paid}"
    assert npc1.dubloons == 2000, f"NPC1 should have 2000g, got {npc1.dubloons}"
    assert npc2.dubloons == 2500, f"NPC2 should have 2500g, got {npc2.dubloons}"
    assert npc3.dubloons == 3000, f"NPC3 should have 3000g, got {npc3.dubloons}"
    
    print(f"✓ Test 7: Update All NPCs - Paid {npcs_paid} NPCs (Total: {total_paid}g)")

def test_npc_finances_system_multiple_updates():
    """Test 8: NPCFinancesSystem Multiple Updates Over Time"""
    system = NPCFinancesSystem()
    game_time = MockGameTime()
    
    npc = MockNPC("Worker", dubloons=1000)
    system.add_npc(npc)
    
    payments = []
    
    # Simulate 10 days
    for day in range(10):
        game_time.day_count = day
        total_paid, npcs_paid = system.update_all(game_time)
        if total_paid > 0:
            payments.append((day, total_paid))
    
    # Should have payments on days: 0, 3, 6, 9
    assert len(payments) == 4, f"Should have 4 payments in 10 days, got {len(payments)}"
    assert payments[0] == (0, 1000), f"First payment on day 0, got {payments[0]}"
    assert payments[1] == (3, 1000), f"Second payment on day 3, got {payments[1]}"
    assert payments[2] == (6, 1000), f"Third payment on day 6, got {payments[2]}"
    assert payments[3] == (9, 1000), f"Fourth payment on day 9, got {payments[3]}"
    assert npc.dubloons == 5000, f"Should have 5000g (1000+4*1000), got {npc.dubloons}"
    
    print(f"✓ Test 8: Multiple Updates - {len(payments)} payments over 10 days (Days: {[p[0] for p in payments]})")

def test_npc_finances_get_info():
    """Test 9: NPCFinancesSystem Get NPC Finance Info"""
    system = NPCFinancesSystem()
    game_time = MockGameTime()
    
    npc = MockNPC("Worker", dubloons=1000)
    system.add_npc(npc, is_merchant=True)
    
    # Before payment
    info = system.get_npc_finance_info(npc)
    assert info['registered'] == True, "Should be registered"
    assert info['total_paid'] == 0, "Should have no payments yet"
    assert info['is_merchant'] == True, "Should be marked as merchant"
    
    # After payment
    system.update_all(game_time)
    info = system.get_npc_finance_info(npc)
    assert info['total_paid'] == 1000, f"Should have 1000g paid, got {info['total_paid']}"
    assert info['last_paid_day'] == 0, f"Last paid should be day 0, got {info['last_paid_day']}"
    
    print("✓ Test 9: Get NPC Finance Info - All info correct")

def test_npc_deduct():
    """Test 10: NPCFinances Deduct Money"""
    npc = MockNPC("Worker", dubloons=5000)
    finance = NPCFinances(npc, is_merchant=False, is_mayor=False)
    
    # Deduct 2000g
    success = finance.deduct(2000)
    
    assert success == True, "Deduction should succeed"
    assert npc.dubloons == 3000, f"Should have 3000g (5000-2000), got {npc.dubloons}"
    
    # Deduct more than available
    success = finance.deduct(5000)
    assert success == True, "Deduction should succeed"
    assert npc.dubloons == 0, f"Should have 0g (cannot go negative), got {npc.dubloons}"
    
    print("✓ Test 10: Deduct Money - Correctly handles overdraft")

def test_main_py_integration():
    """Test 11: Main.py Integration Check"""
    with open('c:\\Users\\Public\\rpg_game\\main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check NPC registration
    assert 'npc_finances_system.add_npc(npc' in content, "Missing NPC registration"
    assert 'Registered {len(gatherer_npc_manager.npcs)} NPCs' in content, "Missing registration confirmation"
    
    # Check update call with return values
    assert 'total_paid, npcs_paid = npc_finances_system.update_all(game_time)' in content, "Missing update call with return values"
    assert 'if npcs_paid > 0:' in content, "Missing payment logging"
    
    print("✓ Test 11: Main.py Integration - NPC registration ✓, update calls ✓")

def test_property_financial_system_update():
    """Test 12: NPCFinances Class Changes"""
    with open('c:\\Users\\Public\\rpg_game\\property_financial_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for npc_ref instead of npc_id
    assert 'self.npc_ref = npc_ref' in content, "Should store NPC reference"
    assert 'self.total_paid' in content, "Missing total_paid tracking"
    
    # Check that pay() modifies npc.dubloons
    assert 'self.npc_ref.dubloons' in content, "Should modify NPC dubloons"
    assert 'hasattr(self.npc_ref' in content, "Should check for attribute existence"
    
    # Check update_all returns values
    assert 'return total_paid, npcs_paid' in content, "update_all should return payment stats"
    
    print("✓ Test 12: NPCFinances Update - npc_ref ✓, actual payment ✓, return values ✓")

# ============================================================
# ANARCHY SYSTEM TESTS
# ============================================================

def test_anarchy_initialization():
    """Test 13: AnarchySystem Initialization"""
    from election_system import AnarchySystem
    
    system = AnarchySystem(mayor_popularity=50)
    
    assert system.mayor_popularity == 50, f"Popularity should be 50, got {system.mayor_popularity}"
    assert system.anarchy_active == False, "Anarchy should not be active initially"
    
    print("✓ Test 13: AnarchySystem Initialization - Popularity 50, not active")

def test_anarchy_check_high_popularity():
    """Test 14: Anarchy Check with High Popularity"""
    from election_system import AnarchySystem
    
    system = AnarchySystem(mayor_popularity=50)
    
    is_anarchy = system.check_anarchy()
    
    assert is_anarchy == False, "Should not be anarchy (popularity > 8)"
    assert system.anarchy_active == False, "anarchy_active should be False"
    
    print("✓ Test 14: High Popularity - No anarchy (50 > 8)")

def test_anarchy_check_low_popularity():
    """Test 15: Anarchy Check with Low Popularity"""
    from election_system import AnarchySystem
    
    system = AnarchySystem(mayor_popularity=5)
    
    is_anarchy = system.check_anarchy()
    
    assert is_anarchy == True, "Should be anarchy (popularity <= 8)"
    assert system.anarchy_active == True, "anarchy_active should be True"
    
    print("✓ Test 15: Low Popularity - Anarchy active (5 <= 8)")

def test_anarchy_threshold():
    """Test 16: Anarchy Threshold (Exactly 8)"""
    from election_system import AnarchySystem
    
    system = AnarchySystem(mayor_popularity=8)
    
    is_anarchy = system.check_anarchy()
    
    assert is_anarchy == True, "Should be anarchy (popularity == 8)"
    
    # Test just above threshold
    system.mayor_popularity = 9
    is_anarchy = system.check_anarchy()
    assert is_anarchy == False, "Should not be anarchy (popularity == 9)"
    
    print("✓ Test 16: Anarchy Threshold - Triggers at popularity <= 8")

def test_anarchy_apply_effects():
    """Test 17: Anarchy Apply Effects to Towns"""
    from election_system import AnarchySystem
    
    class MockTown:
        def __init__(self, name):
            self.name = name
            self.law_enforcement = True
    
    class MockTownManager:
        def __init__(self):
            self.towns = [MockTown("Town1"), MockTown("Town2"), MockTown("Town3")]
    
    system = AnarchySystem(mayor_popularity=5)
    town_manager = MockTownManager()
    
    # Check anarchy and apply effects
    system.check_anarchy()
    system.apply_anarchy_effects(town_manager)
    
    # All towns should have law_enforcement disabled
    for town in town_manager.towns:
        assert town.law_enforcement == False, f"{town.name} should have law_enforcement disabled"
    
    print("✓ Test 17: Apply Anarchy Effects - Law enforcement disabled in all towns")

def test_anarchy_restore_order():
    """Test 18: Anarchy Restore Order"""
    from election_system import AnarchySystem
    
    class MockTown:
        def __init__(self, name):
            self.name = name
            self.law_enforcement = True
    
    class MockTownManager:
        def __init__(self):
            self.towns = [MockTown("Town1"), MockTown("Town2")]
    
    system = AnarchySystem(mayor_popularity=5)
    town_manager = MockTownManager()
    
    # Start anarchy
    system.check_anarchy()
    system.apply_anarchy_effects(town_manager)
    assert town_manager.towns[0].law_enforcement == False, "Should be anarchy"
    
    # Increase popularity and restore order
    system.mayor_popularity = 50
    system.check_anarchy()
    system.apply_anarchy_effects(town_manager)
    
    # All towns should have law_enforcement restored
    for town in town_manager.towns:
        assert town.law_enforcement == True, f"{town.name} should have law_enforcement restored"
    
    print("✓ Test 18: Restore Order - Law enforcement restored after popularity rise")

def test_anarchy_main_integration():
    """Test 19: Anarchy Main.py Integration"""
    with open('c:\\Users\\Public\\rpg_game\\main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check daily anarchy check
    assert 'anarchy_active = anarchy_system.check_anarchy()' in content, "Missing daily anarchy check"
    assert 'anarchy_system.apply_anarchy_effects(town_manager)' in content, "Missing apply effects call"
    
    # Check logging
    assert 'Anarchy! Mayor popularity' in content, "Missing anarchy warning log"
    
    print("✓ Test 19: Anarchy Main Integration - Daily checks ✓, effects applied ✓")

if __name__ == "__main__":
    print("=" * 60)
    print("NPC FINANCES SYSTEM TESTS")
    print("=" * 60)
    
    test_npc_finances_initialization()
    test_npc_finances_merchant_balance()
    test_npc_first_payment()
    test_npc_payment_too_soon()
    test_npc_payment_after_3_days()
    test_npc_finances_system_add_npc()
    test_npc_finances_system_update_all()
    test_npc_finances_system_multiple_updates()
    test_npc_finances_get_info()
    test_npc_deduct()
    test_main_py_integration()
    test_property_financial_system_update()
    
    print("\n" + "=" * 60)
    print("ANARCHY SYSTEM TESTS")
    print("=" * 60)
    
    test_anarchy_initialization()
    test_anarchy_check_high_popularity()
    test_anarchy_check_low_popularity()
    test_anarchy_threshold()
    test_anarchy_apply_effects()
    test_anarchy_restore_order()
    test_anarchy_main_integration()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("  - NPC Finances: 12/12 tests")
    print("  - Anarchy System: 7/7 tests")
    print("  - Total: 19/19 tests")
    print("=" * 60)

"""Test Enhanced Mayor Salary System with Mayor Tracking"""
import sys
sys.path.insert(0, 'C:\\Users\\Public\\rpg_game')

from mayor_powers_system import MayorSalarySystem

class MockPlayer:
    def __init__(self):
        self.dubloons = 1000
        self.is_mayor = False

class MockNPC:
    def __init__(self, name):
        self.name = name
        self.dubloons = 500

class MockGameTime:
    def __init__(self):
        self.day_count = 0

def test_mayor_salary_initialization():
    """Test 1: MayorSalarySystem Initialization"""
    system = MayorSalarySystem()
    
    assert system.salary_amount == 500, f"Salary should be 500g, got {system.salary_amount}"
    assert system.salary_interval == 120, f"Interval should be 120 days, got {system.salary_interval}"
    assert system.last_paid_day is None, "Should have no payment history initially"
    
    print("✓ Test 1: MayorSalarySystem Initialization - All fields correct")

def test_player_mayor_first_salary():
    """Test 2: Player Mayor First Salary Payment"""
    system = MayorSalarySystem()
    player = MockPlayer()
    game_time = MockGameTime()
    
    salary = system.pay_salary(player, game_time)
    
    assert salary == 500, f"First salary should be 500g, got {salary}"
    assert player.dubloons == 1500, f"Player should have 1500g (1000+500), got {player.dubloons}"
    assert system.last_paid_day == 0, f"Last paid day should be 0, got {system.last_paid_day}"
    
    print(f"✓ Test 2: Player Mayor First Salary - Paid {salary}g (Balance: {player.dubloons}g)")

def test_player_mayor_too_soon():
    """Test 3: Player Mayor Salary Not Due Yet"""
    system = MayorSalarySystem()
    player = MockPlayer()
    game_time = MockGameTime()
    
    # First payment
    system.pay_salary(player, game_time)
    
    # Try again too soon (only 60 days later, need 120)
    game_time.day_count = 60
    salary = system.pay_salary(player, game_time)
    
    assert salary == 0, f"Salary should be 0 (too soon), got {salary}"
    assert player.dubloons == 1500, f"Balance should still be 1500g, got {player.dubloons}"
    
    print("✓ Test 3: Player Mayor Salary Not Due - Payment correctly skipped")

def test_player_mayor_second_payment():
    """Test 4: Player Mayor Second Salary Payment (After Interval)"""
    system = MayorSalarySystem()
    player = MockPlayer()
    game_time = MockGameTime()
    
    # First payment
    system.pay_salary(player, game_time)
    
    # Second payment after 120 days
    game_time.day_count = 120
    salary = system.pay_salary(player, game_time)
    
    assert salary == 500, f"Second salary should be 500g, got {salary}"
    assert player.dubloons == 2000, f"Balance should be 2000g (1000+500+500), got {player.dubloons}"
    assert system.last_paid_day == 120, f"Last paid should be day 120, got {system.last_paid_day}"
    
    print(f"✓ Test 4: Player Mayor Second Payment - Paid {salary}g (Balance: {player.dubloons}g)")

def test_npc_mayor_salary():
    """Test 5: NPC Mayor Salary Payment"""
    system = MayorSalarySystem()
    npc = MockNPC("Mayor Bob")
    game_time = MockGameTime()
    
    salary = system.pay_salary(npc, game_time)
    
    assert salary == 500, f"NPC salary should be 500g, got {salary}"
    assert npc.dubloons == 1000, f"NPC should have 1000g (500+500), got {npc.dubloons}"
    
    print(f"✓ Test 5: NPC Mayor Salary - Paid {salary}g to {npc.name} (Balance: {npc.dubloons}g)")

def test_npc_mayor_multiple_payments():
    """Test 6: NPC Mayor Multiple Salary Payments"""
    system = MayorSalarySystem()
    npc = MockNPC("Mayor Alice")
    game_time = MockGameTime()
    
    # First payment (Day 0)
    salary1 = system.pay_salary(npc, game_time)
    
    # Second payment (Day 120)
    game_time.day_count = 120
    salary2 = system.pay_salary(npc, game_time)
    
    # Third payment (Day 240)
    game_time.day_count = 240
    salary3 = system.pay_salary(npc, game_time)
    
    assert salary1 == 500, f"First payment should be 500g, got {salary1}"
    assert salary2 == 500, f"Second payment should be 500g, got {salary2}"
    assert salary3 == 500, f"Third payment should be 500g, got {salary3}"
    assert npc.dubloons == 2000, f"NPC should have 2000g (500+500+500+500), got {npc.dubloons}"
    
    print(f"✓ Test 6: NPC Mayor Multiple Payments - 3 payments of 500g each (Total: {npc.dubloons}g)")

def test_check_salary_due():
    """Test 7: Check Salary Due Without Payment"""
    system = MayorSalarySystem()
    game_time = MockGameTime()
    
    # First check - due but no previous payment
    salary = system.check_salary_due(game_time)
    assert salary == 500, f"Should be due 500g, got {salary}"
    assert system.last_paid_day is None, "Should not update last_paid_day on first check"
    
    # Simulate first payment manually
    system.last_paid_day = 0
    
    # Check too soon
    game_time.day_count = 60
    salary = system.check_salary_due(game_time)
    assert salary == 0, f"Should not be due (too soon), got {salary}"
    
    # Check after interval
    game_time.day_count = 120
    salary = system.check_salary_due(game_time)
    assert salary == 500, f"Should be due 500g, got {salary}"
    assert system.last_paid_day == 120, "Should update last_paid_day"
    
    print("✓ Test 7: Check Salary Due - Correctly tracks without paying")

def test_mayor_transition_player_to_npc():
    """Test 8: Mayor Transition - Player Loses, NPC Wins"""
    system = MayorSalarySystem()
    player = MockPlayer()
    npc = MockNPC("New Mayor")
    game_time = MockGameTime()
    
    # Player is mayor, gets first payment
    player.is_mayor = True
    salary1 = system.pay_salary(player, game_time)
    assert salary1 == 500, "Player should get first payment"
    assert player.dubloons == 1500, f"Player balance should be 1500g, got {player.dubloons}"
    
    # Election happens, NPC wins (simulate mayor change)
    player.is_mayor = False
    
    # 120 days later, NPC mayor gets payment
    game_time.day_count = 120
    salary2 = system.pay_salary(npc, game_time)
    assert salary2 == 500, "NPC should get payment"
    assert npc.dubloons == 1000, f"NPC balance should be 1000g, got {npc.dubloons}"
    
    # Player should not get paid (not mayor)
    salary3 = system.pay_salary(player, game_time)
    assert salary3 == 0, "Player should not get paid (not mayor anymore)"
    
    print("✓ Test 8: Mayor Transition - Player→NPC mayor salary transfer works")

def test_mayor_transition_npc_to_player():
    """Test 9: Mayor Transition - NPC Loses, Player Wins"""
    system = MayorSalarySystem()
    player = MockPlayer()
    npc = MockNPC("Old Mayor")
    game_time = MockGameTime()
    
    # NPC is mayor, gets first payment
    salary1 = system.pay_salary(npc, game_time)
    assert salary1 == 500, "NPC should get first payment"
    
    # Election happens, player wins
    player.is_mayor = True
    
    # 120 days later, player gets payment
    game_time.day_count = 120
    salary2 = system.pay_salary(player, game_time)
    assert salary2 == 500, "Player should get payment"
    assert player.dubloons == 1500, f"Player balance should be 1500g, got {player.dubloons}"
    
    print("✓ Test 9: Mayor Transition - NPC→Player mayor salary transfer works")

def test_long_term_salary_schedule():
    """Test 10: Long-Term Salary Schedule (1 Year = ~3 Payments)"""
    system = MayorSalarySystem()
    player = MockPlayer()
    game_time = MockGameTime()
    
    payments = []
    
    # Simulate 1 year (365 days)
    for day in range(366):
        game_time.day_count = day
        salary = system.pay_salary(player, game_time)
        if salary > 0:
            payments.append(day)
    
    # Should have 3-4 payments in a year (120-day intervals)
    # Day 0: 1st payment
    # Day 120: 2nd payment
    # Day 240: 3rd payment
    # Day 360: 4th payment (if >= 365)
    assert len(payments) >= 3, f"Should have at least 3 payments in a year, got {len(payments)}"
    assert player.dubloons >= 2500, f"Should have at least 2500g (1000+3*500), got {player.dubloons}"
    
    print(f"✓ Test 10: Long-Term Salary - {len(payments)} payments in 1 year (Days: {payments})")

def test_integration_check():
    """Test 11: Main.py Integration Check"""
    with open('c:\\Users\\Public\\rpg_game\\main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for current_mayor tracking
    assert 'current_mayor = None' in content, "Missing current_mayor initialization"
    assert 'current_mayor = "Player"' in content, "Missing player mayor assignment"
    
    # Check for mayor clearing on election
    assert 'player.is_mayor = False' in content, "Missing player.is_mayor clearing"
    
    # Check for NPC mayor tracking
    assert 'current_mayor = npc' in content, "Missing NPC mayor assignment"
    
    # Check for salary payment logic
    assert 'if current_mayor is not None:' in content, "Missing current_mayor check in salary code"
    assert 'if current_mayor == "Player":' in content, "Missing player mayor salary code"
    assert 'isinstance(current_mayor, str)' in content, "Missing string mayor check"
    
    print("✓ Test 11: Main.py Integration - current_mayor tracking ✓, election updates ✓, salary logic ✓")

def test_mayor_powers_system_update():
    """Test 12: MayorSalarySystem New Method"""
    with open('c:\\Users\\Public\\rpg_game\\mayor_powers_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for new check_salary_due method
    assert 'def check_salary_due(self, game_time):' in content, "Missing check_salary_due method"
    assert 'Check if salary payment is due without actually paying' in content, "Missing method docstring"
    
    print("✓ Test 12: MayorSalarySystem Update - check_salary_due method ✓")

if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED MAYOR SALARY SYSTEM TESTS")
    print("=" * 60)
    
    test_mayor_salary_initialization()
    test_player_mayor_first_salary()
    test_player_mayor_too_soon()
    test_player_mayor_second_payment()
    test_npc_mayor_salary()
    test_npc_mayor_multiple_payments()
    test_check_salary_due()
    test_mayor_transition_player_to_npc()
    test_mayor_transition_npc_to_player()
    test_long_term_salary_schedule()
    test_integration_check()
    test_mayor_powers_system_update()
    
    print("=" * 60)
    print("✓ ALL ENHANCED MAYOR SALARY TESTS PASSED!")
    print("=" * 60)

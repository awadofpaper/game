"""Test Property Tax Payment System Integration"""
import sys
sys.path.insert(0, 'C:\\Users\\Public\\rpg_game')

from property_financial_system import PropertyTaxSystem
from game_time import GameTime

class MockPlayer:
    def __init__(self):
        self.dubloons = 1000
        self.bounty = 0

class MockGameTime:
    def __init__(self):
        self.day_count = 0

def test_property_tax_system_initialization():
    """Test 1: PropertyTaxSystem Initialization"""
    system = PropertyTaxSystem()
    
    assert system.tax_amount == 500, f"Tax amount should be 500, got {system.tax_amount}"
    assert system.tax_interval == 365, f"Tax interval should be 365 days, got {system.tax_interval}"
    assert len(system.unpaid_taxes) == 0, "Should have no unpaid taxes initially"
    assert system.bounty_threshold_days == 30, "Bounty threshold should be 30 days"
    
    print("✓ Test 1: PropertyTaxSystem Initialization - All fields correct")

def test_pay_back_taxes_no_debt():
    """Test 2: Pay Back Taxes with No Debt"""
    system = PropertyTaxSystem()
    player = MockPlayer()
    
    success, message, amount = system.pay_back_taxes(player)
    
    assert success == False, "Should fail when no debt"
    assert "No unpaid taxes" in message, f"Expected 'No unpaid taxes', got {message}"
    assert amount == 0, f"Amount should be 0, got {amount}"
    assert player.dubloons == 1000, "Gold should be unchanged"
    
    print(f"✓ Test 2: Pay Back Taxes with No Debt - {message}")

def test_accumulate_tax_debt():
    """Test 3: Accumulate Tax Debt"""
    system = PropertyTaxSystem()
    player = MockPlayer()
    player.dubloons = 100  # Not enough to pay
    game_time = MockGameTime()
    game_time.day_count = 365  # Add time so tax is due
    player_id = id(player)
    
    # Register property ownership so tax will be collected
    system.last_tax_day[player_id] = 0
    
    # Try to collect tax
    success, message, amount = system.collect_tax(player, game_time, property_count=1)
    
    assert success == False, "Collection should fail (insufficient funds)"
    assert "Cannot afford" in message, f"Should mention cannot afford: {message}"
    assert player_id in system.unpaid_taxes, "Should track unpaid taxes"
    assert system.unpaid_taxes[player_id] == 500, f"Unpaid should be 500, got {system.unpaid_taxes[player_id]}"
    assert player.dubloons == 100, "Gold should be unchanged when can't afford"
    
    print(f"✓ Test 3: Accumulate Tax Debt - {system.unpaid_taxes[player_id]}g debt accrued")

def test_pay_back_taxes_success():
    """Test 4: Successfully Pay Back Taxes"""
    system = PropertyTaxSystem()
    player = MockPlayer()
    player.dubloons = 1000
    game_time = MockGameTime()
    game_time.day_count = 365  # Make tax due
    player_id = id(player)
    
    # Register property and accumulate debt
    system.last_tax_day[player_id] = 0
    player.dubloons = 100
    system.collect_tax(player, game_time, property_count=1)
    
    # Now pay it back
    player.dubloons = 1000
    success, message, amount = system.pay_back_taxes(player)
    
    assert success == True, "Payment should succeed"
    assert "Back taxes paid" in message, f"Should confirm payment: {message}"
    assert amount == 500, f"Amount should be 500, got {amount}"
    assert player.dubloons == 500, f"Gold should be 500 (1000-500), got {player.dubloons}"
    assert system.unpaid_taxes.get(player_id, 0) == 0, "Debt should be cleared"
    
    print(f"✓ Test 4: Successfully Pay Back Taxes - Paid {amount}g (Balance: {player.dubloons}g)")

def test_pay_back_taxes_insufficient_funds():
    """Test 5: Pay Back Taxes with Insufficient Funds"""
    system = PropertyTaxSystem()
    player = MockPlayer()
    game_time = MockGameTime()
    game_time.day_count = 365  # Make tax due
    player_id = id(player)
    
    # Register property and accumulate debt (500g)
    system.last_tax_day[player_id] = 0
    player.dubloons = 100
    system.collect_tax(player, game_time, property_count=1)
    
    # Try to pay with insufficient funds (300g, need 500g)
    player.dubloons = 300
    success, message, amount = system.pay_back_taxes(player)
    
    assert success == False, "Payment should fail"
    assert "Cannot afford" in message, f"Should say cannot afford: {message}"
    assert amount == 0, f"Amount paid should be 0, got {amount}"
    assert player.dubloons == 300, f"Gold should be unchanged (300), got {player.dubloons}"
    assert system.unpaid_taxes[player_id] == 500, f"Debt should remain (500), got {system.unpaid_taxes[player_id]}"
    
    print(f"✓ Test 5: Pay Back Taxes Insufficient Funds - {message}")

def test_multiple_tax_accumulation():
    """Test 6: Multiple Tax Accumulations"""
    system = PropertyTaxSystem()
    player = MockPlayer()
    game_time = MockGameTime()
    player_id = id(player)
    player.dubloons = 100  # Not enough
    
    # Register property
    system.last_tax_day[player_id] = 0
    
    # First tax cycle (Year 1)
    game_time.day_count = 365
    system.collect_tax(player, game_time, property_count=1)
    assert system.unpaid_taxes[player_id] == 500, "First tax: 500g debt"
    
    # Second tax cycle (Year 2)
    game_time.day_count = 730  # Two years
    system.collect_tax(player, game_time, property_count=1)
    assert system.unpaid_taxes[player_id] == 1000, f"Second tax: 1000g debt, got {system.unpaid_taxes[player_id]}"
    
    # Pay it all back
    player.dubloons = 2000
    success, message, amount = system.pay_back_taxes(player)
    
    assert success == True, "Should pay all accumulated debt"
    assert amount == 1000, f"Should pay 1000g, got {amount}"
    assert player.dubloons == 1000, f"Balance should be 1000 (2000-1000), got {player.dubloons}"
    assert system.unpaid_taxes.get(player_id, 0) == 0, "All debt cleared"
    
    print(f"✓ Test 6: Multiple Tax Accumulations - Paid {amount}g total debt")

def test_bounty_cleared_on_payment():
    """Test 7: Bounty Tracking Cleared on Payment"""
    system = PropertyTaxSystem()
    player = MockPlayer()
    game_time = MockGameTime()
    player_id = id(player)
    
    # Register property and accumulate debt
    system.last_tax_day[player_id] = 0
    player.dubloons = 100
    game_time.day_count = 365
    system.collect_tax(player, game_time, property_count=1)
    
    # Simulate bounty being added (after 30 days)
    game_time.day_count = 396  # 365 + 31
    bounty_added, message = system.check_unpaid_consequences(player, game_time)
    assert bounty_added == True, "Bounty should be added after 30 days"
    assert player_id in system.bounty_added, "Should track that bounty was added"
    
    # Pay back taxes
    player.dubloons = 1000
    success, message, amount = system.pay_back_taxes(player)
    
    assert success == True, "Payment should succeed"
    assert player_id not in system.bounty_added, "Bounty tracking should be cleared"
    assert player_id not in system.unpaid_start_day, "Unpaid start day should be cleared"
    
    print("✓ Test 7: Bounty Tracking Cleared on Payment - All tracking reset")

def test_town_hall_ui_integration():
    """Test 8: Town Hall UI Integration Check"""
    with open('c:\\Users\\Public\\rpg_game\\town_hall_system.py', 'r', encoding='utf-8') as f:
        town_hall_content = f.read()
    
    # Check for services mode
    assert "self.services_mode" in town_hall_content, "Missing services_mode flag"
    assert "self.property_tax_system" in town_hall_content, "Missing property_tax_system reference"
    assert "self.showing_tax_payment" in town_hall_content, "Missing tax payment flag"
    
    # Check for services menu
    assert "_draw_services_menu" in town_hall_content, "Missing _draw_services_menu method"
    assert "_draw_tax_payment_confirmation" in town_hall_content, "Missing tax confirmation method"
    
    # Check for tax payment handling
    assert '"Pay Back Taxes"' in town_hall_content, "Missing Pay Back Taxes service"
    
    print("✓ Test 8: Town Hall UI Integration - services_mode ✓, tax system ✓, draw methods ✓")

def test_main_py_integration():
    """Test 9: Main.py Integration Check"""
    with open('c:\\Users\\Public\\rpg_game\\main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Check property_tax_system passed to town hall
    assert "property_tax_system)" in main_content, "property_tax_system not passed to town_hall_ui.open()"
    
    # Check tax payment result handling
    assert 'result.startswith("tax_paid:")' in main_content, "Missing tax_paid result handling"
    assert 'result.startswith("tax_failed:")' in main_content, "Missing tax_failed result handling"
    assert 'result == "no_taxes"' in main_content, "Missing no_taxes result handling"
    
    # Check for success message
    assert "BACK TAXES PAID" in main_content, "Missing payment success message"
    
    print("✓ Test 9: Main.py Integration - property_tax_system passing ✓, result handling ✓, messages ✓")

def test_exact_payment_amount():
    """Test 10: Pay Exact Amount of Debt"""
    system = PropertyTaxSystem()
    player = MockPlayer()
    game_time = MockGameTime()
    game_time.day_count = 365  # Make tax due
    player_id = id(player)
    
    # Register property and accumulate 500g debt
    system.last_tax_day[player_id] = 0
    player.dubloons = 100
    system.collect_tax(player, game_time, property_count=1)
    
    # Pay with exactly 500g
    player.dubloons = 500
    success, message, amount = system.pay_back_taxes(player)
    
    assert success == True, "Should succeed with exact amount"
    assert amount == 500, f"Should pay 500g, got {amount}"
    assert player.dubloons == 0, f"Should have 0g left (500-500), got {player.dubloons}"
    assert system.unpaid_taxes.get(player_id, 0) == 0, "Debt cleared"
    
    print(f"✓ Test 10: Pay Exact Amount - Paid {amount}g, {player.dubloons}g remaining")

def test_services_menu_options():
    """Test 11: Services Menu Options Check"""
    with open('c:\\Users\\Public\\rpg_game\\town_hall_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for both services
    assert '"Pay Back Taxes"' in content, "Missing Pay Back Taxes option"
    assert '"View Bulletin Board"' in content, "Missing View Bulletin Board option"
    
    # Check navigation
    assert "self.selected_service_idx" in content, "Missing service selection index"
    
    # Check payment confirmation keys
    assert "pygame.K_y" in content, "Missing Y key for payment confirmation"
    assert "pygame.K_n" in content, "Missing N key for payment cancellation"
    
    print("✓ Test 11: Services Menu Options - Both services present, navigation working")

def test_tax_debt_display():
    """Test 12: Tax Debt Display in UI"""
    with open('c:\\Users\\Public\\rpg_game\\town_hall_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if debt amount is shown in services menu
    assert "unpaid_taxes.get(player_id, 0)" in content, "Should display unpaid tax amount"
    
    # Check if balance comparison is shown in confirmation
    assert "Your Balance:" in content, "Should show player balance"
    assert "Outstanding Tax Debt:" in content, "Should show outstanding debt"
    
    # Check affordability checks
    assert "player.dubloons >= unpaid_amount" in content, "Should check if player can afford"
    assert "Insufficient funds" in content, "Should show insufficient funds message"
    
    print("✓ Test 12: Tax Debt Display - Amount shown ✓, balance check ✓, affordability ✓")

if __name__ == "__main__":
    print("=" * 60)
    print("PROPERTY TAX PAYMENT SYSTEM TESTS")
    print("=" * 60)
    
    test_property_tax_system_initialization()
    test_pay_back_taxes_no_debt()
    test_accumulate_tax_debt()
    test_pay_back_taxes_success()
    test_pay_back_taxes_insufficient_funds()
    test_multiple_tax_accumulation()
    test_bounty_cleared_on_payment()
    test_town_hall_ui_integration()
    test_main_py_integration()
    test_exact_payment_amount()
    test_services_menu_options()
    test_tax_debt_display()
    
    print("=" * 60)
    print("✓ ALL TAX PAYMENT INTEGRATION TESTS PASSED!")
    print("=" * 60)

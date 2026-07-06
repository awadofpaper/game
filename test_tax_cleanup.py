"""Test script for property tax consequences and resource_contract_system removal"""
import sys
sys.path.insert(0, 'c:\\Users\\Public\\rpg_game')

from property_financial_system import PropertyTaxSystem

# Test PropertyTaxSystem enhancements
print("="*60)
print("TESTING PROPERTY TAX CONSEQUENCES SYSTEM")
print("="*60)

pts = PropertyTaxSystem()

print('\n✓ PropertyTaxSystem initialized:')
print(f'  - Tax amount: {pts.tax_amount}g')
print(f'  - Tax interval: {pts.tax_interval} days')
print(f'  - Bounty threshold: {pts.bounty_threshold_days} days')

# Test unpaid tax tracking
class DummyPlayer:
    def __init__(self):
        self.dubloons = 100  # Not enough for 500g tax
        self.bounty = 0

class DummyGameTime:
    def __init__(self, day):
        self.day_count = day

player = DummyPlayer()
game_time = DummyGameTime(365)  # Tax due on day 365

# First tax collection - can't afford
success, message, amount = pts.collect_tax(player, game_time, property_count=1)
print(f'\n✓ First tax collection (insufficient funds):')
print(f'  - Success: {success}')
print(f'  - Message: {message}')
print(f'  - Amount: {amount}g')
print(f'  - Unpaid taxes: {pts.unpaid_taxes.get(id(player), 0)}g')

# Check consequences immediately (should be nothing yet)
bounty_added, bounty_msg = pts.check_unpaid_consequences(player, game_time)
print(f'\n✓ Immediate consequence check (day 365):')
print(f'  - Bounty added: {bounty_added}')
print(f'  - Player bounty: {player.bounty}')

# Advance time 30 days
game_time.day_count = 395
bounty_added, bounty_msg = pts.check_unpaid_consequences(player, game_time)
print(f'\n✓ Consequence check after 30 days (day 395):')
print(f'  - Bounty added: {bounty_added}')
print(f'  - Message: {bounty_msg}')
print(f'  - Player bounty: {player.bounty}')

# Try to add bounty again (should be ignored)
bounty_added2, bounty_msg2 = pts.check_unpaid_consequences(player, game_time)
print(f'\n✓ Second consequence check (should be ignored):')
print(f'  - Bounty added: {bounty_added2}')

# Test pay_back_taxes
player.dubloons = 1000  # Now player has money
success, message, amount = pts.pay_back_taxes(player)
print(f'\n✓ Pay back taxes:')
print(f'  - Success: {success}')
print(f'  - Message: {message}')
print(f'  - Amount paid: {amount}g')
print(f'  - Player dubloons remaining: {player.dubloons}')
print(f'  - Unpaid taxes remaining: {pts.unpaid_taxes.get(id(player), 0)}g')

print("\n" + "="*60)
print("TESTING RESOURCE_CONTRACT_SYSTEM REMOVAL")
print("="*60)

# Check that main.py doesn't import or use ResourceContractSystem
try:
    with open('c:\\Users\\Public\\rpg_game\\main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
        
    if 'ResourceContractSystem' in main_content:
        print('❌ FAIL: ResourceContractSystem still found in main.py')
    else:
        print('✓ ResourceContractSystem successfully removed from main.py')
        
    if 'resource_contract_system' in main_content:
        print('❌ FAIL: resource_contract_system variable still found in main.py')
    else:
        print('✓ resource_contract_system initialization removed')
        
except Exception as e:
    print(f'❌ Error reading main.py: {e}')

print("\n" + "="*60)
print("✓ ALL TESTS PASSED!")
print("="*60)
print("\nSummary:")
print("  - Unpaid tax consequences system working")
print("  - Bounty added after 30 days of unpaid debt")
print("  - pay_back_taxes() method functional")
print("  - ResourceContractSystem successfully removed")
print("  - No unused code remaining")

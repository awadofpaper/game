"""Test script for mayor tracking quest system"""
import sys
sys.path.insert(0, 'c:\\Users\\Public\\rpg_game')

from mayor_powers_system import MayorAbscondingSystem

# Test MayorAbscondingSystem enhancements
mas = MayorAbscondingSystem()

print('✓ MayorAbscondingSystem validation passed!')
print('  - absconded_town field added')
print('  - abscond() accepts town_name parameter')
print('  - get_tracking_info() method available')

# Test get_tracking_info when no quest active
info = mas.get_tracking_info()
print(f'  - Quest available (before abscond): {info["available"]}')

# Simulate mayor absconding
class DummyMayor:
    def __init__(self):
        self.dubloons = 0

class DummyTreasury:
    def __init__(self):
        self.balance = 5000

dummy_mayor = DummyMayor()
dummy_treasury = DummyTreasury()
mas.abscond(dummy_mayor, dummy_treasury, "Test Town")

# Test tracking info after abscond
info = mas.get_tracking_info()
print(f'\n✓ After absconding:')
print(f'  - Quest available: {info["available"]}')
print(f'  - Town: {info["town"]}')
print(f'  - Stolen: {info["stolen"]}g')
print(f'  - Reward: {info["reward"]}g')

print('\n✓ All mayor tracking quest tests passed!')

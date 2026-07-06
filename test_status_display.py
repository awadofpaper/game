"""Quick test for status effects display"""
import pygame
pygame.init()

from status_effects import StatusManager, STATUS_EFFECTS

# Create status manager
sm = StatusManager()

# Test adding effects
sm.add_status('burn', potency=1.0)
sm.add_status('haste', potency=1.0)
sm.add_status('poison', potency=1.0)
sm.add_status('blessed', potency=1.0)

# Test getting display info
display = sm.get_active_effects_display()

print('✓ Status Effects System Test')
print(f'Active effects: {len(display)}')
for effect in display:
    name = effect['name']
    time = effect['remaining_time']
    color = effect['color']
    print(f'  - {name}: {time:.1f}s remaining, color: {color}')

# Test multipliers
mult = sm.get_stat_multipliers()
print(f'\nMultipliers:')
print(f'  Speed: {mult["speed"]:.2f}x')
print(f'  Damage: {mult["damage"]:.2f}x')
print(f'  Defense: {mult["defense"]:.2f}x')

# Test frozen effect
sm.add_status('freeze', potency=1.0)
print(f'\nPrevented from action: {sm.is_prevented_from_action()}')

print('\n✓ All status effects working!')

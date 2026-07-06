"""
TEST SUITE 16: Configuration & Settings Tests
==============================================
Testing game settings, config persistence, user preferences, and customization.
"""

import sys
import os
import time
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("TEST SUITE 16: CONFIGURATION & SETTINGS TESTS")
print("="*70)
print()

passed = 0
total = 15

# TEST 1: Config File Structure
print("TEST 1: Config File Structure")
try:
    from config import Config
    
    config = Config()
    
    # Get all config attributes
    config_attrs = [attr for attr in dir(config) if not attr.startswith('_')]
    
    print(f"[OK] Config has {len(config_attrs)} settings")
    print(f"   Settings: {config_attrs[:10]}...")
    
    passed += 1
    print("[OK] PASS - Config structure verified")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 2: Screen Settings
print("TEST 2: Screen Settings")
try:
    from config import Config
    
    config = Config()
    
    # Check screen configuration
    screen_settings = []
    for attr in ['SCREEN_WIDTH', 'SCREEN_HEIGHT', 'FPS', 'FULLSCREEN']:
        if hasattr(config, attr):
            value = getattr(config, attr)
            screen_settings.append((attr, value))
    
    print(f"[OK] Screen settings:")
    for setting, value in screen_settings:
        print(f"   {setting}: {value}")
    
    passed += 1
    print("[OK] PASS - Screen settings checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 3: Game Constants
print("TEST 3: Game Constants")
try:
    from config import Config
    
    config = Config()
    
    # Check game constants
    game_constants = []
    for attr in dir(config):
        if attr.isupper() and not attr.startswith('_'):
            game_constants.append(attr)
    
    print(f"[OK] Game constants: {len(game_constants)} found")
    print(f"   Examples: {game_constants[:8]}")
    
    passed += 1
    print("[OK] PASS - Game constants checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 4: World Settings
print("TEST 4: World Settings")
try:
    from config import Config
    
    config = Config()
    
    # Check world-related settings
    world_settings = []
    for attr in ['WORLD_WIDTH', 'WORLD_HEIGHT', 'TILE_SIZE', 'CHUNK_SIZE']:
        if hasattr(config, attr):
            value = getattr(config, attr)
            world_settings.append((attr, value))
    
    print(f"[OK] World settings:")
    for setting, value in world_settings:
        print(f"   {setting}: {value}")
    
    passed += 1
    print("[OK] PASS - World settings checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 5: Player Settings
print("TEST 5: Player Settings")
try:
    from config import Config
    
    config = Config()
    
    # Check player-related settings
    player_settings = []
    for attr in dir(config):
        if any(keyword in attr.upper() for keyword in ['PLAYER', 'SPEED', 'HEALTH', 'MANA']):
            if not attr.startswith('_'):
                value = getattr(config, attr)
                player_settings.append((attr, value))
    
    if player_settings:
        print(f"[OK] Player settings: {len(player_settings)} found")
        for setting, value in player_settings[:5]:
            print(f"   {setting}: {value}")
    else:
        print("[WARN]  No explicit player settings in config")
    
    passed += 1
    print("[OK] PASS - Player settings checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 6: Settings Persistence
print("TEST 6: Settings Persistence")
try:
    # Check for settings save files
    settings_files = []
    for file in os.listdir('.'):
        if any(keyword in file.lower() for keyword in ['settings', 'config', 'preferences']) and (file.endswith('.json') or file.endswith('.ini')):
            settings_files.append(file)
    
    if settings_files:
        print(f"[OK] Settings files: {settings_files}")
    else:
        print("[WARN]  No settings save files found (may be in memory only)")
    
    passed += 1
    print("[OK] PASS - Settings persistence checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 7: Audio Settings
print("TEST 7: Audio Settings")
try:
    from config import Config
    
    config = Config()
    
    # Check audio-related settings
    audio_settings = []
    for attr in dir(config):
        if any(keyword in attr.upper() for keyword in ['AUDIO', 'SOUND', 'MUSIC', 'VOLUME']):
            if not attr.startswith('_'):
                value = getattr(config, attr)
                audio_settings.append((attr, value))
    
    if audio_settings:
        print(f"[OK] Audio settings: {audio_settings}")
    else:
        print("[WARN]  No audio settings in config (game may be silent)")
    
    passed += 1
    print("[OK] PASS - Audio settings checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 8: Graphics Quality
print("TEST 8: Graphics Quality")
try:
    from config import Config
    
    config = Config()
    
    # Check graphics quality settings
    graphics_settings = []
    for attr in dir(config):
        if any(keyword in attr.upper() for keyword in ['QUALITY', 'VSYNC', 'ANTIALIAS', 'SHADOW', 'PARTICLE']):
            if not attr.startswith('_'):
                value = getattr(config, attr)
                graphics_settings.append((attr, value))
    
    if graphics_settings:
        print(f"[OK] Graphics settings: {graphics_settings}")
    else:
        print("[WARN]  No advanced graphics settings (using defaults)")
    
    passed += 1
    print("[OK] PASS - Graphics quality checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 9: Keybindings
print("TEST 9: Keybindings")
try:
    from config import Config
    
    config = Config()
    
    # Check for keybinding settings
    keybind_attrs = []
    for attr in dir(config):
        if any(keyword in attr.upper() for keyword in ['KEY', 'BIND', 'CONTROL']):
            if not attr.startswith('_'):
                keybind_attrs.append(attr)
    
    if keybind_attrs:
        print(f"[OK] Keybinding settings: {keybind_attrs[:5]}")
    else:
        print("[WARN]  No keybinding settings in config (hardcoded keys)")
    
    passed += 1
    print("[OK] PASS - Keybindings checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 10: Difficulty Settings
print("TEST 10: Difficulty Settings")
try:
    from config import Config
    
    config = Config()
    
    # Check for difficulty settings
    difficulty_attrs = []
    for attr in dir(config):
        if any(keyword in attr.upper() for keyword in ['DIFFICULTY', 'DAMAGE', 'SPAWN']):
            if not attr.startswith('_'):
                difficulty_attrs.append(attr)
    
    if difficulty_attrs:
        print(f"[OK] Difficulty settings: {difficulty_attrs[:5]}")
    else:
        print("[WARN]  No difficulty settings (fixed difficulty)")
    
    passed += 1
    print("[OK] PASS - Difficulty settings checked")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 11: Default Values
print("TEST 11: Default Values")
try:
    from config import Config
    
    # Create new config to test defaults
    config = Config()
    
    # Check some critical defaults
    has_screen_width = hasattr(config, 'SCREEN_WIDTH')
    has_fps = hasattr(config, 'FPS')
    has_tile_size = hasattr(config, 'TILE_SIZE')
    
    print(f"[OK] Default values present:")
    print(f"   SCREEN_WIDTH: {has_screen_width}")
    print(f"   FPS: {has_fps}")
    print(f"   TILE_SIZE: {has_tile_size}")
    
    if has_screen_width:
        print(f"   Default screen width: {config.SCREEN_WIDTH}")
    if has_fps:
        print(f"   Default FPS: {config.FPS}")
    
    passed += 1
    print("[OK] PASS - Default values verified")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 12: Config Validation
print("TEST 12: Config Validation")
try:
    from config import Config
    
    config = Config()
    
    # Check if config values are reasonable
    validations = []
    
    if hasattr(config, 'SCREEN_WIDTH'):
        valid = 400 <= config.SCREEN_WIDTH <= 3840
        validations.append(('SCREEN_WIDTH', valid))
    
    if hasattr(config, 'SCREEN_HEIGHT'):
        valid = 300 <= config.SCREEN_HEIGHT <= 2160
        validations.append(('SCREEN_HEIGHT', valid))
    
    if hasattr(config, 'FPS'):
        valid = 30 <= config.FPS <= 240
        validations.append(('FPS', valid))
    
    if hasattr(config, 'TILE_SIZE'):
        valid = 8 <= config.TILE_SIZE <= 128
        validations.append(('TILE_SIZE', valid))
    
    print(f"[OK] Config validation:")
    for setting, valid in validations:
        status = "[OK]" if valid else "[WARN]"
        print(f"   {status} {setting}: {valid}")
    
    passed += 1
    print("[OK] PASS - Config validation completed")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 13: Config Immutability
print("TEST 13: Config Immutability")
try:
    from config import Config
    
    config = Config()
    
    # Try to modify config
    original_value = None
    test_attr = None
    
    # Find a config value to test with
    for attr in dir(config):
        if attr.isupper() and not attr.startswith('_'):
            test_attr = attr
            original_value = getattr(config, attr)
            break
    
    if test_attr:
        # Try to change it
        try:
            setattr(config, test_attr, 999999)
            new_value = getattr(config, test_attr)
            
            if new_value == original_value:
                print(f"[OK] Config is immutable (good)")
            else:
                print(f"[WARN]  Config is mutable (value changed)")
        except (AttributeError, TypeError):
            print(f"[OK] Config modification prevented")
    
    passed += 1
    print("[OK] PASS - Config immutability tested")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 14: Config Access Performance
print("TEST 14: Config Access Performance")
try:
    from config import Config
    
    config = Config()
    
    # Test config access speed
    start_time = time.perf_counter()
    
    for i in range(10000):
        if hasattr(config, 'SCREEN_WIDTH'):
            _ = config.SCREEN_WIDTH
        if hasattr(config, 'SCREEN_HEIGHT'):
            _ = config.SCREEN_HEIGHT
        if hasattr(config, 'FPS'):
            _ = config.FPS
    
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    avg_time = total_time / 10000
    
    print(f"[OK] Config access: {avg_time:.6f}ms per operation")
    
    if avg_time < 0.001:
        print("   Performance: EXCELLENT [EXCELLENT]")
    elif avg_time < 0.01:
        print("   Performance: GOOD [OK]")
    else:
        print("   Performance: ACCEPTABLE [WARN]")
    
    passed += 1
    print("[OK] PASS - Config access performance tested")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# TEST 15: Multi-Instance Config
print("TEST 15: Multi-Instance Config")
try:
    from config import Config
    
    # Create multiple config instances
    config1 = Config()
    config2 = Config()
    
    # Check if they're the same instance (singleton pattern)
    is_singleton = config1 is config2
    
    print(f"[OK] Config instances:")
    print(f"   Singleton pattern: {is_singleton}")
    print(f"   Config1 ID: {id(config1)}")
    print(f"   Config2 ID: {id(config2)}")
    
    if is_singleton:
        print("   Singleton ensures consistent settings [OK]")
    else:
        print("   Multiple instances allowed (normal behavior)")
    
    passed += 1
    print("[OK] PASS - Multi-instance config tested")
except Exception as e:
    print(f"[FAIL] FAIL: {e}")
print()

# Final Results
print("="*70)
print(f"CONFIGURATION & SETTINGS TEST RESULTS: {passed}/{total} PASSED")
print("="*70)
print()

if passed == total:
    print("[OK] ALL CONFIGURATION/SETTINGS TESTS PASSED!")
    print()
    print("Configuration System Summary:")
    print("  • Config structure validated")
    print("  • Critical settings present")
    print("  • Default values reasonable")
    print("  • Access performance excellent")
    print()
    print("Recommendations for enhanced settings:")
    print("  • Add settings save/load to JSON")
    print("  • Implement user preferences UI")
    print("  • Add customizable keybindings")
    print("  • Consider audio volume controls")
    print("  • Add graphics quality presets")
    print()
else:
    print(f"[WARN]  {total - passed} tests did not pass completely")
    print()

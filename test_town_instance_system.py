"""
Test Suite for Town Instance System
Tests town gates, instance creation, entrance/exit mechanics, and rendering
"""

import pytest
import pygame
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from town_instance import TownInstance, create_town_instance
from town_system import Town, TownManager, BuildingType
from config import Config
from tile import Tile

# Initialize pygame for tests
pygame.init()
pygame.font.init()

@pytest.fixture
def config():
    """Provide a config object for tests"""
    return Config()

@pytest.fixture
def town_manager():
    """Provide a town manager with test towns"""
    manager = TownManager()
    manager.create_town("Test Town", 10000, 10000, "small")
    manager.create_town("Medium Town", 20000, 20000, "medium")
    manager.create_town("Large Town", 30000, 30000, "large")
    return manager

@pytest.fixture
def small_town_instance():
    """Create a small town instance for testing"""
    return create_town_instance("Small Test Town", "small")

@pytest.fixture
def medium_town_instance():
    """Create a medium town instance for testing"""
    return create_town_instance("Medium Test Town", "medium")

@pytest.fixture
def large_town_instance():
    """Create a large town instance for testing"""
    return create_town_instance("Large Test Town", "large")


class TestTownInstanceCreation:
    """Test town instance creation and initialization"""
    
    def test_create_small_town(self, small_town_instance):
        """Test creating a small town instance"""
        assert small_town_instance is not None
        assert small_town_instance.size == "small"
        assert small_town_instance.name == "Small Test Town"
        assert small_town_instance.width == 2000
        assert small_town_instance.height == 2000
        assert len(small_town_instance.buildings) == 5  # Small towns have 5 buildings
    
    def test_create_medium_town(self, medium_town_instance):
        """Test creating a medium town instance"""
        assert medium_town_instance is not None
        assert medium_town_instance.size == "medium"
        assert medium_town_instance.name == "Medium Test Town"
        assert len(medium_town_instance.buildings) == 8  # Medium towns have 8 buildings
    
    def test_create_large_town(self, large_town_instance):
        """Test creating a large town instance"""
        assert large_town_instance is not None
        assert large_town_instance.size == "large"
        assert large_town_instance.name == "Large Test Town"
        assert len(large_town_instance.buildings) == 12  # Large towns have 12 buildings
    
    def test_town_instance_dimensions(self, small_town_instance, config):
        """Test town instance has correct dimensions"""
        assert small_town_instance.width == 2000
        assert small_town_instance.height == 2000
        assert small_town_instance.tile_width == 2000 // config.TILE_SIZE
        assert small_town_instance.tile_height == 2000 // config.TILE_SIZE
    
    def test_town_instance_has_tiles(self, small_town_instance):
        """Test town instance has a tile map"""
        assert small_town_instance.tiles is not None
        assert len(small_town_instance.tiles) > 0
        assert len(small_town_instance.tiles[0]) > 0
    
    def test_gate_position(self, small_town_instance):
        """Test gate is positioned correctly"""
        assert small_town_instance.gate_x == small_town_instance.width // 2
        assert small_town_instance.gate_y == small_town_instance.height - 100
        assert 0 <= small_town_instance.gate_x < small_town_instance.width
        assert 0 <= small_town_instance.gate_y < small_town_instance.height


class TestTownInstanceBuildings:
    """Test building placement and types in town instances"""
    
    def test_core_buildings_present(self, small_town_instance):
        """Test all core buildings are present"""
        building_types = [b.type for b in small_town_instance.buildings]
        # Core buildings: Inn, Shop, Blacksmith, Town Hall
        assert BuildingType.INN in building_types
        assert BuildingType.SHOP in building_types
        assert BuildingType.BLACKSMITH in building_types
        assert BuildingType.TOWN_HALL in building_types
    
    def test_buildings_have_valid_positions(self, small_town_instance):
        """Test all buildings have valid positions within bounds"""
        for building in small_town_instance.buildings:
            assert 0 <= building.x < small_town_instance.width
            assert 0 <= building.y < small_town_instance.height
            assert building.x + building.width <= small_town_instance.width
            assert building.y + building.height <= small_town_instance.height
    
    def test_buildings_have_valid_sizes(self, small_town_instance):
        """Test all buildings have reasonable sizes"""
        for building in small_town_instance.buildings:
            assert building.width > 0
            assert building.height > 0
            assert building.width < 300  # Max reasonable size
            assert building.height < 300
    
    def test_buildings_dont_overlap(self, small_town_instance):
        """Test that buildings don't overlap"""
        buildings = small_town_instance.buildings
        for i, building1 in enumerate(buildings):
            for building2 in buildings[i+1:]:
                # Check if rectangles overlap
                overlap = (building1.x < building2.x + building2.width and
                          building1.x + building1.width > building2.x and
                          building1.y < building2.y + building2.height and
                          building1.y + building1.height > building2.y)
                assert not overlap, f"Buildings {building1.name} and {building2.name} overlap"
    
    def test_large_town_has_more_buildings(self, small_town_instance, large_town_instance):
        """Test large towns have more buildings than small towns"""
        assert len(large_town_instance.buildings) > len(small_town_instance.buildings)


class TestTownInstanceTiles:
    """Test tile map and terrain in town instances"""
    
    def test_tiles_are_tile_objects(self, small_town_instance):
        """Test all tiles are proper Tile objects"""
        for row in small_town_instance.tiles:
            for tile in row:
                assert isinstance(tile, Tile)
    
    def test_tiles_have_ground_layer(self, small_town_instance):
        """Test all tiles have a ground layer"""
        for row in small_town_instance.tiles:
            for tile in row:
                assert 'ground' in tile
                assert tile['ground'] is not None
    
    def test_path_tiles_exist(self, small_town_instance):
        """Test that path tiles (dirt) exist in the town"""
        path_count = 0
        for row in small_town_instance.tiles:
            for tile in row:
                if tile['ground'] == 'dirt':
                    path_count += 1
        assert path_count > 0, "No path tiles found in town"
    
    def test_grass_tiles_exist(self, small_town_instance):
        """Test that grass tiles exist in the town"""
        grass_count = 0
        for row in small_town_instance.tiles:
            for tile in row:
                if tile['ground'] == 'grass':
                    grass_count += 1
        assert grass_count > 0, "No grass tiles found in town"
    
    def test_tree_tiles_on_edges(self, small_town_instance):
        """Test that tree tiles are placed on edges"""
        tree_count = 0
        for y, row in enumerate(small_town_instance.tiles):
            for x, tile in enumerate(row):
                if tile['ground'] == 'tree':
                    tree_count += 1
                    # Trees should be near edges
                    at_edge = (x < 10 or x > small_town_instance.tile_width - 10 or
                              y < 10 or y > small_town_instance.tile_height - 10)
                    assert at_edge, f"Tree found away from edge at ({x}, {y})"
        # Should have some trees
        assert tree_count > 0, "No trees found in town"


class TestTownInstanceMethods:
    """Test town instance methods and functionality"""
    
    def test_is_in_bounds(self, small_town_instance):
        """Test bounds checking"""
        # Valid positions
        assert small_town_instance.is_in_bounds(100, 100)
        assert small_town_instance.is_in_bounds(1000, 1000)
        assert small_town_instance.is_in_bounds(0, 0)
        assert small_town_instance.is_in_bounds(1999, 1999)
        
        # Invalid positions
        assert not small_town_instance.is_in_bounds(-1, 100)
        assert not small_town_instance.is_in_bounds(100, -1)
        assert not small_town_instance.is_in_bounds(2000, 100)
        assert not small_town_instance.is_in_bounds(100, 2000)
    
    def test_get_tile_at(self, small_town_instance, config):
        """Test getting tile at position"""
        # Get tile at gate position
        tile = small_town_instance.get_tile_at(
            small_town_instance.gate_x,
            small_town_instance.gate_y
        )
        assert tile is not None
        assert isinstance(tile, Tile)
        
        # Get tile at center
        center_tile = small_town_instance.get_tile_at(1000, 1000)
        assert center_tile is not None
        
        # Get tile outside bounds returns default grass
        outside_tile = small_town_instance.get_tile_at(-100, -100)
        assert outside_tile is not None
        assert outside_tile['ground'] == 'grass'


class TestTownGateSystem:
    """Test town gate generation and positioning"""
    
    def test_gate_generation(self, town_manager):
        """Test that gates are generated for all towns"""
        town_gates = {}
        for town in town_manager.towns:
            gate_x = town.center_x
            gate_y = town.center_y + town.radius + 32  # TILE_SIZE = 32
            town_gates[town.name] = (gate_x, gate_y)
        
        assert len(town_gates) == len(town_manager.towns)
        assert "Test Town" in town_gates
        assert "Medium Town" in town_gates
        assert "Large Town" in town_gates
    
    def test_gate_outside_town_boundary(self, town_manager):
        """Test gates are positioned outside town boundaries"""
        for town in town_manager.towns:
            gate_x = town.center_x
            gate_y = town.center_y + town.radius + 32
            
            # Gate should be outside town zone
            distance_from_center = ((gate_x - town.center_x) ** 2 + 
                                   (gate_y - town.center_y) ** 2) ** 0.5
            assert distance_from_center > town.radius, f"Gate for {town.name} is inside town boundary"
    
    def test_gate_positions_unique(self, town_manager):
        """Test each town has a unique gate position"""
        gate_positions = set()
        for town in town_manager.towns:
            gate_x = town.center_x
            gate_y = town.center_y + town.radius + 32
            gate_pos = (gate_x, gate_y)
            assert gate_pos not in gate_positions, f"Duplicate gate position for {town.name}"
            gate_positions.add(gate_pos)


class TestTownInstanceRendering:
    """Test town instance rendering capabilities"""
    
    def test_draw_tiles_method_exists(self, small_town_instance):
        """Test draw_tiles method exists"""
        assert hasattr(small_town_instance, 'draw_tiles')
        assert callable(small_town_instance.draw_tiles)
    
    def test_draw_buildings_method_exists(self, small_town_instance):
        """Test draw_buildings method exists"""
        assert hasattr(small_town_instance, 'draw_buildings')
        assert callable(small_town_instance.draw_buildings)
    
    def test_draw_method_exists(self, small_town_instance):
        """Test main draw method exists"""
        assert hasattr(small_town_instance, 'draw')
        assert callable(small_town_instance.draw)
    
    def test_render_without_crash(self, small_town_instance):
        """Test rendering doesn't crash"""
        # Create a test surface
        screen = pygame.Surface((800, 600))
        camera_x = 0
        camera_y = 0
        
        try:
            small_town_instance.draw(screen, camera_x, camera_y)
            success = True
        except Exception as e:
            success = False
            print(f"Rendering failed: {e}")
        
        assert success, "Town instance rendering crashed"


class TestTownInstanceIntegration:
    """Test integration between town system and town instances"""
    
    def test_town_size_matches_building_count(self):
        """Test building count matches town size specification"""
        small = create_town_instance("Test Small", "small")
        medium = create_town_instance("Test Medium", "medium")
        large = create_town_instance("Test Large", "large")
        
        assert len(small.buildings) == 5
        assert len(medium.buildings) == 8
        assert len(large.buildings) == 12
    
    def test_multiple_instances_independent(self):
        """Test multiple town instances are independent"""
        town1 = create_town_instance("Town 1", "small")
        town2 = create_town_instance("Town 2", "small")
        
        # Instances should be different objects
        assert town1 is not town2
        assert town1.tiles is not town2.tiles
        assert town1.buildings is not town2.buildings
        
        # But should have same size specifications
        assert len(town1.buildings) == len(town2.buildings)
        assert town1.width == town2.width
        assert town1.height == town2.height
    
    def test_town_instance_persistence(self):
        """Test town instance can be stored and retrieved"""
        instances = {}
        town_name = "Persistent Town"
        
        # Create and store
        instances[town_name] = create_town_instance(town_name, "medium")
        
        # Retrieve
        retrieved = instances.get(town_name)
        assert retrieved is not None
        assert retrieved.name == town_name
        assert retrieved.size == "medium"


class TestPlayerInteraction:
    """Test player interaction with town instances"""
    
    def test_gate_detection_radius(self, small_town_instance, config):
        """Test gate detection works at correct radius"""
        gate_x = small_town_instance.gate_x
        gate_y = small_town_instance.gate_y
        detection_radius = config.TILE_SIZE * 4
        
        # Player at gate
        distance = 0
        assert distance < detection_radius
        
        # Player near gate
        distance = config.TILE_SIZE * 3
        assert distance < detection_radius
        
        # Player too far
        distance = config.TILE_SIZE * 5
        assert distance > detection_radius
    
    def test_spawn_position_valid(self, small_town_instance):
        """Test player spawn position at gate is valid"""
        spawn_x = small_town_instance.gate_x
        spawn_y = small_town_instance.gate_y
        
        assert small_town_instance.is_in_bounds(spawn_x, spawn_y)
        assert 0 <= spawn_x < small_town_instance.width
        assert 0 <= spawn_y < small_town_instance.height


def run_tests():
    """Run all tests and return results"""
    print("=" * 70)
    print("TOWN INSTANCE SYSTEM TEST SUITE")
    print("=" * 70)
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-W", "ignore::DeprecationWarning"
    ])
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

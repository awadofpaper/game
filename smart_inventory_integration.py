"""
Smart Inventory Integration
Helper functions to integrate smart inventory with existing game systems
"""

def integrate_smart_inventory_with_player(player, smart_inventory_manager):
    """Connect smart inventory manager to player for seamless integration"""
    # Store reference for auto-pickup and other systems
    player.smart_inventory_manager = smart_inventory_manager
    
    # Enhance player's inventory_system add_item method to use smart features
    if hasattr(player, 'inventory_system') and hasattr(player.inventory_system, 'add_item'):
        original_add_item = player.inventory_system.add_item
        
        def smart_add_item(item_id, quantity=1, item_data=None):
            # Use smart inventory for better stacking and organization
            return smart_inventory_manager.add_item_smart(item_id, quantity, item_data)
        
        # Replace the method while keeping original as backup
        player.inventory_system.add_item_smart = smart_add_item
        player.inventory_system.add_item_original = original_add_item
    
    # Add convenience methods
    player.sort_inventory = lambda: smart_inventory_manager.smart_sort(force=True)
    player.consolidate_inventory = lambda: smart_inventory_manager.consolidate_stacks()
    
    return True

def setup_smart_inventory_hotkeys():
    """Get hotkey mappings for smart inventory"""
    return {
        "toggle_inventory": "F6",
        "sort_by_type": "1",
        "sort_by_rarity": "2", 
        "sort_by_value": "3",
        "sort_by_name": "4",
        "consolidate_stacks": "C",
        "sell_junk": "J",
        "toggle_auto_sort": "S",
        "search": "F",
        "toggle_favorite": "SPACE"
    }
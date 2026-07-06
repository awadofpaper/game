"""
Tutorial Manager - Tracks which tutorials have been shown to the player
"""

import json
import os

class TutorialManager:
    """Manages tutorial state and progress"""
    
    def __init__(self):
        self.tutorials_shown = {
            'inventory': False,
            'equipment': False,
            'crafting': False,
            'stats': False,
            'quests': False,
            'map': False,
            'skills': False,
            'smart_inventory': False,
            'spells': False
        }
        self.save_file = "tutorial_progress.json"
        self.load_data()
    
    def should_show_tutorial(self, menu_name):
        """Check if tutorial should display for a menu"""
        return not self.tutorials_shown.get(menu_name, False)
    
    def mark_shown(self, menu_name):
        """Mark tutorial as seen"""
        if menu_name in self.tutorials_shown:
            self.tutorials_shown[menu_name] = True
            self.save_data()
    
    def reset_tutorial(self, menu_name):
        """Reset a specific tutorial (for testing or user request)"""
        if menu_name in self.tutorials_shown:
            self.tutorials_shown[menu_name] = False
            self.save_data()
    
    def reset_all_tutorials(self):
        """Reset all tutorials"""
        for key in self.tutorials_shown.keys():
            self.tutorials_shown[key] = False
        self.save_data()
    
    def save_data(self):
        """Save tutorial progress to file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.tutorials_shown, f, indent=2)
        except Exception as e:
            print(f"Error saving tutorial data: {e}")
    
    def load_data(self):
        """Load tutorial progress from file"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    loaded_data = json.load(f)
                    # Update with loaded data but keep any new tutorial keys
                    for key, value in loaded_data.items():
                        if key in self.tutorials_shown:
                            self.tutorials_shown[key] = value
            except Exception as e:
                print(f"Error loading tutorial data: {e}")
    
    def get_progress_summary(self):
        """Get summary of tutorial completion"""
        total = len(self.tutorials_shown)
        completed = sum(1 for shown in self.tutorials_shown.values() if shown)
        return completed, total

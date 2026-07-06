"""
Leaderboard System - Global skill rankings for all players

Tracks top players in each skill:
- Mining
- Woodcutting
- Fishing
- Cooking
- Merchant
- Athletics
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class LeaderboardEntry:
    """Single entry in a leaderboard"""
    
    def __init__(self, player_name: str, level: int, xp: int, last_updated: str = None):
        self.player_name = player_name
        self.level = level
        self.xp = xp
        self.last_updated = last_updated or datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self):
        return {
            'player_name': self.player_name,
            'level': self.level,
            'xp': self.xp,
            'last_updated': self.last_updated
        }
    
    @staticmethod
    def from_dict(data):
        return LeaderboardEntry(
            data['player_name'],
            data['level'],
            data['xp'],
            data.get('last_updated')
        )


class LeaderboardSystem:
    """Manages global skill leaderboards"""
    
    SKILLS = [
        'Mining',
        'Woodcutting',
        'Fishing',
        'Cooking',
        'Merchant',
        'Athletics'
    ]
    
    MAX_ENTRIES = 100  # Top 100 for each skill
    
    def __init__(self, save_file='leaderboards.json'):
        self.save_file = save_file
        self.leaderboards: Dict[str, List[LeaderboardEntry]] = {}
        
        # Initialize empty leaderboards for each skill
        for skill in self.SKILLS:
            self.leaderboards[skill] = []
        
        # Load existing data
        self.load()
    
    def update_player(self, player_name: str, skill_name: str, level: int, xp: int):
        """
        Update or add a player's entry in a skill leaderboard
        
        Args:
            player_name: Player's name
            skill_name: Skill to update
            level: Current skill level
            xp: Current skill XP
        """
        if skill_name not in self.SKILLS:
            return
        
        leaderboard = self.leaderboards[skill_name]
        
        # Find existing entry for this player
        existing_idx = None
        for i, entry in enumerate(leaderboard):
            if entry.player_name == player_name:
                existing_idx = i
                break
        
        # Create or update entry
        new_entry = LeaderboardEntry(player_name, level, xp)
        
        if existing_idx is not None:
            # Update existing entry
            leaderboard[existing_idx] = new_entry
        else:
            # Add new entry
            leaderboard.append(new_entry)
        
        # Sort by XP (descending), then by level (descending)
        leaderboard.sort(key=lambda e: (e.xp, e.level), reverse=True)
        
        # Keep only top MAX_ENTRIES
        if len(leaderboard) > self.MAX_ENTRIES:
            self.leaderboards[skill_name] = leaderboard[:self.MAX_ENTRIES]
    
    def update_all_skills(self, player_name: str, skills_manager):
        """
        Update all skills for a player based on their SkillsManager
        
        Args:
            player_name: Player's name
            skills_manager: Player's SkillsManager instance
        """
        for skill in self.SKILLS:
            level = skills_manager.get_level(skill)
            xp = skills_manager.get_xp(skill)
            self.update_player(player_name, skill, level, xp)
    
    def get_rankings(self, skill_name: str, limit: int = 50) -> List[LeaderboardEntry]:
        """
        Get top players for a skill
        
        Args:
            skill_name: Skill to get rankings for
            limit: Maximum number of entries to return
        
        Returns:
            List of LeaderboardEntry objects
        """
        if skill_name not in self.SKILLS:
            return []
        
        return self.leaderboards[skill_name][:limit]
    
    def get_player_rank(self, player_name: str, skill_name: str) -> Optional[Tuple[int, LeaderboardEntry]]:
        """
        Get a player's rank in a specific skill
        
        Args:
            player_name: Player's name
            skill_name: Skill to check
        
        Returns:
            Tuple of (rank, entry) or None if not found
            Rank is 1-indexed (1 = first place)
        """
        if skill_name not in self.SKILLS:
            return None
        
        for i, entry in enumerate(self.leaderboards[skill_name]):
            if entry.player_name == player_name:
                return (i + 1, entry)
        
        return None
    
    def get_player_total_level(self, player_name: str) -> int:
        """
        Get a player's total level across all skills
        
        Args:
            player_name: Player's name
        
        Returns:
            Sum of all skill levels
        """
        total = 0
        for skill in self.SKILLS:
            rank_data = self.get_player_rank(player_name, skill)
            if rank_data:
                _, entry = rank_data
                total += entry.level
        return total
    
    def get_overall_rankings(self, limit: int = 50) -> List[Tuple[str, int]]:
        """
        Get overall rankings based on total level
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of (player_name, total_level) tuples, sorted by total level
        """
        # Collect all unique player names
        all_players = set()
        for skill in self.SKILLS:
            for entry in self.leaderboards[skill]:
                all_players.add(entry.player_name)
        
        # Calculate total levels
        totals = []
        for player_name in all_players:
            total = self.get_player_total_level(player_name)
            totals.append((player_name, total))
        
        # Sort by total level (descending)
        totals.sort(key=lambda x: x[1], reverse=True)
        
        return totals[:limit]
    
    def save(self):
        """Save leaderboards to file"""
        data = {}
        for skill, entries in self.leaderboards.items():
            data[skill] = [entry.to_dict() for entry in entries]
        
        try:
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[LEADERBOARD] Error saving: {e}")
            return False
    
    def load(self):
        """Load leaderboards from file"""
        if not os.path.exists(self.save_file):
            return False
        
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
            
            for skill, entries_data in data.items():
                if skill in self.SKILLS:
                    self.leaderboards[skill] = [
                        LeaderboardEntry.from_dict(entry_data)
                        for entry_data in entries_data
                    ]
            
            return True
        except Exception as e:
            print(f"[LEADERBOARD] Error loading: {e}")
            return False
    
    def clear_leaderboard(self, skill_name: str):
        """Clear a specific skill leaderboard"""
        if skill_name in self.SKILLS:
            self.leaderboards[skill_name] = []
    
    def clear_all(self):
        """Clear all leaderboards"""
        for skill in self.SKILLS:
            self.leaderboards[skill] = []
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the leaderboards"""
        stats = {}
        for skill in self.SKILLS:
            stats[skill] = len(self.leaderboards[skill])
        stats['total_players'] = len(set(
            entry.player_name
            for skill_entries in self.leaderboards.values()
            for entry in skill_entries
        ))
        return stats

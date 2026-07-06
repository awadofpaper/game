"""
Crime & Punishment System
Handles guard searches, wanted durations, town cooldowns, investigations, jail work, multi-stage escapes, and penalties.
"""
import random
import time

class StolenItem:
    def __init__(self, item_id, name):
        self.item_id = item_id
        self.name = name
        self.is_stolen = True
        self.red_x = True  # Marked as stolen

class GuardSearchSystem:
    def __init__(self):
        pass

    def search_player(self, player, leaving_town_hall=True):
        """Search player for stolen items. Returns list of StolenItem objects found."""
        if not hasattr(player, 'stolen_items'):
            return []
        
        # If leaving town hall or being arrested, perform thorough search
        if leaving_town_hall:
            stolen_items = [item for item in player.stolen_items if getattr(item, 'is_stolen', False)]
            # Mark all stolen items with red X
            for item in stolen_items:
                item.red_x = True
            return stolen_items
        return []

class WantedSystem:
    def __init__(self):
        self.wanted_players = {}  # {player_id: {'reason': str, 'duration': int, 'start_day': int}}

    def set_wanted(self, player_id, reason, game_time, escape_days=0):
        if reason == 'escape':
            duration = escape_days
        elif reason == 'abandonment':
            duration = 365  # 1 year
        elif reason == 'investigation':
            duration = 60  # 2 months
        elif reason == 'murder':
            duration = 90  # 3 months for witnessed murder
        else:
            duration = 30  # Default
        self.wanted_players[player_id] = {
            'reason': reason,
            'duration': duration,
            'start_day': game_time.day_count
        }

    def get_wanted_status(self, player_id, game_time):
        info = self.wanted_players.get(player_id)
        if not info:
            return False
        days_wanted = game_time.day_count - info['start_day']
        return days_wanted < info['duration']

class TownCooldownSystem:
    def __init__(self):
        self.cooldowns = {}  # {player_id: {'town': str, 'end_day': int}}

    def set_cooldown(self, player_id, town_name, game_time):
        self.cooldowns[player_id] = {'town': town_name, 'end_day': game_time.day_count + 3}

    def is_on_cooldown(self, player_id, town_name, game_time):
        info = self.cooldowns.get(player_id)
        if not info or info['town'] != town_name:
            return False
        return game_time.day_count < info['end_day']

class InvestigationSystem:
    def __init__(self):
        self.investigations = {}  # {body_id: {'start_day': int, 'player_id': str, 'victim_name': str, 'location': str, 'witnessed': bool}}

    def start_investigation(self, body_id, player_id, game_time, victim_name="Unknown", location="Unknown", witnessed=False):
        self.investigations[body_id] = {
            'start_day': game_time.day_count, 
            'player_id': player_id,
            'victim_name': victim_name,
            'location': location,
            'witnessed': witnessed
        }

    def update(self, game_time, wanted_system):
        """Check for completed investigations and return list of results"""
        completed = []
        for body_id, info in list(self.investigations.items()):
            days = game_time.day_count - info['start_day']
            if days >= 1:
                # Only set wanted status for unwitnessed murders (witnessed already got instant wanted)
                if not info.get('witnessed', False):
                    wanted_system.set_wanted(info['player_id'], 'investigation', game_time)
                completed.append({
                    'player_id': info['player_id'],
                    'victim_name': info['victim_name'],
                    'location': info['location'],
                    'body_id': body_id,
                    'witnessed': info.get('witnessed', False)
                })
                del self.investigations[body_id]
        return completed

class JailWorkSystem:
    def __init__(self):
        self.jail_sentences = {}  # {player_id: {'sentence': int, 'worked_days': int}}

    def set_sentence(self, player_id, sentence_days):
        self.jail_sentences[player_id] = {'sentence': sentence_days, 'worked_days': 0}

    def work_day(self, player_id):
        if player_id in self.jail_sentences:
            self.jail_sentences[player_id]['worked_days'] += 1
            self.jail_sentences[player_id]['sentence'] = max(0, self.jail_sentences[player_id]['sentence'] - 1)

    def get_remaining_sentence(self, player_id):
        return self.jail_sentences.get(player_id, {}).get('sentence', 0)

class JailEscapeSystem:
    def __init__(self):
        self.escape_stages = ['cell', 'block', 'entrance', 'gate']
        self.stage_lockpicking = {
            'cell': 'basic',
            'block': 'improved',
            'entrance': 'advanced',
            'gate': 'master'
        }
        self.player_stages = {}  # {player_id: current_stage}

    def start_escape(self, player_id):
        self.player_stages[player_id] = 'cell'

    def advance_stage(self, player_id, lockpicking_skill):
        current = self.player_stages.get(player_id, 'cell')
        idx = self.escape_stages.index(current)
        required = self.stage_lockpicking[current]
        # Simulate lockpicking check
        skill_levels = {'basic': 20, 'improved': 40, 'advanced': 60, 'master': 80}
        if lockpicking_skill >= skill_levels[required]:
            if idx < len(self.escape_stages) - 1:
                self.player_stages[player_id] = self.escape_stages[idx + 1]
                return True, self.player_stages[player_id]
            else:
                del self.player_stages[player_id]
                return True, 'escaped'
        return False, current

    def caught_escaping(self, player_id, jail_work_system):
        # +50 days penalty
        if player_id in jail_work_system.jail_sentences:
            jail_work_system.jail_sentences[player_id]['sentence'] += 50

"""
Election System
Handles campaign promises, emergency election timeline, ballot stuffing, voter bribery, mayor term limits, and anarchy mechanics.
"""
import random
import time

class CampaignPromise:
    PROMISES = [
        "Lower taxes", "More guards", "Weapon restrictions", "Free food", "Better roads", "Cheaper housing",
        "Expanded market", "Festival funding", "Crime crackdown", "Magic regulation", "Trade incentives",
        "Public health", "School funding", "Inn subsidies", "Bank protection", "No curfew"
    ]
    def __init__(self, promise_id, description):
        self.promise_id = promise_id
        self.description = description
        self.fulfilled = False
        self.impact = random.randint(1, 5)  # Popularity impact

class CampaignPromiseSystem:
    def __init__(self):
        self.promises = [CampaignPromise(i, desc) for i, desc in enumerate(CampaignPromise.PROMISES)]
        self.active_promises = []

    def choose_promises(self, num=3):
        self.active_promises = random.sample(self.promises, num)
        return self.active_promises

    def fulfill_promise(self, promise_id):
        for p in self.active_promises:
            if p.promise_id == promise_id:
                p.fulfilled = True
                return p
        return None

class ElectionTimeline:
    def __init__(self, game_time):
        self.game_time = game_time
        self.state = "anarchy"  # anarchy, campaign, voting, results, inauguration
        self.anarchy_start_day = None
        self.campaign_start_day = None
        self.voting_day = None
        self.inauguration_day = None
        self.days_in_anarchy = 0
        self.days_in_campaign = 0

    def start_anarchy(self):
        self.state = "anarchy"
        self.anarchy_start_day = self.game_time.day_count
        self.days_in_anarchy = 0

    def update(self):
        if self.state == "anarchy":
            self.days_in_anarchy = self.game_time.day_count - self.anarchy_start_day
            if self.days_in_anarchy >= 7:
                self.state = "campaign"
                self.campaign_start_day = self.game_time.day_count
                self.days_in_campaign = 0
        elif self.state == "campaign":
            self.days_in_campaign = self.game_time.day_count - self.campaign_start_day
            if self.days_in_campaign >= 3:
                self.state = "voting"
                self.voting_day = self.game_time.day_count
        elif self.state == "voting":
            # Voting lasts 1 day
            if self.game_time.day_count > self.voting_day:
                self.state = "results"
                self.inauguration_day = self.game_time.day_count + 1
        elif self.state == "results":
            if self.game_time.day_count >= self.inauguration_day:
                self.state = "inauguration"

class BallotBox:
    def __init__(self):
        self.locked = True
        self.ballots = []  # List of candidate names who received votes
        self.stuffed_ballots = 0
        self.candidates = []  # List of candidate names
        self.legitimate_votes = 0  # Track legitimate votes separately
        self.voter_ids = set()  # Track who has voted (prevent double-voting)

    def reset_for_election(self):
        """Reset ballot box for a new election"""
        self.ballots = []
        self.stuffed_ballots = 0
        self.legitimate_votes = 0
        self.voter_ids = set()
        self.locked = True
        self.candidates = []

    def register_candidates(self, candidate_list):
        """Register the candidates for this election"""
        self.candidates = candidate_list.copy()

    def cast_vote(self, candidate_name, voter_id):
        """Cast a legitimate vote (used by player and NPCs)"""
        if voter_id in self.voter_ids:
            return False, "You have already voted in this election"
        
        if candidate_name not in self.candidates:
            return False, f"{candidate_name} is not a registered candidate"
        
        self.ballots.append(candidate_name)
        self.legitimate_votes += 1
        self.voter_ids.add(voter_id)
        return True, f"Vote cast for {candidate_name}"

    def lockpick(self, skill):
        # skill: 0-100
        chance = min(95, skill + 20)
        success = random.randint(1, 100) <= chance
        detected = random.randint(1, 100) < 30  # 30% detection chance
        if success:
            self.locked = False
        return success, detected

    def stuff_ballot(self, candidate_id):
        """Illegally stuff a ballot (requires lockpicking first)"""
        if not self.locked:
            self.ballots.append(candidate_id)
            self.stuffed_ballots += 1
            return True
        return False
    
    def count_votes(self):
        """Count all votes and return results"""
        vote_counts = {}
        for candidate in self.candidates:
            vote_counts[candidate] = 0
        
        for ballot in self.ballots:
            if ballot in vote_counts:
                vote_counts[ballot] += 1
            else:
                # Stuffed ballot for non-candidate
                vote_counts[ballot] = vote_counts.get(ballot, 0) + 1
        
        # Sort by vote count (descending)
        sorted_results = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'results': sorted_results,
            'total_votes': len(self.ballots),
            'legitimate_votes': self.legitimate_votes,
            'stuffed_ballots': self.stuffed_ballots,
            'winner': sorted_results[0][0] if sorted_results and sorted_results[0][1] > 0 else None
        }

class VoterBriberySystem:
    def __init__(self):
        self.bribed_npcs = set()
        self.bribe_amount = 1000

    def bribe(self, npc_id, player_gold, town_treasury_system=None, town_name=None):
        if player_gold >= self.bribe_amount:
            self.bribed_npcs.add(npc_id)
            # Bribes go to town treasury (corruption money)
            if town_treasury_system and town_name:
                town_treasury_system.deposit(town_name, self.bribe_amount, "Bribe")
            return True, player_gold - self.bribe_amount
        return False, player_gold

    def is_bribed(self, npc_id):
        return npc_id in self.bribed_npcs

class MayorTermSystem:
    def __init__(self):
        self.mayor_id = None
        self.term_start_day = None
        self.term_length = 730  # 2 years in days
        self.last_term_end_day = None
        self.term_limit_break = 730  # 2 years mandatory break

    def start_term(self, mayor_id, game_time):
        self.mayor_id = mayor_id
        self.term_start_day = game_time.day_count
        self.last_term_end_day = None

    def end_term(self, game_time):
        self.last_term_end_day = game_time.day_count
        self.mayor_id = None
        self.term_start_day = None

    def can_run_again(self, game_time):
        if self.last_term_end_day is None:
            return True
        return (game_time.day_count - self.last_term_end_day) >= self.term_limit_break

class AnarchySystem:
    def __init__(self, mayor_popularity):
        self.mayor_popularity = mayor_popularity
        self.anarchy_active = False

    def check_anarchy(self):
        if self.mayor_popularity <= 8:
            self.anarchy_active = True
            return True
        self.anarchy_active = False
        return False

    def apply_anarchy_effects(self, town_manager):
        if self.anarchy_active:
            for town in town_manager.towns:
                town.law_enforcement = False
        else:
            for town in town_manager.towns:
                town.law_enforcement = True

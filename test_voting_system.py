"""Test Ballot Box and Voting System Integration"""
import sys
sys.path.insert(0, 'C:\\Users\\Public\\rpg_game')

from election_system import BallotBox, ElectionTimeline
from game_time import GameTime

class MockGameTime:
    def __init__(self):
        self.day_count = 0

class MockPlayer:
    def __init__(self):
        self.can_vote = True
        self.voted_this_election = False
        self.is_mayor = False

def test_ballot_box_initialization():
    """Test 1: Ballot Box Initialization"""
    ballot_box = BallotBox()
    
    assert ballot_box.locked == True, "Ballot box should start locked"
    assert len(ballot_box.ballots) == 0, "Should have no ballots initially"
    assert ballot_box.stuffed_ballots == 0, "Should have no stuffed ballots"
    assert ballot_box.legitimate_votes == 0, "Should have no legitimate votes"
    assert len(ballot_box.candidates) == 0, "Should have no candidates initially"
    assert len(ballot_box.voter_ids) == 0, "Should have no voters tracked"
    
    print("✓ Test 1: Ballot Box Initialization - All fields correct")

def test_register_candidates():
    """Test 2: Register Candidates"""
    ballot_box = BallotBox()
    candidates = ["Player", "Alice", "Bob", "Charlie"]
    
    ballot_box.register_candidates(candidates)
    
    assert len(ballot_box.candidates) == 4, f"Expected 4 candidates, got {len(ballot_box.candidates)}"
    assert "Player" in ballot_box.candidates, "Player should be a candidate"
    assert "Alice" in ballot_box.candidates, "Alice should be a candidate"
    
    print(f"✓ Test 2: Register Candidates - {len(ballot_box.candidates)} candidates registered")

def test_cast_legitimate_vote():
    """Test 3: Cast Legitimate Vote"""
    ballot_box = BallotBox()
    ballot_box.register_candidates(["Player", "Alice", "Bob"])
    
    # Cast vote
    success, message = ballot_box.cast_vote("Alice", "voter_1")
    
    assert success == True, "Vote should succeed"
    assert "Alice" in message, "Message should mention candidate"
    assert len(ballot_box.ballots) == 1, "Should have 1 ballot"
    assert ballot_box.legitimate_votes == 1, "Should have 1 legitimate vote"
    assert ballot_box.stuffed_ballots == 0, "Should have no stuffed ballots"
    assert "voter_1" in ballot_box.voter_ids, "Voter should be tracked"
    
    print(f"✓ Test 3: Cast Legitimate Vote - {message}")

def test_prevent_double_voting():
    """Test 4: Prevent Double Voting"""
    ballot_box = BallotBox()
    ballot_box.register_candidates(["Player", "Alice", "Bob"])
    
    # Cast first vote
    success1, message1 = ballot_box.cast_vote("Alice", "voter_1")
    assert success1 == True, "First vote should succeed"
    
    # Try to vote again with same voter_id
    success2, message2 = ballot_box.cast_vote("Bob", "voter_1")
    assert success2 == False, "Second vote should fail"
    assert "already voted" in message2, "Should indicate already voted"
    assert len(ballot_box.ballots) == 1, "Should still have only 1 ballot"
    
    print(f"✓ Test 4: Prevent Double Voting - {message2}")

def test_invalid_candidate():
    """Test 5: Invalid Candidate Vote"""
    ballot_box = BallotBox()
    ballot_box.register_candidates(["Player", "Alice"])
    
    # Try to vote for non-registered candidate
    success, message = ballot_box.cast_vote("Charlie", "voter_1")
    
    assert success == False, "Vote should fail for invalid candidate"
    assert "not a registered candidate" in message, "Should indicate invalid candidate"
    assert len(ballot_box.ballots) == 0, "Should have no ballots"
    
    print(f"✓ Test 5: Invalid Candidate Vote - {message}")

def test_multiple_voters():
    """Test 6: Multiple Voters"""
    ballot_box = BallotBox()
    ballot_box.register_candidates(["Player", "Alice", "Bob"])
    
    # Multiple voters cast votes
    ballot_box.cast_vote("Alice", "voter_1")
    ballot_box.cast_vote("Bob", "voter_2")
    ballot_box.cast_vote("Alice", "voter_3")
    ballot_box.cast_vote("Player", "voter_4")
    
    assert len(ballot_box.ballots) == 4, f"Should have 4 ballots, got {len(ballot_box.ballots)}"
    assert ballot_box.legitimate_votes == 4, "Should have 4 legitimate votes"
    assert len(ballot_box.voter_ids) == 4, "Should track 4 voters"
    
    print(f"✓ Test 6: Multiple Voters - 4 votes cast successfully")

def test_vote_counting():
    """Test 7: Vote Counting and Results"""
    ballot_box = BallotBox()
    ballot_box.register_candidates(["Player", "Alice", "Bob"])
    
    # Cast votes: Alice gets 3, Player gets 2, Bob gets 1
    ballot_box.cast_vote("Alice", "voter_1")
    ballot_box.cast_vote("Alice", "voter_2")
    ballot_box.cast_vote("Alice", "voter_3")
    ballot_box.cast_vote("Player", "voter_4")
    ballot_box.cast_vote("Player", "voter_5")
    ballot_box.cast_vote("Bob", "voter_6")
    
    results = ballot_box.count_votes()
    
    assert results['total_votes'] == 6, f"Expected 6 total votes, got {results['total_votes']}"
    assert results['legitimate_votes'] == 6, "All votes should be legitimate"
    assert results['stuffed_ballots'] == 0, "No stuffed ballots"
    assert results['winner'] == "Alice", f"Alice should win, got {results['winner']}"
    
    # Check vote counts
    vote_dict = dict(results['results'])
    assert vote_dict['Alice'] == 3, f"Alice should have 3 votes, got {vote_dict['Alice']}"
    assert vote_dict['Player'] == 2, f"Player should have 2 votes, got {vote_dict['Player']}"
    assert vote_dict['Bob'] == 1, f"Bob should have 1 vote, got {vote_dict['Bob']}"
    
    print(f"✓ Test 7: Vote Counting - Winner: {results['winner']} with {vote_dict[results['winner']]} votes")

def test_ballot_stuffing():
    """Test 8: Illegal Ballot Stuffing"""
    ballot_box = BallotBox()
    ballot_box.register_candidates(["Player", "Alice"])
    
    # Locked ballot box - stuffing should fail
    success = ballot_box.stuff_ballot("Player")
    assert success == False, "Cannot stuff ballot when locked"
    
    # Unlock ballot box
    ballot_box.locked = False
    
    # Now stuffing should work (but is illegal!)
    success = ballot_box.stuff_ballot("Player")
    assert success == True, "Should stuff ballot when unlocked"
    assert ballot_box.stuffed_ballots == 1, "Should track stuffed ballots"
    assert ballot_box.legitimate_votes == 0, "Stuffed ballots don't count as legitimate"
    
    print(f"✓ Test 8: Ballot Stuffing - 1 ballot stuffed (illegal)")

def test_reset_for_new_election():
    """Test 9: Reset Ballot Box for New Election"""
    ballot_box = BallotBox()
    ballot_box.register_candidates(["Player", "Alice"])
    ballot_box.cast_vote("Alice", "voter_1")
    ballot_box.cast_vote("Player", "voter_2")
    
    # Reset for new election
    ballot_box.reset_for_election()
    
    assert len(ballot_box.ballots) == 0, "Ballots should be cleared"
    assert ballot_box.stuffed_ballots == 0, "Stuffed ballots should be reset"
    assert ballot_box.legitimate_votes == 0, "Legitimate votes should be reset"
    assert len(ballot_box.voter_ids) == 0, "Voter IDs should be cleared"
    assert len(ballot_box.candidates) == 0, "Candidates should be cleared"
    assert ballot_box.locked == True, "Should be locked again"
    
    print("✓ Test 9: Reset for New Election - All fields cleared")

def test_town_hall_ui_integration():
    """Test 10: Town Hall UI Integration Check"""
    # Read town_hall_system.py to verify integration
    with open('c:\\Users\\Public\\rpg_game\\town_hall_system.py', 'r', encoding='utf-8') as f:
        town_hall_content = f.read()
    
    # Check for voting mode
    assert "self.voting_mode" in town_hall_content, "Missing voting_mode flag"
    assert "self.ballot_box" in town_hall_content, "Missing ballot_box reference"
    assert "self.election_timeline" in town_hall_content, "Missing election_timeline reference"
    
    # Check for voting UI method
    assert "_draw_voting_ui" in town_hall_content, "Missing _draw_voting_ui method"
    
    # Check for candidate selection
    assert "selected_candidate_idx" in town_hall_content, "Missing candidate selection"
    
    print("✓ Test 10: Town Hall UI Integration - voting_mode ✓, ballot_box ✓, draw method ✓")

def test_main_integration():
    """Test 11: Main.py Integration Check"""
    with open('c:\\Users\\Public\\rpg_game\\main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Check ballot_box passed to town hall
    assert "ballot_box, election_timeline)" in main_content, "ballot_box not passed to town_hall_ui.open()"
    
    # Check voting result handling
    assert 'result.startswith("voted:")' in main_content, "Missing vote result handling"
    
    # Check ballot box reset on voting day
    assert "ballot_box.reset_for_election()" in main_content, "Missing ballot box reset"
    assert "ballot_box.register_candidates" in main_content, "Missing candidate registration"
    
    # Check vote counting
    assert "ballot_box.count_votes()" in main_content, "Missing vote counting"
    assert "vote_results['winner']" in main_content, "Missing winner determination"
    
    # Check mayor assignment
    assert 'player.is_mayor = True' in main_content, "Missing mayor assignment"
    
    print("✓ Test 11: Main.py Integration - ballot_box passing ✓, vote handling ✓, counting ✓, winner ✓")

def test_election_cycle_with_voting():
    """Test 12: Complete Election Cycle with Voting"""
    game_time = MockGameTime()
    timeline = ElectionTimeline(game_time)
    ballot_box = BallotBox()
    
    timeline.start_anarchy()
    
    # Fast-forward through anarchy to campaign
    game_time.day_count = 7
    timeline.update()
    assert timeline.state == "campaign", "Should reach campaign"
    
    # Fast-forward through campaign to voting
    game_time.day_count = 10
    timeline.update()
    assert timeline.state == "voting", "Should reach voting"
    
    # Simulate voting day
    ballot_box.reset_for_election()
    ballot_box.register_candidates(["Player", "Alice", "Bob"])
    
    # Simulate votes
    ballot_box.cast_vote("Alice", "voter_1")
    ballot_box.cast_vote("Player", "voter_2")
    ballot_box.cast_vote("Alice", "voter_3")
    
    # Move to results
    game_time.day_count = 11
    timeline.update()
    assert timeline.state == "results", "Should reach results"
    
    # Count votes
    results = ballot_box.count_votes()
    assert results['winner'] == "Alice", "Alice should win with 2 votes"
    
    # Move to inauguration
    game_time.day_count = 12
    timeline.update()
    assert timeline.state == "inauguration", "Should reach inauguration"
    
    print(f"✓ Test 12: Complete Election Cycle - Winner: {results['winner']}")

if __name__ == "__main__":
    print("=" * 60)
    print("BALLOT BOX AND VOTING SYSTEM TESTS")
    print("=" * 60)
    
    test_ballot_box_initialization()
    test_register_candidates()
    test_cast_legitimate_vote()
    test_prevent_double_voting()
    test_invalid_candidate()
    test_multiple_voters()
    test_vote_counting()
    test_ballot_stuffing()
    test_reset_for_new_election()
    test_town_hall_ui_integration()
    test_main_integration()
    test_election_cycle_with_voting()
    
    print("=" * 60)
    print("✓ ALL VOTING SYSTEM INTEGRATION TESTS PASSED!")
    print("=" * 60)

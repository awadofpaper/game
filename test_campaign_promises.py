"""Test Campaign Promise System Integration"""
import sys
sys.path.insert(0, 'C:\\Users\\Public\\rpg_game')

from election_system import CampaignPromise, CampaignPromiseSystem, ElectionTimeline
from game_time import GameTime

class MockGameTime:
    def __init__(self):
        self.day_count = 0

def test_campaign_promise_system():
    """Test 1: Campaign Promise System Initialization"""
    system = CampaignPromiseSystem()
    
    # Verify 16 promises exist
    assert len(system.promises) == 16, f"Expected 16 promises, got {len(system.promises)}"
    assert len(CampaignPromise.PROMISES) == 16, f"Expected 16 promise types, got {len(CampaignPromise.PROMISES)}"
    
    # Verify no active promises initially
    assert len(system.active_promises) == 0, "Should have no active promises initially"
    
    print("✓ Test 1: Campaign Promise System Initialization - 16 promises available")

def test_choose_promises():
    """Test 2: Choose Promises Method"""
    system = CampaignPromiseSystem()
    
    # Choose 3 promises
    selected = system.choose_promises(3)
    
    assert len(selected) == 3, f"Expected 3 promises, got {len(selected)}"
    assert len(system.active_promises) == 3, f"Expected 3 active promises, got {len(system.active_promises)}"
    
    # Verify all selected promises are CampaignPromise objects
    for promise in selected:
        assert isinstance(promise, CampaignPromise), f"Expected CampaignPromise, got {type(promise)}"
        assert hasattr(promise, 'description'), "Promise should have description"
        assert hasattr(promise, 'fulfilled'), "Promise should have fulfilled flag"
    
    print(f"✓ Test 2: Choose Promises - Selected 3: {[p.description for p in selected]}")

def test_fulfill_promise():
    """Test 3: Fulfill Promise Method"""
    system = CampaignPromiseSystem()
    selected = system.choose_promises(3)
    
    # Get first promise ID
    promise_id = selected[0].promise_id
    
    # Fulfill it
    fulfilled = system.fulfill_promise(promise_id)
    
    assert fulfilled is not None, "Fulfill should return the promise object"
    assert fulfilled.fulfilled == True, "Promise should be marked as fulfilled"
    assert fulfilled.promise_id == promise_id, "Promise ID should match"
    
    print(f"✓ Test 3: Fulfill Promise - Fulfilled '{fulfilled.description}'")

def test_election_timeline_states():
    """Test 4: Election Timeline State Transitions"""
    game_time = MockGameTime()
    timeline = ElectionTimeline(game_time)
    
    # Start in anarchy
    timeline.start_anarchy()
    assert timeline.state == "anarchy", f"Expected anarchy, got {timeline.state}"
    
    # Should stay in anarchy for 7 days
    for day in range(7):
        game_time.day_count = day
        timeline.update()
        if day < 6:
            assert timeline.state == "anarchy", f"Day {day}: Should still be anarchy, got {timeline.state}"
    
    # Day 7 - should transition to campaign
    game_time.day_count = 7
    timeline.update()
    assert timeline.state == "campaign", f"Day 7: Should be campaign, got {timeline.state}"
    assert timeline.days_in_campaign == 0, f"Campaign days should be 0, got {timeline.days_in_campaign}"
    
    print(f"✓ Test 4: Election Timeline - Anarchy (7 days) → Campaign")

def test_campaign_period():
    """Test 5: Campaign Period Duration"""
    game_time = MockGameTime()
    timeline = ElectionTimeline(game_time)
    
    # Start at day 7 (end of anarchy)
    game_time.day_count = 0
    timeline.start_anarchy()
    
    # Fast-forward to campaign start
    game_time.day_count = 7
    timeline.update()
    assert timeline.state == "campaign", "Should be in campaign"
    
    # Campaign should last 3 days
    for day in range(3):
        actual_day = 7 + day
        game_time.day_count = actual_day
        timeline.update()
        if day < 2:
            assert timeline.state == "campaign", f"Day {actual_day}: Should still be campaign, got {timeline.state}"
            assert timeline.days_in_campaign == day, f"Campaign day should be {day}, got {timeline.days_in_campaign}"
    
    # Day 10 - should transition to voting
    game_time.day_count = 10
    timeline.update()
    assert timeline.state == "voting", f"Day 10: Should be voting, got {timeline.state}"
    
    print(f"✓ Test 5: Campaign Period - 3 days duration")

def test_full_election_cycle():
    """Test 6: Full Election Cycle"""
    game_time = MockGameTime()
    timeline = ElectionTimeline(game_time)
    
    timeline.start_anarchy()
    
    states_timeline = []
    
    for day in range(15):
        game_time.day_count = day
        timeline.update()
        states_timeline.append((day, timeline.state))
    
    # Verify state transitions
    # Days 0-6: anarchy (7 days)
    # Days 7-9: campaign (3 days)
    # Day 10: voting (1 day)
    # Day 11: results
    # Day 12+: inauguration
    
    expected_states = [
        (0, "anarchy"), (1, "anarchy"), (2, "anarchy"), (3, "anarchy"), 
        (4, "anarchy"), (5, "anarchy"), (6, "anarchy"),
        (7, "campaign"), (8, "campaign"), (9, "campaign"),
        (10, "voting"), (11, "results"), (12, "inauguration")
    ]
    
    for expected_day, expected_state in expected_states:
        actual_state = states_timeline[expected_day][1]
        assert actual_state == expected_state, f"Day {expected_day}: Expected {expected_state}, got {actual_state}"
    
    print(f"✓ Test 6: Full Election Cycle - All states transition correctly")

def test_promise_types():
    """Test 7: All 16 Promise Types"""
    expected_promises = [
        "Lower taxes", "More guards", "Weapon restrictions", "Free food", 
        "Better roads", "Cheaper housing", "Expanded market", "Festival funding",
        "Crime crackdown", "Magic regulation", "Trade incentives", "Public health",
        "School funding", "Inn subsidies", "Bank protection", "No curfew"
    ]
    
    actual_promises = CampaignPromise.PROMISES
    
    assert len(actual_promises) == 16, f"Expected 16 promises, got {len(actual_promises)}"
    
    # Verify all expected promises exist
    for expected in expected_promises:
        assert expected in actual_promises, f"Missing promise: {expected}"
    
    print(f"✓ Test 7: All 16 Promise Types - Verified complete list")

def test_main_py_integration():
    """Test 8: Main.py Integration Check"""
    # Read main.py to verify integration
    with open('c:\\Users\\Public\\rpg_game\\main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Check for P key handler
    assert "elif event.key == pygame.K_p" in main_content, "Missing P key handler"
    assert "showing_campaign_menu" in main_content, "Missing campaign menu flag"
    assert "campaign_menu_state" in main_content, "Missing campaign menu state"
    
    # Check for campaign state check
    assert 'election_timeline.state == "campaign"' in main_content, "Missing campaign state check"
    
    # Check for draw function
    assert "draw_campaign_menu" in main_content, "Missing draw_campaign_menu function"
    
    # Check for campaign promise import
    assert "from election_system import CampaignPromise" in main_content, "Missing CampaignPromise import"
    
    # Check for help screen entry
    assert '"P: Campaign promises' in main_content or 'P: Campaign' in main_content, "Missing help screen entry"
    
    print("✓ Test 8: Main.py Integration - P key ✓, menu state ✓, draw function ✓, import ✓, help screen ✓")

def test_campaign_messages():
    """Test 9: Campaign Period Messages"""
    game_time = MockGameTime()
    timeline = ElectionTimeline(game_time)
    
    timeline.start_anarchy()
    
    # Fast-forward to campaign
    game_time.day_count = 7
    timeline.update()
    
    assert timeline.state == "campaign", "Should be in campaign"
    assert timeline.days_in_campaign == 0, "Should be first day of campaign"
    
    # Verify campaign tracking
    game_time.day_count = 8
    timeline.update()
    assert timeline.days_in_campaign == 1, f"Should be day 1 of campaign, got {timeline.days_in_campaign}"
    
    game_time.day_count = 9
    timeline.update()
    assert timeline.days_in_campaign == 2, f"Should be day 2 of campaign, got {timeline.days_in_campaign}"
    
    print("✓ Test 9: Campaign Period Messages - Days tracked correctly")

def test_multiple_selections():
    """Test 10: Multiple Promise Selections"""
    system = CampaignPromiseSystem()
    
    # First selection
    first_selection = system.choose_promises(3)
    first_descriptions = [p.description for p in first_selection]
    
    # Second selection (simulates re-selecting promises)
    second_selection = system.choose_promises(3)
    second_descriptions = [p.description for p in second_selection]
    
    # Verify 3 selected each time
    assert len(first_selection) == 3, "First selection should have 3"
    assert len(second_selection) == 3, "Second selection should have 3"
    
    # Active promises should be overwritten
    assert len(system.active_promises) == 3, "Should have 3 active promises"
    
    print(f"✓ Test 10: Multiple Selections - Can reselect promises (Active: {len(system.active_promises)})")

if __name__ == "__main__":
    print("=" * 60)
    print("CAMPAIGN PROMISE SYSTEM TESTS")
    print("=" * 60)
    
    test_campaign_promise_system()
    test_choose_promises()
    test_fulfill_promise()
    test_election_timeline_states()
    test_campaign_period()
    test_full_election_cycle()
    test_promise_types()
    test_main_py_integration()
    test_campaign_messages()
    test_multiple_selections()
    
    print("=" * 60)
    print("✓ ALL CAMPAIGN PROMISE INTEGRATION TESTS PASSED!")
    print("=" * 60)

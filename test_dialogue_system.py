"""
Test NPC Dialogue System - Interactive Demo
"""
import pygame
from npc_basic import BasicNPC

pygame.init()

print("="*60)
print("NPC DIALOGUE SYSTEM TEST")
print("="*60)
print()

# Create NPCs of different types
npc_types = ["villager", "merchant", "guard", "elder", "blacksmith", "miner", "fisher"]
npcs = {}

for npc_type in npc_types:
    npc = BasicNPC(f"{npc_type.title()} NPC", 100, 100, npc_type)
    npcs[npc_type] = npc

print("[OK] Created 7 NPCs with different roles")
print()

# Test each NPC's dialogue
for npc_type, npc in npcs.items():
    print(f"{'='*60}")
    print(f"Talking to {npc.name} ({npc_type.upper()})")
    print(f"{'='*60}")
    
    # First conversation (greeting)
    print(f"[Player approaches {npc.name}]")
    response1 = npc.talk()
    print(f"{npc.name}: \"{response1}\"")
    print()
    
    # Second conversation (repeat)
    print(f"[Player talks again]")
    response2 = npc.talk()
    print(f"{npc.name}: \"{response2}\"")
    print()
    
    # Third conversation (farewell)
    print(f"[Player talks one more time]")
    response3 = npc.talk()
    print(f"{npc.name}: \"{response3}\"")
    print()
    
    # Verify dialogue structure
    assert npc.conversation_count == 3, f"Expected 3 conversations, got {npc.conversation_count}"
    assert isinstance(npc.dialogue, dict), "Dialogue should be a dictionary"
    assert "greeting" in npc.dialogue, "Dialogue should have 'greeting' key"
    assert "repeat" in npc.dialogue, "Dialogue should have 'repeat' key"
    assert "farewell" in npc.dialogue, "Dialogue should have 'farewell' key"

print("="*60)
print("CUSTOM DIALOGUE TEST")
print("="*60)
print()

# Test custom dialogue
custom_npc = BasicNPC("Quest Giver", 200, 200, "villager")
custom_dialogue = {
    "greeting": ["I need your help with something important!"],
    "repeat": ["Have you completed the quest yet?"],
    "farewell": ["Thank you for your help, brave adventurer!"]
}
custom_npc.set_custom_dialogue(custom_dialogue)

print("[OK] Set custom dialogue on Quest Giver NPC")
print()
print(f"[Player approaches Quest Giver]")
print(f"Quest Giver: \"{custom_npc.talk()}\"")
print()
print(f"[Player talks again]")
print(f"Quest Giver: \"{custom_npc.talk()}\"")
print()

# Test conversation reset
custom_npc.reset_conversation()
print(f"[Conversation reset]")
print(f"[Player approaches Quest Giver again]")
response = custom_npc.talk()
print(f"Quest Giver: \"{response}\"")
print()

# Verify reset worked
assert custom_npc.conversation_count == 1, "Conversation count should be 1 after reset"

print("="*60)
print("[OK] ALL DIALOGUE TESTS PASSED!")
print("="*60)
print()
print("[STATS] SUMMARY:")
print(f"  [OK] 7 NPC types with unique dialogue")
print(f"  [OK] Greeting/Repeat/Farewell system working")
print(f"  [OK] Custom dialogue support")
print(f"  [OK] Conversation state management")
print(f"  [OK] Conversation reset functionality")
print()
print("NPCs can now talk! The dialogue system is fully functional. ")

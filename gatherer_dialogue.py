"""
Gatherer NPC Dialogue Trees
Handles conversations with gatherer NPCs at resource nodes
"""

from dialogue_system import DialogueTree, DialogueNode, DialogueChoice, DialogueNodeType


def create_gatherer_dialogue(npc):
    """Create dialogue tree for a gatherer NPC based on their state"""
    
    # Different dialogues for different situations
    if npc.is_recovering:
        return create_recovery_dialogue(npc)
    elif npc.state == "gathering" and npc.target_node:
        return create_node_conflict_dialogue(npc)
    else:
        return create_idle_dialogue(npc)


def create_recovery_dialogue(npc):
    """Dialogue when NPC is recovering from death"""
    tree = DialogueTree(f"{npc.name}_recovery", "recovery_greeting")
    
    # Single node - NPC trash talks after being defeated
    tree.nodes["recovery_greeting"] = DialogueNode(
        node_id="recovery_greeting",
        node_type=DialogueNodeType.TEXT,
        content=f"Great fight! I'll get you next time though, those resources ARE MINE!!!!"
    )
    
    # Choices - player can only leave
    tree.nodes["recovery_choices"] = DialogueNode(
        node_id="recovery_choices",
        node_type=DialogueNodeType.CHOICE,
        content="",
        choices=[
            DialogueChoice("[Leave them alone]", None)
        ]
    )
    
    tree.start_node_id = "recovery_greeting"
    tree.nodes["recovery_greeting"].choices = [
        DialogueChoice("...", "recovery_choices")
    ]
    
    return tree


def create_node_conflict_dialogue(npc):
    """Dialogue when player approaches NPC at their gathering node"""
    tree = DialogueTree(f"{npc.name}_node", "node_greeting")
    
    # Determine NPC personality (aggressive or passive)
    is_aggressive = npc.base_damage > 10  # Higher damage = more aggressive
    
    if is_aggressive:
        # Aggressive NPC threatens player
        tree.nodes["node_greeting"] = DialogueNode(
            node_id="node_greeting",
            node_type=DialogueNodeType.TEXT,
            content=f"This is MY node! Leave me be before someone gets hurt."
        )
        
        tree.nodes["node_choices"] = DialogueNode(
            node_id="node_choices",
            node_type=DialogueNodeType.CHOICE,
            content="",
            choices=[
                DialogueChoice(
                    "[Fine, I'll leave]",
                    "leave_response",
                    consequences={'action': 'player_leaves'}
                ),
                DialogueChoice(
                    "[Bribe 300 dubloons to leave]",
                    "bribe_response",
                    requirements={'gold': 300},
                    consequences={'gold': -300, 'action': 'npc_leaves_24h'}
                ),
                DialogueChoice(
                    "[Give me your resources]",
                    "demand_resources"
                ),
                DialogueChoice(
                    "[Attack]",
                    "attack_response",
                    consequences={'action': 'enter_combat'}
                )
            ]
        )
        
    else:
        # Passive NPC pleads with player
        tree.nodes["node_greeting"] = DialogueNode(
            node_id="node_greeting",
            node_type=DialogueNodeType.TEXT,
            content=f"Please don't hurt me! You can have this node if you leave me alone..."
        )
        
        tree.nodes["node_choices"] = DialogueNode(
            node_id="node_choices",
            node_type=DialogueNodeType.CHOICE,
            content="",
            choices=[
                DialogueChoice(
                    "[Fine, I'll leave]",
                    "leave_response",
                    consequences={'action': 'player_leaves'}
                ),
                DialogueChoice(
                    "[Bribe 300 dubloons to leave]",
                    "bribe_response",
                    requirements={'gold': 300},
                    consequences={'gold': -300, 'action': 'npc_leaves_24h'}
                ),
                DialogueChoice(
                    "[Give me your resources]",
                    "demand_resources"
                ),
                DialogueChoice(
                    "[Attack anyway]",
                    "attack_response",
                    consequences={'action': 'enter_combat'}
                )
            ]
        )
    
    # Response nodes
    tree.nodes["leave_response"] = DialogueNode(
        node_id="leave_response",
        node_type=DialogueNodeType.TEXT,
        content="Smart choice. Now get out of here before I change my mind!" if is_aggressive else "Thank you! I really need these resources..."
    )
    
    tree.nodes["bribe_response"] = DialogueNode(
        node_id="bribe_response",
        node_type=DialogueNodeType.TEXT,
        content="Fine, I'll find another spot for now. But I'll be back!" if is_aggressive else "Oh, thank you! That's very generous. The node is yours for the next day."
    )
    
    tree.nodes["demand_resources"] = DialogueNode(
        node_id="demand_resources",
        node_type=DialogueNodeType.TEXT,
        content="Never! I'll never give them up!" if is_aggressive else "No! I worked hard for these! Leave me alone!"
    )
    
    tree.nodes["demand_choices"] = DialogueNode(
        node_id="demand_choices",
        node_type=DialogueNodeType.CHOICE,
        content="",
        choices=[
            DialogueChoice(
                "[Back off]",
                "leave_response"
            ),
            DialogueChoice(
                "[Attack]",
                "attack_response",
                consequences={'action': 'random_combat'}  # 50% chance NPC attacks first
            )
        ]
    )
    
    tree.nodes["attack_response"] = DialogueNode(
        node_id="attack_response",
        node_type=DialogueNodeType.TEXT,
        content="You'll regret this!" if is_aggressive else "No! Please!"
    )
    
    # Link nodes
    tree.start_node_id = "node_greeting"
    tree.nodes["node_greeting"].choices = [
        DialogueChoice("...", "node_choices")
    ]
    tree.nodes["demand_resources"].choices = [
        DialogueChoice("...", "demand_choices")
    ]
    
    return tree


def create_idle_dialogue(npc):
    """Dialogue when NPC is idle (not gathering)"""
    tree = DialogueTree(f"{npc.name}_idle", "idle_greeting")
    
    greetings = [
        f"Hello there! I'm looking for some good {npc.gatherer_type} spots.",
        f"These resources won't gather themselves! Got to keep moving.",
        f"Beautiful day for {npc.gatherer_type}, isn't it?",
        f"The bank's getting full, but I need more!",
    ]
    
    import random
    greeting = random.choice(greetings)
    
    tree.nodes["idle_greeting"] = DialogueNode(
        node_id="idle_greeting",
        node_type=DialogueNodeType.TEXT,
        content=greeting
    )
    
    tree.nodes["idle_choices"] = DialogueNode(
        node_id="idle_choices",
        node_type=DialogueNodeType.CHOICE,
        content="",
        choices=[
            DialogueChoice(
                "[Tell me about your work]",
                "work_info"
            ),
            DialogueChoice(
                "[Goodbye]",
                None
            )
        ]
    )
    
    tree.nodes["work_info"] = DialogueNode(
        node_id="work_info",
        node_type=DialogueNodeType.TEXT,
        content=f"I'm a professional {npc.gatherer_type}. I gather resources and sell them at the bank. It's honest work, and sometimes dangerous when others try to take my spots!"
    )
    
    # Link nodes
    tree.start_node_id = "idle_greeting"
    tree.nodes["idle_greeting"].choices = [
        DialogueChoice("...", "idle_choices")
    ]
    tree.nodes["work_info"].choices = [
        DialogueChoice("[Goodbye]", None)
    ]
    
    return tree


def handle_dialogue_consequence(consequence, npc, player, game_time):
    """Handle the consequence of a dialogue choice"""
    
    action = consequence.get('action')
    
    if action == 'player_leaves':
        # Player must leave within 20 seconds (get 10 tiles away)
        npc.warned_player = True
        npc.aggro_timer = 20.0  # 20 seconds
        return {
            'message': "You have 20 seconds to get 10 tiles away or I attack!",
            'warning': True
        }
    
    elif action == 'npc_leaves_24h':
        # NPC is bribed, leaves node for 24 game hours
        current_hours = game_time.get_total_hours()
        npc.bribed_until = current_hours + 24
        
        # Stop gathering
        if npc.target_node:
            from gathering_nodes import NodeState
            npc.target_node.state = NodeState.AVAILABLE
            npc.target_node.gatherer = None
        npc.target_node = None
        npc.state = "idle"
        
        # Deduct player gold
        player.dubloons -= 300
        
        return {
            'message': f"Paid 300 dubloons. {npc.name} will avoid this node for 24 hours.",
            'success': True
        }
    
    elif action == 'enter_combat':
        # Enter combat immediately
        npc.combat_target = player
        return {
            'message': "Combat started!",
            'combat': True
        }
    
    elif action == 'random_combat':
        # 50% chance NPC attacks
        import random
        if random.random() < 0.5:
            npc.combat_target = player
            return {
                'message': f"{npc.name} attacks you!",
                'combat': True
            }
        else:
            return {
                'message': f"{npc.name} backs down.",
                'success': True
            }
    
    return {}

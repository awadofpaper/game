
import pygame
from config import Config
from item import Item

class Player:
    def handle_event(self, event):
        # Basic WASD movement and action key handling
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls['up']:
                self.move_dir['up'] = True
            elif event.key == self.controls['down']:
                self.move_dir['down'] = True
            elif event.key == self.controls['left']:
                self.move_dir['left'] = True
            elif event.key == self.controls['right']:
                self.move_dir['right'] = True
            # Add more key handling as needed
        elif event.type == pygame.KEYUP:
            if event.key == self.controls['up']:
                self.move_dir['up'] = False
            elif event.key == self.controls['down']:
                self.move_dir['down'] = False
            elif event.key == self.controls['left']:
                self.move_dir['left'] = False
            elif event.key == self.controls['right']:
                self.move_dir['right'] = False

    def __init__(self, config, world, name=None, color=None, skills=None):
        self.x = config.WORLD_WIDTH // 2
        self.y = config.WORLD_HEIGHT // 2
        
        # RPG Stats
        self.level = 1
        self.xp = 0
        self.gold = 0
        
        # Health/Resources
        self.max_health = 100
        self.max_stamina = 100
        self.max_mana = 100
        self.health = 100
        self.stamina = 100
        self.mana = 100
        
        # Base attributes (from character creation or default)
        self.strength = 0
        self.agility = 0
        self.intelligence = 0
        self.charisma = 0
        self.endurance = 0
        
        # Character customization
        self.name = name if name is not None else "Player"
        self.color = color if color is not None else (255, 255, 255)
        self.skills = skills if skills is not None else {}
        # Inventory: stackables (str->int) and equipment (list of Item)
        self.inventory = {
            'stick': 0, 'fiber': 0,
            'apple': 0, 'bread': 0, 'meat': 0, 'cooked_fish': 0, 'berries': 0, 'mushroom': 0,
            'elixir': 0, 'antidote': 0, 'energy_drink': 0,
            'health_potion': 0, 'mana_potion': 0, 'stamina_potion': 0, 'strength_potion': 0, 'defense_potion': 0, 'invisibility_potion': 0, 'fire_resist_potion': 0,
            'ancient_relic': 0, 'magic_key': 0, 'lost_letter': 0, 'sacred_stone': 0,
            'torch': 0, 'rope': 0, 'map_fragment': 0, 'lockpick': 0, 'bomb': 0,
            'herbs': 0, 'ore': 0, 'cloth': 0, 'bones': 0,
            'items': []  # equipment and special items
        }
        # Equipment slots: weapon, armor, etc.
        self.equipment = {'weapon': None, 'armor': None, 'accessory': None}
        self.world = world
        self.config = config
        self.controls = {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'action': pygame.K_SPACE
        }
        # Movement state
        self.move_dir = {'up': False, 'down': False, 'left': False, 'right': False}
        self.speed = config.PLAYER_SPEED
        # Consumable cooldown (frames)
        self.consumable_cooldown = 0
        # Spell system attributes (initialized later in main)
        self.known_spells = set()
        self.selected_spell = None
        self.secondary_spell = None
        self.advanced_spells = None

    def can_use_consumable(self):
        return self.consumable_cooldown <= 0

    def update(self, keys=None, dt=1.0, in_town=False):
        # Add movement, stamina, and interaction logic here
        if self.consumable_cooldown > 0:
            self.consumable_cooldown -= 1
        # ...existing code...

    def use_item(self, item_name_or_obj):
        """Use a consumable item (food, potion, quest). Returns feedback string."""
        if not self.can_use_consumable():
            return "You must wait before using another item!"
        # Stackable food/potion/quest (by name)
        if isinstance(item_name_or_obj, str):
            name = item_name_or_obj
            # Example food
            if name == 'apple':
                if self.inventory.get('apple', 0) > 0:
                    self.health = min(self.max_health, self.health + 10)
                    self.inventory['apple'] -= 1
                    self.consumable_cooldown = 60
                    return "You eat an apple. (+10 HP)"
                else:
                    return "No apples left!"
            elif name == 'bread':
                if self.inventory.get('bread', 0) > 0:
                    self.stamina = min(self.max_stamina, self.stamina + 15)
                    self.inventory['bread'] -= 1
                    self.consumable_cooldown = 60
                    return "You eat bread. (+15 Stamina)"
                else:
                    return "No bread left!"
            elif name == 'health_potion':
                if self.inventory.get('health_potion', 0) > 0:
                    self.health = min(self.max_health, self.health + 50)
                    self.inventory['health_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink a health potion. (+50 HP)"
                else:
                    return "No health potions left!"
            elif name == 'mana_potion':
                if self.inventory.get('mana_potion', 0) > 0:
                    self.mana = min(self.max_mana, self.mana + 40)
                    self.inventory['mana_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink a mana potion. (+40 Mana)"
                else:
                    return "No mana potions left!"
            elif name == 'quest_gem':
                if self.inventory.get('quest_gem', 0) > 0:
                    self.inventory['quest_gem'] -= 1
                    self.consumable_cooldown = 30
                    # Here you would trigger a quest event
                    return "You use the quest gem. Something happens!"
                else:
                    return "No quest gems left!"
            else:
                return f"You can't use {name}!"

        # Item object (future: potions, scrolls, etc.)
        elif hasattr(item_name_or_obj, 'type'):
            item = item_name_or_obj
            if item.type == 'potion':
                if item.name == 'Health Potion':
                    self.health = min(self.max_health, self.health + 50)
                    self.consumable_cooldown = 120
                    self.remove_item(item)
                    return "You drink a health potion. (+50 HP)"
                elif item.name == 'Mana Potion':
                    self.mana = min(self.max_mana, self.mana + 40)
                    self.consumable_cooldown = 120
                    self.remove_item(item)
                    return "You drink a mana potion. (+40 Mana)"
                else:
                    return f"You can't use {item.name}!"
            elif item.type == 'food':
                self.health = min(self.max_health, self.health + 10)
                self.consumable_cooldown = 60
                self.remove_item(item)
                return f"You eat {item.name}. (+10 HP)"
            elif item.type == 'quest':
                self.consumable_cooldown = 30
                self.remove_item(item)
                # Trigger quest event here
                return f"You use {item.name}. Something happens!"
            else:
                return f"You can't use {item.name}!"
        else:
            return "You can't use that!"
    def __init__(self, config, world, name=None, color=None, skills=None):
        self.x = config.WORLD_WIDTH // 2
        self.y = config.WORLD_HEIGHT // 2
        self.health = 100
        self.stamina = 100
        self.mana = 100
        # Character customization
        self.name = name if name is not None else "Player"
        self.color = color if color is not None else (255, 255, 255)
        self.skills = skills if skills is not None else {}
        # Inventory: stackables (str->int) and equipment (list of Item)
        self.inventory = {
            'stick': 0, 'fiber': 0,
            'apple': 0, 'bread': 0, 'meat': 0, 'cooked_fish': 0, 'berries': 0, 'mushroom': 0,
            'elixir': 0, 'antidote': 0, 'energy_drink': 0,
            'health_potion': 0, 'mana_potion': 0, 'stamina_potion': 0, 'strength_potion': 0, 'defense_potion': 0, 'invisibility_potion': 0, 'fire_resist_potion': 0,
            'ancient_relic': 0, 'magic_key': 0, 'lost_letter': 0, 'sacred_stone': 0,
            'torch': 0, 'rope': 0, 'map_fragment': 0, 'lockpick': 0, 'bomb': 0,
            'herbs': 0, 'ore': 0, 'cloth': 0, 'bones': 0,
            'items': []  # equipment and special items
        }
        # Equipment slots: weapon, armor, etc.
        self.equipment = {'weapon': None, 'armor': None, 'accessory': None}
        self.world = world
        self.config = config
        self.controls = {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'action': pygame.K_SPACE
        }
        # Movement state
        self.move_dir = {'up': False, 'down': False, 'left': False, 'right': False}
        self.speed = 4

    def add_item(self, item):
        """Add an Item object to inventory (for equipment/gear)."""
        self.inventory['items'].append(item)

    def use_item(self, item_name_or_obj):
        """Use a consumable item (food, potion, quest). Returns feedback string."""
        if not self.can_use_consumable():
            return "You must wait before using another item!"
        # Stackable food/potion/quest (by name)
        if isinstance(item_name_or_obj, str):
            name = item_name_or_obj
            inv = self.inventory
            # Food
            if name == 'apple':
                                # Break tile at player position
                                tx = self.x // self.config.TILE_SIZE * self.config.TILE_SIZE
                                ty = self.y // self.config.TILE_SIZE * self.config.TILE_SIZE
                                tile = self.world.get_tile(tx, ty)
                                # Only break if not empty or water
                                if tile['ground'] not in ('empty', 'water'):
                                    # Drop table for world objects
                                    drop_table = {
                                        'tree': [
                                            ('stick', 0.08), ('apple', 0.01)
                                        ],
                                        'rock_group': [
                                            ('ore', 0.06), ('rubble', 0.08)
                                        ],
                                        'grass': [
                                            ('fiber', 0.08), ('herbs', 0.02)
                                        ],
                                        'bush': [
                                            ('berries', 0.06)
                                        ],
                                        'mushroom_patch': [
                                            ('mushroom', 0.04)
                                        ]
                                    }
                                    ground = tile['ground']
                                    drops = drop_table.get(ground, [])
                                    for item, chance in drops:
                                        if random.random() < chance:
                                            self.inventory[item] = self.inventory.get(item, 0) + 1
                                    tile['ground'] = 'empty'
                                    self.world.set_tile(tx, ty, tile)
            elif name == 'meat':
                if inv['meat'] > 0:
                    self.health = min(100, self.health + 20)
                    inv['meat'] -= 1
                    self.consumable_cooldown = 80
                    return "You eat meat. (+20 HP)"
                else:
                    return "No meat left!"
            elif name == 'cooked_fish':
                if inv['cooked_fish'] > 0:
                    self.health = min(100, self.health + 12)
                    self.stamina = min(100, self.stamina + 12)
                    inv['cooked_fish'] -= 1
                    self.consumable_cooldown = 70
                    return "You eat cooked fish. (+12 HP, +12 Stamina)"
                else:
                    return "No cooked fish left!"
            elif name == 'berries':
                if inv['berries'] > 0:
                    self.health = min(100, self.health + 5)
                    inv['berries'] -= 1
                    self.consumable_cooldown = 40
                    return "You eat berries. (+5 HP)"
                else:
                    return "No berries left!"
            elif name == 'mushroom':
                if inv['mushroom'] > 0:
                    import random
                    effect = random.choice(['heal', 'poison', 'buff'])
                    inv['mushroom'] -= 1
                    self.consumable_cooldown = 80
                    if effect == 'heal':
                        self.health = min(100, self.health + 15)
                        return "You eat a mushroom. (+15 HP)"
                    elif effect == 'poison':
                        self.health = max(0, self.health - 10)
                        return "You eat a mushroom. (Poisoned! -10 HP)"
                    else:
                        self.stamina = min(100, self.stamina + 10)
                        return "You eat a mushroom. (Buff! +10 Stamina)"
                else:
                    return "No mushrooms left!"
            # Potions
            elif name == 'elixir':
                if inv['elixir'] > 0:
                    self.health = min(100, self.health + 20)
                    self.mana = min(100, self.mana + 20)
                    inv['elixir'] -= 1
                    self.consumable_cooldown = 100
                    return "You drink an elixir. (+20 HP, +20 Mana)"
                else:
                    return "No elixirs left!"
            elif name == 'antidote':
                if inv['antidote'] > 0:
                    # Remove poison status (not implemented)
                    inv['antidote'] -= 1
                    self.consumable_cooldown = 60
                    return "You drink an antidote. (Cured poison)"
                else:
                    return "No antidotes left!"
            elif name == 'energy_drink':
                if inv['energy_drink'] > 0:
                    self.stamina = min(100, self.stamina + 30)
                    self.consumable_cooldown = 80
                    inv['energy_drink'] -= 1
                    return "You drink an energy drink. (+30 Stamina)"
                else:
                    return "No energy drinks left!"
            elif name == 'health_potion':
                if inv['health_potion'] > 0:
                    self.health = min(100, self.health + 50)
                    inv['health_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink a health potion. (+50 HP)"
                else:
                    return "No health potions left!"
            elif name == 'mana_potion':
                if inv['mana_potion'] > 0:
                    self.mana = min(100, self.mana + 40)
                    inv['mana_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink a mana potion. (+40 Mana)"
                else:
                    return "No mana potions left!"
            elif name == 'stamina_potion':
                if inv['stamina_potion'] > 0:
                    self.stamina = min(100, self.stamina + 40)
                    inv['stamina_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink a stamina potion. (+40 Stamina)"
                else:
                    return "No stamina potions left!"
            elif name == 'strength_potion':
                if inv['strength_potion'] > 0:
                    # Not implemented: buff
                    inv['strength_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink a strength potion. (Buffed!)"
                else:
                    return "No strength potions left!"
            elif name == 'defense_potion':
                if inv['defense_potion'] > 0:
                    # Not implemented: buff
                    inv['defense_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink a defense potion. (Buffed!)"
                else:
                    return "No defense potions left!"
            elif name == 'invisibility_potion':
                if inv['invisibility_potion'] > 0:
                    # Not implemented: stealth
                    inv['invisibility_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink an invisibility potion. (Invisible!)"
                else:
                    return "No invisibility potions left!"
            elif name == 'fire_resist_potion':
                if inv['fire_resist_potion'] > 0:
                    # Not implemented: fire resist
                    inv['fire_resist_potion'] -= 1
                    self.consumable_cooldown = 120
                    return "You drink a fire resist potion. (Fire resistance!)"
                else:
                    return "No fire resist potions left!"
            # Quest items
            elif name == 'ancient_relic':
                if inv['ancient_relic'] > 0:
                    inv['ancient_relic'] -= 1
                    self.consumable_cooldown = 30
                    return "You use the ancient relic. A mysterious force stirs!"
                else:
                    return "No ancient relics left!"
            elif name == 'magic_key':
                if inv['magic_key'] > 0:
                    inv['magic_key'] -= 1
                    self.consumable_cooldown = 30
                    return "You use the magic key. You hear a click!"
                else:
                    return "No magic keys left!"
            elif name == 'lost_letter':
                if inv['lost_letter'] > 0:
                    inv['lost_letter'] -= 1
                    self.consumable_cooldown = 30
                    return "You deliver the lost letter. Quest updated!"
                else:
                    return "No lost letters left!"
            elif name == 'sacred_stone':
                if inv['sacred_stone'] > 0:
                    inv['sacred_stone'] -= 1
                    self.consumable_cooldown = 30
                    return "You use the sacred stone. The air shimmers!"
                else:
                    return "No sacred stones left!"
            # Utility/Other
            elif name == 'torch':
                if inv['torch'] > 0:
                    inv['torch'] -= 1
                    self.consumable_cooldown = 10
                    return "You light a torch. (Not implemented)"
                else:
                    return "No torches left!"
            elif name == 'rope':
                if inv['rope'] > 0:
                    inv['rope'] -= 1
                    self.consumable_cooldown = 10
                    return "You use a rope. (Not implemented)"
                else:
                    return "No ropes left!"
            elif name == 'map_fragment':
                if inv['map_fragment'] > 0:
                    inv['map_fragment'] -= 1
                    self.consumable_cooldown = 10
                    return "You study a map fragment. (Not implemented)"
                else:
                    return "No map fragments left!"
            elif name == 'lockpick':
                if inv['lockpick'] > 0:
                    inv['lockpick'] -= 1
                    self.consumable_cooldown = 10
                    return "You use a lockpick. (Not implemented)"
                else:
                    return "No lockpicks left!"
            elif name == 'bomb':
                if inv['bomb'] > 0:
                    inv['bomb'] -= 1
                    self.consumable_cooldown = 30
                    return "You use a bomb. (Not implemented)"
                else:
                    return "No bombs left!"
            elif name == 'herbs':
                if inv['herbs'] > 0:
                    inv['herbs'] -= 1
                    self.consumable_cooldown = 10
                    return "You use herbs. (Not implemented)"
                else:
                    return "No herbs left!"
            elif name == 'ore':
                if inv['ore'] > 0:
                    inv['ore'] -= 1
                    self.consumable_cooldown = 10
                    return "You use ore. (Not implemented)"
                else:
                    return "No ore left!"
            elif name == 'cloth':
                if inv['cloth'] > 0:
                    inv['cloth'] -= 1
                    self.consumable_cooldown = 10
                    return "You use cloth. (Not implemented)"
                else:
                    return "No cloth left!"
            elif name == 'bones':
                if inv['bones'] > 0:
                    inv['bones'] -= 1
                    self.consumable_cooldown = 10
                    return "You use bones. (Not implemented)"
                else:
                    return "No bones left!"
            else:
                return f"You can't use {name}!"
        elif event.type == pygame.KEYUP:
            if event.key == self.controls['up']:
                self.move_dir['up'] = False
            elif event.key == self.controls['down']:
                self.move_dir['down'] = False
            elif event.key == self.controls['left']:
                self.move_dir['left'] = False
            elif event.key == self.controls['right']:
                self.move_dir['right'] = False

    def update(self):
        # Add movement, stamina, and interaction logic here
            # Movement logic with collision
            dx = dy = 0
            if self.move_dir['up']:
                dy -= self.speed
            if self.move_dir['down']:
                dy += self.speed
            if self.move_dir['left']:
                dx -= self.speed
            if self.move_dir['right']:
                dx += self.speed
            # Diagonal normalization
            if dx != 0 and dy != 0:
                dx = int(dx * 0.7071)
                dy = int(dy * 0.7071)

            # Predict new position
            new_x = max(0, min(self.x + dx, self.config.WORLD_WIDTH - self.config.TILE_SIZE))
            new_y = max(0, min(self.y + dy, self.config.WORLD_HEIGHT - self.config.TILE_SIZE))

            # Check collision for each axis separately for smooth sliding
            # X axis
            tx = new_x // self.config.TILE_SIZE * self.config.TILE_SIZE
            ty = self.y // self.config.TILE_SIZE * self.config.TILE_SIZE
            tile_x = self.world.get_tile(tx, ty)
            impassable = ["rock_group", "tree", "water"]
            if tile_x['ground'] in impassable or tile_x['object'] in impassable:
                new_x = self.x

            # Y axis
            tx = self.x // self.config.TILE_SIZE * self.config.TILE_SIZE
            ty = new_y // self.config.TILE_SIZE * self.config.TILE_SIZE
            tile_y = self.world.get_tile(tx, ty)
            if tile_y['ground'] in impassable or tile_y['object'] in impassable:
                new_y = self.y

            self.x = new_x
            self.y = new_y

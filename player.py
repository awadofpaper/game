import pygame
from config import Config
from item import Item

# Import StatusManager if available
try:
    from status_effects import StatusManager
except ImportError:
    StatusManager = None

# Import SkillsManager if available
try:
    from skills_system import SkillsManager
except ImportError:
    SkillsManager = None

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
        # Position
        self.x = config.WORLD_WIDTH // 2
        self.y = config.WORLD_HEIGHT // 2
        
        # RPG Stats (initialized here, can be overridden by main.py or save files)
        self.level = 1
        self.xp = 0
        self.dubloons = 0  # Primary currency (pirate-themed)
        self.stat_points = 0  # Points for allocating to base stats (Strength, Defense, etc.)
        self.perk_points = 0  # Points for skill tree perks
        
        # Health/Resources
        self.max_health = 100
        self.max_stamina = 100
        self.max_mana = 100
        self.health = 100
        self.stamina = 100
        self.mana = 100
        
        # Base attributes (stats menu allocatable)
        self.strength = 0
        self.defense = 0
        self.magic = 0
        self.stamina_stat = 0  # Note: different from stamina resource
        self.speed = 0
        self.agility = 0
        self.willpower = 0
        self.luck = 0
        self.intelligence = 0
        self.talking = 0
        # Legacy attributes
        self.charisma = 0
        self.endurance = 0
        
        # Character customization
        self.name = name if name is not None else "Player"
        self.color = color if color is not None else (255, 255, 255)
        self.skills = skills if skills is not None else {}
        
        # Race and appearance
        self.race_id = 'human'  # Default race
        self.race = None  # Will be set by main.py after initialization
        self.skin_tone = (255, 220, 177)  # Default skin tone
        self.racial_traits = []  # List of active racial traits
        self.trait_manager = None  # Will be initialized after race is set
        
        # Skill tree tracking
        self.acquired_skills = set()  # Set of acquired skill IDs
        self.skill_points_invested = {}  # Dict mapping skill_id -> points invested
        
        # Inventory: stackables (str->int) and equipment (list of Item)
        self.inventory = {
            'stick': 0, 'fiber': 0,
            'apple': 0, 'bread': 0, 'meat': 0, 'cooked_fish': 0, 'berries': 0, 'mushroom': 0,
            'elixir': 0, 'antidote': 0, 'energy_drink': 0,
            'health_potion': 0, 'mana_potion': 0, 'stamina_potion': 0, 'strength_potion': 0, 
            'defense_potion': 0, 'invisibility_potion': 0, 'fire_resist_potion': 0,
            'ancient_relic': 0, 'magic_key': 0, 'lost_letter': 0, 'sacred_stone': 0,
            'torch': 0, 'rope': 0, 'map_fragment': 0, 'lockpick': 0, 'bomb': 0,
            'herbs': 0, 'ore': 0, 'cloth': 0, 'bones': 0,
            'items': []  # equipment and special items
        }
        
        # Tutorial tracking
        self.tutorial_completed = False
        self.tutorial_active = False
        self.tutorial_stage = 'not_started'  # not_started, collecting_sticks, sticks_collected, equipped_stacked, combat, completed
        self.tutorial_sticks_equipped = False
        self.tutorial_sticks_stacked = False
        self.tutorial_enemies_killed = 0
        
        # Equipment slots - expanded to match EQUIPMENT_DATA
        self.equipment = {
            'weapon': None,         # Legacy slot (maps to main_hand)
            'armor': None,          # Legacy slot (maps to chest)
            'accessory': None,      # Legacy slot (maps to necklace/ring)
            'main_hand': None,      # Primary weapon
            'off_hand': None,       # Shield or secondary weapon
            'head': None,           # Helmet
            'chest': None,          # Chest armor
            'legs': None,           # Leg armor
            'feet': None,           # Boots
            'hands': None,          # Gloves
            'neck': None,           # Necklace
            'ring1': None,          # Ring slot 1
            'ring2': None           # Ring slot 2
        }
        
        # References
        self.world = world
        
        # Direction tracking (for visual indicator)
        self.facing_direction = 'down'  # 'up', 'down', 'left', 'right'
        self.config = config
        
        # Controls
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
        
        # Pygame rect for collision detection (50% smaller, rectangular)
        tile_size = config.TILE_SIZE
        player_width = (tile_size - 4) // 2
        player_height = int((tile_size - 4) * 0.75)
        self.rect = pygame.Rect(self.x - player_width//2, self.y - player_height//2, player_width, player_height)
        
        # Consumable cooldown (frames)
        self.consumable_cooldown = 0
        
        # Gathering state
        self.gathering_node = None
        self.gathering_progress = 0
        self.gathering_tool = None
        
        # Resource tracking for decreasing drop rates
        self.trees_broken_count = 0
        self.bushes_broken_count = 0
        self.rocks_broken_count = 0
        self.mushrooms_broken_count = 0  # Currently equipped gathering tool
        
        # Status effects manager
        if StatusManager:
            self.status_manager = StatusManager(entity=self)
        else:
            self.status_manager = None
        
        # Skills manager
        if SkillsManager:
            self.skills_manager = SkillsManager()
        else:
            self.skills_manager = None
        
        # Spell system attributes (initialized by main.py)
        self.known_spells = set()
        self.selected_spell = None
        self.secondary_spell = None
        self.advanced_spells = None

    def can_use_consumable(self):
        return self.consumable_cooldown <= 0

    @property
    def gold(self):
        """Alias for dubloons - for backward compatibility"""
        return self.dubloons
    
    @gold.setter
    def gold(self, value):
        """Set dubloons when gold is set - for backward compatibility"""
        self.dubloons = value
    
    @property
    def money(self):
        """Alias for dubloons - used by loot box system"""
        return self.dubloons
    
    @money.setter
    def money(self, value):
        """Set dubloons when money is set"""
        self.dubloons = value

    def update(self, keys=None, dt=1.0, in_town=False, **kwargs):
        """Update player state"""
        # Update status effects (buffs, debuffs, DoT, HoT)
        if hasattr(self, 'status_manager') and self.status_manager:
            self.status_manager.update_effects(self)
        
        # Update racial trait effects (Elf mana regen, Orc rage, etc.)
        if hasattr(self, 'trait_manager') and self.trait_manager:
            self.trait_manager.update(dt)
        
        if self.consumable_cooldown > 0:
            self.consumable_cooldown -= 1
        
        # Handle sprint toggle (press Shift once to toggle on/off)
        is_moving = (keys.get(self.controls['up'], False) or 
                     keys.get(self.controls['down'], False) or 
                     keys.get(self.controls['left'], False) or 
                     keys.get(self.controls['right'], False))
        
        if keys:
            # Check both left and right shift keys separately
            lshift_pressed = keys.get(pygame.K_LSHIFT, False)
            rshift_pressed = keys.get(pygame.K_RSHIFT, False)
            
            # Initialize sprint attributes if they don't exist
            if not hasattr(self, 'last_lshift_state'):
                self.last_lshift_state = False
            if not hasattr(self, 'last_rshift_state'):
                self.last_rshift_state = False
            if not hasattr(self, 'is_sprinting'):
                self.is_sprinting = False
            
            # Detect shift key press (not hold) - toggle sprint if EITHER key is newly pressed
            if (lshift_pressed and not self.last_lshift_state) or (rshift_pressed and not self.last_rshift_state):
                # Either shift just pressed - toggle sprint
                self.is_sprinting = not self.is_sprinting
            
            # Update last shift states for next frame
            self.last_lshift_state = lshift_pressed
            self.last_rshift_state = rshift_pressed
        
        # Drain stamina while sprinting and moving
        if self.is_sprinting and is_moving:
            if self.stamina > 0:
                stamina_drain = 0.2  # Base stamina drain
                
                # Apply racial modifiers (Halfling: -10% stamina cost)
                if hasattr(self, 'trait_manager') and self.trait_manager:
                    stamina_drain *= self.trait_manager.get_sprint_stamina_modifier()
                
                self.stamina -= stamina_drain
            else:
                # Stamina depleted - auto-stop sprinting
                self.is_sprinting = False
        
        # Handle sneaking (Both Ctrl keys) - drains stamina slower
        is_sneaking = False
        if keys and (keys.get(pygame.K_LCTRL, False) or keys.get(pygame.K_RCTRL, False)) and is_moving:
            if self.stamina >= 0.1:
                is_sneaking = True
                self.stamina -= 0.1  # Drain stamina while sneaking (slower than sprint)
        
        # Regenerate stamina when not sprinting or sneaking (reduced by 65% total)
        if not self.is_sprinting and not is_sneaking and self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + 0.035)
        
        # Regenerate mana passively (same rate as stamina)
        if self.mana < self.max_mana:
            self.mana = min(self.max_mana, self.mana + 0.035)
        
        # Handle movement
        dx = 0
        dy = 0
        
        # Get status effect multipliers
        status_speed_mult = 1.0
        if hasattr(self, 'status_manager') and self.status_manager:
            multipliers = self.status_manager.get_stat_multipliers()
            status_speed_mult = multipliers["speed"]
            
            # Check if frozen or prevented from action
            if self.status_manager.is_prevented_from_action():
                # Can't move when frozen
                status_speed_mult = 0.0
        
        # Prefer keys parameter if provided (always accurate), otherwise use move_dir
        if keys is not None:
            # Use keyboard state directly
            # PLAYER_SPEED is already in pixels/frame, don't multiply by dt
            # Apply speed multiplier based on movement mode and status effects
            if self.is_sprinting:
                move_speed = self.speed * 1.5 * status_speed_mult  # Sprint + status effects
            elif is_sneaking:
                move_speed = self.speed * 0.5 * status_speed_mult  # Sneak + status effects
            else:
                move_speed = self.speed * status_speed_mult  # Normal speed + status effects
            
            if keys.get(self.controls['up'], False):
                dy -= move_speed
            if keys.get(self.controls['down'], False):
                dy += move_speed
            if keys.get(self.controls['left'], False):
                dx -= move_speed
            if keys.get(self.controls['right'], False):
                dx += move_speed
        else:
            # Fallback to move_dir (set by handle_event)
            if self.is_sprinting:
                move_speed = self.speed * 1.5 * status_speed_mult  # Sprint + status effects
            elif is_sneaking:
                move_speed = self.speed * 0.5 * status_speed_mult  # Sneak + status effects
            else:
                move_speed = self.speed * status_speed_mult  # Normal speed + status effects
            
            if self.move_dir['up']:
                dy -= move_speed
            if self.move_dir['down']:
                dy += move_speed
            if self.move_dir['left']:
                dx -= move_speed
            if self.move_dir['right']:
                dx += move_speed
        
        # Update facing direction based on movement
        if dx != 0 or dy != 0:
            # Prioritize vertical movement for direction
            if abs(dy) > abs(dx):
                if dy < 0:
                    self.facing_direction = 'up'
                else:
                    self.facing_direction = 'down'
            else:
                if dx < 0:
                    self.facing_direction = 'left'
                else:
                    self.facing_direction = 'right'
        
        # Get world and enemies from kwargs for collision checking
        world = kwargs.get('world')
        enemies_list = kwargs.get('enemies_list', [])
        
        # Apply collision detection if world is available
        if world and (dx != 0 or dy != 0):
            from config import Config
            tile_size = Config.TILE_SIZE
            blocking_types = {'tree', 'bush', 'rock_group', 'water', 'wall'}
            
            # Check horizontal movement
            if dx != 0:
                new_x = self.x + dx
                # Convert to tile grid coordinates
                tile_wx = (int(new_x) // tile_size) * tile_size
                tile_wy = (int(self.y) // tile_size) * tile_size
                tile = world.get_tile(tile_wx, tile_wy)
                
                # Check terrain collision
                can_move_x = True
                if tile and hasattr(tile, 'layers'):
                    ground = tile.layers.get('ground')
                    obj = tile.layers.get('object')
                    if ground in blocking_types or obj in blocking_types:
                        can_move_x = False
                
                # Check enemy collision
                if can_move_x and enemies_list:
                    for enemy in enemies_list:
                        if hasattr(enemy, 'alive') and enemy.alive and hasattr(enemy, 'rect'):
                            # Calculate distance from potential new position
                            dx_to_enemy = new_x - enemy.rect.centerx
                            dy_to_enemy = self.y - enemy.rect.centery
                            dist = (dx_to_enemy**2 + dy_to_enemy**2) ** 0.5
                            
                            # Enemy collision radius (based on enemy size)
                            collision_radius = 35
                            if hasattr(enemy, 'size'):
                                # Use the larger dimension of the enemy size
                                enemy_radius = max(enemy.size[0], enemy.size[1]) / 2
                                collision_radius = enemy_radius + 15  # Enemy radius plus buffer
                            
                            if dist < collision_radius:
                                can_move_x = False
                                break
                
                if can_move_x:
                    self.x = new_x
            
            # Check vertical movement
            if dy != 0:
                new_y = self.y + dy
                # Convert to tile grid coordinates
                tile_wx = (int(self.x) // tile_size) * tile_size
                tile_wy = (int(new_y) // tile_size) * tile_size
                tile = world.get_tile(tile_wx, tile_wy)
                
                # Check terrain collision
                can_move_y = True
                if tile and hasattr(tile, 'layers'):
                    ground = tile.layers.get('ground')
                    obj = tile.layers.get('object')
                    if ground in blocking_types or obj in blocking_types:
                        can_move_y = False
                
                # Check enemy collision
                if can_move_y and enemies_list:
                    for enemy in enemies_list:
                        if hasattr(enemy, 'alive') and enemy.alive and hasattr(enemy, 'rect'):
                            # Calculate distance from potential new position
                            dx_to_enemy = self.x - enemy.rect.centerx
                            dy_to_enemy = new_y - enemy.rect.centery
                            dist = (dx_to_enemy**2 + dy_to_enemy**2) ** 0.5
                            
                            # Enemy collision radius (based on enemy size)
                            collision_radius = 35
                            if hasattr(enemy, 'size'):
                                # Use the larger dimension of the enemy size
                                enemy_radius = max(enemy.size[0], enemy.size[1]) / 2
                                collision_radius = enemy_radius + 15  # Enemy radius plus buffer
                            
                            if dist < collision_radius:
                                can_move_y = False
                                break
                
                if can_move_y:
                    self.y = new_y
        else:
            # No collision checking, just move
            self.x += dx
            self.y += dy
        
        # Update collision rect to match position
        self.rect.center = (int(self.x), int(self.y))

    def add_item(self, item):
        """Add an Item object to inventory"""
        if hasattr(item, 'name'):
            self.inventory['items'].append(item)

    def remove_item(self, item):
        """Remove an Item object from inventory"""
        if item in self.inventory.get('items', []):
            self.inventory['items'].remove(item)

    def cast_spell(self, spell_id, target_x, target_y):
        """Cast a spell - delegates to advanced_spells system if available"""
        if self.advanced_spells and hasattr(self.advanced_spells, 'cast_spell'):
            return self.advanced_spells.cast_spell(spell_id, self, target_x, target_y)
        return None

    def attempt_dodge_roll(self, direction_x, direction_y):
        """Attempt a dodge roll with stamina cost and invulnerability frames"""
        # Check stamina requirement
        dodge_cost = 20
        if self.stamina < dodge_cost:
            return False, "Not enough stamina to dodge!"
        
        # Check if direction is provided
        if direction_x == 0 and direction_y == 0:
            return False, "No direction for dodge roll!"
        
        # Consume stamina
        self.stamina = max(0, self.stamina - dodge_cost)
        
        # Normalize direction
        magnitude = (direction_x**2 + direction_y**2) ** 0.5
        if magnitude > 0:
            direction_x /= magnitude
            direction_y /= magnitude
        
        # Perform dodge roll (move player quickly in direction)
        dodge_distance = 120  # pixels
        self.x += direction_x * dodge_distance
        self.y += direction_y * dodge_distance
        
        # Update rect
        self.rect.center = (int(self.x), int(self.y))
        
        # Set invulnerability frames (handled by status_manager if available)
        if self.status_manager and hasattr(self.status_manager, 'add_effect'):
            # Add temporary invulnerability (0.5 seconds)
            self.status_manager.add_effect('invulnerable', duration=30)  # 30 frames at 60 FPS
        
        return True, "Dodge successful!"

    def equip(self, item, slot):
        """Equip an item to a slot, returns previously equipped item"""
        # Check for Orc dual-2H weapon special case
        if slot == 'off_hand' and hasattr(item, 'type') and item.type == 'weapon':
            # Check if this is a two-handed weapon
            is_two_handed = getattr(item, 'two_handed', False) or 'two-handed' in getattr(item, 'description', '').lower()
            
            if is_two_handed:
                # Only Orcs can dual-wield two-handed weapons
                if hasattr(self, 'trait_manager') and self.trait_manager:
                    if not self.trait_manager.can_dual_wield_two_handed():
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"[EQUIPMENT] Cannot equip two-handed weapon in off-hand (Orc racial required)")
                        return None  # Prevent equipping
                    else:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"[RACIAL TRAIT] Orc dual-wielding two-handed weapons!")
                else:
                    return None  # No trait manager = can't dual-wield 2H
        
        prev = self.equipment.get(slot)
        self.equipment[slot] = item
        return prev

    def unequip(self, slot):
        """Unequip item from slot"""
        self.equipment[slot] = None

    def start_gathering(self, node):
        """Start gathering from a resource node"""
        # Check if node exists and is available
        if not node:
            return False, "No resource node found"
        
        # Check if node can be gathered
        if not node.can_gather(self):
            if node.gatherer and node.gatherer != self:
                return False, "Someone else is gathering this node"
            return False, "This node is depleted"
        
        # Check skill level requirements
        if hasattr(node, 'node_type'):
            from gathering_nodes import NodeType
            
            # Get required skill level from resource type
            required_level = 1  # Default
            if node.node_type == NodeType.MINING:
                skill_level = self.skills_manager.get_level('Mining') if self.skills_manager else 1
            elif node.node_type == NodeType.WOODCUTTING:
                skill_level = self.skills_manager.get_level('Woodcutting') if self.skills_manager else 1
            elif node.node_type == NodeType.FISHING:
                skill_level = self.skills_manager.get_level('Fishing') if self.skills_manager else 1
            else:
                skill_level = 1
            
            if skill_level < required_level:
                return False, f"You need level {required_level} to gather this resource"
        
        # Start gathering
        if node.start_gathering(self):
            self.gathering_node = node
            self.gathering_progress = 0
            resource_name = getattr(node, 'resource_type', 'resource').replace('_', ' ').title()
            return True, f"Started gathering {resource_name}..."
        
        return False, "Failed to start gathering"
    
    def stop_gathering(self):
        """Stop gathering from current node"""
        if self.gathering_node:
            self.gathering_node.stop_gathering(self)
            self.gathering_node = None
            self.gathering_progress = 0
    
    def complete_gathering(self, resource_type, xp_reward):
        """Complete gathering and receive resource"""
        # Add resource to inventory
        if resource_type not in self.inventory:
            self.inventory[resource_type] = 0
        self.inventory[resource_type] += 1
        
        # Award XP to appropriate skill
        if self.skills_manager and self.gathering_node:
            from gathering_nodes import NodeType
            
            skill_name = None
            if self.gathering_node.node_type == NodeType.MINING:
                skill_name = 'Mining'
            elif self.gathering_node.node_type == NodeType.WOODCUTTING:
                skill_name = 'Woodcutting'
            elif self.gathering_node.node_type == NodeType.FISHING:
                skill_name = 'Fishing'
            
            if skill_name:
                # Apply racial XP modifiers (Dwarf: +100% mining, Elf: +50% all gathering)
                modified_xp = xp_reward
                if hasattr(self, 'trait_manager') and self.trait_manager:
                    # 'gathering' type for Elf bonus, specific skill names for Dwarf
                    xp_type = skill_name.lower()
                    modified_xp = self.trait_manager.apply_xp_modifier(xp_reward, xp_type)
                    
                    if modified_xp != xp_reward:
                        import logging
                        logger = logging.getLogger(__name__)
                        bonus = modified_xp - xp_reward
                        logger.info(f"[RACIAL TRAIT] {skill_name} XP bonus: {xp_reward} → {modified_xp:.0f} (+{bonus:.0f})")
                
                self.skills_manager.add_xp(skill_name, modified_xp)
        
        # Stop gathering
        self.stop_gathering()

    def take_damage(self, damage, attacker=None, damage_type='physical'):
        """Take damage with racial trait modifiers"""
        original_damage = damage
        
        # Check for dodge (Halfling: 8% chance)
        if hasattr(self, 'trait_manager') and self.trait_manager:
            if self.trait_manager.check_dodge_chance():
                # Attack dodged!
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[RACIAL TRAIT] Halfling dodged {original_damage} damage!")
                return 0
        
        # Apply racial damage reduction
        if hasattr(self, 'trait_manager') and self.trait_manager:
            damage = self.trait_manager.apply_incoming_damage_reduction(damage, damage_type)
            if damage < original_damage:
                import logging
                logger = logging.getLogger(__name__)
                reduction = original_damage - damage
                logger.info(f"[RACIAL TRAIT] Reduced {original_damage} → {damage:.0f} damage ({reduction:.0f} blocked by racial traits)")
        
        actual_damage = max(0, damage)
        self.health -= actual_damage
        self.health = max(0, self.health)
        return actual_damage

    def check_building_collision(self, buildings=None, building_interior=None):
        """Check collision with buildings and interiors"""
        if building_interior:
            # Check collision with interior walls and objects
            player_rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
            
            # Check objects (including wall objects - no need for hardcoded boundaries)
            if hasattr(building_interior, 'objects'):
                current_floor = getattr(building_interior, 'current_floor', 1)
                for obj in building_interior.objects:
                    # Only check solid objects on current floor
                    if hasattr(obj, 'solid') and obj.solid:
                        # Skip objects on different floors
                        if hasattr(obj, 'floor') and obj.floor != current_floor:
                            continue
                        
                        # Create rect from object position and size
                        obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        
                        if player_rect.colliderect(obj_rect):
                            # Debug: Write collision to file
                            with open("collision_debug.txt", "a") as f:
                                f.write(f"[COLLISION] Player at ({self.x:.0f}, {self.y:.0f}) colliding with {obj.type} '{obj.name}' at ({obj.x:.0f}, {obj.y:.0f}) size ({obj.width}x{obj.height})\n")
                            
                            # Push player out of object
                            overlap_x = min(player_rect.right - obj_rect.left, obj_rect.right - player_rect.left)
                            overlap_y = min(player_rect.bottom - obj_rect.top, obj_rect.bottom - player_rect.top)
                            
                            if overlap_x < overlap_y:
                                # Push horizontally
                                if player_rect.centerx < obj_rect.centerx:
                                    self.x = obj_rect.left - 15
                                else:
                                    self.x = obj_rect.right + 15
                            else:
                                # Push vertically
                                if player_rect.centery < obj_rect.centery:
                                    self.y = obj_rect.top - 15
                                else:
                                    self.y = obj_rect.bottom + 15
            
            # Update rect
            self.rect.center = (int(self.x), int(self.y))
        
        elif buildings:
            # Check collision with building exteriors (reduced collision box for more natural movement)
            player_rect = pygame.Rect(self.x - 12, self.y - 12, 24, 24)
            
            for building in buildings:
                if hasattr(building, 'rect'):
                    # Create a slightly smaller collision box for the building (allow walking closer to walls)
                    building_collision_rect = building.rect.inflate(-20, -20)
                    
                    if player_rect.colliderect(building_collision_rect):
                        # Only push player if significantly overlapping (reduce invisible wall effect)
                        overlap_x = min(player_rect.right - building_collision_rect.left, building_collision_rect.right - player_rect.left)
                        overlap_y = min(player_rect.bottom - building_collision_rect.top, building_collision_rect.bottom - player_rect.top)
                        
                        # Only push if overlap is significant (>5 pixels)
                        if overlap_x > 5 and overlap_y > 5:
                            if overlap_x < overlap_y:
                                # Push horizontally
                                if player_rect.centerx < building_collision_rect.centerx:
                                    self.x = building_collision_rect.left - 12
                                else:
                                    self.x = building_collision_rect.right + 12
                            else:
                                # Push vertically
                                if player_rect.centery < building_collision_rect.centery:
                                    self.y = building_collision_rect.top - 12
                                else:
                                    self.y = building_collision_rect.bottom + 12
                            
                            # Update rect
                            self.rect.center = (int(self.x), int(self.y))
                        break

    def check_enemy_collision(self, enemies_list):
        """Check collision with enemies and handle contact damage"""
        # Check if player is invulnerable (from dodge roll or other effects)
        is_invulnerable = False
        if self.status_manager and hasattr(self.status_manager, 'has_effect'):
            is_invulnerable = self.status_manager.has_effect('invulnerable')
        
        if is_invulnerable:
            return  # No collision damage while invulnerable
        
        # Check collision with each enemy
        for enemy in enemies_list:
            if not hasattr(enemy, 'alive') or not enemy.alive:
                continue
            
            if hasattr(enemy, 'rect'):
                dx = self.x - enemy.rect.centerx
                dy = self.y - enemy.rect.centery
                distance = (dx**2 + dy**2) ** 0.5
                
                # Collision radius depends on enemy size
                collision_radius = 35
                if hasattr(enemy, 'size'):
                    enemy_radius = max(enemy.size[0], enemy.size[1]) / 2
                    collision_radius = enemy_radius + 15  # Enemy radius plus buffer
                
                if distance < collision_radius:
                    # Calculate contact damage
                    base_damage = 5
                    if hasattr(enemy, 'level'):
                        base_damage = 3 + enemy.level * 2
                    elif hasattr(enemy, 'damage'):
                        base_damage = enemy.damage
                    
                    # Apply damage with cooldown (once per second)
                    current_time = pygame.time.get_ticks()
                    last_contact = getattr(self, 'last_contact_damage', 0)
                    
                    if current_time - last_contact >= 1000:  # 1 second cooldown
                        self.take_damage(base_damage)
                        self.last_contact_damage = current_time
                        
                        # Push player away from enemy
                        if distance > 0:
                            push_strength = 15
                            self.x += (dx / distance) * push_strength
                            self.y += (dy / distance) * push_strength
                            self.rect.center = (int(self.x), int(self.y))

    def get_attack_cooldown(self):
        """Get attack cooldown time in seconds with racial modifiers"""
        base_cooldown = 0.5  # seconds (was 500ms)
        
        # Apply racial attack speed modifiers (Orc: +20% during rage = 0.8x cooldown)
        if hasattr(self, 'trait_manager') and self.trait_manager:
            speed_modifier = self.trait_manager.get_attack_speed_modifier()
            if speed_modifier != 1.0:
                modified_cooldown = base_cooldown * speed_modifier
                return modified_cooldown
        
        return base_cooldown

    def check_level_up(self):
        """Check if player should level up"""
        xp_needed = self.level * 100
        if self.xp >= xp_needed:
            self.xp -= xp_needed
            self.level += 1
            self.max_health += 10
            self.health = self.max_health
            
            # Award level-up rewards
            self.stat_points += 3  # Points for allocating to base stats
            self.perk_points += 1  # Points for skill tree perks
            
            # Apply racial bonuses (Human: +1 extra stat point)
            if hasattr(self, 'trait_manager') and self.trait_manager:
                bonus_stat_points = self.trait_manager.get_bonus_stat_points_per_level()
                if bonus_stat_points > 0:
                    self.stat_points += bonus_stat_points
            
            return True
        return False

    def allocate_stat_point(self, stat_name):
        """Allocate a stat point to a stat
        Returns: (success: bool, message: str)
        """
        if self.stat_points <= 0:
            return False, "No stat points available!"
        
        # Map stat names to attributes
        stat_to_attr = {
            "Strength": "strength",
            "Defense": "defense",
            "Magic": "magic",
            "Stamina": "stamina_stat",
            "Speed": "speed",
            "Agility": "agility",
            "Willpower": "willpower",
            "Luck": "luck",
            "Intelligence": "intelligence",
            "Talking": "talking"
        }
        
        attr_name = stat_to_attr.get(stat_name)
        if not attr_name:
            return False, f"Unknown stat: {stat_name}"
        
        # Allocate the point
        current_value = getattr(self, attr_name, 0)
        setattr(self, attr_name, current_value + 1)
        self.stat_points -= 1
        
        return True, f"{stat_name} increased to {current_value + 1}!"

    def break_tile(self, world=None):
        """Break tile at player position with DECREASING drop rates (50% reduction each time)"""
        if world is None:
            return False
        
        import random
        from config import Config
        tile_size = Config.TILE_SIZE
        
        # Convert player pixel position to tile grid coordinates
        tile_x = (int(self.x) // tile_size) * tile_size
        tile_y = (int(self.y) // tile_size) * tile_size
        
        # Define breakable tile types
        breakable_types = {'tree', 'bush', 'rock_group', 'mushroom_patch', 'grass'}
        
        # CHECK ALL 9 SURROUNDING TILES for breakable resources (trees have collision, can't stand on them!)
        found_resource = None
        found_tile_x = None
        found_tile_y = None
        found_tile = None
        
        for dy in [-tile_size, 0, tile_size]:
            for dx in [-tile_size, 0, tile_size]:
                check_x = tile_x + dx
                check_y = tile_y + dy
                check_tile = world.get_tile(check_x, check_y)
                
                if check_tile and hasattr(check_tile, 'layers'):
                    obj = check_tile.layers.get('object')
                    ground = check_tile.layers.get('ground')
                    
                    # Prioritize object over ground (trees/bushes before grass)
                    resource_type = obj if obj in breakable_types else (ground if ground in breakable_types else None)
                    
                    if resource_type:
                        found_resource = resource_type
                        found_tile_x = check_x
                        found_tile_y = check_y
                        found_tile = check_tile
                        break  # Found something breakable, stop searching
            if found_resource:
                break  # Break outer loop too
        
        if not found_resource:
            return False
        
        resource_type = found_resource
        tile = found_tile
        ground = tile.layers.get('ground')
        obj = tile.layers.get('object')
        
        broke_something = False
        if resource_type:
            # STICK GRINDING SYSTEM: Multiplicative 25% reduction per tree
            # Creates infinite grind - sticks become increasingly rare but never impossible
            # 100% → 75% → 56% → 42% → 32% → 24% → 18% → 13% → 10% → 7.5% → 5.6% → 4.2% → 3.2% ...
            if resource_type == 'tree':
                self.trees_broken_count += 1
                
                # STICKS: Exponential decay - reduces by 25% each tree (multiplicative)
                # Formula: 0.75 ** (trees_broken - 1) = continuous 25% reduction that never hits zero
                stick_chance = 0.75 ** (self.trees_broken_count - 1)
                roll = random.random()
                success = roll < stick_chance
                
                print(f"[TREE BREAK] Tree #{self.trees_broken_count}: Stick chance={stick_chance*100:.2f}%, Roll={roll:.4f}, {'SUCCESS' if success else 'FAIL'}")
                
                if success:
                    # Get 1 stick on success - use the dict-based inventory that the entire game uses
                    num_sticks = 1
                    if 'stick' not in self.inventory:
                        self.inventory['stick'] = 0
                    self.inventory['stick'] += num_sticks
                    print(f"[TREE BREAK] Added {num_sticks} stick(s). Total in inventory: {self.inventory['stick']}")
                    
                    # Track tutorial quest progress for stick collection
                    print(f"[QUEST DEBUG] Checking quest tracking: tutorial_active={self.tutorial_active}, stick_count={self.inventory.get('stick', 0)}")
                    if hasattr(self, 'tutorial_active') and self.tutorial_active and self.inventory.get('stick', 0) >= 3:
                        self.tutorial_stage = 'sticks_collected'
                        print("[TUTORIAL] *** Stick collection objective complete! (3+ sticks collected) ***")
                
                # Bonus apple: Fixed 10% chance (random, not decreasing)
                apple_chance = 0.10
                if random.random() < apple_chance:
                    self.add_item_by_name('apple', 1)
                    
            elif resource_type == 'bush':
                # BERRIES: Fixed 50% chance (random, not decreasing)
                berries_chance = 0.50
                if random.random() < berries_chance:
                    num_berries = random.randint(1, 2)
                    self.add_item_by_name('berries', num_berries)
                    
            elif resource_type == 'rock_group':
                # ORE: Fixed 40% chance (random, not decreasing)
                ore_chance = 0.40
                if random.random() < ore_chance:
                    num_ore = random.randint(1, 2)
                    self.add_item_by_name('ore', num_ore)
                
                # Bonus rubble: Fixed 20% chance
                rubble_chance = 0.20
                if random.random() < rubble_chance:
                    self.add_item_by_name('rubble', 1)
                    
            elif resource_type == 'mushroom_patch':
                # MUSHROOM: Fixed 35% chance (random, not decreasing)
                mushroom_chance = 0.35
                if random.random() < mushroom_chance:
                    self.add_item_by_name('mushroom', 1)
                    
            elif resource_type == 'grass':
                # Grass doesn't have decreasing rates (always low chance)
                fiber_chance = 0.20  # 20% chance
                if random.random() < fiber_chance:
                    self.add_item_by_name('fiber', 1)
                
                herbs_chance = 0.05  # 5% chance
                if random.random() < herbs_chance:
                    self.add_item_by_name('herbs', 1)
            
            # Actually remove/replace the tile - check which layer we broke
            if resource_type == ground:
                # Broke the ground layer - replace grass with sand (bare ground), others with grass
                from tile import Tile
                if resource_type == 'grass':
                    # Grass becomes sand after harvesting (bare ground)
                    world.set_tile(found_tile_x, found_tile_y, Tile(ground='sand'))
                else:
                    world.set_tile(found_tile_x, found_tile_y, Tile(ground='grass'))
                broke_something = True
                
                # Register harvest for respawn tracking
                if hasattr(self, 'respawn_manager') and self.respawn_manager:
                    self.respawn_manager.register_harvest(found_tile_x, found_tile_y, resource_type)
                    
            elif resource_type == obj:
                # Broke the object layer - remove it
                tile.layers['object'] = None
                broke_something = True
                
                # Register harvest for respawn tracking
                if hasattr(self, 'respawn_manager') and self.respawn_manager:
                    self.respawn_manager.register_harvest(found_tile_x, found_tile_y, resource_type)
        
        return broke_something
    
    def add_item_by_name(self, item_name, count=1):
        """Add an item to inventory by name (for simple resource gathering)"""
        if not hasattr(self, 'inventory') or not isinstance(self.inventory, dict):
            self.inventory = {}
        if 'items' not in self.inventory:
            self.inventory['items'] = []
        
        # Add to stackable inventory if it exists
        if item_name not in self.inventory:
            self.inventory[item_name] = 0
        self.inventory[item_name] += count

    def use_item(self, item_name_or_obj):
        """Use a consumable item (food, potion, quest). Returns feedback string."""
        if not self.can_use_consumable():
            return "You must wait before using another item!"
        
        # Stackable food/potion/quest (by name)
        if isinstance(item_name_or_obj, str):
            name = item_name_or_obj
            
            # Food items
            if name == 'apple':
                if self.inventory.get('apple', 0) > 0:
                    self.health = min(self.max_health, self.health + 10)
                    self.inventory['apple'] -= 1
                    self.consumable_cooldown = 60
                    return "You eat an apple. (+10 HP)"
                return "No apples left!"
                
            elif name == 'bread':
                if self.inventory.get('bread', 0) > 0:
                    self.stamina = min(self.max_stamina, self.stamina + 15)
                    self.inventory['bread'] -= 1
                    self.consumable_cooldown = 60
                    return "You eat bread. (+15 Stamina)"
                return "No bread left!"
                
            # Potions
            elif name == 'health_potion':
                if self.inventory.get('health_potion', 0) > 0:
                    self.health = min(self.max_health, self.health + 50)
                    self.inventory['health_potion'] -= 1
                    self.consumable_cooldown = 120
                    
                    # Check for disease cures
                    msg = "You drink a health potion. (+50 HP)"
                    if hasattr(self, 'disease_manager'):
                        diseases = self.disease_manager.get_entity_diseases("player")
                        for disease_infection in diseases:
                            disease = disease_infection.disease
                            if disease.is_curable and "potion" in disease.cures:
                                self.disease_manager.cure_disease("player", disease.disease_id, "potion")
                                msg += f"\nCured {disease.name}!"
                    return msg
                return "No health potions left!"
                
            elif name == 'mana_potion':
                if self.inventory.get('mana_potion', 0) > 0:
                    self.mana = min(self.max_mana, self.mana + 40)
                    self.inventory['mana_potion'] -= 1
                    self.consumable_cooldown = 120
                    
                    # Check for disease cures
                    msg = "You drink a mana potion. (+40 Mana)"
                    if hasattr(self, 'disease_manager'):
                        diseases = self.disease_manager.get_entity_diseases("player")
                        for disease_infection in diseases:
                            disease = disease_infection.disease
                            if disease.is_curable and "potion" in disease.cures:
                                self.disease_manager.cure_disease("player", disease.disease_id, "potion")
                                msg += f"\nCured {disease.name}!"
                    return msg
                return "No mana potions left!"
            
            elif name == 'herbs':
                if self.inventory.get('herbs', 0) > 0:
                    self.inventory['herbs'] -= 1
                    self.consumable_cooldown = 60
                    
                    # Herbs cure common diseases
                    msg = "You consume healing herbs."
                    if hasattr(self, 'disease_manager'):
                        diseases = self.disease_manager.get_entity_diseases("player")
                        cured_count = 0
                        for disease_infection in diseases:
                            disease = disease_infection.disease
                            if disease.is_curable and "herbs" in disease.cures:
                                self.disease_manager.cure_disease("player", disease.disease_id, "herbs")
                                msg += f"\nCured {disease.name}!"
                                cured_count += 1
                        if cured_count == 0:
                            msg += " (+5 HP)"
                            self.health = min(self.max_health, self.health + 5)
                    return msg
                return "No herbs left!"
            
            # Dungeon Ingredients (cure magical diseases + pay 1000 dubloons)
            elif name == 'arcane_crystal':
                if self.inventory.get('arcane_crystal', 0) > 0:
                    if self.dubloons < 1000:
                        return "Arcane Crystal requires 1000 dubloons to activate!"
                    
                    if hasattr(self, 'disease_manager'):
                        diseases = self.disease_manager.get_entity_diseases("player")
                        cured = False
                        for disease_infection in diseases:
                            disease = disease_infection.disease
                            if disease.disease_id in ["mana_rot", "arcane_flu"]:
                                self.inventory['arcane_crystal'] -= 1
                                self.dubloons -= 1000
                                self.disease_manager.cure_disease("player", disease.disease_id, "dungeon_ingredient")
                                self.consumable_cooldown = 120
                                return f"Arcane Crystal glows! Cured {disease.name}! (-1000db)"
                        return "You don't have Mana Rot or Arcane Flu to cure!"
                    return "No magical diseases detected!"
                return "No Arcane Crystals!"
            
            elif name == 'shadow_essence':
                if self.inventory.get('shadow_essence', 0) > 0:
                    if self.dubloons < 1500:
                        return "Shadow Essence requires 1500 dubloons to activate!"
                    
                    if hasattr(self, 'disease_manager'):
                        diseases = self.disease_manager.get_entity_diseases("player")
                        for disease_infection in diseases:
                            disease = disease_infection.disease
                            if disease.disease_id == "shadow_plague":
                                self.inventory['shadow_essence'] -= 1
                                self.dubloons -= 1500
                                self.disease_manager.cure_disease("player", disease.disease_id, "dungeon_ingredient")
                                self.consumable_cooldown = 120
                                return f"Shadow Essence purifies! Cured {disease.name}! (-1500db)"
                        return "You don't have Shadow Plague to cure!"
                    return "No magical diseases detected!"
                return "No Shadow Essence!"
            
            elif name == 'fey_dust':
                if self.inventory.get('fey_dust', 0) > 0:
                    if self.dubloons < 1500:
                        return "Fey Dust requires 1500 dubloons to activate!"
                    
                    if hasattr(self, 'disease_manager'):
                        diseases = self.disease_manager.get_entity_diseases("player")
                        for disease_infection in diseases:
                            disease = disease_infection.disease
                            if disease.disease_id == "fey_fever":
                                self.inventory['fey_dust'] -= 1
                                self.dubloons -= 1500
                                self.disease_manager.cure_disease("player", disease.disease_id, "dungeon_ingredient")
                                self.consumable_cooldown = 120
                                return f"Fey Dust sparkles! Cured {disease.name}! (-1500db)"
                        return "You don't have Fey Fever to cure!"
                    return "No magical diseases detected!"
                return "No Fey Dust!"
            
            elif name == 'infernal_ash':
                if self.inventory.get('infernal_ash', 0) > 0:
                    if self.dubloons < 1000:
                        return "Infernal Ash requires 1000 dubloons to activate!"
                    
                    if hasattr(self, 'disease_manager'):
                        diseases = self.disease_manager.get_entity_diseases("player")
                        for disease_infection in diseases:
                            disease = disease_infection.disease
                            if disease.disease_id == "fire_sneezing":
                                self.inventory['infernal_ash'] -= 1
                                self.dubloons -= 1000
                                self.disease_manager.cure_disease("player", disease.disease_id, "dungeon_ingredient")
                                self.consumable_cooldown = 120
                                return f"Infernal Ash burns away curse! Cured {disease.name}! (-1000db)"
                        return "You don't have Fire Sneezing Curse to cure!"
                    return "No magical diseases detected!"
                return "No Infernal Ash!"
            
            elif name == 'soul_fragment':
                if self.inventory.get('soul_fragment', 0) > 0:
                    if self.dubloons < 2500:
                        return "Soul Fragment requires 2500 dubloons to activate!"
                    
                    if hasattr(self, 'disease_manager'):
                        diseases = self.disease_manager.get_entity_diseases("player")
                        for disease_infection in diseases:
                            disease = disease_infection.disease
                            if disease.disease_id == "soul_binding_sickness":
                                self.inventory['soul_fragment'] -= 1
                                self.dubloons -= 2500
                                self.disease_manager.cure_disease("player", disease.disease_id, "dungeon_ingredient")
                                self.consumable_cooldown = 120
                                return f"Soul Fragment resonates! Cured {disease.name}! (-2500db)"
                        return "You don't have Soul Binding Sickness to cure!"
                    return "No magical diseases detected!"
                return "No Soul Fragments!"
                
            elif name == 'quest_gem':
                if self.inventory.get('quest_gem', 0) > 0:
                    self.inventory['quest_gem'] -= 1
                    self.consumable_cooldown = 30
                    return "You use the quest gem. Something happens!"
                return "No quest gems left!"
                
            else:
                return f"You can't use {name}!"

        # Item object (equipment/gear/special items)
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
                    
            elif item.type == 'food':
                self.health = min(self.max_health, self.health + 10)
                self.consumable_cooldown = 60
                self.remove_item(item)
                return f"You eat {item.name}. (+10 HP)"
                
            elif item.type == 'quest':
                self.consumable_cooldown = 30
                self.remove_item(item)
                return f"You use {item.name}. Something happens!"
                
            return f"You can't use {item.name}!"
        
        return "You can't use that!"

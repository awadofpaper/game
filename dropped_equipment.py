import pygame
import time
import random
from equipment import EQUIPMENT_DATA, EQUIPMENT_RARITY, EQUIPMENT_SETS

class DroppedEquipment:
    def __init__(self, equipment_id, x, y, rarity=None):
        self.equipment_id = equipment_id
        self.data = EQUIPMENT_DATA[equipment_id]
        # Use provided rarity if given, otherwise use the item's default
        self.rarity = rarity if rarity is not None else self.data.get("rarity", "common")
        self.rarity_data = EQUIPMENT_RARITY[self.rarity]
        self.rect = pygame.Rect(x, y, 16, 16)  # Small pickup size
        self.color = self.rarity_data["color"]
        self.name = self.data["name"]
        self.spawn_time = time.time()
        
        # Auto-pickup compatibility
        self.type = "equipment"
        self.equipment_type = self.data.get("type", "weapon")     
        
    def draw(self, screen, offset):
        # Draw the equipment pickup with rarity color
        pr = self.rect.move(-offset[0], -offset[1])
        pygame.draw.rect(screen, self.color, pr)
        # Draw equipped armor and weapons on the dropped equipment
        armor_shapes = {
            "helmet": {"shape": "circle", "offset": (8, 2), "size": 6},
            "chestplate": {"shape": "rect", "offset": (8, 8), "size": (10, 8)},
            "leggings": {"shape": "rect", "offset": (8, 14), "size": (8, 6)},
            "boots": {"shape": "rect", "offset": (8, 20), "size": (6, 4)},
        }
        item_type = self.data.get("type", "")
        rarity = self.data.get("rarity", "common")
        color = EQUIPMENT_RARITY[rarity]["color"]
        if "color" in self.data:
            color = self.data["color"]

        # Draw armor shapes
        for part, info in armor_shapes.items():
            if part in item_type:
                ox, oy = info["offset"]
                if info["shape"] == "circle":
                    pygame.draw.circle(screen, color, (pr.x + ox, pr.y + oy), info["size"])
                    pygame.draw.circle(screen, (0, 0, 0), (pr.x + ox, pr.y + oy), info["size"], 2)
                elif info["shape"] == "rect":
                    w, h = info["size"]
                    rect = pygame.Rect(pr.x + ox - w // 2, pr.y + oy - h // 2, w, h)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        # Draw weapon shapes
        if "stick" in item_type:
            # Draw brown wooden stick
            brown = (139, 90, 43)
            pygame.draw.line(screen, brown, (pr.x + 8, pr.y + 4), (pr.x + 8, pr.y + 20), 4)
            pygame.draw.line(screen, (0, 0, 0), (pr.x + 8, pr.y + 4), (pr.x + 8, pr.y + 20), 1)
            # Wood grain
            for i in range(1, 4):
                y = pr.y + 4 + i * 5
                pygame.draw.line(screen, (101, 67, 33), (pr.x + 6, y), (pr.x + 10, y), 1)
        elif "sword" in item_type:
            pygame.draw.line(screen, (180, 180, 180), (pr.x + 8, pr.y + 6), (pr.x + 8, pr.y + 14), 4)
            pygame.draw.line(screen, (0, 0, 0), (pr.x + 8, pr.y + 6), (pr.x + 8, pr.y + 14), 2)
            pygame.draw.line(screen, (80, 60, 40), (pr.x + 8, pr.y + 14), (pr.x + 8, pr.y + 18), 3)
            pygame.draw.line(screen, (0, 0, 0), (pr.x + 8, pr.y + 14), (pr.x + 8, pr.y + 18), 1)
        elif "axe" in item_type:
            pygame.draw.line(screen, (80, 60, 40), (pr.x + 8, pr.y + 6), (pr.x + 8, pr.y + 16), 4)
            pygame.draw.line(screen, (0, 0, 0), (pr.x + 8, pr.y + 6), (pr.x + 8, pr.y + 16), 2)
            pygame.draw.polygon(screen, (180, 180, 180), [(pr.x + 4, pr.y + 6), (pr.x + 12, pr.y + 6), (pr.x + 8, pr.y + 2)])
            pygame.draw.polygon(screen, (0, 0, 0), [(pr.x + 4, pr.y + 6), (pr.x + 12, pr.y + 6), (pr.x + 8, pr.y + 2)], 1)
        elif "staff" in item_type or "wand" in item_type:
            pygame.draw.line(screen, (80, 60, 40), (pr.x + 8, pr.y + 6), (pr.x + 8, pr.y + 18), 3)
            pygame.draw.line(screen, (0, 0, 0), (pr.x + 8, pr.y + 6), (pr.x + 8, pr.y + 18), 1)
            pygame.draw.circle(screen, (180, 180, 180), (pr.x + 8, pr.y + 6), 3)
            pygame.draw.circle(screen, (0, 0, 0), (pr.x + 8, pr.y + 6), 3, 1)
        elif "shield" in item_type:
            pygame.draw.circle(screen, (180, 180, 180), (pr.x + 8, pr.y + 12), 6)
            pygame.draw.circle(screen, (0, 0, 0), (pr.x + 8, pr.y + 12), 6, 2)
        elif "dagger" in item_type:
            pygame.draw.line(screen, (180, 180, 180), (pr.x + 8, pr.y + 8), (pr.x + 8, pr.y + 16), 2)
            pygame.draw.line(screen, (0, 0, 0), (pr.x + 8, pr.y + 8), (pr.x + 8, pr.y + 16), 1)
        elif "spear" in item_type:
            pygame.draw.line(screen, (180, 180, 180), (pr.x + 8, pr.y + 6), (pr.x + 8, pr.y + 18), 2)
            pygame.draw.line(screen, (0, 0, 0), (pr.x + 8, pr.y + 6), (pr.x + 8, pr.y + 18), 1)
            pygame.draw.polygon(screen, (180, 180, 180), [(pr.x + 6, pr.y + 6), (pr.x + 10, pr.y + 6), (pr.x + 8, pr.y + 2)])
            pygame.draw.polygon(screen, (0, 0, 0), [(pr.x + 6, pr.y + 6), (pr.x + 10, pr.y + 6), (pr.x + 8, pr.y + 2)], 1)
        pygame.draw.rect(screen, (255, 255, 255), pr, 1)  # White border
        
        # Optional: Make it pulse/glow
        pulse = abs(int((time.time() - self.spawn_time) * 3) % 2)
        if pulse:
            pygame.draw.rect(screen, self.color, pr.inflate(2, 2), 1)
    
    def can_pickup(self, player_rect):
        return self.rect.colliderect(player_rect)
    
def get_enemy_drops(enemy):
    """Calculate drops from an enemy, potentially including set pieces"""
    drops = []
    
    # Regular drop calculation logic...
    
    # Special logic for rare/legendary enemies to drop set pieces
    if enemy.rarity in ["rare", "legendary", "artifact"] and random.random() < 0.2:  # 20% chance
        # Select a random set
        set_id = random.choice(list(EQUIPMENT_SETS.keys()))
        set_data = EQUIPMENT_SETS[set_id]
        
        # If enemy rarity meets minimum requirement for the set
        if EQUIPMENT_RARITY[enemy.rarity]["multiplier"] >= EQUIPMENT_RARITY[set_data["min_rarity"]]["multiplier"]:
            # Select a random piece from the set
            piece_id = random.choice(set_data["pieces"])
            
            # Ensure the piece exists in EQUIPMENT_DATA
            if piece_id in EQUIPMENT_DATA:
                # Create the item with appropriate rarity
                item_rarity = enemy.rarity  # Or use set_data["min_rarity"] for minimum
                
                # Add item to drops
                drops.append({
                    "id": piece_id,
                    "rarity": item_rarity,
                    # Other item properties...
                })
    
    return drops

class DroppedDubloon:
    def __init__(self, x, y, amount):
        self.x = x
        self.y = y
        self.amount = amount
        self.rect = pygame.Rect(x, y, 16, 16)
        
        # Auto-pickup compatibility
        self.type = "dubloon"
        self.value = amount
        self.name = f"{amount} Dubloons"

    def draw(self, screen, offset):
        pr = self.rect.move(-offset[0], -offset[1])
        pygame.draw.ellipse(screen, (220, 200, 40), pr)
        font = pygame.font.SysFont(None, 16)
        text = font.render(str(self.amount), True, (60, 40, 0))
        screen.blit(text, (pr.x + 2, pr.y + 2))

class DroppedFiller:
    def __init__(self, item_type, x, y):
        self.item_type = item_type
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 16, 16)
        
        # Auto-pickup compatibility
        self.type = item_type
        self.name = item_type.replace('_', ' ').title()

    def draw(self, screen, offset):
        pr = self.rect.move(-offset[0], -offset[1])
        
        # Draw visual graphics for each filler type
        if self.item_type == "fiber":
            # Draw green plant fibers
            pygame.draw.ellipse(screen, (180, 220, 120), pr)
            pygame.draw.line(screen, (100, 180, 80), (pr.left + 4, pr.top + 4), (pr.right - 4, pr.bottom - 4), 2)
            pygame.draw.line(screen, (100, 180, 80), (pr.right - 4, pr.top + 4), (pr.left + 4, pr.bottom - 4), 2)
        elif self.item_type == "wood":
            # Draw brown wood logs
            pygame.draw.rect(screen, (120, 80, 40), pr)
            pygame.draw.rect(screen, (80, 50, 20), pr, 2)  # Bark outline
            # Wood grain lines
            for i in range(3):
                y = pr.top + (i + 1) * (pr.height // 4)
                pygame.draw.line(screen, (80, 50, 20), (pr.left + 2, y), (pr.right - 2, y), 1)
        elif self.item_type == "rubble":
            # Draw gray stone chunks
            pygame.draw.rect(screen, (100, 100, 100), pr)
            pygame.draw.rect(screen, (60, 60, 60), pr, 2)
            # Add some cracks
            pygame.draw.line(screen, (60, 60, 60), (pr.centerx, pr.top), (pr.left + 2, pr.centery), 1)
            pygame.draw.line(screen, (60, 60, 60), (pr.centerx, pr.top), (pr.right - 2, pr.centery), 1)
        elif self.item_type == "ash":
            # Draw gray ash pile
            pygame.draw.ellipse(screen, (140, 140, 140), pr)
            pygame.draw.ellipse(screen, (100, 100, 100), pr, 1)
            # Add some ash particles
            pygame.draw.circle(screen, (120, 120, 120), (pr.centerx - 3, pr.centery - 2), 2)
            pygame.draw.circle(screen, (120, 120, 120), (pr.centerx + 4, pr.centery + 1), 2)
        else:
            # Default fallback
            color = (200, 200, 200)
            pygame.draw.rect(screen, color, pr)
            font = pygame.font.SysFont(None, 16)
            text = font.render(self.item_type[0].upper(), True, (0, 0, 0))
            screen.blit(text, (pr.x + 2, pr.y + 2))
        
class DroppedConsumable:
    def __init__(self, item_type, x, y):
        self.item_type = item_type
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 16, 16)
        
        # Auto-pickup compatibility
        self.type = item_type
        
        # Format name for recipe scrolls
        if item_type.startswith("recipe_"):
            recipe_name = item_type.replace("recipe_", "").replace("_", " ").title()
            self.name = f"{recipe_name} Recipe"
        else:
            self.name = item_type.replace('_', ' ').title()

    def draw(self, screen, offset):
        pr = self.rect.move(-offset[0], -offset[1])
        
        # Recipe scrolls get a special golden color
        if self.item_type.startswith("recipe_"):
            # Draw scroll with rolled ends
            pygame.draw.rect(screen, (255, 215, 0), pr.inflate(-2, 0))  # Gold paper
            pygame.draw.rect(screen, (139, 69, 19), pr, 2)  # Brown border
            # Draw scroll ends (rolled edges)
            pygame.draw.circle(screen, (139, 69, 19), (pr.left + 2, pr.centery), 3)
            pygame.draw.circle(screen, (139, 69, 19), (pr.right - 2, pr.centery), 3)
            # Add some text lines
            for i in range(3):
                y = pr.top + 3 + i * 4
                pygame.draw.line(screen, (139, 69, 19), (pr.left + 4, y), (pr.right - 4, y), 1)
        elif self.item_type == "potion":
            # Draw potion bottle
            bottle_rect = pygame.Rect(pr.x + 4, pr.y + 6, 8, 8)
            pygame.draw.rect(screen, (120, 200, 255), bottle_rect)  # Blue potion
            # Bottle neck
            neck_rect = pygame.Rect(pr.x + 6, pr.y + 3, 4, 4)
            pygame.draw.rect(screen, (100, 180, 220), neck_rect)
            # Cork
            pygame.draw.rect(screen, (139, 69, 19), pygame.Rect(pr.x + 6, pr.y + 2, 4, 2))
            # Shine effect
            pygame.draw.circle(screen, (200, 240, 255), (pr.x + 9, pr.y + 8), 2)
        elif self.item_type == "scroll":
            # Draw scroll
            pygame.draw.rect(screen, (220, 220, 180), pr.inflate(-2, 0))  # Parchment
            pygame.draw.rect(screen, (160, 160, 120), pr, 2)  # Border
            # Rolled edges
            pygame.draw.circle(screen, (160, 160, 120), (pr.left + 2, pr.centery), 3)
            pygame.draw.circle(screen, (160, 160, 120), (pr.right - 2, pr.centery), 3)
            # Mystic symbol
            pygame.draw.circle(screen, (100, 100, 180), (pr.centerx, pr.centery), 3, 1)
        elif self.item_type == "food":
            # Draw food (bread/meat)
            pygame.draw.ellipse(screen, (200, 160, 80), pr)  # Bread color
            pygame.draw.ellipse(screen, (150, 110, 40), pr, 2)  # Crust
            # Add some texture
            pygame.draw.arc(screen, (150, 110, 40), pr.inflate(-4, -4), 0, 3.14, 1)
            pygame.draw.arc(screen, (150, 110, 40), pr.inflate(-4, -4), 3.14, 6.28, 1)
        else:
            # Default fallback - draw as ellipse with letter
            color = (200, 200, 200)
            pygame.draw.ellipse(screen, color, pr)
            font = pygame.font.SysFont(None, 16)
            text = font.render(self.item_type[0].upper(), True, (0, 0, 0))
            screen.blit(text, (pr.x + 2, pr.y + 2))
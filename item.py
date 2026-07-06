# item.py

class Item:
    def __init__(self, name, item_type, stats=None, durability=100, max_durability=100):
        self.name = name
        self.type = item_type  # e.g., 'weapon', 'armor', 'tool', etc.
        self.stats = stats or {}
        self.durability = durability
        self.max_durability = max_durability

    def is_broken(self):
        return self.durability <= 0

    def repair(self, amount=None):
        if amount is None:
            self.durability = self.max_durability
        else:
            self.durability = min(self.max_durability, self.durability + amount)

    def degrade(self, amount=1):
        self.durability = max(0, self.durability - amount)

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'stats': self.stats,
            'durability': self.durability,
            'max_durability': self.max_durability
        }

    @staticmethod
    def from_dict(data):
        return Item(
            name=data['name'],
            item_type=data['type'],
            stats=data.get('stats', {}),
            durability=data.get('durability', 100),
            max_durability=data.get('max_durability', 100)
        )

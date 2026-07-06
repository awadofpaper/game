class EntityManager:
    def __init__(self, config, world):
        self.entities = []
        self.config = config
        self.world = world

    def update(self, player):
        # Update all entities (NPCs, monsters, etc.)
        pass

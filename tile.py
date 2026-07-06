# tile.py

class Tile:
    def __init__(self, ground=None, obj=None, effect=None):
        self.layers = {
            'ground': ground or 'grass',
            'object': obj or None,
            'effect': effect or None
        }

    def to_dict(self):
        return dict(self.layers)

    @staticmethod
    def from_dict(data):
        return Tile(
            ground=data.get('ground', 'grass'),
            obj=data.get('object'),
            effect=data.get('effect')
        )

    def __getitem__(self, layer):
        return self.layers.get(layer)

    def __setitem__(self, layer, value):
        self.layers[layer] = value

    def __contains__(self, layer):
        return layer in self.layers

    def get(self, layer, default=None):
        """Dictionary-style get method for compatibility"""
        return self.layers.get(layer, default)

class Item:
    def __init__(self, name: str = ''):
        self.name = name
    
    @staticmethod
    def from_core(pure_item):
        return Item(pure_item.name)
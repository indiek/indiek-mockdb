def generate_id(existing):    
    return max(existing) + 1 if len(existing) else 0

class Item:
    _item_dict = {}
    def __init__(self, name: str = '', content: str = '', ikid: int = None):
        self.name = name
        self.content = content
        self.ikid = ikid

    def save(self):
        if self.ikid is None:
            self.ikid = generate_id(self._item_dict.keys())
        self._item_dict[self.ikid] = self.to_dict()

    def to_dict(self):
        return {'name': self.name, 'content': self.content}

    @staticmethod
    def from_core(pure_item):
        return Item(**pure_item.to_dict())

    @staticmethod
    def load(ikid):
        dict_ = Item._item_dict[ikid]
        return Item(**dict_)
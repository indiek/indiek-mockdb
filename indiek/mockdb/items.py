from __future__ import annotations
from typing import Sequence, Dict, Optional, List, Any


def generate_id(existing: Sequence[int]) -> int:
    """Generate ID."""
    return max(existing) + 1 if len(existing) else 0


class Item:
    """Class that represents genericItem in mockdb.

    In mockdb, all items are stored in the class variable `Item._item_dict`.

    Unless specified, attributes below should be compatible
    with indiek-core.

    Attributes:
        name (str): item name.
        content (str): item content.
        _ikid (int): ID of item in mockdb. This is not part of indiek-core API.
    """

    _item_dict = {}
    """All items are stored in this class variable that maps item unique ID to their content."""

    def __repr__(self):
        _ikid = self._ikid
        name = self.name
        content_hash = hash(self.content)
        return f"MockDB Item:{_ikid=};{name=};{content_hash=}"
    
    def __str__(self):
        return f"MockDB Item with ID {self._ikid} and name {self.name}"

    def __eq__(self, other) -> bool:
        cond = self._ikid == other._ikid
        cond = cond and self.name == other.name
        cond = cond and self.content == other.content
        return cond and isinstance(other, self.__class__)

    def __init__(
            self, *,
            name: str = '',
            content: str = '',
            _ikid: Optional[int] = None
    ):
        """Initialize Item.

        Args:
            name (str, optional): item name. Defaults to ''.
            content (str, optional): item description. Defaults to ''.
            _ikid (int, optional): item id in mockdb; note that if the id corresponds to an existing
                item in the DB and a save operation occurs later on, the existing data will be overriden.
        """
        self._ikid = _ikid
        self.name = name
        self.content = content

    def save(self) -> int:
        """Save instance data into mockdb.

        If the instance doesn't have an id, (`ikid` attr), a new unique one
        is generated add added before saving.

        Returns:
            int: _ikid of item
        """
        if self._ikid is None:
            self._ikid = generate_id(self._item_dict.keys())
        self._item_dict[self._ikid] = self.to_dict()
        return self._ikid

    def to_dict(self):
        """Return mockdb Item instance content as dict.

        Returns:
            dict: mockdb Item instance
        """
        return {
            '_ikid': self._ikid,
            'name': self.name,
            'content': self.content
        }

    @staticmethod
    def from_core(pure_item: Any) -> Item:
        """Instantiate mockdb Item off of an Item from indiek-core.

        Args:
            pure_item (Any): item instance from indiek-core library.

        Returns:
            Item: mockdb Item instance
        """
        return Item(**pure_item.to_dict())

    @staticmethod
    def load(_ikid: int) -> Item:
        """Load (instantiate) mockdb Item from its ID.

        Args:
            ikid (int): item ID in mockdb.

        Returns:
            Item: mockdb Item instance
        """
        dict_ = Item._item_dict[_ikid]
        return Item(**dict_)

    @classmethod
    def list_all(cls) -> List[Item]:
        """Fetch all stored mockdb items as a list.

        Returns:
            List[Item]: stored items.
        """
        return [cls(**item_dict) for item_dict in cls._item_dict.values()]

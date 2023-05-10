from __future__ import annotations
import re
from typing import Sequence, Optional, List, Any
from frozendict import frozendict


class MixedTypeOverrideError(Exception):
    """
    An item is trying to be saved with an ID 
    pertaining to an existing item of a different type.
    """
    pass


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

    _item_dict = frozendict(
        Definition = {},  # keys MUST match class names from module
        Theorem = {},
        Proof = {},
    )
    """
    All items are stored in this class variable. It is a nested dict. First level of 
    keys are classes, and values are dicts. Second level of keys are item unique IDs 
    (_ikid) and values are dicts containing item data."""

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

    def save(self):
        myclass = self.__class__.__name__

        # check existing ids
        existing_ids = set.union(*(set(d.keys()) for d in self._item_dict.values()))

        if self._ikid is not None:  # item has an ID
            if self._ikid in existing_ids:  # ID already present in DB
                if self._ikid not in self._item_dict[myclass].keys():  # ID belongs to another type
                    raise MixedTypeOverrideError()
                # at this level we are dealing with an override; relegated to end of function
                
        else:  # we generate the ID
            self._ikid = generate_id(existing_ids)

        # we write or override safely
        self._item_dict[myclass][self._ikid] = self.to_dict()
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
    
    @classmethod
    def str_filter(cls, regex: re.Pattern):
        """Return list of items from specified class with a regex match.

        Regex is applied on name and content attr.

        Args:
            regex (re.Pattern): regex to match

        Returns:
            List[Item]: filtered list of stored items
        """
        filtered_dicts = []
        for item_dict in cls._item_dict[cls.__name__].values():
            if regex.search(item_dict['name']):
                filtered_dicts.append(item_dict)
                continue
            if regex.search(item_dict['content']):
                filtered_dicts.append(item_dict)

        return [cls(**item_dict) for item_dict in filtered_dicts]

    @classmethod
    def from_core(cls, pure_item: Any) -> Item:
        """Instantiate mockdb Item off of an Item from indiek-core.

        Args:
            pure_item (Any): item instance from indiek-core library.

        Returns:
            type(self): mockdb Item instance
        """
        return cls(**pure_item.to_dict())

    @classmethod
    def load(cls, _ikid: int) -> Item:
        """Load (instantiate) mockdb Item from its ID.

        Args:
            _ikid (int): item ID in mockdb.

        Returns:
            Item: mockdb Item instance
        """
        dict_ = cls._item_dict[cls.__name__][_ikid]
        return cls(**dict_)

    @classmethod
    def list_all(cls) -> List[Item]:
        """Fetch all stored mockdb items as a list.

        Returns:
            List[Item]: stored items.
        """
        class_items = cls._item_dict[cls.__name__]
        return [cls(**item_dict) for item_dict in class_items.values()]


class Definition(Item):
    pass

class Theorem(Item):
    pass

class Proof(Item):
    pass

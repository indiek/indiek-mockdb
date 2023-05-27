from __future__ import annotations
import re
from typing import Sequence, Optional, List, Any, Set, Tuple
from frozendict import frozendict



class MixedTypeOverrideError(Exception):
    """
    An item is trying to be saved with an ID 
    pertaining to an existing item of a different type.
    """
    pass


class UnsavedNestedNoteError(Exception):
    """
    A Note's content contains unsaved nested notes.
    """
    pass


def generate_id(existing: Sequence[int]) -> int:
    """Generate ID."""
    return max(existing) + 1 if len(existing) else 0


NESTED_NOTE = 'NeStEdNoTe'


class Nucleus:
    _item_dict = frozendict(
        Definition={},  # keys MUST match class names from module
        Theorem={},
        Proof={},
        Note={},
        Question={}
    )
    """
    All items are stored in this class variable. It is a nested dict. First level of 
    keys are classes, and values are dicts. Second level of keys are item unique IDs 
    (ikid) and values are dicts containing item data."""

    def __init__(self, ikid: int | None, forbid_existing: bool = True) -> None:
        if forbid_existing:
            assert ikid not in self.existing_ids, "Attempt to instantiate an existing ikid."
        self.ikid = ikid

    @property
    def existing_ids(self):
        return set.union(*(set(d.keys()) for d in self._item_dict.values()))

    def save(self):
        cls = self.__class__

        if self.ikid is not None:  # item has an ID
            if self.ikid in self.existing_ids:  # ID already present in DB
                if self.ikid not in self._item_dict[cls.__name__].keys():  # ID belongs to another type
                    raise MixedTypeOverrideError()
                # at this level we are dealing with an override; relegated to end of function
                
        else:  # we generate the ID
            self.ikid = generate_id(self.existing_ids)

        # we write or override safely
        self._item_dict[cls.__name__][self.ikid] = self.to_dict()
        return self.ikid
    
    def delete(self):
        cls_name = self.__class__.__name__
        idict = self._item_dict[cls_name]
        ikid = self.ikid

        if cls_name != 'Note':
            # delete name and content notes
            # TODO: I can foresee problems if name and content mutually refer to each other.
            Note.load(self.name).delete()
            Note.load(self.content).delete()

        # delete actual entry
        idict.pop(ikid)

        # reset ikid to unsaved
        self.ikid = None

        # now we clean up all the mentions of this item
        notes_dict = self._item_dict['Note']
        for _, note_dict in notes_dict.items():
            mentions = note_dict['mentions']
            if ikid in mentions:
                mentions.pop(ikid)

    @classmethod
    def load(cls, ikid: int) -> Nucleus:
        """Load (instantiate) mockdb Item from its ID.

        Args:
            ikid (int): item ID in mockdb.

        Returns:
            Item: mockdb Item instance
        """
        dict_ = cls._item_dict[cls.__name__][ikid]
        return cls(**dict_, forbid_existing=False)


class Note(Nucleus):
    @staticmethod
    def is_note(str_entry: str) -> Tuple[bool, int | None]:
        is_note = str_entry.startswith(NESTED_NOTE)
        ikid = str_entry[len(NESTED_NOTE):]
        return is_note, ikid
    
    @classmethod
    def flatten(cls, content):
        to_return = []
        for entry in content:
            if isinstance(entry, str):
                to_return.append(entry)
            else:
                if entry.ikid is None:
                    raise UnsavedNestedNoteError()
                to_return.append(NESTED_NOTE + str(entry.ikid))
        return to_return

    @classmethod
    def from_core(cls, core_note):
        return cls(
            ikid=core_note.ikid, 
            flat_content=cls.flatten(core_note.content),
            mentions=core_note.mentions,
            depth=core_note.depth,
            children=core_note.children,
            )
    
    @property
    def str(self):
        return ' '.join(self.flat_content)
    
    def __init__(self, 
                 flat_content: List[str], 
                 mentions: Set[int],
                 depth: int,
                 children: Set[int],
                 ikid: int | None = None,
                 forbid_existing: bool = True):
        super().__init__(ikid, forbid_existing=forbid_existing)
        self.flat_content = flat_content
        self.mentions = mentions
        self.depth = depth
        self.children = children

    def to_dict(self):
        return dict(
            ikid=self.ikid,
            depth=self.depth,
            children=self.children,
            mentions=self.mentions,
            flat_content=self.flat_content
        )

    @staticmethod
    def create_empty():
        return Note([], set(), 1, children=set())


PointerNote = Note


class Item(Nucleus):
    """Class that represents genericItem in mockdb.

    In mockdb, all items are stored in the class variable `Item._item_dict`.

    Unless specified, attributes below should be compatible
    with indiek-core.self

    Attributes:
        name (int): ikid of Note for item name.
        content (int): ikid of Note for item content.
        ikid (int): ID of item in mockdb. This is not part of indiek-core API.
    """

    _attr_defs = ['name', 'content', 'ikid']
    """List of attr that fully define an Item."""

    def __repr__(self):
        ikid = self.ikid
        name = self.name
        content_hash = hash(self.content)
        return f"MockDB Item:{ikid=};{name=};{content_hash=}"

    def __str__(self):
        return f"MockDB Item with ID {self.ikid} and name {self.name}"

    def __eq__(self, other) -> bool:
        attr_eq = all(getattr(self, a) == getattr(other, a) for a in Item._attr_defs)
        return attr_eq and type(other) == type(self)

    def __init__(
            self, *,
            name: Optional[int] = None,
            content: Optional[int] = None,
            ikid: Optional[int] = None,
            forbid_existing: bool = True
    ):
        """Initialize Item.

        Args:
            name (int, optional): item name. Defaults to None. This is the ikid of a Note.
            content (int, optional): item description. Defaults to None. This is the ikid of a Note.
            ikid (int, optional): item id in mockdb; note that if the id corresponds to an existing
                item in the DB and a save operation occurs later on, the existing data will be overriden.
        """
        # breakpoint()
        
        super().__init__(ikid, forbid_existing=forbid_existing)
        self.name = name
        self.content = content

    def load_note(self, attr_name):
        return Note.load(getattr(self, attr_name))
    
    def save(self):
        super().save()
        # breakpoint()
        for attr_name in set(self._attr_defs) - {'ikid'}:
            attr_val = getattr(self, attr_name)
            if attr_val is None:
                note = Note.create_empty()
            else:  # TODO: this overrides the note...
                note = Note.load(attr_val)
            setattr(self, attr_name, note.save())
        return self.ikid

    def to_dict(self):
        """Return mockdb Item instance content as dict.

        Returns:
            dict: mockdb Item instance
        """
        return {a: getattr(self, a) for a in self._attr_defs}

    def reload(self):
        """Reload written values if ikid exists otherwise nothing happens."""
        if self.ikid is not None:
            written = self._item_dict[self.__class__.__name__][self.ikid]
            for attribute in self._attr_defs:
                setattr(self, attribute, written[attribute])
    
    @classmethod
    def str_filter(cls, regex: re.Pattern):
        """Return list of items from specified class with a regex match.

        Regex is applied on name and content attr.

        Args:
            regex (re.Pattern): regex to match

        Returns:
            List[Item]: filtered list of stored items
        """
        # TODO: revisit
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
    def list_all(cls) -> List[Item]:
        """Fetch all stored mockdb items as a list.

        Returns:
            List[Item]: stored items.
        """
        class_items = cls._item_dict[cls.__name__]
        return [cls(**item_dict) for item_dict in class_items.values()]


# TODO: automate class create below (__new__?)
# Note impact of classes below on Item._item_dict
class Definition(Item): pass
class Theorem(Item): pass
class Proof(Item): pass
class Question(Item): pass


ITEM_CLASSES = [
    Definition, 
    Theorem, 
    Proof,
    Question,
    ]
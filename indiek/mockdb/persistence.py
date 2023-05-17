from .items import Item
import json
from frozendict import frozendict


def persist(file_path):
    with open(file_path, 'wt') as f:
        json.dump(Item._item_dict, f)


def load_from_file(file_path):
    with open(file_path, 'rt') as f:
        loaded = json.load(f)
    cleaned = {}
    for cls_name, cls_dict in loaded.items():
        # cast ikid to int below
        sub_dict = {int(ikid): v for ikid, v in cls_dict.items()}
        cleaned[cls_name] = sub_dict

    Item._item_dict = frozendict(cleaned)
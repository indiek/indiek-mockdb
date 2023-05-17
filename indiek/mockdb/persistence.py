from .items import Item
import json


def persist(file_path):
    with open(file_path, 'wt') as f:
        json.dump(Item._item_dict, f)


def load_from_file(file_path):
    with open(file_path, 'rt') as f:
        Item._item_dict = json.load(f)

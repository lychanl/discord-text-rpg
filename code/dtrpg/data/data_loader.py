from dtrpg.data.loaders.schema_loader import SchemaLoader
from dtrpg.data.loaders.type_loader import TypeLoader

from typing import Dict

import os
import yaml


class DuplicateIdentifierError(Exception):
    pass


class InvalidIdError(Exception):
    pass


class DataLoader:
    def __init__(self):
        self._schema_loader = SchemaLoader()
        self._loaders = None
        self._world = None

    def load(self, schema_path: str, world_dir: str):
        self._loaders = self._load_schema(schema_path)
        self._world = self._load_world(world_dir)

    def _load_world(self, world_dir):
        obj_dicts = self._load_world_files(world_dir)
        objects = self._parse_obj_dicts(obj_dicts)
        return objects

    def _load_world_files(self, world_dir):
        obj_dicts = {}
        for root, _, filenames in os.walk(world_dir):
            for filename in filenames:
                if os.path.splitext(filename)[1] in ('.yaml', '.yml'):
                    fpath = os.path.join(root, filename)
                    with open(fpath, 'r') as world_file:
                        file_obj = yaml.safe_load(world_file)
                        for key, value in file_obj.items():
                            name, type_ = self._split_name_type(key)
                            if name in obj_dicts:
                                raise DuplicateIdentifierError(f'Duplicate name: {name} in file {fpath}')

                            obj_dicts[name] = (type_, value)

        return obj_dicts

    def _parse_obj_dicts(self, obj_dicts):
        objects = {name: self._loaders[type_].preload() for name, (type_, _) in obj_dicts.items()}

        for name, (type_, dict_) in obj_dicts.items():
            loader = self._loaders[type_]
            obj = objects[name]
            loader.load(obj, objects, dict_)

        return objects

    def _split_name_type(self, value):
        tokens = value.split()
        if len(tokens) > 2 or len(tokens) < 1:
            raise InvalidIdError(f'Invalid identifier: {value}')
        name = tokens[-1]
        type_ = tokens[-2] if len(tokens) > 1 else None

        return name, type_

    def _load_schema(self, path: str) -> Dict[str, TypeLoader]:
        with open(path, 'r') as schema_file:
            structure = yaml.safe_load(schema_file)
            return self._schema_loader.parse_schema(structure)

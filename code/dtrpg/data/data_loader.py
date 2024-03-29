from dtrpg.data.parsing.parser import NameParser
from dtrpg.data.locale.localized_object import LocalizedObject
from dtrpg.core.game_object import GameObject
from dtrpg.data.loaders.schema_loader import SchemaLoader
from dtrpg.data.loaders.type_loader import TypeLoader
from dtrpg.data.locale.locale_loader import LocaleLoader

from dtrpg.core import Config

from typing import Dict, Iterable, Tuple

import csv
import os
import yaml


class DuplicateIdentifierError(Exception):
    pass


class InvalidIdError(Exception):
    pass


class LoadException(Exception):
    pass


class DataLoader:
    def __init__(self):
        self._schema_loader = SchemaLoader()
        self._loaders = None
        self._world = None
        self._locale = None

    def load(self, schema_path: str, world_dir: str, locale_path: str) -> None:
        self._loaders = self._load_schema(schema_path)
        self._world = self._load_world(world_dir)
        self._locale_loader = self._load_locale(locale_path)

        self._locale_loader.apply(self._world, self._loaders)
        self._create_default_parsers(self._loaders.values(), self._world.values())

    def _load_world(self, world_dir: str) -> dict:
        obj_dicts = self._load_world_files(world_dir)
        objects, game_objects = self._parse_obj_dicts(obj_dicts)
        for obj in game_objects:
            obj.finalize()
        return objects

    def _load_world_files(self, world_dir: str):
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

    def _parse_obj_dicts(self, obj_dicts: dict) -> Tuple[dict, list]:
        game_objects = []
        objects = {name: self._loaders[type_].preload() for name, (type_, _) in obj_dicts.items()}

        for name, (type_, dict_) in obj_dicts.items():
            try:
                loader = self._loaders[type_]
                obj = objects[name]
                loader.load(obj, name, name, None, objects, dict_, game_objects, self._loaders)
            except Exception as e:
                raise LoadException(f'Error while loading {name}: {e}') from e

        named_objects = {name: obj for name, obj in game_objects if name}
        named_objects.update(objects)
        all_game_objects = [obj for _, obj in game_objects if isinstance(obj, GameObject)]

        return named_objects, all_game_objects

    def _split_name_type(self, value: str) -> None:
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

    def get_config(self, config_name: str) -> Config:
        config = self._world[config_name]
        if not isinstance(config, Config):
            raise TypeError('Config must be of type Config!')

        return config

    def get_world(self) -> Iterable[object]:
        return list(self._world.values())

    def _load_locale(self, locale_path: str) -> LocaleLoader:
        locale_rows = []
        for root, _, fnames in os.walk(locale_path):
            for fname in fnames:
                if os.path.splitext(fname)[-1] == '.csv':
                    with open(os.path.join(root, fname)) as fp:
                        locale_rows.extend(list(csv.DictReader(fp)))

        return LocaleLoader(locale_rows)

    def _create_default_parsers(self, loaders: Iterable[TypeLoader], world: Iterable[LocalizedObject]):
        for loader in loaders:
            if issubclass(loader.class_, LocalizedObject):
                loader.class_.default_parser = NameParser(loader.class_, world)

from dtrpg.data.loaders.schema_loader import SchemaLoader

import yaml


class DataLoader:
    def __init__(self):
        self._schema_loader = SchemaLoader()
        self._loaders = None

    def load(self, schema_path: str):
        self._loaders = self._load_schema(schema_path)

    def _load_schema(self, path: str) -> SchemaLoader:
        with open(path, 'r') as schema_file:
            structure = yaml.load(schema_file)
            return self._schema_loader.parse_schema(structure)

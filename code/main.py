from dtrpg.data.data_loader import DataLoader

import argparse
import os


def main(schema_path: str, world_path: str) -> None:
    loader = DataLoader()
    loader.load(schema_path, world_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--schema', type=str, default=os.path.join('..', 'worlds', 'schema.yaml'), help='Path to schema file')
    parser.add_argument('--world', type=str, required=True, help='Path to the directory with world files')

    args = parser.parse_args()

    main(args.schema, args.world)

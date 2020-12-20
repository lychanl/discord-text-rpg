from dtrpg.data.data_loader import DataLoader

import argparse
import os


def main(schema_path: str, world_path: str, config_name: str) -> None:
    loader = DataLoader()
    loader.load(schema_path, world_path)
    config = loader.get_config(config_name)
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--schema',
        type=str,
        default=os.path.join('..', 'worlds', 'schema.yaml'),
        help='Path to schema file'
    )
    parser.add_argument('--world', type=str, required=True, help='Path to the directory with world files')
    parser.add_argument('--config', type=str, default='config', help='Config object to use')

    args = parser.parse_args()

    main(args.schema, args.world, args.config)

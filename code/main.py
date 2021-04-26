import sys

if sys.version_info.major < 3 or sys.version_info.major == 3 and sys.version_info.minor < 7:
    raise RuntimeError(f"Python version must be at least 3.7. Current: {sys.version}")

from dtrpg.core import Game
from dtrpg.data.data_loader import DataLoader
from dtrpg.io import CommandLineIO

import argparse
import os
import yaml


INTERFACES = {
    'cli': CommandLineIO
}

try:
    from dtrpg.io.dcio import DiscordBotIO
    INTERFACES['discord'] = DiscordBotIO
except ImportError:
    pass


def prepare_game(schema_path: str, world_path: str, config_name: str, locale_path: str) -> Game:
    loader = DataLoader()
    loader.load(schema_path, world_path, locale_path)
    config = loader.get_config(config_name)
    objects = loader.get_world()
    return Game(config, objects)


def load_client_config(path: str) -> dict:
    if path:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    else:
        return {}


def main(
    schema_path: str, world_path: str, config_name: str, locale_path: str, interface_name: str, client_config: str
) -> None:
    game = prepare_game(schema_path, world_path, config_name, locale_path)

    config_data = load_client_config(client_config)

    interface = INTERFACES[interface_name](game, **config_data)
    interface.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--schema',
        type=str,
        default=os.path.join(os.path.dirname(__file__), '..', 'worlds', 'schema.yaml'),
        help='Path to schema file'
    )
    parser.add_argument('--world', type=str, required=True, help='Path to the directory with world files')
    parser.add_argument('--config', type=str, default='config', help='Config object to use (default `config`)')
    parser.add_argument(
        '--locales',
        type=str,
        default=None,
        help='Path to locales directory (default `locales` in world files'
    )
    parser.add_argument('--locale', type=str, default=None, help='Locale, default - first directory in locales')
    parser.add_argument(
        '--client-config',
        type=str,
        default=None,
        help='Client configuration file'
    )
    parser.add_argument('interface', type=str, choices=INTERFACES.keys(), help='Interface')

    args = parser.parse_args()

    locales_path = args.locales or os.path.join(args.world, 'locales')
    locale = args.locale or next(iter(os.listdir(locales_path)))
    locale_path = os.path.join(locales_path, locale)

    main(args.schema, args.world, args.config, locale_path, args.interface, args.client_config)

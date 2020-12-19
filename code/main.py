from dtrpg.data.data_loader import DataLoader

import argparse
import os


def main(schema_path):
    loader = DataLoader()
    loader.load(schema_path)
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--schema', type=str, default=os.path.join('..', 'worlds', 'schema.yaml'))

    args = parser.parse_args()

    main(args.schema)

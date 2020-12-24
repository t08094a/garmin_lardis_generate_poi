#!/usr/bin/python3

import sys
import os
import errno
import argparse
from pathlib import Path
import shutil
import logging
from typing import List, Dict, Any
from xml.dom.minidom import parse, Node


class ReadableDir(argparse.Action):
    def __call__(self, arg_parser, namespace, values, option_string=None):
        prospective_dir = values

        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))

        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self. dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


def get_all_gpx_files(source_dir: str) -> List[Path]:
    path = Path(source_dir)
    if not path.exists():
        raise NotADirectoryError(errno.ENOENT, os.strerror(errno.ENOENT), source_dir)

    files: List[Path] = list(path.glob('*.gpx'))

    return files


def generate_target_structure(target_dir: Path, gpx_files: List[Path]) -> List[Path]:
    # if not target_dir.is_dir():
    #     raise NotADirectoryError(errno.ENOENT, os.strerror(errno.ENOENT), target_dir)
    if not gpx_files:
        # TODO: log
        return

    if target_dir.exists():
        print('target already exist, delete it: ' + str(target_dir.resolve()))
        shutil.rmtree(str(target_dir.resolve()))

    print('create target: ' + str(target_dir.resolve()))
    target_dir.mkdir(parents=True)

    new_target_gpx_files: Dict[Path, str] = {}

    for gpx in gpx_files:
        current_target: Path = Path.joinpath(target_dir, gpx.stem)
        current_target.mkdir()

        shutil.copy(gpx.resolve(), current_target.resolve())

        symbol: Path = Path(gpx.with_suffix('.bmp'))
        #symbol: Path = Path(gpx.with_suffix('.png'))
        shutil.copy(symbol.resolve(), current_target.resolve())

        new_target_gpx_files[current_target.joinpath(gpx.name)] = symbol.stem

    return new_target_gpx_files


def add_symbol_to_gpx_waypoints(gpx_files: Dict[Path, str]):
    for gpx in gpx_files:
        print('modify: ' + str(gpx.resolve()))
        symbol_name: str = gpx_files[gpx]

        with gpx.open(mode='r', encoding='UTF-8') as gpx_file:
            with parse(gpx_file) as dom:
                for node in dom.getElementsByTagName('wpt'):
                    symNode: Node = dom.createElement('sym')
                    symContent: Node = dom.createTextNode(symbol_name)
                    symNode.appendChild(symContent)

                    node.appendChild(symNode)

                with gpx.open(mode='w', encoding='UTF-8') as file_write:
                    dom.writexml(file_write, indent='  ', addindent='  ', newl='\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reichert GPX Dateien mit individuellen Symbolen an. Die Ausgabe erfolgt in einem Unterverzeichnis.')
    parser.add_argument('source',
                        action=ReadableDir,
                        help='Das Verzeichnis das alle GPX Dateien enthält. Die Symbole müssen den identischen Dateinamen zu den GPX Dateien haben.')
    parser.add_argument('target',
                        help='Das Zielverzeichnis in dem die erzeugten Dateien abgelegt werden sollen.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Sei gesprächig')

    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        parser.print_help()
        sys.exit(0)

    found_gpx_files: List[Path] = get_all_gpx_files(Path(args.source))
    target_gpx_files: Dict[Path, str] = generate_target_structure(Path(args.target), found_gpx_files)
    add_symbol_to_gpx_waypoints(target_gpx_files)

#!/usr/bin/python3

import sys
import os
import errno
import argparse
from pathlib import Path
import shutil
import logging
from typing import List, Dict, Any
from xml.dom.minidom import parse, Document, Node, Element


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


def generate_target_structure(target_dir: Path, gpx_files: List[Path]) -> Dict[Path, str]:
    if not gpx_files:
        # TODO: log
        return Dict[Path, str]

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
        shutil.copy(symbol.resolve(), current_target.resolve())

        new_target_gpx_files[current_target.joinpath(gpx.name)] = symbol.stem

    return new_target_gpx_files


def modify_gpx_file(gpx_files: Dict[Path, str]):
    for gpx in gpx_files:
        print('modify: ' + str(gpx.resolve()))
        symbol_name: str = gpx_files[gpx]

        with gpx.open(mode='r', encoding='UTF-8') as gpx_file:
            with parse(gpx_file) as dom:
                for wpt in dom.getElementsByTagName('wpt'):
                    add_sym_to_gpx(dom, wpt, symbol_name)
                    add_category_to_gpx(dom, wpt)

                with gpx.open(mode='w', encoding='UTF-8') as file_write:
                    dom.writexml(file_write, indent='  ', addindent='  ', newl='\n')


def add_sym_to_gpx(dom: Document, wpt: Node, symbol_name: str):
    sym_node: Node = dom.createElement('sym')
    sym_content: Node = dom.createTextNode(symbol_name)
    sym_node.appendChild(sym_content)

    wpt.appendChild(sym_node)


def add_category_to_gpx(dom: Document, wpt: Node):
    extensions_node: Element = (wpt.getElementsByTagName('extensions')[:1] or [None])[0]

    if not extensions_node:
        extensions_node = dom.createElement('extensions')
        wpt.appendChild(extensions_node)

    # gpxx=http://www.garmin.com/xmlschemas/GpxExtensions/v3
    gpx_ns: str = 'http://www.garmin.com/xmlschemas/GpxExtensions/v3'
    gpx_ns_short: str = 'gpxx'

    gpxx_waypoint_extension_node: Element = (extensions_node.getElementsByTagNameNS(gpx_ns, 'WaypointExtension')[:1] or [None])[0]
    if not gpxx_waypoint_extension_node:
        dom.documentElement.setAttributeNS('xmls', '%s:%s' % ('xmlns', gpx_ns_short), gpx_ns)

        gpxx_waypoint_extension_node = dom.createElementNS(gpx_ns, '%s:%s' % (gpx_ns_short, 'WaypointExtension'))
        extensions_node.appendChild(gpxx_waypoint_extension_node)

        display_mode_node: Element = dom.createElementNS(gpx_ns, '%s:%s' % (gpx_ns_short, 'DisplayMode'))
        display_mode_content_node: Node = dom.createTextNode('SymbolOnly')
        display_mode_node.appendChild(display_mode_content_node)
        gpxx_waypoint_extension_node.appendChild(display_mode_node)

        categories_node: Element = dom.createElementNS(gpx_ns, '%s:%s' % (gpx_ns_short, 'Categories'))
        gpxx_waypoint_extension_node.appendChild(categories_node)

        category1_node: Element = dom.createElementNS(gpx_ns, '%s:%s' % (gpx_ns_short, 'Category'))
        category1_content_node: Node = dom.createTextNode('Feuerwehr')
        category1_node.appendChild(category1_content_node)
        categories_node.appendChild(category1_node)

        # TODO: abhängig der Datei muss die Kategorie anders gesetzt werden
        category2_node: Element = dom.createElementNS(gpx_ns, '%s:%s' % (gpx_ns_short, 'Category'))
        category2_content_node: Node = dom.createTextNode('Feuerwehr Gerätehäuser')
        category2_node.appendChild(category2_content_node)
        categories_node.appendChild(category2_node)

    # wptx1=http://www.garmin.com/xmlschemas/WaypointExtension/v1
    garmin_ns: str = 'http://www.garmin.com/xmlschemas/WaypointExtension/v1'
    garmin_ns_short: str = 'wptx1'

    garmin_waypoint_extension_node: Element = (extensions_node.getElementsByTagNameNS(garmin_ns, 'WaypointExtension')[:1] or [None])[0]
    if not garmin_waypoint_extension_node:
        dom.documentElement.setAttributeNS('xmls', '%s:%s' % ('xmlns', garmin_ns_short), garmin_ns)

        garmin_waypoint_extension_node = dom.createElementNS(garmin_ns, '%s:%s' % (garmin_ns_short, 'WaypointExtension'))
        extensions_node.appendChild(garmin_waypoint_extension_node)

        display_mode_node: Element = dom.createElementNS(garmin_ns, '%s:%s' % (garmin_ns_short, 'DisplayMode'))
        display_mode_content_node: Node = dom.createTextNode('SymbolOnly')
        display_mode_node.appendChild(display_mode_content_node)
        garmin_waypoint_extension_node.appendChild(display_mode_node)

        categories_node: Element = dom.createElementNS(garmin_ns, '%s:%s' % (garmin_ns_short, 'Categories'))
        garmin_waypoint_extension_node.appendChild(categories_node)

        category1_node: Element = dom.createElementNS(garmin_ns, '%s:%s' % (garmin_ns_short, 'Category'))
        category1_content_node: Node = dom.createTextNode('Feuerwehr')
        category1_node.appendChild(category1_content_node)
        categories_node.appendChild(category1_node)

        # TODO: abhängig der Datei muss die Kategorie anders gesetzt werden
        category2_node: Element = dom.createElementNS(garmin_ns, '%s:%s' % (garmin_ns_short, 'Category'))
        category2_content_node: Node = dom.createTextNode('Feuerwehr Gerätehäuser')
        category2_node.appendChild(category2_content_node)
        categories_node.appendChild(category2_node)


    # getElementsByTagNameNS(namespaceURI, localName)
    # createElementNS


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
    modify_gpx_file(target_gpx_files)

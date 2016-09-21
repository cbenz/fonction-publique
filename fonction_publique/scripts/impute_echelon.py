#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Impute echelons"""


import argparse
import logging
import os
import sys


from fonction_publique.base import raw_directory_path
from fonction_publique import merge_careers_and_legislation

app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)
age_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action = 'store_true', default = False,
        help = 'use smaller subset for debugging purposes')
    parser.add_argument('-s', '--source', default = raw_directory_path,
        help = 'path of source directory containing the stata files or individual stata file')
    # parser.add_argument('-t', '--target', default = output_directory_path,
    #     help = 'path of source directory')
    parser.add_argument('-f', '--force-rebuild', action = 'store_true', default = False, help = "rebuild legislation")
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.INFO if args.verbose else logging.WARNING, stream = sys.stdout)
    if not os.path.exists(args.source):
        log.error('{} is not a valid path')
        raise ValueError
    merge_careers_and_legislation.main(
        source = args.source,
        force_rebuild = args.force_rebuild,
        debug = args.debug,
        )


if __name__ == "__main__":
    sys.exit(main())

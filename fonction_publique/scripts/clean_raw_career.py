#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Clean the raw career data from stata files to stock them in HDF5 stores"""


import argparse
import logging
import os
import sys


from fonction_publique.base import raw_directory_path, clean_directory_path
from fonction_publique import cleaner_base_carriere

app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)
age_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action = 'store_true', default = False,
        help = 'Use smaller subset fro debugging purposes')
    parser.add_argument('-s', '--source', default = raw_directory_path,
        help = 'path of source directory containing the stata files')
    parser.add_argument('-t', '--target', default = clean_directory_path,
        help = 'path of generated hdf5 files through the cleaning operation')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)

    cleaner_base_carriere.main(
        raw_directory_path = args.source,
        clean_directory_path = args.target,
        debug = args.debug,
        )


if __name__ == "__main__":
    sys.exit(main())

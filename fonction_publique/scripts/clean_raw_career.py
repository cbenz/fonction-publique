#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""Clean the raw career data from stata files to stock them in HDF5 stores"""


import argparse
import logging
import os
import sys


from fonction_publique import raw_data_cleaner
from fonction_publique.base import clean_directory_path, raw_directory_path


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--chunksize', type=int,  default = 1000, help = 'size of subset when in debug mode')
    parser.add_argument('-y', '--year_min', type=int,   default = 1900, help = 'starting year for time-varying variables')
    parser.add_argument('--subset_data', nargs='+', default = None,
        help = 'subset of datasets to extract in the source directory. syntax: --subset_data data1 data2')
    parser.add_argument('--subset_var', nargs='+', default = None,
        help = 'subset of variables to extract in the raw dataset. syntax: --subset_var var1 var2')
    parser.add_argument('-d', '--debug', action = 'store_true', default = False,
        help = 'use smaller subset for debugging purposes')
    parser.add_argument('-s', '--source', default = os.path.join(raw_directory_path, "csv"),
        help = 'path of source directory containing the original files (stata or csv)')
    parser.add_argument('-t', '--target', default = clean_directory_path,
        help = 'path of generated hdf5 files through the cleaning operation')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.INFO if args.verbose else logging.WARNING, stream = sys.stdout)
    log.info('Start cleaning data in {}'.format(args.source))
    log.info('Cleaned data will be saved in {}'.format(args.target))


    chunksize = args.chunksize if args.debug else None
    raw_data_cleaner.main(
        raw_directory_path = args.source,
        clean_directory_path = args.target,
        debug = args.debug,
        chunksize = chunksize,
        year_min = args.year_min,
        subset_data = args.subset_data,
        subset_var = args.subset_var,
        )


if __name__ == "__main__":
    sys.exit(main())



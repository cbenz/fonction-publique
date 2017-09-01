#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generate data for imputation and treatment"""


import argparse
import logging
import os
import sys


from fonction_publique.data_generation import (
    step_1_extract_data_by_c_cir,
    step_2_filter_data,
    # step_3_correct_anciennete_echelon,
    )

from fonction_publique.base import output_directory_path


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--first_year', type = int, default = 2011,
        help = 'starting year for dataset. defaut = 2011')
    parser.add_argument('--subset_data', nargs='+', default = [
        '1960_1965_carrieres.h5',
        '1966_1969_carrieres.h5',
        '1970_1975_carrieres.h5',
        '1976_1979_carrieres.h5',
        '1980_1999_carrieres.h5',
        ],
        help = 'subset of datasets to extract from the cleaned data directory. syntax: --subset_data data1 data2')
    parser.add_argument('--list_corps', nargs='+', default = ['adjoints techniques territoriaux'],
        help = 'list of corps to extract from the cleaned data. syntax: --list_corps corps1 corp2')

    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    parser.add_argument('-d', '--debug', action = 'store_true', default = False,
        help = "maximal increase of output verbosity (debug mode)")

    args = parser.parse_args()
    logging.basicConfig(level = logging.INFO if args.verbose else logging.WARNING, stream = sys.stdout)
    if args.debug:
        logging.basicConfig(level = logging.DEBUG)

    # first_year = args.first_year
    first_year = 2000  # 2011 ??
    # step_1_extract_data_by_c_cir.main(
    #     datasets = args.subset_data,
    #     first_year = first_year
    #     list_corps = args.list_corps,
    #     save_path = os.path.join(output_directory_path, 'select_data')
    #     )
    step_2_filter_data.main(corps = args.list_corps[0], first_year = first_year)  # FIXME should loop over list_corps


if __name__ == "__main__":
    sys.exit(main())

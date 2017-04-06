# -*- coding: utf-8 -*-
"""
Created on Wed Apr 05 13:53:10 2017

@author: l.degalle
"""

"""Clean the raw career data from csv files to stock them in HDF5 stores"""


import argparse
import logging
import os
import sys


from fonction_publique import select_data
from fonction_publique.base import clean_directory_path, raw_directory_path


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-y','--first_year', type=int,   default = 2011, help = 'starting year for dataset')
    parser.add_argument('--subset_data', nargs='+', default = ['1980_1999_carrieres.h5',
                                                               '1976_1979_carrieres.h5',
                                                               '1970_1975_carrieres.h5',
                                                               '1960_1965_carrieres.h5',
                                                               '1966_1969_carrieres.h5'],
        help = 'subset of datasets to extract from the cleaned data directory. syntax: --subset_data data1 data2')
    parser.add_argument('--list_corps', nargs='+', default = ['AT'],
        help = 'list of corps to extract from the cleaned data. syntax: --list_corps corps1 corp2')
    parser.add_argument('--list_permanent_variables', nargs='+', default = ['generation', 'sexe', 'an_aff'],
        help = 'list of time invariant variables to extract from the cleaned data. syntax: --list_permanent_variables permanent_variable1 permanent_variable2')
    parser.add_argument('--list_quaterly_variables', nargs='+', default = ['ib', 'echelon', 'etat'],
        help = 'list of quaterly defined variables to extract from the cleaned data. syntax: --list_quaterly_variables quaterly_variable1 quaterly_variable2')
    parser.add_argument('--list_yearly_variables', nargs='+', default = ['c_neg', 'libemploi', 'statut'],
        help = 'list of yearly defined variables to extract from the cleaned data. syntax: --list_yearly_variables yearly_variable1 yearly_variable2')
#    parser.add_argument('-s', '--source', default = os.path.join(clean_directory_path, "csv"),
#        help = 'path of source directory containing the original files (stata or csv)')
#    parser.add_argument('-t', '--target', default = clean_directory_path,
#        help = 'path of generated hdf5 files through the cleaning operation')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.INFO if args.verbose else logging.WARNING, stream = sys.stdout)
#    log.info('Start extracting data from {}'.format(args.source))
#    log.info('Cleaned data will be saved in {}'.format(args.target))


    select_data.main(
        first_year = args.first_year,
        datasets = args.subset_data,
        list_corps = args.list_corps,
        list_permanent_variables = args.list_permanent_variables,
        list_quaterly_variables = args.list_quaterly_variables,
        list_yearly_variables = args.list_yearly_variables
        )


if __name__ == "__main__":
    sys.exit(main())



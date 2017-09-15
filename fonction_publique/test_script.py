# -*- coding: utf-8 -*-


import argparse
import logging
import os
import sys


from fonction_publique.base import (output_directory_path, simulation_directory_path)

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', default = 'data_simul_2011_m1.csv', help = 'input file (csv)')
    parser.add_argument('-o', '--output-file', default = 'results_2011_m1.csv', help = 'output file (csv)')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    parser.add_argument('-d', '--debug', action = 'store_true', default = True, help = "increase output verbosity (debug mode)")

    args = parser.parse_args()
    if args.verbose:
        level = logging.INFO
    elif args.debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(level = level, stream = sys.stdout)
    input_file_path = os.path.join(
        output_directory_path,
        '..',
        'simulation',
        args.input_file
        )
    log.info('Using unput data from {}'.format(input_file_path))
    directory_path = os.path.join(simulation_directory_path, 'results_modif_regles_replacement')
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    output_file_path = os.path.join(directory_path, args.output_file)
    log.info("Saving results to {}".format(output_file_path))


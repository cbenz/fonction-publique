# -*- coding:utf-8 -*-


from __future__ import division

import logging
import os
import re
import time

import pkg_resources

import pandas as pd

from fonction_publique.config import Config

parser = Config()

app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)

# Paths to legislation
asset_path = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )

law_xls_path = os.path.join(
    asset_path,
    "neg_pour_ipp.txt")

law_hdf_path = os.path.join(
    asset_path,
    "grilles.h5")

# Directories paths:
raw_directory_path = parser.get('data', 'raw')
tmp_directory_path = parser.get('data', 'tmp')
clean_directory_path = parser.get('data', 'clean')
output_directory_path = parser.get('data', 'output')


# Options:
DEFAULT_CHUNKSIZE = 30000
DEBUG_CLEAN_CARRIERES = True
debug_chunk_size = 30000


# HDF5 files paths (temporary):
# Store des variables liées aux carrières nettoyées et stockées dans des tables du fichier donnees_de_carrieres.h5
def get_careers_hdf_path(clean_directory_path = None, file_path = None, debug = None):
    return create_file_path(
        directory = clean_directory_path,
        extension = 'carrieres',
        file_path = file_path,
        debug = debug,
        )


def get_tmp_hdf_path(file_path, debug = None):
    return create_file_path(
        directory = tmp_directory_path,
        extension = 'tmp',
        file_path = file_path,
        debug = debug,
        )


def get_output_hdf_path(file_path, debug = None):
    years = re.findall(r'\d+', file_path)
    assert int(years[0]) < int(years[1])
    assert debug is not None, 'debug should be True or False'
    output_hdf_path = os.path.join(
        output_directory_path,
        "debug",
        "{}_{}".format(years[0], years[1])
        ) if debug else os.path.join(
        output_directory_path,
        "{}_{}.h5".format(years[0], years[1]),
        )
    return output_hdf_path


# Helpers

def create_file_path(directory = None, extension = None, file_path = None, debug = None):
    assert directory is not None
    assert extension is not None
    assert (debug is False) or (debug is True), 'debug should be True or False'
    assert file_path is not None
    years = re.findall(r'\d+', file_path)
    filename = "{}_{}_{}.h5".format(
        years[0],
        years[1],
        extension,
        )
    if debug:
        return os.path.join(directory, "debug", filename)
    else:
        return os.path.join(directory, filename)


def get_variables(variables = None, stop = None, decennie = None):
    """Recupere certaines variables de la table des carrières matchées avec grilles"""
    if decennie == 1990:
        hdf5_file_path = os.path.join(output_directory_path, '{}_{}_carrieres.h5'.format(decennie, decennie + 6))
    else:
        hdf5_file_path = os.path.join(output_directory_path, '{}_{}_carrieres.h5'.format(decennie, decennie + 9))
    return pd.read_hdf(hdf5_file_path, 'output', columns = variables, stop = stop)


def get_careers(variable = None, variables = None, stop = None, decennie = None, debug = False, where = None):
    """Recupere certaines variables de la table des carrières bruts"""
    assert (variable is not None) or (variables is not None)
    assert not(
        (variable is not None) and (variables is not None)
        )
    if debug:
        actual_clean_directory_path = os.path.join(
            clean_directory_path,
            'debug',
            )
    else:
        actual_clean_directory_path = clean_directory_path

    if decennie == 1990:
        careers_hdf_path = os.path.join(
            actual_clean_directory_path,
            '{}_{}_carrieres.h5'.format(decennie, decennie + 6)
            )
    else:
        careers_hdf_path = os.path.join(
            actual_clean_directory_path,
            '{}_{}_carrieres.h5'.format(decennie, decennie + 9)
            )
    if variable:
        print('Reading variable {} from file {}'.format(variable, careers_hdf_path))
        return pd.read_hdf(careers_hdf_path, variable, stop = stop, where = where)
    elif variables:
        with pd.HDFStore(careers_hdf_path) as store:
            return store.select_as_multiple(
                variables,
                columns = variables,
                where = where,
                selector = variables[0]
                )


# Timer

def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        log.info('{} function took {:.3f} s'.format(f.func_name, (time2 - time1)))
        return ret
    return wrap

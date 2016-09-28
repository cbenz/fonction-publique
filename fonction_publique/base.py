# -*- coding:utf-8 -*-


from __future__ import division

import logging
import os
import time

import pkg_resources

import pandas as pd

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


# linux_cnracl_path = os.path.join("/run/user/1000/gvfs", "smb-share:server=192.168.1.2,share=data", "CNRACL")
linux_cnracl_path = os.path.join("/home/benjello/data", "CNRACL")
windows_cnracl_path = os.path.join("M:/CNRACL/")
simon_cnracl_path = os.path.join("/Users/simonrabate/Desktop/data/CNRACL/")

if os.path.exists(linux_cnracl_path):
    cnracl_path = linux_cnracl_path
elif os.path.exists(simon_cnracl_path):
    cnracl_path = simon_cnracl_path
else:
    cnracl_path = windows_cnracl_path

# Directories paths:
raw_directory_path = os.path.join(cnracl_path, "raw")
tmp_directory_path = os.path.join(cnracl_path, "tmp")
clean_directory_path = os.path.join(cnracl_path, "clean")
output_directory_path = os.path.join(cnracl_path, "output")


# Options:
DEFAULT_CHUNKSIZE = 30000
DEBUG_CLEAN_CARRIERES = True
debug_chunk_size = 30000


# HDF5 files paths (temporary):
# Store des variables liées aux carrières nettoyées et stockées dans des tables du fichier donnees_de_carrieres.h5
def get_careers_hdf_path(clean_directory_path = None, stata_file_path = None, debug = None):
    return create_file_path(
        directory = clean_directory_path,
        extension = 'carrieres',
        stata_file_path = stata_file_path,
        debug = debug,
        )


def get_tmp_hdf_path(stata_file_path, debug = None):
    return create_file_path(
        directory = tmp_directory_path,
        extension = 'tmp',
        stata_file_path = stata_file_path,
        debug = debug,
        )


def get_output_hdf_path(stata_file_path, debug = None):
    assert debug is not None, 'debug should be True or False'
    output_hdf_path = os.path.join(
        output_directory_path,
        "debug",
        "{}_{}".format(stata_file_path[-14:-10], stata_file_path[-8:-4]),
        ) if debug else os.path.join(
            output_directory_path,
            "{}_{}.h5".format(stata_file_path[-14:-10], stata_file_path[-8:-4]),
            )
    return output_hdf_path


# Helpers
def create_file_path(directory = None, extension = None, stata_file_path = None, debug = None):
    assert directory is not None
    assert extension is not None
    assert (debug is False) or (debug is True), 'debug should be True or False'
    assert stata_file_path is not None
    filename = "{}_{}_{}.h5".format(
        stata_file_path[-14:-10],
        stata_file_path[-8:-4],
        extension,
        )
    if debug:
        return os.path.join(directory, "debug", filename)
    else:
        return os.path.join(directory, filename)


def get_variables(variables = None, stop = None, decennie = None):
    """Recupere certaines variables de la table des carrières matchées avec grilles"""
    hdf5_file_path = os.path.join(output_directory_path, '{}_{}_carrieres.h5'.format(decennie, decennie + 9))
    return pd.read_hdf(hdf5_file_path, 'output', columns = variables, stop = stop)


def get_careers(variable = None, stop = None, decennie = None):
    """Recupere certaines variables de la table des carrières bruts"""

    careers_hdf_path = os.path.join(
        clean_directory_path,
        '{}_{}_carrieres.h5'.format(decennie, decennie + 9)
        )
    return pd.read_hdf(careers_hdf_path, variable, stop = stop)


# Timer
def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        log.info('{} function took {:.3f} s'.format(f.func_name, (time2 - time1)))
        return ret
    return wrap

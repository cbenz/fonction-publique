# -*- coding:utf-8 -*-


from __future__ import division


import os
import pandas as pd

from fonction_publique.base import clean_directory_path


def get_careers(variables = None, stop = None, decennie = None, debug = False):
    """Recupere certaines variables de la table des carrières bruts"""
    if debug:
        actual_clean_directory_path = os.path.join(
            clean_directory_path,
            'debug',
            )
    else:
        actual_clean_directory_path = clean_directory_path

    careers_hdf_path = os.path.join(
        actual_clean_directory_path,
        '{}_{}_carrieres.h5'.format(decennie, decennie + 9)
        )

    with pd.HDFStore(careers_hdf_path) as store:
        df = store.select_as_multiple(
            ['c_cir', 'c_netneh'],
            columns = ['c_cir', 'c_netneh'],
            where = ["annee == 2013 & ident > 2000000"],
            selector = 'c_cir'
            )
    return df


def test_get():
    variables = 'libemploi'
    print(get_careers(variables = variables, decennie = 1970, debug = True))


if __name__ == '__main__':
    # logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    test_get()

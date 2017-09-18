# -*- coding: utf-8 -*-


import pandas as pd

from fonction_publique.merge_careers_and_legislation import get_grilles
from fonction_publique.career_simulation_vectorized import compute_echelon_max


def test_compute_echelon_max():
    grilles = get_grilles()
    compute_echelon_max(grilles = grilles, start_date = None)


def test_grilles_subset():
    grilles = get_grilles(subset = ['libelle_FP', 'libelle_grade_NEG'])
    assert set(grilles.columns) == set(['libelle_FP', 'libelle_grade_NEG', 'date_effet_grille'])


def test_grilles_dates():
    grilles = get_grilles()
    code_grade = 'TTH1'
    tth1 = grilles.loc[
        (grilles.code_grade == code_grade) &
        (grilles.echelon == "01")
        ]

    tth1_extract = tth1.set_index('date_effet_grille')
    # titi.asof(pd.Timestamp(2014, 2, 1))

    date_effet_min = pd.Timestamp(2007, 2, 1)
    date_effet_max = pd.Timestamp(2014, 3, 2)
    assert tth1_extract.loc[date_effet_min:date_effet_max].ib[0] == 297
    assert tth1_extract.loc[date_effet_min:date_effet_max].ib[1] == 330


def test_hdf_grilles():
    from fonction_publique.base import grilles
    code_grade = 'TTH1'

    tth1 = grilles.loc[
        (grilles.code_grade_NETNEH == code_grade) &
        (grilles.echelon == 1)
        ]

    tth1_extract = tth1.set_index('date_effet_grille')
    # titi.asof(pd.Timestamp(2014, 2, 1))

    date_effet_min = pd.Timestamp(2007, 2, 1)
    date_effet_max = pd.Timestamp(2014, 3, 2)
    assert tth1_extract.loc[date_effet_min:date_effet_max].ib[0] == 297
    assert tth1_extract.loc[date_effet_min:date_effet_max].ib[1] == 330


if __name__ == '__main__':
    test_hdf_grilles()
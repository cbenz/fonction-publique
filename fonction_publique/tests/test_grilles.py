# -*- coding: utf-8 -*-


import pandas as pd

from fonction_publique.merge_careers_and_legislation import get_grilles
from fonction_publique.career_simulation_vectorized import compute_echelon_max


grilles = get_grilles('grilles')



def test_compute_echelon_max():
    compute_echelon_max(grilles = grilles, start_date = None)


def test_time_span_grilles():
    code_grade = 'TTH1'
    tth1 = grilles.loc[
    #    (grilles.date_effet_grille > datetime.date(2000, 1, 1)) &
        (grilles.code_grade == code_grade) &
        (grilles.echelon == "01")
        ]

    tth1_extract = tth1.set_index('date_effet_grille')
    # titi.asof(pd.Timestamp(2014, 2, 1))

    date_effet_min = pd.Timestamp(2007, 2, 1)
    date_effet_max = pd.Timestamp(2014, 3, 2)
    assert tth1_extract.loc[date_effet_min:date_effet_max][0] == 297
    assert tth1_extract.loc[date_effet_min:date_effet_max][1] == 330
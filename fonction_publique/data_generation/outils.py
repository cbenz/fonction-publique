# -*- coding: utf-8 -*-
import pandas as pd

def add_grilles_variable(data, grilles = grilles, first_year = 2011, last_year = 2015): #FIXME deal with late policy implementation
    data_after_first_year = data.query('(annee >= @first_year)').copy()
    cas_uniques_with_echelon = list()
    for annee in range(first_year, last_year + 1):
        cas_uniques = (data_after_first_year
            .query('annee == @annee')[['c_cir', 'ib']]
            .drop_duplicates()
            .set_index(['c_cir', 'ib'])
            )
        for (c_cir, ib), row in cas_uniques.iterrows():
            date_effet_grille = grilles[
                (grilles['code_grade_NETNEH'] == c_cir) &
                (grilles['date_effet_grille'] <= pd.datetime(annee, 12, 31))
                ].date_effet_grille.max()
            grille_in_effect = grilles[
                (grilles['code_grade_NETNEH'] == c_cir) &
                (grilles['date_effet_grille'] == date_effet_grille)
                ].query('ib == @ib')
            if grille_in_effect.empty:
                echelon = -1
                min_mois = -1
                moy_mois = -1
                max_mois = -1
                date_effet_grille = -1
            else:
                grille_in_effect = grille_in_effect
                assert len(grille_in_effect) == 1
                echelon = grille_in_effect.echelon.values.astype(str)[0]
                min_mois = grille_in_effect.min_mois.values.astype(int)[0]
                moy_mois = grille_in_effect.moy_mois.values.astype(int)[0]
                max_mois = grille_in_effect.max_mois.values.astype(int)[0]
                date_effet_grille = grille_in_effect.date_effet_grille.values.astype(str)[0]
            cas_uniques_with_echelon.append(
                [annee, c_cir, ib, echelon, min_mois, moy_mois, max_mois, date_effet_grille]
                )
    cas_uniques = pd.DataFrame(
        cas_uniques_with_echelon,
        columns = ['annee', 'c_cir', 'ib', 'echelon', 'min_mois', 'moy_mois', 'max_mois', 'date_effet_grille'],
        )
    assert not cas_uniques[['c_cir', 'ib', 'annee']].duplicated().any()
    data = data.merge(cas_uniques, on = ['c_cir', 'ib', 'annee'], how = 'left')
    data['echelon'] = data['echelon'].fillna(-2).astype(int)
    return data

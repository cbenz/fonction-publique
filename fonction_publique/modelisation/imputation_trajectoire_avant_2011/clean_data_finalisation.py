# -*- coding: utf-8 -*-


from __future__ import division
import os
import pandas as pd
import numpy as np
from clean_data_initialisation import clean_grille, clean_careers, merge_careers_with_grilles
from fonction_publique.base import output_directory_path, project_path

# Paths
careers_asset_path = os.path.join(output_directory_path, 'bases_AT_imputations_trajectoires_1995_2011/')
results_asset_path = os.path.join(output_directory_path, 'base_AT_clean_2006_2011/')
save_path =  os.path.join(output_directory_path, 'estimations/')
grilles_path = os.path.join(project_path, 'assets/')

# Data grilles
grilles = pd.read_hdf(
        os.path.join(grilles_path, 'grilles_fonction_publique/grilles_old.h5')
        )

def load_clean_careers(first_year_data, first_year_imputation, careers_asset_path, grilles):
    '''
    # Load career data from first_year to 2015
    '''
    filename = "corpsAT_{}.csv".format(first_year_data)
    data_carrieres = pd.read_csv(
        os.path.join(careers_asset_path, filename)
        )
    data_carrieres = data_carrieres[data_carrieres.annee >= first_year_imputation]
    data_carrieres = clean_careers(data_carrieres, 'ATT', True, 1960, grilles)
    return data_carrieres


def clean_data_durees_chgt(data_path):
    # On attribue une durée min et max dans le grade, avec un statut d'ambiguité pour la durée max, la durée min
    # étant par définition incertaine
    data_durees_imputees_chgt = pd.read_csv(data_path)

    data_durees_imputees = data_durees_imputees_chgt[[
        "ident",
        "duree_initiale_dans_le_grade.1",
        "duree_initiale_dans_le_grade",
        "duree_initiale_dans_le_grade.2",
        "duree_initiale_dans_le_grade.3",
        "ambiguite_2010",
        "ambiguite_2009",
        "ambiguite_2008",
        "ambiguite_2007"
        ]].set_index("ident")

    data_durees_imputees['min_duration_in_grade'] = data_durees_imputees[[
       "duree_initiale_dans_le_grade",
       "duree_initiale_dans_le_grade.1",
       "duree_initiale_dans_le_grade.2",
       "duree_initiale_dans_le_grade.3"
       ]].min(axis=1)

    data_durees_imputees['max_duration_in_grade'] = data_durees_imputees[[
       "duree_initiale_dans_le_grade",
       "duree_initiale_dans_le_grade.1",
       "duree_initiale_dans_le_grade.2",
       "duree_initiale_dans_le_grade.3"
       ]].max(axis=1)

    data_durees_imputees = data_durees_imputees.reset_index()

    data_ambiguite = []

    data_durees_ecart = data_durees_imputees.reset_index()

    for cas in range(len(data_durees_ecart)):
        data_durees_cas = data_durees_ecart.iloc[cas]
        ident = data_durees_cas['ident']

        if data_durees_cas['min_duration_in_grade'] == 0:
            data_ambig_min = data_durees_cas['ambiguite_2010']
        elif data_durees_cas['min_duration_in_grade'] == 1:
            data_ambig_min = data_durees_cas['ambiguite_2009']

        elif data_durees_cas['min_duration_in_grade'] == 2:
            data_ambig_min = data_durees_cas['ambiguite_2008']

        else:
            data_ambig_min = data_durees_cas['ambiguite_2007']

        if data_durees_cas['max_duration_in_grade'] == 0:
            data_ambig_max = data_durees_cas['ambiguite_2010']
        elif data_durees_cas['max_duration_in_grade'] == 1:
            data_ambig_max = data_durees_cas['ambiguite_2009']
        elif data_durees_cas['max_duration_in_grade'] == 2:
            data_ambig_max = data_durees_cas['ambiguite_2008']
        else:
            data_ambig_max = data_durees_cas['ambiguite_2007']

        data_ambiguite.append([ident, data_ambig_min, data_ambig_max])

    data_ambiguite = pd.DataFrame(
        data_ambiguite,
        columns = ['ident', 'ambig_duree_min', 'ambig_duree_max']
        ).drop_duplicates()

    data_durees_imputees = data_durees_imputees.merge(data_ambiguite, on = 'ident', how = 'left')

    data_durees_imputees['ambig_duree_max'] = data_durees_imputees['ambig_duree_max'].fillna(value=False).astype('bool')
    data_durees_imputees['ambig_duree_min'] = data_durees_imputees['ambig_duree_min'].fillna(value=False).astype('bool')

    # Incertitude en 2007
    data_durees_imputees['ambiguity_2007'] = (data_durees_imputees['ambig_duree_max'])
    data_durees_imputees.loc[data_durees_imputees.ambiguity_2007, 'max_duration_in_grade'] = None


    # Dummy for change
    data_durees_imputees['change'] = [1] * len(data_durees_imputees)

    # Select variables
    data_durees_imputees = data_durees_imputees[[
    "ident",
    "min_duration_in_grade",
    "max_duration_in_grade",
    'ambiguity_2007',
    'change',
    ]]

    # Drop duplicates
    data_durees_imputees = data_durees_imputees.drop_duplicates()

    return data_durees_imputees


def clean_data_durees_non_chgt(data_path):
    # On attribue une durée min et max dans le grade, avec un statut d'ambiguité pour la durée max, la durée min
    # étant par définition incertaine
    data_durees_imputees_non_chgt = pd.read_csv(data_path)

    data_durees_imputees = data_durees_imputees_non_chgt[[ "ident"]].copy()

    data_durees_imputees['change'] = [0] * len(data_durees_imputees)
    data_durees_imputees['min_duration_in_grade'] = [None] * len(data_durees_imputees)
    data_durees_imputees['max_duration_in_grade'] = [None] * len(data_durees_imputees)
    data_durees_imputees['ambiguity_2007'] = [False] * len(data_durees_imputees)

    return data_durees_imputees


def merge_data_durees_and_careers(data_chgt,
                                  data_non_chgt,
                                  data_carreers):
    '''
    Merging data on carreers and imputed initial duration.
    '''
    # For individuals in both chgt and not_change we keep only one observation (those in the change data)
    common_id = list(set(data_chgt.ident) & set(data_non_chgt.ident))
    data_non_chgt = data_non_chgt[~data_non_chgt.ident.isin(common_id)]
    # Appending data
    appended_data = data_chgt.append(data_non_chgt)
    # Merging with careers
    data = data_carreers.merge(appended_data, on = 'ident')
    return data


def tidy_data(data):
    "retourne données mergées 2007 2015 avec une ligne = un individu*année"
    # Initial duration (equal to max or to 2011 - first year)
    data['duree_initiale_en_2011'] = data['max_duration_in_grade']
    data['duree_initiale_en_2011'].fillna(4, inplace=True)
    durees = data.duree_initiale_en_2011.unique().tolist()
    data_clean = []
    for duree in durees:
        data_par_duree = data.query('duree_initiale_en_2011 == {}'.format(duree))
        data_par_duree_group = data_par_duree.groupby('ident').tail(duree + 5)
        data_clean.append(data_par_duree_group)
    data_clean = pd.concat(data_clean)
    data_clean['c_cir_impute_bef_2011'] = data_clean.groupby('ident')['c_cir'].transform('first')
    data_clean_aft_2011 = data_clean.query('annee > 2011')
    data_clean_bef_2011 = data_clean.query('annee <= 2011')
    data_clean_bef_2011.c_cir.fillna(
        data_clean_bef_2011.c_cir_impute_bef_2011, inplace = True
        )
    data_clean = data_clean_bef_2011.append(data_clean_aft_2011).sort(['ident', 'annee'])
    # Ind datamin
    data_clean['I_min'] = (data_clean['annee'] >= 2011 - data_clean['min_duration_in_grade'] )

    del data_clean['c_cir_impute_bef_2011']
    return data_clean


def impute_exit_grade(data):
    data.c_cir.fillna('out', inplace = True)

    data['first_year_in_index'] = data.groupby('ident')['annee'].transform('first')
    data = data.set_index(['ident', 'annee'])

    data = data.sort_index()
    data['past_c_cir'] = data.groupby(level=0)['c_cir'].shift(1); data
    data = data.reset_index()
#    data['c_cir_equal_next_c_cir'] = (data['c_cir'] == data['past_c_cir'])
#
#    data['exit_status'] = (data['c_cir_equal_next_c_cir'] == False) & (data['annee'] != data['first_year_in_index']) #| (data['etat'] == 0)
#    del data['c_cir_equal_next_c_cir']
    data['grade_de_2011'] = data.groupby('ident')['c_cir'].transform('first')

    data['exit_status'] = data['c_cir'] != data['grade_de_2011']
#    del data['first_year_in_index']
    data['exit_status'] = data['exit_status'].astype(int)

    data = data[(data['exit_status'] == 0) | (data['exit_status'] == 1) & (data['past_c_cir'] == data['grade_de_2011'])]

    data['next_grade'] = data.groupby(['ident'])['c_cir'].transform('last')

    data_ident_grade_de_2011 = data[['ident', 'grade_de_2011']].drop_duplicates().rename(columns={'grade_de_2011':'c_cir'})

    data_2011_2015 = data.query('annee > 2010')
    data_2011_2015_group = data_2011_2015.groupby('ident')['c_cir'].value_counts().rename(
        columns = {'c_cir':'c_cir2'}
        ).reset_index()
    data_2011_2015_group = data_2011_2015_group.rename(columns = {0:'duration_in_grade_from_2011'})

    data_duration_in_grade_from_2011 = data_ident_grade_de_2011.merge(
        data_2011_2015_group, on = ['ident', 'c_cir'], how = 'inner'
        )

    data = data.merge(data_duration_in_grade_from_2011, on = ['ident'], how = 'left')
    del data['c_cir_y']
    del data['past_c_cir']
    data = data.rename(columns = {"c_cir_x":"c_cir"})

    data_2015 = data.query('annee == 2015')
    idents_with_right_censoring = data_2015[data_2015['grade_de_2011'] == data_2015['c_cir']].ident.unique()

    data['right_censoring'] = data.ident.isin(idents_with_right_censoring)

    return data


def variables_management(data):
    """
    Creating variables needed for estimations (generation_group, left_censoring) and selecting variables
    kept for estimations

    Parameters
    ---------
    `data`: dataframe

    Returns
    ---------
    dataframe

    """
    data['generation_group'] = data['generation'].apply(str).str[2:3]
    data['generation_group'] = data['generation_group'].astype('category')
    data['generation'] = data.generation.fillna(-1)

    data['left_censoring'] = (data.max_duration_in_grade.isnull())

    variables_kept = [u'ident', u'annee', u'etat', u'c_cir', u'ib', u'grade_de_2011',
                      u'sexe', 'an_aff', u'generation', u'generation_group',
                      u'min_duration_in_grade', u'max_duration_in_grade', u'duration_in_grade_from_2011',
                      u'right_censoring', u'left_censoring', u'change', u'ambiguity_2007',
                      u'exit_status', u'next_grade']

    return data[variables_kept]


def main(first_year_imputation,
         first_year_data,
         careers_asset_path,
         results_asset_path,
         grilles,
         ):
    # Load Carrers
    data_carreers = load_clean_careers(first_year_imputation, first_year_data, careers_asset_path, grilles)
    # Load imputation:
    filename = "data_changement_grade_" + str(first_year_imputation)+ "_2011.csv"
    data_path_chgt = os.path.join(results_asset_path, filename)
    data_chgt = clean_data_durees_chgt(data_path_chgt)
    filename = "data_non_changement_grade_" + str(first_year_imputation)+ "_2011.csv"
    data_path_non_chgt = os.path.join(results_asset_path, filename)
    data_non_chgt = clean_data_durees_non_chgt(data_path_non_chgt)
    # Merge
    data = merge_data_durees_and_careers(data_chgt, data_non_chgt, data_carreers)
    # Formatting
    data_tidy = tidy_data(data)
    data_with_dummy_exit = impute_exit_grade(data_tidy)
    # Variable kept
    final_data = variables_management(data_with_dummy_exit)
    # Save
    filename = "base_AT_clean_" + str(first_year_imputation) + ".csv"
    final_data.to_csv(os.path.join(save_path, filename))
    print("Estimation data saved as {}".format(os.path.join(save_path, filename)))


if __name__ == '__main__':
    main(first_year_imputation = 2007,
         first_year_data = 2007,
         careers_asset_path = careers_asset_path,
         results_asset_path = results_asset_path,
         grilles = grilles,
        )
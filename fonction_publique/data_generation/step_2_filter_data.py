# -*- coding: utf-8 -*-
from __future__ import division

import logging
import numpy as np
import os
import pandas as pd

from fonction_publique.base import add_grilles_variable, grilles, output_directory_path, tmp_directory_path
from fonction_publique.data_generation.add_durations import main_duration

log = logging.getLogger(__name__)


# Read data and replace cir codes for ATT interns
def read_data(data_path = os.path.join(output_directory_path, 'select_data'), corps = None, first_year = None):
    """read output from step_1_extract_data_by_c_cir.py"""
    log.info("Reading data")
    assert corps is not None
    assert first_year is not None
    filename = 'corps{}_{}.csv'.format(corps, first_year)
    log.debug('Reading data from {}'.format(os.path.join(data_path, filename)))
    return pd.read_csv(
        os.path.join(data_path, filename),
        index_col = 0,
        usecols = [
            u'annee',
            u'an_aff',
            u'c_cir',
            u'etat4',
            u'generation',
            u'ib1',
            u'ib2',
            u'ib3',
            u'ib4',
            u'ident',
            u'libemploi',
            u'sexe',
            u'statut',
            ],
        dtype = {
            'annee': int,
            'an_aff': int,
            'c_cir': str,
            'etat4': int,
            'generation': int,
            'ib1': int,
            'ib2': int,
            'ib3': int,
            'ib4': int,
            'ident': int,
            'libemploi': str,
            'sexe': str,
            'statut': str,
            }
        ).rename(columns = {"etat4": "etat", "ib4": "ib"}).reset_index()


def replace_interns_cir(data):
    """replace ATT interns grade code by ATT fonctionnaires grade code"""
    log.info("Replacing interns grade codes")
    interns_cir = {
        "STH1": "TTH1",
        "STH2": "TTH2",
        "STH3": "TTH3",
        "STH4": "TTH4",
        }
    data['c_cir'] = data['c_cir'].replace(interns_cir)
    return data


# I. Sample selection
def select_ATT_in_2011(data):
    """select careers of agents who are ATT (interns and fonctionnaires) in 2011 according to their c_cir"""
    log.info("Selecting ATT agents in 2011")
    ATT_cir = ['TTH1', 'TTH2', 'TTH3', 'TTH4']
    idents_keep = data.query('(annee == 2011) & (c_cir in @ATT_cir)').ident.unique()
    data = data.query('ident in @idents_keep').copy()
    assert set(data.query('annee == 2011').c_cir.unique()) == set(ATT_cir)
    return data


def select_next_state_in_fonction_publique(data):
    """select careers of agents who are active the year after they leave their 2011 grade,
     or who do not leave their grade"""
    log.info("Selecting next grade state active in civil service")
    data = data.merge(
        data.query(
            'annee == 2011'
            ).copy()[['ident', 'c_cir']].rename(columns = {"c_cir": "c_cir_2011"}), on = 'ident', how = 'left'
        )
    data_after_2011 = data.query('(annee > 2011) & (c_cir != c_cir_2011)').copy()[['ident', 'annee']]
    data_after_2011['annee_exit'] = data_after_2011.groupby('ident')['annee'].transform(min)
    data_after_2011 = data_after_2011[['ident', 'annee_exit']].drop_duplicates()
    data = data.merge(data_after_2011, on = 'ident', how = 'left')
    data['annee_exit'] = data['annee_exit'].fillna(9999).astype(int)
    idents_keep = data.query('((annee == annee_exit) & (etat == 1)) | (annee_exit == 9999)').ident.unique()
    return data.query('ident in @idents_keep').copy()


def select_generation(data, generation = 1960):
    """select careers of agents who were born after 1960"""
    log.info("Selecting generation > 1960")
    return data.query('generation > @generation').copy()


def select_continuous_activity_state(data):
    """select careers of agents who are actively working between the maximum between the first year of observation
     (2003 by default) and the year they join civil service, and the last year they spend in their grade, included """
    log.info("Selecting continuous activity")
    data['annee_min_to_consider'] = np.where(data['an_aff'] >= 2003, data['an_aff'], 2003)
    idents_del = data.query('(etat not in [1, 2, 3, 5, 6]) & (annee >= annee_min_to_consider) & (annee < annee_exit)').ident.unique()
    return data.query('ident not in @idents_del').copy()


# II. Data issues
def select_positive_ib(data):  # compare with interval (entry in grade, exit)
    """ select careers of agents who have a stricly positive ib between the maximum between the first year of observation
     (2003 by default) and the year they join civil service, and the minimum between the first year they spend in their
     next grade, included, and 2015 """
    log.info("Selecting strictly positive ib")
    idents_del = data.query('(ib <= 0) & (annee >= annee_min_to_consider) & (annee <= annee_exit)').ident.unique()
    return data.query('ident not in @idents_del').copy()


def select_non_missing_c_cir(data):
    """ select careers of agents with no missing grade code between 2011 and their first year in next grade included (or
    2015 if they do not leave """
    log.info("Selecting non missing code cir")
    data_after_2011 = data.query('(annee > 2011) & (annee <= annee_exit)').copy()
    idents_del = data_after_2011[data_after_2011['c_cir'].isnull()].ident.unique()
    return data.query('ident not in @idents_del').copy()


def select_no_decrease_in_ATT_rank(data):
    """ select careers of agents with no hierarchical decrease in their grade between 2011 and 2015 """
    log.info("Selecting careers with no hierarchical decrease in ATT grades")
    ATT_cir = ['TTH1', 'TTH2', 'TTH3', 'TTH4']
    data_exit = data.query('annee >= annee_exit')
    data_exit = data_exit.groupby('ident')['c_cir'].value_counts().rename(
        columns = {'c_cir': 'c_cir_aft_exit'}
        ).reset_index()
    del data_exit[0]
    data_exit = data_exit.merge(data[['ident', 'c_cir_2011']], on = 'ident', how = 'inner').query(
        "c_cir_2011 != 'TTH1'"
        ).drop_duplicates().query('c_cir in @ATT_cir')
    data_exit = data_exit.query("c_cir_2011 != 'TTH1'").copy()
    for col in ['c_cir', 'c_cir_2011']:
        data_exit[col] = data_exit[col].str[3:].astype(int)
    idents_del = data_exit.query('c_cir < c_cir_2011').ident.unique()
    return data.query('ident not in @idents_del')


def select_no_decrease_in_ib(data):
    """ select careers of agents with no decrease in IB between the maximum between the first year of observation
     (2003 by default) and the year they join civil service, and 2015 """
    log.info("Selecting no decrease in ib on L")
    def non_decreasing(L):
        return all(x <= y for x, y in zip(L, L[1:]))

    data_entered = data.query('annee >= annee_min_to_consider').copy().sort_values('annee', ascending = True)
    data_entered = data_entered.groupby('ident')['ib'].apply(list).reset_index()
    data_entered['non_decreasing'] = data_entered['ib'].apply(non_decreasing)
    idents_del = data_entered.query('non_decreasing == False').copy().ident.unique()
    return data.query('ident not in @idents_del')


def select_no_goings_and_comings_of_rank(data):
    """ select careers of agents who don't come back to their 2011 grade after leaving it """
    log.info("Selecting no goings and comings of grade")
    idents_del = data.query('(annee > annee_exit) & (c_cir == c_cir_2011)').ident.unique()
    return data.query('ident not in @idents_del')


# IV. Sample selection based on echelon variable
def select_non_special_level(data):
    """ select careers of agents who only have regular, numeric echelons if their echelon is not missing """
    log.info("Selecting only numeric echelon")
    data['echelon'] = data['echelon'].astype(int)
    idents_del = data.query('echelon == -5').ident.unique()
    return data.query('ident not in @idents_del')


# V. Filters on echelon variable issues
def select_non_missing_level(data):
    """ select careers of agents with no missing echelon between 2011 and their first year in next grade included"""
    log.info("Selecting non missing echelon")
    idents_del = data.query('(echelon == -1) & (annee <= annee_exit)').ident.unique()
    return data.query('ident not in @idents_del')


# VI. Add duration in grade variables
def add_duration_var(data):
    log.info("Add duration in grade and duration in echelon variables")
    """ add variables linked to durations in rank and durations in echelon (from add_durations.py) """
    return main_duration(data)


# VII. Filter on duration variables
def select_non_left_censored(data):
    """ select careers of agents who are not left censored """
    return data.query('left_censored == False')


def main(corps = None, first_year = None):
    # use pipes to chain functions
    tracking = []
    data = read_data(corps = corps, first_year = first_year)
    tracking.append(['ATT once btw. 2011-2015', len(data.ident.unique()), 100, 100])
    data = replace_interns_cir(data)
    data = select_ATT_in_2011(data)
    tracking.append(['ATT in 2011, interns included', len(data.ident.unique())])
    data = select_next_state_in_fonction_publique(data)
    tracking.append(['Next grade state = activity in civil service', len(data.ident.unique())])
    data = select_generation(data)
    tracking.append(['Generation > 1960', len(data.ident.unique())])
    data = select_continuous_activity_state(data)
    tracking.append(['Continuous activity on I', len(data.ident.unique())])
    data = select_positive_ib(data)
    tracking.append(['IB > 0 on J', len(data.ident.unique())])
    data = select_non_missing_c_cir(data)
    tracking.append(['Non missing c_cir on K', len(data.ident.unique())])
    data = select_no_decrease_in_ATT_rank(data)
    tracking.append(['Non decreasing grades for ATT', len(data.ident.unique())])
    data = select_no_decrease_in_ib(data)
    tracking.append(['Non decreasing IB on L', len(data.ident.unique())])
    data = select_no_goings_and_comings_of_rank(data)
    tracking.append(['No goings and comings of grade', len(data.ident.unique())])
    data = add_grilles_variable(data, grilles = grilles, first_year = 2011, last_year = 2015)
    log.info("adding echelon variable")
    data = select_non_special_level(data)
    tracking.append(['No special echelon', len(data.ident.unique())])
    data = select_non_missing_level(data)
    tracking.append(['Non missing echelons on K', len(data.ident.unique())])

    # data = pd.read_csv(os.path.join(tmp_directory_path, 'filter', 'data_with_echelon.csv'))
    # print data.head()
    # log.info("saving data with echelon to tmp_directory_path\filter")
    # data.to_csv(os.path.join(tmp_directory_path, 'filter', 'data_with_echelon.csv'))

    # try:
    data15 = add_duration_var(data)
    # except Exception as e:
    #     print(e)
    #    return data
    data15.to_csv(os.path.join(tmp_directory_path, 'filter', 'data_with_duration_variables.csv'))
    log.info("Saving data with duration variables tmp_directory_path\filter")
    data16 = select_non_left_censored(data15)
    log.info("Select non left censored")
    tracking.append(['Non left censored', len(data16.ident.unique())])
    tracking.append(['I', '[max(an_aff, 2003), min(2015, last year in grade)]'])
    tracking.append(['J', '[max(an_aff, 2003), min(2015, first year in next grade)]'])
    tracking.append(['K', '[2011, min(2015, first year in next grade)]'])
    tracking.append(['L', '[max(an_aff, 2003), 2015]'])
    tracking = pd.DataFrame(tracking)
    print tracking.to_latex()
    data16.to_csv(
        os.path.join(output_directory_path, 'filter', "data_ATT_2011_filtered_after_duration_var_added.csv")
        )
    log.info(r"saving data to data_ATT_2011_filtered_after_duration_var_added.csv")
    return data16


if __name__ == "__main__":
    import sys
    logging.basicConfig(level = logging.DEBUG, stream = sys.stdout)
    data = main(first_year = 2000, corps = 'adjoints techniques territoriaux')

# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import os
import pandas as pd
from fonction_publique.base import grilles, output_directory_path, add_grilles_variable
from fonction_publique.data_generation.add_durations import main_duration


# Read data and replace cir codes for ATT interns
def read_data(data_path = os.path.join(output_directory_path, 'select_data'), filename = 'corpsAT_1995.csv'):
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
            'annee':int,
            'an_aff':int,
            'c_cir':str,
            'etat4':int,
            'generation':int,
            'ib1':int,
            'ib2':int,
            'ib3':int,
            'ib4':int,
            'ident':int,
            'libemploi':str,
            'sexe':str,
            'statut':str,
            }
        ).rename(columns = {"etat4":"etat", "ib4":"ib"}).reset_index()


def replace_interns_cir(data):
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
    ATT_cir = ['TTH1', 'TTH2', 'TTH3', 'TTH4']
    idents_keep = data.query('(annee == 2011) & (c_cir in @ATT_cir)').ident.unique()
    data = data.query('ident in @idents_keep').copy()
    assert set(data.query('annee == 2011').c_cir.unique()) == set(ATT_cir)
    return data


def select_next_state_in_fonction_publique(data):
    data = data.merge(
        data.query(
            'annee == 2011'
            ).copy()[['ident', 'c_cir']].rename(columns = {"c_cir":"c_cir_2011"}), on = 'ident', how = 'left'
        )
    data_after_2011 = data.query('(annee > 2011) & (c_cir != c_cir_2011)').copy()[['ident', 'annee']]
    data_after_2011['annee_exit'] = data_after_2011.groupby('ident')['annee'].transform(min)
    data_after_2011 = data_after_2011[['ident', 'annee_exit']].drop_duplicates()
    data = data.merge(data_after_2011, on = 'ident', how = 'left')
    data['annee_exit'] = data['annee_exit'].fillna(9999).astype(int)
    idents_keep = data.query('((annee == annee_exit) & (etat == 1)) | (annee_exit == 9999)').ident.unique()
    return data.query('ident in @idents_keep').copy()


def select_generation(data, generation = 1960):
    return data.query('generation > @generation').copy()


def select_continuous_activity_state(data):
    data['annee_min_to_consider'] = np.where(data['an_aff'] >= 2003, data['an_aff'], 2003)
    idents_del = data.query('(etat != 1) & (annee >= annee_min_to_consider) & (annee < annee_exit)').ident.unique()
    return data.query('ident not in @idents_del').copy()


# II. Data issues
def select_positive_ib(data): # compare with interval (entry in grade, exit)
    idents_del = data.query('(ib <= 0) & (annee >= annee_min_to_consider) & (annee <= annee_exit)').ident.unique()
    return data.query('ident not in @idents_del').copy()


def select_non_missing_c_cir(data):
    data_after_2011 = data.query('(annee > 2011) & (annee <= annee_exit)').copy()
    idents_del = data_after_2011[data_after_2011['c_cir'].isnull()].ident.unique()
    return data.query('ident not in @idents_del').copy()


def select_no_decrease_in_ATT_rank(data):
    ATT_cir = ['TTH1', 'TTH2', 'TTH3', 'TTH4']
    data_exit = data.query('annee >= annee_exit').copy()
    data_exit = data_exit.groupby('ident')['c_cir'].value_counts().rename(
        columns = {'c_cir':'c_cir_aft_exit'}
        ).reset_index()
    del data_exit[0]
    data_exit = data_exit.merge(data[['ident', 'c_cir_2011']], on = 'ident', how = 'inner').query(
        "c_cir_2011 != 'TTH1'"
        ).copy().drop_duplicates().query('c_cir in @ATT_cir').copy()
    data_exit = data_exit.query("c_cir_2011 != 'TTH1'")
    for col in ['c_cir', 'c_cir_2011']:
        data_exit[col] = data_exit[col].str[3:].astype(int)
    idents_del = data_exit.query('c_cir < c_cir_2011').copy().ident.unique()
    return data.query('ident not in @idents_del')


def select_no_decrease_in_ib(data):
    def non_decreasing(L):
        return all(x<=y for x, y in zip(L, L[1:]))
    data_entered = data.query('annee >= annee_min_to_consider').copy().sort_values('annee', ascending = True)
    data_entered = data_entered.groupby('ident')['ib'].apply(list).reset_index()
    data_entered['non_decreasing'] = data_entered['ib'].apply(non_decreasing)
    idents_del = data_entered.query('non_decreasing == False').copy().ident.unique()
    return data.query('ident not in @idents_del')


def select_no_goings_and_comings_of_rank(data):
    idents_del = data.query('(annee > annee_exit) & (c_cir == c_cir_2011)').copy().ident.unique()
    return data.query('ident not in @idents_del')


# IV. Sample selection based on echelon variable
def select_non_special_level(data):
    data['echelon'] = data['echelon'].astype(int)
    idents_del = data.query('echelon == -5').ident.unique()
    return data.query('ident not in @idents_del').copy()


# V. Filters on echelon variable issues
def select_non_missing_level(data):
    idents_del = data.query('(echelon == -1) & (annee <= annee_exit)').ident.unique()
    return data.query('ident not in @idents_del').copy()


# VI. Add duration in grade variables
def add_duration_var(data):
    return main_duration(data)


# VII. Filter on duration variables
def select_non_left_censored(data):
    return data.query('left_censored == False').copy()


def main():
    data = read_data()
    tracking = []
    tracking.append(['ATT once btw. 11-15', len(data.ident.unique())])
    data2 = replace_interns_cir(data)
    print "2"
    data3 = select_ATT_in_2011(data2)
    tracking.append(['ATT in 11, interns included', len(data3.ident.unique())])
    data4 = select_next_state_in_fonction_publique(data3)
    tracking.append(['Next state = activity in civil service', len(data4.ident.unique())])
    data5 = select_generation(data4)
    tracking.append(['Generation > 1960', len(data5.ident.unique())])
    print "5"
    data6 = select_continuous_activity_state(data5)
    tracking.append(['Continuous activity on I', len(data6.ident.unique())])
    data7 = select_positive_ib(data6)
    tracking.append(['IB > 0 on I', len(data7.ident.unique())])
    print "7"
    data8 = select_non_missing_c_cir(data7)
    tracking.append(['Non missing c_cir on I', len(data8.ident.unique())])
    data9 = select_no_decrease_in_ATT_rank(data8)
    tracking.append(['Non decreasing rank for ATT', len(data9.ident.unique())])
    data10 = select_no_decrease_in_ib(data9)
    tracking.append(['Non decreasing IB on I', len(data10.ident.unique())])
    data11 = select_no_goings_and_comings_of_rank(data10)
    tracking.append(['No goings and comings of rank', len(data11.ident.unique())])
    print "11"
    data12 = add_grilles_variable(data11, grilles = grilles, first_year = 2011, last_year = 2015)
    data13 = select_non_special_level(data12)
    tracking.append(['No special levels', len(data13.ident.unique())])
    data14 = select_non_missing_level(data13)
    tracking.append(['Non missing levels on I', len(data14.ident.unique())])
    print "14"
    data15 = add_duration_var(data14)
    data16 = select_non_left_censored(data15)
    tracking.append(['Non left censored', len(data16.ident.unique())])
    tracking.append(['Definition of I', 'max(an_aff, 2003), min(2015, first year of exit)'])
    tracking = pd.DataFrame(tracking)
    print tracking.to_latex()
    data16.to_csv(os.path.join('M:/CNRACL/filter', "data_ATT_2011_filtered_after_duration_var_added.csv"))
    return data16


if __name__ == "__main__":
    main()
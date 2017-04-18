from __future__ import division

import os
import pandas as pd
import numpy as np

careers_input_path = 'M:/CNRACL/output'
grilles_input_path = 'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/assets/'

# read grilles
grilles_AT = pd.read_csv(os.path.join(grilles_input_path, "grille_AT.csv"))

# read careers AT 2011-2015
careers_AT = pd.read_csv(os.path.join(careers_input_path,
                                      "corpsAT_2011.csv"))
test = careers_AT.head(25)

# reshape tofix
ib = pd.melt(test, id_vars = ['ident', 'annee'],
             value_vars = ['ib1', 'ib2', 'ib3', 'ib4'],
             value_name = 'ib',
             var_name = 'trimestre')
ib['trimestre'] = pd.to_numeric(ib['trimestre'].str.lstrip('ib'))
etat = pd.melt(test, id_vars = ['ident', 'annee'],
             value_vars = ['etat1', 'etat2', 'etat3', 'etat4'],
             value_name = 'etat',
             var_name = 'trimestre')
etat['trimestre'] = pd.to_numeric(etat['trimestre'].str.lstrip('etat'))
echelon = pd.melt(test, id_vars = ['ident', 'annee'],
             value_vars = ['echelon1', 'echelon2', 'echelon3', 'echelon4'],
             value_name = 'echelon',
             var_name = 'trimestre')
echelon['trimestre'] = pd.to_numeric(echelon['trimestre'].str.lstrip('echelon'))

df_test = pd.merge(ib, etat, on = ['ident', 'annee', 'trimestre'])
df_test = pd.merge(df_test, echelon, on = ['ident', 'annee', 'trimestre'])

test.drop(test.columns[[range(6,18)]], axis=1, inplace=True)
df2 = pd.merge(df_test, test, how = 'outer', on = ['ident', 'annee'])

# TO DO RESHAPE WIDE TO LONG
#pd.concat((pd.DataFrame({'ib':careers_AT.head().iloc[:,i+6], 
#                         'echelon':careers_AT.head().iloc[:,i+10],
#                         'etat':careers_AT.head().iloc[:,i+14]}) 
#             for i in range(4)))
#
#test = careers_AT.head()
#test["ident", "annee"] = test.index
#test_reshape = pd.lreshape(test, {'ib': ['ib1', 'ib2', 'ib3', 'ib4'],
#                                  'echelon': ['echelon1', 'echelon2', 'echelon3', 'echelon4'],
#                                  'etat':['etat1', 'etat2', 'etat3', 'etat4']})
#
#test2 = pd.wide_to_long(test, "etat", i="ident", j="trimestre")

# add trimestre annee à grille

grilles_AT['date_effet_grille'] = pd.to_datetime(grilles_AT.date_effet_grille)
grilles_AT.sort_values('date_effet_grille', inplace = True)
df2['date_observation'] = (np.array(df2.annee.astype(str),dtype='datetime64[Y]') 
              + np.array(df2.trimestre*3,dtype='timedelta64[M]')
              - np.timedelta64(1,'D'))
df2.sort_values('date_observation', inplace = True)

uniques_dates_obs = df2['date_observation'].unique()
uniques_dates_effet = grilles_AT['date_effet_grille'].unique()

match_dates_obs_et_effet = []
for date_obs in uniques_dates_obs:
    date_effet_grille_ant = uniques_dates_effet[uniques_dates_effet <= date_obs]
    date_effet_grille_actu = date_effet_grille_ant.max()
    match_dates_obs_et_effet.append(
            (date_obs, date_effet_grille_actu))
match_dates_obs_et_effet = pd.DataFrame(match_dates_obs_et_effet)
rename(ma)

df2.index = np.searchsorted(grilles_AT.date_effet_grille.values, df2.date_observation.values)
x = pd.merge(left=grilles_AT, right=df2, left_index=True, right_index=True, how='left')

#http://stackoverflow.com/questions/30627968/merge-pandas-dataframes-where-one-value-is-between-two-others
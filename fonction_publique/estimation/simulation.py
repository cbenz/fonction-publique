import pandas as pd
import numpy as np
from fonction_publique.base import grilles

grilles = grilles[grilles['code_grade_NETNEH'].isin(['TTM1', 'TTH1', 'TTH2', 'TTH3', 'TTH4'])]

# Input: corps, grade, échelon, ib, position prédite entre autre, grade suivant dans corps, grade suivant hors corps
agent_1 = [1, 2011, 'ATT', 'TTH1', 5, 201, 'exit_oth']
agent_2 = [2, 2011, 'ATT', 'TTH3', 1, 201, 'exit_next']
agent_3 = [3, 2011, 'ATT', 'TTH4', 2, 202, 'no_exit']
agent_4 = [4, 2011, 'ATT', 'TTH3', 1, 198, 'exit_next']
agent_5 = [5, 2011, 'ATT', 'TTH2', 3, 203, 'exit_next']
agents = [agent_1, agent_2, agent_3, agent_4, agent_5]


data = pd.DataFrame(agents, columns = ['ident', 'annee', 'corps', 'grade', 'echelon', 'ib', 'next_situation'])
data['next_grade'] = None


data_counterfactual_echelon_trajectory = pd.DataFrame() #to def

def predict_next_period_grade_when_exit_to_other_corps(data):
    data.loc[(data['next_situation'] == 'exit_oth'), 'next_grade'] = "TTM1"
    return data


def predict_next_period_echelon_when_no_exit_of_grade(data):
    data_no_exit = data.query("next_situation == 'no_exit'").copy()
    data_no_exit['next_grade'] = data_no_exit['grade']
    data_no_exit = data_no_exit.merge(
        data_counterfactual_echelon_trajectory, #
        on = ['ident', 'annee'],
        how = 'left'
        )
    data_no_exit = data_no_exit.merge( #
        grilles,
        on = ['grade', 'annee', 'echelon'],
        how = 'left'
        ).rename(columns = {'ib':'next_ib'})
    data_no_exit = data_no_exit[[data.columns, next_ib]]
    return data_no_exit


def predict_echelon_next_period_when_exit_of_grade(data, grilles):
    data_exit = data.query("next_situation != 'no_exit'").copy()
    data_exit.loc[(data_exit['next_situation'] == 'exit_next'), 'next_grade'] = [
        'TTH' + str(int(s[-1:]) + 1) for s in data_exit.query("next_situation == 'exit_next'")['grade'].copy()
        ]
    grilles_in_effect = grilles.query("date_effet_grille <= 2011").groupby(
        ['code_grade_NETNEH']
        ).agg({'date_effet_grille': np.max}).reset_index()
    grilles = grilles.merge(grilles_in_effect, on = ['code_grade_NETNEH', 'date_effet_grille'], how = 'inner')
    data_exit_merged = data_exit.merge(grilles, left_on = 'next_grade', right_on = 'code_grade_NETNEH', how = 'right')
    data_exit_merged = data_exit_merged.query('ib_y >= ib_x').groupby(
        ['ident']).agg({'ib_y': np.min}).reset_index()
    data_exit = data_exit.merge(data_exit_merged, on = ['ident'])
    data_exit = data_exit.merge(
        grilles[['code_grade_NETNEH', 'ib', 'echelon']].rename(columns = {'ib':'ib_next', 'echelon':'echelon_next'}),
        left_on = ['ib_y', 'next_grade'],
        right_on = ['ib_next', 'code_grade_NETNEH'],
        how = 'left')
    del data_exit['code_grade_NETNEH']
    del data_exit['ib_y']
    data_exit['echelon_next'] = data_exit['echelon_next'].astype(int)
    data_missing_echelon_next = data.query("next_situation != 'no_exit'")[~
        data.query("next_situation != 'no_exit'")['ident'].isin(
            data_exit.ident.unique().tolist()
            )
        ]
    data_missing_echelon_next['ib_next'] = 446
    data_missing_echelon_next['echelon_next'] = 11 #tofix
    assert (data_missing_echelon_next.grade.unique().tolist() == ['TTH4']) & (
            data_missing_echelon_next.next_grade.unique().tolist() == ['TTM1']
            )
    data_exit = data_exit.append(data_missing_echelon_next)
    return data_exit

data_with_next_grade_when_exit_oth = predict_next_period_grade_when_exit_to_other_corps(data)
data_with_next_echelon_when_exit_of_grade = predict_echelon_next_period_when_exit_of_grade(
    data_with_next_grade_when_exit_oth, grilles
    )

data.query("next_situation != 'no_exit'")[~
    data.query("next_situation != 'no_exit'")['ident'].isin(
        data_with_next_echelon_when_exit_of_grade.ident.unique().tolist()
        )
    ]

data = pd.read_csv('M:/CNRACL/simulation/data_simul_2011.csv')
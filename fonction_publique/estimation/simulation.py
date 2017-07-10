import pandas as pd
from fonction_publique.base import grilles


# Input: corps, grade, échelon, ib, position prédite entre autre, grade suivant dans corps, grade suivant hors corps
agent_1 = [1, 2011, 'ATT', 792, 1, 201, 'exit_oth']
agent_2 = [2, 2011, 'ATT', 793, 1, 201, 'exit_next']
agent_3 = [3, 2011, 'ATT', 792, 1, 201, 'no_exit']
agents = [agent_1, agent_2, agent_3]


data = pd.DataFrame(agents, columns = ['ident', 'annee', 'corps', 'grade', 'echelon', 'ib', 'next_situation'])
data['next_grade'] = None


data_counterfactual_echelon_trajectory = pd.DataFrame() #to def

def predict_next_period_grade_when_exit_to_other_corps(data):
    data_exit_oth = data.query("next_situation == 'exit_oth'").copy()
    data_exit_oth['next_grade'] = "TTM1"
    return data_exit_oth


def predict_next_period_echelon_when_no_exit(data):
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


def predict_echelon_next_period_when_exit(data):
    data_exit = data.query("next_situation != 'no_exit'").copy()
    data_exit.loc[data_exit['next_situation'] == 'exit_next', 'next_grade'] = data_exit['grade'][:-1] + str(
        int(data_exit['grade'][3:4]) + 1
        )
    data_exit['next_echelon'] = []
    data_exit['next_ib'] = []
    return data_exit




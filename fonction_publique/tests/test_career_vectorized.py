# -*- coding: utf-8 -*-

import datetime
import numpy as np
import pandas as pd

from openfisca_core import periods

from fonction_publique.career_simulation_vectorized import AgentFpt
from fonction_publique.career_simulation_vectorized import grille_adjoint_technique, compute_changing_echelons_by_grade
from fonction_publique import career_simulation_expected_results
from fonction_publique.career_simulation_expected_results import resultats_attendus as ra

#1. Case tests
agent0 = (0, datetime.date(2006, 12, 1), 793, 1)
# agent0 is a basic case: the periods associated with his echelons change once in 2014, in a non problematic manner.
# agent0 acceedes to echelon 5 in 2012-12 and is, according to the law of 2008-07, supposed to stay there for
# 24 to 36 months before acceeding echelon. However, the law changes in 2014 and fixes the periods associated with
# echelon 5 at 20 to 24 months. Hence, agent0 acceedes echelon 6 after 20 to 24 months, that is to say, if he has a fast
# career, he changes echelon to echelon 6 in 2014-08.
agent1 = (1, datetime.date(2018, 11, 1), 793, 5)
# agent1 accedes to echelon 5 in the future. Hence, by default, his evolution is given by the 2015-01-01 grid for grade
# 793, all along his grade.
agent2 = (2, datetime.date(2007, 11, 1), 500, 4)
# agent2's code grade does not exist. This raises an error. TODO
agent3 = (3, datetime.date(2011, 11, 1), 793, 6)
# agent3 is similar to agent1. agent4 gets to echelon 7 with no legislation change, in 2013-11. He is then supposed to
# spend 36 to 48 months in echelon 7. However, in 2014-02, the law shortens the duration in echelon 7 to 20 to 24
# months. Instead of acceeding echelon 8 on the 2016-11, as planned by the law before 2014-02, agent4 is at echelon 8
# in 2015-07 if he has a fast career.
agent4 = (4, datetime.date(2013, 6, 1), 796, 7)
# agent4 is supposed to stay in echelon 7 from 36 to 48 months at start before acceeding echelon 8, the top echelon
# of the grade. However, the law of 2014 extends the duration of echelon 7 to 40 to 48 month and creates a new echelon,
# echelon 9, in the grade.
agent5 = (5, datetime.date(2007, 11, 1), 793, 11)
# agent5 is stuck at the top of the grade. This case is currently handled in the function get_career_states_in_grade()
# only.
agent6 = (6, datetime.date(2012, 11, 1), 796, 1)
# agent6 is a problematic case. In 2012-11, agent6 is supposed to spend 18 to 24 month in echelon 1. However,
# in 2014-02, the law shortens the durations in echelon 1 to 12 months. At the date of the law change, agent7 has
# already spent more time than required by the new grid in echelon1. Hence, agent6 goes to echelon 2 at the date of the
# law change. His effective duration in echelon 1, if he has a fast career, is 15 months.
agent7 = (7, datetime.date(2026, 10, 1), 796, 8)
# agent7 is similar to agent2. agent7 has code_grade_NEG == 796 and acceedes to echelon 8 in the future.
# Hence, by default, his evolution is given by the 2015-01-01 grid all along.
agent8 = (8, datetime.date(2003, 11, 1), 796, 4)
# agent 8 acceedes to echelon 4 in 2003. However, we don't have information on the legislation back then.
# This raises an error is handled in _conditions_on_agent


# 2. Format case tests into a dataframe and an instance of AgentFpt
agent_tuples = [locals()['agent{}'.format(i)] for i in range(0, 9)]
df = pd.DataFrame(agent_tuples, columns = ['identif', 'period', 'grade', 'echelon'])
agents = AgentFpt(df)

def test():

    resultats_attendus = ra # defined in career_simulation_expected_results.py

    list_of_id = ['identif == {}'.format(x) for x in range(9)]
    queries = map(agents.dataframe.query, list_of_id)

    results_labels = [
        'date_debut_effet_result',
        'date_next_effet_result',
        'date_next_change_effet_result',
        'date_end_period_echelon_grille_in_effect_at_start_result',
        'echelon_period_for_grille_at_start_max_result',
        'echelon_period_for_grille_at_end_max_result',
        'echelon_duration',
        ]

    variables = [
        'date_debut_effet',
        'next_grille_date_effet',
        'next_change_of_legis_grille',
        'end_echelon_grille_in_effect_at_start',
        'echelon_period_for_grille_at_start',
        'echelon_duration_with_grille_in_effect_at_end',
        'echelon_duration_with_grille_in_effect',
        ]

    results = []

    for index in range(len(results_labels)):
        result = results_labels[index]
        variable = variables[index]
        result = [pd.Series(list(x[variable])).values.astype(str) for x in queries]
        result = [''.join(x) for x in result]
        if 'date' in results_labels[index]:
            result = [pd.to_datetime(str(x)[:10]) for x in result]
        else:
            result = result
        results.append(result)

    resultats_obtenus = []
    for index in range(9):
        resultat_obtenu = [item[index] for item in results]
        resultats_obtenus += resultat_obtenu

    resultats = pd.DataFrame(
        {'identif': [i for i in range(9) for _ in range(7)],
        'variable': variables * 9,
        'resultats_obtenus': resultats_obtenus,
        'resultats_attendus': resultats_attendus,
        'resultats_obtenus': resultats_obtenus,
        }
        )

    resultats['tests_results'] = np.array(resultats.resultats_attendus) == np.array(resultats.resultats_obtenus)

    results_errors = resultats.loc[resultats['tests_results'] == False].reset_index()

    def mess():
        messages = ''
        for row in range(len(results_errors)):
            message = 'La variable {} pour l\'identifiant {} vaut {} et devrait valoir {}'.format(
                results_errors['variable'][row],
                results_errors['identif'][row],
                results_errors['resultats_obtenus'][row],
                results_errors['resultats_attendus'][row],
                )
            messages += message + '\n'
        return messages

    assert np.equal(resultats.resultats_attendus, resultats.resultats_obtenus).all(), mess()


#if __name__ == '__main__':

agents.set_dates_effet(
    date_observation='period',
    start_variable_name = "date_debut_effet",
    next_variable_name = 'next_grille_date_effet'
    )
agents.compute_echelon_duree(
    date_effet_variable_name='date_debut_effet',
    duree_variable_name='echelon_period_for_grille_at_start'
    )
agents.compute_date_effet_legislation_change(
    start_date_effet_variable_name = 'date_debut_effet',
    date_effet_legislation_change_variable_name = 'next_change_of_legis_grille'
    )
agents.add_duree_echelon_to_date(
    new_date_variable_name = 'end_echelon_grille_in_effect_at_start',
    start_date_variable_name = 'period',
    duree_variable_name = 'echelon_period_for_grille_at_start')

agents.set_dates_effet(
    date_observation = 'end_echelon_grille_in_effect_at_start',
    start_variable_name = "date_debut_effet2",
    next_variable_name = None)

agents.compute_echelon_duree(
    date_effet_variable_name= 'date_debut_effet2',
    duree_variable_name='echelon_duration_with_grille_in_effect_at_end'
    )

agents.add_echelon_max(date_effet_grille = 'date_debut_effet', echelon_max_variable_name = 'echelon_max')
agents.compute_echelon_duration_with_grille_in_effect()

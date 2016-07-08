# -*- coding: utf-8 -*-

import datetime
import numpy as np
import pandas as pd

from openfisca_core import periods

from fonction_publique.career_simulation_vectorized import AgentFpt
from fonction_publique.career_simulation_vectorized import grille_adjoint_technique, compute_changing_echelons_by_grade

# TODO:
# - Start at zero

# Case tests
agent1 = (1, datetime.date(2006, 12, 1), 793, 1)
# agent1 is a basic case: the periods associated with his echelons change once in 2014, in a non problematic manner.
# agent1 acceedes to echelon 5 in 2012-12 and is, according to the law of 2008-07, supposed to stay there for
# 24 to 36 months before acceeding echelon. However, the law changes in 2014 and fixes the periods associated with
# echelon 5 at 20 to 24 months. Hence, agent1 acceedes echelon 6 after 20 to 24 months, that is to say, if he has a fast
# career, he changes echelon to echelon 6 in 2014-08.
agent2 = (2, datetime.date(2018, 11, 1), 793, 5)
# agent2 accedes to echelon 5 in the future. Hence, by default, his evolution is given by the 2015-01-01 grid for grade
# 793, all along his grade.
agent3 = (3, datetime.date(2007, 11, 1), 500, 4)
# agent3's code grade does not exist. This raises an error. TODO
agent4 = (4, datetime.date(2011, 11, 1), 793, 6)
# agent4 is similar to agent1. agent4 gets to echelon 7 with no legislation change, in 2013-11. He is then supposed to
# spend 36 to 48 months in echelon 7. However, in 2014-02, the law shortens the duration in echelon 7 to 20 to 24
# months. Instead of acceeding echelon 8 on the 2016-11, as planned by the law before 2014-02, agent4 is at echelon 8
# in 2015-07 if he has a fast career.
agent5 = (5, datetime.date(2013, 06, 1), 796, 7)
# agent5 is supposed to stay in echelon 7 from 36 to 48 months at start before acceeding echelon 8, the top echelon
# of the grade. However, the law of 2014 extends the duration of echelon 7 to 40 to 48 month and creates a new echelon,
# echelon 9, in the grade.
agent6 = (6, datetime.date(2007, 11, 1), 793, 11)
# agent6 is stuck at the top of the grade. This case is currently handled in the function get_career_states_in_grade()
# only.
agent7 = (7, datetime.date(2012, 11, 1), 796, 1)
# agent7 is a problematic case. In 2012-11, agent7 is supposed to spend 18 to 24 month in echelon 1. However,
# in 2014-02, the law shortens the durations in echelon 1 to 12 months. At the date of the law change, agent7 has
# already spent more time than required by the new grid in echelon1. Hence, agent7 goes to echelon 2 at the date of the
# law change. His effective duration in echelon 1, if he has a fast career, is 15 months.
agent8 = (8, datetime.date(2026, 10, 1), 796, 8)
# agent8 is similar to agent2. agent8 has code_grade_NEG == 796 and acceedes to echelon 8 in the future.
# Hence, by default, his evolution is given by the 2015-01-01 grid all along.
agent9 = (9, datetime.date(2003, 11, 1), 500, 1000)
# agent3's acceedes to echelon 4 in 2003. However, we don't have information on the legislation back then.
# This raises an error is handled in _conditions_on_agent

agent_tuples = [locals()['agent{}'.format(i)] for i in range(1, 10)]
df = pd.DataFrame(agent_tuples, columns = ['identif', 'period', 'grade', 'echelon'])
agents = AgentFpt(df)


def test_grid_date_effet_at_start():
    assert (agents.dataframe.query('identif == 1').date_debut_effet == datetime.datetime(2006, 11, 01)).all()
    assert (agents.dataframe.query('identif == 1').next_grille_date_effet == datetime.datetime(2008, 07, 01)).all()
    # TODO extend test
    # TODO write error message

def test_echelon_period_for_grille_at_start():
    assert (agents.dataframe.query('identif == 1').echelon_period_for_grille_at_start == 12).all()
    # TODO ask lisa for this one: print agent4._echelon_period_for_grille_at_start(True)


def test_next_change_of_legis_grille():
    agents.dataframe.query('identif == 1').next_change_of_legis_grille.isnull().all()
    assert agents.dataframe.query('identif == 1').next_change_of_legis_grille.isnull().all()
    assert (agents.dataframe.query('identif == 4').next_change_of_legis_grille == datetime.datetime(2014, 02, 01)).all()
    # TODO there is something with 5
    assert (agents.dataframe.query('identif == 7').next_change_of_legis_grille == datetime.datetime(2014, 02, 01)).all()


def test_end_period_echelon_grille_in_effect_at_start():
#    assert agent1._end_echelon_grille_in_effect_at_start(True) == periods.instant('2007-11-30'), \
#        "Got {} instead of {}".format(
#            agent1._end_echelon_grille_in_effect_at_start(True),
#            periods.instant('2007-11-30'))
    assert (agents.dataframe.query('identif == 1').end_echelon_grille_in_effect_at_start ==
        datetime.datetime(2007, 12, 01)).all()


def test_echelon_duration_with_grille_in_effect_at_end():
    assert (agents.dataframe.query('identif == 1').echelon_duration_with_grille_in_effect_at_end == 12).all()


def test_echelon_duration_with_grille_in_effect():
    assert agent1._echelon_duration_with_grille_in_effect(True) == 12
    assert agent7._echelon_duration_with_grille_in_effect(True) == 15
#    assert agent6.echelon_duration_with_grille_in_effect(True) == 40 CASE TO HANDLE


if __name__ == '__main__':

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
    agents.compose_date_duree_echelon(
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

    test_grid_date_effet_at_start()
    test_echelon_period_for_grille_at_start()
    test_next_change_of_legis_grille()
    test_end_period_echelon_grille_in_effect_at_start()
    test_echelon_duration_with_grille_in_effect_at_end()
    # agents._echelon_period_for_grille_at_start(True)

    agents.dataframe['condit_1'] = (
        agents.dataframe.next_change_of_legis_grille < agents.dataframe.end_echelon_grille_in_effect_at_start
        )
    agents.dataframe['condit_3'] = (
        agents.dataframe.period +
        agents.dataframe.echelon_duration_with_grille_in_effect_at_end.values.astype("timedelta64[M]")
        ) < (
        agents.dataframe.period +
        agents.dataframe.echelon_period_for_grille_at_start.values.astype("timedelta64[M]")
        )
    agents.dataframe['does_grille_change_during_period'] = (
        agents.dataframe.end_echelon_grille_in_effect_at_start >
        agents.dataframe.next_change_of_legis_grille
        ) & ~agents.dataframe.next_change_of_legis_grille.isnull()

    agents.dataframe['duree_a'] = (
        agents.dataframe.eval('does_grille_change_during_period & condit_1 & condit_3') *
        (
            agents.dataframe.next_change_of_legis_grille - agents.dataframe.period
            ).values.astype("timedelta64[M]") / np.timedelta64(1, 'M')
        )

    agents.dataframe['duree_b'] = (
        agents.dataframe.eval('does_grille_change_during_period & ~(condit_1 & condit_3)') *
        agents.dataframe.echelon_duration_with_grille_in_effect_at_end
        )

    agents.dataframe['duree_b'] = (
        agents.dataframe.eval('does_grille_change_during_period & ~(condit_1 & condit_3)') *
        agents.dataframe.echelon_duration_with_grille_in_effect_at_end
        )

    agents.dataframe['duree_c'] = (
            agents.dataframe.eval('~does_grille_change_during_period') *
            agents.dataframe.echelon_period_for_grille_at_start
            )

    print agents.dataframe

#    agents.dataframe.echelon_duration_with_grille_in_effect =

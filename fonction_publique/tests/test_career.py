# -*- coding: utf-8 -*-

from openfisca_core import periods

from fonction_publique.career_simulation import AgentFpt

# Case tests
agent1 = AgentFpt(1, '2006-12', 793, 1)
# agent1 is a basic case: the periods associated with his echelons change once in 2014, in a non problematic manner.
# agent1 acceedes to echelon 5 in 2012-12 and is, according to the law of 2008-07, supposed to stay there for
# 24 to 36 months before acceeding echelon. However, the law changes in 2014 and fixes the periods associated with
# echelon 5 at 20 to 24 months. Hence, agent1 acceedes echelon 6 after 20 to 24 months, that is to say, if he has a fast
# career, he changes echelon to echelon 6 in 2014-08.
agent2 = AgentFpt(2, '2018-11', 793, 5)
# agent2 accedes to echelon 5 in the future. Hence, by default, his evolution is given by the 2015-01-01 grid for grade
# 793, all along his grade.
agent3 = AgentFpt(3, '2007-11', 500, 4)
# agent3's code grade does not exist. This raises an error. TODO
agent4 = AgentFpt(4, '2011-11', 793, 6)
# agent4 is similar to agent1. agent4 gets to echelon 7 with no legislation change, in 2013-11. He is then supposed to
# spend 36 to 48 months in echelon 7. However, in 2014-02, the law shortens the duration in echelon 7 to 20 to 24
# months. Instead of acceeding echelon 8 on the 2016-11, as planned by the law before 2014-02, agent4 is at echelon 8
# in 2015-07 if he has a fast career.
agent5 = AgentFpt(5, '2013-06', 796, 7)
# agent5 is supposed to stay in echelon 7 from 36 to 48 months at start before acceeding echelon 8, the top echelon
# of the grade. However, the law of 2014 extends the duration of echelon 7 to 40 to 48 month and creates a new echelon,
# echelon 9, in the grade.
agent6 = AgentFpt(6, '2007-11', 793, 11)
# agent6 is stuck at the top of the grade. This case is currently handled in the function get_career_states_in_grade()
# only.
agent7 = AgentFpt(5, '2012-11', 796, 1)
# agent7 is a problematic case. In 2012-11, agent7 is supposed to spend 18 to 24 month in echelon 1. However,
# in 2014-02, the law shortens the durations in echelon 1 to 12 months. At the date of the law change, agent7 has
# already spent more time than required by the new grid in echelon1. Hence, agent7 goes to echelon 2 at the date of the
# law change. His effective duration in echelon 1, if he has a fast career, is 15 months.
agent8 = AgentFpt(5, '2026-10', 796, 8)
# agent8 is similar to agent2. agent8 has code_grade_NEG == 796 and acceedes to echelon 8 in the future.
# Hence, by default, his evolution is given by the 2015-01-01 grid all along.
agent9 = AgentFpt(3, '2003-11', 500, 1000)
# agent3's acceedes to echelon 4 in 2003. However, we don't have information on the legislation back then.
# This raises an error is handled in _conditions_on_agent

def test_grid_date_effet_at_start():
    assert agent1._grille_date_effet_at_start() == periods.instant('2006-11-01')  # TODO write error message


def test_next_grille_date_effet():
    assert agent1._next_grille_date_effet() == periods.instant('2008-07-01')  # TODO write error message


def test_echelon_period_for_grille_at_start():
    assert agent1._echelon_period_for_grille_at_start(True) == periods.period('month:2006-12:12')
    print agent4._echelon_period_for_grille_at_start(True)


def test_next_change_of_legis_grille():
    assert agent1._next_change_of_legis_grille(True) == periods.instant('2006-11-01')
    assert agent5._next_change_of_legis_grille(True) == periods.instant('2014-02-01')
    assert agent7._next_change_of_legis_grille(True) == periods.instant('2014-02-01')


def test_end_period_echelon_grille_in_effect_at_start():
    assert agent1._end_echelon_grille_in_effect_at_start(True) == periods.instant('2007-11-30'), \
        "Got {} instead of {}".format(
            agent1._end_echelon_grille_in_effect_at_start(True),
            periods.instant('2007-11-30'))


def test_echelon_duration_with_grille_in_effect_at_end():
    assert agent1._echelon_duration_with_grille_in_effect_at_end(True) == \
        periods.instant('2007-11-30').period('month', 12)


def test_echelon_duration_with_grille_in_effect():
    assert agent1._echelon_duration_with_grille_in_effect(True) == 12
    assert agent7._echelon_duration_with_grille_in_effect(True) == 15
#    assert agent6.echelon_duration_with_grille_in_effect(True) == 40 CASE TO HANDLE

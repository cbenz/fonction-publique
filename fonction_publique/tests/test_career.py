# -*- coding: utf-8 -*-

from openfisca_core import periods

from fonction_publique.career_simulation import AgentFpt


# Case tests
agent1 = AgentFpt(1, '2006-12', 793, 1)
agent2 = AgentFpt(2, '2018-11', 793, 5)
agent3 = AgentFpt(3, '2007-11', 500, 4)  # the grade does not exist
agent4 = AgentFpt(4, '2011-11', 793, 6)
agent5 = AgentFpt(5, '2013-06', 796, 7)  # changement de grille en cours d'échelon
agent6 = AgentFpt(6, '2007-11', 793, 11)
agent7 = AgentFpt(5, '2012-11', 796, 1)
agent8 = AgentFpt(5, '2026-10', 796, 8)


def test_grid_date_effet_at_start():
    assert agent1.grille_date_effet_at_start() == periods.instant('2006-11-01')  # TODO write error message


def test_next_grille_date_effet():
    assert agent1.next_grille_date_effet() == periods.instant('2008-07-01')  # TODO write error message


def test_echelon_period_for_grille_at_start():
    assert agent1.echelon_period_for_grille_at_start(True) == periods.period('month:2006-12:12')


def test_next_change_of_legis_grille():
    assert agent1.next_change_of_legis_grille(True) == periods.instant('2006-11-01')
    assert agent5.next_change_of_legis_grille(True) == periods.instant('2014-02-01')
    assert agent7.next_change_of_legis_grille(True) == periods.instant('2014-02-01')


def test_end_period_echelon_grille_in_effect_at_start():
    assert agent1.end_echelon_grille_in_effect_at_start(True) == periods.instant('2007-11-30'), \
        "Got {} instead of {}".format(
            agent1.end_echelon_grille_in_effect_at_start(True),
            periods.instant('2007-11-30'))

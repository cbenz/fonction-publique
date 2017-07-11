# -*- coding: utf-8 -*-

import datetime
import numpy as np
import os
import pandas as pd

from openfisca_core import periods

from fonction_publique.base import asset_path

from fonction_publique.career_simulation_vectorized import AgentFpt
from fonction_publique.career_simulation_vectorized import compute_changing_echelons_by_grade


grille_adjoint_technique_path = os.path.join(
    asset_path,
    'FPT_adjoint_technique.xlsx',
    )
grille_adjoint_technique = pd.read_excel(grille_adjoint_technique_path, encoding='utf-8')
grille_adjoint_technique = grille_adjoint_technique.rename(columns = dict(code_grade_NEG = 'code_grade'))


# 1. Case tests
agent0 = (0, datetime.datetime(2006, 12, 1), 793, 1)
# agent0 is a basic case: the periods associated with his echelons change once in 2014, in a non problematic manner.
# agent0 acceedes to echelon 5 in 2012-12 and is, according to the law of 2008-07, supposed to stay there for
# 24 to 36 months before acceeding echelon. However, the law changes in 2014 and fixes the periods associated with
# echelon 5 at 20 to 24 months. Hence, agent0 acceedes echelon 6 after 20 to 24 months, that is to say, if he has a fast
# career, he changes echelon to echelon 6 in 2014-08.
agent1 = (1, datetime.datetime(2018, 11, 1), 793, 5)
# agent1 accedes to echelon 5 in the future. Hence, by default, his evolution is given by the 2015-01-01 grid for grade
# 793, all along his grade.
agent2 = (2, datetime.datetime(2007, 11, 1), 500, 4)
# agent2's code grade does not exist. This raises an error. TODO
agent3 = (3, datetime.datetime(2011, 11, 1), 793, 6)
# agent3 is similar to agent1. agent4 gets to echelon 7 with no legislation change, in 2013-11. He is then supposed to
# spend 36 to 48 months in echelon 7. However, in 2014-02, the law shortens the duration in echelon 7 to 20 to 24
# months. Instead of acceeding echelon 8 on the 2016-11, as planned by the law before 2014-02, agent4 is at echelon 8
# in 2015-07 if he has a fast career.
agent4 = (4, datetime.datetime(2013, 6, 1), 796, 7)
# agent4 is supposed to stay in echelon 7 from 36 to 48 months at start before acceeding echelon 8, the top echelon
# of the grade. However, the law of 2014 extends the duration of echelon 7 to 40 to 48 month and creates a new echelon,
# echelon 9, in the grade.
agent5 = (5, datetime.datetime(2007, 11, 1), 793, 11)
# agent5 is stuck at the top of the grade. This case is currently handled in the function get_career_states_in_grade()
# only.
agent6 = (6, datetime.datetime(2012, 11, 1), 796, 1)
# agent6 is a problematic case. In 2012-11, agent6 is supposed to spend 18 to 24 month in echelon 1. However,
# in 2014-02, the law shortens the durations in echelon 1 to 12 months. At the date of the law change, agent7 has
# already spent more time than required by the new grid in echelon1. Hence, agent6 goes to echelon 2 at the date of the
# law change. His effective duration in echelon 1, if he has a fast career, is 15 months.
agent7 = (7, datetime.datetime(2026, 10, 1), 796, 8)
# agent7 is similar to agent2. agent7 has code_grade_NEG == 796 and acceedes to echelon 8 in the future.
# Hence, by default, his evolution is given by the 2015-01-01 grid all along.
agent8 = (8, datetime.datetime(2003, 11, 1), 796, 4)
# agent 8 acceedes to echelon 4 in 2003. However, we don't have information on the legislation back then.
# This raises an error is handled in _conditions_on_agent

agent_tuples = [locals()['agent{}'.format(i)] for i in range(0, 9)]
df = pd.DataFrame(agent_tuples, columns = ['ident', 'period', 'grade', 'echelon'])


date_effet_at_start_expect = [
    datetime.datetime(2006, 11, 1),
    datetime.datetime(2015, 01, 01),
    pd.NaT,
    datetime.datetime(2008, 07, 01),
    datetime.datetime(2012, 05, 01),
    datetime.datetime(2006, 11, 01),
    datetime.datetime(2012, 05, 01),
    datetime.datetime(2015, 01, 01),
    pd.NaT,
    ]

date_next_effet_expect = [
    datetime.datetime(2008, 7, 1),
    pd.NaT,
    pd.NaT,
    datetime.datetime(2014, 02, 01),
    datetime.datetime(2013, 07, 07),
    datetime.datetime(2008, 07, 01),
    datetime.datetime(2013, 07, 07),
    pd.NaT,
    pd.NaT,
    ]

date_next_change_effet_expect = [
    pd.Timestamp.max.floor('D'),
    pd.Timestamp.max.floor('D'),
    pd.Timestamp.max.floor('D'),
    datetime.datetime(2014, 02, 01),
    pd.Timestamp.max.floor('D'),
    pd.Timestamp.max.floor('D'),
    datetime.datetime(2014, 02, 01),
    pd.Timestamp.max.floor('D'),
    pd.Timestamp.max.floor('D'),
    ]

date_end_period_echelon_grille_in_effect_at_start_expect = [
    datetime.datetime(2007, 12, 01),
    datetime.datetime(2020, 11, 01),
    pd.NaT,
    datetime.datetime(2014, 11, 01),
    datetime.datetime(2017, 06, 01),
    pd.Timestamp.max.floor('D'),
    datetime.datetime(2014, 11, 01),
    datetime.datetime(2030, 10, 01),
    pd.NaT,
    ]

duree_echelon_grille_initiale_max_expect = [
    12.0,
    24.0,
    np.nan,  # should raise an errr
    36.0,
    48.0,
    np.inf,  # should be inf or a prob of transitin
    24.0,
    48.0,
    np.nan,
    ]

duration_echelon_grille_in_effect_at_end_expect = [
    12.0,
    24.0,
    np.nan,
    24.0,
    48.0,
    np.inf,
    12.0,
    48.0,
    np.nan,
    ]

duration_echelon_expect = [
    12.0,
    24.0,
    np.nan,
    27.0,
    48.0,
    np.inf,
    15.0,
    48.0,
    np.nan,
    ]

results_expect = [
    date_effet_at_start_expect,
    date_next_effet_expect,
    date_next_change_effet_expect,
    date_end_period_echelon_grille_in_effect_at_start_expect,
    duree_echelon_grille_initiale_max_expect,
    duration_echelon_grille_in_effect_at_end_expect,
    duration_echelon_expect,
    ]

results_expect_dataframe = pd.DataFrame.from_dict(dict(
    date_effet_grille_en_cours = date_effet_at_start_expect,
    next_grille_date_effet = date_next_effet_expect,
    date_prochaine_reforme_grille = date_next_change_effet_expect,
    date_fin_echelon_grille_initiale = date_end_period_echelon_grille_in_effect_at_start_expect,
    duree_echelon_grille_initiale = duree_echelon_grille_initiale_max_expect,
    echelon_duration_with_grille_in_effect_at_end = duration_echelon_grille_in_effect_at_end_expect,
    duree_effective_echelon = duration_echelon_expect,
    ))
results_expect_dataframe.index.name = 'ident'
results_expect_dataframe = pd.melt(
    results_expect_dataframe.reset_index(),
    id_vars = 'ident',
    value_vars = results_expect_dataframe.columns.tolist(),
    value_name = 'resultats_attendus',
    )


def mess(resultats):
    results_errors = resultats.loc[
        ~(
            np.equal(resultats.resultats_attendus, resultats.resultats_obtenus) |
            (
                resultats.resultats_obtenus.isnull() & resultats.resultats_attendus.isnull()
                )
            )
        ].reset_index()
    messages = ''
    for row in range(len(results_errors)):
        message = 'La variable {} pour l\'identifiant {} vaut {} et devrait valoir {}'.format(
            results_errors['variable'][row],
            results_errors['ident'][row],
            results_errors['resultats_obtenus'][row],
            results_errors['resultats_attendus'][row],
            )
        messages += message + '\n'
    return messages


def test():
    agents = AgentFpt(df)
    agents.set_grille(grille_adjoint_technique)
    value_vars = results_expect_dataframe.variable.unique().tolist()
    agents.compute_all()
    results_actual_dataframe = pd.melt(
        agents.dataframe,
        id_vars = 'ident',
        value_vars = value_vars,
        value_name = 'resultats_obtenus',
        )

    resultats = results_expect_dataframe.merge(
        results_actual_dataframe,
        )

    ignored_idents = [8]
    resultats = resultats[~resultats.ident.isin(ignored_idents)].copy()

    assert resultats.resultats_attendus.equals(resultats.resultats_obtenus), resultats[
        ~(resultats.resultats_attendus == resultats.resultats_obtenus) & ~(
            resultats.resultats_attendus.isnull() & resultats.resultats_obtenus.isnull()
            )
        ]


def test_result():
    agents = AgentFpt(df)
    agents.set_grille(grille_adjoint_technique)
    agents.compute_all()
    result = agents.fill()
    print result
    print agents.dataframe
    print result.loc[result.ident == 0]


def test_next():
    agents = AgentFpt(df)
    agents.set_grille(grille_adjoint_technique)
    print agents.compute_result()

agents = AgentFpt(df)
agents.set_grille(grille_adjoint_technique)
agents.compute_result(end_date = pd.Timestamp("2040-01-01").floor('D'))
print agents.result
#
#agents2 = AgentFpt(pd.DataFrame(agents.next()))
#agents2.set_grille(grille_adjoint_technique)
#agents2.compute_all()
# -*- coding:utf-8 -*-


from __future__ import division


from datetime import datetime, date
import numpy as np
import pandas as pd
from time import gmtime, strftime


from openfisca_core import periods
from fonction_publique.base import grille_adjoint_technique


dates_effet_grille = grille_adjoint_technique['date_effet_grille']


class AgentFpt:
    'common base class for all agent of French fonction publique'

    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.identif = dataframe.identif
        dataframe.period = pd.to_datetime(dataframe.period)
        self.period = dataframe.period
        self.grade = dataframe.grade
        self.echelon = dataframe.echelon
        self.agentfptCount = len(dataframe)
        self.result = pd.DataFrame()

    def compute_echelon_duration_with_grille_in_effect(self):
        dataframe = self.dataframe
        # TODO this bloc should be reworked
        date_effet_variable_name = 'date_debut_effet'
        echelon_max_variable_name = 'echelon_max_at_{}'.format(date_effet_variable_name)

        echelon_condition = (dataframe.echelon + 1) <= dataframe[echelon_max_variable_name]  # TODO echelon sera une str
        condit_1 = (
            dataframe.next_change_of_legis_grille < dataframe.end_echelon_grille_in_effect_at_start
            )
        condit_3 = (
            dataframe.period +
            dataframe.echelon_duration_with_grille_in_effect_at_end.values.astype("timedelta64[M]")
            ) < (
            dataframe.period +
            dataframe.echelon_period_for_grille_at_start.values.astype("timedelta64[M]")
            )
        grille_change_during_period = (
            dataframe.end_echelon_grille_in_effect_at_start >
            dataframe.next_change_of_legis_grille
            ) & ~dataframe.next_change_of_legis_grille.isnull()

        duree_a = (
            dataframe.next_change_of_legis_grille - dataframe.period
            ).values.astype("timedelta64[M]") / np.timedelta64(1, 'M')

        duree_b = dataframe.echelon_duration_with_grille_in_effect_at_end

        duree_c = dataframe.echelon_period_for_grille_at_start

        grades_from_dataframe = dataframe.grade.unique()  # TODO: use a cache for this
        grades_from_grilles = grille_adjoint_technique.code_grade_NEG.unique()
        valid_grades = set(grades_from_dataframe).intersection(set(grades_from_grilles))

        dataframe['echelon_duration_with_grille_in_effect'] = np.where(
            dataframe.grade.isin(valid_grades),
            np.where(
                echelon_condition,
                np.where(
                    grille_change_during_period,
                    np.where(
                        condit_1 & condit_3,
                        duree_a,
                        duree_b,
                        ),
                    duree_c,
                    ),
                np.inf,
                ),
            np.nan,
            )

    def set_dates_effet(self, date_observation = None, start_variable_name = "date_debut_effet",
            next_variable_name = None):

        assert date_observation is not None
        dataframe = self.dataframe

        grades_from_dataframe = dataframe.grade.unique()  # TODO: use a cache for this
        grades_from_grilles = grille_adjoint_technique.code_grade_NEG.unique()
        grades = set(grades_from_dataframe).intersection(set(grades_from_grilles))

        grade_filtered_grille = grille_adjoint_technique.loc[
            grille_adjoint_technique.code_grade_NEG.isin(grades)
            ]
        for grade in grades:
            max_dates_effet_grille = dataframe.loc[
                dataframe.grade == grade,
                'period'
                ].max()
            date_effet_filtered_grille = grade_filtered_grille.loc[
                (grade_filtered_grille.code_grade_NEG == grade) &
                (grade_filtered_grille.date_effet_grille <= max_dates_effet_grille)
                ]
            dates_effet_grille = np.sort(date_effet_filtered_grille.date_effet_grille.unique())

            previous_start_date = None
            # TODO use a grade extract out of the next loop
            for start_date in dates_effet_grille:
                dataframe.loc[
                    (dataframe.grade == grade) & (dataframe[date_observation] >= start_date),
                    start_variable_name,
                    ] = start_date

                if previous_start_date and next_variable_name is not None:
                    settled_grille = (
                        (dataframe.grade == grade) &
                        (dataframe.date_debut_effet >= previous_start_date) &
                        (dataframe.date_debut_effet < start_date)
                        )
                    dataframe.loc[
                        settled_grille,
                        next_variable_name,
                        ] = start_date

                previous_start_date = start_date

    def compute_echelon_duree(self, date_effet_variable_name = None, duree_variable_name = None, speed = True):
        # TODO may be a merge is faster
        assert date_effet_variable_name is not None
        echelon_max_variable_name = 'echelon_max_at_{}'.format(date_effet_variable_name)
        self.add_echelon_max(
            date_effet_grille = date_effet_variable_name,
            echelon_max_variable_name = echelon_max_variable_name,
            )
        dataframe = self.dataframe
        grades = dataframe.grade.unique()  # TODO: use a cache for this
        grade_filtered_grille = grille_adjoint_technique.loc[
            grille_adjoint_technique.code_grade_NEG.isin(grades)
            ]
        for grade in grades:
            clean_dates_effet_grille = dataframe.loc[
                dataframe.grade == grade,
                date_effet_variable_name
                ].dropna()

            max_dates_effet_grille = clean_dates_effet_grille.max()
            min_dates_effet_grille = clean_dates_effet_grille.min()

            date_effet_filtered_grille = grade_filtered_grille.loc[
                (grade_filtered_grille.date_effet_grille <= max_dates_effet_grille) &
                (grade_filtered_grille.date_effet_grille >= min_dates_effet_grille)
                ]
            dates_effet_grille = np.sort(
                dataframe.query('grade == @grade')[date_effet_variable_name].dropna().unique()
                )
            for date_effet_grille in dates_effet_grille:
                selected_entries = (
                    (dataframe.grade == grade) &
                    (dataframe[date_effet_variable_name] == date_effet_grille)
                    )
                echelons = dataframe.loc[selected_entries, 'echelon'].unique()
                for echelon in echelons:
                    duree = get_duree_echelon_from_grilles_dataframe(
                        echelon = echelon, grade = grade, date_effet = date_effet_grille,
                        grilles = date_effet_filtered_grille, speed = speed)
                    dataframe.loc[
                        selected_entries & (dataframe.echelon == echelon),
                        duree_variable_name,
                        ] = duree
                    dataframe.loc[
                        selected_entries & (dataframe.echelon == dataframe[echelon_max_variable_name]),
                        duree_variable_name,
                        ] = np.inf

    def compute_date_effet_legislation_change(self, start_date_effet_variable_name = None,
            date_effet_legislation_change_variable_name = None, speed = True):

        duree_str = get_duree_str_from_speed(speed)
        dataframe = self.dataframe

        if date_effet_legislation_change_variable_name is not None:
            self.dataframe[date_effet_legislation_change_variable_name] = pd.Timestamp.max.floor('D')

        grades = dataframe.grade.unique()  # TODO: use a cache for this
        grade_filtered_grille = grille_adjoint_technique.loc[
            grille_adjoint_technique.code_grade_NEG.isin(grades)
            ]
        changing_echelons_by_grade = compute_changing_echelons_by_grade(grade_filtered_grille)
        for grade, echelons in changing_echelons_by_grade.iteritems():
            clean_dates_effet_grille = dataframe.loc[
                dataframe.grade == grade,
                start_date_effet_variable_name
                ].dropna()

            min_dates_effet_grille = clean_dates_effet_grille.min()

            date_effet_filtered_grille = grade_filtered_grille.loc[
                (grade_filtered_grille.date_effet_grille >= min_dates_effet_grille)
                ]
            for echelon in echelons:  # Only changing echlons
                if not ((dataframe.echelon == echelon) & (dataframe.grade)).any():
                    continue  # We skip those not in the dataframe
                dates_effet_grille = dataframe.loc[
                    (dataframe.echelon == echelon) & (dataframe.grade == grade),
                    start_date_effet_variable_name
                    ]
                for date_effet_grille in dates_effet_grille:
                    duree = dataframe.loc[
                        (dataframe.echelon == echelon) &
                        (dataframe.grade == grade) &
                        (dataframe[start_date_effet_variable_name] == date_effet_grille),
                        'echelon_period_for_grille_at_start'
                        ].squeeze()

                    durees_by_date = date_effet_filtered_grille.loc[
                        (date_effet_filtered_grille.date_effet_grille >= date_effet_grille) &
                        (date_effet_filtered_grille.code_grade_NEG == grade) &
                        (date_effet_filtered_grille.echelon == echelon),
                        [
                            'date_effet_grille',
                            duree_str
                            ]
                        ].set_index('date_effet_grille', drop = True)

                    if [duree] != durees_by_date[duree_str].unique().tolist():
                        next_change_of_legis_grille = durees_by_date.loc[
                            durees_by_date[duree_str] != duree,
                            ].index.min()
                        dataframe.loc[
                            (dataframe.echelon == echelon) &
                            (dataframe.grade == grade) &
                            (dataframe[start_date_effet_variable_name] == date_effet_grille),
                            date_effet_legislation_change_variable_name,
                            ] = next_change_of_legis_grille

    def add_duree_echelon_to_date(self, new_date_variable_name = None, start_date_variable_name = None,
            duree_variable_name = None):
        dataframe = self.dataframe
        dataframe[new_date_variable_name] = (
            dataframe[start_date_variable_name].values.astype("datetime64[M]") +
            dataframe[duree_variable_name].values.astype("timedelta64[M]")
            )

        dataframe.loc[dataframe[duree_variable_name] == np.inf, new_date_variable_name] = pd.Timestamp.max.floor('D')

    def add_echelon_max(self, date_effet_grille, echelon_max_variable_name = None):
        assert echelon_max_variable_name is not None
        echelon_max_by_grille = compute_echelon_max(grilles = grille_adjoint_technique, start_date = None,
            echelon_max_variable_name = echelon_max_variable_name)
        dataframe = self.dataframe
        assert date_effet_grille != 'date_effet_grille'
        dataframe = dataframe.merge(
            echelon_max_by_grille,
            how = 'left',
            left_on = [date_effet_grille, 'grade'],
            right_on = ['date_effet_grille', 'code_grade_NEG'],
            copy = False
            )
        del dataframe['date_effet_grille']
        del dataframe['code_grade_NEG']
        self.dataframe = dataframe

    def compute_all(self):
        self.set_dates_effet(
            date_observation='period',
            start_variable_name = "date_debut_effet",
            next_variable_name = 'next_grille_date_effet'
            )

        self.compute_echelon_duree(
            date_effet_variable_name='date_debut_effet',
            duree_variable_name='echelon_period_for_grille_at_start'
            )
        self.compute_date_effet_legislation_change(
            start_date_effet_variable_name = 'date_debut_effet',
            date_effet_legislation_change_variable_name = 'next_change_of_legis_grille'
            )
        self.add_duree_echelon_to_date(
            new_date_variable_name = 'end_echelon_grille_in_effect_at_start',
            start_date_variable_name = 'period',
            duree_variable_name = 'echelon_period_for_grille_at_start')

        self.set_dates_effet(
            date_observation = 'end_echelon_grille_in_effect_at_start',
            start_variable_name = "date_debut_effet2",
            next_variable_name = None)

        self.compute_echelon_duree(
            date_effet_variable_name = 'date_debut_effet2',
            duree_variable_name = 'echelon_duration_with_grille_in_effect_at_end'
            )
        self.compute_echelon_duration_with_grille_in_effect()

        self.add_duree_echelon_to_date(
            new_date_variable_name = 'end_date_in_echelon',
            start_date_variable_name = 'period',
            duree_variable_name = 'echelon_duration_with_grille_in_effect')

    def complete(self):
        print self.dataframe
        dataframe = self.dataframe.loc[~self.dataframe.identif.isin([2, 8])].copy()
        # We select the quarter starting after the oldest date
        start_date = (
            dataframe.period.min() + pd.tseries.offsets.QuarterEnd() + pd.tseries.offsets.MonthBegin(n=1)
            ).floor('D')
        end_date = pd.Timestamp("2020-01-01").floor('D')
        quarters_range = pd.date_range(start = start_date, end = end_date, freq = 'Q')
        result = pd.DataFrame()
        for quarter_date in quarters_range:
            quarter_begin = quarter_date - pd.tseries.offsets.QuarterBegin(startingMonth = 1)
            quarter = quarter_date.quarter
            df = dataframe.loc[
                (dataframe.period <= quarter_begin) &
                (quarter_date <= (dataframe.end_date_in_echelon + pd.tseries.offsets.MonthEnd())),
                ['period', 'echelon', 'identif', 'grade']
                ]
            df['quarter'] = quarter_date
            result = pd.concat([result, df])
        self.result = pd.concat([self.result, result])
        return result

    def next(self):
        dataframe = self.dataframe
        next_dataframe = dataframe.loc[
            dataframe.end_date_in_echelon.notnull() & (dataframe.end_date_in_echelon < pd.Timestamp.max.floor('D')),
            ['identif', 'end_date_in_echelon', 'grade', 'echelon'],
            ].copy()
        next_dataframe.rename(columns = dict(end_date_in_echelon = 'period'), inplace = True)
        next_dataframe.echelon += 1
        return next_dataframe

    def compute_result(self):
        iteration = 0
        while not self.dataframe.empty:
            print 'iteration', iteration
            print self.dataframe
            print 'compute_all'
            self.compute_all()
            print 'complete'
            self.complete()
            print 'next'
            self.dataframe = self.next().copy()
            print self.result.sort_values(by = ['identif', 'quarter'])
            iteration += 1


def get_duree_echelon_from_grilles_dataframe(
        echelon = None, grade = None, date_effet = None, grilles = None, speed = True):
    duree_str = get_duree_str_from_speed(speed)
    expr = '(code_grade_NEG == @grade) & (echelon == @echelon) & (date_effet_grille == @date_effet)'
    duree = grilles.query(expr)[duree_str].copy()

    #    assert not duree.empty, u"Pas d'echelon {} valide dans le grade {} a la date {}".format(
    #        echelon, grade, date_effet)
    if duree.empty:
        print(
            u"Pas d'echelon {} valide dans le grade {} a la date {}. Using NaN".format(
                echelon, grade, date_effet)
            )
        return np.nan
    return duree.squeeze()


def compute_changing_echelons_by_grade(grilles = None, start_date = None, speed = True):
    duree_str = get_duree_str_from_speed(speed)
    if start_date is not None:
        grilles = grilles.query('date_effet_grille >= start_date')

    df = grilles.groupby(['code_grade_NEG', 'echelon'])[duree_str].nunique()  # unique() ?
    df = df.reset_index()
    df = df.loc[df['max_mois'] > 1][['code_grade_NEG', 'echelon']]
    echelons_by_grade = df.groupby('code_grade_NEG')['echelon'].unique().to_dict()
    return echelons_by_grade


def compute_echelon_max(grilles = None, start_date = None, echelon_max_variable_name = None):
    if start_date is not None:
        grilles = grilles.query('date_effet_grille >= start_date')

    df = grilles.groupby(['date_effet_grille', 'code_grade_NEG'])['echelon'].max()
    df.name = echelon_max_variable_name
    return df.reset_index()


def get_duree_str_from_speed(speed):
    if speed:
        duree_str = '{}_mois'.format('max')
    else:
        duree_str = '{}_mois'.format('min')
    return duree_str
# TODO construire la table
# grade echelon start_date new_date new_duree
# et faire des merge

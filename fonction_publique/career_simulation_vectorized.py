from __future__ import division


from datetime import datetime
import numpy as np
import os
import pandas as pd
import pkg_resources
from time import gmtime, strftime


from openfisca_core import periods


asset_path = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    )
grille_adjoint_technique_path = os.path.join(
    asset_path,
    'FPT_adjoint_technique.xlsx',
    )
grille_adjoint_technique = pd.read_excel(grille_adjoint_technique_path, encoding='utf-8')
dates_effet_grille = grille_adjoint_technique['date_effet_grille']


donnees_adjoints_techniques = os.path.join(
    asset_path,
    'donnees_indiv_adjoint_technique_test.xlsx',
    )
donnees_adjoints_techniques = pd.read_excel(donnees_adjoints_techniques)


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

    def _conditions_on_agent(self):
        if self.period < '2006-11':
            raise Exception('agent s period must be greater than 2006-11-01')
        elif self.grade not in [793, 794, 795, 796]:
            raise Exception('agent s grade is invalid')
        if self.echelon not in range(0, self._echelon_max()):
            raise Exception('agent s echelon is invalid')

    def _date_change_career_state(self, speed):
        period_to_offset = (self._echelon_duration_with_grille_in_effect(speed))
        date_change = periods.period('month', self.period).offset(period_to_offset)
        return date_change

    def display_agent(self):
        print "Identif : ", self.identif, "Period :", self.period, ", Grade :", self.grade, ", Echelon :", self.echelon

    def _does_grille_change_during_period(self, speed):
        period_at_start = self._echelon_period_for_grille_at_start(speed)
        period_at_end = self._echelon_duration_with_grille_in_effect_at_end(speed)
        return period_at_start != period_at_end

    def _duration_in_career_state(self, speed):
        period_to_offset = (self._echelon_duration_with_grille_in_effect(speed))
        duration_in_career_state = periods.period('month', self.period).offset(period_to_offset)
        duration_in_career_state = periods.period('month', self.period, period_to_offset)
        return duration_in_career_state

    def _echelon_duration_with_grille_in_effect(self, speed):
        echelon_max = self._echelon_max()
        next_echelon = self.echelon + 1
        diff = days_between(
            str(self.period), str(self._next_change_of_legis_grille(speed)))
        period_echelon_days = (self._echelon_period_for_grille_at_start(speed)).days
        if next_echelon <= echelon_max:
            if self._does_grille_change_during_period(speed):
                condit_1 = diff < period_echelon_days
                condit_2 = self._next_change_of_legis_grille(speed) > self._grille_date_effet_at_start()
                condit_3 = diff > self._echelon_duration_with_grille_in_effect_at_end(speed).days
                if condit_1 and condit_2 and condit_3:
                    echelon_period = diff
                    echelon_period = periods.instant(self.period).period('month', int(round(echelon_period / 30)))
                else:
                    echelon_period = self._echelon_duration_with_grille_in_effect_at_end(speed)
            else:
                echelon_period = self._echelon_period_for_grille_at_start(speed)
        else:
            echelon_period = periods.period(self.period)
        return echelon_period.size

    def _echelon_duration_with_grille_in_effect_at_end(self, speed):
        instant = self._end_echelon_grille_in_effect_at_start(speed)
        indiv_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['echelon'] == self.echelon) &
            (grille_adjoint_technique['date_effet_grille'] < str(instant))
            ]
        indiv_grille = indiv_grille[
            (grille_adjoint_technique['date_effet_grille'] == indiv_grille['date_effet_grille'].max())
            ]
        if speed:
            period_at_echelon = indiv_grille['min_mois'].squeeze()
        else:
            period_at_echelon = indiv_grille['max_mois'].squeeze()
        echelon_period_at_end = periods.period((u'month'), instant, int(period_at_echelon))

        return echelon_period_at_end

    def _echelon_max(self):
        period = periods.period(self.period)
        indiv_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['date_effet_grille'] < str(period.start))
            ]

        indiv_grille = indiv_grille[
            (grille_adjoint_technique['date_effet_grille'] == indiv_grille['date_effet_grille'].max())
            ]

        echelon_max = indiv_grille['echelon'].max()
        return echelon_max

    def _echelon_period_for_grille_at_start(self, speed):
        period = periods.period(self.period)
        indiv_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['echelon'] == self.echelon) &
            (grille_adjoint_technique['date_effet_grille'] < str(period.start))
            ]
        indiv_grille = indiv_grille[
            (grille_adjoint_technique['date_effet_grille'] == indiv_grille['date_effet_grille'].max())
        ]
        if speed:
            period_at_echelon = indiv_grille['min_mois'].squeeze()
        else:
            period_at_echelon = indiv_grille['max_mois'].squeeze()

        echelon_period_at_start = periods.period((u'month'), periods.instant(period), int(period_at_echelon))
        return echelon_period_at_start

    def _end_echelon_grille_in_effect_at_start(self, speed):
        return self._echelon_period_for_grille_at_start(speed).stop

    def get_career_states_in_grade(self, speed):
        self._conditions_on_agent()
        career_states = [self.period]
        period_to_offset = (self._echelon_duration_with_grille_in_effect(speed))
        durations_in_career_states = [periods.period(u'month', self.period, period_to_offset)]
        echelon = []
        grade = []
        identif = []
        if self.echelon == self._echelon_max():
            echelon.append(self.echelon)
            grade.append(self.grade)
            identif.append(self.identif)
            result = [identif, grade, echelon, career_states]
            result = pd.DataFrame(result).transpose()[:]
            return result
        else:
            while self.echelon < self._echelon_max():
                career_state = self._date_change_career_state(speed)
                career_state = periods.period(career_state)
                career_states.append(career_state)
                echelon.append(self.echelon)
                grade.append(self.grade)
                identif.append(self.identif)
                setattr(self, 'period', career_state)
                setattr(self, 'echelon', self.echelon + 1)
                if self.echelon < self._echelon_max():
                    duration_in_career_state = self._duration_in_career_state(speed)
                    durations_in_career_states.append(duration_in_career_state)
            if self.echelon == self._echelon_max():
                career_state = career_state
                duration_in_career_state = 0
                career_states.append(career_state)
                durations_in_career_states.append(duration_in_career_state)
                echelon.append(self.echelon)
                grade.append(self.grade)
                identif.append(self.identif)

        career_states_formatted = map(periods.instant, career_states)
        result = [identif, grade, echelon, career_states_formatted, durations_in_career_states]
        result = pd.DataFrame(result).transpose()[:-1]
        result.columns = ("id", "code_grade_NEG", "echelon", "date_du_changement", "duree_dans_etat")
        return result

    def _grille_date_effet_at_start(self):
        dataframe = self.dataframe
        grades = dataframe.grade.unique()  # TODO: use a cache for this
        grade_filtered_grille = grille_adjoint_technique.loc[
            grille_adjoint_technique.code_grade_NEG.isin(grades)
            ]
        for grade in grades:
            print '==========================='
            print 'grade: ', grade
            max_dates_effet_grille = dataframe.loc[
                dataframe.grade == grade,
                'period'
                ].max()
            date_effet_filtered_grille = grade_filtered_grille.loc[
                grade_filtered_grille.date_effet_grille <= max_dates_effet_grille
                ]
            dates_effet_grille = np.sort(date_effet_filtered_grille.date_effet_grille.unique())

            previous_start_date = None
            # TODO use a grade extract out of the next loop
            for start_date in dates_effet_grille:
                dataframe.loc[
                    (dataframe.grade == grade) & (dataframe.period >= start_date),
                    'date_debut_effet',
                    ] = start_date

                if previous_start_date:
                    settled_grille = (
                        (dataframe.grade == grade) &
                        (dataframe.date_debut_effet >= previous_start_date) &
                        (dataframe.date_debut_effet < start_date)
                        )
                    print 'number of settled_grille: ', settled_grille.sum()
                    print 'identif of setteld_grille: ', dataframe.loc[settled_grille, 'identif'].tolist()

                    dataframe.loc[
                        settled_grille,
                        'next_grille_date_effet',
                        ] = start_date

                    echelons = dataframe.loc[
                        settled_grille,
                        'echelon',
                        ].unique()
                    print 'echelons: ', echelons
                    for echelon in echelons:
                        print 'echelon: ', echelon
                        # TODO usa as parameter
                        speed = True
                        if speed:
                            speed_str = 'max'
                        else:
                            speed_str = 'min'

                        duree = date_effet_filtered_grille.loc[
                            (date_effet_filtered_grille.date_effet_grille == previous_start_date) &
                            (date_effet_filtered_grille.code_grade_NEG == grade) &
                            (date_effet_filtered_grille.echelon == echelon),
                            '{}_mois'.format(speed_str)
                            ]
                        print 'duree: ', duree.tolist()
                        assert not duree.empty
                        assert len(duree) == 1
                        duree = duree.squeeze()
                        dataframe.loc[
                            settled_grille & (dataframe.echelon == echelon),
                            'echelon_period_for_grille_at_start',
                            ] = duree

                        durees_by_date = date_effet_filtered_grille.loc[
                            (date_effet_filtered_grille.date_effet_grille >= start_date) &
                            (date_effet_filtered_grille.code_grade_NEG == grade) &
                            (date_effet_filtered_grille.echelon == echelon),
                            [
                                'date_effet_grille',
                                '{}_mois'.format(speed_str)
                                ]
                            ].set_index('date_effet_grille', drop = True)
                        print 'durees_by_date: ', durees_by_date
                        print durees_by_date['{}_mois'.format(speed_str)].unique().tolist()
                        if [duree] != durees_by_date['{}_mois'.format(speed_str)].unique().tolist():
                            next_change_of_legis_grille = durees_by_date.loc[
                                durees_by_date['{}_mois'.format(speed_str)] != duree,
                                ].index.min()
                            dataframe.loc[
                                settled_grille & (dataframe.echelon == echelon),
                                'next_change_of_legis_grille',
                                ] = next_change_of_legis_grille


                        print dataframe
                #

                previous_start_date = start_date



    def _next_change_of_legis_grille(self, speed):  # echelon level
        period = periods.period(self.period)
        grille_date_effet_at_start = self._grille_date_effet_at_start()
        echelon_period_at_start = self._echelon_period_for_grille_at_start(speed)
        next_change_of_legis_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['echelon'] == self.echelon) &
            (grille_adjoint_technique['date_effet_grille'] > str(period.start))
            ]
        if speed:
            condition_change_min_mois = (
                next_change_of_legis_grille['min_mois'] !=
                [echelon_period_at_start.size] * len(next_change_of_legis_grille['min_mois'])
                )
            next_change_of_legis_grille = next_change_of_legis_grille[condition_change_min_mois]
            condition_date_effet_min = (
                next_change_of_legis_grille['date_effet_grille'] ==
                next_change_of_legis_grille['date_effet_grille'].min()
                )
            next_change_of_legis_grille = next_change_of_legis_grille[condition_date_effet_min]
            if next_change_of_legis_grille.empty is True:
                next_change_of_legis_grille = grille_date_effet_at_start
            else:
                next_change_of_legis_grille = (
                    next_change_of_legis_grille['date_effet_grille'].map(lambda x: x.strftime('%Y-%m'))
                    )
                next_change_of_legis_grille = periods.period(next_change_of_legis_grille.unique()[0])
                next_change_of_legis_grille = next_change_of_legis_grille.start
        else:
            condition_change_max_mois = (
                next_change_of_legis_grille['max_mois'] !=
                [echelon_period_at_start.size] * len(next_change_of_legis_grille['max_mois'])
                )
            next_change_of_legis_grille = next_change_of_legis_grille[condition_change_max_mois]
            condition_date_effet_min = (
                next_change_of_legis_grille['date_effet_grille'] ==
                next_change_of_legis_grille['date_effet_grille'].min()
                )
            next_change_of_legis_grille = next_change_of_legis_grille[condition_date_effet_min]

            if next_change_of_legis_grille.empty is True:
                next_change_of_legis_grille = grille_date_effet_at_start
            else:
                next_change_of_legis_grille = next_change_of_legis_grille['date_effet_grille'].map(
                    lambda x: x.strftime('%Y-%m'))
                next_change_of_legis_grille = periods.period(next_change_of_legis_grille.unique()[0])
                next_change_of_legis_grille = next_change_of_legis_grille.start

        return next_change_of_legis_grille

    def _next_grille_date_effet(self):  # grade level
        grille_date_effet_at_start = self._grille_date_effet_at_start()
        next_grille_date_effet = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['date_effet_grille'] > str(grille_date_effet_at_start))
            ]
        next_grille_date_effet = next_grille_date_effet[
            (grille_adjoint_technique['date_effet_grille'] == next_grille_date_effet['date_effet_grille'].min())
            ]
        if next_grille_date_effet.shape == (0, 12):
            date_debut_effet = self._grille_date_effet_at_start()
        else:
            date_debut_effet = next_grille_date_effet['date_effet_grille'].map(lambda x: x.strftime('%Y-%m'))
            date_debut_effet = periods.period(date_debut_effet.unique()[0])
            date_debut_effet = date_debut_effet.start

        return date_debut_effet


def datefunc(x):
    datetime.strptime(x, '%Y-%m-%d')


def timestampToDate(timestamp, datePattern):
    return strftime("%b %d %Y %H:%M", gmtime(float(timestamp)))


def days_between(m1, m2):
    m1 = datetime.strptime(m1, "%Y-%m")
    m2 = datetime.strptime(m2, "%Y-%m-%d")
    return ((m2 - m1).days)

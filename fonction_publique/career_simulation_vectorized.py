# -*- coding:utf-8 -*-


from __future__ import division


import logging
import numpy as np
import pandas as pd


log = logging.getLogger(__name__)


class AgentFpt:
    'Common base class for all agent of French fonction publique'

    def __init__(self, dataframe, grille = None, end_date = None):

        assert set(dataframe.columns) >= set(['ident', 'period', 'grade', 'echelon', 'anciennete_dans_echelon']), \
            "The Agents dataframe lacks the following column(s): {}".format(
            set(['ident', 'period', 'grade', 'echelon', 'anciennete_dans_echelon']).difference(
                set(dataframe.columns)))
        for col in ['ident', 'grade', 'echelon']:
            assert  np.issubdtype(dataframe[col].dtype, np.integer)
        assert np.issubdtype(dataframe.period.dtype, np.datetime64), dataframe.period.dtype

        self.dataframe = dataframe
        self.ident = dataframe.ident
        self.period = dataframe.period
        self.grade = dataframe.grade
        self.echelon = dataframe.echelon

        self.agentfptCount = len(dataframe)
        self.result = pd.DataFrame()
        if grille is not None:
            self.set_grille(grille)
        if end_date is not None:
            self.set_end_date(end_date)

    def compute_duree_effective_dans_echelon(self):
        dataframe = self.dataframe
        # TODO this bloc should be reworked (variable names)
        date_effet_variable_name = 'date_effet_grille_en_cours'
        date_fin_echelon_grille_initiale = 'date_fin_echelon_grille_initiale'
        echelon_max_variable_name = 'echelon_max_at_{}'.format(date_effet_variable_name)
        duree_echelon_grille_finale = 'duree_echelon_selon_grille_en_cours_fin_periode_echelon_selon_grille_initiale'
        duree_echelon_grille_initiale = 'duree_echelon_grille_initiale'

        echelon_inferieur_a_echelon_terminal = (dataframe.echelon + 1) <= dataframe[echelon_max_variable_name]  # TODO echelon sera une str
        reforme_intervient_pendant_duree_donnee_par_grille_initiale = (
            dataframe.date_prochaine_reforme_grille < dataframe[date_fin_echelon_grille_initiale]
            )
        reforme_raccourcit_duree_donnee_par_grille_initiale = (
            dataframe.period +
            dataframe[duree_echelon_grille_finale].values.astype("timedelta64[M]")
            ) < (
            dataframe.period +
            dataframe[duree_echelon_grille_initiale].values.astype("timedelta64[M]")
            )
        grille_change_during_period = (
            dataframe[date_fin_echelon_grille_initiale] >
            dataframe.date_prochaine_reforme_grille
            ) & ~dataframe.date_prochaine_reforme_grille.isnull()

        duree_jusque_reforme_qui_raccourcit_duree_donnee_par_grille_initiale = (
            dataframe.date_prochaine_reforme_grille - dataframe.period
            ).values.astype("timedelta64[M]") / np.timedelta64(1, 'M')

        duree_donnee_par_grille_finale = dataframe[duree_echelon_grille_finale]

        duree_donnee_par_grille_initiale = dataframe[duree_echelon_grille_initiale]

        grades_from_dataframe = dataframe.grade.unique()  # TODO: use a cache for this
        grades_from_grilles = self.grille.code_grade_NEG.unique()
        valid_grades = set(grades_from_dataframe).intersection(set(grades_from_grilles))

        dataframe['duree_effective_echelon'] = np.where(
            dataframe.grade.isin(valid_grades),
            np.where(
                echelon_inferieur_a_echelon_terminal,
                np.where(
                    grille_change_during_period,
                    np.where(
                        reforme_intervient_pendant_duree_donnee_par_grille_initiale &
                        reforme_raccourcit_duree_donnee_par_grille_initiale &
                        (duree_donnee_par_grille_finale <= duree_jusque_reforme_qui_raccourcit_duree_donnee_par_grille_initiale),
                        duree_jusque_reforme_qui_raccourcit_duree_donnee_par_grille_initiale,
                        duree_donnee_par_grille_finale,
                        ),
                    duree_donnee_par_grille_initiale,
                    ),
                (self.end_date - dataframe.period).values.astype("timedelta64[M]") / np.timedelta64(1, 'M'),
                ),
            np.nan,
            )


    def set_dates_effet(self, date_observation = None, start_variable_name = "date_effet_grille_en_cours",
            next_variable_name = None):

        assert date_observation is not None
        dataframe = self.dataframe

        _set_dates_effet(dataframe, date_observation = date_observation, start_variable_name = start_variable_name,
            next_variable_name = next_variable_name, grille = self.grille)
        assert start_variable_name in dataframe.columns, \
            '{} is not present in the dataframe which contains: \n {}'.format(start_variable_name, dataframe)

    def get_echelon_duree(self, date_effet_variable_name = None, duree_variable_name = None, speed = True):
        # TODO may be a merge is faster
        assert date_effet_variable_name is not None
        echelon_max_variable_name = 'echelon_max_at_{}'.format(date_effet_variable_name)
        self.add_echelon_max(
            date_effet_grille = date_effet_variable_name,
            echelon_max_variable_name = echelon_max_variable_name,
            )
        dataframe = self.dataframe
        grades = dataframe.grade.unique()  # TODO: use a cache for this
        grade_filtered_grille = self.grille.loc[
            self.grille.code_grade_NEG.isin(grades)
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

    def get_date_prochaine_reforme_grille(self, start_date_effet_variable_name = None,
            date_effet_legislation_change_variable_name = None, speed = True):

        duree_str = get_duree_str_from_speed(speed)
        dataframe = self.dataframe

        if date_effet_legislation_change_variable_name is not None:
            # Initialize date_effet_legislation_change_variable_name to "infinity"
            self.dataframe[date_effet_legislation_change_variable_name] = pd.Timestamp.max.floor('D')

        grades = dataframe.grade.unique()  # TODO: use a cache for this
        grade_filtered_grille = self.grille.loc[
            self.grille.code_grade_NEG.isin(grades)
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
                if not ((dataframe.echelon == echelon) & (dataframe.grade == grade)).any():
                    continue  # We skip the echelons not present in the dataframe
                dates_effet_grille = dataframe.loc[
                    (dataframe.echelon == echelon) & (dataframe.grade == grade),
                    start_date_effet_variable_name
                    ]
                for date_effet_grille in dates_effet_grille:
                    duree = dataframe.loc[
                        (dataframe.echelon == echelon) &
                        (dataframe.grade == grade) &
                        (dataframe[start_date_effet_variable_name] == date_effet_grille),
                        'duree_echelon_grille_initiale'
                        ].unique()
                    if len(duree) == 0:
                        duree = [0]
                    assert len(duree) == 1
                    duree = duree[0]

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
                        try:
                            date_prochaine_reforme_grille = durees_by_date.loc[
                                durees_by_date[duree_str] != duree,
                                ].index.min()
                        except ValueError as error:
                            log.error(durees_by_date[duree_str])
                            log.error(duree)
                            raise(error)

                        dataframe.loc[
                            (dataframe.echelon == echelon) &
                            (dataframe.grade == grade) &
                            (dataframe[start_date_effet_variable_name] == date_effet_grille),
                            date_effet_legislation_change_variable_name,
                            ] = date_prochaine_reforme_grille

    def add_duree_echelon_to_date(self, new_date_variable_name = None, start_date_variable_name = None,
            duree_variable_name = None, offset = None):
        dataframe = self.dataframe
        if offset is not None:
            assert offset in self.dataframe
        dataframe[new_date_variable_name] = (
            dataframe[start_date_variable_name].values.astype("datetime64[M]") +
            dataframe[duree_variable_name].values.astype("timedelta64[M]")
            ) if offset is None else (
            dataframe[start_date_variable_name].values.astype("datetime64[M]") +
            dataframe[duree_variable_name].values.astype("timedelta64[M]")
            - dataframe[offset].values.astype("timedelta64[M]")  # TODO maybe a +/- 1 Month
            )

        dataframe.loc[dataframe[duree_variable_name] == np.inf, new_date_variable_name] = pd.Timestamp.max.floor('D')

    def add_echelon_max(self, date_effet_grille = None, echelon_max_variable_name = None):
        """
        Ajoute le rang de l'echelon le plus élevé à la nouvelle date d'effet de la grille date_effet_grille
        """
        assert date_effet_grille is not None and echelon_max_variable_name is not None
        echelon_max_by_grille = compute_echelon_max(grilles = self.grille, start_date = None,
            echelon_max_variable_name = echelon_max_variable_name)
        dataframe = self.dataframe
        assert date_effet_grille != 'date_effet_grille'
        assert date_effet_grille in dataframe, '{} is not present in dataframe which columns are {}'.format(
            date_effet_grille, dataframe.columns)

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
        # 1. Renseigne les dates de grille en cours et de la prochaine réforme de cette grille
        self.set_dates_effet(
            date_observation = 'period',
            start_variable_name = "date_effet_grille_en_cours",
            next_variable_name = 'date_prochaine_reforme_grille'
            )
        # 2. Renseigne la durée dans l'échelon selon la grille initialement en cours (grille initiale)
        self.get_echelon_duree(
            date_effet_variable_name = 'date_effet_grille_en_cours',
            duree_variable_name = 'duree_echelon_grille_initiale'
            )
        # 3. Renseigne la date de la prochaine réforme de la grille si elle intervient avant la fin de l'échelon
        # sinon elle vaut +infinity
        self.get_date_prochaine_reforme_grille(
            start_date_effet_variable_name = 'date_effet_grille_en_cours',
            date_effet_legislation_change_variable_name = 'date_prochaine_reforme_grille'
            )
        # 4. On calcue la date de fin de la période passée dans l'échelon dans la grille initiale
        self.add_duree_echelon_to_date(
            new_date_variable_name = 'date_fin_echelon_grille_initiale',
            start_date_variable_name = 'period',
            duree_variable_name = 'duree_echelon_grille_initiale',
            offset = 'anciennete_dans_echelon',
            )
        # 5. Renseigne la date d'effet de la grille en vigueur à la fin de la période passée dans l'échelon
        # selon la grille initiale
        self.set_dates_effet(
            date_observation = 'date_fin_echelon_grille_initiale',
            start_variable_name = "date_effet_grille_en_cours_fin_periode_echelon_selon_grille_initiale",
            next_variable_name = None,
            )
        # 6. Renseigne la durée dans l'échelon selon la grille en cours à la fin de la période de l'échelon
        # selon la grille initiale
        self.get_echelon_duree(
            date_effet_variable_name = 'date_effet_grille_en_cours_fin_periode_echelon_selon_grille_initiale',
            duree_variable_name = 'duree_echelon_selon_grille_en_cours_fin_periode_echelon_selon_grille_initiale'
            )
        # 7. Calcule duree effectie dans l'échelon
        self.compute_duree_effective_dans_echelon()
        # 8. Calcule la date finale dans l'échelon
        self.add_duree_echelon_to_date(
            new_date_variable_name = 'date_finale_dans_echelon',
            start_date_variable_name = 'period',
            duree_variable_name = 'duree_effective_echelon',
            offset = 'anciennete_dans_echelon',
            )

    def fill(self, date_observation = None):
        dataframe = self.dataframe

        if date_observation is None:
            date_observation = 'period'
            log.info('date_observation is none. Using period')

        assert self.end_date is not None
       # We select the quarter starting after the oldest date
        start_date = (
            dataframe[date_observation].min() + pd.tseries.offsets.QuarterEnd() + pd.tseries.offsets.MonthBegin(n=1)
            ).floor('D')

        quarters_range = pd.date_range(start = start_date, end = self.end_date, freq = 'Q')
        result = pd.DataFrame()
        for quarter_date in quarters_range:
            quarter_begin = quarter_date - pd.tseries.offsets.QuarterBegin(startingMonth = 1)
            df = dataframe.loc[
                (dataframe[date_observation] <= quarter_begin) &
                (quarter_date <= (dataframe.date_finale_dans_echelon + pd.tseries.offsets.MonthEnd())),
                [date_observation, 'echelon', 'ident', 'grade']
                ].copy()
            df['quarter'] = quarter_date

            result = pd.concat([result, df])

        self.result = pd.concat([self.result, result])
        return result

    def test_dataframe(self, iteration):
#        problematic_cols = [col for col in self.dataframe.columns if col.endswith('_y')]
#        print('iteration {}: {}'.format(iteration, problematic_cols))

        # print('iteration {}: {}'.format(iteration, self.dataframe))
        print('iteration {}'.format(iteration))
        pass

    def compute_result(self, test = False):
        iteration = 0

        while not self.dataframe.empty:
            self.test_dataframe(iteration)
            self.compute_all()
            self.test_dataframe(iteration)
            if test:
                self.dataframe = self.dataframe.loc[~self.dataframe.ident.isin([2, 8])].copy()  # TOOO remove this
                self.end_date = pd.Timestamp("2020-01-01").floor('D')

            self.fill()
            self.test_dataframe(iteration)
            self.dataframe = self.next().copy()
            self.test_dataframe(iteration)
            iteration += 1

#        df_echelon_terminal = dataframe.loc[
#                (dataframe[date_observation] <= quarter_begin) &
#                (quarter_date > (dataframe.date_finale_dans_echelon + pd.tseries.offsets.MonthEnd())),
#                [date_observation, 'echelon', 'ident', 'grade']
#                ].copy()
#            echelon_max = compute_echelon_max(
#                    grilles = self.grille, at_date = quarter_date, echelon_max_variable_name = 'echelon_max')
#            print echelon_max
#            df_echelon_terminal  = df_echelon_terminal.merge(
#                echelon_max[['code_grade_NEG', 'echelon_max']],
#                left_on = 'grade',
#                right_on = 'code_grade_NEG',
#                )
#            df_echelon_terminal = df_echelon_terminal.query('echelon == echelon_max').dropna().drop_duplicates().copy()
#            del df_echelon_terminal['echelon_max']
#            del df_echelon_terminal['code_grade_NEG']
#            df_echelon_terminal['quarter'] = quarter_date
#            #print df_echelon_terminal.sort_values(['ident', 'quarter'])
#            print df_echelon_terminal


    def next(self):
        '''Remove from dataframe all agents that have reached their ultimate echelon'''
        dataframe = self.dataframe
        next_dataframe = dataframe.loc[
            dataframe.date_finale_dans_echelon.notnull() & (
                dataframe.date_finale_dans_echelon < self.end_date
                ),
            ['ident', 'date_finale_dans_echelon', 'grade', 'echelon'],
            ].copy()
        next_dataframe.rename(columns = dict(date_finale_dans_echelon = 'period'), inplace = True)

        next_dataframe.echelon += 1  # TODO deal with str echelon
        next_dataframe['anciennete_dans_echelon'] = 0
        return next_dataframe

    def set_end_date(self, end_date):
        log.debug('Setting end_date to {}'.format(end_date))
        # assert np.issubdtype(end_date, np.datetime64), "end_date type is {} and should be datetime64".format(end_date.dtype)
        self.end_date = end_date

    def set_grille(self, grille = None):
        assert grille is not None
        assert 'code_grade_NEG' in grille
        assert 'date_effet_grille' in grille
        assert 'echelon' in grille
        assert 'max_mois' in grille
        assert 'min_mois' in grille
        for col in ['code_grade_NEG', 'echelon', 'max_mois', 'min_mois']:
            assert  np.issubdtype(grille[col].dtype, np.integer), "{} dtype is {} and should be integer".format(
                col, grille[col].dtype)
        assert np.issubdtype(grille.date_effet_grille.dtype, np.datetime64), \
                "date_effet_grille dtype is {} and should be datetime64".format(grille.period.dtype)

        self.grille = grille[['code_grade_NEG', 'date_effet_grille', 'echelon', 'max_mois', 'min_mois']].copy()


def get_duree_echelon_from_grilles_dataframe(
        echelon = None, grade = None, date_effet = None, grilles = None, speed = True):
    duree_str = get_duree_str_from_speed(speed)
    expr = '(code_grade_NEG == @grade) & (echelon == @echelon) & (date_effet_grille == @date_effet)'
    duree = grilles.query(expr)[duree_str].copy()

    #    assert not duree.empty, u"Pas d'echelon {} valide dans le grade {} a la date {}".format(
    #        echelon, grade, date_effet)
    if duree.empty:
        log.info(
            u"Pas d'echelon {} valide dans le grade {} dans la grille en effet à la date {}. Using NaN".format(
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
    df = df.loc[df[duree_str] > 1][['code_grade_NEG', 'echelon']]
    echelons_by_grade = df.groupby('code_grade_NEG')['echelon'].unique().to_dict()
    return echelons_by_grade


def compute_echelon_max(grilles = None, start_date = None, at_date = None, echelon_max_variable_name = None):

    if at_date is not None:
        assert start_date is None
        df = (grilles
            .query('date_effet_grille <= @at_date')
            .groupby(['code_grade_NEG', 'echelon']).agg({'date_effet_grille': np.max}).reset_index() # np.max
            )
    elif start_date is not None:
        grilles = grilles.query('date_effet_grille >= @start_date')

    df = grilles.groupby(['date_effet_grille', 'code_grade_NEG'])['echelon'].max()
    df.name = echelon_max_variable_name
    return df.reset_index()


def get_duree_str_from_speed(speed):
    if speed:
        duree_str = '{}_mois'.format('max')
    else:
        duree_str = '{}_mois'.format('min')
    return duree_str


def _set_dates_effet(dataframe, date_observation = None, start_variable_name = None,
        next_variable_name = None, grille = None):
    assert start_variable_name is not None
    if date_observation is None:
        date_observation = 'period'
        log.info('date_observation is None. using period')

    grades_from_dataframe = dataframe.grade.unique()  # TODO: use a cache for this
    assert 'code_grade_NEG' in grille.columns
    grades_from_grilles = grille.code_grade_NEG.unique()

    grades = set(grades_from_dataframe).intersection(set(grades_from_grilles))

    grade_filtered_grille = grille.loc[
        grille.code_grade_NEG.isin(grades)
        ]

    if not grades:
        log.info('No grades present')
    for grade in grades:
        max_dates_effet_grille = dataframe.loc[
            dataframe.grade == grade,
            date_observation
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

            if previous_start_date and next_variable_name is not None: # pervious_start_date set at None line 424
                settled_grille = (
                    (dataframe.grade == grade) &
                    (dataframe.date_effet_grille_en_cours >= previous_start_date) &
                    (dataframe.date_effet_grille_en_cours < start_date)
                    )
                dataframe.loc[
                    settled_grille,
                    next_variable_name,
                    ] = start_date
            previous_start_date = start_date

    # All dates_effet_grille are empty is cannot be present in the dataframe
    if start_variable_name not in dataframe.columns:
        dataframe[start_variable_name] = pd.Timestamp.max.floor('D')

# TODO construire la table
# grade echelon start_date new_date new_duree
# et faire des merge

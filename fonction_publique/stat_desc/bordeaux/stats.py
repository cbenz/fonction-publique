# -*- coding:utf-8 -*-


import os

import pkg_resources

from fonction_publique.bordeaux.utils import (
    build_destinations_by_grade,
    build_transitions_pct_by_echantillon,
    build_transitions_pct_by_grade_initial,
    build_destinations_dataframes,
    get_careers,
    clean_empty_netneh,
    get_destinations_dataframe
    )

results_path = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'bordeaux',
    'results',
    )


def build_transitions():
    for decennie in [1970]:  # 1950
        transitions_pct_by_echantillon = build_transitions_pct_by_echantillon(decennie = decennie)
        transitions_pct_by_grade_initial = build_transitions_pct_by_grade_initial(decennie = decennie)

        transitions_pct_by_echantillon.to_csv(os.path.join(results_path, 'transitions_distribution.csv'))
        transitions_pct_by_grade_initial.to_csv(os.path.join(results_path, 'transitions_distribution_grade_initial.csv'))


def build_destinations():
    for decennie in [1970]:  # 1950
        destinations_by_grade = build_destinations_by_grade(decennie)
        destinations_by_grade.to_csv(os.path.join(results_path, 'destinations.csv'))


def build_destinations_tables():
    decennie = 1970
    destinations, purged_destinations = build_destinations_dataframes(decennie)

    destinations.to_latex(
        os.path.join(
            pkg_resources.get_distribution('fonction_publique').location,
            'fonction_publique',
            'note',
            'Section2',
            'destination.tex',
            ),
        formatters = {
            'part': '{:,d} %'.format,
            },
        index = False,
        )

    purged_destinations.to_latex(
        os.path.join(
            pkg_resources.get_distribution('fonction_publique').location,
            'fonction_publique',
            'note',
            'Section2',
            'purged_destination.tex',
            ),
        formatters = {
            'part': '{:,d} %'.format,
            },
        index = False,
        )

    decennie = 1970
    carrieres = get_careers(variable = 'c_netneh', decennie = decennie).sort_values(['ident', 'annee'])
    carrieres = clean_empty_netneh(carrieres.query('annee > 2010'))

    get_destinations_dataframe(carrieres=carrieres, initial_grades = ['TAJ2', 'TTH2']).to_latex(
        os.path.join(
            pkg_resources.get_distribution('fonction_publique').location,
            'fonction_publique',
            'note',
            'Section2',
            'purged_second_destination.tex',
            ),
        formatters = {
            'part': '{:,d} %'.format,
            },
        index = False,
        )


if __name__ == '__main__':
    # build_destinations()
    # build_transitions()
    build_destinations_tables()
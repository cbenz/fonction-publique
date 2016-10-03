# -*- coding:utf-8 -*-


import os

import pkg_resources

from fonction_publique.bordeaux.utils import (
    build_destinations_by_grade,
    build_transitions_pct_by_echantillon,
    build_transitions_pct_by_grade_initial,
    build_destinations_dataframes
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
    print destinations

    destinations.to_latex(
        os.path.join(
            pkg_resources.get_distribution('fonction_publique').location,
            'fonction_publique',
            'note',
            'Section2',
            'destination.tex',
            ),
        formatters = {
            'part': '{:,.2f} %'.format,
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
            'part': '{:,.2f} %'.format,
            },
        index = False,
        )

if __name__ == '__main__':
    # build_destinations()
    # build_transitions()
    build_destinations_tables()
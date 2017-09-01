# -*- coding: utf-8 -*-


def fix_anciennete_dans_echelon(data, default_value = None):
    """
    Fix anciennete_dans_echelon
    FIXME: UNFINISHED
    """
    assert default_value in ['min_mois', 'max_mois']
    data.loc[
        (data['annee'] == 2011) & (data['min_mois'] != -1) & (data['anciennete_echelon'] >= data[default_value]),
        'anciennete_echelon'
        ] = data[default_value]
    return data


def main():
    NotImplementedError

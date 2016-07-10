# -*- coding:utf-8 -*-


from __future__ import division


import os
import pandas as pd
import pkg_resources

asset_path = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )
grille_adjoint_technique_path = os.path.join(
    asset_path,
    'FPT_adjoint_technique.xlsx',
    )
grille_adjoint_technique = pd.read_excel(grille_adjoint_technique_path, encoding='utf-8')

donnees_adjoints_techniques = os.path.join(
    asset_path,
    'donnees_indiv_adjoint_technique_test.xlsx',
    )
donnees_adjoints_techniques = pd.read_excel(donnees_adjoints_techniques)

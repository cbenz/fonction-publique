# -*- coding: utf-8 -*-
import pandas as pd
import os
from fonction_publique.base import grilles

data = pd.read_csv(
    os.path.join('M:/CNRACL/filter', 'data_ATT_2011_filtered.csv'),
    index_col = 0,
    )
data_carrieres_with_indicat_grade_chg = []  # Redefined at the end of the loop
annees = list(reversed(range(2003, 2012)))
data_a_utiliser_pour_annee_precedente = None
#for annee in annees:
annee = 2011
if annee == 2011:
    data_annee = add_grilles_variable
    data_annee = merge_careers_with_grilles(data_a_utiliser_pour_annee_precedente, grilles, annee)
#
data_annee = clean_careers_annee_annee_bef(
    data_annee,
    data_carrieres,
    annee,
    'adjoints techniques territoriaux',
    )
cas_uniques_annee_et_annee_bef = get_career_transitions_uniques_annee_annee_bef(data_annee, annee)
cas_uniques_with_indic_grade_change = get_indicatrice_chgmt_grade_annee_annee_bef(
    cas_uniques_annee_et_annee_bef,
    True,
    annee,
    grilles,
    table_corresp_grade_corps
    )
c_cir_bef_predits = (cas_uniques_with_indic_grade_change.query(
    '(indicat_ch_grade == True) & (ambiguite == False)').c_cir_bef_predit
    .value_counts(dropna = False)
    .index.tolist()
    )
print c_cir_bef_predits
assert 'TTH1' in c_cir_bef_predits






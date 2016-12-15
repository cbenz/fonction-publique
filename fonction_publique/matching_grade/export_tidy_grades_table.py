# -*- coding: utf-8 -*-

from __future__ import division

import os
import pandas as pd

from fonction_publique.matching_grade.grade_matching import (
    get_correspondance_data_frame,
    )
from fonction_publique.merge_careers_and_legislation import get_grilles

from fonction_publique.base import parser

libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')
output_directory = parser.get('data', 'output')

from fonction_publique.matching_grade.merge_correspondance import validate_correspondance_table



def main():

    correspondance_data_frame = get_correspondance_data_frame(which = 'grade')
    cleaned_correspondance_data_frame = validate_correspondance_table(correspondance_data_frame)
    cleaned_correspondance_data_frame = cleaned_correspondance_data_frame.drop('date_effet', axis = 1)

    grilles = get_grilles()

    correspondance_libemploi_slug_h5 = os.path.join(libelles_emploi_directory, 'correspondance_libemploi_slug.h5')
    correspondance_libemploi_slug = pd.read_hdf(correspondance_libemploi_slug_h5, 'correspondance_libemploi_slug')

    versants = set(['FONCTION PUBLIQUE HOSPITALIERE', 'FONCTION PUBLIQUE TERRITORIALE'])
    assert set(grilles.libelle_FP.value_counts(dropna = False).index.tolist()) == versants

    grilles['versant'] = 'T'
    grilles.loc[grilles.libelle_FP == "FONCTION PUBLIQUE HOSPITALIERE", 'versant'] = 'H'

    # Step 1 : merge correspondance table with grille to recover the code_grade
    merge_correspondance_grilles = (cleaned_correspondance_data_frame
        .merge(
            grilles[['versant', 'libelle_grade_NEG', 'code_grade']].drop_duplicates(),
            how = 'left',
            left_on = ['versant', 'grade'],
            right_on = ['versant', 'libelle_grade_NEG'],
            )
        .drop('grade', axis = 1)
        )

    # Step 2 : merge correspondance table with non slugified libemploi to get the full correspondance
    final_merge = (correspondance_libemploi_slug
        .merge(
            merge_correspondance_grilles,
            how = 'inner',
            left_on = ['versant', 'annee', 'libemploi_slugified'],
            right_on = ['versant', 'annee', 'libelle'],
            )
        .drop('libelle', axis = 1)
        )

    # Step 3 : Save to csv
    save_path = os.path.join(output_directory, 'correspondance_libemploi_grade.csv')
    final_merge.to_csv(save_path, sep = ';', encoding = 'utf-8')
    print("The table of correspondance between libelles and grade is saved at {}".format(save_path))

main()

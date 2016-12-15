# -*- coding: utf-8 -*-

from __future__ import division

from fonction_publique.matching_grade.extract_libelles import (
    load_libelles,
    )
from fonction_publique.matching_grade.grade_matching import (
    get_correspondance_data_frame,
    )
from fonction_publique.merge_careers_and_legislation import get_grilles

from fonction_publique.base import parser
from slugify import slugify

libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')

from fonction_publique.matching_grade.merge_correspondance import validate_correspondance_table

def main():

    correspondance_libemploi_slug_h5 = os.path.join(libelles_emploi_directory, 'correspondance_libemploi_slug.h5')
    correspondance_libemploi_slug = pd.read_hdf(correspondance_libemploi_slug_h5, 'correspondance_libemploi_slug')

    correspondance_data_frame = get_correspondance_data_frame(which = 'grade').drop('date_effet', axis = 1)
    grilles = get_grilles()

    versants = set(['FONCTION PUBLIQUE HOSPITALIERE', 'FONCTION PUBLIQUE TERRITORIALE'])
    assert set(grilles.libelle_FP.value_counts(dropna = False).index.tolist()) == versants

    grilles['versant'] = 'T'
    grilles.loc[grilles.libelle_FP == "FONCTION PUBLIQUE HOSPITALIERE", 'versant'] = 'H'

    # Step 1 : merge correspondance table with grille to recover the code_grade
    merge_correspondance_grilles = (correspondance_data_frame
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

    return final_merge


# -*- coding: utf-8 -*-

from __future__ import division

import logging
import os
import pandas as pd
import numpy as np
import sys


from fonction_publique.matching_grade.grade_matching import get_correspondance_data_frame
from fonction_publique.merge_careers_and_legislation import get_grilles
from fonction_publique.base import parser
from fonction_publique.matching_grade.grade_matching import validate_correspondance


log = logging.getLogger(__name__)


libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')
output_directory = parser.get('data', 'output')


def main():
    correspondance_data_frame = get_correspondance_data_frame(which = 'grade')
    valid_data_frame = validate_correspondance(correspondance_data_frame, check_only = True)
    assert valid_data_frame, 'The correspondace data frame is not valid'

    grilles = get_grilles()
    grilles.loc[
    grilles.libelle_grade_NEG == 'INFIRMIER DE CLASSE NORMALE (*)', 'libelle_grade_NEG'
    ] = 'INFIRMIER DE CLASSE NORMALE(*)'
    grilles.loc[
    grilles.libelle_grade_NEG == 'INFIRMIER DE CLASSE SUPERIEURE (*)', 'libelle_grade_NEG'
    ] = 'INFIRMIER DE CLASSE SUPERIEURE(*)'

    correspondance_libemploi_slug_h5 = os.path.join(libelles_emploi_directory, 'correspondance_libemploi_slug.h5')
    correspondance_libemploi_slug = pd.read_hdf(correspondance_libemploi_slug_h5, 'correspondance_libemploi_slug')

    versants = set(['FONCTION PUBLIQUE HOSPITALIERE', 'FONCTION PUBLIQUE TERRITORIALE'])
    assert set(grilles.libelle_FP.value_counts(dropna = False).index.tolist()) == versants

    grilles['versant'] = 'T'
    grilles.loc[grilles.libelle_FP == "FONCTION PUBLIQUE HOSPITALIERE", 'versant'] = 'H'

    # 1. Merge correspondance data frame with grille to recover the code_grade
    merge_correspondance_grilles = (correspondance_data_frame
        .merge(
            grilles[['versant', 'libelle_grade_NEG', 'code_grade']].drop_duplicates(),
            how = 'left',
            left_on = ['versant', 'grade'],
            right_on = ['versant', 'libelle_grade_NEG'],
            )
        .drop('grade', axis = 1)
        )

    # 2. Merge correspondance data frame with libelle saisi (libemploi) to get the full correspondance
    final_merge = (correspondance_libemploi_slug
        .merge(
            merge_correspondance_grilles,
            how = 'inner',
            left_on = ['versant', 'annee', 'libemploi_slugified'],
            right_on = ['versant', 'annee', 'libelle'],
            )
        .drop('libelle', axis = 1)
        )

    # 3. Expand to add years*libelle lines from the date d'effet
    final_merge["beg"] =  pd.to_datetime(final_merge.date_effet).dt.year.astype(str)
    final_merge["end"] =  final_merge.annee.astype(str)
    expended_data = pd.DataFrame(columns = final_merge.columns)

    for row_nb in range(0, len(final_merge)):
        row = final_merge[row_nb:(row_nb + 1)]
        row.index = pd.DatetimeIndex(pd.to_datetime(row.beg))
        end = row.end.values[0]
        beg = row.beg.values[0]
        idx = pd.date_range(beg, end, freq = 'AS') # Date au 31 décembre: hyp implicite que la date d'effet est au 1er janvier
        exp_row= row.reindex(idx, method = 'ffill')
        expended_data = expended_data.append(exp_row)

    expended_data['annee'] = pd.to_datetime(expended_data.index)
    expended_data['annee'] = expended_data['annee'].dt.year
    expended_data.drop(["beg","end","libemploi_slugified"], inplace = True, axis = 1)
    expended_data = expended_data.reset_index(drop = True)

    # 4. Save to csv
    save_path = os.path.join(output_directory, 'correspondance_libemploi_grade.csv')
    expended_data.to_csv(save_path, sep = ';', encoding = 'latin1')
    log.info("The table of correspondance between libelles and grade is saved at {}".format(save_path))
    assert len(set(expended_data.libelle_grade_NEG))== len(set(correspondance_data_frame.grade))
    log.info("{} libellés différents assignés à {} grades".format(len(set(expended_data.libemploi)),len(set(expended_data.libelle_grade_NEG))))
    return expended_data


if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    final_merge = main()





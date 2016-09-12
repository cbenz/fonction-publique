# -*- coding: utf-8 -*-


import pandas as pd

from fonction_publique.base import law_hdf_path
from fonction_publique.career_simulation_vectorized import compute_echelon_max


law_store = pd.HDFStore(law_hdf_path)
grilles = law_store.select('grilles')

print compute_echelon_max(grilles = grilles, start_date = None)

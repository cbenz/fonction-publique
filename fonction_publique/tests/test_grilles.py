# -*- coding: utf-8 -*-

from fonction_publique.base import grille_adjoint_technique
from fonction_publique.career_simulation_vectorized import compute_echelon_max


grilles = grille_adjoint_technique

print compute_echelon_max(grilles = grilles, start_date = None)

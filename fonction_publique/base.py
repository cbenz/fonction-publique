# -*- coding:utf-8 -*-


from __future__ import division


import os
import pandas as pd
import pkg_resources


## Paths to legislation

asset_path = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )

law_xls_path = os.path.join(
    asset_path,
    "neg_pour_ipp.txt")

law_hdf_path = os.path.join(
    asset_path,
    "grilles.hdf5")

#grille_adjoint_technique_path = os.path.join(
#    asset_path,
#    'FPT_adjoint_technique.xlsx',
#    )
#grille_adjoint_technique = pd.read_excel(grille_adjoint_technique_path, encoding='utf-8')
#grille_adjoint_technique = grille_adjoint_technique.rename(columns = dict(code_grade_NEG = 'code_grade'))
#
#donnees_adjoints_techniques = os.path.join(
#    asset_path,
#    'donnees_indiv_adjoint_technique_test.xlsx',
#    )
#donnees_adjoints_techniques = pd.read_excel(donnees_adjoints_techniques)



# linux_cnracl_path = os.path.join("/run/user/1000/gvfs", "smb-share:server=192.168.1.2,share=data", "CNRACL")
linux_cnracl_path = os.path.join("/home/benjello/data", "CNRACL")
windows_cnracl_path = os.path.join("M:/CNRACL/")

if os.path.exists(linux_cnracl_path):
    cnracl_path = linux_cnracl_path
else:
    cnracl_path = windows_cnracl_path

# Directories paths:

raw_directory_path = os.path.join(cnracl_path, "raw")
tmp_directory_path = os.path.join(cnracl_path, "tmp")
clean_directory_path = os.path.join(cnracl_path, "clean")
output_directory_path = os.path.join(cnracl_path, "output")


# Options:

DEBUG_CLEAN_CARRIERES = True
DEBUG = True
debug_chunk_size = 1000 if DEBUG else None

# HDF5 files paths (temporary):
## Store des variables liées aux carrières nettoyées et stockées dans des tables du fichier donnees_de_carrieres.hdf5
def get_careers_hdf_path(stata_file_path, debug_cleaner_base_carriere = None):
    careers_hdf_path = os.path.join(
        clean_directory_path,
        "debug",
        "{}_{}_carrieres.hdf5".format(stata_file_path[-14:-10], stata_file_path[-8:-4]),
        ) if debug_cleaner_base_carriere else os.path.join(
            clean_directory_path,
            "{}_{}_carrieres.hdf5".format(stata_file_path[-14:-10], stata_file_path[-8:-4])
            )
    return careers_hdf_path


## Store des carrieres dont on a la législation contenant une table des carrieres dont on a la legislation et une
## table des états uniques de carrières rencontrés
def get_careers_for_which_we_have_law_hdf_file_path(careers_hdf_path):
    careers_for_which_we_have_law_hdf_file_path = os.path.join(
        tmp_directory_path,
        "{}_dont_on_a_la_legislation.hdf5".format(careers_hdf_path[-36:-31])
        )
    return careers_for_which_we_have_law_hdf_file_path


## Store des carrières partiellement fusionnées avec la législation
def get_careers_partly_merged_with_law_hdf_file_path(careers_hdf_path):
    careers_partly_merged_with_law = os.path.join(
        tmp_directory_path,
        "{}_{}_partiellement_fusionnees_avec_les_grilles.hdf5".format(
            careers_hdf_path[-36:-31], careers_hdf_path[-30:-26]
            )
        )
    return careers_partly_merged_with_law


# CSV files paths (final files):
def get_careers_merged_with_law_csv_file_path(careers_hdf_path):
    careers_merged_with_law_csv_file_path = os.path.join(
        output_directory_path,
        "{}_{}.csv".format(careers_hdf_path[-35:-31], careers_hdf_path[-30:-26])
        )
    return careers_merged_with_law_csv_file_path



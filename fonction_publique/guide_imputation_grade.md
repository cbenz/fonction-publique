# Correspondance entre libellé et grade: guide d'utilisation

Objectif du programme: obtenir les grades correspondants aux libellés remplis à la main pour les années 2000 à 2014.

Toutes les manipulations de l'utilisateur se font dans le terminal (invite de commande http://fr.wikihow.com/changer-de-r%C3%A9pertoire-dans-le-mode-de-commande)

Liste des étapes pour la mise en oeuvre du matching
  - I. Initialisation: installation de l'environnement de travail (Python, chemins)
  - II. Travail sur les données: à partir des données brutes pour obtenir des données propres au format voulu.
  - III. Programme de matching qui crée la table de correspondance entre libellé et grade.


### I. Initialisation : installation de Python et gestion des chemins

1. Installation de Python et des paquets idoines (fait sur l'ordinateur de Laurent)
L'utilisation du programme nécessite l'installation de python ainsi que l'installation à la main des packages suivants:
- fuzzywuzzy
- python-Levenshstein
- python-slugify

Il est possible de vérifier qu'ils sont installés en faisant : `pip list`

S'ils ne sont pas installés il peuvent être récupérés sur les sites suivants:
- fuzzywuzzy : https://pypi.python.org/pypi/fuzzywuzzy/0.13.0
- python-Levenshstein : http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein
- python-slugify : https://pypi.python.org/pypi/python-slugify/1.2.1

Pour les installer le paquet, il y a deux possibilités :
- `pip instal nom_du_paquet.whl`
- Aller dans le répertoire du paquet (ou se trouve le fichier setup.py) et faire `pip install .`

L'initialisation du programme fournit ici se fait de la manière suivante:
    - se rendre dans le répertoire fonction-publique
    - installer le paquet fonction_publique : `pip install .`

2. Gestion des chemins
    Doivent être précisés dans un fichier config.ini (à partir du config_template.ini) les chemins suivants:
    - Données: emplacement des données initiales (raw) et des données retravaillée (clean).
    - Correspondance: emplacement du dossier où l'on souhaite conserver la table de correspondance.

### II. Travail sur les données

    input: bases carrière par décennie en csv
    output: bases libemploi par décenie en h5
    script: clean_raw_career.py

Le programme d'imputation des libellés se base sur des données en format HDF (fichier .h5),
avec un travail prélable de mise en forme des données pour traitement sous Python
Cette étape consiste donc à transformer les données initiales qui sont au format csv,
en données utilisables pour le matching.

__Ce travail sur les données ne doit être lancé qu'une seule fois, en amont du matching.__

[//]: # Les bases finales ont la forme suivante: pour chaque année entre 2014 et 2000, (TODO MBJ)

### III. Programmes d'imputation des grade pour les libellés observés entre 2000 et 2014.

inputs :
 - liste des libellés observés chaque année pour chaque versant de la fonction publique (base libemploi)
 - éventuellement une table de correspondance déjà commencée que l'on complète avec les libellés qui n'ont pas encore été renseignés.
output: table de correspondance entre les libellés et les grades officiels.
programmes:
 - grade_matching.py
[//]: #  - grade_matching_short.py (TODO)

N.B Pour chaque décennie, le chargement de la base pour la première fois prend du temps, car l'on lance une procédure pour neutraliser
les différences entre libellés simplement dus aux différences de majuscule, d'espace, ou d'accent.

##  Résumé des étapes à réaliser:

 - Installer python et les packages
 - Lancer le setup.py ('pip install .')
 - Renseigner les chemins
 - Lancer le data cleaning ('fonction_publique/scripts/clean_raw_career.py')
 - Lancer l'algorithme de classification des libellés ('grade_matching.py')

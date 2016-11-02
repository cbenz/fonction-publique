# Correspondance entre libélé et grade: guide d'utilisation

Objectif du programme: obtenir les grades correspondants aux libellés remplis à la main pour les années 2000 à 2014. 

Toutes les manipulations de l'utilisateur se font dans le terminal (invite de commande http://fr.wikihow.com/changer-de-r%C3%A9pertoire-dans-le-mode-de-commande)

Liste des étapes pour la mise en oeuvre du matching
  - I. Initialisation: installation de l'environnement de travail (Python, chemins)
  - II. Travail sur les données: à partir des données brutes, faire tourner le programme ??? pour obtenir les données au format voulu. 
  - III. Programme de matching qui crée la table de correspondance entre libélé et grade. 


### I. Initialisation : installation de Python et gestion des chemins 

1. Installation de Python (fait sur l'ordinateur de Laurent)
L'utilisation du programme nécessite l'installation de python ainsi que l'installation à la main des packages suivants: 
- fuzzywuzzy
- python-Levenshstein
- python-slugify
L'initialisation du programme se fait de la manière suivante: dans le repertoire fonction-publique, 
lancer le script "setup.py" (commande: 'pip install .' dans le répertoire)

2. Gestion des chemins
    Doivent être précisés dans un script config.ini (à partir du config_template.ini) les chemins suivants: 
    - Données: emplacement des données initiales (raw) et des données retravaillée (clean). 
    - Correspondance: emplacement du dossier où l'on souhaite conserver la table de correspondance.

### II. Travail sur les données

    input: bases carrière par décennie en csv
    output: bases libemploi par décenie en h5
    script: clean_raw_career.py

Le programme d'imputation des libélés se base sur des données en format h5, avec un travail prélable de mise en forme des données pour traitement sous Python
Cette étape consiste donc à transformer les données initiales qui sont au format csv, en données utilisables pour le matching. 

__Ce travail sur les données ne doit être lancé qu'une seule fois, en amont du matching.__ 

Les bases finales ont la forme suivante: pour chaque année entre 2014 et 2000, ??? MBJ

### III. Programmes d'imputation des grade pour les libellés observés entre 2000 et 2014. 

    inputs: 
    - liste des libellés observés chaque année pour chaque versant de la fonction publique (base libemploi)
    - éventuellement une table de correspondance déjà commencée que l'on complète avec les libellés qui n'ont pas encore été renseignés.
    output: table de correspondance entre les libellés et les grades officiels. 
    programmes: 
    - grade_matching.py
    - grade_matching_short.py (TO DO)

N.B Pour chaque décennie, le chargement de la base pour la première fois prend du temps, car l'on lance une procédure pour neutraliser
les différences entre libellés simplement dus aux différences de majuscule, d'espace, ou d'accent. 


##  Résumé des étapes à réaliser: 

 - Installer python et les packages
 - Lancer le setup.py ('pip install .')
 - Renseigner les chemins 
 - Lancer le data cleaning ('clean_raw_career.py')
 - Lancer l'algorithme de classification des libellés ('grade_matching.py')

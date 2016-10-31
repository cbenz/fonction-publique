Correspondance entre libélé et grade: guide d'utilisation

Preview: liste des étapes pour la mise en oeuvre du matching
I. Installation de l'environnement de travail (Python, Anaconda, chemins)
II. Travail sur les données: à partir des données brutes, faire tourner le programme ??? pour obtenir les données au format voulu. 
III. Programme de matching qui crée la table de correspondance entre libélé et grade. 
IV. Test d'adéquation du matching sur les années où l'on observe le grade et le libélé


I. Installation 

1. Installation de Python

2. Gestion des chemins
    Doivent être précisés dans le programme config.ini (à partir du config_template.ini) les chemins suivants: 
    - Données: emplacement des données initiales (raw) et des données retravaillée (clean). 
    - Correspondance: emplacement du dossier où l'on souhaite conserver la table de correspondance.

II. Travail sur les données

    input: bases carrière par décennie en csv
    output: bases libemploi par décenie en h5
    programme: raw_data_cleaner.py

Le programme d'imputation des libélés se base sur des données en format h5, avec un travail prélable de mise en forme des donnés pour neutraliser
les différences entre libellés simplement dus aux différences de majuscule, d'espace, ou d'accent. 
Une première étape consiste donc à transformer les données initiales qui sont au format csv, en données utilisables pour le matching. 

Ce travail sur les données ne doit être lancé qu'une seul fois, en amont du matching. 
Les bases finales ont la forme suivante: pour chaque année entre 2014 et 2000, est stockée la liste des libellés (variable libemploi)
avec le versant de la FP correspondant (varible status), et le nombre d'occurence de chacun des libellés dans la base carrière.

III. Programmes d'imputation des grade pour les libellés observés entre 2000 et 2014. 

    inputs: 
    - liste des libellés observés chaque année pour chaque versant de la fonction publique (base libemploi)
    - éventuellement une table de correspondance déjà commencée que l'on complète avec les libellés qui n'ont pas encore été renseignés.
    output: table de correspondance entre les libellés et les grades officiels. 
    programmes: 
    - grade_matching.py
    - grade_matching_short.py

Par défaut, la nouvelle table sauvegarde l'ancienne. Pour sauvegarder une nouvelle table il faut préciser un nouveau nom dans la fonction "store_libelle".  
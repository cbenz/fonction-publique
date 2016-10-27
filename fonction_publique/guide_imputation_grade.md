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
    - Correspondance: emplacement du dossier où l'on souhaite conservé la table de correspondance.

II. Travail sur les données

Le programme d'imputation des libélés se base sur des données en format h5. Une première étape consiste donc à transformer les données initiales qui sont au format SAS. 

III. Programme d'imputation des grade pour les libellés observés entre 2000 et 2014. 
    input: liste des libellés observés chaque année pour chaque versant de la fonction publique
    output: table de correspondance entre:
        1. Grades officiels, sous la forme de triplets (versant, grade, date d'effet) pour gérer l'historique des Grades
        2. Liste de libellés, sous la forme de duplets (libellés, année) pour gérer le fait qu'un même libellé peut renvoyer à des grades différents en fonction de l'année.


Par défaut, la nouvelle table sauvegarde l'ancienne. Pour sauvegarder une nouvelle table il faut préciser un nouveau nom dans la fonction "store_libelle".  
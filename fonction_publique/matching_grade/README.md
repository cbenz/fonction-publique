Correspondance entre libélé et grade: guide d'utilisation




Preview: liste des étapes pour la mise en oeuvre du matching
I. Installation de l'environnement de travail (Python, Anaconda, chemins)
II. Travail sur les données: à partir des données brutes, faire tourner le programme ??? pour obtenir les données au format voulu. 
III. Programme de matching qui crée la table de correspondance entre libélé et grade. 
IV. Test d'adéquation du matching sur les années où l'on observe le grade et le libélé (2011-2014)


I. Installation 

1. Installation de Python

2. Gestion des chemins
    Doivent être précisés dans le programme config.ini (à partir du config_template.ini) les chemins suivants: 
    - Données: emplacement des données initiales (raw) et des données retravaillée (clean). 
    - Correspondance: emplacement du dossier où l'on souhaite conservé la table de correspondance.

II. Travail sur les données

Le programme d'imputation des libélés se base sur des données en format h5. Une première étape consiste donc à transformer les données initiales qui sont au format SAS. 
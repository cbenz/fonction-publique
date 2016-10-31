 QUESTIONS MAHDI
 
 
-  Comment lire: 

    return (libemplois
            .loc[annee]
            .loc[
                ~libemplois.loc[annee].index.isin(libelles_emploi_deja_renseignes)
                ]
            .index
            .tolist()
            )

- A more efficient way to do: 

    list_max = list()    
    for lib in liste_lib:
        list_max += process.extractBests(lib, liste_grade, score_cutoff = 0, limit = 1)
    low_score =   pd.DataFrame(list_max,columns=('lib','score_max')) 
    return (low_score[low_score.score_max<=score_max])
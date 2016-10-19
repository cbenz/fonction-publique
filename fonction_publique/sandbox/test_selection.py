# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 17:19:43 2016

@author: simonrabate
"""

import numpy as np
import pandas as pd

lab   = ["label"]*20
score = ["score"]*20
nb = [str(i) for i in range(1,21)]

lab = map(lambda (x,y): x+y, zip(lab,nb)) 
score = map(lambda (x,y): x+y, zip(score,nb))
 
libelles_emploi_additionnels = pd.DataFrame({'libelle_emploi':lab, 'score':score})
selection = "1:4,6,8,15:18"


libelles_emploi_selectionnes= list()
sel = list()
if (":" in selection) or ("," in selection):
    for  s in selection.split(","):
        if ":" in s:
            start = int(s.split(":")[0])
            stop = int(s.split(":")[1])
            if not (libelles_emploi_additionnels.index[0] <= start <= stop <= libelles_emploi_additionnels.index[-1:]):
                print 'Plage de valeurs incorrecte.'
                continue
            else:
                sel += range(start,stop+1)
                continue

        else: 
            sel += s

sel = [int(i) for i in sel]

libelles_emploi_selectionnes += libelles_emploi_additionnels.iloc[sel].libelle_emploi.tolist()



# -*- coding:utf-8 -*-
from __future__ import print_function, division
'''
Created on 14 oct. 2013
@author: aeidelman
'''

import pdb
import numpy as np
import pandas as pd 
from config import path_pgm_esps, path_data_contrats
import random

import sys
sys.path.append(path_pgm_esps)
import src.ESPS as ESPS
import src.readSAS as readSAS
import src.utils as utils
from scipy.stats import rv_discrete  

path_medicam = "C:\\Users\\Toni\\Dropbox\\Toni Dropbox\\Vie etudiante\\M2\\Stage DGT/Donnees/Medicament/MEDICAM'/"
medicam = pd.read_excel(path_medicam + 'MEDICAM 2008-2012-AMELI_tous prescripteurs.xls', "MedicAM 0812")
medicam = medicam[:15552]
annees = range(2008,2013)
### selection des statine
test = medicam["Classe EphMRA"]
statine = medicam["Classe EphMRA"].str.contains("STATINE")
statine = medicam[statine]

### Travail sur les quantités de médicaments
nom = statine['NOM COURT']
statine['nbr'] = [x[-3:] for x in nom]
statine['nbr'] = statine['nbr'].astype(int)

statine['mg'] = [x[1][-3:] for x in nom.str.split('MG')] # TODO: utiliser s2.str.split('_').str.get(0)
## correction issus de R, mais à retrouver
#TODO: verifier que MG n'apparait qu'une fois
statine.loc[[8925,8926,10470,10471],"mg"] = 5 
statine.loc[[9038,10037],"mg"] = 40
statine['mg'] = statine['mg'].astype(int)

statine.loc[statine['Classe\nATC'] == 'PRAVASTATINE ET ACIDE ACETYLSALICYLIQUE','Classe\nATC'] = 'PRAVASTATINE'
statine.loc[statine['Classe\nATC'] == 'ATORVASTATINE ET AMLODIPINE','Classe\nATC'] = 'ATORVASTATINE'
statine['Classe\nATC'].value_counts()

pdb.set_trace()
for annee in annees:
    variable_name = 'Nombre de boites rembours\ées ' + str(annee)
    
    statine['mg_conso'] = statine['mg']*statine['nbr']*statine[variable_name]
grps_statine = statine.groupby('Classe\nATC')
grps_statine['Nombre de boites remboursées 2008']*grps_statine['mg']
pdb.set_trace()

# -*- coding:utf-8 -*-
'''
Created on 5 août 2014

@author: tvialette
'''

import numpy as np
import pandas as pd
from pandas import DataFrame
import datetime as dt
import matplotlib.pyplot as plt

from medic_gouv import load_medic_gouv
from sniiram import load_sniiram
from infos_sniiram import load_infos_sniiram
from outils import (relative_dates, application_regression_rupture,
                   application_regression_simple, evolution, moving_average)

# parametres du calcul
info_utiles_from_gouv = ['CIP7', 'CIP13', 'Nom', 'Id_Groupe', 'Type', 'Date_declar_commerc']

# chargement des donnees
maj_bdm = 'maj_20140801\\'
gouv = load_medic_gouv(maj_bdm, var_to_keep=info_utiles_from_gouv, CIP_not_null=True)

# On mets les dates au format datetime
for var in info_utiles_from_gouv:
    if 'date' in var or 'Date' in var:
        gouv[var] = gouv[var].map(lambda t: dt.datetime.strptime(t, "%d/%m/%Y").date())
        for time_idx in ['month', 'year']:
            name = var + '_' + time_idx
            gouv[name] = 0
            gouv[name][gouv[var].notnull()] = gouv[var][gouv[var].notnull()].apply(lambda x: getattr(x, time_idx))

# On charge la base et les informations issues de sniiram
infos_sniiram = load_infos_sniiram()
sniiram = load_sniiram()

# On définit la période d'étude
period = sniiram.columns
assert all(period == sorted(period))
period = list(period)

# Pour chaque médicament on détermine l'année de la première vente :
premiere_vente = pd.Series(index=sniiram.index)
derniere_vente = pd.Series(index=sniiram.index)
for month in period:
    vente = sniiram[month] > 0
    cond_prem = vente & premiere_vente.isnull()
    premiere_vente[cond_prem] = month
    cond_dern = ~vente & premiere_vente.notnull() & derniere_vente.isnull()
    derniere_vente[cond_dern] = month - 1

sniiram['premiere_vente'] = premiere_vente
sniiram['derniere_vente'] = derniere_vente

# Définition de la base brute contenant toutes les variables et les données chargées :
base_brute = pd.merge(gouv, sniiram, left_on='CIP13', right_index=True)
base_brute = pd.merge(base_brute, infos_sniiram, left_on='CIP13', right_on='Code_CIP_13_delivre_pharmacie')

var = 'Date_declar_commerc'
test = 100*base_brute[var+'_year'] + base_brute[var+'_month'] - base_brute['premiere_vente']
test_in_month = abs(test)
test_in_month.value_counts()


##### On fait maintenant l'exploitation à partir de groupe : 
### Un groupe c'est : un identifiant de groupe + un indicateur du statut dans chaque groupe
### Exemple : Id_groupe et is_princeps
base_brute['group'] = base_brute['Id_Groupe']
base_brute['role'] = base_brute['Type'] == 0

#On concerve sulement les medicaments dont on connait le groupe generique
base_brute = base_brute.loc[base_brute['group'].notnull()]
base_brute['group'] = base_brute['group'].astype(int)
#pour faire planter si on a trois groupes...
base_brute['role'] = base_brute['role'].astype(bool)
# quelques infos pour faire joli
nombre_cip = len(base_brute['CIP13'].unique())
taille_base_brute = len(base_brute)
print "La base base_brute provisoire dont tous les medicaments ont un groupe generique defini contient " + str(taille_base_brute) + \
    " lignes pour " + str(nombre_cip) + " medicaments uniques (CIP)."

### Date de chute du brevet, se généralise en "modification du groupe" ? 
## On a deux méthodes concurrentes
grp = base_brute.groupby('group')

chute_brevet1 = grp.apply(lambda group: group.loc[~group['role'],'premiere_vente'].min())
chute_brevet2 = grp.apply(lambda group: group.loc[~group['role'],'Date_declar_commerc'].min())

# Condition qui permet de selectionner les médicaments à conserver, on veut des génériques et des princeps
cond = (grp['role'].sum() > 0) & (grp.size() - grp['role'].sum() > 0) & (chute_brevet1 > period[0])

# On travaille maintenant sur les unités des ventes, il faut donc comparer les quantités en fonction
# du contenu des boites

# Pour comparer les quantités au sein des groupes il est nécessaire de s'assurer que les unités sont les mêmes
# On ne conserve que les unités de dosages communes aux groupes.

# 5 groupes posent problèmes : parmi les 5, les groupes 341 et 845 ne semblent pas présenter des dosages différents (erreurs
# dans la retranscriptions ?)
# Les 3 autres groupes (493, 494, 521) sont des comprimés avec dosages différents, on ponderera le nombre
# d'unités par le dosage
# ponderation = base_brute['group'].isin((493, 494, 521))
# base_brute['unite_reference'] = (base_brute.Dosage[ponderation].apply(float))*(base_brute.Nombre_dunites_par_conditionnement[ponderation].apply(float))


# On garde les groupes "simples": ceux où il y a un seul dosage, une seule unité
# de dosage. De plus on ne garde que les conditionnement exprimés en nombre entiers
# ou bien, quand il y a un slash dedans (deux indications de conditionnement), ceux
# pour lesquels le conditionnement est le même pour tous les médicaments du groupe
base_brute['slash_in_cond'] = base_brute['Nombre_dunites_par_conditionnement'].str.contains('\/')
grp = base_brute.groupby('group')
longueur_dosage = grp.apply(lambda x: len(x['Dosage'].unique()))
longueur_unite = grp.apply(lambda x: len(x['Unite_du_dosage'].unique()))
longueur_slash = grp.apply(lambda x: ((len(x['Nombre_dunites_par_conditionnement'].unique()) == 1) | (sum(x['slash_in_cond']) == 0)))
condition_dosage = (longueur_dosage == 1) & (longueur_unite == 1) | (longueur_slash == 1)

print '''Après le travail sur le dosage les problèmes d'informations nous obligent à
nous séparer de ''' + str(sum(cond) - sum(cond & condition_dosage)) + ''' groupes.'''

cond = cond & condition_dosage

# L'unité de référence permet de comparer au sein d'un même groupe la quantité des boites
# c'est le nombre d'unité de conditionnement sauf quand il y a un slash où là, on met 
# 1 comme référence puisqu'on ne gardera que les groupes qui ont un même conditionnement
base_brute['unite_reference'] = base_brute['Nombre_dunites_par_conditionnement']
base_brute.loc[base_brute['slash_in_cond'].isnull(), :] = False
base_brute.loc[base_brute['slash_in_cond'], 'unite_reference'] = 1

for date in period:
    base_brute.loc[:, date] *= base_brute['unite_reference'].apply(float)

table_final = base_brute.loc[base_brute['Id_Groupe'].isin(cond.index[cond]), :]


###############################################################################

# Retour sur les problèmes de dosage.
## S'il y a un slash il y en a 1 ou 3 : pour les 4 médicaments ayant 3 slashes il n'y a pas de
## problème puisque se sont des médicaments du même groupes ayant la même unité de dosage, donc
## l'unité référence sera donc le nombre d'unité par boite :
#base_brute.loc[(nb_slashes == 3), 'unite_reference'] = base_brute['Nombre_dunites_par_conditionnement'][nb_slashes == 3]
#
##Pour les produits ayant un slash on sépare les deux valeurs :
#def get_dose1(string):
#    idx = string.index('/')
#    return string[:idx]
#    
#def get_dose2(string):
#    idx = string.index('/')
#    return string[idx+1:]
#
#
#base_brute.loc[nb_slashes == 1, 'Dosage1'] = base_brute['Dosage'][nb_slashes == 1].apply(get_dose1)
#base_brute.loc[nb_slashes == 1, 'Dosage2'] = base_brute['Dosage'][nb_slashes == 1].apply(get_dose2)
#
#obj = base_brute.loc[base_brute.index == 108, 'Dosage']
#
## Seul le groupe 845 pose un problème avec différents dosage2 [5, 20, 50]
## On vérifie qu'ils cependat tous tous les mêmes caractéristiques de dosage 
##2734     'DORZOLAMIDE/TIMOLOL ACTAVIS 20 mg/ml + 5 mg/ml, collyre en solution'
##4331     'DORZOLAMIDE/TIMOLOL SANDOZ 20 mg/5 mg/ml, collyre en solution'
##5141     'COSOPT 20 mg/ml + 5 mg/ml, collyre en solution'
##5977     'DORZOLAMIDE/TIMOLOL EG 20 mg/ml + 5 mg/ml, collyre en solution'
##9311     'DORZOLAMIDE/TIMOLOL TEVA 20 mg/ml + 5 mg/ml, collyre en solution'
##9513     'DORZOLAMIDE/TIMOLOL ZENTIVA 20 mg/ml + 5 mg/ml, collyre en solution'
##15701    'DORZOLAMIDE/TIMOLOL MYLAN 20 mg/ml + 5 mg/ml, collyre en solution'
##17411    'DORZOLAMIDE/TIMOLOL BIOGARAN 20 mg/ml + 5 mg/ml, collyre en solution'

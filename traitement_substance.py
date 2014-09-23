'''
Created on 23 juil. 2014

@author: tvialette
'''

import numpy as np
import pandas as pd
import pdb

from medic_gouv import load_medic_gouv
from medicam import load_medicam



years = range(2002,2013)
info_utiles_from_gouv = ['Etat', 'Date_AMM',
                         'CIP7', 'Date_declar_commerc', 'Taux_rembours', 'Prix',
                         'Id_Groupe', 'Type',
                         'Code_Substance', 'Nom_Substance', 'Dosage',
                         'Valeur_SMR', 'Valeur_ASMR']

# chargement des donnees
medicam, axis0, axis1, axis2 = load_medicam(years)
maj_bdm = 'maj_20140630\\'
gouv = load_medic_gouv(maj_bdm, info_utiles_from_gouv, CIP_not_null=True)

## On veut les substance dans lesquelles il y eu perte de brevet
# il faut deux conditions, ne pas avoir de generique au debut, en avoir a la fin
first = years[0]
last = years[-1]

''' Détermine les groupes avec lesquels on travaille ensuite'''
substance_princeps = gouv.loc[gouv['Type']==0,['Code_Substance','Nom_Substance']]
substance_princeps.drop_duplicates(inplace=True)

gouv['is_generique'] = gouv['Type'] > 0

princeps =  gouv.loc[~gouv['is_generique'],:]
generiques = gouv.loc[gouv['is_generique'],:]

# Collecte l'ensemble des groupes de generiques de la base
keep = gouv.loc[gouv['Id_Groupe'].notnull(), 'Id_Groupe']
beta = np.unique(keep)

base = axis2.index('base')

# Pour chaque médicament on détermine l'année de la première vente :
premiere_vente = pd.Series(index=axis0.index)
for year in range(len(years)):
    condition = medicam[:,year,base] > 0
    condition = condition & premiere_vente.isnull()
    premiere_vente[condition] = year
axis0['premiere_vente'] = premiere_vente

cip_pas_dans_gouv = [cip for cip in axis0['CIP7'].astype(float) if cip not in gouv['CIP7']]
chute_brevet = pd.Series(index=axis0.index)


final = pd.merge(axis0, gouv, on='CIP7')

CIP_unique = pd.unique(final['CIP7'])

#A chaque medicament (generique ou princeps) , on cherche a indique la date de chute du brevet


#Pour les médicaments ayant un groupe d'identification (sur le marche ces 2 dernieres annees), la selection est directe
chute_brevet = pd.Series(index=final.CIP7.index)

condition_gene = final['is_generique']
condition_na = ~final['premiere_vente'].isnull()


for id_gr in final['Id_Groupe'].unique():
    condition_id = final['Id_Groupe'] == id_gr
    var = final[condition_id & condition_gene & condition_na]
    teta = var.premiere_vente
    if not teta.empty:
        chute_brevet[condition_id] = min(teta)
        
final['chute_brevet'] = chute_brevet 


#On repertorie les annees de chute de brevet en fonction des CIP unique         
chute_brevet_cip = pd.Series(index=range(0,len(CIP_unique)))
condition_na_2 = final['chute_brevet'].notnull()

for cip in CIP_unique:
    bool_int = final[(final['CIP7'] == cip) & condition_na_2]
    if not bool_int.empty:
        index_final = bool_int.index[0]
        index_unique = CIP_unique == cip
        chute_brevet_cip[index_unique] = final.loc[index_final, 'chute_brevet']
    
chute_brevet_cip = pd.DataFrame({'CIP7':np.unique(final['CIP7']), 'chute_brevet':chute_brevet_cip})

nb_med = len(chute_brevet_cip)
nb_gouv = sum(chute_brevet_cip.chute_brevet.notnull())

print 'Sur les '+ str(nb_med) + ' medicaments de la base finale, seuls '+ str(nb_gouv) +' ont leur groupe générique répertorié (sur le marche il y a au plus 2 ans).'


#for cip in chute_brevet_cip['CIP7']:
#    final.chute_brevet[final['CIP7'] == cip] = chute_brevet_cip.chute_brevet[chute_brevet_cip['CIP7'] == cip]
    


chute_brevet_substance = pd.Series(index=range(0,len(final.CIP7)))

#Pour chaque CIP on determine le nombre de substances qu'il contient :
nb_subs_par_cip =  pd.Series(index=range(0,len(CIP_unique)))

for cip in CIP_unique:
    nb_subs = len(final[final['CIP7'] == cip])
    nb_subs_par_cip[CIP_unique == cip] =  nb_subs
   
nb_subs_par_cip = pd.DataFrame({'CIP7':CIP_unique, 'nb_subs':nb_subs_par_cip})

#On concerve sulement les medicaments dont on connait le groupe
#

final = final.loc[final['chute_brevet'].notnull()]

#Fonciton permettant de lire la base

variable = 'base'                                   #Definit la variable sur laquelle on veut travailler
medic = final.CIP7[final.Code_Substance == 3127]    #liste de medicaments identifies par leur CIP
periode = years                                     #periode d'interet

def read(medic, variable, periode):
    index0 = [axis0.CIP7[axis0.CIP7 == item].index[0] for item in medic]
    index1 = [axis1.index(item) for item in periode]
    index2 = axis2.index(variable)
    output = np.zeros((len(index0), len(index1)))
    for el in index0:
        output[el - index0[0]] = medicam[el,index1,index2]
    return output

'''
pour chaque molecule princeps de la table Gener il faut: 
    date perte du brevet
    la liste des generique
    la liste des medicaments avec la meme substance.
dictionnaire : {'CIP du medicament qui pert le brevet' : (date perte du brevet, la liste des generiques, la liste des medicaments avec la meme substance)}
'''

groupe = 850

def variables(groupe, periode):
    condition_id = final['Id_Groupe'] == groupe
    annee_chute = final.chute_brevet[condition_id].unique()
    gene = final.CIP7[condition_id & condition_gene].unique()
    princeps = final.CIP7[condition_id & ~condition_gene].unique()
    return annee_chute, gene, princeps

#########################################################################################################################

pdb.set_trace()

#########################################################################################################################


#On cherche un deuxieme indicateur de l'annee de chute du brevet pour les medicaments sortis du marche il y a plus de 2ans
#On peut s'aider de la substance :

chute_brevet_substance = pd.Series(index=range(0,len(final.CIP7)))

#Pour chaque CIP on determine le nombre de substances qu'il contient :
nb_subs_par_cip = pd.Series(index=range(0,len(CIP_unique)))

for cip in CIP_unique:
    nb_subs = len(final[final['CIP7'] == cip])
    nb_subs_par_cip[CIP_unique == cip] =  nb_subs
   
nb_subs_par_cip = pd.DataFrame({'CIP7':CIP_unique, 'nb_subs':nb_subs_par_cip})

#print nb_subs_par_cip['nb_subs'].value_counts()

#On cree des groupes de medicaments contenant les memes substances

groupe_substance = pd.Series(index=range(0,len(CIP_unique)))

#On change la valeur des Na dans le Code_Substance pour pouvoir ranger la liste
final.Code_Substance[final.Code_Substance.isnull()] = 0


#Pour chaque substance on determine la chute du brevet en prenant la valeur mediane de la premiere vente

for code_subs in final['Code_Substance'].unique():
    condition_subs = final['Code_Substance'] == code_subs
    var = final[condition_subs & condition_na]
    teta = var.premiere_vente
    if not teta.empty:
        chute_brevet_substance[condition_subs] = ceil(np.median(teta))

final['chute_brevet_substance'] = chute_brevet_substance



CIP_unique = pd.unique(final['CIP7'])
condition_na_2 = ~final['chute_brevet_substance'].isnull()

chute_brevet_substance_mediane = pd.Series(index=range(0,len(CIP_unique)))

for cip in final['CIP7'].unique():
    condition_cip = final['CIP7'] == cip
    var = final[condition_cip & condition_na_2]
    teta_2 = var.chute_brevet_substance
    if not teta_2.empty:
        condition_cip_unique = CIP_unique == cip
        chute_brevet_substance_mediane[condition_cip_unique] = ceil(np.median(teta_2))
        
chute_brevet_substance_mediane = pd.DataFrame({'CIP7':CIP_unique, 'chute_brevet_substance_mediane':chute_brevet_substance_mediane})
final = pd.merge(final, chute_brevet_substance_mediane, on='CIP7')


#Quels differences pour en fonction du traitement ?

cip_pas_dans_gouv = [cip for cip in axis0['CIP7'].astype(float) if cip not in gouv['CIP7']]
medicam_pas_dans_gouv = final['Type'].isnull()

final_gouv = final.loc[~medicam_pas_dans_gouv]

test_diff = final_gouv['chute_brevet'] == final_gouv['chute_brevet_substance_mediane']
test_diff_2 = final_gouv['chute_brevet'] == final_gouv['chute_brevet_substance']

pdb.set_trace()

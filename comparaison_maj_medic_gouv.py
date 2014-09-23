'''
Created on 16 juil. 2014

@author: tvialette
'''

#Programme permettant d'etudier les differences entre les mises a jour de la base medicament.gouv

import pdb

from medic_gouv import load_medic_gouv

#Ancienne maj
maj_bdm_old = 'maj_20140630\\'

#Nouvelle maj
maj_bdm_new = 'maj_20140801\\'



#Variables d'interet
info_utiles_from_gouv = ['Etat','Date_AMM',
                         'CIP7','Date_declar_commerc','Taux_rembours','Prix',
                         'Id_Groupe','Type',
                         'Code_Substance','Nom_Substance','Dosage',
                         'Valeur_SMR','Valeur_ASMR']

#Extraction des bases a traiter
gouv_old = load_medic_gouv(maj_bdm_old, info_utiles_from_gouv, CIP_not_null=True)
gouv_new = load_medic_gouv(maj_bdm_new, info_utiles_from_gouv, CIP_not_null=True)


#Nouveau medicaments de la base
medic_new = gouv_new.loc[-gouv_new['CIP7'].isin(gouv_old['CIP7'])]
print 'Nouveaux medicaments dans la base :' 
print medic_new.loc[:,('CIP7','Nom')]

#Medicaments sortis de la base
medic_drop = gouv_old.loc[-gouv_old['CIP7'].isin(gouv_new['CIP7'])]
print 'Medicaments sortis de la base :' 
print medic_drop.loc[:,('CIP7','Nom')]

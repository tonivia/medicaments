# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 13:31:35 2014

@author: tvialette
"""
import pandas as pd
import numpy as np

def load_infos_sniiram(variables_interet = ['Nom_court_du_medicament_', 'Code_CIP_13_delivre_pharmacie',
                                             'Dosage', 'Unite_du_dosage', 'Nombre_dunites_par_conditionnement']):
    ''' Retourne les variables d'intérets de dosage disponibles de la base sniiram '''
    path_data = "C:\\Users\\Toni\\Dropbox\\Toni Dropbox\\Vie etudiante\\M2\\Stage DGT\\Donnees\\Medicament\\Sniiram\\"
    table = pd.read_csv(path_data + 'IR_PHA_R.csv', sep=';')

    # On renomme les colonnes dont on a les descriptifs (nouvelles versions)
    nom_variable = pd.read_csv(path_data + 'Referentiel PHARMACIE.csv', sep=';')
    nom_variable.set_index('Donnees', drop=True, inplace=True)
    table.rename(columns=nom_variable['Libelle'].to_dict(), inplace=True)
#     # 7 variables présentes dans l’ancienne version du référentiel,
#     # c'est-à-dire avant sous ORAREF, ne sont plus restituées dans la nouvelle version
#     variables_old = ['PHA_ATC_CLA', 'PHA_ATC_LIB', 'PHA_EPH_CLA', 'PHA_EPH_LIB',
#                        'PHA_SUB_DOS', 'PHA_DOS_UNI', 'PHA_UPC_NBR']

    # Pour certains produits seules les anciennes variables nous informent du dosage,
    # on va donc prendre l'union des deux sources pour avoir le  moins de NaN possible :
    # ['Dosage'] avec ['PHA_SUB_DOS'] et ['Unite_du_dosage'] avec ['PHA_DOS_UNI']
    table.loc[table['Dosage'].isnull(), 'Dosage'] = table.loc[table['Dosage'].isnull(), 'PHA_SUB_DOS']
    table.loc[table['Unite_du_dosage'].isnull(), 'Unite_du_dosage'] = table.loc[table['Unite_du_dosage'].isnull(), 'PHA_DOS_UNI']
    
    table_int = table[variables_interet]
    is_nan = table_int['Dosage'].isnull() | table_int['Unite_du_dosage'].isnull()
    
    print "Sur les " + str(len(table_int)) + " médicaments de la base, nous avons \
    des informations de dosage sur " + str(len(table_int) - sum(is_nan)) + " d'entre eux."
    table_int.drop(is_nan.index[is_nan], inplace=True)
    # Remplacemet des virgules par des points
    table_int.loc[:, 'Dosage'] = table_int['Dosage'].str.replace(',', '.')
    table_int.loc[:, 'Dosage'] = table_int['Dosage'].str.replace('0.50', '0.5')
    table_int.loc[:, 'Nombre_dunites_par_conditionnement'] = table_int['Nombre_dunites_par_conditionnement'].str.replace(',', '.')
    table_int.loc[:, 'Nombre_dunites_par_conditionnement'] = table_int['Nombre_dunites_par_conditionnement'].str.replace(' DOSES', '')
    table_int.loc[:, 'Unite_du_dosage'] = table_int['Unite_du_dosage'].str.replace(',', '.')
    table_int.loc[:, 'Unite_du_dosage'] = table_int['Unite_du_dosage'].str.replace('P. 100', '%')
    table_int.loc[:, 'Unite_du_dosage'] = table_int['Unite_du_dosage'].str.replace('MG/24 H', 'MG/24H')
    table_int.loc[:, 'Unite_du_dosage'] = table_int['Unite_du_dosage'].str.replace('G/100 G', '%')
    table_int.loc[:, 'Unite_du_dosage'] = table_int['Unite_du_dosage'].str.replace('M.UI', 'MUI')
    table_int.loc[:, 'Unite_du_dosage'] = table_int['Unite_du_dosage'].str.replace('MUI/ MG', 'MUI/MG')
    table_int.loc[:, 'Unite_du_dosage'] = table_int['Unite_du_dosage'].str.replace('MG/1 ML', 'MG/ML')
    return table_int

test = load_infos_sniiram()
test.loc[test['Nombre_dunites_par_conditionnement'].isnull()]

## Pour info, les variables disponibles dans la base sont les suivantes :
#variables_dispo = ['Code_CIP_13_delivre_pharmacie', 'Code_CIP_7delivre__pharmacie', 'Code_ucd',
#                  'Nature_medicament', 'PHA_MED_NOM', 'Plus_petit_conditionnement', 'Debut_inscription',
#                  'Fin_inscription', 'Motif_de_fin_de_remboursement', 'Indicateur_inscription_sur_liste',
#                  'Forme', 'Libelle_forme', 'Complement_de_forme', 'Libelle_complement_de_forme',
#                  'PHA_SUB_DOS', 'PHA_DOS_UNI', 'PHA_UPC_NBR', 'PHA_ATC_CLA', 'PHA_ATC_LIB',
#                  'PHA_EPH_CLA', 'PHA_EPH_LIB', 'Nom_du_laboratoire', 'Nom_complet_1ere_partie',
#                  'Nom_complet_2eme_partie', 'Derniere_mise_a_jour', 'Quantite_maxi_signalement',
#                  'Quantite_maxi_rejet', 'Prescription_restreinte', 'Medicament_dexception',
#                  'Type_de_specialite', 'Date_deffet_restriction_selon_sexe', 'Restriction_selon_sexe',
#                  'Date_deffet_restriction_selon_age', 'Age_minimum', 'Age_maximum',
#                  'Interaction_medicamenteuse_grave', 'Indicateur_medicament_generique', 'Date_deffet_de_la_pecp',
#                  'Prise_en_charge_particuliere', 'Prescription_initiale_hospitaliere', 'Date_debut_alm',
#                  'Date_fin_alm', 'Indicateur_suivi_de_medicaments',
#                  'Date_debut_de_validite_du_tarif_d’un_medicament_le_plus_recent', 'Prix_unitaire',
#                  'Prix_unitaire_de_lunite', 'Code_taux', 'Code_CIP_7_referent_du_groupe_generique',
#                  'Code_CIP_13_referent_du_groupe_generique', 'Numero_GERS_du_groupe_generique',
#                  'Nom_du_groupe_generique', 'Liste_des_principes_actifs', 'Libelle_du_nom_commercial_du_medicament',
#                  'Nom_court_du_medicament_', 'Code_de_la_Classe_therapeutique_ephmra',
#                  'Libelle_de_la_classe_therapeutique_ephmra', 'Indicateur_medicament_generique',
#                  'Top_convention_DSES_suivi_de_la_reforme', 'Date_de_debut_de_generication_du_groupe',
#                  'Top_Hypertension_arterielle', 'Top_grand_conditionnement', 'Dosage', 'Unite_du_dosage',
#                  'Nombre_dunites_par_conditionnement', 'Code_de_la_classe_therapeutique_ATC',
#                  'Libelle__de_la_classe_therapeutique_ATC', 'Code__2eme_niveau_de_la_classe_ATC',
#                  'Libelle_2eme_niveau_de_la_classe_ATC', 'PHA_DIA_TOP', 'PHA_AST_TOP', 'PHA_CAR_TOP']

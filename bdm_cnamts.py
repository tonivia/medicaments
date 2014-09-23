# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 15:30:38 2014

@author: tvialette
"""
import pandas as pd

path_data = "C:\\Users\\Toni\\Dropbox\\Toni Dropbox\\Vie etudiante\\M2\\Stage DGT\\Donnees\\BDM_CNAMTS\\AFM\\"

info_dispo = ['CIP', 'CIP7', 'CIP_UCD', 'NATURE', 'NOM_COURT', 'INDIC_COND',
              'DEBUT_REMB', 'FIN_REMB', 'CODE_LISTE', 'CODE_FORME', 'FORME',
              'CODE_CPLT', 'CPLT_FORME', 'DOSAGE_SA', 'UNITE_SA', 'NB_UNITES',
              'CODE_ATC', 'CLASSE_ATC', 'CODE_EPH', 'CLASSE_EPH', 'LABO',
              'NOM_LONG1', 'NOM_LONG2', 'SUIVI', 'DATE_EFFET', 'SEUIL_ALER',
              'SEUIL_REJE', 'PRESC_REST', 'EXCEPTIONS', 'TYPE', 'SEXE',
              'INTERACT', 'PIH', 'PECP']


def as_number(string):
    ''' fonction float() qui renvoie NaN en cas d'erreur '''
    try:
        return float(string)
    except ValueError:
        return None


def get_dose(obj):
    ''' permet d'extraire le nombre d'unités des cellules où il y a un slash,
    exemple : pour [1/10 ML] renvoie [1] '''
    obj = str(obj)
    if '/' in obj:
        idx = obj.index('/')
        return obj[:idx]
    else:
        return obj


def bdm_cnamts(info_utiles, unites_par_boite=True):
    ''' charge les info_utiles et crée la variable unites_par_boite '''
    table_entiere = pd.read_excel(path_data + "BDM_CIP.xlsx")
    table = table_entiere.loc[:, info_utiles]
    if unites_par_boite:
        table['unites_par_boite'] = table_entiere['NB_UNITES'].str.replace(',', '.')
        table['unites_par_boite'] = table['unites_par_boite'].apply(get_dose)
        table['unites_par_boite'] = table['unites_par_boite'].apply(as_number)
    return table

if __name__ == '__main__':
    info_utiles_from_cnamts = ['CIP', 'CIP7', 'FORME', 'DOSAGE_SA', 'UNITE_SA']
    test = bdm_cnamts(info_utiles_from_cnamts)

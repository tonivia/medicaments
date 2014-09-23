# -*- coding: utf-8 -*-
"""
Created on Thu Aug 21 10:12:58 2014

@author: tvialette
"""

import pandas as pd
import numpy as np
import datetime as dt

def load_infos_tarifs():
    path_data = "C:\\Users\\Toni\\Dropbox\\Toni Dropbox\\Vie etudiante\\M2\\Stage DGT\\Donnees\\BDM_CNAMTS\\AFM\\"
    table = pd.read_csv(path_data + 'BDM_PRIX.csv', sep=';')
    table['DATE_APPLI'] = table['DATE_APPLI'].map(lambda t : dt.datetime.strptime(t,"%d/%m/%Y").date())
    table['date_appli_str'] = float('NaN')
    for idx in table.index:
        year = str(table.loc[idx, 'DATE_APPLI'].year)
        month = str(0) + str(table.loc[idx, 'DATE_APPLI'].month)
        table.loc[idx, 'date_appli_str'] = float(year + month[-2:])
    return table

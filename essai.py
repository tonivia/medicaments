#-*- coding: utf-8 -*-
'''
Created on 26 juin 2014
'''
#from __future__ import unicode_literals

import pandas as pd
from pdb import set_trace

path_data = "C:\\Users\\Toni\\Dropbox\\Toni Dropbox\\Vie etudiante\\M2\\Stage DGT/Donnees/Medicament/Sniiram/"

def load_sniiram():
    table = pd.read_csv(path_data + 'PHARMA.csv', sep=';')
    table.columns = ['cip13', 'date', 'nb']
    table['nb'] *= 97
    table['year'] = table['date']//100
    #table['cip13'].fillna(1, inplace=True)
    #table = table.pivot(index='cip13', columns='date', values='nb')
    #TODO: redresser après 2011
    return table



if __name__ == '__main__':
    table = load_sniiram()
    table2 = table.loc[table['cip13'].isnull()]
    test = float(sum(table2['nb'])/sum(table['nb']))
    set_trace()
    table2 = table.loc[table['cip13'].isnull()]
    sum(table2['nb'])
    sum(table['nb'])
    test = sum(table2['nb'])/sum(table['nb'])
    #table.drop('year', axis=1, inplace=True)
    print(table.loc[ table['cip13'] == 3400934917547].groupby('year').sum())
    


# tend = pd.DataFrame(index = evolution_princeps.index, columns=('avant', 'apres'))
# for group in tend.index:
#     interet = evolution_princeps[evolution_princeps.index == group]
#     chute = int(chute_brevet1[group])
#     tend.avant[group] = np.mean([interet[month] for month in period[period < chute][1:]])
#     tend.apres[group] = np.mean([interet[month] for month in period[period[1:] > chute]])

#-*- coding: utf-8 -*-
'''
Created on 26 juin 2014
'''
#from __future__ import unicode_literals

import pandas as pd
import tables
from numpy.core.numeric import dtype
import numpy as np
import pdb

path_data = "C:\\Users\\Toni\\Dropbox\\Toni Dropbox\\Vie etudiante\\M2\\Stage DGT\\Donnees\\Medicament\\"

def moulinette(list):
    ''' petite fonction pour avoir des noms de variables plus simples '''
    output = []
    for el in list:
        if 'ombre' in el:
            output += ['nombre']         
        elif 'embours' in el and 'remboursement' not in el:
            output += ['rembourse']            
        elif 'ville' in el:
            output += ['ville']             
        elif 'utres' in el:
            output += ['autres']
        elif 'base' in el or 'Base' in el:
            output += ['base']
    return output

def load_medicam(years, to_hdf=True):

    print('debut chargement de medicam')    
    try: 
        saved = tables.openFile("medicam.h5", "r", driver="H5FD_SEC2", title='Medicam')
        data = saved.root.medicam[:]
        axis1 = saved.root.medicam.attrs.axis1
        assert len([prob for prob in years if prob not in axis1]) == 0
        axis2 = saved.root.medicam.attrs.axis2
        saved.close()
        axis0 = pd.read_hdf("medicam.h5", "axis0")        
        print('depuis hdf5')
    
    except:
        print('depuis excel medicam')
        assert min(years) > 2001
        assert max(years) < 2014
        
        # chargement des données médicam
        path = path_data + "MEDICAM'\\" + 'MEDICAM 2008-2013-ameli.xls'
        medicam = pd.read_excel(path, 1)
        medicam.dropna(inplace=True)
        medicam['CIP7'].replace(u"Homéopathie *", 1, inplace=True)
        medicam['CIP7'] = medicam['CIP7'].astype(int)
       
        if min(years) < 2008:
            path = path_data + "MEDICAM'\\" + 'medicam2002_2007_ameli.xls'
            medicam_02_07 = pd.read_excel(path, 0, sep=";", skiprows=9)
            # retire les MEDICAMENT A 15% NON CODE (2006) pour pouvoir transformer en int 
            medicam_02_07['CIP'][0] = 15 
            medicam_02_07['CIP'] = medicam_02_07['CIP'].astype(int)
            medicam = medicam.merge(medicam_02_07, how='outer', left_on='CIP7', right_on='CIP', suffixes=('','_old'))
            
            col_def_medicament = [col for col in medicam.columns if len(col) < 16] #condition pas très belle mais efficace
            # ne garde qu'une variable en ayant étudié les différences de codage
            names0 = col_def_medicament[:9]
            names1 = col_def_medicament[9:]
            ## Les colonnes ont le bon goût d'être triées de la même façon.
            for k in range(9):
                name0 = names0[k]
                name1 = names1[k]
                cond = medicam[name0].notnull() & medicam[name1].notnull()
                if name0 == 'CIP7':
                    assert( all(medicam[name0][cond] == medicam[name1][cond]))
                    not_in_0 = medicam[name0].isnull()
    #             print name0, name1
    #             print sum(medicam[name0][cond] == medicam[name1][cond])
    #             print sum(medicam[name0][cond] != medicam[name1][cond])
    #             test = medicam[name0][cond] != medicam[name1][cond]
    #             print medicam[name0][cond][test] , medicam[name1][cond][test]
                medicam.loc[not_in_0, name0] = medicam.loc[not_in_0, name1]
            medicam.drop(names1, axis=1, inplace=True)
            print (" ATTENTION ne pas utiliser EphMRA et EmphRA : pas les mêmes codes ni les mêmes noms ")
            print ("on a 22 différence dans les codes ATC et 3 dans ATC2")        
            
        # Travail sur les colonnes
                # Test infructuer de tableau à 3 dimension...
                # dt = np.dtype([('name', np.str_, 16), ('grades', np.float64, (2,))])
        data = np.zeros((len(medicam), len(years), 5)) # cip*year*variable
        new_cols = ['base', 'nombre', 'rembourse', 'ville', 'autres'] 
        for year in years:
            print year
            col_year = [col for col in medicam.columns if str(year) in col]
            table = medicam.loc[:,col_year]
            new_names = moulinette(col_year)
        #     new_cols = [ x + '_' + str(year) for x in new_cols] # si on voulait garder la forme initiale
            table.columns = new_names
            table.reindex_axis(new_cols, axis=1)  #être sûr de l'ordre des variables    
        #     table['year'] = year # si on veut une base de données
            data[:,year-min(years),:] = table.replace(' ', 0).fillna(0)
    
        # on définit les axes du data
        axis0 = medicam.iloc[:,:9] #on n'utilise pas names0 car pas toujours défini 
        axis1 = years
        axis2 = new_cols
        
        if to_hdf:
            h5 = tables.openFile("medicam.h5", "w", driver="H5FD_SEC2", title='Medicam')
            data = h5.createArray("/", "medicam", data)
            data.attrs.axis1 = axis1
            data.attrs.axis2 = axis2
            h5.close()
            axis0.to_hdf("medicam.h5", 'axis0', fmt='t')            
        
    print('fin chargement de medicam')
    return (data, axis0, axis1, axis2)

if __name__ == '__main__':
    years = range(2002,2014)
    output = load_medicam(years)
    
    print('temps initial : ' + str(fin1 - deb1))
    print('temps final : ' + str(fin2 - deb2))    
    
    pdb.set_trace()

# -*- coding:utf-8 -*-
'''
Created on 31 juil. 2014
@author: aeidelman
'''
import numpy as np
import pandas as pd
from pandas import DataFrame

# Fonciton permettant de lire les valeurs dans medicam
def _index_group_medicam(group_id):
    ''' retourne l'indice des médicaments de group_id '''
    list_cip = grp['CIP7'].get_group(group_id)
    select = axis0['CIP7'].isin(list_cip)
    return axis0.index[select].tolist()


def _sum_for_group(group, medicam, years):
    ''' retourne la somme du groupe générique par année'''
    group_id = group['group'].values[0]
    index0 = _index_group_medicam(group_id)
    data = DataFrame(columns=years, index=None)
    data.loc[0, :] = medicam[index0, :].sum(axis=0)
    return data


def sum_by_group(groupby, years, variable):
    ''' retourne une table avec pour chaque group de groupby
      la somme de la variable sur toutes les années de years
    '''
    min_axis1 = min(axis1)
    index1 = [year - min_axis1 for year in years]
    index2 = axis2.index(variable)
    medicam_selected = medicam[:, :, index2]
    medicam_selected = medicam_selected[:, index1]
    output = groupby.apply(_sum_for_group, medicam_selected, years)
    output.set_index(output.index.levels[0], inplace=True)
    return output


def moving_average(table, size=12):
    ''' Calcule les moyennes mobiles de la table sur 12 mois '''
    assert size % 2 == 0
    mid_size = size/2
    output = DataFrame(columns=table.columns, index=table.index)
    for date in range(mid_size, len(table.columns) - mid_size):
        output.iloc[:, date] = table.iloc[:, (date-mid_size+1):(date+mid_size+1)].values.mean(axis=1)
        # les dépenses du mois sont prise en fin de mois
    return output


def evolution(table, period_is_columns=True):
    ''' Mesure l'évolution de période en periode de la table sélectionnée '''
    if period_is_columns:
        period = table.columns
    evolution = pd.DataFrame(index=table.index, columns=period[1:])
    table[table == 0] = float('NaN')
    last_month = table[period[0]]
    for month in period[1:]:
        evolution[month] = (table[month] - last_month)/last_month
        last_month = table[month]
    return evolution


def _basic_linear_regression_(y, retour_serie=True):
    ''' Renvoie la régression linéaire simple de la série par rapport au temps. '''
    condition = y.notnull()
    y = y[condition]
    x = range(len(y))

    length = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    if length > 1:
        sum_x_squared = sum(map(lambda a: a * a, x))
        covariance = sum([x[i] * y.iloc[i] for i in range(length)])

        a = (covariance - (sum_x * sum_y) / length) / (sum_x_squared - ((sum_x ** 2) / length))
        b = (sum_y - a * sum_x) / length
        if retour_serie:
            return a*pd.Series(x, index=y.index) + b
        else:
            return a, b
    else:
        if retour_serie:
            return y
        else:
            return (float('NaN'), float('NaN'))


def application_regression_simple(serie):
    '''Permet d'appliquer le calcul de la régression linéaire simple sur un DataFrame'''
    if all(serie.isnull()):
        return serie
    else:
        output = pd.Series(index=serie.index)
        data = _basic_linear_regression_(serie)
        output.loc[data.index] = data
        return output


def application_regression_rupture(serie, objet_chute):
    '''Permet d'appliquer le calcul de la régression linéaire simple sur un DataFrame
    avec une date de rupture'''
    if all(serie.isnull()):
        return serie
    else:
        output = pd.Series(index=serie.index)
        if isinstance(objet_chute, int):
            chute = objet_chute
        else:
            chute = objet_chute.loc[serie.name]
        before = serie[serie.index < chute]
        after = serie[serie.index > chute]
        data_before = _basic_linear_regression_(before)
        data_after = _basic_linear_regression_(after)
        output.loc[data_before.index] = data_before
        output.loc[data_after.index] = data_after
        return output


#def graphs(group, name_table='nombre'):
#    ''' Créer le plot de comparaison entre princeps et generic '''
#    col0 = eval(name_table + '_princeps').loc[group, :].values
#    col1 = eval(name_table + '_generic').loc[group, :].values
#    col2 = eval(name_table + '_total').loc[group, :].values
#    # TODO: title
#    period_str = [str(t) for t in eval(name_table + '_total').columns]
#    output = DataFrame({'princeps': col0, 'generic': col1, 'total': col2}, index=period_str).plot() 
#    return output


def relative_dates(table, vecteur_date, period=None):
    '''Callage des valeur de la table en fonction d'une date repère (zéro) définie
    pour chaqe groupe dans le vecteur_date'''
    if period is None:
        period = table.columns
    nb_relative_period = 2*len(period)  # le zéro peut être au tout début où à la fin (et est toujours dedans)
    calendrier_relatif = np.ndarray((len(table), nb_relative_period))
    vecteur_date.drop(vecteur_date.index[~vecteur_date.index.isin(table.index)], inplace=True)
    # TODO: avoir le date de chute du brevet en même temps que la table
    for k, month in enumerate(period):
        concern = vecteur_date == month
        debut_de_plage_temps_relatif = len(period) - k
        dbt = debut_de_plage_temps_relatif
        calendrier_relatif[concern.values, dbt:(dbt + len(period))] = table.loc[concern, :].values
    return pd.DataFrame(calendrier_relatif, index=table.index, columns=range(-len(period), len(period)))

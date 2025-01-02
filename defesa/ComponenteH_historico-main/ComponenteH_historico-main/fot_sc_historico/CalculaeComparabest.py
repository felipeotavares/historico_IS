# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:49:59 2024

@author: amanda
"""

import pyIGRF
from pyIGRF import calculate
from datetime import datetime
import numpy as np

#%%
def calcular_coordenadas_magneticas2(estacoes, date):
    """
    Calcula as coordenadas magnéticas e o L-shell para uma lista de estações.

    Parâmetros:
    estacoes (list): Lista de dicionários com latitude, longitude e altitude das estações.
    date (str): Data no formato 'YYYY-MM-DD'.

    Retorna:
    list: Lista de dicionários contendo os valores do campo geomagnético e L-shell para cada estação.
    """
    R_E = 6371.2  # Raio médio da Terra em quilômetros
    B_eq = 3.12e4  # Intensidade do campo magnético equatorial em nanoteslas

    coordenadas_magneticas = []

    for estacao in estacoes:
        lat = estacao['lat']
        lon = estacao['lon']
        alt_km = estacao['alt_km']

        # Converte a data em ano decimal
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        year_decimal = date_obj.year + (date_obj.timetuple().tm_yday - 1) / 365.25

        # Calcula os valores geomagnéticos usando pyIGRF
        D, I, H, X, Y, Z, F = pyIGRF.igrf_value(lat, lon, alt_km, year_decimal)

        # Calcula a intensidade total do campo magnético em nanoteslas
        B_total = (X**2 + Y**2 + Z**2) ** 0.5

        # Calcula o L-shell
        r = R_E + alt_km  # Distância radial em quilômetros
        L_shell = (r / R_E) ** 2 * (B_eq / B_total)

        coordenadas_magneticas.append({
            'nome': estacao['nome'],
            'latitude': estacao['lat'],
            'longitude': estacao['lon'],
            'lat_m': I,  # Latitude magnética
            'Declinação': D,  # Longitude magnética
            'B_total': B_total,
            'L_shell': L_shell
        })

    return coordenadas_magneticas


#%%
date = '2022-05-05'
#TABELACONFERIDA

estacoes = [
    {'nome': 'KHB', 'lat': 47.6100, 'lon': 134.6900, 'alt_km': 0.092}, #Russia
    {'nome': 'NVS', 'lat': 54.8500, 'lon': 83.2300, 'alt_km': 0.130}, #Russia
    {'nome': 'YAK', 'lat': 61.960, 'lon': 129.6600, 'alt_km': 0.100}, #Russia
    {'nome': 'PET', 'lat': 52.9710, 'lon': 158.2480, 'alt_km': 0.100}, #Russia
    {'nome': 'KAK', 'lat': 36.23, 'lon': 140.18, 'alt_km': 0.036}, #Japan
    {'nome': 'KNY', 'lat': 31.42, 'lon': 130.88, 'alt_km': 0.107}, #Japan
    {'nome': 'BMT', 'lat': 40.3000, 'lon': 116.2000, 'alt_km': 0.183}, #China
    {'nome': 'CYG', 'lat': 36.3700, 'lon': 126.8540, 'alt_km': 0.165}, #Korea
    {'nome': 'ABG', 'lat': 18.62, 'lon': 72.87, 'alt_km': 0.007}, #ITALIA
    {'nome': 'DUR', 'lat': 41.35, 'lon': 14.46, 'alt_km': 0.920}, #ITALIA
    {'nome': 'SJG', 'lat': 18.11, 'lon': 293.85, 'alt_km': 0.424}, #EUA
    {'nome': 'TUC', 'lat': 32.17, 'lon': -110.91, 'alt_km': 0.447}, #Eua
    {'nome': 'SHU', 'lat': 55.3500, 'lon': -160.4600, 'alt_km': 0.080}, #Eua
    {'nome': 'FRD', 'lat': 38.2100, 'lon': -77.3670, 'alt_km': 0.069},  #eua
    {'nome': 'GUI', 'lat': 28.32, 'lon': -16.43, 'alt_km': 0.289}, #SPAIN
    {'nome': 'ASC', 'lat': -7.95, 'lon': -14.38, 'alt_km': 0.859}, #United Kingdom
    {'nome': 'BLC', 'lat': 64.318, 'lon': -96.012, 'alt_km': 0.030}, #canada
    {'nome': 'OTT', 'lat': 45.42, 'lon': -75.92, 'alt_km': 0.075}, #Canada
    {'nome': 'MEA', 'lat': 54.616, 'lon': -113.3470, 'alt_km': 0.700}, #CANADA
    {'nome': 'IQA', 'lat': 63.7530, 'lon': -68.5180, 'alt_km': 0.067}, #Canada
    {'nome': 'OTT', 'lat': 45.4030, 'lon': -75.5520, 'alt_km': 0.075}, #canada
    {'nome': 'WNG', 'lat': 53.725, 'lon': 9.0530, 'alt_km': 0.066}, #Germany
    {'nome': 'NGK', 'lat': 52.0700, 'lon': 12.6800, 'alt_km': 0.078},  #Germany
    {'nome': 'MAB', 'lat': 50.2980, 'lon': 5.6820, 'alt_km': 0.440},  #Belgica
    {'nome': 'DOU', 'lat': 50.1000, 'lon': 4.6000, 'alt_km': 0.225},  #Belgica
    {'nome': 'CLF', 'lat': 48.0250, 'lon': 2.2600, 'alt_km': 0.145},  #Franca
    {'nome': 'LYC', 'lat': 64.6120, 'lon': 18.7480, 'alt_km': 0.270},  #Suécia
    {'nome': 'UPS', 'lat': 59.9030, 'lon': 17.3530, 'alt_km': 0.050},  #Suécia
    {'nome': 'WIC', 'lat': 47.9305, 'lon': 15.8657, 'alt_km': 1.088},  #Austria
    {'nome': 'CNB', 'lat': -35.30, 'lon': 149.13, 'alt_km': 0.859}, #Australia
    {'nome': 'KDU', 'lat': -12.69, 'lon': 132.47, 'alt_km': 0.140}, #Australia
    {'nome': 'ASP', 'lat': -23.77, 'lon': 133.88, 'alt_km': 0.557}, #Australia
    {'nome': 'ASP', 'lat': -54.5000, 'lon': 158.9500, 'alt_km': 0.004}, #Australia
    {'nome': 'EYR', 'lat': -43.4740, 'lon': 172.3930, 'alt_km': 0.102}, #Australia
    {'nome': 'BOA', 'lat': 2.800556, 'lon': -60.675833, 'alt_km': 0.090}, #Brazil
    {'nome': 'MAN', 'lat':-2.888333, 'lon': -59.969722, 'alt_km': 0.092}, #Brazil
    {'nome': 'SJC', 'lat':-23.208611, 'lon': -45.963611, 'alt_km': 0.600}, #Brazil
    {'nome': 'CXP', 'lat':-22.701944, 'lon': -45.014444, 'alt_km': 0.521}, #Brazil
    {'nome': 'SMS', 'lat': -29.44, 'lon': 306.18, 'alt_km': 0.453}, #Brazil
    {'nome': 'TTB', 'lat': -1.2050, 'lon':  -48.5130, 'alt_km': 0.010}, #brasil
    {'nome': 'PIL', 'lat': -31.6670, 'lon': -63.8810, 'alt_km': 0.336}, #Argentina
    {'nome': 'HBK', 'lat': -25.8800, 'lon': 27.7100, 'alt_km': 1.555}, #SouthAfrica
    {'nome': 'HER', 'lat':-34.43, 'lon': 19.23, 'alt_km': 0.026}, #SouthAfrica
    {'nome': 'KMH', 'lat': -26.54, 'lon': 18.11, 'alt_km': 1.003},  #SouthAfrica
    {'nome': 'BNG', 'lat': 4.3300, 'lon': 18.11, 'alt_km': 0.395},  #centralAfrica
   
]



#%%
coordenadasmagneticas = calcular_coordenadas_magneticas2(estacoes, date)



#%%

def encontrar_estacoes_proximas(estacao_entrada, coordenadasmagneticas, limite=0.2):
    """
    Encontra estações com L-shell próximo ao da estação de entrada e no hemisfério oposto.

    Parâmetros:
    - estacao_entrada (str): Nome da estação de entrada.
    - todas_estacoes (list): Lista de dicionários contendo todas as estações e seus L-shells.
    - limite (float): Limite de diferença aceitável entre os L-shells.

    Retorna:
    - list: Lista de dicionários das estações próximas e no hemisfério oposto.
    """
    estacao_entrada_lshell = None
    estacao_entrada_lat = None

    # Encontrar o L-shell e a latitude da estação de entrada
    for estacao in coordenadasmagneticas:
        if estacao['nome'] == estacao_entrada:
            estacao_entrada_lshell = estacao['L_shell']
            estacao_entrada_lat = estacao['lat_m']
            break

    # Verificar se a estação de entrada foi encontrada
    if estacao_entrada_lshell is None or estacao_entrada_lat is None:
        print(f"Estação '{estacao_entrada}' não encontrada.")
        return []

    # Encontrar estações próximas e no hemisfério oposto
    estacoes_proximas = []
    for estacao in coordenadasmagneticas:
        if abs(estacao['L_shell'] - estacao_entrada_lshell) <= limite and \
           (estacao['lat_m'] > 0) != (estacao_entrada_lat > 0):
            estacoes_proximas.append(estacao)

    return estacoes_proximas

# Exemplo de uso
estacao_entrada = 'SJG'
estacoes_proximas = encontrar_estacoes_proximas(estacao_entrada, coordenadasmagneticas)

# Exibir estações próximas e no hemisfério oposto
print(f"Estações próximas e no hemisfério oposto à '{estacao_entrada}':")
for estacao in estacoes_proximas:
    print(f"Nome: {estacao['nome']}, L-shell: {estacao['L_shell']}, Latitude: {estacao['lat_m']}")

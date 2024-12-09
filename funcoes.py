# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:54 2024

@author: felip
"""

import pandas as pd
import os
import numpy as np
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from scipy.optimize import curve_fit
import warnings
import io
import csv

# Configurações e informações de estações
stations_info = {
    "BOA": {"lat": 2.800556, "lon": -60.675833, "city": "Boa Vista", 'local': "Embrace"},
    "MAN": {"lat": -2.888333, "lon": -59.969722, "city": "Manaus", 'local': "Embrace"},
    "PVE": {"lat": -8.763611, "lon": -63.906389, "city": "Porto Velho", 'local': "Embrace"},
    "BLM": {"lat": -1.441111, "lon": -48.444444, "city": "Belém", 'local': "Embrace"},
    "SLZ": {"lat": -2.594167, "lon": -44.209722, "city": "São Luís", 'local': "Embrace"},
    "ALF": {"lat": -9.870278, "lon": -56.104167, "city": "Alta Floresta", 'local': "Embrace"},
    "ARA": {"lat": -5.600278, "lon": -48.100556, "city": "Araguaína", 'local': "Embrace"},
    "EUS": {"lat": -3.880000, "lon": -38.424444, "city": "Fortaleza", 'local': "Embrace"},
    "PAL": {"lat": -10.297222, "lon": -48.361389, "city": "Palmas", 'local': "Embrace"},
    "CBA": {"lat": -15.554722, "lon": -56.069444, "city": "Cuiabá", 'local': "Embrace"},
    "CRR": {"lat": -7.389167, "lon": -36.539167, "city": "Caruaru", 'local': "Embrace"},
    "JAT": {"lat": -17.931944, "lon": -51.718056, "city": "Jataí", 'local': "Embrace"},
    "CGR": {"lat": -20.506667, "lon": -54.617778, "city": "Campo Grande",'local': "Embrace"},
    "TCM": {"lat": -26.822222, "lon": -65.194444, "city": "Termas de Río Hondo",'local': "Embrace"},
    "MED": {"lat": -25.295278, "lon": -54.093889, "city": "Medianeira",'local': "Embrace"},
    "CXP": {"lat": -22.701944, "lon": -45.014444, "city": "Caraguatatuba",'local': "Embrace"},
    "SJC": {"lat": -23.208611, "lon": -45.963611, "city": "São José dos Campos",'local': "Embrace"},
    "VSS": {"lat": -22.402778, "lon": -43.652222, "city": "Volta Redonda",'local': "Embrace"},
    "SMS": {"lat": -29.443611, "lon": -53.822778, "city": "São Martinho da Serra",'local': "Embrace"},
    "SJG": {"lat": 18.11, "lon": -66.15, "city": "San Juan",'local': "Intermag"},
    "ASC": {"lat": -7.9, "lon": -14.4, "city": "Ascension Island",'local': "Intermag"},
    "GUI": {"lat": 28.3, "lon": -16.4, "city": "Guimar",'local': "Intermag"},
    "DUR": {"lat": 41.4, "lon": 14.3, "city": "Duronia",'local': "Intermag"},
    "KMH": {"lat": -26.5, "lon": 18.1, "city": "Keetmanshoop",'local': "Intermag"},
    "BRW" :  {"lat": 71.3, "lon": -156, "city": "Barrow",'local': "Intermag"},
    "YKC" :  {"lat": 62.4, "lon": -114.37, "city": "Yellowknife",'local': "Intermag"},
    "PQB" :  {"lat": 55.3, "lon": -78, "city": "Yellowknife",'local': "Intermag"},#Auroral
    "HBA" :  {"lat": -75.5, "lon": -25.5, "city": "Halley Bay",'local': "Agonet"}, #auroral
    "THL" :  {"lat": 77.47, "lon": -69.227, "city": "Thule",'local': "Intermag"}, #polar
    "OTT" :  {"lat": 45.4, "lon":-75.6227, "city": "Ottawa",'local': "Intermag"}, #auroral
    "NAQ" :  {"lat": 61.167, "lon": -45.433, "city": "Narsarsuaq",'local': "Intermag"},#auroral 
    "ABG" :  {"lat": 18.62, "lon": 72.87 , "city": "Alibag",'local': "Intermag"}, #media
    "GAN" :  {"lat": 0.69, "lon": 73.15 , "city": "Alibag",'local': "Intermag"},
    "KNY" :  {"lat": 31.42, "lon": 130.88, "city": "Kanoya",'local': "Intermag"},#mesmo Lshell SMS
    "KDU" :  {"lat": -12.69, "lon": 132.47, "city": "Kakadu",'local': "Intermag"}#mesmo Lshell SMS    
}

def find_header(file_path):
    station_name = os.path.basename(file_path)[:3].upper()
    line_count, kind = 0, np.nan
    
    with open(file_path, 'r') as file:
        for line in file:
            if "Reported" in line:
                kind = "HDZF" if "HDZF" in line else "XYZF"
            elif line.startswith('DATE') or line.startswith(' DD MM YYYY'):
                kind = 'EMBRACE' if line.startswith(' DD MM YYYY') else kind
                break
            line_count += 1
    
    return station_name, line_count, kind

def process_data(file_path):
    station_name, header_lines, kind = find_header(file_path)
    df = pd.read_csv(file_path, skiprows=header_lines, sep='\s+')

    if kind == "HDZF" or kind == "XYZF":
        df['TIME'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'])
        df['TIME'] = df['TIME'].dt.hour + df['TIME'].dt.minute / 60 + df['TIME'].dt.second / 3600
        if kind == "XYZF":
            df[f'{station_name}H'] = np.sqrt(df[f'{station_name}X']**2 + df[f'{station_name}Y']**2)
        df[f'{station_name}H1'] = df[f'{station_name}H'] - df[f'{station_name}H'][0]
        df['H_nT'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H1'])
    elif kind == 'EMBRACE':
        df['DATE'] = pd.to_datetime(df['YYYY'].astype(str) + '-' + df['MM'].astype(str) + '-' + df['DD'].astype(str))
        df['TIME'] = pd.to_timedelta(df['HH'], unit='h') + pd.to_timedelta(df['MM.1'], unit='m')
        df['DATETIME'] = pd.to_datetime(df['DATE'] + df['TIME'])
        df['TIME'] = df['DATETIME'].dt.hour + df['DATETIME'].dt.minute / 60 + df['DATETIME'].dt.second / 3600
        df[f'{station_name}H'] = df['H(nT)'] - df['H(nT)'][0]
        df['H_nT'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H'])

    df['dH_nT'] = df['H_nT'].diff()
    return df[['TIME', 'H_nT', 'dH_nT']], station_name

def get_filtered_solar_flux_data():
    url = 'https://spaceweather.gc.ca/solar_flux_data/daily_flux_values/fluxtable.txt'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        df = pd.read_csv(io.StringIO(data), delim_whitespace=True, skiprows=1)
        df.columns = ['FluxDate', 'FluxTime', 'FluxJulian', 'CarringtonRot', 'ObsFlux', 'AdjFlux', 'Urs']
        df['Date'] = pd.to_datetime(df['FluxDate'], format='%Y%m%d', errors='coerce')
        filtered_data = df[(df['Date'] >= '2019-01-01') & (df['Date'] <= '2024-12-31') & (df['ObsFlux'] <= 300)].dropna(subset=['Date'])
        filtered_data['SmoothedObsFlux'] = filtered_data['ObsFlux'].rolling(window=30).mean()
        return filtered_data
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Erro: {e}")
        return None

def download_sc_dates(years, save_folder):
    if not isinstance(years, list):
        raise ValueError("O argumento 'years' deve ser uma lista de anos.")
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    for year in years:
        url = f"https://www.obsebre.es/php/geomagnetisme/vrapides/ssc_{year}_p.txt"
        file_name = url.split("/")[-1]
        file_path = os.path.join(save_folder, file_name)
        if os.path.exists(file_path):
            print(f"[{file_name}] Already on the disk")
            continue
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"[{file_name}] Downloaded")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download [{file_name}]. Error: {e}")

def download_embrace(files_folder, date_str, station):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    date = datetime.strptime(date_str, "%Y-%m-%d")
    d = date.strftime('%Y%m%d')
    folder_save = os.path.join(files_folder, 'Dados', d)
    
    if not os.path.exists(folder_save):
        os.makedirs(folder_save)

    base_url = "https://embracedata.inpe.br/magnetometer/"
    variable_url = f"{station}/{date.year}/"
    final_url = urljoin(base_url, variable_url)
    
    response = requests.get(final_url, verify=False)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a'):
        file_name = link.get('href')
        if file_name == "../" or not file_name.endswith(f'.{date.year % 100}m'):
            continue
        
        wanted_date = date.strftime("%d%b").lower()
        file_date = file_name[3:8]

        if wanted_date == file_date:
            local_file_path = os.path.join(folder_save, file_name)
            if os.path.exists(local_file_path):
                print(f"[{file_name}] Already on the disk")
            else:
                file_url = urljoin(final_url, file_name)
                print(f"[{file_name}] Downloaded")
                with open(local_file_path, 'wb') as file:
                    file_response = requests.get(file_url, verify=False)
                    file.write(file_response.content)

def intermagnet_download(files_folder, date_str, station):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    d = date.strftime('%Y%m%d')
    url = "https://imag-data.bgs.ac.uk/GIN_V1/GINServices"
    params = {
        "Request": "GetData",
        "format": "Iaga2002",
        "testObsys": 0,
        "observatoryIagaCode": station,
        "samplesPerDay": "minute",
        "publicationState": "Best available",
        "dataStartDate": date_str,
        "dataDuration": 1
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.text
        save_folder = os.path.join(files_folder, 'Dados', d)
        file_name = f'{station.lower()}{d}vmin.min'
        full_save_path = os.path.join(save_folder, file_name)
        
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        if os.path.exists(full_save_path):
            print(f"[{file_name}] Already on the disk")
        else:
            with open(full_save_path, "w") as file:
                file.write(data)
            print(f"[{file_name}] Downloaded")

def download_files(files_folder, dates, stations):
    for date_str in dates:
        for station in stations:
            local = stations_info[station]['local']
            date = datetime.strptime(date_str, "%Y-%m-%d")
            folder_save = os.path.join(files_folder, 'Dados', date.strftime('%Y%m%d'))
            
            if not os.path.exists(folder_save):
                os.makedirs(folder_save)
            
            if local == 'Embrace':
                file_name = f'{station.lower()}{date.strftime("%Y%m%d")}.min'
                local_file_path = os.path.join(folder_save, file_name)
                if os.path.exists(local_file_path):
                    print(f"[{file_name}] Already on disk")
                else:
                    download_embrace(files_folder, date_str, station)
            elif local == 'Intermag':
                file_name = f'{station.lower()}{date.strftime("%Y%m%d")}vmin.min'
                local_file_path = os.path.join(folder_save, file_name)
                if os.path.exists(local_file_path):
                    print(f"[{file_name}] Already on disk")
                else:
                    intermagnet_download(files_folder, date_str, station)

def read_data_eventos(filename):
    column_names = [
        'DATE', 'TIME', 'DOY', 'MDUR', 'MAMP', 'CODES', 'TYPE',
        'OBSERVATORIES', 'DURATION', 'AMPLITUDE'
    ]
    data = []
    with open(filename, 'r') as file:
        reader = csv.reader(file, delimiter=' ', skipinitialspace=True)
        for _ in range(27):
            next(reader)
        
        for row in reader:
            if len(row) < 26:
                continue
            date, time, doy, mdur, mamp = row[:5]
            try:
                doy = int(doy)
                mdur, mamp = float(mdur), float(mamp)
            except ValueError:
                continue
            
            codes, event_type = row[5:10], row[10]
            observatories, durations, amplitudes = row[11:16], row[16:21], row[21:26]
            data.append([date, time, doy, mdur, mamp, codes, event_type, observatories, durations, amplitudes])

    df = pd.DataFrame(data, columns=column_names)
    for col, cols in zip(['CODES', 'OBSERVATORIES', 'DURATION', 'AMPLITUDE'], 
                         [['CODES_1', 'CODES_2', 'CODES_3', 'CODES_4', 'CODES_5'],
                          ['OBSERVATORY_1', 'OBSERVATORY_2', 'OBSERVATORY_3', 'OBSERVATORY_4', 'OBSERVATORY_5'],
                          ['DURATION_1', 'DURATION_2', 'DURATION_3', 'DURATION_4', 'DURATION_5'],
                          ['AMPLITUDE_1', 'AMPLITUDE_2', 'AMPLITUDE_3', 'AMPLITUDE_4', 'AMPLITUDE_5']]):
        df[cols] = pd.DataFrame(df[col].tolist(), index=df.index)
        df.drop(columns=[col], inplace=True)

    return df

def get_events_dates(folder):
    all_data = []
    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path) and not file_path.endswith('.ini'):
            hora_especifica = read_data_eventos(file_path)
            hora_especifica['TIME'] = hora_especifica['TIME'].apply(time_to_decimal_24)
            all_data.append(hora_especifica)

    combined_data = pd.concat(all_data, ignore_index=True)
    lista_datas = combined_data[['DATE', 'TIME']].drop_duplicates().rename(columns={'DATE': 'Data', 'TIME': 'Hora'})
    
    return lista_datas

def time_to_decimal_24(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M:%S.%f').time()
    decimal_time = time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600 + time_obj.microsecond / 3600000000
    return decimal_time

def sigmoid(x, L, x0, k, b):
    return L / (1 + np.exp(-k * (x - x0))) + b

def caract_ajuste(dados_janela, coluna):
    x_data = np.arange(len(dados_janela))
    y_data = dados_janela[coluna].values
    y_data = pd.Series(y_data).interpolate().ffill().bfill().values
    mask = ~np.isinf(y_data)
    x_data = x_data[mask]
    y_data = y_data[mask]

    if len(x_data) < 2 or np.isnan(y_data).all():
        return np.full(len(dados_janela), np.nan), np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    p0 = [max(y_data), np.median(x_data), 1, min(y_data)]
    try:
        with warnings.catch_warnings():
            params, _ = curve_fit(sigmoid, x_data, y_data, p0, method='dogbox', maxfev=10000)
        L, x0, k, b = params
        y_fit = sigmoid(x_data, L, x0, k, b)
        max_idx = np.argmax(y_fit)
        min_idx = np.argmin(y_fit)
        posicao_esquerda = dados_janela.iloc[min_idx]['TIME']
        posicao_direita = dados_janela.iloc[max_idx]['TIME']
        ponto_esquerda = [posicao_esquerda, y_fit[min_idx]]
        ponto_direita = [posicao_direita, y_fit[max_idx]]
        residual = np.sum((y_data - sigmoid(x_data, *params))**2)
        ss_res = np.sum((y_data - y_fit)**2)
        ss_tot = np.sum((y_data - np.mean(y_data))**2)
        r_squared = 1 - (ss_res / ss_tot)
        rmse = np.sqrt(np.mean((y_data - y_fit)**2))
    except (RuntimeError, ValueError):
        return np.full(len(dados_janela), np.nan), np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    return y_fit, L, ponto_esquerda, ponto_direita, residual, r_squared, rmse

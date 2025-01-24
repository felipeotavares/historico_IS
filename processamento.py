# -*- coding: utf-8 -*-
"""
Created on Thu May 23 17:00:33 2024

@author: felip
"""

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import os
import numpy as np
# from scipy.signal import butter, lfilter  # Para pulsação
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# from scipy.signal import filtfilt
from scipy.optimize import curve_fit
# from scipy.optimize import OptimizeWarning
import warnings
# from matplotlib.dates import DateFormatter, DayLocator
# import matplotlib.dates as mdates
import seaborn as sns
from datetime import timedelta
# import matplotlib.pyplot as plt
# from matplotlib.dates import DateFormatter, DayLocator
import pandas as pd
import io
import pickle
# import numpy as np
import pywt
import pandas as pd
import ast
import pyIGRF
import math


from scipy.signal import butter, filtfilt
import pandas as pd

# Caminho para o arquivo txt contendo os dados das estações
# file_path = 'stations_data.txt'
file_path = 'stations_data_with_elevation.txt'
# Função para carregar o conteúdo do arquivo como um dicionário
with open(file_path, 'r') as file:
    data = file.read()

# Converte o conteúdo do arquivo para um dicionário
stations_info = ast.literal_eval('{' + data + '}')


#%% infos
# stations_info = {
#     "BOA": {"lat": 2.800556, "lon": -60.675833, "city": "Boa Vista", 'local': "Embrace"},
#     "MAN": {"lat": -2.888333, "lon": -59.969722, "city": "Manaus", 'local': "Embrace"},
#     "PVE": {"lat": -8.763611, "lon": -63.906389, "city": "Porto Velho", 'local': "Embrace"},
#     "BLM": {"lat": -1.441111, "lon": -48.444444, "city": "Belém", 'local': "Embrace"},
#     "SLZ": {"lat": -2.594167, "lon": -44.209722, "city": "São Luís", 'local': "Embrace"},
#     "ALF": {"lat": -9.870278, "lon": -56.104167, "city": "Alta Floresta", 'local': "Embrace"},
#     "ARA": {"lat": -5.600278, "lon": -48.100556, "city": "Araguaína", 'local': "Embrace"},
#     "EUS": {"lat": -3.880000, "lon": -38.424444, "city": "Fortaleza", 'local': "Embrace"},
#     "PAL": {"lat": -10.297222, "lon": -48.361389, "city": "Palmas", 'local': "Embrace"},
#     "CBA": {"lat": -15.554722, "lon": -56.069444, "city": "Cuiabá", 'local': "Embrace"},
#     "CRR": {"lat": -7.389167, "lon": -36.539167, "city": "Caruaru", 'local': "Embrace"},
#     "JAT": {"lat": -17.931944, "lon": -51.718056, "city": "Jataí", 'local': "Embrace"},
#     "CGR": {"lat": -20.506667, "lon": -54.617778, "city": "Campo Grande",'local': "Embrace"},
#     "TCM": {"lat": -26.822222, "lon": -65.194444, "city": "Termas de Río Hondo",'local': "Embrace"},
#     "MED": {"lat": -25.295278, "lon": -54.093889, "city": "Medianeira",'local': "Embrace"},
#     "CXP": {"lat": -22.701944, "lon": -45.014444, "city": "Caraguatatuba",'local': "Embrace"},
#     "SJC": {"lat": -23.208611, "lon": -45.963611, "city": "São José dos Campos",'local': "Embrace"},
#     "VSS": {"lat": -22.402778, "lon": -43.652222, "city": "Volta Redonda",'local': "Embrace"},
#     "SMS": {"lat": -29.443611, "lon": -53.822778, "city": "São Martinho da Serra",'local': "Embrace"},
#     "SJG": {"lat": 18.11, "lon": -66.15, "city": "San Juan",'local': "Intermag"},
#     "ASC": {"lat": -7.9, "lon": -14.4, "city": "Ascension Island",'local': "Intermag"},
#     "GUI": {"lat": 28.3, "lon": -16.4, "city": "Guimar",'local': "Intermag"},
#     "DUR": {"lat": 41.4, "lon": 14.3, "city": "Duronia",'local': "Intermag"},
#     "KMH": {"lat": -26.5, "lon": 18.1, "city": "Keetmanshoop",'local': "Intermag"},
#     "BRW" :  {"lat": 71.3, "lon": -156, "city": "Barrow",'local': "Intermag"},
#     "YKC" :  {"lat": 62.4, "lon": -114.37, "city": "Yellowknife",'local': "Intermag"},
#     "PQB" :  {"lat": 55.3, "lon": -78, "city": "Yellowknife",'local': "Intermag"},#Auroral
#     "HBA" :  {"lat": -75.5, "lon": -25.5, "city": "Halley Bay",'local': "Agonet"}, #auroral
#     "THL" :  {"lat": 77.47, "lon": -69.227, "city": "Thule",'local': "Intermag"}, #polar
#     "OTT" :  {"lat": 45.4, "lon":-75.6227, "city": "Ottawa",'local': "Intermag"}, #auroral
#     "NAQ" :  {"lat": 61.167, "lon": -45.433, "city": "Narsarsuaq",'local': "Intermag"},#auroral 
#     "ABG" :  {"lat": 18.62, "lon": 72.87 , "city": "Alibag",'local': "Intermag"}, #media
#     "GAN" :  {"lat": 0.69, "lon": 73.15 , "city": "Alibag",'local': "Intermag"},
#     "KNY" :  {"lat": 31.42, "lon": 130.88, "city": "Kanoya",'local': "Intermag"},#mesmo Lshell SMS
#     "KDU" :  {"lat": -12.69, "lon": 132.47, "city": "Kakadu",'local': "Intermag"}#mesmo Lshell SMS    
# }

# %% level 0 process
def find_header(file_path):
    station_name = os.path.basename(file_path)[:3].upper()
    line_count, kind = 0, np.nan  # Inicializa kind com np.nan
    
    with open(file_path, 'r') as file:
        for line in file:
            if " Reported               HDZF" in line:
                kind = "HDZF"
            elif " Reported               XYZF" in line:
                kind = "XYZF"
            elif " Reported               XYZG" in line:
                kind = "XYZG"
            elif line.startswith('DATE') or line.startswith(' DD MM YYYY'):
                if line.startswith(' DD MM YYYY'):
                    kind = 'EMBRACE'
                break
            line_count += 1
    
    return station_name, line_count, kind

# def process_data(file_path):
#     try:
#         # Tenta encontrar o cabeçalho e o tipo de arquivo
#         try:
#             station_name, header_lines, kind = find_header(file_path)
#         except Exception as e:
#             return None, None

#         # Tenta ler o arquivo CSV
#         try:
#             df = pd.read_csv(file_path, skiprows=header_lines, sep='\s+')
#         except pd.errors.EmptyDataError:
#             return None, None
#         except FileNotFoundError:
#             return None, None
#         except Exception as e:
#             return None, None

#         # Processamento de acordo com o tipo de arquivo identificado
#         try:
#             if kind == "HDZF" or kind == "XYZF":
#                 df['TIME'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'], errors='coerce')
#                 df['TIME'] = df['TIME'].dt.hour + df['TIME'].dt.minute / 60 + df['TIME'].dt.second / 3600

#                 if kind == "XYZF":
#                     df[f'{station_name}H'] = np.sqrt(df[f'{station_name}X']**2 + df[f'{station_name}Y']**2)

#                 df[f'{station_name}H1'] = df[f'{station_name}H'] - df[f'{station_name}H'][0]
#                 df['H_nT'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H1'])

#             elif kind == 'EMBRACE':
#                 df['DATE'] = pd.to_datetime(df['YYYY'].astype(str) + '-' + df['MM'].astype(str) + '-' + df['DD'].astype(str), errors='coerce')
#                 df['TIME'] = pd.to_timedelta(df['HH'], unit='h') + pd.to_timedelta(df['MM.1'], unit='m')
#                 df['DATETIME'] = df['DATE'] + df['TIME']
#                 df['TIME'] = df['DATETIME'].dt.hour + df['DATETIME'].dt.minute / 60 + df['DATETIME'].dt.second / 3600

#                 df[f'{station_name}H'] = df['H(nT)'] - df['H(nT)'][0]
#                 df['H_nT'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H'])
#             else:
#                 return None, None
#         except KeyError as e:
#             return None, None
#         except Exception as e:
#             return None, None

#         # Tenta detectar anomalias e calcular a diferença
#         try:
#             df = detectar_anomalias(df)
#             df['dH_nT'] = df['H_nT'].diff()
#         except Exception as e:
#             return None, None

#         return df[['TIME', 'H_nT', 'dH_nT']], station_name

#     except Exception as e:
#         return None, None
def process_data(file_path):
    try:
        # Tenta encontrar o cabeçalho e o tipo de arquivo
        try:
            station_name, header_lines, kind = find_header(file_path)
        except Exception as e:
            return None, None

        # Tenta ler o arquivo CSV
        try:
            df = pd.read_csv(file_path, skiprows=header_lines, sep='\s+')
        except pd.errors.EmptyDataError:
            return None, None
        except FileNotFoundError:
            return None, None
        except Exception as e:
            return None, None

        # Processamento de acordo com o tipo de arquivo identificado
        try:
            if kind == "HDZF" or kind == "XYZF" or kind == "XYZG":
                df['TIME'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'], errors='coerce')
                df['TIME'] = df['TIME'].dt.hour + df['TIME'].dt.minute / 60 + df['TIME'].dt.second / 3600
                # print(kind)
                if kind == "XYZF":
                    # Calcula a componente H
                    df[f'{station_name}H'] = np.sqrt(df[f'{station_name}X']**2 + df[f'{station_name}Y']**2)
                    df[f'{station_name}D'] = np.arctan2(df[f'{station_name}Y'], df[f'{station_name}X'])* (180 / np.pi) * 60  #converte de rad para arc min
                if kind == "XYZG":
                    # Calcula a componente H
                    df[f'{station_name}H'] = np.sqrt(df[f'{station_name}X']**2 + df[f'{station_name}Y']**2)
                    df[f'{station_name}D'] = np.arctan2(df[f'{station_name}Y'], df[f'{station_name}X'])* (180 / np.pi) * 60  #converte de rad para arc min
                    df[f'{station_name}F'] = np.sqrt(df[f'{station_name}X']**2 + df[f'{station_name}Y']**2 + df[f'{station_name}Z']**2)
                # coloca o primeiro dado da serie como o "zero" (ajuste de offset)
           
                df['H_nT'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H'])
                df['D_deg'] = np.where(df[f'{station_name}D'] > 99999, np.nan, df[f'{station_name}D']/60) #converte de arc min para deg
                df['Z_nT'] = np.where(df[f'{station_name}Z'] > 99999, np.nan, df[f'{station_name}Z'])
                
                # campo normalizado com componente F
                df['H_nT_norm'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H']/df[f'{station_name}F'])
                # campo sem ajuste de offset
                df['H_nT_source'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H'])

            elif kind == 'EMBRACE':
                df['DATE'] = pd.to_datetime(df['YYYY'].astype(str) + '-' + df['MM'].astype(str) + '-' + df['DD'].astype(str), errors='coerce')
                df['TIME'] = pd.to_timedelta(df['HH'], unit='h') + pd.to_timedelta(df['MM.1'], unit='m')
                df['DATETIME'] = df['DATE'] + df['TIME']
                df['TIME'] = df['DATETIME'].dt.hour + df['DATETIME'].dt.minute / 60 + df['DATETIME'].dt.second / 3600

                df[f'{station_name}H'] = df['H(nT)']
                df[f'{station_name}D'] = df['D(Deg)'] 
                df[f'{station_name}Z'] = df['Z(nT)']
                df['H_nT'] = np.where(df[f'{station_name}H'] > 99999, np.nan, df[f'{station_name}H'])
                df['D_deg'] = np.where(df[f'{station_name}D'] > 99999, np.nan, df[f'{station_name}D'])
                df['Z_nT'] = np.where(df[f'{station_name}Z'] > 99999, np.nan, df[f'{station_name}Z'])
                
                # campo normalizado com componente F
                df['H_nT_norm'] = np.where(df['H(nT)'] > 99999, np.nan, df['H(nT)']/df['F(nT)'])
                # campo sem ajuste de offset
                df['H_nT_source'] = np.where(df['H(nT)'] > 99999, np.nan, df['H(nT)'])

            else:
                return None, None
        except KeyError as e:
            return None, None
        except Exception as e:
            return None, None

        # Tenta detectar anomalias e calcular a diferença
        try:
            # df = detectar_anomalias(df,colunas=['H_nT'])
            df['dH_nT'] = df['H_nT'].diff()
            df['dD_deg'] = df['D_deg'].diff()
            df['dZ_nT'] = df['Z_nT'].diff()
                        
        except Exception as e:
            return None, None

        return df[['TIME','H_nT_source', 'H_nT_norm','H_nT', 'dH_nT', 'D_deg','dD_deg','Z_nT', 'dZ_nT']], station_name

    except Exception as e:
        return None, None


def detectar_anomalias(df, colunas=['H_nT']):
    """
    Detecta anomalias em um DataFrame e substitui por NaN.
    Utiliza o desvio interquartil (IQR) para detectar valores extremos.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados a serem analisados.
        colunas (list, opcional): Lista de colunas para verificar anomalias. Se None, aplica a todas as colunas numéricas.

    Retorna:
        pd.DataFrame: DataFrame com anomalias substituídas por NaN.
    """
    df_anomalias = df.copy()
    for coluna in colunas:
        # Calcula os quartis e o IQR
        Q1 = df[coluna].quantile(0.25)
        Q3 = df[coluna].quantile(0.75)
        IQR = Q3 - Q1

        # Define os limites para detecção de anomalias
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR

        # Substitui os valores fora dos limites por NaN
        df_anomalias[coluna] = df[coluna].where((df[coluna] >= limite_inferior) & (df[coluna] <= limite_superior), np.nan)

    return df_anomalias
# %% Data download -não esta retornando os arquivos corretos, url pode estar errada
def get_filtered_solar_flux_data():
    """
    Faz o download dos dados diários do fluxo solar F10.7, filtra para o período de 2019 a 2024,
    remove linhas com datas inválidas e valores acima de 300 sfu, e aplica suavização com média móvel.
    
    Returns:
        filtered_data (DataFrame): Dados filtrados e suavizados do fluxo solar F10.7.
    """
    # URL dos dados diários do fluxo solar F10.7
    url = 'https://spaceweather.gc.ca/solar_flux_data/daily_flux_values/fluxtable.txt'

    try:
        # Fazer o download dos dados
        response = requests.get(url)
        response.raise_for_status()  # Verifica se houve algum erro na requisição

        # Ler o conteúdo como texto e carregar em um DataFrame
        data = response.text

        # Processar o conteúdo para criar um DataFrame
        df = pd.read_csv(io.StringIO(data), delim_whitespace=True, skiprows=1)

        # Ajustar os nomes das colunas conforme necessário
        df.columns = ['FluxDate', 'FluxTime', 'FluxJulian', 'CarringtonRot', 'ObsFlux', 'AdjFlux', 'Urs']

        # Criar uma coluna de data usando o FluxDate
        df['Date'] = pd.to_datetime(df['FluxDate'], format='%Y%m%d', errors='coerce')

        # Filtrar os dados para o período de 2019 a 2024, remover linhas com datas inválidas e valores acima de 300 sfu
        filtered_data = df[(df['Date'] >= '2015-01-01') & (df['Date'] <= '2024-12-31') & (df['ObsFlux'] <= 300)].dropna(subset=['Date'])

        # Suavização dos dados usando média móvel (window=30 dias)
        filtered_data['SmoothedObsFlux'] = filtered_data['ObsFlux'].rolling(window=30).mean()

        return filtered_data

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição HTTP: {e}")
        return None
    except Exception as e:
        print(f"Erro ao processar os dados: {e}")
        return None

def download_sc_dates(years, save_folder):
    """
    Faz o download de arquivos SSC para uma lista de anos e salva na pasta especificada.

    Args:
        years (list): Lista de anos para fazer o download dos arquivos.
        save_folder (str): Pasta onde os arquivos serão salvos.
    """
    # Certifique-se de que years é uma lista
    if not isinstance(years, list):
        raise ValueError("O argumento 'years' deve ser uma lista de anos.")

    # Cria a pasta de destino se ela não existir
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    for year in years:
        # Gera a URL a partir do ano
        url = f"https://www.obsebre.es/php/geomagnetisme/vrapides/ssc_{year}_p.txt"
        
        # Extrai o nome do arquivo a partir da URL
        file_name = url.split("/")[-1]
        
        # Caminho completo para salvar o arquivo
        file_path = os.path.join(save_folder, file_name)
        
        # Verifica se o arquivo já existe
        if os.path.exists(file_path):
            print(f"[{file_name}] Already on the disk")
            continue
        
        try:
            # Faz o download do arquivo
            response = requests.get(url, verify=False)
            response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
            
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"[{file_name}] Downloaded")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download [{file_name}]. Error: {e}")

# def download_embrace(files_folder, date_str, station,duration):
#     requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#     date = datetime.strptime(date_str, "%Y-%m-%d")
#     d = date.strftime('%Y%m%d')
#     folder_save = os.path.join(files_folder, 'Dados', d)
    
#     if not os.path.exists(folder_save):
#         os.makedirs(folder_save)

#     base_url = "https://embracedata.inpe.br/magnetometer/"
#     variable_url = f"{station}/{date.year}/"
#     final_url = urljoin(base_url, variable_url)
    
#     response = requests.get(final_url, verify=False)
#     if response.status_code != 200:
#         return

#     soup = BeautifulSoup(response.text, 'html.parser')
    
#     for link in soup.find_all('a'):
#         file_name = link.get('href')
#         if file_name == "../" or not file_name.endswith(f'.{date.year % 100}m'):
#             continue
        
#         wanted_date = date.strftime("%d%b").lower()
#         file_date = file_name[3:8]

#         if wanted_date == file_date:
#             local_file_path = os.path.join(folder_save, file_name)
#             if os.path.exists(local_file_path):
#                 print(f"[{file_name}] Already on the disk")
#             else:
#                 file_url = urljoin(final_url, file_name)
#                 print(f"[{file_name}] Downloaded")
#                 with open(local_file_path, 'wb') as file:
#                     file_response = requests.get(file_url, verify=False)
#                     file.write(file_response.content)

def download_embrace(files_folder, date_str, station, duration):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    date = datetime.strptime(date_str, "%Y-%m-%d")
    combined_file_name = None

    for day_offset in range(duration):
        current_date = date + timedelta(days=day_offset)
        d = current_date.strftime('%Y%m%d')
        folder_save = os.path.join(files_folder, 'Dados', d)

        if not os.path.exists(folder_save):
            os.makedirs(folder_save)

        base_url = "https://embracedata.inpe.br/magnetometer/"
        variable_url = f"{station}/{current_date.year}/"
        final_url = urljoin(base_url, variable_url)

        response = requests.get(final_url, verify=False)
        if response.status_code != 200:
            print(f"Failed to access data for {station} {current_date.strftime('%Y-%m-%d')}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a'):
            file_name = link.get('href')
            if file_name == "../" or not file_name.endswith(f'.{current_date.year % 100}m'):
                continue

            wanted_date = current_date.strftime("%d%b").lower()
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

                if combined_file_name is None:
                    combined_file_name = file_name
                    combined_file_path = os.path.join(files_folder,'Dados', combined_file_name)

                # Append the content to the combined file
                with open(combined_file_path, 'ab') as combined_file:
                    with open(local_file_path, 'rb') as file:
                        combined_file.write(file.read())

    if combined_file_name:
        print(f"Combined file saved at: {combined_file_path}")
    else:
        print("No files were downloaded.")

def intermagnet_download(files_folder, date_str, station,duration):
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
        "dataDuration": duration
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

def download_files(files_folder, dates, stations,duration=1):
    for date_str in dates:
        for station in stations:
            local = stations_info[station]['local']
            date = datetime.strptime(date_str, "%Y-%m-%d")
            folder_save = os.path.join(files_folder, 'Dados', date.strftime('%Y%m%d'))
            
            if not os.path.exists(folder_save):
                os.makedirs(folder_save)
            
            if local == 'Embrace':
                # Verifica se o arquivo já existe antes de baixar
                file_name = f'{station.lower()}{date.strftime("%Y%m%d")}.min'
                local_file_path = os.path.join(folder_save, file_name)
                # print(file_name)
                if os.path.exists(local_file_path):
                    print(f"[{file_name}] Already on disk")
                else:
                    download_embrace(files_folder, date_str, station,duration)
            elif local == 'Intermag':
                # Verifica se o arquivo já existe antes de baixar
                file_name = f'{station.lower()}{date.strftime("%Y%m%d")}vmin.min'
                local_file_path = os.path.join(folder_save, file_name)
                # print(file_name)
                if os.path.exists(local_file_path):
                    print(f"[{file_name}] Already on disk")
                else:

                    intermagnet_download(files_folder, date_str, station,duration)



# %% Data selection
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
    """
    Lê arquivos de eventos de uma pasta e retorna uma lista de datas únicas com horas convertidas para decimal.

    Parâmetros:
    folder (str): A pasta contendo os arquivos de eventos.

    Retorna:
    DataFrame: DataFrame com colunas 'Data' e 'Hora' contendo as datas e horas específicas.
    """
    all_data = []
    # Itera sobre todos os arquivos na pasta
    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path) and not file_path.endswith('.ini'):
            # Ler os eventos do arquivo e converter a coluna TIME para decimal
            # print(file_path)
            hora_especifica = read_data_eventos(file_path)
            hora_especifica['TIME'] = hora_especifica['TIME'].apply(time_to_decimal_24)

            all_data.append(hora_especifica)

    # Combina todos os DataFrames em um único DataFrame
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Obter todas as datas e horas únicas no arquivo de eventos
    lista_datas = combined_data[['DATE', 'TIME','MAMP']].drop_duplicates().rename(columns={'DATE': 'Data', 'TIME': 'Hora','MAMP': 'Amp_intermagnet'})
    
    return lista_datas

# def get_date_selection(diretorio_base, event_dates):
    
#     # diretorio_base = os.path.join(files_folder, 'Dados')
#     # event_dates_orig = event_dates
#     # row = event_dates_orig.iloc[4]
     
#     dados_por_data = []

#     # Iterar sobre as datas e horas fornecidas
#     for _, row in event_dates.iterrows():
#         data = pd.to_datetime(row['Data'])
#         hora_decimal = row['Hora']
        
#         # Converter a hora decimal para horas e minutos
#         horas = int(hora_decimal)
#         minutos = int((hora_decimal - horas) * 60)
        
#         # Criar um timedelta com horas e minutos
#         delta_tempo = pd.to_timedelta(f'{horas}h {minutos}m')
        
#         # Criar um timestamp com data e hora
#         data_hora = data + delta_tempo
        
#         caminho_pasta = os.path.join(diretorio_base, data.strftime('%Y%m%d'))
#         # print(row)
#         if os.path.isdir(caminho_pasta):
#             for nome_arquivo in os.listdir(caminho_pasta):
#                 caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
#                 # print(nome_arquivo)
#                 if os.path.isfile(caminho_arquivo) and not caminho_arquivo.endswith('.ini'):
#                     df, estacao = process_data(caminho_arquivo)
                    
#                     # df = detectar_anomalias(df)
#                     # city, lat, lon = stations_info[estacao]['city'], round(stations_info[estacao]['lat'], 1), round(stations_info[estacao]['lon'], 1)
#                     city, lat, lon, altitude = stations_info[estacao]['city'], round(stations_info[estacao]['lat'], 1), round(stations_info[estacao]['lon'], 1), stations_info[estacao]['altitude']
#                     altitude = altitude/1000 #converte para km
#                     ano = data_hora.year
#                     # print(ano)
#                     D, I, H, X, Y, Z, F = pyIGRF.igrf_value(lat, lon, altitude, ano)
                    
#                     dados_por_data.append({
#                         'DataHora': data_hora,
#                         'Hora': hora_decimal,
#                         'Estacao': estacao,
#                         'Dados': df,
#                         'Cidade': city,
#                         'Latitude': lat,
#                         'Longitude': lon,
#                         'Altitude': altitude,
#                         'igrf_H': H
#                     })
    
#     return dados_por_data

def get_date_selection(diretorio_base, event_dates, estacoes_conjugadas):
    dados_por_data = []

    # Iterar sobre as datas e horas fornecidas
    for _, row in event_dates.iterrows():
        data = pd.to_datetime(row['Data'])
        hora_decimal = row['Hora']

        # Converter a hora decimal para horas e minutos
        horas = int(hora_decimal)
        minutos = int((hora_decimal - horas) * 60)

        # Criar um timedelta com horas e minutos
        delta_tempo = pd.to_timedelta(f'{horas}h {minutos}m')

        # Criar um timestamp com data e hora
        data_hora = data + delta_tempo

        caminho_pasta = os.path.join(diretorio_base, data.strftime('%Y%m%d'))
        if os.path.isdir(caminho_pasta):
            for nome_arquivo in os.listdir(caminho_pasta):
                caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
                if os.path.isfile(caminho_arquivo) and not caminho_arquivo.endswith('.ini'):
                    df, estacao = process_data(caminho_arquivo)

                    # Verificar se a estação está na lista de estacoes_conjugadas
                    if estacao in estacoes_conjugadas or estacao in estacoes_conjugadas.values():
                        
                        city = stations_info[estacao]['city']
                        lat = round(stations_info[estacao]['lat'], 1)
                        lon = round(stations_info[estacao]['lon'], 1)
                        altitude = stations_info[estacao]['altitude'] / 1000  # Converte para km
                        ano = data_hora.year

                        if lon < 0:
                            elong = lon + 360  # Adiciona 360 para longitudes negativas
                        else:
                            elong = lon
                        D, I, H, X, Y, Z, F = pyIGRF.igrf_value(lat, elong, altitude, ano)

                        dados_por_data.append({
                            'DataHora': data_hora,
                            'Hora': hora_decimal,
                            'Estacao': estacao,
                            'Dados': df,
                            'Cidade': city,
                            'Latitude': lat,
                            'Longitude': lon,
                            'Altitude': altitude,
                            'igrf_H_nT': H,
                            'igrf_D_deg': D,
                            'igrf_Z_nT': Z
                        })

    return dados_por_data


# %% Processa dados level 1
# def quality_data_test(data_list, colunas_intervalo={'H_nT': (-100, 100)}):
#     """
#     Avalia a qualidade dos dados de uma lista de DataFrames com base em valores nulos, valores absurdos e consistência estatística.
#     Retorna uma pontuação de qualidade entre 0 e 1 para cada entrada.

#     Parâmetros:
#     data_list (list): Lista de dicionários, cada um contendo um DataFrame a ser avaliado.
#     colunas_intervalo (dict): Dicionário onde as chaves são os nomes das colunas e os valores são tuplas (min, max)
#                               indicando o intervalo válido para cada coluna.

#     Retorna:
#     list: Lista de dicionários, cada um contendo a pontuação de qualidade dos dados entre 0 e 1.
#     """
#     for entry in data_list:
#         df = entry.get('Dados')
        
#         if df is None or df.empty:
#             entry['Qualidade'] = 0
#             continue
        
#         # Verifique se o campo 'Amplitude' existe no dicionário
#         if 'Amplitude' in entry:
#             amplitude = entry.get('Amplitude')
#             if not (0 < amplitude <= 1000):  # Verifique se a amplitude está no intervalo válido
#                 entry['Qualidade'] = 0
                
#                 continue
    
        
#         # 1. Porcentagem de valores não "NaN"
#         porcentagem_nao_nulos = df['H_nT'].notna().mean()  # Média da porcentagem de valores não nulos na coluna 'H_nT'

#         # 2. Percentual de valores dentro do intervalo definido (evitar valores absurdos)
#         total_linhas = len(df)
#         critico = 1
#         if total_linhas < 30:
#             critico = 1  # Se o DataFrame tiver menos de 30 linhas, considera crítico
        
#         total_validos = 0
#         colunas_intervalo = colunas_intervalo or {}
#         for coluna, (min_val, max_val) in colunas_intervalo.items():
#             if coluna in df.columns:
#                 validos = df[coluna].between(min_val, max_val).sum()
#                 total_validos += validos
#         percentual_valores_validos = total_validos / (total_linhas * len(colunas_intervalo))
    
#         # 3. Consistência estatística (comparando média e mediana)
#         # consistencia_estatistica = 0
#         # colunas_numericas = df.select_dtypes(include=np.number).columns
#         # for coluna in colunas_numericas:
#         #     media = df[coluna].mean()
#         #     mediana = df[coluna].median()
#         #     if media != 0:
#         #         consistencia_estatistica += 1 - abs(media - mediana) / abs(media)
#         # consistencia_estatistica /= len(colunas_numericas) if len(colunas_numericas) > 0 else 1
    
#         # Cálculo da pontuação final (média dos dois critérios)
#         pontuacao_qualidade = critico * (porcentagem_nao_nulos + percentual_valores_validos) / 2

#         entry['Qualidade'] = pontuacao_qualidade 
    
#     # Remover entradas com pontuação de qualidade menor que 0.8
#     # data_list = [entry for entry in data_list if entry['Qualidade'] >= 0.8]
    
#     return data_list
def quality_data_test(data, intervalo=(-100, 100), campo='H_nT'):
    """
    Avalia a qualidade dos dados de uma lista de DataFrames com base em valores válidos, valores não nulos, intervalo de faixas
    e repetição sequencial de valores (para identificar possíveis erros de sensores).
    
    Retorna uma métrica única de qualidade entre 0 e 1 para cada entrada.

    Parâmetros:
    data (list): Lista de dicionários, cada um contendo um DataFrame a ser avaliado.
    intervalo (tuple): Tupla indicando o intervalo válido para os valores (mínimo, máximo).
    campo (str): Nome da coluna que será avaliada.

    Retorna:
    list: Lista de dicionários com a métrica de qualidade para cada entrada.
    """
    data_list = data
    for entry in data_list:
        df = entry.get('Dados')
        evento_time = entry.get('DataHora')  # Momento central do evento, tipo datetime

        if df is None or df.empty or evento_time is None:
            entry['Qualidade'] = 0  # Qualidade mínima se não houver dados
            continue

        # Convertendo o momento do evento para decimal (0 a 24 horas)
        evento_time_decimal = evento_time.hour + evento_time.minute / 60 + evento_time.second / 3600

        # Definindo janela de tempo de 10 minutos (±5 minutos em torno do evento)
        janela_min = evento_time_decimal - 10 / 60  # 5 minutos antes
        janela_max = evento_time_decimal + 10 / 60  # 5 minutos depois

        # Filtrar os dados dentro da janela de tempo
        dados_janela = df[(df['TIME'] >= janela_min) & (df['TIME'] <= janela_max)]

        if dados_janela.empty:
            entry['Qualidade'] = 0
            continue

        total_linhas = len(dados_janela)

        # 1. Porcentagem de valores válidos (não NaN) para a coluna 'H_nT'
        if campo in dados_janela.columns:
            porcentagem_validos = dados_janela[campo].notna().mean()
        else:
            porcentagem_validos = 0

        # 2. Porcentagem de valores não nulos para a coluna 'H_nT' (1 se não houver zeros, 0 se apenas zeros)
        if campo in dados_janela.columns:
            total_zeros = (dados_janela[campo] == 0).sum()
            porcentagem_nao_nulos = 1 - (total_zeros / total_linhas if total_linhas > 0 else 0)
        else:
            porcentagem_nao_nulos = 0

        # 3. Porcentagem de valores dentro do intervalo definido para 'H_nT'
        if campo in dados_janela.columns:
            min_val, max_val = intervalo
            porcentagem_dentro_faixa = dados_janela[campo].between(min_val, max_val).mean()
        else:
            porcentagem_dentro_faixa = 0

        # 4. Verificação de repetição sequencial de valores na coluna 'H_nT'
        if campo in dados_janela.columns:
            repeticoes_sequenciais = (dados_janela[campo].diff() == 0).sum()
            porcentagem_sem_repeticao = 1 - (repeticoes_sequenciais / total_linhas if total_linhas > 0 else 0)
        else:
            porcentagem_sem_repeticao = 0

        # 5. Cálculo da pontuação final de qualidade
        pontuacao_qualidade = (
            porcentagem_validos + 
            porcentagem_nao_nulos + 
            porcentagem_dentro_faixa + 
            porcentagem_sem_repeticao
        ) / 4

        # Garantir que a pontuação esteja entre 0 e 1
        entry['Qualidade'] = min(max(pontuacao_qualidade, 0), 1)
        entry['Qualidade verbose'] = (
            f"{entry['Estacao']} -> {entry['DataHora']} -> "
            f"validos:{porcentagem_validos:.2f}/nulos:{porcentagem_nao_nulos:.2f}/"
            f"faixa:{porcentagem_dentro_faixa:.2f}/sem_repeticao:{porcentagem_sem_repeticao:.2f} "
            f"Qualidade: {entry['Qualidade']:.2f}"
        )

        print(entry['Qualidade verbose'])

    return data_list



def add_conjugate_entry(data_list, conjugate_mapping):
    """
    Adds a new entry "Conjugada" to each dictionary in the data list,
    indicating the conjugate station according to the provided mapping.

    Parameters:
        data_list (list): List of dictionaries containing station data.
        conjugate_mapping (dict): Dictionary mapping station names to their conjugate station names.

    Returns:
        list: Updated list with the new "Conjugada" entry added.
    """
    for entry in data_list:
        station = entry.get('Estacao')
        
        # print(f'estacao:{station}')
        # Add the conjugate station if it exists in the mapping
        if station in conjugate_mapping:
            entry['Conjugada'] = conjugate_mapping[station]
        else:
            entry['Conjugada'] = None  # Set to None if there's no conjugate
    
    return data_list

def calcular_tempo_local(data):
    
    eventos_sc = data
    df = pd.DataFrame(eventos_sc)
    
    # Verifique se o DataFrame contém as colunas necessárias
    if 'Longitude' not in df.columns or 'DataHora' not in df.columns:
        print("O DataFrame não contém as colunas necessárias: 'Longitude' e 'DataHora'.")
        return

    # Converta 'DataHora' para datetime, se ainda não estiver
    df['DataHora'] = pd.to_datetime(df['DataHora'])

    # Calcular o fuso horário local a partir da longitude
    df['FusoHorario'] = df['Longitude'] / 15

    # Calcular o Tempo Local adicionando o fuso horário ao Tempo Universal (UTC)
    df['TempoLocal'] = df.apply(lambda row: row['DataHora'] + timedelta(hours=row['FusoHorario']), axis=1)

    # Retornar o DataFrame com o Tempo Local calculado
    eventos_sc_local = df.to_dict(orient='records')
    
    return eventos_sc_local

def amplificacao_estacoes(data, estacoes_conjugadas):

    #opção para calcular amplificação para cada estação conjugada
    # estacoes_conjugadas_reverso = {v: k for k, v in estacoes_conjugadas.items()}
    eventos_sc = data
    eventos_com_amplificacao = []
    
    # Crie um dicionário para armazenar amplitudes por DataHora e Estação
    amplitudes_por_datahora = {}
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        amplitude = evento['Amplitude']
        
        if datahora not in amplitudes_por_datahora:
            amplitudes_por_datahora[datahora] = {}
        
        amplitudes_por_datahora[datahora][estacao] = amplitude
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        
        amplificacao = None
        
        if datahora in amplitudes_por_datahora:
            # estacao_conjugada_nome = estacoes_conjugadas.get(estacao, estacoes_conjugadas_reverso.get(estacao))
            estacao_conjugada_nome = estacoes_conjugadas.get(estacao, None)

            if estacao_conjugada_nome:
                conjugada_amplitude = amplitudes_por_datahora[datahora].get(estacao_conjugada_nome, None)
                
                if conjugada_amplitude is not None and conjugada_amplitude != 0:
                    estacao_amplitude = amplitudes_por_datahora[datahora].get(estacao, None)
                    if estacao_amplitude is not None:
                        amplificacao = estacao_amplitude / conjugada_amplitude
                else:
                    amplificacao = None
            else:
                amplificacao = None
        
        evento_com_amplificacao = evento.copy()
        evento_com_amplificacao['Amplificacao'] = amplificacao
        eventos_com_amplificacao.append(evento_com_amplificacao)
    
    return eventos_com_amplificacao

def amplificacao_estacoes_dH_nT_abs(eventos_sc, estacoes_conjugadas):

    #opção para calcular amplificação para cada estação conjugada
    # estacoes_conjugadas_reverso = {v: k for k, v in estacoes_conjugadas.items()}

    eventos_com_amplificacao = []
    
    # Crie um dicionário para armazenar amplitudes por DataHora e Estação
    amplitudes_por_datahora = {}
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        amplitude = evento['Amplitude_D']
        
        if datahora not in amplitudes_por_datahora:
            amplitudes_por_datahora[datahora] = {}
        
        amplitudes_por_datahora[datahora][estacao] = amplitude
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        
        amplificacao = None
        
        if datahora in amplitudes_por_datahora:
            # estacao_conjugada_nome = estacoes_conjugadas.get(estacao, estacoes_conjugadas_reverso.get(estacao))
            estacao_conjugada_nome = estacoes_conjugadas.get(estacao, None)

            if estacao_conjugada_nome:
                conjugada_amplitude = amplitudes_por_datahora[datahora].get(estacao_conjugada_nome, None)
                
                if conjugada_amplitude is not None and conjugada_amplitude != 0:
                    estacao_amplitude = amplitudes_por_datahora[datahora].get(estacao, None)
                    if estacao_amplitude is not None:
                        amplificacao = estacao_amplitude / conjugada_amplitude
                else:
                    amplificacao = None
            else:
                amplificacao = None
        
        evento_com_amplificacao = evento.copy()
        evento_com_amplificacao['Amplificacao_dH_nT_abs'] = amplificacao
        eventos_com_amplificacao.append(evento_com_amplificacao)
    
    return eventos_com_amplificacao

def amplificacao_estacoes_dH_nT_absacumulado(eventos_sc, estacoes_conjugadas):

    #opção para calcular amplificação para cada estação conjugada
    # estacoes_conjugadas_reverso = {v: k for k, v in estacoes_conjugadas.items()}

    eventos_com_amplificacao = []
    
    # Crie um dicionário para armazenar amplitudes por DataHora e Estação
    amplitudes_por_datahora = {}
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        amplitude = evento['Amplitude_E']
        
        if datahora not in amplitudes_por_datahora:
            amplitudes_por_datahora[datahora] = {}
        
        amplitudes_por_datahora[datahora][estacao] = amplitude
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        
        amplificacao = None
        
        if datahora in amplitudes_por_datahora:
            # estacao_conjugada_nome = estacoes_conjugadas.get(estacao, estacoes_conjugadas_reverso.get(estacao))
            estacao_conjugada_nome = estacoes_conjugadas.get(estacao, None)

            if estacao_conjugada_nome:
                conjugada_amplitude = amplitudes_por_datahora[datahora].get(estacao_conjugada_nome, None)
                
                if conjugada_amplitude is not None and conjugada_amplitude != 0:
                    estacao_amplitude = amplitudes_por_datahora[datahora].get(estacao, None)
                    if estacao_amplitude is not None:
                        amplificacao = estacao_amplitude / conjugada_amplitude
                else:
                    amplificacao = None
            else:
                amplificacao = None
        
        evento_com_amplificacao = evento.copy()
        evento_com_amplificacao['Amplificacao_dH_nT_absacumulado'] = amplificacao
        eventos_com_amplificacao.append(evento_com_amplificacao)
    
    return eventos_com_amplificacao

def derivativas(dados_por_data):
    for item in dados_por_data:
        df_dados = item['Dados']
        # print(f"{item['Estacao']} : {item['DataHora']}")

        # Avalia se o DataFrame possui muitos NaN
        if df_dados.empty or df_dados['H_nT'].isna().mean() > 0.20:  # Exemplo: mais de 20% de NaN
            # Caso haja muitos NaNs, atribui NaN aos campos de interesse
            item['Ponto_Esquerda_A'] = float('nan')
            item['Ponto_Direita_A'] = float('nan')
            item['Residual_A'] = float('nan')
            item['R_squared_A'] = float('nan')
            item['RMSE_A'] = float('nan')
            item['Amplitude'] = float('nan')
                        
            df_dados['H_nT_movmean'] = float('nan')
            df_dados['dH_nT_movmean'] = float('nan')
            df_dados['H_nT_ajuste'] = float('nan')
            df_dados['D_deg_ajuste'] = float('nan')
            df_dados['dH_nT_abs'] = float('nan')
            df_dados['dH_nT_absacumulado'] = float('nan')
            df_dados['dH_nT_drmsacumulado'] = float('nan')
            
            df_dados['DateTime'] = float('nan')
            
            item['Ponto_Esquerda_D'] = float('nan')
            item['Ponto_Direita_D'] = float('nan')
            item['Residual_D'] = float('nan')
            item['R_squared_D'] = float('nan')
            item['RMSE_D'] = float('nan')
            item['Amplitude_D'] = float('nan')
            
            item['Ponto_Esquerda_E'] = float('nan')
            item['Ponto_Direita_E'] = float('nan')
            item['Residual_E'] = float('nan')
            item['R_squared_E'] = float('nan')
            item['RMSE_E'] = float('nan')
            item['Amplitude_E'] = float('nan')
            
            item['Dados'] = df_dados
            continue  # Passa para o próximo item

        # df = detectar_anomalias(df,colunas=['H_nT'])
        df_dados['dH_nT'] = df_dados['H_nT'].diff()
        df_dados['dD_deg'] = df_dados['D_deg'].diff()
        df_dados['dZ_nT'] = df_dados['Z_nT'].diff()

        # Aplica média móvel
        df_dados['H_nT_movmean'] = df_dados['H_nT'].rolling(window=20, center=True).mean()

        # Calcula a derivada
        df_dados['dH_nT_movmean'] = df_dados['H_nT_movmean'].diff()

        # Aplica a função de ajuste e calcula parâmetros
        df_dados['H_nT_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_wavelet_amplitude(df_dados, 'H_nT')
        
        # df_dados['H_nT_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_iir_amplitude(df_dados, 'H_nT')

        # df_dados['H_nT_iir'] = filtro_iir(df_dados, 'H_nT')
        # df_dados['H_nT_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_ajuste(df_dados, 'H_nT_ajuste')
        # df_dados['H_nT_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_ajuste_modificada(df_dados, 'H_nT')
        
        # df_dados['dH_nT_abs']=df_dados['dH_nT'].apply(lambda x: (x**2))
        df_dados['dH_nT_abs']=df_dados['dH_nT'].abs()
        
        df_dados['dH_nT_absacumulado']= df_dados['dH_nT_abs'].cumsum()
        df_dados['dH_nT_drmsacumulado'] =df_dados['dH_nT_absacumulado'].diff()
        
        df_dados['dH_nT_abs_ajuste'], amplitude_D, ponto_esquerda_D, ponto_direita_D, residual_D, r_squared_D, rmse_D = caract_wavelet_amplitude(df_dados, 'dH_nT_abs')
        
        df_dados['dH_nT_absacumulado_ajuste'], amplitude_E, ponto_esquerda_E, ponto_direita_E, residual_E, r_squared_E, rmse_E = caract_wavelet_amplitude(df_dados, 'dH_nT_absacumulado')

        # df_dados['dH_nT_abs_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_wavelet_amplitude(df_dados, 'dH_nT_abs')
        # df_dados['dH_nT_abs_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_wavelet_amplitude(df_dados, 'dH_nT_abs')

        df_dados['DateTime'] = df_dados['TIME']
        # D, I, H, X, Y, Z, F = campo_H_igrf(item['Latitude'], item['Longitude'], alt, ano)

        # Atribui valores calculados ao item
        item['Ponto_Esquerda_A'] = ponto_esquerda
        item['Ponto_Direita_A'] = ponto_direita
        item['Residual_A'] = residual
        item['R_squared_A'] = r_squared
        item['RMSE_A'] = rmse
        item['Amplitude'] = amplitude
                
        item['Ponto_Esquerda_D'] = ponto_esquerda_D
        item['Ponto_Direita_D'] = ponto_direita_D
        item['Residual_D'] = residual_D
        item['R_squared_D'] = r_squared_D
        item['RMSE_D'] = rmse_D
        item['Amplitude_D'] = amplitude_D
        
        item['Ponto_Esquerda_E'] = ponto_esquerda_E
        item['Ponto_Direita_E'] = ponto_direita_E
        item['Residual_E'] = residual_E
        item['R_squared_E'] = r_squared_E
        item['RMSE_E'] = rmse_E
        item['Amplitude_E'] = amplitude_E
        
        item['Dados'] = df_dados

    return dados_por_data

def estatisticas(dados_por_data):
    for item in dados_por_data:
        df_dados = item['Dados']
        # print(item['DataHora'])
        # print(item['Estacao'])
        
        # Cálculo do RMSE entre as colunas 'sinal_1' e 'sinal_2'
        mse = ((df_dados['dH_nT_absacumulado_diff']) ** 2).mean()
        rmse = np.sqrt(mse)
        item['RMSE_H_nT_rmsacumulado'] = rmse
                
    return dados_por_data

def normalize(dados_por_data):
    for item in dados_por_data:
        df_dados = item['Dados']
        # print(item['DataHora'])
        # print(item['Estacao'])
        
        #normalizar pelo valor do igrf
        df_dados['H_nT'] = df_dados['H_nT_source']/item['igrf_H']
        #normalizar pelo valor de F do dado
        # df_dados['H_nT'] = df_dados['H_nT_norm']/item['igrf_H']

    return dados_por_data

def offset(data, mode='igrf', campo='H_nT'):
    """
    Ajusta os valores do campo de acordo com o modo selecionado.

    Parâmetros:
    - dados_por_data: lista de dicionários contendo os dados e metadados.
    - mode: 'igrf' para ajuste com base no valor do IGRF, 
            'first_value' para ajuste com base no primeiro valor válido do dataframe.
    - campo: nome do campo a ser ajustado (padrão 'H_nT').

    Retorna:
    - lista com os dados ajustados.
    """
    dados_por_data = data 
    for item in dados_por_data:
        df_dados = item['Dados']
        print(f"offset:{item['Estacao']}->{item['DataHora']}-> {item.get(f'igrf_{campo}', 'N/A')}")
        
        if mode == 'igrf':
            # Offset pelo valor do IGRF
            df_dados[campo] = df_dados[f"{campo}_source"] - item[f"igrf_{campo}"]
        
        elif mode == 'first_value':
            # Offset pelo primeiro valor válido do campo
            first_valid_idx = df_dados[campo].first_valid_index()
            if first_valid_idx is not None:
                first_valid_value = df_dados.loc[first_valid_idx, campo]
                df_dados[campo] = df_dados[campo] - first_valid_value
            else:
                print(f"AVISO: Nenhum valor válido encontrado para '{campo}' em {item['Estacao']} na data {item['DataHora']}")
        
        else:
            raise ValueError("Modo inválido! Escolha 'igrf' ou 'first_value'.")
    
    return dados_por_data



def recorte_evento(dado, tamanho_janela):
    
    dados_por_data = dado
    for item in dados_por_data:
        df_dados = item['Dados']
        hora_central = item['Hora']

        # Calcular o intervalo de tempo
        janela_inicio = max(0, hora_central - tamanho_janela / 2)
        janela_fim = min(24, hora_central + tamanho_janela / 2)

        # print(f"Processing Hora: {hora_central}")
        # print(f"Time Window: {janela_inicio} to {janela_fim}")
        # print(f"Original Data Length: {len(df_dados)}")

        # Filtrar o DataFrame 'Dados' para manter apenas os dados dentro do intervalo
        df_recortado = df_dados[(df_dados['TIME'] >= janela_inicio) & (df_dados['TIME'] <= janela_fim)].copy()

        # print(f"Filtered Data Length: {len(df_recortado)}")

        if df_recortado.empty:
            # Handle the empty DataFrame case
            print(f"No data available in the time window for Hora {hora_central}.")
        
        item['Dados'] = df_recortado
    return dados_por_data

def calculate_conjugate_difference(data_list):
    """
    Calcula a diferença nos valores de "dH_nT" entre cada estação e sua estação conjugada
    para cada "DataHora" disponível.

    Parâmetros:
        data_list (list): Lista de dicionários contendo dados das estações.

    Retorna:
        list: Lista atualizada com a diferença adicionada como uma nova coluna "dH_nT_diff" no DataFrame "Dados".
    """
    # Cria um dicionário para indexar dados por estação e DataHora para fácil consulta
    data_index = {}
    for entry in data_list:
        station = entry.get('Estacao')
        datahora = entry.get('DataHora')
        if station and datahora:
            if station not in data_index:
                data_index[station] = {}
            data_index[station][datahora] = entry
    
    # Calcula a diferença em dH_nT entre cada estação e sua conjugada
    for entry in data_list:
        conjugate_station = entry.get('Conjugada')
        # print(conjugate_station)
        datahora = entry.get('DataHora')
        if conjugate_station and datahora:
            
            conjugate_entry = data_index.get(conjugate_station, {}).get(datahora)
            if conjugate_entry:
                entry['Dados']['dH_nT_diff'] = entry['Dados']['dH_nT'] - conjugate_entry['Dados']['dH_nT']              
            else:
                entry['Dados']['dH_nT_diff'] = None  # Definir como None se os dados da conjugada não estiverem disponíveis
        else:
            entry['Dados']['dH_nT_diff'] = None  # Definir como None se não houver estação conjugada
    
    return data_list

from scipy.signal import butter, filtfilt
import pandas as pd

def filtro_iir(df_dados, coluna):
    # Frequências de corte (em Hz)
    low_cut = 0.002  # 2 mHz
    high_cut = 0.007  # 7 mHz

    # Frequência de amostragem (em Hz)
    fs = 1 / 60  # Amostragem a cada 1 minuto -> 1/60 Hz

    # Normalização da frequência de corte (para fs/2 como Nyquist)
    nyquist = fs / 2
    low = low_cut / nyquist
    high = high_cut / nyquist

    # Design do filtro Butterworth passa-banda de ordem 4
    b, a = butter(N=4, Wn=[low, high], btype='band', analog=False)

    # Filtrar a coluna especificada
    coluna_filtrada = filtfilt(b, a, df_dados[coluna])

    return coluna_filtrada



# %% tools
# Função para converter HH:MM:SS.000 para decimal entre 0 e 24
def time_to_decimal_24(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M:%S.%f').time()
    decimal_time = time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600 + time_obj.microsecond / 3600000000
    decimal_time = round(decimal_time,2)
    return decimal_time

def decimal_para_hora(decimal_hora):
    horas = int(decimal_hora)
    minutos = int((decimal_hora - horas) * 60)
    # segundos = int((decimal_hora - horas - minutos / 60) * 3600)
    
    return f"{horas:02d}:{minutos:02d}"
# %% caracteristicas extrator
# def caract_wavelet_amplitude(dados_janela, coluna, wavelet='db4', level=1):
#     # Extrair dados da coluna específica e preencher NaNs com interpolação
#     y_data = dados_janela[coluna].values
#     y_data = pd.Series(y_data).interpolate().ffill().bfill().values

#     # Remover infs
#     mask = ~np.isinf(y_data)
#     y_data = y_data[mask]

#     # Verificar se temos dados suficientes após remover infs e NaNs
#     if len(y_data) < 2 or np.isnan(y_data).all():
#         return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

#     # Aplicar a transformada wavelet discreta (DWT) para decompor o sinal
#     coeffs = pywt.wavedec(y_data, wavelet, level=level)
    
#     # Reconstruir o sinal detalhado de maior escala (primeira decomposição de detalhe)
#     y_detail = pywt.waverec([coeffs[0]] + [np.zeros_like(c) for c in coeffs[1:]], wavelet)
    
#     # Garantir que y_detail tenha o mesmo comprimento que y_data
#     y_detail = y_detail[:len(y_data)]

#     # Calcular o valor máximo e mínimo na componente de detalhe (impulso súbito)
#     max_idx = np.argmax(y_detail)
#     min_idx = np.argmin(y_detail)
    
#     # Amplitude do SI como a diferença entre máximo e mínimo
#     L = y_detail[max_idx] - y_detail[min_idx]
    
#     # Verificar se os índices estão dentro do tamanho de dados_janela
#     if max_idx >= len(dados_janela) or min_idx >= len(dados_janela):
#         return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan
    
#     # Posições dos valores à esquerda e à direita (máximo e mínimo)
#     posicao_esquerda = dados_janela.iloc[min_idx]['TIME']
#     posicao_direita = dados_janela.iloc[max_idx]['TIME']
    
#     ponto_esquerda = [posicao_esquerda, y_detail[min_idx]]
#     ponto_direita = [posicao_direita, y_detail[max_idx]]
    
#     # Calcular o RMSE entre o sinal original e o detalhe reconstruído (erro de ajuste)
#     rmse = np.sqrt(np.mean((y_data - y_detail)**2))
    
#     # Cálculo do R²
#     ss_res = np.sum((y_data - y_detail)**2)
#     ss_tot = np.sum((y_data - np.mean(y_data))**2)
#     r_squared = 1 - (ss_res / ss_tot)

#     residual = 0
#     return y_detail, L, ponto_esquerda, ponto_direita, residual, r_squared, rmse
def caract_iir_amplitude(dados_janela, coluna):
    # Extrair dados da coluna específica e preencher NaNs com interpolação
    y_data = dados_janela[coluna].values
    y_data = pd.Series(y_data).interpolate().ffill().bfill().values

    # Remover infs
    mask = ~np.isinf(y_data)
    y_data = y_data[mask]

    # Verificar se temos dados suficientes após remover infs e NaNs
    if len(y_data) < 2 or np.isnan(y_data).all():
        return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    # Frequências de corte (em Hz)
    low_cut = 0.002  # 2 mHz
    high_cut = 0.007  # 7 mHz

    # Frequência de amostragem (em Hz)
    fs = 1 / 60  # Amostragem a cada 1 minuto -> 1/60 Hz

    # Normalização da frequência de corte (para fs/2 como Nyquist)
    nyquist = fs / 2
    low = low_cut / nyquist
    high = high_cut / nyquist

    # Design do filtro Butterworth passa-banda de ordem 4
    b, a = butter(N=4, Wn=[low, high], btype='band', analog=False)

    # Calcular padlen
    padlen = 3 * (max(len(a), len(b)) - 1)

    # Verificar se y_data é longo o suficiente para filtfilt
    if len(y_data) <= padlen:
        return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    # Aplicar o filtro IIR na coluna especificada
    y_detail = filtfilt(b, a, y_data)

    # Índice do valor máximo na componente de detalhe
    max_idx = np.argmax(y_detail)

    # Procurar o índice do mínimo antes do máximo
    if max_idx > 0:
        min_idx = np.argmin(y_detail[:max_idx])
    else:
        min_idx = max_idx  # Caso não haja valores antes do máximo, o mínimo será o próprio máximo

    # Amplitude do SI como a diferença entre o máximo e o mínimo
    L = y_detail[max_idx] - y_detail[min_idx]

    # Verificar se os índices estão dentro do tamanho de dados_janela
    if max_idx >= len(dados_janela) or min_idx >= len(dados_janela):
        return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    # Posições dos valores à esquerda e à direita (mínimo antes do máximo e o próprio máximo)
    posicao_esquerda = dados_janela.iloc[min_idx]['TIME']
    posicao_direita = dados_janela.iloc[max_idx]['TIME']

    ponto_esquerda = [posicao_esquerda, y_detail[min_idx]]
    ponto_direita = [posicao_direita, y_detail[max_idx]]

    # Calcular o RMSE entre o sinal original e o detalhe filtrado (erro de ajuste)
    rmse = np.sqrt(np.mean((y_data - y_detail) ** 2))

    # Cálculo do R²
    ss_res = np.sum((y_data - y_detail) ** 2)
    ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # Calcular o valor residual (placeholder)
    residual = 0

    return y_detail, L, ponto_esquerda, ponto_direita, residual, r_squared, rmse


def caract_wavelet_amplitude(dados_janela, coluna, wavelet='db4', level=2):
    # Extrair dados da coluna específica e preencher NaNs com interpolação
    y_data = dados_janela[coluna].values
    y_data = pd.Series(y_data).interpolate().ffill().bfill().values

    # Remover infs
    mask = ~np.isinf(y_data)
    y_data = y_data[mask]

    # Verificar se temos dados suficientes após remover infs e NaNs
    if len(y_data) < 2 or np.isnan(y_data).all():
        return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    # Aplicar a transformada wavelet discreta (DWT) para decompor o sinal
    coeffs = pywt.wavedec(y_data, wavelet, level=level)
    # print(coeffs)
    
    # Reconstruir o sinal detalhado de maior escala (primeira decomposição de detalhe)
    # y_detail = pywt.waverec([coeffs[0]] + [np.zeros_like(c) for c in coeffs[1:]], wavelet)
    y_detail = pywt.waverec(coeffs, wavelet)
    type(y_detail)
    
      
    # Garantir que y_detail tenha o mesmo comprimento que y_data
    y_detail = y_detail[:len(y_data)]

    # Índice do valor máximo na componente de detalhe
    max_idx = np.argmax(y_detail)

    # Procurar o índice do mínimo antes do máximo
    if max_idx > 0:
        min_idx = np.argmin(y_detail[:max_idx])
    else:
        min_idx = max_idx  # Caso não haja valores antes do máximo, o mínimo será o próprio máximo

    # Amplitude do SI como a diferença entre o máximo e o mínimo
    L = y_detail[max_idx] - y_detail[min_idx]

    # Verificar se os índices estão dentro do tamanho de dados_janela
    if max_idx >= len(dados_janela) or min_idx >= len(dados_janela):
        return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    # Posições dos valores à esquerda e à direita (mínimo antes do máximo e o próprio máximo)
    posicao_esquerda = dados_janela.iloc[min_idx]['TIME']
    posicao_direita = dados_janela.iloc[max_idx]['TIME']
    
    ponto_esquerda = [posicao_esquerda, y_detail[min_idx]]
    ponto_direita = [posicao_direita, y_detail[max_idx]]

    # Calcular o RMSE entre o sinal original e o detalhe reconstruído (erro de ajuste)
    rmse = np.sqrt(np.mean((y_data - y_detail) ** 2))

    # Cálculo do R²
    ss_res = np.sum((y_data - y_detail) ** 2)
    ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # Calcular o valor residual (placeholder)
    residual = 0

    return y_detail, L, ponto_esquerda, ponto_direita, residual, r_squared, rmse


def sigmoid(x, L, x0, k, b):
    # Limitar o valor da exponencial para evitar overflow
    exp_input = np.clip(-k * (x - x0), -700, 700)  # Limite para evitar overflow em exp
    return L / (1 + np.exp(exp_input)) + b

def sigmoid_modified(x, L, x0, k, b, beta):
    """
    Função sigmoide modificada com um termo de decaimento exponencial.

    Parâmetros:
        x : array-like
            O valor de entrada (eixo x).
        L : float
            Amplitude máxima do sinal.
        x0 : float
            Posição do ponto médio (onde ocorre a transição).
        k : float
            Taxa de crescimento (quanto maior, mais abrupto o crescimento).
        b : float
            Deslocamento vertical (valor mínimo da sigmoide).
        beta : float
            Taxa de decaimento após o pico.

    Retorna:
        array-like
            Valores da sigmoide modificada.
    """
    # Limitar o valor da exponencial para evitar overflow
    exp_input = np.clip(-k * (x - x0), -700, 700)  # Limite para evitar overflow em exp
    
    # Função sigmoide com o termo de decaimento
    return (L / (1 + np.exp(exp_input)) + b) * np.exp(-beta * (x - x0))

def caract_ajuste_modificada(dados_janela, coluna):
    x_data = np.arange(len(dados_janela))
    y_data = dados_janela[coluna].values

    # Preencher NaNs com interpolação linear
    y_data = pd.Series(y_data).interpolate().ffill().bfill().values

    # Remover infs
    mask = ~np.isinf(y_data)
    x_data = x_data[mask]
    y_data = y_data[mask]

    # Chute inicial para os parâmetros da sigmoide modificada
    p0 = [max(y_data), np.median(x_data), 1, min(y_data), 0.1]  # L, x0, k, b, beta

    # Ajuste da curva sigmoide modificada com tratamento de exceção
    try:
        with warnings.catch_warnings():
            # warnings.simplefilter('ignore', OptimizeWarning)
            params, _ = curve_fit(sigmoid_modified, x_data, y_data, p0, maxfev=10000)
        
        L, x0, k, b, beta = params
        
        # Curva ajustada
        y_fit = sigmoid_modified(x_data, L, x0, k, b, beta)

        # Valores máximo e mínimo na curva ajustada
        max_idx = np.argmax(y_fit)
        min_idx = np.argmin(y_fit)
        
        # Posições dos valores à esquerda e à direita
        posicao_esquerda = dados_janela.iloc[min_idx]['TIME']
        posicao_direita = dados_janela.iloc[max_idx]['TIME']
        
        ponto_esquerda = [posicao_esquerda, y_fit[min_idx]]
        ponto_direita = [posicao_direita, y_fit[max_idx]]
        
        # Cálculo do resíduo
        residual = np.sum((y_data - sigmoid_modified(x_data, *params))**2)

        # Cálculo do R²
        ss_res = np.sum((y_data - y_fit)**2)
        ss_tot = np.sum((y_data - np.mean(y_data))**2)
        r_squared = 1 - (ss_res / ss_tot)

        # Cálculo do RMSE
        rmse = np.sqrt(np.mean((y_data - y_fit)**2))

    except (RuntimeError, ValueError):     
        return np.full(len(dados_janela), np.nan), np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    return y_fit, L, ponto_esquerda, ponto_direita, residual, r_squared, rmse


def caract_ajuste(dados_janela, coluna):
    x_data = np.arange(len(dados_janela))
    y_data = dados_janela[coluna].values

    # Preencher NaNs com interpolação linear
    y_data = pd.Series(y_data).interpolate().ffill().bfill().values

    # Remover infs
    mask = ~np.isinf(y_data)
    x_data = x_data[mask]
    y_data = y_data[mask]

    # Chute inicial para os parâmetros
    p0 = [max(y_data), np.median(x_data), 1, min(y_data)]

    # Ajuste da curva sigmoide com tratamento de exceção
    try:
        with warnings.catch_warnings():
            params, _ = curve_fit(sigmoid, x_data, y_data, p0, maxfev=1000)
        L, x0, k, b = params

        # Curva ajustada
        y_fit = sigmoid(x_data, L, x0, k, b)

        # Índice do valor máximo na curva ajustada
        max_idx = np.argmax(y_fit)
        
        # Procurar o índice do mínimo antes do máximo
        if max_idx > 0:
            min_idx = np.argmin(y_fit[:max_idx])
        else:
            min_idx = max_idx  # Caso não haja valores antes do máximo, o mínimo será o próprio máximo

        # Posições dos valores à esquerda (mínimo) e à direita (máximo)
        posicao_esquerda = dados_janela.iloc[min_idx]['TIME']
        posicao_direita = dados_janela.iloc[max_idx]['TIME']
        
        ponto_esquerda = [posicao_esquerda, y_fit[min_idx]]
        ponto_direita = [posicao_direita, y_fit[max_idx]]
        
        # Cálculo do resíduo
        residual = np.sum((y_data - sigmoid(x_data, *params))**2)

        # Cálculo do R²
        ss_res = np.sum((y_data - y_fit)**2)
        ss_tot = np.sum((y_data - np.mean(y_data))**2)
        r_squared = 1 - (ss_res / ss_tot)

        # Cálculo do RMSE
        rmse = np.sqrt(np.mean((y_data - y_fit)**2))

    except (RuntimeError, ValueError):     
        return np.full(len(dados_janela), np.nan), np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    return y_fit, L, ponto_esquerda, ponto_direita, residual, r_squared, rmse


def calcula_amplificacao(amplitude_estacao, amplitude_conjugada):
    """
    Calcula a amplificação com base na amplitude de duas estações conjugadas.

    Parâmetros:
    amplitude_estacao (float): Amplitude da estação atual.
    amplitude_conjugada (float): Amplitude da estação conjugada.

    Retorna:
    float: O valor da amplificação.
    """
    if amplitude_conjugada == 0:
        return None
    return amplitude_estacao / amplitude_conjugada


def caract_longitude(station_name, stations_info):
  # Verifica se a estação existe no dicionário
  if station_name in stations_info:
      # Retorna as coordenadas de latitude e longitude
      return stations_info[station_name]["lon"]
  else:
      # Retorna uma mensagem de erro se a estação não for encontrada
      return "Estação não encontrada"  
  
def caract_latitude(station_name, stations_info):
  # Verifica se a estação existe no dicionário
  if station_name in stations_info:
      # Retorna as coordenadas de latitude e longitude
      return stations_info[station_name]["lat"]
  else:
      # Retorna uma mensagem de erro se a estação não for encontrada
      return "Estação não encontrada"
  
#%%filtragem pela qualidadade
def filter_by_quality(data, estacoes_conjugadas, limite=0.9, field='Qualidade'):
    """
    Retorna uma lista filtrada de dados em 'my_list' com base em uma lista de estações conjugadas,
    considerando apenas as datas em que todas as estações (principal e conjugada) têm o valor do campo especificado
    maior que o limite e 'Amplificacao' no intervalo (> 0 e <= 5).

    Parâmetros:
        data (list): Lista de dicionários contendo dados das estações.
        estacoes_conjugadas (dict): Dicionário com as estações principais como chaves e suas estações conjugadas como valores.
        limite (float): Limite mínimo para o campo especificado (padrão: 0.9).
        field (str): Nome do campo a ser verificado (padrão: 'Qualidade').

    Retorna:
        list: Lista filtrada com dados que atendem aos critérios de qualidade.
    """
    # Converte my_list em um dicionário para acesso mais rápido por estação e data
    my_list = data
    data_index = {}
    for entry in my_list:
        station = entry.get('Estacao')
        datahora = entry.get('DataHora')
        if station and datahora:
            if datahora not in data_index:
                data_index[datahora] = {}
            data_index[datahora][station] = entry

    # Filtra as datas que satisfazem as condições de qualidade e amplificação
    filtered_data = []
    for datahora, stations_data in data_index.items():
        all_stations_meet_criteria = True
        for principal, conjugada in estacoes_conjugadas.items():
            principal_data = stations_data.get(principal)
            conjugada_data = stations_data.get(conjugada)

            if not principal_data:
                all_stations_meet_criteria = False
                # print(f"[{principal_data.get('Estacao', 'N/A')}] [{principal_data.get('DataHora', 'N/A')}]; dados da estação principal ausentes")
                print(f"[{station}] [{datahora}] dados da estação principal ausentes")

                break
            
            if principal_data.get(field, 0) < limite:
                all_stations_meet_criteria = False
                print(f"[{principal_data['Estacao']}] [{principal_data['DataHora']}] valor do campo '{field}' ({principal_data.get(field, 0)}) inadequado na estação principal")
                break
            
            if not conjugada_data:
                all_stations_meet_criteria = False
                print(f"[{conjugada_data.get('Estacao', 'N/A')}] [{conjugada_data.get('DataHora', 'N/A')}] dados da estação conjugada ausentes")
                break
            
            if conjugada_data.get(field, 0) < limite:
                all_stations_meet_criteria = False
                print(f"[{conjugada_data['Estacao']}] [{conjugada_data['DataHora']}] valor do campo '{field}' ({conjugada_data.get(field, 0)}) inadequado na estação conjugada")
                break
            
            # if not (0 < principal_data.get('Amplificacao', -5) <= 5):
            #     all_stations_meet_criteria = False
            #     print(f"[{principal_data['Estacao']}] [{principal_data['DataHora']}] valor da amplificação ({principal_data.get('Amplificacao', -5)}) fora do intervalo permitido (0, 5]")
            #     break

        # Adiciona ao resultado final se a data satisfizer todas as condições para todas as estações
        if all_stations_meet_criteria:
            filtered_data.extend(stations_data.values())

    return filtered_data



# %% Plot data
# def plot_amplificacao_and_solar_flux(eventos_sc_local, filtered_data, anos, estacoes):
#     """
#     Plota a amplificação por data para as estações especificadas e os anos fornecidos, junto com os dados do fluxo solar F10.7.

#     Args:
#         eventos_sc_local (list): Lista de eventos com amplificação e tempo local calculado.
#         filtered_data (DataFrame): Dados filtrados e suavizados do fluxo solar F10.7.
#         anos (list): Lista de anos para filtrar os dados.
#         estacoes (str): String com os códigos das estações separadas por espaço.
#     """
#     # eventos_sc_local = my_list_filtered
#     # filtered_data = flux_data
#     # Crie um DataFrame a partir dos eventos
#     df_amplificacao = pd.DataFrame(eventos_sc_local)

    
#     # Verifique se o DataFrame contém as colunas necessárias
#     if 'Amplificacao' not in df_amplificacao.columns or 'DataHora' not in df_amplificacao.columns:
#         print("A lista de eventos não contém dados de amplificação, DataHora ou RMSE.")
#         return
    
#     # Converter a coluna 'DataHora' para datetime, se ainda não estiver
#     df_amplificacao['DataHora'] = pd.to_datetime(df_amplificacao['DataHora'])
    
#     # Filtrar os dados pelos anos especificados
#     df_amplificacao = df_amplificacao[df_amplificacao['DataHora'].dt.year.isin(anos)]
       
#     # Filtrar pelas estações especificadas
#     estacoes_lista = estacoes
    
#     df_amplificacao = df_amplificacao[df_amplificacao['Estacao'].isin(estacoes_lista)]
    
#     # Verificar se há dados após o filtro
#     if df_amplificacao.empty:
#         print("Nenhum dado encontrado para os anos e estações especificados.")
#         return
    
#     # Calcular a porcentagem de pontos com RMSE > 0.8
#     total_pontos = len(df_amplificacao)
#     pontos_rmse_alto = len(df_amplificacao[df_amplificacao['Qualidade'] > 0.8])
#     porcentagem_rmse_alto = (pontos_rmse_alto / total_pontos) * 100 if total_pontos > 0 else 0
    
#     # Definir cores específicas para cada estação
#     cmap = plt.get_cmap('tab10')
#     cores = cmap(np.linspace(0, 1, len(estacoes_lista)))
#     cor_estacao = {estacao: cores[i] for i, estacao in enumerate(estacoes_lista)}

#     # Criar o gráfico
#     fig, ax1 = plt.subplots(figsize=(14, 8))

#     for estacao in estacoes_lista:
#         df_estacao = df_amplificacao[df_amplificacao['Estacao'] == estacao]
#         if not df_estacao.empty:
#             ax1.scatter(df_estacao['DataHora'], df_estacao['Amplificacao'], label=estacao, color=cor_estacao[estacao], s=50)
            
#             # Destacar pontos com RMSE maior que 0.8
#             df_high_rmse = df_estacao[df_estacao['Qualidade'] > 0.8]
#             if not df_high_rmse.empty:
#                 ax1.scatter(df_high_rmse['DataHora'], df_high_rmse['Amplificacao'], edgecolor='red', facecolor='none', s=100, linewidth=1.5)

#     ax1.set_xlabel('Data')
#     ax1.set_ylabel('Amplificação')
#     ax1.set_title(f'Amplificação por Data para as Estações: {estacoes}\n{porcentagem_rmse_alto:.2f}% de pontos com RMSE > 0.8')
#     ax1.grid(True, linestyle='--', alpha=0.7)
#     ax1.legend(title='Estação')

#     # Adicionar os dados do fluxo solar F10.7
#     ax2 = ax1.twinx()
#     ax2.plot(filtered_data['Date'], filtered_data['SmoothedObsFlux'], label='Fluxo Solar F10.7 (Suavizado)', linewidth=2, color='orange')
#     ax2.set_ylabel('F10.7 (sfu)')
#     ax2.legend(loc='upper left')

#     # Ajustar a formatação do eixo x
#     plt.xticks(rotation=45)  # Rotaciona os rótulos do eixo x para melhor leitura
    
#     # Exibir o gráfico
#     plt.tight_layout()
#     plt.show()
    
def plot_amplificacao_por_data(eventos_sc_local, anos, estacoes):
    """
    Plota a amplificação por data para as estações especificadas e os anos fornecidos.

    Args:
        eventos_sc_local (aist): Lista de eventos com amplificação e tempo local calculado.
        anos (list): Lista de anos para filtrar os dados.
        estacoes (str): String com os códigos das estações separadas por espaço.
    """
    # Crie um DataFrame a partir dos eventos
    df = pd.DataFrame(eventos_sc_local)
    
    # Verifique se o DataFrame contém as colunas necessárias
    if 'Amplificacao' not in df.columns or 'DataHora' not in df.columns or 'RMSE' not in df.columns:
        print("A lista de eventos não contém dados de amplificação, DataHora ou RMSE.")
        return
    
    # Converter a coluna 'DataHora' para datetime, se ainda não estiver
    df['DataHora'] = pd.to_datetime(df['DataHora'])
    
    # Filtrar os dados pelos anos especificados
    df = df[df['DataHora'].dt.year.isin(anos)]
    
    # Filtrar pelas estações especificadas
    estacoes_lista = estacoes.split()
    df = df[df['Estacao'].isin(estacoes_lista)]
    
    # Verificar se há dados após o filtro
    if df.empty:
        print("Nenhum dado encontrado para os anos e estações especificados.")
        return
    
    # Calcular a porcentagem de pontos com RMSE > 0.8
    total_pontos = len(df)
    pontos_rmse_alto = len(df[df['RMSE'] > 0.8])
    porcentagem_rmse_alto = (pontos_rmse_alto / total_pontos) * 100 if total_pontos > 0 else 0
    
    # Definir cores específicas para cada estação
    cmap = plt.get_cmap('tab10')
    cores = cmap(np.linspace(0, 1, len(estacoes_lista)))
    cor_estacao = {estacao: cores[i] for i, estacao in enumerate(estacoes_lista)}

    # Criar o gráfico
    plt.figure(figsize=(14, 8))
    for estacao in estacoes_lista:
        df_estacao = df[df['Estacao'] == estacao]
        # print(estacao)
        if not df_estacao.empty:
            plt.scatter(df_estacao['DataHora'], df_estacao['Amplificacao'], label=estacao, color=cor_estacao[estacao])

            # # Destacar pontos com RMSE maior que 0.8
            # df_high_rmse = df_estacao[df_estacao['RMSE'] > 0.8]
            # if not df_high_rmse.empty:
            #     plt.scatter(df_high_rmse['DataHora'], df_high_rmse['Amplificacao'], edgecolor='red', facecolor='none', s=100, linewidth=1.5)

    # Configurar formato do eixo x
    plt.xlabel('Data')
    plt.ylabel('Amplificação')
    plt.title(f'Amplificação por Data para as Estações: {estacoes}\n{porcentagem_rmse_alto:.2f}% de pontos com RMSE > 0.8')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Ajustar a formatação do eixo x
    plt.xticks(rotation=45)  # Rotaciona os rótulos do eixo x para melhor leitura
    plt.legend(title='Estação')
    
    # Exibir o gráfico
    plt.tight_layout()
    plt.show()

def plotar_amplificacao_por_tempo_local(eventos_sc, estacao_filtrar):
    # Crie um DataFrame a partir dos eventos com amplificação
    df = pd.DataFrame(eventos_sc)
    
    # Verifique se o DataFrame contém as colunas necessárias
    if 'Amplificacao' not in df.columns or 'TempoLocal' not in df.columns:
        print("A lista de eventos não contém dados de amplificação ou TempoLocal.")
        return
    
    # Filtrar amplificações dentro do intervalo [-10, 10]
    df = df[(df['Amplificacao'] >= -10) & (df['Amplificacao'] <= 10)]
    
    # Filtrar por estação específica
    df = df[df['Estacao'] == estacao_filtrar]

    # Verificar se há dados após o filtro
    if df.empty:
        print(f"Nenhum dado encontrado para a estação '{estacao_filtrar}'.")
        return

    # Converta 'TempoLocal' para datetime, se ainda não estiver
    df['TempoLocal'] = pd.to_datetime(df['TempoLocal'])
    
    # Extrair a hora e minuto como decimal
    df['HoraDecimal'] = df['TempoLocal'].dt.hour + df['TempoLocal'].dt.minute / 60

    # Crie o gráfico
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x='HoraDecimal', y='Amplificacao', marker='o', color='b')

    # Configurar formato do eixo x
    plt.xlabel('Hora (decimal)')
    plt.ylabel('Amplificação')
    plt.title(f'Amplificação por Hora e Minuto - Estação: {estacao_filtrar}')
    plt.grid(True, linestyle='--', alpha=0.7)

    # Ajustar a formatação do eixo x
    plt.xticks(rotation=45)  # Rotaciona os rótulos do eixo x para melhor leitura

    # Exiba o gráfico
    plt.tight_layout()
    plt.show()

#%% save and load data
def save_data(data, file_path, metadata="- FelipeOT "):
    # Atualizando a lista de dados com entradas conjugadas
   

    readme = "Serie historica de dados de magnetometros de diferentes estações: "
    # Filtrando apenas as estações desejadas
    def filter_stations_data(stations_dict, stations):
        return {key: stations_dict[key] for key in stations if key in stations_dict}

    # Estações a serem filtradas
    stations = 'SJG GUI KNY SMS ASC KDU'.split()
    filtered_stations_info = filter_stations_data(stations_info, stations)

    # Atualizando os metadados com as estações filtradas
    metadata = readme + metadata + str(stations) + str(filtered_stations_info)

    # Salvando a lista e metadados no arquivo
    with open(file_path, 'wb') as file:
        # Primeiro, salva os metadados como texto (convertido para bytes)
        file.write(metadata.encode('utf-8'))
        file.write(b'\n===END_METADATA===\n')  # Separador para diferenciar metadados dos dados serializados
        # Depois, salva a lista serializada
        pickle.dump(data, file)
        
def load_data(file_path):
    # Carregando os metadados e a lista do arquivo
    with open(file_path, 'rb') as file:
        # Lê os metadados até o delimitador
        metadata = ""
        for line in file:
            if line.strip() == b'===END_METADATA===':
                break
            metadata += line.decode('utf-8')

        # Carrega a lista serializada
        data_list = pickle.load(file)
    
    return metadata, data_list   


#%%teste
# metadata, data_list = load_data('selected_statios_full_singnal.pkl')

# metadata2, data_list2 = load_data('selected_statios_just_events.pkl')
#%% testes 2
def derivativas2(data, campo='H_nT', filtro = 'wavelet'):
    dados_por_data = data
    for item in dados_por_data:
        df_dados = item['Dados']

        # Avalia se o DataFrame possui muitos NaN
        if df_dados.empty or df_dados[campo].isna().mean() > 0.20:  # Exemplo: mais de 20% de NaN
            # Caso haja muitos NaNs, atribui NaN aos campos de interesse
            item['Ponto_Esquerda_A'] = float('nan')
            item['Ponto_Direita_A'] = float('nan')
            item['Residual_A'] = float('nan')
            item['R_squared_A'] = float('nan')
            item['RMSE_A'] = float('nan')
            item['Amplitude'] = float('nan')

            for col in [f'{campo}_movmean', f'd{campo}_movmean', f'{campo}_ajuste',
                        'D_deg_ajuste', f'd{campo}_abs', f'd{campo}_absacumulado', f'd{campo}_drmsacumulado']:
                df_dados[col] = float('nan')

            df_dados['DateTime'] = float('nan')

            for suffix in ['D', 'E']:
                for metric in ['Ponto_Esquerda', 'Ponto_Direita', 'Residual', 'R_squared', 'RMSE', 'Amplitude']:
                    item[f'{metric}_{suffix}'] = float('nan')

            item['Dados'] = df_dados
            continue  # Passa para o próximo item

        # Calcula diferenças
        df_dados[f'd{campo}'] = df_dados[campo].diff()

        # Aplica média móvel
        df_dados[f'{campo}_movmean'] = df_dados[campo].rolling(window=20, center=True).mean()

        # Calcula a derivada
        df_dados[f'd{campo}_movmean'] = df_dados[f'{campo}_movmean'].diff()

        # Aplica a função de ajuste e calcula parâmetros
        if filtro == 'iir-pc5':
            ajuste, amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_iir_amplitude(df_dados, campo, low_cut=1.6e-3, high_cut=7e-3, fs=1/60, order=2)
        elif filtro == 'wavelet':
            ajuste, amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_wavelet_amplitude(df_dados, campo)
        else:
            print(f"Tipo de sinal '{sinal}' não reconhecido. Use 'pc5' ou 'H'.")
        
        df_dados[f'{campo}_ajuste'] = ajuste

        df_dados[f'd{campo}_abs'] = df_dados[f'd{campo}'].abs()
        df_dados[f'd{campo}_absacumulado'] = df_dados[f'd{campo}_abs'].cumsum()
        df_dados[f'd{campo}_drmsacumulado'] = df_dados[f'd{campo}_absacumulado'].diff()

        ajuste_abs, amplitude_D, ponto_esquerda_D, ponto_direita_D, residual_D, r_squared_D, rmse_D = caract_wavelet_amplitude(df_dados, f'd{campo}_abs')
        ajuste_acum, amplitude_E, ponto_esquerda_E, ponto_direita_E, residual_E, r_squared_E, rmse_E = caract_wavelet_amplitude(df_dados, f'd{campo}_absacumulado')

        df_dados[f'd{campo}_abs_ajuste'] = ajuste_abs
        df_dados[f'd{campo}_absacumulado_ajuste'] = ajuste_acum

        df_dados['DateTime'] = df_dados['TIME']

        # Atribui valores calculados ao item
        item['Ponto_Esquerda_A'] = ponto_esquerda
        item['Ponto_Direita_A'] = ponto_direita
        item['Residual_A'] = residual
        item['R_squared_A'] = r_squared
        item['RMSE_A'] = rmse
        item['Amplitude'] = amplitude

        item['Ponto_Esquerda_D'] = ponto_esquerda_D
        item['Ponto_Direita_D'] = ponto_direita_D
        item['Residual_D'] = residual_D
        item['R_squared_D'] = r_squared_D
        item['RMSE_D'] = rmse_D
        item['Amplitude_D'] = amplitude_D

        item['Ponto_Esquerda_E'] = ponto_esquerda_E
        item['Ponto_Direita_E'] = ponto_direita_E
        item['Residual_E'] = residual_E
        item['R_squared_E'] = r_squared_E
        item['RMSE_E'] = rmse_E
        item['Amplitude_E'] = amplitude_E

        item['Dados'] = df_dados

    return dados_por_data


def calculate_conjugate_difference2(data, campo='dH_nT'):
    # data_list = amp_sc_local 
    """
    Calcula a diferença nos valores do campo especificado entre cada estação e sua estação conjugada
    para cada "DataHora" disponível.

    Parâmetros:
        data_list (list): Lista de dicionários contendo dados das estações.
        campo (str): Nome do campo para o qual calcular a diferença. Default é 'dH_nT'.

    Retorna:
        list: Lista atualizada com a diferença adicionada como uma nova coluna "<campo>_diff" no DataFrame "Dados".
    """
    data_list = data
    # Cria um dicionário para indexar dados por estação e DataHora para fácil consulta
    data_index = {}
    for entry in data_list:
        station = entry.get('Estacao')
        datahora = entry.get('DataHora')
        
        if station and datahora:
            if station not in data_index:
                data_index[station] = {}
            data_index[station][datahora] = entry

    # Calcula a diferença no campo especificado entre cada estação e sua conjugada
    for entry in data_list:
        conjugate_station = entry.get('Conjugada')
        datahora = entry.get('DataHora')
        if conjugate_station and datahora:
            conjugate_entry = data_index.get(conjugate_station, {}).get(datahora)
            if conjugate_entry:
                entry['Dados'][f'{campo}_diff'] = entry['Dados'][campo] - conjugate_entry['Dados'][campo]
            else:
                entry['Dados'][f'{campo}_diff'] = None  # Definir como None se os dados da conjugada não estiverem disponíveis
        else:
            entry['Dados'][f'{campo}_diff'] = None  # Definir como None se não houver estação conjugada

    return data_list

def estatisticas2(data, campo='dH_nT_absacumulado_diff'):
    dados_por_data = data
    for item in dados_por_data:
        df_dados = item['Dados']

        # Cálculo do RMSE entre os valores do campo especificado
        mse = ((df_dados[campo]) ** 2).mean()
        rmse = np.sqrt(mse)
        item[f'RMSE_{campo}'] = rmse
                
    return dados_por_data

def amplificacao_D_estacoes_dcampo_abs(data, estacoes_conjugadas, campo = 'H_nT'):

    #opção para calcular amplificação para cada estação conjugada
    # estacoes_conjugadas_reverso = {v: k for k, v in estacoes_conjugadas.items()}
    eventos_sc = data
    eventos_com_amplificacao = []
    
    # Crie um dicionário para armazenar amplitudes por DataHora e Estação
    amplitudes_por_datahora = {}
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        amplitude = evento['Amplitude_D']
        
        if datahora not in amplitudes_por_datahora:
            amplitudes_por_datahora[datahora] = {}
        
        amplitudes_por_datahora[datahora][estacao] = amplitude
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        
        amplificacao = None
        
        if datahora in amplitudes_por_datahora:
            # estacao_conjugada_nome = estacoes_conjugadas.get(estacao, estacoes_conjugadas_reverso.get(estacao))
            estacao_conjugada_nome = estacoes_conjugadas.get(estacao, None)

            if estacao_conjugada_nome:
                conjugada_amplitude = amplitudes_por_datahora[datahora].get(estacao_conjugada_nome, None)
                
                if conjugada_amplitude is not None and conjugada_amplitude != 0:
                    estacao_amplitude = amplitudes_por_datahora[datahora].get(estacao, None)
                    if estacao_amplitude is not None:
                        amplificacao = estacao_amplitude / conjugada_amplitude
                else:
                    amplificacao = None
            else:
                amplificacao = None
        
        evento_com_amplificacao = evento.copy()
        evento_com_amplificacao[f'Amplificacao_{campo}'] = amplificacao
        eventos_com_amplificacao.append(evento_com_amplificacao)
    
    return eventos_com_amplificacao

def amplificacao_E_estacoes_dcampo_abs(data, estacoes_conjugadas, campo = 'H_nT'):

    #opção para calcular amplificação para cada estação conjugada
    # estacoes_conjugadas_reverso = {v: k for k, v in estacoes_conjugadas.items()}
    eventos_sc = data
    eventos_com_amplificacao = []
    
    # Crie um dicionário para armazenar amplitudes por DataHora e Estação
    amplitudes_por_datahora = {}
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        amplitude = evento['Amplitude_E']
        
        if datahora not in amplitudes_por_datahora:
            amplitudes_por_datahora[datahora] = {}
        
        amplitudes_por_datahora[datahora][estacao] = amplitude
    
    for evento in eventos_sc:
        datahora = evento['DataHora']
        estacao = evento['Estacao']
        
        amplificacao = None
        
        if datahora in amplitudes_por_datahora:
            # estacao_conjugada_nome = estacoes_conjugadas.get(estacao, estacoes_conjugadas_reverso.get(estacao))
            estacao_conjugada_nome = estacoes_conjugadas.get(estacao, None)

            if estacao_conjugada_nome:
                conjugada_amplitude = amplitudes_por_datahora[datahora].get(estacao_conjugada_nome, None)
                
                if conjugada_amplitude is not None and conjugada_amplitude != 0:
                    estacao_amplitude = amplitudes_por_datahora[datahora].get(estacao, None)
                    if estacao_amplitude is not None:
                        amplificacao = estacao_amplitude / conjugada_amplitude
                else:
                    amplificacao = None
            else:
                amplificacao = None
        
        evento_com_amplificacao = evento.copy()
        evento_com_amplificacao[f'Amplificacao_{campo}'] = amplificacao
        eventos_com_amplificacao.append(evento_com_amplificacao)
    
    return eventos_com_amplificacao
def caract_iir_amplitude(data, coluna, low_cut=1.6e-3, high_cut=7e-3, fs=1/60, order=2):
    """
    Função para calcular a amplitude de um sinal filtrado usando filtro IIR bandpass.

    Parâmetros:
        - dados_janela: DataFrame com os dados.
        - coluna: Nome da coluna com os valores do sinal.
        - low_cut: Frequência de corte inferior em Hz.
        - high_cut: Frequência de corte superior em Hz.
        - fs: Frequência de amostragem em Hz (1 amostra por 60 segundos = 1/60 Hz).
        - order: Ordem do filtro IIR.

    Retorno:
        - y_filtered: Sinal filtrado.
        - L: Amplitude entre o máximo e o mínimo do sinal filtrado.
        - ponto_esquerda: Posição e valor mínimo antes do máximo.
        - ponto_direita: Posição e valor máximo.
        - residual: Placeholder para valor residual.
        - r_squared: Coeficiente de determinação.
        - rmse: Erro médio quadrático.
    """
    dados_janela = data
    # Extrair dados da coluna específica e preencher NaNs com interpolação
    y_data = dados_janela[coluna].values
    y_data = pd.Series(y_data).interpolate().ffill().bfill().values

    # Remover infs
    mask = ~np.isinf(y_data)
    y_data = y_data[mask]

    # Verificar se temos dados suficientes após remover infs e NaNs
    if len(y_data) < 2 or np.isnan(y_data).all():
        return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    # Design do filtro IIR Butterworth bandpass
    nyquist = 0.5 * fs  # Frequência de Nyquist
    low = low_cut / nyquist
    high = high_cut / nyquist
    b, a = butter(order, [low, high], btype='band')

    # Aplicar o filtro
    y_filtered = filtfilt(b, a, y_data)

    # Índice do valor máximo na componente filtrada
    max_idx = np.argmax(y_filtered)

    # Procurar o índice do mínimo antes do máximo
    if max_idx > 0:
        min_idx = np.argmin(y_filtered[:max_idx])
    else:
        min_idx = max_idx  # Caso não haja valores antes do máximo, o mínimo será o próprio máximo

    # Amplitude do SI como a diferença entre o máximo e o mínimo
    L = y_filtered[max_idx] - y_filtered[min_idx]

    # Verificar se os índices estão dentro do tamanho de dados_janela
    if max_idx >= len(dados_janela) or min_idx >= len(dados_janela):
        return np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    # Posições dos valores à esquerda e à direita (mínimo antes do máximo e o próprio máximo)
    posicao_esquerda = dados_janela.iloc[min_idx]['TIME']
    posicao_direita = dados_janela.iloc[max_idx]['TIME']

    ponto_esquerda = [posicao_esquerda, y_filtered[min_idx]]
    ponto_direita = [posicao_direita, y_filtered[max_idx]]

    # Calcular o RMSE entre o sinal original e o sinal filtrado
    rmse = np.sqrt(np.mean((y_data - y_filtered) ** 2))

    # Cálculo do R²
    ss_res = np.sum((y_data - y_filtered) ** 2)
    ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # Calcular o valor residual (placeholder)
    residual = 0

    return y_filtered, L, ponto_esquerda, ponto_direita, residual, r_squared, rmse

#%%teste 3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def espectro_frequencia(data, campo='H_nT', amostragem=1, interpolacao=True):
    """
    Calcula o espectro de frequência por transformada de Fourier para uma lista de dados de séries temporais.
    
    Parâmetros:
    - dados_por_data: lista de dicionários, onde cada dicionário contém um DataFrame associado à chave 'Dados'.
    - campo: str, o nome da coluna no DataFrame que contém os dados da série temporal (default: 'H_nT').
    - amostragem: float, intervalo de amostragem da série temporal em minutos (default: 1).
    - interpolacao: bool, aplica interpolação para lidar com valores NaN na série temporal (default: True).
    
    Retorno:
    - Retorna a lista com o espectro de frequência adicionado a cada item.
    """
    dados_por_data = data
    for item in dados_por_data:
        df_dados = item['Dados']
        # print(f"{item['Estacao']} -> {item['DataHora']}:")
        # Obter a série temporal do campo especificado
        if interpolacao:
            serie_temporal = df_dados[campo].interpolate(method='linear', limit_direction='both').values
        else:
            serie_temporal = df_dados[campo].values
        
        # Aplicar a transformada de Fourier
        if len(serie_temporal) == 0:
            # Adicionar os resultados ao item com escala logarítmica
            item[f'FFT'] = pd.DataFrame({
                'Frequencia (mHz)': [0],  # Conversão para mHz
                f'Amplitude_{campo}': [0],
                f'Log10(Amplitude)_{campo}': [0]  # Adiciona pequena constante para evitar log(0)
            })
            continue
            print("{item['Estacao']} -> {item['DataHora']}:A série temporal está vazia. Verifique os dados de entrada.")
        else:
            fft_result = np.fft.fft(serie_temporal)
            frequencias = np.fft.fftfreq(len(serie_temporal), d=amostragem)
            # Apenas as frequências positivas
            frequencias_positivas = frequencias[:len(frequencias)//2]
            amplitudes = np.abs(fft_result)[:len(fft_result)//2]
        
        # Adicionar os resultados ao item com escala logarítmica
        item[f'FFT'] = pd.DataFrame({
            'Frequencia (mHz)': frequencias_positivas * 1000,  # Conversão para mHz
            f'Amplitude_{campo}': amplitudes,
            f'Log10(Amplitude)_{campo}': np.log10(amplitudes + 1e-10)  # Adiciona pequena constante para evitar log(0)
        })

    
    return dados_por_data



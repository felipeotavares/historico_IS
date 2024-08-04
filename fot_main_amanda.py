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
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator
import pandas as pd

# %% infos
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

# %% level 0 process
def find_header(file_path):
    station_name = os.path.basename(file_path)[:3].upper()
    line_count, kind = 0, np.nan  # Inicializa kind com np.nan
    
    with open(file_path, 'r') as file:
        for line in file:
            if " Reported               HDZF" in line:
                kind = "HDZF"
            elif " Reported               XYZ" in line:
                kind = "XYZF"
            elif line.startswith('DATE') or line.startswith(' DD MM YYYY'):
                if line.startswith(' DD MM YYYY'):
                    kind = 'EMBRACE'
                break
            line_count += 1
    
    return station_name, line_count, kind

def process_data(file_path):
    station_name, header_lines, kind = find_header(file_path)
    df = pd.read_csv(file_path, skiprows=header_lines, delim_whitespace=True)

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

# %% Data download -não esta retornando os arquivos corretos, url pode estar errada
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
                # Verifica se o arquivo já existe antes de baixar
                file_name = f'{station.lower()}{date.strftime("%Y%m%d")}.min'
                local_file_path = os.path.join(folder_save, file_name)
                if os.path.exists(local_file_path):
                    print(f"[{file_name}] Already on disk")
                else:
                    download_embrace(files_folder, date_str, station)
            elif local == 'Intermag':
                # Verifica se o arquivo já existe antes de baixar
                file_name = f'{station.lower()}{date.strftime("%Y%m%d")}vmin.min'
                local_file_path = os.path.join(folder_save, file_name)
                if os.path.exists(local_file_path):
                    print(f"[{file_name}] Already on disk")
                else:
                    intermagnet_download(files_folder, date_str, station)



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
        if os.path.isfile(file_path):
            # Ler os eventos do arquivo e converter a coluna TIME para decimal
            print(file_path)
            hora_especifica = read_data_eventos(file_path)
            
            hora_especifica['TIME'] = hora_especifica['TIME'].apply(time_to_decimal_24)
            all_data.append(hora_especifica)

    # Combina todos os DataFrames em um único DataFrame
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Obter todas as datas e horas únicas no arquivo de eventos
    lista_datas = combined_data[['DATE', 'TIME']].drop_duplicates().rename(columns={'DATE': 'Data', 'TIME': 'Hora'})
    
    return lista_datas

def get_date_selection(diretorio_base, event_dates):
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
                    city, lat, lon = stations_info[estacao]['city'], round(stations_info[estacao]['lat'], 1), round(stations_info[estacao]['lon'], 1)
                    dados_por_data.append({
                        'DataHora': data_hora,
                        'Hora': hora_decimal,
                        'Estacao': estacao,
                        'Dados': df,
                        'Cidade': city,
                        'Latitude': lat,
                        'Longitude': lon
                    })
    
    return dados_por_data
# %% Processa dados level 1
def calcular_tempo_local(eventos_sc):
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

def amplificacao_estacoes(eventos_sc, estacoes_conjugadas):

    #opção para calcular amplificação para cada estação conjugada
    # estacoes_conjugadas_reverso = {v: k for k, v in estacoes_conjugadas.items()}

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


def derivativas(dados_por_data):
    eventos_sc = []

    for item in dados_por_data:
        df_dados = item['Dados']
        # hora_central = item['Hora']
    
        # Filtro passabaixa
        # dados_janela['H_nT_filtered'] = filtro_passa_baixa(dados_janela['dH_nT'],0.001,1,1)
        df_dados['H_nT_movmean'] = df_dados['H_nT'].rolling(window=5, center=True).mean()
        # Calculando derivada de H filtrado
        df_dados['dH_nT_movmean'] = df_dados['H_nT_movmean'].diff()
        # Calculo função sigmoid
        df_dados['H_nT_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_ajuste(df_dados, 'H_nT_movmean')
        
        # Adicionar o DataFrame recortado ao resultado
        eventos_sc.append({
            'DataHora': item['DataHora'],
            'Hora': item['Hora'],
            'Estacao': item['Estacao'],
            'Dados': df_dados,
            'Cidade': item['Cidade'],
            'Latitude': item['Latitude'],
            'Longitude': item['Longitude'],
            'Amplitude': amplitude,
            # 'Amplitude_ponto_esq': amp_ponto_esq,
            # 'Amplitude_ponto_dir': amp_ponto_dir,
            'Ponto_Esquerda': ponto_esquerda,
            'Ponto_Direita': ponto_direita,
            'Residual': residual,
            'R_squared': r_squared,
            'RMSE': rmse
        })
    
    return eventos_sc

def recorte_evento(dados_por_data, tamanho_janela):
    eventos_sc = []

    for item in dados_por_data:
        df_dados = item['Dados']
        hora_central = item['Hora']
        
        # Calcular o intervalo de tempo
        janela_inicio = hora_central - tamanho_janela / 2
        janela_fim = hora_central + tamanho_janela / 2
        
        # Filtrar o DataFrame 'Dados' para manter apenas os dados dentro do intervalo
        df_recortado = df_dados[(df_dados['TIME'] >= janela_inicio) & (df_dados['TIME'] <= janela_fim)]
        
        # Adicionar o DataFrame recortado ao resultado
        eventos_sc.append({
            'DataHora': item['DataHora'],
            'Hora': item['Hora'],
            'Estacao': item['Estacao'],
            'Dados': df_recortado,
            'Cidade': item['Cidade'],
            'Latitude': item['Latitude'],
            'Longitude': item['Longitude']
        })
    
    return eventos_sc

def processa_dados_estacoes(df_global, datas_horas, janela, estacoes_conjugadas):
    """
    Parâmetros:
    df_global (DataFrame): DataFrame contendo os dados agrupados.
    datas_horas (DataFrame): DataFrame contendo as datas e horas no formato 'AAAA-MM-DD' e horas no formato float.
    janela (int): Tamanho da janela em torno da hora especificada.
    estacoes_conjugadas (dict): Dicionário com pares de estações conjugadas.

    Retorna:
    list: Lista de dicionários, cada um com uma data e uma lista de estações com seus dados e diferenças calculadas.
    """
    # df_global = files_by_date
    # datas_horas = event_dates
    # janela
    # estacoes_conjugadas

    # Inicializando uma lista para armazenar os dados agrupados por data
    lista_dados_agrupados = []

    # Iterando sobre todas as datas e horas especificadas
    for data, group in datas_horas.groupby('Data'):
        dados_por_data = []
        for _, row in group.iterrows():
            hora = row['Hora']

            # Buscando a linha que corresponde à data
            linha_data = df_global[df_global['Data'] == data]

            # Iterando sobre todas as estações disponíveis na data especificada
            for index, linha in linha_data.iterrows():
                dados_por_estacao = linha['Dados_por_Estacao']
                
                for estacao in dados_por_estacao['Estacao'].unique():
                    # Buscando a linha que corresponde à estação atual
                    linha_estacao = dados_por_estacao[dados_por_estacao['Estacao'] == estacao]
                    
                    # Extraindo o DataFrame de dados da estação
                    if not linha_estacao.empty:
                        dados_estacao = linha_estacao.iloc[0]['Dados']
                        
                        # Buscando o índice correspondente à hora especificada
                        indice_hora = dados_estacao[dados_estacao['TIME'] == hora].index.tolist()
                        
                        if indice_hora:
                            indice_hora = indice_hora[0]
                            inicio_janela = max(0, indice_hora - janela // 2)
                            fim_janela = min(len(dados_estacao) - 1, indice_hora + janela // 2)
                            
                            # Verificando se a janela tem tamanho suficiente
                            if fim_janela - inicio_janela + 1 >= 20:
                                #verbose
                                print(estacao)
                                print(data)
                                # Extraindo a janela de dados
                                dados_janela = dados_estacao.iloc[inicio_janela:fim_janela + 1]
                                # Filtro passabaixa
                                # dados_janela['H_nT_filtered'] = filtro_passa_baixa(dados_janela['dH_nT'],0.001,1,1)
                                dados_janela['H_nT_movmean'] = dados_janela['H_nT'].rolling(window=5, center=True).mean()
                                # Calculando derivada de H filtrado
                                dados_janela['dH_nT_movmean'] = dados_janela['H_nT_movmean'].diff()
                                # Calculo função sigmoid
                                dados_janela['H_nT_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_ajuste(dados_janela, 'H_nT_movmean')
                                print(ponto_esquerda)
                                print(ponto_direita)

                                
                            # Adicionando os dados à lista de dados por data
                            dados_por_data.append({
                                'Hora': hora,
                                'Estacao': estacao,
                                'Dados_Janela': dados_janela,
                                'Amplitude': amplitude,
                                'Latitude': caract_latitude(estacao, stations_info),
                                'Longitude': caract_longitude(estacao, stations_info),
                                'Ponto_Esquerda': ponto_esquerda,
                                'Ponto_Direita': ponto_direita,
                                'Residual': residual,
                                'R_squared': r_squared,
                                'RMSE': rmse
                            })

        # Adicionando os dados por data à lista agrupada
        lista_dados_agrupados.append({
            'Data': data,
            'Estacoes': dados_por_data
        })
    
    return lista_dados_agrupados



# %% tools
# Função para converter HH:MM:SS.000 para decimal entre 0 e 24
def time_to_decimal_24(time_str):
    time_obj = datetime.strptime(time_str, '%H:%M:%S.%f').time()
    decimal_time = time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600 + time_obj.microsecond / 3600000000
    return decimal_time

# %% caracteristicas extrator
# Função sigmoide
def sigmoid(x, L, x0, k, b):
    return L / (1 + np.exp(-k * (x - x0))) + b

def caract_ajuste(dados_janela, coluna):
    x_data = np.arange(len(dados_janela))
    y_data = dados_janela[coluna].values

    # Preencher NaNs com interpolação linear
    y_data = pd.Series(y_data).interpolate().ffill().bfill().values

    # Remover infs
    mask = ~np.isinf(y_data)
    x_data = x_data[mask]
    y_data = y_data[mask]

    # Verificar se temos dados suficientes após remover infs e NaNs
    if len(x_data) < 2 or np.isnan(y_data).all():
        return np.full(len(dados_janela), np.nan), np.nan, [np.nan, np.nan], [np.nan, np.nan], np.nan, np.nan, np.nan

    # Chute inicial para os parâmetros
    p0 = [max(y_data), np.median(x_data), 1, min(y_data)]

    # Ajuste da curva sigmoide com tratamento de exceção
    try:
        with warnings.catch_warnings():
            # warnings.simplefilter('ignore', OptimizeWarning)
            params, _ = curve_fit(sigmoid, x_data, y_data, p0, method='dogbox', maxfev=10000)
        L, x0, k, b = params

        # Curva ajustada
        y_fit = sigmoid(x_data, L, x0, k, b)

        # display(y_fit)
        # Valores máximo e mínimo na curva ajustada
        max_idx = np.argmax(y_fit)
        min_idx = np.argmin(y_fit)
        
        # Posições dos valores à esquerda e à direita
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
        # display(r_squared)

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


# %% Plot data
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


# %% Gera lista de todos dados agrupados por estação
files_folder = diretorio_base = os.getcwd()
stations = 'SJG GUI KNY SMS ASC KDU'.split()

folder_path = "sc_eventos"
event_dates = get_events_dates(folder_path)

# download_files(files_folder, event_dates['Data'], stations)
print(event_dates)


# %% testes
event_dates['Data'] = pd.to_datetime(event_dates['Data'])
# filtra dados por data
dados_por_data = get_date_selection(os.path.join(files_folder, 'Dados'),event_dates)

# Define o tamanho da janela em horas decimais (exemplo: 15.5 é as 15h e 30 min)
tamanho_janela =1

# Chame a função para recortar os dados
eventos_sc = recorte_evento(dados_por_data, tamanho_janela)

eventos_sc_est = derivativas(eventos_sc)

estacoes_conjugadas = {
    'SMS': 'SJG',
    'ASC': 'GUI',
    'KDU': 'KNY'
}
amp_sc = amplificacao_estacoes(eventos_sc_est, estacoes_conjugadas)

amp_sc_local = calcular_tempo_local(amp_sc)

plotar_amplificacao_por_tempo_local(amp_sc_local,'SMS')

# # Definindo os anos a serem plotados
anos = [2019, 2020, 2021, 2022, 2023, 2024]

# plot_amplificacao_por_data(amp_sc_local, [2014,2015,2016], 'SJG GUI KNY SMS ASC KDU')



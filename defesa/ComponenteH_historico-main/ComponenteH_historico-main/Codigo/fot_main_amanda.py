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
from scipy.signal import butter, lfilter  # Para pulsação
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit
from scipy.optimize import OptimizeWarning
import warnings
from matplotlib.dates import DateFormatter, DayLocator
import matplotlib.dates as mdates
import seaborn as sns
from datetime import timedelta

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
# %% level 1 process
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
        hora_central = item['Hora']
    
        # Filtro passabaixa
        # dados_janela['H_nT_filtered'] = filtro_passa_baixa(dados_janela['dH_nT'],0.001,1,1)
        df_dados['H_nT_movmean'] = df_dados['H_nT'].rolling(window=5, center=True).mean()
        # Calculando derivada de H filtrado
        df_dados['dH_nT_movmean'] = df_dados['H_nT_movmean'].diff()
        # Calculo função sigmoid
        df_dados['H_nT_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_ajuste(df_dados, 'H_nT_movmean')
        # Extraindo amplitude 
        # amplitude, amp_ponto_esq, amp_ponto_dir = caract_amplitudeV2(dados_janela, 'dH_nT_movmean', 'H_nT_movmean')
        # amplitude, amp_ponto_esq, amp_ponto_dir = caract_amplitudeV4(df_dados, 'H_nT_movmean', 'H_nT_movmean')
        # display(amp_ponto_esq)
        # display(amp_ponto_dir)
        # dst = fget_dst(df_dados['DataHora'])
        
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
                                display(estacao)
                                display(data)
                                # Extraindo a janela de dados
                                dados_janela = dados_estacao.iloc[inicio_janela:fim_janela + 1]
                                # Filtro passabaixa
                                # dados_janela['H_nT_filtered'] = filtro_passa_baixa(dados_janela['dH_nT'],0.001,1,1)
                                dados_janela['H_nT_movmean'] = dados_janela['H_nT'].rolling(window=5, center=True).mean()
                                # Calculando derivada de H filtrado
                                dados_janela['dH_nT_movmean'] = dados_janela['H_nT_movmean'].diff()
                                # Calculo função sigmoid
                                dados_janela['H_nT_ajuste'], amplitude, ponto_esquerda, ponto_direita, residual, r_squared, rmse = caract_ajuste(dados_janela, 'H_nT_movmean')
                                # Extraindo amplitude 
                                # amplitude, amp_ponto_esq, amp_ponto_dir = caract_amplitudeV2(dados_janela, 'dH_nT_movmean', 'H_nT_movmean')
                                # amplitude, amp_ponto_esq, amp_ponto_dir = caract_amplitudeV4(dados_janela, 'H_nT_movmean', 'H_nT_movmean')
                                display(amp_ponto_esq)
                                display(amp_ponto_dir)

                                
                            # Adicionando os dados à lista de dados por data
                            dados_por_data.append({
                                'Hora': hora,
                                'Estacao': estacao,
                                'Dados_Janela': dados_janela,
                                'Amplitude': amplitude,
                                'Amplitude_ponto_esq': amp_ponto_esq,
                                'Amplitude_ponto_dir': amp_ponto_dir,
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

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# %% caracteristicas extrator
# Função sigmoide
def sigmoid(x, L, x0, k, b):
    return L / (1 + np.exp(-k * (x - x0))) + b

# x_data = np.arange(50)
# L= params[0]
# x0= params[1]
# k= params[2]
# b= params[3]

# A = L / (1 + np.exp(-k * (x_data - x0))) + b

# B = np.exp(-k * (x_data - x0))



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

def filtro_passa_baixa(data,cutoff_frequency, sampling_frequency, order=5):
    """
    Calcula a derivada de uma coluna do DataFrame e aplica um filtro passa-baixa.

    Parâmetros:
    data (pd.DataFrame): DataFrame contendo os dados.
    column (str): Nome da coluna para calcular a derivada.
    cutoff_frequency (float): Frequência de corte do filtro passa-baixa.
    sampling_frequency (float): Frequência de amostragem dos dados.
    order (int): Ordem do filtro Butterworth (padrão é 5).

    Retorna:
    pd.DataFrame: DataFrame original com duas novas colunas:
                  'column_diff' e 'column_diff_filtered'.
    """
    
    def butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs  # Frequência de Nyquist
        normal_cutoff = cutoff / nyq  # Frequência de corte normalizada
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def lowpass_filter(data, cutoff, fs, order=5):
        b, a = butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    # Aplicando o filtro passa-baixa
    data = lowpass_filter(data, cutoff_frequency, sampling_frequency, order)

    return data

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

def caract_amplitude(dados_janela):
    centro = len(dados_janela) // 2

    # Certificando-se de que o centro e as posições à direita/esquerda estão dentro dos limites do DataFrame
    if centro - 10 >= 0 and centro + 10 < len(dados_janela):
        valor_direita = dados_janela.iloc[centro + 10]['H_nT']
        valor_esquerda = dados_janela.iloc[centro - 10]['H_nT']
        
        # Posições dos valores laterais
        posicao_direita = dados_janela.iloc[centro + 10]['TIME']
        posicao_esquerda = dados_janela.iloc[centro - 10]['TIME']
    
        # Calculando a diferença entre os valores
        diferenca = valor_direita - valor_esquerda
        
        ponto_esquerda = [posicao_esquerda,valor_esquerda]
        ponto_direita = [posicao_direita,valor_direita]
        
        return round(diferenca, 3), ponto_esquerda, ponto_direita
    else:
        return None, None, None  # ou outro tratamento caso não esteja dentro dos limites
    
def caract_amplitudeV2(dados_janela, campo_indices = 'H_nT_movmean',campo_valor = 'H_nT_movmean' ):
    # Substituir NaN pelos valores da vizinhança
    dados_janela[campo_indices] = dados_janela[campo_indices].ffill().bfill()
    
    # Verificar se há valores NaN ou NoneType no campo especificado após a substituição
    if dados_janela[campo_indices].isnull().any() or dados_janela[campo_indices].isna().any():
        print(f"Há valores NaN ou NoneType em '{campo_indices}' após substituição pelos valores da vizinhança.")
        return None, None, None  # ou faça algum tratamento adequado
    
    # Encontrar índice do centro dos dados
    centro = len(dados_janela) // 2
    
    # Encontrar índice do primeiro zero à esquerda do centro
    dados_esquerda = dados_janela.iloc[:centro]
    if dados_esquerda.empty or not (dados_esquerda[campo_indices] <= 0).any():
        print(f"Não há valores negativos à esquerda do centro para '{campo_indices}'.")
        return None, None, None
    indice_esq = dados_esquerda[dados_esquerda[campo_indices] <= 0].index[-1]
      
    # Encontrar índice do primeiro zero à direita do centro
    dados_direita = dados_janela.iloc[centro:]
    if dados_direita.empty or not (dados_direita[campo_indices] <= 0).any():
        print(f"Não há valores negativos à direita do centro para '{campo_indices}'.")
        return None, None, None
    indice_dir = dados_direita[dados_direita[campo_indices] <= 0].index[0]
    lista_indice = dados_direita[dados_direita[campo_indices] <= 0]
    
    # display("lista_indice")
    # display(lista_indice)
    # display(indice_dir)
    
    valor_esq = dados_janela.loc[indice_esq, campo_valor]
    valor_dir = dados_janela.loc[indice_dir, campo_valor]

    # Posições dos valores à esquerda e à direita
    posicao_esquerda = dados_janela.loc[indice_esq, 'TIME']
    posicao_direita = dados_janela.loc[indice_dir, 'TIME']
    
    diferenca = valor_dir - valor_esq
    
    ponto_esquerda = [posicao_esquerda, valor_esq]
    ponto_direita = [posicao_direita, valor_dir]
    
    return round(diferenca, 3), ponto_esquerda, ponto_direita

def caract_amplitudeV3(dados_janela, campo_indices='dH_nT_movmean', campo_valor='H_nT_movmean'):
    # Substituir NaN pelos valores da vizinhança
    dados_janela[campo_indices] = dados_janela[campo_indices].ffill().bfill()

    # Verificar se há valores NaN ou NoneType no campo especificado após a substituição
    if dados_janela[campo_indices].isnull().any() or dados_janela[campo_indices].isna().any():
        print(f"Há valores NaN ou NoneType em '{campo_indices}' após substituição pelos valores da vizinhança.")
        return None, None, None  # ou faça algum tratamento adequado

    # Encontrar índice do centro dos dados
    centro = len(dados_janela) // 2

    # Encontrar índice do primeiro pico mínimo à esquerda do centro
    dados_esquerda = dados_janela.iloc[:centro]
    if dados_esquerda.empty or not (dados_esquerda[campo_indices].diff().fillna(0) < 0).any():
        print(f"Não há pico mínimo à esquerda do centro para '{campo_indices}'.")
        return None, None, None
    indice_esq = dados_esquerda[dados_esquerda[campo_indices].diff().fillna(0) < 0].index[-1]

    # Encontrar índice do primeiro pico mínimo à direita do centro
    dados_direita = dados_janela.iloc[centro:]
    if dados_direita.empty or not (dados_direita[campo_indices].diff().fillna(0) > 0).any():
        print(f"Não há pico mínimo à direita do centro para '{campo_indices}'.")
        return None, None, None
    indice_dir = dados_direita[dados_direita[campo_indices].diff().fillna(0) > 0].index[0]

    valor_esq = dados_janela.loc[indice_esq, campo_valor]
    valor_dir = dados_janela.loc[indice_dir, campo_valor]

    # Posições dos valores à esquerda e à direita
    posicao_esquerda = dados_janela.loc[indice_esq, 'TIME']
    posicao_direita = dados_janela.loc[indice_dir, 'TIME']

    diferenca = valor_dir - valor_esq

    ponto_esquerda = [posicao_esquerda, valor_esq]
    ponto_direita = [posicao_direita, valor_dir]

    return round(diferenca, 3), ponto_esquerda, ponto_direita

def caract_amplitudeV4(dados_janela, campo_indices='dH_nT_movmean', campo_valor='H_nT_movmean'):
    # Substituir NaN pelos valores da vizinhança
    dados_janela[campo_indices] = dados_janela[campo_indices].ffill().bfill()

    # Verificar se há valores NaN ou NoneType no campo especificado após a substituição
    if dados_janela[campo_indices].isnull().any() or dados_janela[campo_indices].isna().any():
        print(f"Há valores NaN ou NoneType em '{campo_indices}' após substituição pelos valores da vizinhança.")
        return None, None, None  # ou faça algum tratamento adequado

    # Encontrar índice do centro dos dados
    centro = len(dados_janela) // 2

    # Encontrar índice do menor valor à esquerda do centro
    dados_esquerda = dados_janela.iloc[:centro]
    if dados_esquerda.empty:
        print(f"Não há dados à esquerda do centro para '{campo_indices}'.")
        return None, None, None
    indice_min_esq = dados_esquerda[campo_indices].idxmin()

    # Encontrar índice do maior valor à direita do centro
    dados_direita = dados_janela.iloc[centro:]
    if dados_direita.empty:
        print(f"Não há dados à direita do centro para '{campo_indices}'.")
        return None, None, None
    indice_max_dir = dados_direita[campo_indices].idxmax()

    valor_min_esq = dados_janela.loc[indice_min_esq, campo_valor]
    valor_max_dir = dados_janela.loc[indice_max_dir, campo_valor]

    # Posições dos valores à esquerda e à direita
    posicao_esquerda = dados_janela.loc[indice_min_esq, 'TIME']
    posicao_direita = dados_janela.loc[indice_max_dir, 'TIME']

    diferenca = valor_max_dir - valor_min_esq

    ponto_esquerda = [posicao_esquerda, valor_min_esq]
    ponto_direita = [posicao_direita, valor_max_dir]

    return round(diferenca, 3), ponto_esquerda, ponto_direita


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

def calcular_amplificacao(lista_dados_agrupados, estacoes_conjugadas):
    # Criar um dicionário reverso para facilitar a busca de estações conjugadas
    estacoes_conjugadas_reverso = {v: k for k, v in estacoes_conjugadas.items()}

    nova_lista_dados_agrupados = []

    for dado in lista_dados_agrupados:
        novas_estacoes = []
        for estacao in dado['Estacoes']:
            estacao_nome = estacao['Estacao']

            conjugada_nome = estacoes_conjugadas.get(estacao_nome, estacoes_conjugadas_reverso.get(estacao_nome))

            # Verificar se existe uma estação conjugada
            if conjugada_nome:
                conjugada_estacao = next((e for e in dado['Estacoes'] if e['Estacao'] == conjugada_nome), None)
                
                if conjugada_estacao and conjugada_estacao['Amplitude'] is not None and estacao['Amplitude'] is not None:
                    if conjugada_estacao['Amplitude'] != 0:  # Evitar divisão por zero
                        estacao['Amplificacao'] = estacao['Amplitude'] / conjugada_estacao['Amplitude']
                    else:
                        estacao['Amplificacao'] = None
                else:
                    estacao['Amplificacao'] = None
            else:
                estacao['Amplificacao'] = None
            
            novas_estacoes.append(estacao)

        nova_lista_dados_agrupados.append({
            'Data': dado['Data'],
            'Estacoes': novas_estacoes
        })
    
    return nova_lista_dados_agrupados
# %% Plot data
def plotar_media_amplificacao_por_hora(eventos_sc, estacao_filtrar):
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

    # Converta 'TempoLocal' para datetime
    df['TempoLocal'] = pd.to_datetime(df['TempoLocal'])

    # Certificar que 'Amplificacao' é numérica
    df['Amplificacao'] = pd.to_numeric(df['Amplificacao'], errors='coerce')

    # Filtrar dados para garantir que não existam valores NaN na amplificação
    df = df.dropna(subset=['Amplificacao'])

    # Definir o intervalo de 1 hora
    df.set_index('TempoLocal', inplace=True)
    df_resampled = df.resample('H').mean()  # Resample para 1 hora e calcula a média
    
    # Crie o gráfico
    plt.figure(figsize=(12, 6))
    plt.plot(df_resampled.index, df_resampled['Amplificacao'], marker='o', linestyle='-', color='b')

    # Configurar formato do eixo x
    plt.xlabel('Tempo')
    plt.ylabel('Média da Amplificação')
    plt.title(f'Média da Amplificação por Intervalos de 1 Hora - Estação: {estacao_filtrar}')
    plt.grid(True, linestyle='--', alpha=0.7)

    # Ajustar a formatação do eixo x
    # plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    # plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))
    # plt.gcf().autofmt_xdate()  # Rotaciona os rótulos do eixo x para melhor visualização

    # Exiba o gráfico
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

def plot_amplificacao_por_data(lista_dados_agrupados, anos_selecionados, stations, amplificacao_min=None, amplificacao_max=None):
    # Define a paleta de cores para as estações
    cores = ['b', 'g', 'r', 'c', 'm', 'y']
    
    # Mapa de cores para estações
    mapa_cores = {}
    
    # Dicionário para armazenar os dados por estação
    dados_por_estacao = {}
    
    # Converte a string de estações para uma lista
    estações_selecionadas = stations.split()
    
    # Contadores para estações destacadas e total de estações
    total_estacoes = 0
    estacoes_destacadas = 0
    
    plt.figure(figsize=(12, 6))  # Ajustei o tamanho do gráfico para melhor visualização
    
    # Itera sobre a lista de dados agrupados
    for dados_agrupados in lista_dados_agrupados:
        data = pd.to_datetime(dados_agrupados['Data'])  # Converte a data para datetime
        ano = data.year
        
        if ano in anos_selecionados:
            estacoes = dados_agrupados.get('Estacoes', [])  # Lidando com o caso de não haver 'Estacoes' definido
            
            for estacao in estacoes:
                estacao_nome = estacao['Estacao']
                
                # Verifica se a estação está na lista de estações selecionadas
                if estacao_nome in estações_selecionadas:
                    if estacao_nome not in mapa_cores:
                        mapa_cores[estacao_nome] = cores[len(mapa_cores) % len(cores)]
                    
                    amplificacao = estacao.get('Amplificacao')  # 'Amplificacao' deve existir, não precisa verificar por None
                    r_squared = estacao.get('R_squared')  # Verifica R_squared
                    
                    if not pd.isnull(amplificacao) and not pd.isnull(r_squared):
                        if estacao_nome not in dados_por_estacao:
                            dados_por_estacao[estacao_nome] = {'datas': [], 'amplificacoes': [], 'r_squared': []}
                        
                        dados_por_estacao[estacao_nome]['datas'].append(data)
                        dados_por_estacao[estacao_nome]['amplificacoes'].append(amplificacao)
                        dados_por_estacao[estacao_nome]['r_squared'].append(r_squared)
                        
                        total_estacoes += 1
                        if r_squared > 0.9:
                            estacoes_destacadas += 1

    # Plotagem dos dados acumulados por estação
    for estacao_nome, dados in dados_por_estacao.items():
        # Marca os pontos com R_squared > 0.9
        plt.scatter(dados['datas'], dados['amplificacoes'], color=mapa_cores.get(estacao_nome, 'k'), label=None)
        plt.scatter([dados['datas'][i] for i in range(len(dados['r_squared'])) if dados['r_squared'][i] > 0.9],
                    [dados['amplificacoes'][i] for i in range(len(dados['r_squared'])) if dados['r_squared'][i] > 0.9],
                    color=mapa_cores.get(estacao_nome, 'k'), marker='o', s=100, edgecolor='black', linewidth=1.5, label=None)

    # Calcula a porcentagem de estações destacadas
    if total_estacoes > 0:
        percent_destacadas = (estacoes_destacadas / total_estacoes) * 100
    else:
        percent_destacadas = 0.0
    
    # Configurações do gráfico
    plt.xlabel('Data')
    plt.ylabel('Amplificação')
    plt.title(f'Amplificação por Data de Cada Estação nos Anos {", ".join(map(str, anos_selecionados))} ({percent_destacadas:.1f}% destacadas)')
    
    # Criação da legenda única
    handles = []
    labels = []
    for estacao_nome in dados_por_estacao:
        handles.append(plt.scatter([], [], color=mapa_cores.get(estacao_nome, 'k')))
        labels.append(estacao_nome)
    
    plt.legend(handles, labels, loc='best')
    
    plt.grid(True)
    
    # Formatação do eixo x para mostrar dia, mês e ano
    date_format = DateFormatter('%d-%m-%Y')
    plt.gca().xaxis.set_major_formatter(date_format)
    
    # Ajuste dos intervalos dos ticks para mostrar mais datas
    plt.gca().xaxis.set_major_locator(DayLocator(interval=30))  # Intervalo de 7 dias
    
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Definindo os limites do eixo y se especificado
    if amplificacao_min is not None and amplificacao_max is not None:
        plt.ylim(amplificacao_min, amplificacao_max)
    
    # Exibe o gráfico
    plt.show()
    
def plot_data_conjugadasV2(lista_dados_agrupados, target_date, target_stations, estacoes_conjugadas=None, event_index=0, campos=["H_nT", "D_nT"], ver_caracteristicas=True):
    import matplotlib.pyplot as plt
    import pandas as pd

    # Convert the target_date to a datetime object for comparison
    target_date = pd.to_datetime(target_date)
    
    # Vector to store possible "Hora" values
    horas_possiveis = []
    
    # Iterate through lista_dados_agrupados to find target_date and possible "Hora" values
    for data_entry in lista_dados_agrupados:
        data_date = pd.to_datetime(data_entry["Data"])
        if data_date == target_date:
            for station_data in data_entry["Estacoes"]:
                hora = station_data["Hora"]
                if hora not in horas_possiveis:
                    horas_possiveis.append(hora)
    
    # Print possible "Hora" values found
    print(f"Valores possíveis de 'Hora' para a data {target_date}: {horas_possiveis}")
    
    # Prepare subplots
    num_plots = len(target_stations)
    fig, axes = plt.subplots(num_plots, 1, figsize=(10, 6*num_plots))

    if num_plots == 1:
        axes = [axes]  # Ensure axes is a list even if there is only one plot

    # Iterate through each target station
    for i, target_station in enumerate(target_stations):
        if estacoes_conjugadas is None or target_station not in estacoes_conjugadas:
            station_pair = [target_station]
        else:
            station_pair = [target_station, estacoes_conjugadas[target_station]]
        
        # Check if the stations exist in the data
        found_stations = []
        for data_entry in lista_dados_agrupados:
            data_date = pd.to_datetime(data_entry["Data"])
            if data_date == target_date:
                for station_data in data_entry["Estacoes"]:
                    estacao = station_data["Estacao"]
                    if estacao in station_pair:
                        # Extract the DataFrame with the magnetic field data
                        df = station_data["Dados_Janela"]
                        
                        # Additional station information
                        hora = station_data["Hora"]
                        amplitude = station_data["Amplitude"]
                        latitude = station_data["Latitude"]
                        longitude = station_data["Longitude"]
                        ponto_amp_esq = station_data.get("Amplitude_ponto_esq", None)
                        ponto_amp_dir = station_data.get("Amplitude_ponto_dir", None)
                        r_squared = station_data["R_squared"]
                        rmse = station_data["RMSE"]
                        
                        # Check if this hora matches the event_index
                        if hora == horas_possiveis[event_index]:
                            # Plot the data on the corresponding subplot
                            ax = axes[i]
                            for campo in campos:
                                if campo in df.columns:
                                    ax.plot(df["TIME"], df[campo], label=f"{campo} - {estacao}")
                                    
                            # Plot amplitude_x and amplitude_y as points if data is valid
                            if ponto_amp_esq is not None and ponto_amp_dir is not None:
                                ax.scatter(ponto_amp_esq[0], ponto_amp_esq[1], color='red')
                                ax.scatter(ponto_amp_dir[0], ponto_amp_dir[1], color='blue')
                                
                            ax.set_xlabel("Time")
                            ax.set_ylabel("Magnetic Field (nT)")
                            ax.set_title(f"Magnetic Field Components on {target_date.strftime('%Y-%m-%d')} at {target_station}")
                            ax.legend()
                            ax.grid(True)
                            
                            # Display characteristics if ver_caracteristicas is True
                            if ver_caracteristicas:
                                # Fixed text position in the bottom right corner
                                text_x = 0.95  # X position in axes coordinates
                                text_y = 0.8 if estacao == target_station else 0.35  # Adjusted for multiple stations

                                ax.text(text_x, text_y, f"Estacao: {estacao}\nHora: {hora}\nAmplitude: {amplitude}\nLatitude: {latitude}\nLongitude: {longitude}\nR^2: {r_squared}", 
                                        transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.5), 
                                        verticalalignment='top', horizontalalignment='right')
                            
                            found_stations.append(estacao)
        
        # If not all stations were found
        if not found_stations:
            not_found_stations = set(station_pair) - set(found_stations)
            not_found_stations_str = ", ".join(not_found_stations)
            print(f"No data found for date {target_date.strftime('%Y-%m-%d')} and stations: {not_found_stations_str}.")
    
    plt.tight_layout()
    plt.show()
        
def plot_data_conjugadas(lista_dados_agrupados, target_date, target_stations, estacoes_conjugadas, event_index=0, campos=["H_nT", "D_nT"], ver_caracteristicas=True):
    # Convert the target_date to a datetime object for comparison
    target_date = pd.to_datetime(target_date)
    
    # Vector to store possible "Hora" values
    horas_possiveis = []
    
    # Iterate through lista_dados_agrupados to find target_date and possible "Hora" values
    for data_entry in lista_dados_agrupados:
        data_date = pd.to_datetime(data_entry["Data"])
        if data_date == target_date:
            for station_data in data_entry["Estacoes"]:
                hora = station_data["Hora"]
                if hora not in horas_possiveis:
                    horas_possiveis.append(hora)
    
    # Print possible "Hora" values found
    print(f"Valores possíveis de 'Hora' para a data {target_date}: {horas_possiveis}")
    
    # Prepare subplots
    num_plots = len(target_stations)
    fig, axes = plt.subplots(num_plots, 1, figsize=(10, 6*num_plots))

    if num_plots == 1:
        axes = [axes]  # Ensure axes is a list even if there is only one plot

    # Iterate through each target station
    for i, target_station in enumerate(target_stations):
        station_pair = [target_station, estacoes_conjugadas.get(target_station, None)]
        
        # Check if both stations exist in the data
        found_both_stations = False
        for data_entry in lista_dados_agrupados:
            data_date = pd.to_datetime(data_entry["Data"])
            if data_date == target_date:
                found_stations = []
                for station_data in data_entry["Estacoes"]:
                    estacao = station_data["Estacao"]
                    if estacao in station_pair:
                        # Extract the DataFrame with the magnetic field data
                        df = station_data["Dados_Janela"]
                        
                        # Additional station information
                        hora = station_data["Hora"]
                        amplitude = station_data["Amplitude"]
                        latitude = station_data["Latitude"]
                        longitude = station_data["Longitude"]
                        ponto_amp_esq = station_data.get("Amplitude_ponto_esq", None)
                        ponto_amp_dir = station_data.get("Amplitude_ponto_dir", None)
                        r_squared = station_data["R_squared"]
                        rmse = station_data["RMSE"]
                        
                        # Check if this hora matches the event_index
                        if hora == horas_possiveis[event_index]:
                            # Plot the data on the corresponding subplot
                            ax = axes[i]
                            for campo in campos:
                                if campo in df.columns:
                                    ax.plot(df["TIME"], df[campo], label=f"{campo} - {estacao}")
                                    
                            # Plot amplitude_x and amplitude_y as points if data is valid
                            if ponto_amp_esq is not None and ponto_amp_dir is not None:
                                ax.scatter(ponto_amp_esq[0], ponto_amp_esq[1], color='red')
                                ax.scatter(ponto_amp_dir[0], ponto_amp_dir[1], color='blue')
                                
                            ax.set_xlabel("Time")
                            ax.set_ylabel("Magnetic Field (nT)")
                            ax.set_title(f"Magnetic Field Components on {target_date.strftime('%Y-%m-%d')} at {target_station}")
                            ax.legend()
                            ax.grid(True)
                            
                            # Display characteristics if ver_caracteristicas is True
                            if ver_caracteristicas:
                                # Fixed text position in the bottom right corner
                                text_x = 0.95  # X position in axes coordinates
                                if estacao == target_station:
                                    text_y = 0.8  # Y position for the first station
                                else:
                                    text_y = 0.35  # Y position for the second station

                                ax.text(text_x, text_y, f"Estacao: {estacao}\nHora: {hora}\nAmplitude: {amplitude}\nLatitude: {latitude}\nLongitude: {longitude}\nR^2: {r_squared}", 
                                        transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.5), 
                                        verticalalignment='top', horizontalalignment='right')
                            
                            found_stations.append(estacao)
                            if len(found_stations) == len(station_pair):
                                found_both_stations = True
                                break
                                
                if found_both_stations:
                    break
        
        # If not all stations were found
        if not found_both_stations:
            not_found_stations = set(station_pair) - set(found_stations)
            not_found_stations_str = ", ".join(not_found_stations)
            print(f"No data found for date {target_date.strftime('%Y-%m-%d')} and stations: {not_found_stations_str}.")
    
    plt.tight_layout()
    plt.show()


# %% Gera lista de dados agrupados
files_folder = diretorio_base = os.getcwd()

folder_path = "sc_eventos"
event_dates = get_events_dates(folder_path)
download_files(files_folder, event_dates['Data'], stations)
display(event_dates)
stations = 'SJG GUI KNY SMS ASC KDU'.split()

estacoes_conjugadas = {
    'SMS': 'SJG',
    'ASC': 'GUI',
    'KDU': 'KNY'
}



# #%% Plota por ano
# # Anos a serem plotados
# anos = [2019, 2020, 2021, 2022, 2023,2024]
# estacoes_estudadas = 'SMS ASC KDU'

# plot_amplificacao_por_data(nova_lista_dados_agrupados, anos, estacoes_estudadas,amplificacao_min=-10, amplificacao_max=10)

# # %% plota detalhes estação, conjugada, data
# target_date = event_dates["Data"][51]
# # target_station = ['SMS', 'ASC', 'KDU']
# target_station = ['SJG']
# # campos = ["H_nT", "H_nT_filtered"]  # Lista de campos a serem plotados
# # campos = ["dH_nT_movmean","H_nT_movmean"]  # Lista de campos a serem plotados
# # campos = ["H_nT"]  # Lista de campos a serem plotados
# campos = ["H_nT","H_nT_ajuste"]  # Lista de campos a serem plotados

# # plot_data_conjugadas(nova_lista_dados_agrupados, '2023-09-12', target_station, estacoes_conjugadas, event_index=0, campos=campos, ver_caracteristicas=True)

# plot_data_conjugadasV2(nova_lista_dados_agrupados, '2023-09-12', target_station, event_index=0, campos=campos, ver_caracteristicas=True)

#%%
# plt.close('all')

# %% testes

# #%% teste execução
event_dates['Data'] = pd.to_datetime(event_dates['Data'])


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

    
# plotar_amplificacao_por_datav2(amp_sc)
    
# plotar_amplificacao_por_hora(amp_sc)

plotar_amplificacao_por_tempo_local(amp_sc_local,'SMS')
plotar_media_amplificacao_por_hora(amp_sc_local,'SMS')

# # Definindo os anos a serem plotados
# anos = [2019, 2020, 2021, 2022, 2023, 2024]

# # Estações estudadas
# estacoes_estudadas = 'SMS ASC KDU'


# plot_amplificacao_por_datav2(amplificacao_sc, anos, estacoes_estudadas, amplificacao_min=-10, amplificacao_max=10)


# lista_dados_agrupadosv2 = processa_dados_estacoesv2(files_by_date, event_dates, janela,estacoes_conjugadas)
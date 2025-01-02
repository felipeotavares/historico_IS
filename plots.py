# -*- coding: utf-8 -*-
"""
Criado em Sáb Nov  2 15:12:53 2024

@author: felip
"""

# Importações
import pickle
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from datetime import datetime
import mplcursors
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.cm as cm
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as mtick
from datetime import datetime, timedelta
from matplotlib.backends.backend_pdf import PdfPages
from collections import defaultdict
import math
from math import ceil, sqrt    
from matplotlib.cm import get_cmap
from matplotlib.patches import Rectangle
import datetime as dt

# event_dates = pd.DataFrame({
#     'Data': ['2015-11-03'],
#     'Hora': [7.5]
# })

# Fechar todos os gráficos abertos ao iniciar o script
plt.close('all')

#%% Carregamento dos Metadados e Lista de Dados
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

# #%% Função para Calcular Diferença com Estação Conjugada
# def calculate_conjugate_difference(data_list):
#     """
#     Calcula a diferença nos valores de "dH_nT" entre cada estação e sua estação conjugada
#     para cada "DataHora" disponível.

#     Parâmetros:
#         data_list (list): Lista de dicionários contendo dados das estações.

#     Retorna:
#         list: Lista atualizada com a diferença adicionada como uma nova coluna "dH_nT_diff" no DataFrame "Dados".
#     """
#     # Cria um dicionário para indexar dados por estação e DataHora para fácil consulta
#     data_index = {}
#     for entry in data_list:
#         station = entry.get('Estacao')
#         datahora = entry.get('DataHora')
#         if station and datahora:
#             if station not in data_index:
#                 data_index[station] = {}
#             data_index[station][datahora] = entry
    
#     # Calcula a diferença em dH_nT entre cada estação e sua conjugada
#     for entry in data_list:
#         conjugate_station = entry.get('Conjugada')
#         datahora = entry.get('DataHora')
#         if conjugate_station and datahora:
#             conjugate_entry = data_index.get(conjugate_station, {}).get(datahora)
#             if conjugate_entry:
#                 entry['Dados']['dH_nT_diff'] = entry['Dados']['dH_nT'] - conjugate_entry['Dados']['dH_nT']
#             else:
#                 entry['Dados']['dH_nT_diff'] = None  # Definir como None se os dados da conjugada não estiverem disponíveis
#         else:
#             entry['Dados']['dH_nT_diff'] = None  # Definir como None se não houver estação conjugada
    
#     return data_list



#%%filtragem pela qualidadade
def filter_by_quality(my_list, estacoes_conjugadas, limite=0.9, field='Qualidade'):
    """
    Retorna uma lista filtrada de dados em 'my_list' com base em uma lista de estações conjugadas,
    considerando apenas as datas em que todas as estações (principal e conjugada) têm o valor do campo especificado
    maior que o limite e 'Amplificacao' no intervalo (> 0 e <= 5).

    Parâmetros:
        my_list (list): Lista de dicionários contendo dados das estações.
        estacoes_conjugadas (dict): Dicionário com as estações principais como chaves e suas estações conjugadas como valores.
        limite (float): Limite mínimo para o campo especificado (padrão: 0.9).
        field (str): Nome do campo a ser verificado (padrão: 'Qualidade').

    Retorna:
        list: Lista filtrada com dados que atendem aos critérios de qualidade.
    """
    # Converte my_list em um dicionário para acesso mais rápido por estação e data
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

            # Verifica critérios do campo especificado e 'Amplificacao' para ambas as estações
            if (not principal_data or principal_data.get(field, 0) <= limite or
                not conjugada_data or conjugada_data.get(field, 0) <= limite or
                not (0 < principal_data.get('Amplificacao', -5) <= 5)):
                all_stations_meet_criteria = False
                break

        # Adiciona ao resultado final se a data satisfizer todas as condições para todas as estações
        if all_stations_meet_criteria:
            filtered_data.extend(stations_data.values())

    return filtered_data


#%% parametro por tempo
# def plot_amplification_for_stations(my_list, stations, field):
#     """
#     Plota o campo especificado ao longo do tempo como pontos para as estações especificadas
#     e adiciona uma linha da média e desvio padrão para cada estação, usando a mesma cor dos pontos.
#     Destaca pontos que estejam na noite, baseado na longitude da estação.
#     Exibe no título a quantidade total de dados plotados.

#     Parâmetros:
#         my_list (list): Lista de dicionários contendo dados das estações.
#         stations (list): Lista de estações a serem plotadas.
#         field (str): Campo a ser plotado (e.g., 'Amplificacao').
#     """

#     plt.figure(figsize=(12, 8))

#     # Define a paleta de cores 'viridis', adequada para daltônicos
#     colors = cm.get_cmap("viridis", len(stations))

#     # Variável para contar o total de dados plotados
#     total_data_points = 0

#     # Itera sobre cada estação na lista especificada para plotar o campo especificado ao longo do tempo
#     for idx, station in enumerate(stations):
#         # Filtra dados para a estação atual
#         station_data = [entry for entry in my_list if entry['Estacao'] == station]
        
#         # Obtém os valores de tempo e do campo especificado
#         times = [entry['DataHora'] for entry in station_data]
#         # times = [time.strftime("%H:%M %d/%m/%Y") for time in times]  # Formata a data para HH MM DD MM AAAA
#         values = [entry[field] for entry in station_data]
#         longitudes = [entry['Longitude'] for entry in station_data]
#         local_times = [entry['TempoLocal'] for entry in station_data]

#         # Incrementa o contador de pontos de dados
#         total_data_points += len(values)

#         # Escolhe a cor específica para a estação
#         color = colors(idx)

#         # Plota todos os dados do campo especificado ao longo do tempo como pontos para a estação
#         plt.scatter(times, values, label=station, alpha=1, color=color)

#         # Calcula e plota a linha da média e desvio padrão para a estação
#         if values:  # Verifica se há dados
#             mean_value = np.nanmean(values)
#             std_value = np.nanstd(values)
#             plt.axhline(y=mean_value, color=color, linestyle='--', linewidth=1, alpha=0.7,
#                         label=f"{station} Média = {mean_value:.2f}, Desvio Padrão = {std_value:.2f}")

#     # Configurações do gráfico
#     plt.xlabel('Tempo')
#     plt.ylabel(field)
#     plt.title(f'{field} ao longo do tempo com linha da média e desvio padrão\nTotal de pontos de dados: {total_data_points}')
#     plt.xticks(rotation=90, fontsize=8)
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()

#%% plotar detalhes evento 
# def plot_event_data(data_list, intervalo, event_dates, colunas_eixo_esquerdo, colunas_eixo_direito, stations, salvar_pdf=False, datafile_name='Teste', parametros=[], view_points = True):
#     """
#     Plota os campos especificados para múltiplos eventos e múltiplas estações dentro de um intervalo de datas.

#     Parâmetros:
#         data_list (pd.DataFrame): DataFrame contendo dados das estações.
#         intervalo (list): Lista com duas strings especificando a data de início e fim (formato: 'DD/MM/YYYY').
#         colunas_eixo_esquerdo (list of tuples): Campos para plotar em cada painel no eixo y à esquerda (ex.: [('H_nT', 'Principal'), ('H_nT', 'Conjugada')]).
#         colunas_eixo_direito (list of tuples): Campos para plotar em cada painel no eixo y à direita (ex.: [('dH_nT_diff', 'Principal')]).
#         stations (list of str): Lista de estações principais a serem analisadas.
#         event_dates (pd.DataFrame): DataFrame com duas colunas, 'Data' (tipo datetime) e 'hora' (str, formato 'HH:MM').
#         salvar_pdf (bool): Se True, salva os gráficos em um PDF. Padrão é False.
#         parametros (list of tuples): Lista de parâmetros a serem exibidos em cada gráfico (ex.: [('Amplitude', 'Principal')]).
#     """
#     start_date = datetime.strptime(intervalo[0], '%d/%m/%Y')
#     end_date = datetime.strptime(intervalo[1], '%d/%m/%Y')
#     # data_list = my_list
#     # Filtra os dados dentro do intervalo especificado
#     filtered_data = [entry for entry in data_list if start_date <= entry.get('DataHora') <= end_date]

#     # Filtra os dados para apenas as datas e horas explicitadas em event_dates
#     valid_dates = []
#     for _, row in event_dates.iterrows():
#         data = row['Data']
#         hora_decimal = row['Hora']
#         horas = int(row['Hora'])
#         minutos = int((hora_decimal - horas) * 60)
#         delta_tempo = pd.to_timedelta(f'{horas}h {minutos}m')
#         # Criar um timestamp com data e hora
#         data_hora = data + delta_tempo
#         valid_dates.append(data_hora)
    
#     # print(valid_dates)
#     filtered_data = [entry for entry in filtered_data if entry.get('DataHora') in valid_dates]

#     if not filtered_data:
#         print(f"Nenhum dado disponível no intervalo especificado: {intervalo[0]} a {intervalo[1]}.")
#         return

#     events = sorted(set([entry['DataHora'] for entry in filtered_data]))
#     num_events = len(events)
#     num_stations = len(stations)
#     eventos_por_pagina = 2

#     # Cria um PDF para salvar os gráficos se salvar_pdf for True
#     if salvar_pdf:
#         pdf = PdfPages(datafile_name + '.pdf')

#     # Divide os eventos em páginas com no máximo 6 eventos por página
#     for page_start in range(0, num_events, eventos_por_pagina):
#         page_events = events[page_start:page_start + eventos_por_pagina]
#         fig, axes = plt.subplots(num_stations, len(page_events), figsize=(5 * len(page_events), 5 * num_stations), sharex=False)

#         if num_stations == 1:
#             axes = [axes]
#         if len(page_events) == 1:
#             axes = [[ax] for ax in axes]

#         # Plota os dados para cada estação e evento
#         for i, station in enumerate(stations):
#             for j, event in enumerate(page_events):
#                 ax = axes[i][j]
#                 main_data = next((entry for entry in filtered_data if entry.get('Estacao') == station and entry.get('DataHora') == event), None)
#                 conjugate_data = None
#                 if main_data and main_data.get('Conjugada'):
#                     conjugate_data = next((e for e in filtered_data if e.get('Estacao') == main_data['Conjugada'] and e.get('DataHora') == event), None)

#                 if not main_data:
#                     ax.set_title(f"Nenhum dado disponível ({event.strftime('%d/%m/%Y')}")
#                     continue

#                 # Plota as colunas especificadas para a estação atual e evento no eixo y à direita
#                 if colunas_eixo_direito:
#                     ax_right = ax.twinx()
#                     for field_right, station_type in colunas_eixo_direito:
#                         if station_type == 'Principal':
#                             time_series = main_data['Dados']['TIME']
#                             ax_right.plot(time_series, main_data['Dados'][field_right], linestyle='-', color='green', alpha=0.5, label=f"{colunas_eixo_direito[0]}")

#                         elif station_type == 'Conjugada' and conjugate_data:
#                             time_series = conjugate_data['Dados']['TIME']
#                             ax_right.plot(time_series, conjugate_data['Dados'][field_right], linestyle='-', color='orange', alpha=0.5, label=f"{colunas_eixo_direito[1]}")

#                 # Plota as colunas especificadas para a estação atual e evento no eixo y à esquerda
#                 for field, station_type in colunas_eixo_esquerdo:
#                     if station_type == 'Principal':
#                         time_series = main_data['Dados']['TIME']
#                         ax.plot(time_series, main_data['Dados'][field], linestyle='-', color='green', label=f"{colunas_eixo_esquerdo[0]}")
#                         if not ((np.isnan(main_data['Ponto_Esquerda']).any() or np.isnan(main_data['Ponto_Direita']).any())) and view_points :
#                             ax_right.scatter(main_data['Ponto_Esquerda'][0], main_data['Ponto_Esquerda'][1], color='red')
#                             ax_right.scatter(main_data['Ponto_Direita'][0], main_data['Ponto_Direita'][1], color='red')
#                     elif station_type == 'Conjugada' and conjugate_data:
#                         time_series = conjugate_data['Dados']['TIME']
#                         ax.plot(time_series, conjugate_data['Dados'][field], linestyle='-', color='orange', label=f"{colunas_eixo_esquerdo[1]}")
#                         if not ((np.isnan(conjugate_data['Ponto_Esquerda']).any() or np.isnan(conjugate_data['Ponto_Direita']).any())) and view_points:
#                             ax_right.scatter(conjugate_data['Ponto_Esquerda'][0], conjugate_data['Ponto_Esquerda'][1], color='red')
#                             ax_right.scatter(conjugate_data['Ponto_Direita'][0], conjugate_data['Ponto_Direita'][1], color='red')

#                 # Adiciona os parâmetros especificados em uma caixa de texto no gráfico
#                 parametros_texto = ""
#                 for parametro, station_type in parametros:
#                     if station_type == 'Principal' and parametro in main_data:
#                         parametros_texto += f"{parametro}_P: {main_data[parametro]:.2f}\n"
#                     elif station_type == 'Conjugada' and conjugate_data and parametro in conjugate_data:
#                         parametros_texto += f"{parametro}_C: {conjugate_data[parametro]:.2f}\n"

#                 if parametros_texto:
#                     bbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5, edgecolor='black')
#                     ax.text(0.05, 0.95, parametros_texto, transform=ax.transAxes, fontsize=10,
#                             verticalalignment='top', bbox=bbox_props)

#                 # Adiciona o título com a parte exponencial nos eixos
#                 if i == 0 and j == 0:
#                     ax.set_xlabel("TIME")
#                     ax.set_ylabel(f"{field}")
#                     if colunas_eixo_direito:
#                         ax_right.set_ylabel(f"{field_right}")

#                 if i == 0:
#                     ax.set_title(f"#{j + page_start} {event.strftime('%d/%m/%Y')} \n P:{station}/C:{main_data.get('Conjugada')}", fontweight='bold')
#                 else:
#                     ax.set_title(f"P:{station}/C:{main_data.get('Conjugada')}", fontweight='bold')

#                 time_data = main_data['Dados']['TIME']

#                 # Verificar se há valores NaN ou infinitos
#                 if time_data.isna().any() or np.isinf(time_data).any():
#                     continue
#                 # Definir os limites do eixo x
#                 ax.set_xlim(time_data.iloc[0], time_data.iloc[-1])
#                 ax_right
#                 ax.grid(True)

#         # Adiciona uma única legenda para todos os subplots
#         handles_left, labels_left = ax.get_legend_handles_labels()
#         handles_right, labels_right = ax_right.get_legend_handles_labels() if colunas_eixo_direito else ([], [])
#         handles_combined = handles_left + handles_right
#         labels_combined = labels_left + labels_right
#         fig.legend(handles_combined, labels_combined, loc='upper right')

#         mplcursors.cursor(hover=True)
#         plt.tight_layout()

#         if salvar_pdf:
#             pdf.savefig(fig)
#         plt.show()

#     # Fecha o PDF se ele foi criado
#     if salvar_pdf:
#         pdf.close()

#%% plotar amplificação por estação 
def plot_bar_chart_for_stations(my_list, stations, field):
    """
    Plots a bar chart for the specified field for the given stations.
    Each bar represents the average of the field for the corresponding station.
    
    Parameters:
        my_list (list): List of dictionaries containing station data.
        stations (list): List of stations to be plotted.
        field (str): Field to be plotted (e.g., 'Amplification').
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    
    # Initialize lists to store means, standard deviations, and data counts for each station
    station_means = []
    station_stds = []
    station_counts = []
    station_labels = []
    
    # Iterate over each station to calculate the mean, standard deviation, and count of data for the specified field
    for station in stations:
        # Filter data for the current station
        station_data = [entry for entry in my_list if entry['Estacao'] == station]
        values = [entry[field] for entry in station_data]
        # print(station)
        conj_station = station_data[0]['Conjugada'] if station_data else ''  # Get conjugated station name if available
        
        # Calculate mean and standard deviation, ignoring NaN values
        if values:
            mean_value = np.nanmean(values)
            std_value = np.nanstd(values)
            count_value = len(values)
        else:
            mean_value = 0
            std_value = 0
            count_value = 0
        
        # Store the calculated values
        station_means.append(mean_value)
        station_stds.append(std_value)
        station_counts.append(count_value)
        station_labels.append(f'{station}/{conj_station}')
    
    # Chart settings
    plt.figure(figsize=(12, 8))
    x_positions = np.arange(len(stations))
    colors = cm.get_cmap('tab10', len(stations))  # Define a color map for different stations
    
    # Plot bars with mean and standard deviation, each station with a different color
    bars = plt.bar(x_positions, station_means, yerr=station_stds, capsize=5, alpha=0.7, color=[colors(i) for i in range(len(stations))])
    
    # Add text indicating the number of data points and the standard deviation for each bar
    for bar, std, count in zip(bars, station_stds, station_counts):
        plt.text(bar.get_x(), bar.get_height(), f'N={count}σ={std:.2f}', ha='left', va='bottom', fontsize=12, color='black')
    
    # Axis and title settings
    plt.xlabel('Station', fontsize=14)
    plt.ylabel(field, fontsize=14)
    plt.title(f'Average {field} (dH/dt)² by Station with Standard Deviation', fontsize=16)
    plt.xticks(ticks=x_positions, labels=station_labels, rotation=45, ha='right', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Show the chart
    plt.tight_layout()
    plt.show()
    
def plot_scatter_for_stations(data_list, stations, field):
    """
    Plots a scatter plot for the specified field for the given stations.
    Each point represents the value of the field for a specific entry.
    Additionally, plots the mean and standard deviation for each station.

    Parameters:
        data_list (list): List of dictionaries containing station data.
        stations (list): List of stations to be plotted.
        field (str): Field to be plotted (e.g., 'Amplification').
    """
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import numpy as np

    # Chart settings
    plt.figure(figsize=(12, 8))
    colors = cm.get_cmap('tab10', len(stations))  # Define a color map for different stations

    # Plot points for each station
    for idx, station in enumerate(stations):
        station_data = [entry for entry in data_list if entry['Estacao'] == station]
        values = [entry[field] for entry in station_data if entry[field] is not None]
        values = np.array(values, dtype=np.float32)  # Convert to numpy array to handle NaN

        # Scatter plot of individual values
        plt.scatter([station] * len(values), values, label=f'{station}', color=colors(idx), alpha=0.6, edgecolors='w', s=100)

        # Calculate mean and standard deviation, ignoring NaN values
        mean_value = np.nanmean(values)
        std_dev = np.nanstd(values)

        # Calculate the number of amplifications greater than 1
        num_amplification_gt_1 = np.sum(values > 1)

        # Calculate the total number of events
        total_events = len(values)

        # Plot mean and standard deviation with the number of amplifications > 1 and total events
        plt.errorbar(station, mean_value, yerr=std_dev, fmt='o', color='red', ecolor='black', capsize=5, markersize=10)
        plt.text(station, mean_value, f' ({num_amplification_gt_1}/{total_events})', color='blue', fontsize=10, ha='left', va='bottom')

    # Axis and title settings
    plt.xlabel('Station', fontsize=14)
    plt.ylabel(field, fontsize=14)
    plt.title(f'{field} (dH/dt)² by Station', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Stations', loc='best')

    # Show the chart
    plt.tight_layout()
    plt.show()



#%% busca anomalos 
def buscar_anomalos(my_list, stations, field, condition):
    """
    Finds the dates of data entries for the specified field that satisfy the given condition for the specified stations.
    
    Parameters:
        my_list (list): List of dictionaries containing station data.
        stations (list): List of stations to be searched.
        field (str): Field to be analyzed (e.g., 'Amplification').
        condition (str): Condition to apply to the field (e.g., '> 3').
    
    Returns:
        DataFrame: A DataFrame containing dates and hours for anomalous data entries.
    """
    import operator
    import re
    import pandas as pd
    
    # Extract condition operator and value
    match = re.match(r'([<>]=?|==|!=)\s*(\d+(\.\d+)?)', condition)
    if not match:
        raise ValueError("Condition must be a valid comparison (e.g., '> 3', '== 2.5').")
    
    op_str, value_str = match.groups()[:2]
    value = float(value_str)
    
    # Define a dictionary of valid operators
    ops = {
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }
    
    if op_str not in ops:
        raise ValueError("Invalid operator in condition.")
    
    op_func = ops[op_str]
    
    # Filter data entries based on the condition
    anomalous_dates = []
    for station in stations:
        station_data = [entry for entry in my_list if entry['Estacao'] == station]
        for entry in station_data:
            if field in entry and op_func(entry[field], value):
                date = entry['DataHora'].date()
                hour = entry['DataHora'].hour + entry['DataHora'].minute / 60.0
                anomalous_dates.append({'Data': date, 'Hora': hour})
    
    # Convert the list of dictionaries to a DataFrame
    anomalous_df = pd.DataFrame(anomalous_dates)
    anomalous_df['Data'] = pd.to_datetime(anomalous_df['Data'])
    
    return anomalous_df


#%%teste
def plot_event_data(data_list, intervalo, event_dates, colunas_eixo_esquerdo, colunas_eixo_direito, stations, salvar_pdf=False, datafile_name='Teste', parametros=[], view_points=True):
    """
    Plota os campos especificados para múltiplos eventos e múltiplas estações dentro de um intervalo de datas.

    Parâmetros:
        data_list (list of dicts): Lista contendo dados das estações.
        intervalo (list): Lista com duas strings especificando a data de início e fim (formato: 'DD/MM/YYYY').
        colunas_eixo_esquerdo (list of tuples): Campos para plotar em cada painel no eixo y à esquerda (ex.: [('H_nT', 'Principal'), ('H_nT', 'Conjugada')]).
        colunas_eixo_direito (list of tuples): Campos para plotar em cada painel no eixo y à direita (ex.: [('dH_nT_diff', 'Principal')]).
        stations (list of str): Lista de estações principais a serem analisadas.
        event_dates (pd.DataFrame): DataFrame com duas colunas, 'Data' (tipo datetime) e 'Hora' (float, horas decimais).
        salvar_pdf (bool): Se True, salva os gráficos em um PDF. Padrão é False.
        datafile_name (str): Nome do arquivo PDF a ser salvo.
        parametros (list of tuples): Lista de parâmetros a serem exibidos em cada gráfico (ex.: [('Amplitude', 'Principal')]).
        view_points (bool): Se True, exibe pontos específicos no gráfico. Padrão é True.
    """
    start_date = datetime.strptime(intervalo[0], '%d/%m/%Y')
    end_date = datetime.strptime(intervalo[1], '%d/%m/%Y')
    
    # Filtra os dados dentro do intervalo especificado
    filtered_data = [entry for entry in data_list if start_date <= entry.get('DataHora') <= end_date]

    # Filtra os dados para apenas as datas e horas explicitadas em event_dates
    valid_dates = []
    for _, row in event_dates.iterrows():
        data = row['Data']
        hora_decimal = row['Hora']
        horas = int(hora_decimal)
        minutos = int((hora_decimal - horas) * 60)
        delta_tempo = pd.to_timedelta(f'{horas}h {minutos}m')
        # Criar um timestamp com data e hora
        data_hora = data + delta_tempo
        valid_dates.append(data_hora)
    
    filtered_data = [entry for entry in filtered_data if entry.get('DataHora') in valid_dates]

    if not filtered_data:
        print(f"Nenhum dado disponível no intervalo especificado: {intervalo[0]} a {intervalo[1]}.")
        return

    events = sorted(set([entry['DataHora'] for entry in filtered_data]))
    num_events = len(events)
    num_stations = len(stations)
    eventos_por_pagina = 2

    # Cria um PDF para salvar os gráficos se salvar_pdf for True
    if salvar_pdf:
        pdf = PdfPages(datafile_name + '.pdf')

    # Divide os eventos em páginas com no máximo 2 eventos por página
    for page_start in range(0, num_events, eventos_por_pagina):
        page_events = events[page_start:page_start + eventos_por_pagina]
        fig, axes = plt.subplots(num_stations, len(page_events), figsize=(5 * len(page_events), 5 * num_stations), sharex=False)

        if num_stations == 1:
            axes = [axes]
        if len(page_events) == 1:
            axes = [[ax] for ax in axes]

        # Inicializa limites dos eixos y para cada coluna
        y_left_limits = [None] * len(page_events)
        y_right_limits = [None] * len(page_events) if colunas_eixo_direito else None

        # Primeira passagem: determinar os limites dos eixos y
        for j, event in enumerate(page_events):
            for i, station in enumerate(stations):
                main_data = next((entry for entry in filtered_data if entry.get('Estacao') == station and entry.get('DataHora') == event), None)
                conjugate_data = None
                if main_data and main_data.get('Conjugada'):
                    conjugate_data = next((e for e in filtered_data if e.get('Estacao') == main_data['Conjugada'] and e.get('DataHora') == event), None)

                if not main_data:
                    continue

                # Determina limites para o eixo y esquerdo
                for field, station_type in colunas_eixo_esquerdo:
                    if station_type == 'Principal':
                        data_series = main_data['Dados'][field]
                    elif station_type == 'Conjugada' and conjugate_data:
                        data_series = conjugate_data['Dados'][field]
                    else:
                        continue

                    min_val, max_val = data_series.min(), data_series.max()
                    if y_left_limits[j] is None:
                        y_left_limits[j] = [min_val * 1.05, max_val * 1.05]
                    else:
                        y_left_limits[j][0] = min(y_left_limits[j][0], min_val) * 1.05
                        y_left_limits[j][1] = max(y_left_limits[j][1], max_val) * 1.05

                # Determina limites para o eixo y direito
                if colunas_eixo_direito:
                    for field_right, station_type in colunas_eixo_direito:
                        if station_type == 'Principal':
                            data_series = main_data['Dados'][field_right]
                        elif station_type == 'Conjugada' and conjugate_data:
                            data_series = conjugate_data['Dados'][field_right]
                        else:
                            continue

                        min_val, max_val = data_series.min(), data_series.max()
                        if y_right_limits[j] is None:
                            y_right_limits[j] = y_left_limits[j]
                        else:
                            y_right_limits[j][0] = min(y_right_limits[j][0], min_val)
                            y_right_limits[j][1] = y_left_limits[j][1]

        # Segunda passagem: plotar os dados com os limites definidos
        for i, station in enumerate(stations):
            for j, event in enumerate(page_events):
                ax = axes[i][j]
                main_data = next((entry for entry in filtered_data if entry.get('Estacao') == station and entry.get('DataHora') == event), None)
                conjugate_data = None
                if main_data and main_data.get('Conjugada'):
                    conjugate_data = next((e for e in filtered_data if e.get('Estacao') == main_data['Conjugada'] and e.get('DataHora') == event), None)

                if not main_data:
                    ax.set_title(f"Nenhum dado disponível ({event.strftime('%d/%m/%Y')}")
                    continue

                # Plota as colunas especificadas para a estação atual e evento no eixo y à direita
                if colunas_eixo_direito:
                    ax_right = ax.twinx()
                    for field_right, station_type in colunas_eixo_direito:
                        if station_type == 'Principal':
                            time_series = main_data['Dados']['TIME']
                            ax_right.plot(time_series, main_data['Dados'][field_right], linestyle='-', color='green', alpha=1, label=f"{field_right} Principal")

                        elif station_type == 'Conjugada' and conjugate_data:
                            time_series = conjugate_data['Dados']['TIME']
                            ax_right.plot(time_series, conjugate_data['Dados'][field_right], linestyle='-', color='orange', alpha=1, label=f"{field_right} Conjugada")

                    # Aplica os limites do eixo y direito
                    if all(math.isfinite(limit) for limit in y_right_limits[j]):
                        ax_right.set_ylim(y_right_limits[j])

                # Plota as colunas especificadas para a estação atual e evento no eixo y à esquerda
                # for field, station_type in colunas_eixo_esquerdo:
                #     if station_type == 'Principal':
                #         time_series = main_data['Dados']['TIME']
                #         ax.plot(time_series, main_data['Dados'][field], linestyle='-', color='black', alpha=0.5, label=f"{field} Principal")
                #         if view_points and 'Ponto_Esquerda' in main_data and 'Ponto_Direita' in main_data:
                #             if not (np.isnan(main_data['Ponto_Esquerda']).any() or np.isnan(main_data['Ponto_Direita']).any()):
                #                 ax_right.scatter(main_data['Ponto_Esquerda'][0], main_data['Ponto_Esquerda'][1], color='red')
                #                 ax_right.scatter(main_data['Ponto_Direita'][0], main_data['Ponto_Direita'][1], color='red')
                #     elif station_type == 'Conjugada' and conjugate_data:
                #         time_series = conjugate_data['Dados']['TIME']
                #         ax.plot(time_series, conjugate_data['Dados'][field], linestyle='-', color='black', alpha=0.5, label=f"{field} Conjugada")
                #         if view_points and 'Ponto_Esquerda' in conjugate_data and 'Ponto_Direita' in conjugate_data:
                #             if not (np.isnan(conjugate_data['Ponto_Esquerda']).any() or np.isnan(conjugate_data['Ponto_Direita']).any()):
                #                 ax_right.scatter(conjugate_data['Ponto_Esquerda'][0], conjugate_data['Ponto_Esquerda'][1], color='red')
                #                 ax_right.scatter(conjugate_data['Ponto_Direita'][0], conjugate_data['Ponto_Direita'][1], color='red')
                # Plota as colunas especificadas para a estação atual e evento no eixo y à esquerda
                # for field, station_type in colunas_eixo_esquerdo:
                    
                #     if station_type == 'Principal':
                #         time_series = main_data['Dados']['TIME']
                #         ax.plot(time_series, main_data['Dados'][field], linestyle='-', color='black', alpha=0.5, label=f"{field} Principal")
                        
                #         # Determina as chaves de ponto dependendo do valor de 'field'
                #         ponto_esquerda_key = 'Ponto_Esquerda_D' if field == 'dH_nT_abs' else 'Ponto_Esquerda_D' if field == 'dH_nT_absacumulado' else 'Ponto_Esquerda'

                #         ponto_direita_key = 'Ponto_Direita_D' if field == 'dH_nT_abs' else 'Ponto_Direita'
                        
                        
                        
                        
                #         if view_points and ponto_esquerda_key in main_data and ponto_direita_key in main_data:
                #             if not (np.isnan(main_data[ponto_esquerda_key]).any() or np.isnan(main_data[ponto_direita_key]).any()):
                #                 ax_right.scatter(main_data[ponto_esquerda_key][0], main_data[ponto_esquerda_key][1], color='red')
                #                 ax_right.scatter(main_data[ponto_direita_key][0], main_data[ponto_direita_key][1], color='red')
                                
                #     elif station_type == 'Conjugada' and conjugate_data:
                #         time_series = conjugate_data['Dados']['TIME']
                #         ax.plot(time_series, conjugate_data['Dados'][field], linestyle='-', color='black', alpha=0.5, label=f"{field} Conjugada")
                        
                #         # Determina as chaves de ponto dependendo do valor de 'field'
                #         ponto_esquerda_key = 'Ponto_Esquerda_D' if field == 'dH_nT_abs' else 'Ponto_Esquerda'
                #         ponto_direita_key = 'Ponto_Direita_D' if field == 'dH_nT_abs' else 'Ponto_Direita'
                        
                #         if view_points and ponto_esquerda_key in conjugate_data and ponto_direita_key in conjugate_data:
                #             if not (np.isnan(conjugate_data[ponto_esquerda_key]).any() or np.isnan(conjugate_data[ponto_direita_key]).any()):
                #                 ax_right.scatter(conjugate_data[ponto_esquerda_key][0], conjugate_data[ponto_esquerda_key][1], color='red')
                #                 ax_right.scatter(conjugate_data[ponto_direita_key][0], conjugate_data[ponto_direita_key][1], color='red')
                # Dicionário para mapear valores de 'field' para sufixos
                sufixo_mapeamento = {
                    'dH_nT_abs': 'D',
                    'dH_nT_absacumulado': 'E',
                    'H_nT': 'A',  # Exemplo adicional
                    'dH_nT_media': 'M',     # Outro exemplo
                }
                
                for field, station_type in colunas_eixo_esquerdo:
                                    
                    if station_type == 'Principal':
                        time_series = main_data['Dados']['TIME']
                        ax.plot(time_series, main_data['Dados'][field], linestyle='-', color='black', alpha=0.5, label=f"{field} Principal")
                        
                        # Determina o sufixo com base no valor de 'field'
                        sufixo = sufixo_mapeamento.get(field, 'D')  # 'D' é o padrão caso não esteja no dicionário
                        ponto_esquerda_key = f"Ponto_Esquerda_{sufixo}"
                        ponto_direita_key = f"Ponto_Direita_{sufixo}"
                
                        if view_points and ponto_esquerda_key in main_data and ponto_direita_key in main_data:
                            if not (np.isnan(main_data[ponto_esquerda_key]).any() or np.isnan(main_data[ponto_direita_key]).any()):
                                ax_right.scatter(main_data[ponto_esquerda_key][0], main_data[ponto_esquerda_key][1], color='red')
                                ax_right.scatter(main_data[ponto_direita_key][0], main_data[ponto_direita_key][1], color='red')
                                                
                    elif station_type == 'Conjugada' and conjugate_data:
                        time_series = conjugate_data['Dados']['TIME']
                        ax.plot(time_series, conjugate_data['Dados'][field], linestyle='-', color='black', alpha=0.5, label=f"{field} Conjugada")
                        
                        # Determina o sufixo com base no valor de 'field'
                        sufixo = sufixo_mapeamento.get(field, 'D')  # 'D' é o padrão caso não esteja no dicionário
                        ponto_esquerda_key = f"Ponto_Esquerda_{sufixo}"
                        ponto_direita_key = f"Ponto_Direita_{sufixo}"
                
                        if view_points and ponto_esquerda_key in conjugate_data and ponto_direita_key in conjugate_data:
                            if not (np.isnan(conjugate_data[ponto_esquerda_key]).any() or np.isnan(conjugate_data[ponto_direita_key]).any()):
                                ax_right.scatter(conjugate_data[ponto_esquerda_key][0], conjugate_data[ponto_esquerda_key][1], color='red')
                                ax_right.scatter(conjugate_data[ponto_direita_key][0], conjugate_data[ponto_direita_key][1], color='red')
                                
                                
                # Aplica os limites do eixo y esquerdo
                if all(math.isfinite(limit) for limit in y_left_limits[j]):
                    ax.set_ylim(y_left_limits[j])

                # Adiciona os parâmetros especificados em uma caixa de texto no gráfico
                parametros_texto = ""
                for parametro, station_type in parametros:
                    if station_type == 'Principal' and parametro in main_data:
                        parametros_texto += f"{parametro}_P: {main_data[parametro]:.2f}\n"
                    elif station_type == 'Conjugada' and conjugate_data and parametro in conjugate_data:
                        parametros_texto += f"{parametro}_C: {conjugate_data[parametro]:.2f}\n"

                if parametros_texto:
                    bbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5, edgecolor='black')
                    ax.text(0.05, 0.95, parametros_texto, transform=ax.transAxes, fontsize=10,
                            verticalalignment='top', bbox=bbox_props)

                # Adiciona o título
                if i == 0:
                    ax.set_title(f"#{j + page_start} {event.strftime('%d/%m/%Y')} \n P:{station}/C:{main_data.get('Conjugada')}", fontweight='bold')
                else:
                    ax.set_title(f"P:{station}/C:{main_data.get('Conjugada')}", fontweight='bold')

                ax.set_xlim(time_series.iloc[0], time_series.iloc[-1])
                ax.grid(True)

                # Adiciona a legenda somente no primeiro gráfico
                if i == 0 and j == 0:
                    handles_left, labels_left = ax.get_legend_handles_labels()
                    if colunas_eixo_direito:
                        handles_right, labels_right = ax_right.get_legend_handles_labels()
                    else:
                        handles_right, labels_right = [], []
                    handles_combined = handles_left + handles_right
                    labels_combined = labels_left + labels_right
                    ax.legend(handles_combined, labels_combined, loc='upper right',fontsize=6)

        # Remove a legenda em nível de figura
        # handles_left, labels_left = ax.get_legend_handles_labels()
        # handles_right, labels_right = ax_right.get_legend_handles_labels() if colunas_eixo_direito else ([], [])
        # handles_combined = handles_left + handles_right
        # labels_combined = labels_left + labels_right
        # fig.legend(handles_combined, labels_combined, loc='upper right')

        mplcursors.cursor(hover=True)
        plt.tight_layout()

        if salvar_pdf:
            pdf.savefig(fig)
        plt.show()

    # Fecha o PDF se ele foi criado
    if salvar_pdf:
        pdf.close()
# %% teste
def plot_bar_chart_for_stations(my_list, stations, field, save_path=None, titulo = "Sem Titulo"):
    """
    Plots a bar chart for the specified field for the given stations.
    Each bar represents the average of the field for the corresponding station.
    
    Parameters:
        my_list (list): List of dictionaries containing station data.
        stations (list): List of stations to be plotted.
        field (str): Field to be plotted (e.g., 'Amplification').
        save_path (str, optional): Path to save the figure. If None, the figure is not saved.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    
    # Initialize lists to store means, standard deviations, and data counts for each station
    station_means = []
    station_stds = []
    station_counts = []
    station_labels = []
    
    # Iterate over each station to calculate the mean, standard deviation, and count of data for the specified field
    for station in stations:
        # Filter data for the current station
        station_data = [entry for entry in my_list if entry['Estacao'] == station]
        values = [entry[field] for entry in station_data]
        # print(station)
        conj_station = station_data[0]['Conjugada'] if station_data else ''  # Get conjugated station name if available
        
        # Calculate mean and standard deviation, ignoring NaN values
        if values:
            mean_value = np.nanmean(values)
            std_value = np.nanstd(values)
            count_value = len(values)
        else:
            mean_value = 0
            std_value = 0
            count_value = 0
        
        # Store the calculated values
        station_means.append(mean_value)
        station_stds.append(std_value)
        station_counts.append(count_value)
        station_labels.append(f'{station}/{conj_station}')
    
    # Chart settings
    plt.figure(figsize=(6, 8))
    x_positions = np.arange(len(stations))
    colors = cm.get_cmap('tab10', len(stations))  # Define a color map for different stations
    
    # Plot bars with mean and standard deviation, each station with a different color
    bars = plt.bar(x_positions, station_means, yerr=station_stds, capsize=5, alpha=0.7, color=[colors(i) for i in range(len(stations))])
    
    # Add text indicating the number of data points and the standard deviation for each bar
    for bar, std, count in zip(bars, station_stds, station_counts):
        plt.text(bar.get_x(), bar.get_height(), f'N={count} σ={std:.2f}', ha='left', va='bottom', fontsize=12, color='black')
    
    # Axis and title settings
    plt.xlabel('Station', fontsize=14)
    plt.ylabel(field, fontsize=14)
    # plt.title(f'Média {field} (dH/dt)² por estação', fontsize=16)
    plt.title(titulo, fontsize=16)
    plt.xticks(ticks=x_positions, labels=station_labels, rotation=45, ha='right', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save or show the chart
    if save_path:
        plt.savefig(save_path)
    plt.show()
    
def plot_scatter_for_stations(data_list, stations, field, save_path=None,titulo = "Sem Titulo"):
    """
    Plots a scatter plot for the specified field for the given stations.
    Each point represents the value of the field for a specific entry.
    Additionally, plots the mean and standard deviation for each station.
    
    Parameters:
        data_list (list): List of dictionaries containing station data.
        stations (list): List of stations to be plotted.
        field (str): Field to be plotted (e.g., 'Amplification').
        save_path (str, optional): Path to save the figure. If None, the figure is not saved.
    """
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import numpy as np
    
    # Chart settings
    plt.figure(figsize=(6, 8))
    colors = cm.get_cmap('tab10', len(stations))  # Define a color map for different stations
    
    # Plot points for each station
    for idx, station in enumerate(stations):
        station_data = [entry for entry in data_list if entry['Estacao'] == station]
        values = [entry[field] for entry in station_data if entry[field] is not None]
        values = np.array(values, dtype=np.float32)  # Convert to numpy array to handle NaN
    
        # Scatter plot of individual values
        plt.scatter([station] * len(values), values, label=f'{station}', color=colors(idx), alpha=0.6, edgecolors='w', s=100)
    
        # Calculate mean and standard deviation, ignoring NaN values
        mean_value = np.nanmean(values)
        std_dev = np.nanstd(values)
    
        # Calculate the number of amplifications greater than 1
        num_amplification_gt_1 = np.sum(values > 1)
    
        # Calculate the total number of events
        total_events = len(values)
    
        # Plot mean and standard deviation with the number of amplifications > 1 and total events
        plt.errorbar(station, mean_value, yerr=std_dev, fmt='o', color='red', ecolor='black', capsize=5, markersize=10)
        plt.text(station, mean_value, f' ({num_amplification_gt_1}/{total_events})', color='blue', fontsize=14, ha='left', va='bottom')
    
    # Axis and title settings
    plt.xlabel('Station', fontsize=14)
    plt.ylabel(field, fontsize=14)
    plt.title(titulo, fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Stations', loc='best')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save or show the chart
    if save_path:
        plt.savefig(save_path)
    plt.show()

# def plot_amplification_for_stations(my_list, stations, field, save_path=None,titulo = "Sem Titulo"):
#     """
#     Plota o campo especificado ao longo do tempo como pontos para as estações especificadas
#     e adiciona uma linha da média e desvio padrão para cada estação, usando a mesma cor dos pontos.
#     Destaca pontos que estejam na noite, baseado na longitude da estação.
#     Exibe no título a quantidade total de dados plotados.

#     Parâmetros:
#         my_list (list): Lista de dicionários contendo dados das estações.
#         stations (list): Lista de estações a serem plotadas.
#         field (str): Campo a ser plotado (e.g., 'Amplificacao').
#         save_path (str, opcional): Caminho para salvar a figura. Se None, a figura não será salva.
#     """
#     import matplotlib.pyplot as plt
#     import matplotlib.cm as cm
#     import numpy as np

#     plt.figure(figsize=(16, 8))

#     # Define a paleta de cores 'viridis', adequada para daltônicos
#     colors = cm.get_cmap("Accent", len(stations))

#     # Variável para contar o total de dados plotados
#     total_data_points = 0

#     # Itera sobre cada estação na lista especificada para plotar o campo especificado ao longo do tempo
#     for idx, station in enumerate(stations):
#         # Filtra dados para a estação atual
#         station_data = [entry for entry in my_list if entry['Estacao'] == station]
        
#         # Obtém os valores de tempo e do campo especificado
#         times = [entry['DataHora'] for entry in station_data]
#         values = [entry[field] for entry in station_data]
#         longitudes = [entry['Longitude'] for entry in station_data]
#         local_times = [entry['TempoLocal'] for entry in station_data]

#         # Incrementa o contador de pontos de dados
#         total_data_points += len(values)

#         # Escolhe a cor específica para a estação
#         color = colors(idx)

#         # Plota todos os dados do campo especificado ao longo do tempo como pontos para a estação
#         # plt.scatter(times, values, label=station, alpha=1, color=color)
#         plt.scatter(times, values, alpha=1, color=color)

#         # Calcula e plota a linha da média e desvio padrão para a estação
#         if values:  # Verifica se há dados
#             mean_value = np.nanmean(values)
#             std_value = np.nanstd(values)
#             plt.axhline(y=mean_value, color=color, linestyle='-', linewidth=1, alpha=0.7,
#                         label=f"{station} Média = {mean_value:.2f}, Desvio Padrão = {std_value:.2f}")

#     # Configurações do gráfico
#     plt.xlabel('Tempo', fontsize=14)
#     plt.ylabel(field, fontsize=14)
#     plt.title(titulo + f'\n Total de amostras: {total_data_points}', fontsize=14)
#     plt.xticks(rotation=90, fontsize=14)
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()

#     # Salva ou mostra o gráfico
#     if save_path:
#         plt.savefig(save_path)
#     plt.show()
# %%teste2
def plot_amplification_for_stations(my_list, stations, field, save_path=None, titulo="Sem Titulo"):
    """
    Plota o campo especificado ao longo do tempo como pontos para as estações especificadas
    e adiciona uma linha da média e desvio padrão para cada estação em gráficos separados, um embaixo do outro.

    Parâmetros:
        my_list (list): Lista de dicionários contendo dados das estações.
        stations (list): Lista de estações a serem plotadas.
        field (str): Campo a ser plotado (e.g., 'Amplificacao').
        save_path (str, opcional): Caminho para salvar a figura. Se None, a figura não será salva.
        titulo (str, opcional): Título geral do gráfico.
    """
    # Define a paleta de cores 'viridis', adequada para daltônicos
    colors = cm.get_cmap("Accent", len(stations))

    # Cria os subplots
    fig, axes = plt.subplots(len(stations), 1, figsize=(16, 6 * len(stations)), sharex=True)

    # Variável para contar o total de dados plotados
    total_data_points = 0

    for idx, station in enumerate(stations):
        # Filtra dados para a estação atual
        station_data = [entry for entry in my_list if entry['Estacao'] == station]
        conjugada = station_data[0]['Conjugada']

        # Obtém os valores de tempo e do campo especificado
        times = [entry['DataHora'] for entry in station_data]
        values = [entry[field] for entry in station_data]

        # Incrementa o contador de pontos de dados
        total_data_points += len(values)

        # Escolhe a cor específica para a estação
        color = colors(idx)

        # Seleciona o subplot atual
        ax = axes[idx] if len(stations) > 1 else axes

        # Plota os dados do campo especificado ao longo do tempo como pontos para a estação
        ax.scatter(times, values, alpha=0.7, color=color, label=station)

        # Calcula e plota a linha da média e desvio padrão para a estação
        if values:  # Verifica se há dados
            mean_value = np.nanmean(values)
            std_value = np.nanstd(values)
            ax.axhline(y=mean_value, color=color, linestyle='-', linewidth=1, alpha=0.7,
                        label=f"Média = {mean_value:.2f}, Desvio Padrão = {std_value:.2f}")

        # Configurações do subplot atual
        ax.set_ylabel(field, fontsize=14)
        ax.set_title(f"{station}/{conjugada}  Total pontos: {total_data_points}", fontsize=16)
        ax.legend(fontsize=12)
        ax.grid(True)
        ax.set_ylim(0, 3.2)
        
        # Configurar eixo x com passo mensal
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        total_data_points = 0

    # Configurações gerais
    plt.xlabel('Tempo', fontsize=14)
    plt.suptitle(titulo, fontsize=18)
    plt.xticks(rotation=90, fontsize=10)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Salva ou mostra o gráfico
    if save_path:
        plt.savefig(save_path)
    plt.show()
    
# %%teste3
def plot_grouped_bars_by_month(my_list, stations, field, save_path=None, titulo="Sem Titulo"):
    """
    Plota o campo especificado ao longo do tempo como barras para as estações especificadas,
    agrupando os dados por mês e criando gráficos separados em uma disposição vertical,
    com um gráfico abaixo do outro.

    Parâmetros:
        my_list (list): Lista de dicionários contendo dados das estações.
        stations (list): Lista de estações a serem plotadas.
        field (str): Campo a ser plotado (e.g., 'Amplificacao').
        save_path (str, opcional): Caminho para salvar a figura. Se None, a figura não será salva.
    """

    # Define a paleta de cores 'Accent'
    colors = cm.get_cmap("Accent", len(stations))

    # Configura a figura com subplots verticais
    num_rows = len(stations)
    fig, axes = plt.subplots(num_rows, 1, figsize=(16, 6 * num_rows))

    # Variável para contar o total de dados plotados
    total_data_points = 0
    
    # Garante que axes seja uma lista, mesmo para um único subplot
    if num_rows == 1:
        axes = [axes]

    for idx, station in enumerate(stations):
        ax = axes[idx]

        # Filtra dados para a estação atual
        station_data = [entry for entry in my_list if entry['Estacao'] == station]

        # Agrupa os dados por mês
        monthly_data = defaultdict(list)
        for entry in station_data:
            date = pd.to_datetime(entry['DataHora'])  # Converte para datetime
            month_key = date.to_period('M')  # Agrupa por mês
            monthly_data[month_key].append(entry[field])
            conjugada = entry['Conjugada']
            
        values = [entry[field] for entry in station_data]
        # Incrementa o contador de pontos de dados
        total_data_points += len(values)
        # Ordena os meses e calcula os valores médios por mês
        months = sorted(monthly_data.keys())
        values = [np.nanmean(monthly_data[month]) for month in months]

        

        # Converte os meses para datetime para escala temporal correta
        month_dates = [date.to_timestamp() for date in months]

        # Escolhe a cor específica para a estação
        color = colors(idx)

        # Plota os dados do campo especificado agrupados por mês como barras para a estação
        ax.bar(month_dates, values, color=color, alpha=1, width=20)  # Ajusta largura para visualização

        # Calcula a média e o desvio padrão dos dados
        all_values = [value for data in monthly_data.values() for value in data]
        if all_values:
            mean_value = np.nanmean(all_values)
            std_value = np.nanstd(all_values)

            # Adiciona a linha da média
            ax.axhline(y=mean_value, color='red', linestyle='--', linewidth=1.5, label=f"Média = {mean_value:.2f}")

            # Adiciona uma linha em y=1
            ax.axhline(y=1, color='blue', linestyle='-.', linewidth=1, label="y = 1")

            # Adiciona legenda com a média e o desvio padrão
            ax.legend(fontsize=10, title=f"Desvio Padrão = {std_value:.2f}")

        # Configurações específicas de cada gráfico
        ax.set_title(f"{station}/{conjugada} Total pontos:{total_data_points}", fontsize=14)
        ax.set_ylabel(field, fontsize=12)
        # ax.grid(True, which='both', linewidth=0.7)  # Aumenta a resolução do grid, horizontal e vertical

        # Configura o formato do eixo x como meses no formato desejado e o intervalo mensal
        # ax.xaxis.set_major_locator(mdates.MonthLocator())  # Intervalo mensal
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))  # Formato do mês-ano
        if idx == num_rows - 1:
            ax.tick_params(axis='x', rotation=90)  # Rotação padrão para ticks
            ax.set_xlabel("Tempo (Meses)", fontsize=12)
        else:
            ax.tick_params(labelbottom=False)  # Remove os rótulos dos ticks para os gráficos superiores

        # Define o limite do eixo Y
        ax.set_ylim(0, 3)
        
        total_data_points = 0

    # Configurações gerais do gráfico
    plt.suptitle(titulo, fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Salva ou mostra o gráfico
    if save_path:
        plt.savefig(save_path)
    plt.show()

# #%% teste 4 tempo local
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.cm as cm
# import numpy as np

# def plot_field_by_local_time(my_list, stations, field, save_path=None, titulo="Sem Titulo"):
#     """
#     Plota o campo especificado ao longo do tempo local como pontos para as estações especificadas,
#     adicionando uma linha da média e desvio padrão para cada estação em gráficos separados.

#     Parâmetros:
#         my_list (list): Lista de dicionários contendo dados das estações.
#         stations (list): Lista de estações a serem plotadas.
#         field (str): Campo a ser plotado (e.g., 'Amplificacao').
#         save_path (str, opcional): Caminho para salvar a figura. Se None, a figura não será salva.
#         titulo (str, opcional): Título geral do gráfico.
#     """
#     # Define a paleta de cores adequada
#     colors = cm.get_cmap("Accent", len(stations))

#     # Cria os subplots
#     fig, axes = plt.subplots(len(stations), 1, figsize=(16, 6 * len(stations)), sharex=True)

#     # Certifique-se de lidar com o caso de uma única estação
#     if len(stations) == 1:
#         axes = [axes]

#     for idx, station in enumerate(stations):
#         # Filtra os dados da estação
#         station_data = [entry for entry in my_list if entry['Estacao'] == station]
#         conjugada = station_data[0]['Conjugada'] if station_data else "N/A"

#         # Obtém os valores de TempoLocal e do campo especificado
#         times = [entry['TempoLocal'].hour + entry['TempoLocal'].minute / 60 for entry in station_data]
#         values = [entry[field] for entry in station_data]

#         # Verifica se há dados
#         if not times or not values:
#             continue

#         # Seleciona o subplot correto
#         ax = axes[idx]

#         # Plota os pontos
#         ax.scatter(times, values, alpha=0.7, color=colors(idx), label=station)

#         # Calcula e plota a linha da média e desvio padrão
#         mean_value = np.nanmean(values)
#         std_value = np.nanstd(values)
#         ax.axhline(y=mean_value, color=colors(idx), linestyle='-', linewidth=1, alpha=0.7,
#                    label=f"Média = {mean_value:.2f}, Desvio Padrão = {std_value:.2f}")

#         # Configurações do subplot
#         ax.set_ylabel(field, fontsize=14)
#         ax.set_title(f"{station}/{conjugada}  Total pontos: {len(values)}", fontsize=16)
#         ax.legend(fontsize=12)
#         ax.grid(True)

                   
#         # ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

#     # Configurações gerais
#     plt.xlabel('Hora Local', fontsize=14)
#     plt.suptitle(titulo, fontsize=18)
#     plt.xticks(rotation=45, fontsize=12)
#     plt.tight_layout(rect=[0, 0, 1, 0.95])

#     # Salva ou exibe o gráfico
#     if save_path:
#         plt.savefig(save_path)
#     plt.show()
def plot_field_by_local_time(my_list, stations, field, save_path=None, titulo="Sem Titulo"):
    """
    Plota o campo especificado ao longo do tempo local como pontos para as estações especificadas,
    adicionando uma linha da média e desvio padrão para cada estação em gráficos separados.
    Marca regiões fixas de noite (antes de 6h e depois de 18h) com um fundo cinza e organiza os gráficos em
    uma matriz quadrada quando possível. Calcula e exibe os valores médios das partes noturna e diurna.

    Parâmetros:
        my_list (list): Lista de dicionários contendo dados das estações.
        stations (list): Lista de estações a serem plotadas.
        field (str): Campo a ser plotado (e.g., 'Amplificacao').
        save_path (str, opcional): Caminho para salvar a figura. Se None, a figura não será salva.
        titulo (str, opcional): Título geral do gráfico.
    """
    colors = cm.get_cmap("Accent", len(stations))

    # Determina o layout da matriz (linhas x colunas)
    n_stations = len(stations)
    n_cols = ceil(sqrt(n_stations))  # Determina número de colunas
    n_rows = ceil(n_stations / n_cols)  # Determina número de linhas

    # Cria os subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 6 * n_rows), sharex=True, sharey=True)
    axes = np.array(axes).reshape(-1)  # Garante que axes seja 1D

    for idx, station in enumerate(stations):
        # Filtra os dados da estação
        station_data = [entry for entry in my_list if entry['Estacao'] == station]
        conjugada = station_data[0]['Conjugada'] if station_data else "N/A"

        # Obtém os valores de TempoLocal e do campo especificado
        times = [entry['TempoLocal'].hour + entry['TempoLocal'].minute / 60 for entry in station_data]
        values = [entry[field] for entry in station_data]

        if not times or not values:
            continue

        ax = axes[idx]

        # Marca regiões fixas de noite
        ax.axvspan(0, 6, color='gray', alpha=0.1, zorder=1)  # Antes de 6h
        ax.axvspan(18, 24, color='gray', alpha=0.1, zorder=1)  # Depois de 18h

        # Plota os pontos com zorder alto
        ax.scatter(times, values, alpha=0.7, color=colors(idx), zorder=2)

        # Calcula os valores médios das partes noturna e diurna
        night_values = [value for time, value in zip(times, values) if time < 6 or time >= 18]
        day_values = [value for time, value in zip(times, values) if 6 <= time < 18]
        night_mean = np.nanmean(night_values) if night_values else np.nan
        day_mean = np.nanmean(day_values) if day_values else np.nan

        # Plota as médias noturna e diurna como linhas horizontais
        if not np.isnan(night_mean):
            ax.axhline(y=night_mean, color='blue', linestyle='--', linewidth=1.5, label=f"Média Noturna = {night_mean:.2f}", zorder=3)
        if not np.isnan(day_mean):
            ax.axhline(y=day_mean, color='orange', linestyle='--', linewidth=1.5, label=f"Média Diurna = {day_mean:.2f}", zorder=3)

        # Calcula e plota a linha da média geral e desvio padrão
        mean_value = np.nanmean(values)
        std_value = np.nanstd(values)
        ax.axhline(y=mean_value, color='black', linestyle='-', linewidth=1, alpha=0.7,
                   label=f"Média Geral = {mean_value:.2f}, Desvio Padrão = {std_value:.2f}", zorder=3)

        ax.set_ylabel(field, fontsize=14)
        ax.set_title(f"{station}/{conjugada}  Total pontos: {len(values)}", fontsize=14)
        ax.legend(fontsize=8)

        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 6))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 25, 6)])

    # Desativa os eixos extras (se o número de estações não preencher toda a matriz)
    for i in range(len(axes)):
        if i >= n_stations:
            axes[i].axis('off')

    plt.xlabel('Hora Local', fontsize=14)
    plt.suptitle(titulo, fontsize=18)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if save_path:
        plt.savefig(save_path)
    plt.show()
#%% teste 4
def plot_frequency_bars(my_list, stations, field, save_path=None, titulo="Frequência por Hora"):
    """
    Plota barras de frequência com bins de 1 hora para os valores do campo especificado,
    separados por estações, destacando a parte noturna com escurecimento e usando cores Accent.
    
    Parâmetros:
        my_list (list): Lista de dicionários contendo dados das estações.
        stations (list): Lista de estações a serem plotadas.
        field (str): Campo a ser analisado (e.g., 'Amplificacao').
        save_path (str, opcional): Caminho para salvar a figura. Se None, a figura não será salva.
        titulo (str, opcional): Título geral do gráfico.
    """
    # Define a matriz de subplots
    n_stations = len(stations)
    n_cols = ceil(sqrt(n_stations))
    n_rows = ceil(n_stations / n_cols)

    # Define o mapa de cores Accent
    colors = cm.get_cmap("Accent", n_stations)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 6 * n_rows), sharex=True, sharey=True)
    axes = np.array(axes).reshape(-1)  # Garante que axes seja 1D

    for idx, station in enumerate(stations):
        # Filtra os dados da estação
        station_data = [entry for entry in my_list if entry['Estacao'] == station]

        # Obtém os tempos (em horas inteiras) e valores do campo
        times = [entry['TempoLocal'].hour for entry in station_data]
        values = [entry[field] for entry in station_data]

        if not times or not values:
            continue

        ax = axes[idx]

        # Adiciona o sombreamento para regiões noturnas
        ax.axvspan(0, 6, color='gray', alpha=0.1, zorder=0)  # Antes de 6h
        ax.axvspan(18, 24, color='gray', alpha=0.1, zorder=0)  # Após 18h

        # Cria o histograma com bins de 1 hora
        bins = range(0, 25)  # Bins de 0 a 24 horas
        ax.hist(times, bins=bins, color=colors(idx), edgecolor="black", alpha=0.8, zorder=1)

        # Configurações do gráfico
        ax.set_title(f"{station} - Frequência por Hora", fontsize=14)
        ax.set_xlabel("Hora Local", fontsize=12)
        ax.set_ylabel("Frequência", fontsize=12)
        ax.set_xticks(range(0, 25, 1))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 25, 1)], rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Desativa os eixos extras (se o número de estações não preencher toda a matriz)
    for i in range(len(axes)):
        if i >= n_stations:
            axes[i].axis("off")

    plt.suptitle(titulo, fontsize=18)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if save_path:
        plt.savefig(save_path)
    plt.show()
#%% teste 5
def plot_amplificacao_and_solar_flux(eventos_sc_local, filtered_data, intervalo, estacoes, field='',save_path = 'lixo'):
    """
    Plota a amplificação por data para cada estação especificada e o intervalo de datas fornecido,
    junto com os dados do fluxo solar F10.7. Os gráficos são gerados sequencialmente
    em uma única figura, um em cima do outro. As estações do ano são marcadas com regiões levemente coloridas.

    Args:
        eventos_sc_local (list): Lista de eventos com amplificação e tempo local calculado.
        filtered_data (DataFrame): Dados filtrados e suavizados do fluxo solar F10.7.
        intervalo (list): Lista com as datas de início e fim do intervalo no formato ['dd/mm/aaaa', 'dd/mm/aaaa'].
        estacoes (list): Lista com os códigos das estações.
        field (str): Nome do campo a ser avaliado para destacar pontos específicos.
    """

    # Definir os períodos das estações do ano no hemisfério sul
    estacoes_ano = {
        "Verão": [(12, 21), (3, 20)],
        "Outono": [(3, 21), (6, 20)],
        "Inverno": [(6, 21), (9, 22)],
        "Primavera": [(9, 23), (12, 20)]
    }

    # Crie um DataFrame a partir dos eventos
    df_amplificacao = pd.DataFrame(eventos_sc_local)

    # Verifique se o DataFrame contém as colunas necessárias
    if 'Amplificacao' not in df_amplificacao.columns or 'DataHora' not in df_amplificacao.columns:
        print("A lista de eventos não contém dados de amplificação ou DataHora.")
        return

    # Converter a coluna 'DataHora' para datetime, se ainda não estiver
    df_amplificacao['DataHora'] = pd.to_datetime(df_amplificacao['DataHora'])

    # Converter o intervalo para datetime
    inicio, fim = pd.to_datetime(intervalo[0], dayfirst=True), pd.to_datetime(intervalo[1], dayfirst=True)

    # Filtrar os dados pelo intervalo especificado
    df_amplificacao = df_amplificacao[(df_amplificacao['DataHora'] >= inicio) & (df_amplificacao['DataHora'] <= fim)]

    # Filtrar pelas estações especificadas
    df_amplificacao = df_amplificacao[df_amplificacao['Estacao'].isin(estacoes)]

    # Verificar se há dados após o filtro
    if df_amplificacao.empty:
        print("Nenhum dado encontrado para o intervalo e estações especificados.")
        return

    # Criar esquema de cores
    # cmap = get_cmap('Accent')
    cmap = get_cmap('Accent_r')
    cores = cmap.colors[:len(estacoes)]
    estacao_colors = {
        "Verão": 'yellow',
        "Outono": 'orange',
        "Inverno": 'lightblue',
        "Primavera": 'lightgreen'
    }

    # Criar a figura e eixos
    fig, axs = plt.subplots(len(estacoes), 1, figsize=(14, 4 * len(estacoes)), sharex=True)

    if len(estacoes) == 1:
        axs = [axs]  # Garantir que axs seja uma lista quando há apenas um gráfico

    # Listas para handles e labels unificadas
    all_handles = []
    all_labels = []
    f107_added = False  # Verificação para adicionar F10.7 apenas uma vez

    for i, estacao in enumerate(estacoes):
        ax = axs[i]
        df_estacao = df_amplificacao[df_amplificacao['Estacao'] == estacao]

        if df_estacao.empty:
            ax.text(0.5, 0.5, f"Sem dados para a estação {estacao}", ha='center', va='center')
            continue

        total_pontos = len(df_estacao)
        scatter = ax.scatter(df_estacao['DataHora'], df_estacao['Amplificacao'], label=f"Estação: {estacao} ({total_pontos})", s=50, color=cores[i], zorder=3)

        
        
        # Adicionar os handles e labels do scatter à lista
        handles, labels = ax.get_legend_handles_labels()
        all_handles.extend(handles)
        all_labels.extend(labels)

        # Destacar pontos com valores altos no campo especificado, se field não for vazio
        if field:
            df_high_field = df_estacao[df_estacao[field] > 0.8]
            if not df_high_field.empty:
                ax.scatter(df_high_field['DataHora'], df_high_field['Amplificacao'], edgecolor='red', facecolor='none', s=100, linewidth=1.5, zorder=4)

        # Adicionar regiões coloridas para as estações do ano
        for estacao_ano, ((mes_ini, dia_ini), (mes_fim, dia_fim)) in estacoes_ano.items():
            ano_inicio = inicio.year
            ano_fim = fim.year
            for ano in range(ano_inicio, ano_fim + 1):
                if estacao_ano == "Verão":
                    data_inicio_estacao = pd.Timestamp(year=ano - 1, month=mes_ini, day=dia_ini)
                    data_fim_estacao = pd.Timestamp(year=ano, month=mes_fim, day=dia_fim)
                else:
                    data_inicio_estacao = pd.Timestamp(year=ano, month=mes_ini, day=dia_ini)
                    data_fim_estacao = pd.Timestamp(year=ano, month=mes_fim, day=dia_fim)

                # Ajustar os limites ao intervalo especificado
                if data_fim_estacao < inicio or data_inicio_estacao > fim:
                    continue

                data_inicio_estacao = max(data_inicio_estacao, inicio)
                data_fim_estacao = min(data_fim_estacao, fim)

                ax.axvspan(data_inicio_estacao, data_fim_estacao, color=estacao_colors[estacao_ano], alpha=0.3, zorder=1, label=estacao_ano if estacao_ano not in all_labels else None)

        ax.set_ylabel('Amplificação')
        ax.set_title(f"Estação {estacao}")
        ax.grid(True, linestyle='--', alpha=0.7, zorder=0)

        # Adicionar os dados do fluxo solar F10.7
        ax_twin = ax.twinx()
        line, = ax_twin.plot(filtered_data['Date'], filtered_data['SmoothedObsFlux'], linewidth=2, color='orange', zorder=2)

        # Adicionar handle e label do F10.7 apenas uma vez
        if not f107_added:
            all_handles.append(line)
            all_labels.append("F10.7")
            f107_added = True

    # Adicionar legenda unificada
    fig.legend(all_handles, all_labels, loc='upper center', bbox_to_anchor=(0.5, 0.91), ncol=3)

    axs[-1].set_xlabel('Data')  # Definir o rótulo do eixo x apenas no último gráfico
    plt.xticks(rotation=45)

    # Ajustar o layout para evitar sobreposição
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
    
    if save_path:
        plt.savefig(save_path)
    plt.show()

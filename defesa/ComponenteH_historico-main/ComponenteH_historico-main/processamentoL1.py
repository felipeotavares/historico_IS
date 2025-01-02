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

#%% Função para Calcular Diferença com Estação Conjugada
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
        conjugate_station = entry.get('Conjulgada')
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

#%% Função para Plotar Dados por Evento
def plot_event_data(data_list, intervalo, colunas_eixo_esquerdo, colunas_eixo_direito, stations, salvar_pdf=False, datafile_name='Teste'):
    """
    Plota os campos especificados para múltiplos eventos e múltiplas estações dentro de um intervalo de datas.

    Parâmetros:
        data_list (list): Lista de dicionários contendo dados das estações.
        intervalo (list): Lista com duas strings especificando a data de início e fim (formato: 'DD/MM/YYYY').
        colunas_eixo_esquerdo (list of tuples): Campos para plotar em cada painel no eixo y à esquerda (ex.: [('H_nT', 'Principal'), ('H_nT', 'Conjulgada')]).
        colunas_eixo_direito (list of tuples): Campos para plotar em cada painel no eixo y à direita (ex.: [('dH_nT_diff', 'Principal')]).
        stations (list of str): Lista de estações principais a serem analisadas.
        salvar_pdf (bool): Se True, salva os gráficos em um PDF. Padrão é False.
    """
    
    start_date = datetime.strptime(intervalo[0], '%d/%m/%Y')
    end_date = datetime.strptime(intervalo[1], '%d/%m/%Y')
    
    # Filtra os dados dentro do intervalo especificado
    filtered_data = [entry for entry in data_list if start_date <= entry.get('DataHora') <= end_date]
    
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
       
    # Divide os eventos em páginas com no máximo 6 eventos por página
    for page_start in range(0, num_events, eventos_por_pagina):
        page_events = events[page_start:page_start + eventos_por_pagina]
        fig, axes = plt.subplots(num_stations, len(page_events), figsize=(5 * len(page_events), 5 * num_stations), sharex=False)
        
        if num_stations == 1:
            axes = [axes]
        if len(page_events) == 1:
            axes = [[ax] for ax in axes]

        # Plota os dados para cada estação e evento
        for i, station in enumerate(stations):
            
            for j, event in enumerate(page_events):
                ax = axes[i][j]
                main_data = next((entry for entry in filtered_data if entry.get('Estacao') == station and entry.get('DataHora') == event), None)
                conjugate_data = None
                if main_data and main_data.get('Conjulgada'):
                    conjugate_data = next((e for e in filtered_data if e.get('Estacao') == main_data['Conjulgada'] and e.get('DataHora') == event), None)

                if not main_data:
                    ax.set_title(f"Nenhum dado disponível ({event.strftime('%d/%m/%Y')}")
                    print(station)
                    continue
                
                # Plota as colunas especificadas para a estação atual e evento no eixo y à direita
                if colunas_eixo_direito:
                    ax_right = ax.twinx()
                    for field_right, station_type in colunas_eixo_direito:
                        if station_type == 'Principal':
                            time_series = main_data['Dados']['TIME']
                            data_series = main_data['Dados'][field_right].dropna()
                            # Calcula o RMS e exibe na caixa de texto
                            rms_value_p = np.sqrt(np.mean(np.square(data_series)))
                            ax_right.plot(time_series, main_data['Dados'][field_right], linestyle='-', color='green', alpha=0.5, label=f"{colunas_eixo_direito[0]}")
        
                        elif station_type == 'Conjulgada' and conjugate_data:
                            time_series = conjugate_data['Dados']['TIME']
                            data_series = conjugate_data['Dados'][field_right].dropna()
                            # Calcula o RMS e exibe na caixa de texto
                            rms_value_c = np.sqrt(np.mean(np.square(data_series)))
                            ax_right.plot(time_series, conjugate_data['Dados'][field_right], linestyle='-', color='orange', alpha=0.5, label=f"{colunas_eixo_direito[1]}")
                    
                    # Formata o eixo x para mostrar horas no formato HH:MM
                    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    # Destaca áreas de noite e dia no fundo do gráfico
                    # ax.axvspan(0, 6, color='gray', alpha=0.2)  # Noite antes das 6:00
                    # ax.axvspan(18, 24, color='gray', alpha=0.2)  # Noite após as 18:00           
                    # Formatação do eixo Y direito para 2 algarismos significativos
                    # ax_right.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
                    
                # Plota as colunas especificadas para a estação atual e evento no eixo y à esquerda
                for field, station_type in colunas_eixo_esquerdo:
                    if station_type == 'Principal':
                        time_series = main_data['Dados']['TIME']
                        data_series = main_data['Dados'][field]
                        
                        ax.plot(time_series, main_data['Dados'][field], linestyle='-', color='green', label=f"{colunas_eixo_esquerdo[0]}")
                        # if not (np.isnan(main_data['Ponto_Esquerda']).any() or np.isnan(main_data['Ponto_Direita']).any()):
                        #     ax.scatter(main_data['Ponto_Esquerda'][0], main_data['Ponto_Esquerda'][1], color='red')
                        #     ax.scatter(main_data['Ponto_Direita'][0], main_data['Ponto_Direita'][1], color='red')
                    elif station_type == 'Conjulgada' and conjugate_data:
                        time_series = conjugate_data['Dados']['TIME']
                        data_series = conjugate_data['Dados'][field]
                        # Calcula o RMS e exibe na caixa de texto
                        rms_value = np.sqrt(np.mean(np.square(data_series)))
                        ax.plot(time_series, conjugate_data['Dados'][field], linestyle='-', color='orange', label=f"{colunas_eixo_esquerdo[1]}")
                        # if not (np.isnan(conjugate_data['Ponto_Esquerda']).any() or np.isnan(conjugate_data['Ponto_Direita']).any()):
                        #     ax.scatter(conjugate_data['Ponto_Esquerda'][0], conjugate_data['Ponto_Esquerda'][1],color='red')
                        #     ax.scatter(conjugate_data['Ponto_Direita'][0], conjugate_data['Ponto_Direita'][1],color='red')

                # Formatação do eixo Y esquerdo para 2 algarismos significativos
                # ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
                # Calcula e exibe R_squared, destacando em vermelho se for menor que 0.95
                pos_y0 = 1.10
                pos_x0 = 0.05
                pos_ystep = 0.15
                # print(station)
                if 'Qualidade' in main_data:
                    qualidade_p = main_data['Qualidade']
                                        
                if 'Qualidade' in conjugate_data:
                    qualidade_c = conjugate_data['Qualidade']
                    

                bbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5, edgecolor='black')
                ax.text(pos_x0, pos_y0-1*pos_ystep, f"RMS {field_right}  (P:C) {rms_value_p:.2f}:{rms_value_c:.2f}", transform=ax.transAxes, fontsize=10, 
                        verticalalignment='top', bbox=bbox_props)
                
                bbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5, edgecolor='black' if qualidade_c > 0.7 else 'black')
                ax.text(pos_x0, pos_y0-2*pos_ystep, f"Qualidade (P:C) = {qualidade_p:.1f}:{qualidade_c:.1f}", transform=ax.transAxes, fontsize=10,
                        verticalalignment='top', bbox=bbox_props)
                    
                # Calcula e exibe amplitude Principal, destacando em vermelho se for menor que 0.95
                if 'Amplitude' in main_data:
                    amplitude_p = main_data['Amplitude']
                    bbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5, edgecolor='black')
                    ax.text(pos_x0, pos_y0-3*pos_ystep, f"Amplitude_P = {amplitude_p:.2f}", transform=ax.transAxes, fontsize=10,
                            verticalalignment='top', bbox=bbox_props)
                    
                # Calcula e exibe amplitude conjulgada, destacando em vermelho se for menor que 0.95
                if 'Amplitude' in main_data:
                    amplitude_c = conjugate_data['Amplitude']
                    bbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5, edgecolor='black')
                    ax.text(pos_x0, pos_y0-4*pos_ystep, f"Amplitude_C = {amplitude_c:.2f}", transform=ax.transAxes, fontsize=10,
                            verticalalignment='top', bbox=bbox_props)
                    
                # Calcula e exibe amplificação, destacando em vermelho se for menor que 0.95
                if 'Amplificacao' in main_data:
                    amplificacao = main_data['Amplificacao']
                    bbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5, edgecolor='black' )
                    ax.text(pos_x0, pos_y0-5*pos_ystep, f"Ganho = {amplificacao:.2f}", transform=ax.transAxes, fontsize=10,
                            verticalalignment='top', bbox=bbox_props)
                # Adiciona o título com a parte exponencial nos eixos
                if i == 0 and j == 0:
                    ax.set_xlabel("TIME")
                    ax.set_ylabel(f"{field}")  # Substitua X pela parte exponencial apropriada
                    if colunas_eixo_direito:
                        ax_right.set_ylabel(f"{field_right}")  # Substitua Y pela parte exponencial apropriada
                    
                if i == 0:
                    ax.set_title(f"#{j + page_start} {event.strftime('%d/%m/%Y')} \n P:{station}/C:{main_data.get('Conjulgada')}",fontweight='bold')
                else:
                    ax.set_title(f"P:{station}/C:{main_data.get('Conjulgada')}",fontweight='bold')

                time_data = main_data['Dados']['TIME']
    
                # Verificar se há valores NaN ou infinitos
                if time_data.isna().any() or np.isinf(time_data).any():
                    print("Dados contêm valores NaN ou infinitos. Pulando esta iteração.")
                    continue
                # Definir os limites do eixo x
                ax.set_xlim(time_data.iloc[0], time_data.iloc[-1])
                ax.grid(True)
                # ax.set_ylim(-0.004, 0.004)
                # ax_right.set_ylim(-10, 10)

        # Adiciona uma única legenda para todos os subplots
        handles_left, labels_left = ax.get_legend_handles_labels()
        handles_right, labels_right = ax_right.get_legend_handles_labels() if colunas_eixo_direito else ([], [])
        handles_combined = handles_left + handles_right
        labels_combined = labels_left + labels_right
        fig.legend(handles_combined, labels_combined, loc='upper right')

        plt.tight_layout()
        mplcursors.cursor(hover=True)
        
        if salvar_pdf:
            pdf.savefig(fig)
        plt.show()

    # Fecha o PDF se ele foi criado
    if salvar_pdf:
        pdf.close()

#%% tools
def decimal_para_hora(decimal_hora):
    horas = int(decimal_hora)
    minutos = int((decimal_hora - horas) * 60)
    segundos = int((decimal_hora - horas - minutos / 60) * 3600)


#%%others
def plot_amplification_for_stations(my_list, stations, field):
    """
    Plota o campo especificado ao longo do tempo como pontos para as estações especificadas
    e adiciona uma linha da média e desvio padrão para cada estação, usando a mesma cor dos pontos.
    Destaca pontos que estejam na noite, baseado na longitude da estação.
    Exibe no título a quantidade total de dados plotados.

    Parâmetros:
        my_list (list): Lista de dicionários contendo dados das estações.
        stations (list): Lista de estações a serem plotadas.
        field (str): Campo a ser plotado (e.g., 'Amplificacao').
    """
    import datetime as dt
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm

    plt.figure(figsize=(12, 8))

    # Define a paleta de cores 'viridis', adequada para daltônicos
    colors = cm.get_cmap("viridis", len(stations))

    # Variável para contar o total de dados plotados
    total_data_points = 0

    # Itera sobre cada estação na lista especificada para plotar o campo especificado ao longo do tempo
    for idx, station in enumerate(stations):
        # Filtra dados para a estação atual
        station_data = [entry for entry in my_list if entry['Estacao'] == station]
        
        # Obtém os valores de tempo e do campo especificado
        times = [entry['DataHora'] for entry in station_data]
        values = [entry[field] for entry in station_data]
        longitudes = [entry['Longitude'] for entry in station_data]
        local_times = [entry['TempoLocal'] for entry in station_data]

        # Incrementa o contador de pontos de dados
        total_data_points += len(values)

        # Escolhe a cor específica para a estação
        color = colors(idx)

        # Plota todos os dados do campo especificado ao longo do tempo como pontos para a estação
        plt.scatter(times, values, label=station, alpha=1, color=color)

        # Destaca pontos que estejam na noite
        night_values = []
        night_times = []
        for i, local_time in enumerate(local_times):
            # Calcula a hora do nascer e pôr do sol aproximado (6h e 18h, respectivamente)
            sunrise = 6
            sunset = 18
            hour = local_time.hour
            if hour < sunrise or hour >= sunset:
                night_times.append(times[i])
                night_values.append(values[i])

        # Plota os pontos noturnos em uma cor diferente
        plt.scatter(night_times, night_values, edgecolor='red', facecolor='none', s=100, linewidth=1.5, label=f"{station} (Noite)")

        # Calcula e plota a linha da média e desvio padrão para a estação
        if values:  # Verifica se há dados
            mean_value = np.nanmean(values)
            std_value = np.nanstd(values)
            plt.axhline(y=mean_value, color=color, linestyle='--', linewidth=1, alpha=0.7,
                        label=f"{station} Média = {mean_value:.2f}, Desvio Padrão = {std_value:.2f}")

    # Configurações do gráfico
    plt.xlabel('Tempo')
    plt.ylabel(field)
    plt.title(f'{field} ao longo do tempo com linha da média e desvio padrão\nTotal de pontos de dados: {total_data_points}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# def plot_amplification_for_stations(my_list, stations):
#     """
#     Plota a amplificação ao longo do tempo como pontos para as estações especificadas
#     e adiciona uma linha da média de amplificação e desvio padrão para cada estação, usando a mesma cor dos pontos.
#     Exibe no título a quantidade total de dados plotados.

#     Parâmetros:
#         my_list (list): Lista de dicionários contendo dados das estações.
#         stations (list): Lista de estações a serem plotadas.
#     """
#     plt.figure(figsize=(12, 8))

#     # Define a paleta de cores 'viridis', adequada para daltônicos
#     colors = cm.get_cmap("viridis", len(stations))

#     # Variável para contar o total de dados plotados
#     total_data_points = 0

#     # Itera sobre cada estação na lista especificada para plotar sua amplificação ao longo do tempo
#     for idx, station in enumerate(stations):
#         # Filtra dados para a estação atual
#         station_data = [entry for entry in my_list if entry['Estacao'] == station]
        
#         # Obtém os valores de tempo e amplificação
#         times = [entry['DataHora'] for entry in station_data]
#         amplification = [entry['Amplificacao'] for entry in station_data]

#         # Incrementa o contador de pontos de dados
#         total_data_points += len(amplification)

#         # Escolhe a cor específica para a estação
#         color = colors(idx)

#         # Plota todos os dados de amplificação ao longo do tempo como pontos para a estação
#         plt.scatter(times, amplification, label=station, alpha=1, color=color)

#         # Calcula e plota a linha da média de amplificação e desvio padrão para a estação
#         if amplification:  # Verifica se há dados de amplificação
#             mean_amplification = np.nanmean(amplification)
#             std_amplification = np.nanstd(amplification)
#             plt.axhline(y=mean_amplification, color=color, linestyle='--', linewidth=1, alpha=0.7,
#                         label=f"{station} Média = {mean_amplification:.2f}, Desvio Padrão = {std_amplification:.2f}")

#     # Configurações do gráfico
#     plt.xlabel('Tempo')
#     plt.ylabel('Amplificação')
#     plt.title(f'Amplificação ao longo do tempo com linha da média e desvio padrão\nTotal de pontos de dados: {total_data_points}')
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()

#%%filtragem pela qualidadade
def filter_by_quality(my_list, estacoes_conjugadas):
    """
    Retorna uma lista filtrada de dados em 'my_list' com base em uma lista de estações conjugadas,
    considerando apenas as datas em que todas as estações (principal e conjugada) têm 'Qualidade' maior que 0.9.

    Parâmetros:
        my_list (list): Lista de dicionários contendo dados das estações.
        estacoes_conjugadas (dict): Dicionário com as estações principais como chaves e suas estações conjugadas como valores.

    Retorna:
        list: Lista filtrada com dados que atendem ao critério de qualidade.
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

    # Filtra as datas que satisfazem a condição de qualidade
    filtered_data = []
    for datahora, stations_data in data_index.items():
        all_stations_meet_quality = True
        for principal, conjugada in estacoes_conjugadas.items():
            principal_data = stations_data.get(principal)
            conjugada_data = stations_data.get(conjugada)

            # Verifica se ambas as estações têm 'Qualidade' > 0.9
            if (not principal_data or principal_data.get('Qualidade', 0) <= 0.9 or
                not conjugada_data or conjugada_data.get('Qualidade', 0) <= 0.9):
                all_stations_meet_quality = False
                break

        # Adiciona ao resultado final se a data satisfizer a condição para todas as estações
        if all_stations_meet_quality:
            filtered_data.extend(stations_data.values())

    return filtered_data

# plt.close('all')
# filtered_data = filter_by_quality(my_list, estacoes_conjugadas)
# plot_amplification_for_stations(my_list, stations)
# plot_amplification_for_stations(filtered_data, stations)
#%% Execução das Funções
# estacoes_conjugadas = {
#     'CXP': 'SJG',

# }
estacoes_conjugadas = {
    'CXP': 'SJG',
    'ASC': 'GUI',
    'KMH': 'DUR',
    'KDU': 'KNY'
}
# stations = sorted(set(estacoes_conjugadas.keys()).union(estacoes_conjugadas.values()))

stations= list(estacoes_conjugadas.keys())

intervalo=['01/10/2023', '31/12/2025']
# intervalo=['09/05/2024', '11/05/2024']
# intervalo=['01/01/2015', '31/12/2025']

# datafile_name = 'selected_statios_full_singnal.pkl'
# metadata, my_list = load_data(datafile_name)
# plot_event_data(my_list, intervalo=['01/01/2023', '31/12/2023'], colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjulgada')], colunas_eixo_direito=[('dH_nT', 'Principal')], stations=stations, salvar_pdf=True, datafile_name = datafile_name)

plt.close('all')

datafile_name = 'selected_stations_just_events.pkl'
metadata, my_list = load_data(datafile_name)
plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjulgada')], colunas_eixo_direito=[('dH_nT_rmsacumulado', 'Principal'), ('dH_nT_rmsacumulado', 'Conjulgada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms')

# filtered_data = filter_by_quality(my_list, estacoes_conjugadas)
# plot_event_data(filtered_data, intervalo=intervalo, colunas_eixo_esquerdo=[('dH_nT_rms', 'Principal'), ('dH_nT_rms', 'Conjulgada')], colunas_eixo_direito=[('dH_nT_rmsacumulado', 'Principal'), ('dH_nT_rmsacumulado', 'Conjulgada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms_filtred')

# plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT', 'Principal'),('H_nT', 'Conjulgada')], colunas_eixo_direito=[('D_deg', 'Principal'),('D_deg', 'Conjulgada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_D')

# plt.close('all')

plot_amplification_for_stations(my_list, stations,"RMSE_H_nT_rmsacumulado")

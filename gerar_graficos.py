campo = 'H_nT'
# filtro = 'iir-pc5'
filtro = 'wavelet'
# campo = 'D_deg'
# campo = 'Z_nT'
# Obtém o valor do campo a partir dos argumentos de linha de comando
import sys
import os
from processamento import *
from plots import *
# campo = sys.argv[1]
global event_dates, dados_por_data

files_folder = diretorio_base = os.getcwd()
# stations = 'CXP ASC KMH KDU SJG GUI DUR KNY SMS'.split()
estacoes_conjugadas = {
    'SMS': 'SJG',
    'ASC': 'GUI',
    'GAN': 'ABG',
    'KDU': 'KNY'
}
# estacoes_conjugadas = {
#     'SMS': 'SJG',
#     'ASC': 'GUI',
# }
# estacoes_conjugadas = {
#     'SMS': 'SJG',
#     'ASC': 'GUI',
#     'GAN': 'ABG',
#     'KDU': 'KNY',
#     'PAL': 'KDU',
#     'ORC': 'SBL',
#     'HER': 'FUR',
#     'KMH': 'AQU',
#     'KHB': 'PAG',
#     'GNA': 'MZL',
#     'CNB': 'PET',
#     'CBA': 'JAT',
#     'CGR': 'BOA'
# }
# estacoes_conjugadas = {
#     'SMS': 'SJG',
#     'ASC': 'GUI',
#     'GAN': 'ABG',
#     'KDU': 'KNY',
#     'KMH': 'AQU',
#     'ASP': 'KAK',
#     'GNA': 'MZL',
#     'SHE': 'STT',
#     'CBA': 'JAT'
#     }

# estacoes_conjugadas = {
#     'SMS': 'SJG'
# }
# estacoes_conjugadas = {
#     'CXP': 'SJG'
# }
stations = sorted(set(estacoes_conjugadas.keys()).union(estacoes_conjugadas.values()))

folder_path = "sc_eventos"
event_dates = get_events_dates(folder_path)
# event_dates = event_dates.iloc[[1,2]]
# event_dates = pd.DataFrame({
#     'Data': ['2016-10-25'],
#     'Hora': [9.2]
# })

# event_dates = pd.DataFrame({
#     'Data': ['2023-07-13'],
#     'Hora': [12.2]
# })

# event_dates = pd.DataFrame({
#     'Data': ['2025-03-20'],
#     'Hora': [12]
# })

download_files(files_folder, event_dates['Data'], stations,duration = 1)
event_dates['Data'] = pd.to_datetime(event_dates['Data'])

# %% testes

# filtra dados por data
dados_por_data = get_date_selection(os.path.join(files_folder, 'Dados'),event_dates,estacoes_conjugadas)
# dados_por_data = offset(dados_por_data,campo=campo,mode='igrf')
dados_por_data = quality_data_test(dados_por_data,campo = campo)
# dados_por_data = filter_by_quality(dados_por_data, estacoes_conjugadas,limite=0.9)

dados_por_data = add_conjugate_entry(dados_por_data, estacoes_conjugadas)
# dados_por_data = calculate_conjugate_difference(dados_por_data)
save_data(dados_por_data, f'Resultados/selected_stations_full_singnal.pkl', metadata="")

# Define o tamanho da janela em horas decimais (exemplo: 15.5 é as 15h e 30 min)
tamanho_janela = 4

eventos_sc = recorte_evento(dados_por_data, tamanho_janela)
eventos_sc = offset(eventos_sc,campo=campo,mode='first_value')

save_data(eventos_sc, f'Resultados/eventos_sc.pkl', metadata="")

eventos_sc = quality_data_test(eventos_sc,campo = campo)
# eventos_sc_filtered = filter_by_quality(eventos_sc, estacoes_conjugadas,limite=0.9)
# eventos_sc_filtered = quality_data_test(eventos_sc_filtered,campo = campo)

# eventos_sc_est = derivativas2(eventos_sc_filtered, campo=campo, sinal = 'pc5')
eventos_sc_est = derivativas2(eventos_sc, campo=campo, filtro = filtro)
save_data(eventos_sc_est, f'Resultados/eventos_sc_est.pkl', metadata="")

eventos_sc_est= quality_data_test(eventos_sc_est,campo=campo,intervalo=(-100, 100))

amp_sc = amplificacao_estacoes(eventos_sc_est, estacoes_conjugadas)

amp_sc_local = calcular_tempo_local(amp_sc)

amp_sc_local_conj_diff = calculate_conjugate_difference2(amp_sc_local,campo=f'd{campo}')
amp_sc_local_conj_diff = calculate_conjugate_difference2(amp_sc_local,campo=f'd{campo}_absacumulado')
amp_sc_local_conj_diff = estatisticas2(amp_sc_local,campo=f'd{campo}_absacumulado_diff')

amp_sc = amplificacao_D_estacoes_dcampo_abs(amp_sc_local_conj_diff, estacoes_conjugadas, campo=f'd{campo}_abs')
amp_sc = amplificacao_E_estacoes_dcampo_abs(amp_sc, estacoes_conjugadas, campo=f'd{campo}_absacumulado')
amp_sc = amplificacao_Pc5(amp_sc, estacoes_conjugadas, campo=f'{campo}_Pc5')

fft = espectro_frequencia(amp_sc, campo='H_nT', amostragem=1)

save_data(fft, f'Resultados/selected_stations_eventwindow_{tamanho_janela}h.pkl',metadata="")

#%% plots
from plots import *

intervalo=['01/01/2015', '01/01/2025']
filtro_qualidade = 0
stations= list(estacoes_conjugadas.keys())

# stations1=['SMS', 'ASC', 'GAN', 'KDU', 'PAL']
# stations2= ['ORC', 'HER', 'KMH', 'KHB', 'GNA', 'CNB']

plt.close('all')

datafile_name = f'Resultados/selected_stations_eventwindow_{tamanho_janela}h.pkl'
metadata, my_list = load_data(datafile_name)

#plota valor 1D (amplificação, rmse, etc)
my_list_filtered = filter_by_quality(my_list, estacoes_conjugadas,limite=filtro_qualidade)

#%% plota graficos da amplificação com filtro 
# # plot_amplification_for_stations(my_list_filtered, stations, "Amplificacao", titulo=campo, 
# #                                 save_path=f'Resultados/{campo}_{filtro}__historico_amplificacao_ano')
# # plot_amplification_for_stations(my_list, stations, "Amplificacao", limite_qualidade=0.9, 
# #                                 titulo=campo, save_path=f'Resultados/{campo}_{filtro}_historico_amplificacao_ano_Q9')

# plot_grouped_bars_by_month(my_list_filtered, stations, "Amplificacao", titulo=campo, 
#                            save_path=f'Resultados/{campo}_{filtro}__historico_amplificacao_ano_barra_filtrado')
# plot_grouped_bars_by_month(my_list, stations, "Amplificacao", titulo=campo, 
#                            save_path=f'Resultados/{campo}_{filtro}__historico_amplificacao_ano_barra')

# plot_bar_chart_for_stations(my_list_filtered, stations, "Amplificacao", 
#                             save_path=f'Resultados/{campo}_{filtro}__plot_bar_chart_for_stations_amplificacao')
# plot_bar_chart_for_stations(my_list, stations, "Amplificacao", limite_qualidade=0.9, 
#                             save_path=f'Resultados/{campo}_{filtro}__plot_bar_chart_for_stations_amplificacaoQ9')

# plot_scatter_for_stations(my_list_filtered, stations, "Amplificacao", 
#                           save_path=f'Resultados/{campo}_{filtro}__plot_scatter_for_stations_amplificacao')
# plot_scatter_for_stations(my_list, stations, "Amplificacao", limite_qualidade=0.9, 
#                           save_path=f'Resultados/{campo}_{filtro}__plot_scatter_for_stations_amplificacao_Q9')
# mplcursors.cursor(hover=True) 

#%%
plt.close('all')

plot_variantes = ["Amplificacao","Amplificacao_dH_nT_abs", "Amplificacao_dH_nT_absacumulado","Amplificacao_H_nT_Pc5"]
limite_qualidade=0  
f107_data = get_filtered_solar_flux_data()


for variant in plot_variantes:
    # plot_amplification_for_stations(my_list, stations, variant, titulo=campo, 
    #                                 save_path=f'Resultados/{campo}_historico_{variant}_ano_filtrado')
    # plot_amplification_for_stations(my_list, stations, variant, limite_qualidade=0.7, 
    #                                 titulo=campo, save_path=f'Resultados/{campo}_historico_{variant}_ano_Q9')
    
    plot_grouped_bars_by_month(my_list, stations, variant, titulo=campo, 
                               save_path=f'Resultados/{campo}_historico_{variant}_ano_barra_completo')
    plot_grouped_bars_by_month(my_list_filtered, stations, variant, titulo=campo, 
                               save_path=f'Resultados/{campo}_historico_{variant}_ano_barra_simultaneoQ{int(filtro_qualidade*100)}')
    plot_grouped_bars_with_f107(my_list, stations, variant,f107_data, titulo=campo, 
                               save_path=f'Resultados/{campo}_historico_{variant}_ano_barra_completo_f10_7')
    # plot_bar_chart_for_stations(my_list_filtered, stations, variant, 
    #                             save_path=f'Resultados/{campo}_plot_bar_chart_for_stations_{variant}')
    # plot_bar_chart_for_stations(my_list, stations, variant, limite_qualidade=limite_qualidade, 
    #                             save_path=f'Resultados/{campo}_plot_bar_chart_for_stations_{variant}_Q{limite_qualidade}')
    
    # plot_scatter_for_stations(my_list_filtered, stations, variant, 
    #                           save_path=f'Resultados/{campo}_plot_scatter_for_stations_{variant}')
    # plot_scatter_for_stations(my_list, stations, variant, limite_qualidade=limite_qualidade, 
    #                           save_path=f'Resultados/{campo}_plot_scatter_for_stations_{variant}_Q{limite_qualidade}')

# Adicionando a chamada para 'Qualidade', que não depende das variantes
plot_grouped_bars_by_month(my_list, stations, "Qualidade", titulo=campo, 
                           save_path=f'Resultados/{campo}_historico_qualidade_ano_barra')

# cursor = mplcursors.cursor(bars, hover=True)


# %%
# import matplotlib.pyplot as plt

# plot_variantes = ["Amplificacao", "Amplificacao_dH_nT_abs", 
#                   "Amplificacao_dH_nT_absacumulado", "Amplificacao_H_nT_Pc5"]

# for variant in plot_variantes:
#     fig = plt.figure(figsize=(15, 8))
#     plt.suptitle(f'{campo}', fontsize=16)
    
#     # Subplot 1
#     plt.subplot(2, 2, 1)
#     plot_bar_chart_for_stations2(my_list_filtered, stations, variant, show=True)

#     # Subplot 2
#     plt.subplot(2, 2, 2)
#     plot_bar_chart_for_stations2(my_list, stations, variant, limite_qualidade=0.9, show=True)

#     # Subplot 3
#     plt.subplot(2, 2, 3)
#     plot_scatter_for_stations2(my_list_filtered, stations, variant, show=True)

#     # Subplot 4
#     plt.subplot(2, 2, 4)
#     plot_scatter_for_stations2(my_list, stations, variant, limite_qualidade=0.9, show=True)
    
#     # Ajusta layout e salva tudo em um único arquivo
#     plt.tight_layout(rect=[0, 0, 1, 0.95])
#     plt.savefig(f'Resultados/{campo}_historico_{variant}_conjunto.png')
#     plt.close()
#%%
# Garante que o diretório exista
os.makedirs('Resultados', exist_ok=True)

plot_variantes = ["Amplificacao", "Amplificacao_dH_nT_abs", 
                  "Amplificacao_dH_nT_absacumulado", "Amplificacao_H_nT_Pc5"]

num_variantes = len(plot_variantes)

# Cria figura com 2 linhas (tipos de dados) e N colunas (variants)
fig, axs = plt.subplots(2, num_variantes, figsize=(5 * num_variantes, 10))
fig.suptitle(f'{campo}', fontsize=18)

for col, variant in enumerate(plot_variantes):
    # Linha 0: my_list_filtered
    plt.sca(axs[0, col])
    plot_bar_chart_for_stations2(my_list, stations, variant, show=True)
    axs[0, col].set_title(f'{variant} (Completo)', fontsize=12)

    # Linha 1: my_list
    plt.sca(axs[1, col])
    plot_bar_chart_for_stations2(my_list_filtered, stations, variant, show=True)
    axs[1, col].set_title(f'{variant} (Q simultâneo) ', fontsize=12)

# Ajusta layout e salva a figura única
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(f'Resultados/{campo}_amplificacoes_barra.png')
plt.close()

#%%
# Garante que o diretório exista
plots_qualidade = [0.7,0.8,0.9,1]
os.makedirs('Resultados', exist_ok=True)

plot_variantes = ["Amplificacao", "Amplificacao_dH_nT_abs", 
                  "Amplificacao_dH_nT_absacumulado", "Amplificacao_H_nT_Pc5"]

num_variantes = len(plot_variantes)
num_plots = len(plots_qualidade)


for lin, variant in enumerate(plot_variantes):
    # Cria figura com 2 linhas (tipos de dados) e N colunas (variants)
    fig, axs = plt.subplots(1,num_plots, figsize=(5 * num_variantes, 10))
    fig.suptitle(f'{campo}', fontsize=18)
    for col, qualidade in enumerate(plots_qualidade):
        if qualidade == 1:
            # coluna 0: 
            plt.sca(axs[col])
            plot_scatter_for_stations2(my_list_filtered, stations, variant, show=True)
            axs[col].set_title(f'Qualidade>{qualidade} (Evento simultâneo)', fontsize=12)
            continue
        # coluna 0: 
        plt.sca(axs[col])
        plot_scatter_for_stations2(my_list, stations, variant, show=True,limite_qualidade=qualidade)
        axs[col].set_title(f'Qualidade>{qualidade}', fontsize=12)

    # Ajusta layout e salva a figura única
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(f'Resultados/{campo}_amplificacoes_dispersao_{variant}.png')
    plt.close()
# plot_event_data(my_list, 
#                 intervalo = intervalo, 
#                 event_dates = event_dates, 
#                 titulo = f'{campo} - Pc5 Todas estações',
#                 colunas_eixo_esquerdo=[(campo, 'Principal'), (campo, 'Conjugada')], 
#                 colunas_eixo_direito=[(f'{campo}_ajuste', 'Principal'), (f'{campo}_ajuste', 'Conjugada')],
#                 parametros=[('Qualidade', 'Principal'),('Qualidade', 'Conjugada'),('Amplificacao', 'Principal')], 
#                 stations = stations, 
#                 salvar_pdf=True,
#                 datafile_name = f'{campo}_detalhes_Pc5',
#                 view_points=True)

# plot_event_data(my_list_filtered, 
#                 intervalo = intervalo, 
#                 event_dates = event_dates, 
#                 titulo = f'{campo} - Pc5 Qualidade alta',
#                 colunas_eixo_esquerdo=[(campo, 'Principal'), (campo, 'Conjugada')], 
#                 colunas_eixo_direito=[(f'{campo}_ajuste', 'Principal'), (f'{campo}_ajuste', 'Conjugada')],
#                 parametros=[('Qualidade', 'Principal'),('Qualidade', 'Conjugada'),('Amplificacao', 'Principal')], 
#                 stations = stations, 
#                 salvar_pdf=True, 
#                 datafile_name = f'{campo}_detalhes_filtrado_pc5',
#                 view_points=True)

# #%%%
# plot_field_by_local_time(my_list_filtered, stations,"Amplificacao", titulo=campo , save_path = f'Resultados/{campo}_TempoLocal_pc5')
# mplcursors.cursor(hover=True) 
# plot_frequency_bars(my_list_filtered, stations, "Amplificacao", titulo=campo, save_path = f'Resultados/{campo}_TempoLocal_barra_pc5')

# #%%
# flux_data = get_filtered_solar_flux_data()
# #%%
# # 

# plot_amplificacao_and_solar_flux(my_list, flux_data, intervalo, stations,save_path = f'Resultados/{campo}_Amplificacao_fluxosolar_pc5')
# #%%
# resultado = espectro_frequencia(my_list_filtered, campo='H_nT', amostragem=1)
# plot_espectros_frequencia(resultado, stations,campo = f'Amplitude_{campo}', salvar_pdf=True, nome_pdf='Resultados/espectrosFFT.pdf')
# mplcursors.cursor(hover=True) 
#%%

# print_events_above_threshold(my_list, stations, field='Amplificacao', threshold=3)
print_events_outside_range(
    my_list,
    stations,
    field='Amplificacao',
    min_threshold=-10.0,
    max_threshold=10.0
)
my_list = print_events_outside_range(my_list, stations, 'Amplificacao', -10, 10, excluir=True)

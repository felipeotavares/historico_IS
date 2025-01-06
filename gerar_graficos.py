campo = 'H_nT'
# campo = 'D_deg'
# campo = 'Z_nT'
# Obtém o valor do campo a partir dos argumentos de linha de comando
import sys
import os
from processamento import *
from plots import *
# campo = sys.argv[1]

files_folder = diretorio_base = os.getcwd()
# stations = 'CXP ASC KMH KDU SJG GUI DUR KNY SMS'.split()
estacoes_conjugadas = {
    'SMS': 'SJG',
    'ASC': 'GUI',
    'GAN': 'ABG',
    'KDU': 'KNY'
}
# estacoes_conjugadas = {
#     'CXP': 'SJG'
# }
stations = sorted(set(estacoes_conjugadas.keys()).union(estacoes_conjugadas.values()))

folder_path = "sc_eventos"
event_dates = get_events_dates(folder_path)
# event_dates = event_dates.iloc[[126]]
event_dates = pd.DataFrame({
    'Data': ['2016-10-25'],
    'Hora': [9.2]
})

# download_files(files_folder, event_dates['Data'], stations,duration = 1)

# %% testes

event_dates['Data'] = pd.to_datetime(event_dates['Data'])
# filtra dados por data
dados_por_data = get_date_selection(os.path.join(files_folder, 'Dados'),event_dates,estacoes_conjugadas)
# dados_por_data = normalize(dados_por_data)

dados_por_data = add_conjugate_entry(dados_por_data, estacoes_conjugadas)
# dados_por_data = calculate_conjugate_difference(dados_por_data)
save_data(dados_por_data, f'Resultados/{campo}_selected_stations_full_singnal.pkl', metadata="")

# Define o tamanho da janela em horas decimais (exemplo: 15.5 é as 15h e 30 min)
tamanho_janela = 2
eventos_sc = recorte_evento(dados_por_data, tamanho_janela)
eventos_sc = quality_data_test(eventos_sc,campo = campo)

eventos_sc_est = derivativas2(eventos_sc, campo=campo, sinal = 'pc5')

eventos_sc_est= quality_data_test(eventos_sc_est,campo=campo)

amp_sc = amplificacao_estacoes(eventos_sc_est, estacoes_conjugadas)

amp_sc_local = calcular_tempo_local(amp_sc)

amp_sc_local_conj_diff = calculate_conjugate_difference2(amp_sc_local,campo=f'd{campo}')
amp_sc_local_conj_diff = calculate_conjugate_difference2(amp_sc_local,campo=f'd{campo}_absacumulado')
amp_sc_local_conj_diff = estatisticas2(amp_sc_local,campo=f'd{campo}_absacumulado_diff')

amp_sc = amplificacao_D_estacoes_dcampo_abs(amp_sc, estacoes_conjugadas, campo=f'd{campo}_abs')
amp_sc = amplificacao_E_estacoes_dcampo_abs(amp_sc, estacoes_conjugadas, campo=f'd{campo}_absacumulado')

save_data(amp_sc_local_conj_diff, f'Resultados/{campo}_selected_stations_just_events.pkl',metadata="")

#%% plots
from plots import *

intervalo=['01/01/2015', '01/01/2025']

stations= list(estacoes_conjugadas.keys())

plt.close('all')

datafile_name = f'Resultados/{campo}_selected_stations_just_events.pkl'
metadata, my_list = load_data(datafile_name)

#plota valor 1D (amplificação, rmse, etc)
my_list_filtered = filter_by_quality(my_list, estacoes_conjugadas,limite=0)
# my_list_filtered = my_list
#%%
plot_amplification_for_stations(my_list_filtered, stations,"Amplificacao", titulo=campo , save_path = f'Resultados/{campo}_historico_amplificacao_ano_pc5')

plot_grouped_bars_by_month(my_list_filtered, stations,"Amplificacao", titulo=campo , save_path = f'Resultados/{campo}_historico_amplificacao_ano_barra_pc5')

plot_grouped_bars_by_month(my_list, stations,"Qualidade", titulo=campo , save_path = f'Resultados/{campo}_historico_qualidade_ano_barra_pc5')

mplcursors.cursor(hover=True) 

plot_event_data(my_list, 
                intervalo = intervalo, 
                event_dates = event_dates, 
                titulo = f'{campo} - Pc5 Todas estações',
                colunas_eixo_esquerdo=[(campo, 'Principal'), (campo, 'Conjugada')], 
                colunas_eixo_direito=[(f'{campo}_ajuste', 'Principal'), (f'{campo}_ajuste', 'Conjugada')],
                parametros=[('Qualidade', 'Principal'),('Qualidade', 'Conjugada'),('Amplificacao', 'Principal')], 
                stations = stations, 
                salvar_pdf=True,
                datafile_name = f'{campo}_detalhes_Pc5',
                view_points=True)

plot_event_data(my_list_filtered, 
                intervalo = intervalo, 
                event_dates = event_dates, 
                titulo = f'{campo} - Pc5 Qualidade alta',
                colunas_eixo_esquerdo=[(campo, 'Principal'), (campo, 'Conjugada')], 
                colunas_eixo_direito=[(f'{campo}_ajuste', 'Principal'), (f'{campo}_ajuste', 'Conjugada')],
                parametros=[('Qualidade', 'Principal'),('Qualidade', 'Conjugada'),('Amplificacao', 'Principal')], 
                stations = stations, 
                salvar_pdf=True, 
                datafile_name = f'{campo}_detalhes_full_pc5',
                view_points=True)

#%%%
plot_field_by_local_time(my_list_filtered, stations,"Amplificacao", titulo=campo , save_path = f'Resultados/{campo}_TempoLocal_pc5')
mplcursors.cursor(hover=True) 
plot_frequency_bars(my_list_filtered, stations, "Amplificacao", titulo=campo, save_path = f'Resultados/{campo}_TempoLocal_barra_pc5')

#%%
flux_data = get_filtered_solar_flux_data()
#%%
# plt.close('all')

plot_amplificacao_and_solar_flux(my_list, flux_data, intervalo, stations,save_path = f'Resultados/{campo}_Amplificacao_fluxosolar_pc5')

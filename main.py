# -*- coding: utf-8 -*-
from processamento import *

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
# event_dates = pd.DataFrame({
#     'Data': ['2021-05-26'],
#     'Hora': [7.5]
# })


# download_files(files_folder, event_dates['Data'], stations,duration = 1)


# %% testes
# estacoes_conjugadas = {
#     'SMS': 'SJG',
#     'ASC': 'GUI',
#     'KDU': 'KNY'
# }

event_dates['Data'] = pd.to_datetime(event_dates['Data'])
# filtra dados por data
dados_por_data = get_date_selection(os.path.join(files_folder, 'Dados'),event_dates,estacoes_conjugadas)
# dados_por_data = normalize(dados_por_data)

dados_por_data = add_conjugate_entry(dados_por_data, estacoes_conjugadas)
# dados_por_data = calculate_conjugate_difference(dados_por_data)
save_data(dados_por_data, 'selected_stations_full_singnal.pkl', metadata="")

# Define o tamanho da janela em horas decimais (exemplo: 15.5 é as 15h e 30 min)
tamanho_janela = 2
eventos_sc = recorte_evento(dados_por_data, tamanho_janela)
eventos_sc= quality_data_test(eventos_sc)
eventos_sc_est = derivativas(eventos_sc)
eventos_sc_est= quality_data_test(eventos_sc_est)

amp_sc = amplificacao_estacoes(eventos_sc_est, estacoes_conjugadas)
amp_sc = amplificacao_estacoes_dH_nT_abs(amp_sc, estacoes_conjugadas)
amp_sc = amplificacao_estacoes_dH_nT_absacumulado(amp_sc, estacoes_conjugadas)


amp_sc_local = calcular_tempo_local(amp_sc)
amp_sc_local_conj_diff = calculate_conjugate_difference(amp_sc_local)
amp_sc_local_conj_diff = estatisticas(amp_sc_local)

save_data(amp_sc_local_conj_diff, 'selected_stations_just_events.pkl',metadata="")

#%% plota
from plots import *


# stations = sorted(set(estacoes_conjugadas.keys()).union(estacoes_conjugadas.values()))

# intervalo=['01/01/2015', '30/12/2024']
# intervalo=['01/01/2023', '31/12/2024']
# intervalo=['01/01/2022', '31/01/2022']
intervalo=['25/05/2021', '27/05/2021']

stations= list(estacoes_conjugadas.keys())

plt.close('all')

datafile_name = 'selected_stations_just_events.pkl'
metadata, my_list = load_data(datafile_name)

#plota valor 1D (amplificação, rmse, etc)
my_list_filtered = filter_by_quality(my_list, estacoes_conjugadas,limite=0)
# my_list_filtered = my_list
#%%
plot_amplification_for_stations(my_list_filtered, stations,"Amplificacao", titulo="" , save_path = 'Resultados/historico_amplificacao_ano_H_nT')
plot_amplification_for_stations(my_list_filtered, stations,"Amplificacao_dH_nT_abs", titulo="" , save_path = 'historico_amplificacao_ano_dH_nT_abs')
plot_amplification_for_stations(my_list_filtered, stations,"Amplificacao_dH_nT_absacumulado", titulo="" , save_path = 'historico_amplificacao_ano_dH_nT_absacumulado')

plot_grouped_bars_by_month(my_list_filtered, stations,"Amplificacao", titulo="" , save_path = 'historico_amplificacao_ano_barra_H_nT')
plot_grouped_bars_by_month(my_list_filtered, stations,"Amplificacao_dH_nT_abs", titulo="" , save_path = 'historico_amplificacao_ano_barra_dH_abs')
plot_grouped_bars_by_month(my_list_filtered, stations,"Amplificacao_dH_nT_absacumulado", titulo="" , save_path = 'historico_amplificacao_ano_barra_dH_absacumulado')

plot_grouped_bars_by_month(my_list, stations,"Qualidade", titulo="" , save_path = 'historico_qualidade_ano_barra_H_nT')

# plot_bar_chart_for_stations(my_list_filtered, stations,"Amplificacao", titulo="Distribuição de amplificação \n por par de estação conjulgadas" ,save_path = 'historico_amplificacao_estacao_barra')
# plot_scatter_for_stations(my_list_filtered, stations,"Amplificacao", titulo="Distribuição de amplificação \n por par de estação conjulgadas" ,save_path = 'historico_amplificacao_estacao_pontos')

mplcursors.cursor(hover=True) 

plot_event_data(my_list_filtered, intervalo = intervalo, event_dates = event_dates, colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjugada')], colunas_eixo_direito=[('H_nT_ajuste', 'Principal'), ('H_nT_ajuste', 'Conjugada')],parametros=[('Qualidade', 'Principal'),('Qualidade', 'Conjugada'),('Amplificacao', 'Principal')], stations = stations, salvar_pdf=True, datafile_name = 'detalhes_H_nT',view_points=True)
plot_event_data(my_list_filtered, intervalo = intervalo, event_dates = event_dates, colunas_eixo_esquerdo=[('dH_nT_abs', 'Principal'), ('dH_nT_abs', 'Conjugada')], colunas_eixo_direito=[('dH_nT', 'Principal'), ('dH_nT', 'Conjugada')],parametros=[('Qualidade', 'Principal'),('Qualidade', 'Conjugada'),('Amplificacao_dH_nT_abs', 'Principal')], stations = stations, salvar_pdf=True, datafile_name = 'detalhes_dH_nT_abs',view_points=True)
plot_event_data(my_list_filtered, intervalo = intervalo, event_dates = event_dates, colunas_eixo_esquerdo=[('dH_nT_absacumulado', 'Principal'), ('dH_nT_absacumulado', 'Conjugada')], colunas_eixo_direito=[('dH_nT_abs', 'Principal'), ('dH_nT_abs', 'Conjugada')],parametros=[('Qualidade', 'Principal'),('Qualidade', 'Conjugada'),('Amplificacao_dH_nT_abs', 'Principal')], stations = stations, salvar_pdf=True, datafile_name = 'detalhes_dH_nT_absacumulado',view_points=True)

#%%%
plot_field_by_local_time(my_list_filtered, stations,"Amplificacao", titulo="" , save_path = 'TempoLocal_H_nT')
mplcursors.cursor(hover=True) 
plot_frequency_bars(my_list_filtered, stations, "Amplificacao", titulo="" , save_path = 'TempoLocal_H_nT_barra')

#%%
flux_data = get_filtered_solar_flux_data()
#%%
plt.close('all')

plot_amplificacao_and_solar_flux(my_list, flux_data, intervalo, stations)


#%%
# datas_e_estacoes_dbdt = [
#     {"DataHora": item['DataHora'], "Estacao": item['Estacao']}
#     for item in my_list_filtered
# ]
# df_datas_e_estacoes_dbdt = pd.DataFrame(datas_e_estacoes_dbdt)

# datas_e_estacoes_origin = [
#     {"DataHora": item['DataHora'], "Estacao": item['Estacao']}
#     for item in my_list_filtered
# ]
# df_datas_e_estacoes_origin = pd.DataFrame(datas_e_estacoes_origin)

# df_faltando_no_dbdt = (
#     df_datas_e_estacoes_origin
#     .merge(df_datas_e_estacoes_dbdt, on=["DataHora", "Estacao"], how="left", indicator=True)
#     .query("_merge == 'left_only'")
#     .drop("_merge", axis=1)
# )

# df_faltando_no_origin = (
#     df_datas_e_estacoes_dbdt
#     .merge(df_datas_e_estacoes_origin , on=["DataHora", "Estacao"], how="left", indicator=True)
#     .query("_merge == 'left_only'")
#     .drop("_merge", axis=1)
# )



# plot_event_data(my_list_filtered, intervalo = intervalo, event_dates = event_dates, colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjugada')], colunas_eixo_direito=[('dH_nT_rms', 'Principal'), ('dH_nT_rms', 'Conjugada')],parametros=[('Amplitude', 'Principal'),('Amplitude', 'Conjugada'),('Qualidade', 'Conjugada'),('Amplificacao', 'Principal')], stations = stations, salvar_pdf=True, datafile_name = 'detalhes_dH_nT_individual',view_points=True)

# anomalous_data = buscar_anomalos(my_list_filtered, stations=stations, field='Amplificacao', condition='> 3')
# plot_event_data(my_list, intervalo = intervalo, event_dates = anomalous_data, colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjugada')], colunas_eixo_direito=[('H_nT_ajuste', 'Principal'), ('H_nT_ajuste', 'Conjugada')],parametros=[('Amplitude', 'Principal'),('Amplitude', 'Conjugada'),('Qualidade', 'Conjugada'),('Amplificacao', 'Principal')], stations = stations, salvar_pdf=True, datafile_name = 'detalhes_anomalos')

# plot_amplification_for_stations(my_list_filtered, stations,"Amplificacao")
# 
#plota variavel 2D (H_nT,dH_nT...)
# plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjugada')], colunas_eixo_direito=[('H_nT_ajuste', 'Principal'), ('H_nT_ajuste', 'Conjugada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms')
# plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT', 'Conjugada')], colunas_eixo_direito=[('dH_nT', 'Principal'), ('dH_nT', 'Conjugada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms')
# plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjugada')], colunas_eixo_direito=[('H_nT_ajuste', 'Principal'), ('H_nT_ajuste', 'Conjugada')],parametros=[('Amplitude', 'Principal'),('Amplitude', 'Conjugada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms')
# plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT_iir', 'Principal'), ('H_nT_iir', 'Conjugada')], colunas_eixo_direito=[('H_nT_ajuste', 'Principal'), ('H_nT_ajuste', 'Conjugada')],parametros=[('Amplitude', 'Principal'),('Amplitude', 'Conjugada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms')

# plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjugada')], colunas_eixo_direito=[], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms')


#%%outrs opções 
# # datafile_name = 'selected_statios_full_singnal.pkl'
# # metadata, my_list = load_data(datafile_name)
# # plot_event_data(my_list, intervalo=['01/01/2023', '31/12/2023'], colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjugada')], colunas_eixo_direito=[('dH_nT', 'Principal')], stations=stations, salvar_pdf=True, datafile_name = datafile_name)

# plt.close('all')

# datafile_name = 'selected_stations_just_events.pkl'
# metadata, my_list = load_data(datafile_name)
# plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT', 'Principal'), ('H_nT', 'Conjugada')], colunas_eixo_direito=[('dH_nT_rmsacumulado', 'Principal'), ('dH_nT_rmsacumulado', 'Conjugada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms')

# # filtered_data = filter_by_quality(my_list, estacoes_conjugadas)
# # plot_event_data(filtered_data, intervalo=intervalo, colunas_eixo_esquerdo=[('dH_nT_rms', 'Principal'), ('dH_nT_rms', 'Conjugada')], colunas_eixo_direito=[('dH_nT_rmsacumulado', 'Principal'), ('dH_nT_rmsacumulado', 'Conjugada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_rms_filtred')

# # plot_event_data(my_list, intervalo=intervalo, colunas_eixo_esquerdo=[('H_nT', 'Principal'),('H_nT', 'Conjugada')], colunas_eixo_direito=[('D_deg', 'Principal'),('D_deg', 'Conjugada')], stations = stations, salvar_pdf=True, datafile_name = 'selected_stations_just_events_D')

# # plt.close('all')

# plot_amplification_for_stations(my_list, stations,"RMSE_H_nT_rmsacumulado")

# df = my_list[0]['Dados']

# max_values = df['H_nT_ajuste'].max()
# print(max_values)
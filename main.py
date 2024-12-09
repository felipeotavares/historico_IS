# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:46:06 2024

@author: felip
"""
import os

from funcoes import (
    get_events_dates,
    download_files,
    get_filtered_solar_flux_data,
    process_data,
    sigmoid,
    caract_ajuste,
    time_to_decimal_24
)
from plot import plot_amplificacao_and_solar_flux

def main():
    files_folder = os.getcwd()
    stations = 'SJG GUI KNY SMS ASC KDU'.split()
    folder_path = "sc_eventos"
    event_dates = get_events_dates(folder_path)
    
    download_files(files_folder, event_dates['Data'], stations)
    dados_por_data = get_date_selection(os.path.join(files_folder, 'Dados'), event_dates)
    
    tamanho_janela = 1
    eventos_sc = recorte_evento(dados_por_data, tamanho_janela)
    eventos_sc_est = derivativas(eventos_sc)
    
    estacoes_conjugadas = {'SMS': 'SJG', 'ASC': 'GUI', 'KDU': 'KNY'}
    amp_sc = amplificacao_estacoes(eventos_sc_est, estacoes_conjugadas)
    amp_sc_local = calcular_tempo_local(amp_sc)
    
    anos = [2019, 2020, 2021, 2022, 2023, 2024]
    plot_amplificacao_por_data(amp_sc_local, anos, 'SJG ASC KDU')
    
    filtered_data = get_filtered_solar_flux_data()
    if filtered_data is not None:
        plot_amplificacao_and_solar_flux(amp_sc_local, filtered_data, anos, 'SJG ASC KDU')

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:45:46 2024

@author: felip
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_amplificacao_and_solar_flux(eventos_sc_local, filtered_data, anos, estacoes):
    df_amplificacao = pd.DataFrame(eventos_sc_local)
    if 'Amplificacao' not in df_amplificacao.columns or 'DataHora' not in df_amplificacao.columns or 'RMSE' not in df_amplificacao.columns:
        print("A lista de eventos não contém dados de amplificação, DataHora ou RMSE.")
        return
    
    df_amplificacao['DataHora'] = pd.to_datetime(df_amplificacao['DataHora'])
    df_amplificacao = df_amplificacao[df_amplificacao['DataHora'].dt.year.isin(anos)]
    estacoes_lista = estacoes.split()
    df_amplificacao = df_amplificacao[df_amplificacao['Estacao'].isin(estacoes_lista)]
    
    if df_amplificacao.empty:
        print("Nenhum dado encontrado para os anos e estações especificados.")
        return
    
    total_pontos = len(df_amplificacao)
    pontos_rmse_alto = len(df_amplificacao[df_amplificacao['RMSE'] > 0.8])
    porcentagem_rmse_alto = (pontos_rmse_alto / total_pontos) * 100 if total_pontos > 0 else 0
    cmap = plt.get_cmap('tab10')
    cores = cmap(np.linspace(0, 1, len(estacoes_lista)))
    cor_estacao = {estacao: cores[i] for i, estacao in enumerate(estacoes_lista)}

    fig, ax1 = plt.subplots(figsize=(14, 8))
    for estacao in estacoes_lista:
        df_estacao = df_amplificacao[df_amplificacao['Estacao'] == estacao]
        if not df_estacao.empty:
            ax1.scatter(df_estacao['DataHora'], df_estacao['Amplificacao'], label=estacao, color=cor_estacao[estacao], s=50)
            df_high_rmse = df_estacao[df_estacao['RMSE'] > 0.8]
            if not df_high_rmse.empty:
                ax1.scatter(df_high_rmse['DataHora'], df_high_rmse['Amplificacao'], edgecolor='red', facecolor='none', s=100, linewidth=1.5)

    ax1.set_xlabel('Data')
    ax1.set_ylabel('Amplificação')
    ax1.set_title(f'Amplificação por Data para as Estações: {estacoes}\n{porcentagem_rmse_alto:.2f}% de pontos com RMSE > 0.8')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(title='Estação')

    ax2 = ax1.twinx()
    ax2.plot(filtered_data['Date'], filtered_data['SmoothedObsFlux'], label='Fluxo Solar F10.7 (Suavizado)', linewidth=2, color='orange')
    ax2.set_ylabel('F10.7 (sfu)')
    ax2.legend(loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

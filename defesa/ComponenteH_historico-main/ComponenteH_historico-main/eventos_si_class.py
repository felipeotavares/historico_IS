from typing import List
import pandas as pd
from datetime import datetime


class ParametrosRegressao:
    def __init__(
        self,
        r_squared: float,
        r_squared_d: float,
        residual: float,
        residual_d: float,
        rmse: float,
        rmse_d: float
    ):
        self.r_squared = r_squared
        self.r_squared_d = r_squared_d
        self.residual = residual
        self.residual_d = residual_d
        self.rmse = rmse
        self.rmse_d = rmse_d

    def __str__(self):
        return (
            f"Parâmetros de Regressão:\n"
            f"R²: {self.r_squared}, R² (D): {self.r_squared_d}\n"
            f"Residual: {self.residual}, Residual (D): {self.residual_d}\n"
            f"RMSE: {self.rmse}, RMSE (D): {self.rmse_d}"
        )

class Dados:
    def __init__(
        self, 
        dados: pd.DataFrame,
        ponto_direita: List[float], 
        ponto_direita_d: List[float], 
        ponto_esquerda: List[float], 
        ponto_esquerda_d: List[float], 
        qualidade: float, 
        regressao: ParametrosRegressao,
        amplitude: float = None, 
        amplitude_d: float = None, 
        amplificacao: float = None
    ):
        self.dados = dados
        self.ponto_direita = ponto_direita
        self.ponto_direita_d = ponto_direita_d
        self.ponto_esquerda = ponto_esquerda
        self.ponto_esquerda_d = ponto_esquerda_d
        self.qualidade = qualidade
        self.regressao = regressao
        self.amplitude = amplitude
        self.amplitude_d = amplitude_d
        self.amplificacao = amplificacao

    def __str__(self):
        return (
            f"Dados com qualidade {self.qualidade}\n"
            f"Amplitude: {self.amplitude}, Amplitude (D): {self.amplitude_d}, Amplificação: {self.amplificacao}\n"
            f"{self.regressao}"
        )


class EstacaoGeofisica:
    def __init__(
        self, 
        cidade: str, 
        conjugada: str, 
        dados: Dados, 
        datahora: datetime, 
        estacao: str, 
        fuso_horario: float, 
        hora: float, 
        latitude: float, 
        longitude: float
    ):
        self.cidade = cidade
        self.conjugada = conjugada
        self.dados = dados
        self.datahora = datahora
        self.estacao = estacao
        self.fuso_horario = fuso_horario
        self.hora = hora
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        # Exibindo uma representação personalizada com informações relevantes
        return (
            f"EstacaoGeofisica(estacao='{self.estacao}'"
            f"datahora='{self.datahora}'"
        )



#%%
# Exemplo de DataFrame de dados
df_dados = pd.DataFrame({
    'TIME': ['2024-11-12 00:00', '2024-11-12 00:01', '2024-11-12 00:02'],
    'H_nT': [50.1, 50.5, 50.8],
    'dH_nT': [0.1, 0.05, 0.07],
    'D_deg': [1.1, 1.2, 1.3]
})

# Criação do objeto ParametrosRegressao
parametros_regressao = ParametrosRegressao(
    r_squared=0.999,
    r_squared_d=0.998,
    residual=0.01,
    residual_d=0.02,
    rmse=0.03,
    rmse_d=0.04
)

# Criação do objeto Dados
dados_objeto = Dados(
    dados=df_dados,
    ponto_direita=[7.5, 54.0],
    ponto_direita_d=[4.6, -0.01],
    ponto_esquerda=[8.6, 2.1],
    ponto_esquerda_d=[8.7, -0.1],
    qualidade=1.0,
    regressao=parametros_regressao,
    amplitude=51.9,
    amplitude_d=0.1,
    amplificacao=1.03
)

# Criação do objeto EstacaoGeofisica
estacao_exemplo = EstacaoGeofisica(
    cidade="Ascension Island",
    conjugada="GUI",
    dados=dados_objeto,
    datahora=datetime(2024, 11, 12, 6, 16),
    estacao="ASC",
    fuso_horario=-1.0,
    hora=6.27,
    latitude=-8.0,
    longitude=-14.4
)

# Impressão do objeto EstacaoGeofisica
print(estacao_exemplo)


#%%
# Função para criar dados fictícios para uma estação
def criar_estacao(cidade, conjugada, estacao_nome, latitude, longitude):
    # Exemplo de DataFrame de dados para a estação
    df_dados = pd.DataFrame({
        'TIME': ['2024-11-12 00:00', '2024-11-12 00:01', '2024-11-12 00:02'],
        'H_nT': [50.1, 50.5, 50.8],
        'dH_nT': [0.1, 0.05, 0.07],
        'D_deg': [1.1, 1.2, 1.3]
    })
    
    # Parâmetros de regressão para a estação
    parametros_regressao = ParametrosRegressao(
        r_squared=0.999,
        r_squared_d=0.998,
        residual=0.01,
        residual_d=0.02,
        rmse=0.03,
        rmse_d=0.04
    )
    
    # Objeto Dados para a estação
    dados_objeto = Dados(
        dados=df_dados,
        ponto_direita=[7.5, 54.0],
        ponto_direita_d=[4.6, -0.01],
        ponto_esquerda=[8.6, 2.1],
        ponto_esquerda_d=[8.7, -0.1],
        qualidade=1.0,
        regressao=parametros_regressao,
        amplitude=51.9,
        amplitude_d=0.1,
        amplificacao=1.03
    )
    
    # Criação do objeto EstacaoGeofisica
    estacao = EstacaoGeofisica(
        cidade=cidade,
        conjugada=conjugada,
        dados=dados_objeto,
        datahora=datetime(2024, 11, 12, 6, 16),
        estacao=estacao_nome,
        fuso_horario=-1.0,
        hora=6.27,
        latitude=latitude,
        longitude=longitude
    )
    
    return estacao

# Criação de uma lista de estações
lista_estacoes = [
    criar_estacao("Ascension Island", "GUI", "ASC", -8.0, -14.4),
    criar_estacao("São Luís", "SJL", "SLZ", -2.5, -44.3),
    criar_estacao("Fortaleza", "FZA", "FOR", -3.7, -38.5),
    criar_estacao("Manaus", "MNS", "MAN", -3.1, -60.0),
    criar_estacao("Brasília", "BSA", "BSB", -15.8, -47.9)
]

# Imprimindo cada estação na lista
for estacao in lista_estacoes:
    print(estacao)
    print("-" * 40)
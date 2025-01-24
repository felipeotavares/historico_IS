#!/bin/bash

# Criação do ambiente Conda e instalação dos pacotes
conda create -n impulse_env python=3.9 -y

# Ativação do ambiente
source activate impulse_env

# Instalação de pacotes via conda
conda install pandas matplotlib numpy scipy seaborn beautifulsoup4 -y
conda install -c conda-forge pywt pyigrf mplcursors -y

# Instalação de pacotes via pip
pip install requests

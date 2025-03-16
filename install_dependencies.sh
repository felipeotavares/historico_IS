#!/bin/bash

# Lista das bibliotecas a serem instaladas
LIBRARIES=(
    "tkinter"
    "pickle-mixin"
    "matplotlib"
    "numpy"
    "pandas"
    "scipy"
    "mplcursors"
    "requests"
    "beautifulsoup4"
    "pyIGRF"
    "pywt"
    "seaborn"
)

# Instalar as bibliotecas com pip
echo "Instalando as bibliotecas necessárias..."

for LIB in "${LIBRARIES[@]}"; do
    echo "Instalando $LIB..."
    pip install $LIB
done

echo "Instalação concluída."

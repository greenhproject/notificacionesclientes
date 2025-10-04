#!/usr/bin/env bash
# Script de build para Render

set -o errexit

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorio para base de datos si no existe
mkdir -p data

echo "Build completado exitosamente"

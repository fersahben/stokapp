#!/usr/bin/env bash
# exit on error
set -o errexit

# Python sürümünü ayarla
pyenv install 3.8.0
pyenv global 3.8.0

pip install -r requirements.txt

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
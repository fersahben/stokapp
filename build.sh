#!/bin/bash

# pip'i güncelle
pip install --upgrade pip

# Numpy ve pandas'ı wheel paketleri ile kur
pip install numpy==1.21.6 --only-binary :all:
pip install pandas==1.3.5 --only-binary :all:

# Python paketlerini kur
pip install -r requirements.txt

# PATH'i ayarla
export PATH="/opt/render/project/src/.local/bin:$PATH"

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
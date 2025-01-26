#!/bin/bash

# pip'i güncelle
pip install --upgrade pip

# Önce numpy ve pandas'ı kur
pip install numpy==1.24.3 --only-binary :all:
pip install pandas==2.0.3 --only-binary :all:

# Diğer gereksinimleri kur
pip install -r requirements.txt

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
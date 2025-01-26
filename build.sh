#!/bin/bash

# pip'i güncelle
pip install --upgrade pip

# Sistem paketlerini kur
apt-get update && apt-get install -y python3-numpy python3-pandas

# Python paketlerini kur
pip install -r requirements.txt

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
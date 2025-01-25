#!/usr/bin/env bash
# exit on error
set -o errexit

# Python 3.8.0 kurulumu
curl -O https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
tar -xf Python-3.8.0.tgz
cd Python-3.8.0
./configure --enable-optimizations
make -j 8
sudo make altinstall
cd ..
rm -rf Python-3.8.0 Python-3.8.0.tgz

# Python sürümünü kontrol et
python3.8 --version

# pip'i güncelle
python3.8 -m pip install --upgrade pip

# Gereksinimleri yükle
python3.8 -m pip install -r requirements.txt

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
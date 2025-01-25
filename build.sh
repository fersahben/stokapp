#!/usr/bin/env bash
# exit on error
set -o errexit

# Python 3.8.0 kurulumu
curl -O https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
tar -xf Python-3.8.0.tgz
cd Python-3.8.0
./configure --prefix=$HOME/.local
make -j 8
make install
cd ..
rm -rf Python-3.8.0 Python-3.8.0.tgz

# PATH'e Python'u ekle
export PATH=$HOME/.local/bin:$PATH

# Python sürümünü kontrol et
$HOME/.local/bin/python3.8 --version

# pip'i güncelle
$HOME/.local/bin/python3.8 -m pip install --upgrade pip

# Gereksinimleri yükle
$HOME/.local/bin/python3.8 -m pip install -r requirements.txt

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
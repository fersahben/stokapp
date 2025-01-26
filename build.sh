#!/bin/bash

# Python 3.9'u kur
curl -O https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar -xf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations
make -j 8
make altinstall
cd ..
rm -rf Python-3.9.18 Python-3.9.18.tgz

# Virtualenv kur ve etkinleştir
python3.9 -m pip install virtualenv
python3.9 -m virtualenv venv
source venv/bin/activate

# pip'i güncelle
pip install --upgrade pip

# Numpy ve pandas'ı wheel paketleri ile kur
pip install numpy==1.21.6 --only-binary :all:
pip install pandas==1.3.5 --only-binary :all:

# Gunicorn'u doğrudan kur
pip install gunicorn==20.1.0

# Python paketlerini kur
pip install -r requirements.txt

# PATH'i ayarla
export PATH="/opt/render/project/src/venv/bin:$PATH"

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
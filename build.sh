#!/bin/bash

# Gerekli sistem paketlerini kur
apt-get update
apt-get install -y python3-opencv libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev zbar-tools

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

# Temel paketleri kur
pip install Flask==2.0.1
pip install Flask-SQLAlchemy==2.5.1
pip install Flask-Bootstrap==3.3.7.1
pip install Werkzeug==2.0.1

# Numpy ve pandas'ı wheel paketleri ile kur
pip install numpy==1.21.6 --only-binary :all:
pip install pandas==1.3.5 --only-binary :all:

# Diğer paketleri kur
pip install opencv-python-headless==4.5.3.56
pip install pyzbar==0.1.9
pip install python-barcode==0.14.0
pip install Pillow==8.3.2
pip install openpyxl==3.0.9
pip install et-xmlfile==1.1.0
pip install gunicorn==20.1.0

# PATH'i ayarla
export PATH="/opt/render/project/src/venv/bin:$PATH"

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
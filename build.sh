#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Gerekli dizinleri oluştur
mkdir -p static/uploads
mkdir -p static/temp 
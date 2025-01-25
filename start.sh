#!/usr/bin/env bash

# PATH'i ayarla
export PATH="/opt/render/.local/bin:$PATH"

# Gunicorn'u çalıştır
exec gunicorn app:app 
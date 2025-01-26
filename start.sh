#!/bin/bash
exec /opt/render/.local/bin/python3.8 -m gunicorn app:app --bind=0.0.0.0:$PORT 
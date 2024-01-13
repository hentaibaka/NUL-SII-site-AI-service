#!/bin/bash
source /var/www/NUL-SII-site-AI-service/venv/bin/activate
exec uvicorn main:app --host 127.0.0.1 --port 8001 --workers 5

import os
from fastapi.templating import Jinja2Templates
import logging
import uvicorn

# TEMPLATES

TEMPLATES = Jinja2Templates(directory='templates')

#ROOT DIRECTORY

ROOT = os.path.dirname(__file__)

#LOGGER CONFIG

logging.basicConfig(level=logging.INFO,
                    filename="ai-service.log", 
                    filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt='%m/%d/%Y %H:%M:%S')

#CORS CONFIG

CORS_ORIGINS = [
    "*",
    #"http://127.0.0.1",
]

#UVICORN CONFIG

HOST = '127.0.0.1'
PORT = 8001
WORKERS = os.cpu_count() + 1 #кол-во логических ядер процессора + 1


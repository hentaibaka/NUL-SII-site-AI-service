import os
from fastapi.templating import Jinja2Templates
import logging


TEMPLATES = Jinja2Templates(directory='templates')


ROOT = os.path.dirname(__file__)


logging.basicConfig(level=logging.INFO)


CORS_ORIGINS = [
    "*",
    #"http://127.0.0.1:8080",
]
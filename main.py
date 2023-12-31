from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src import PeerConnectionsManager, WebRTCApplication, Application 
import settings
#обязательно должно быть, инициализирует создание роутеров проектов
import projects


# FastAPI app
app = FastAPI(lifespan=PeerConnectionsManager.lifespan)

app.mount('/webrtc', WebRTCApplication.include_routers())
app.mount('/photo', Application.include_routers())

app.mount('/static', StaticFiles(directory='static'), name='static')

# CORS


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app)
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

app.mount('/api/ai/webrtc', WebRTCApplication.include_routers())
app.mount('/api/ai/photo', Application.include_routers())

app.mount('/ai/static', StaticFiles(directory='static'), name='static')

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=["*"],
)


if __name__ == "__main__":
    config = uvicorn.Config("main:app", 
                            host=settings.HOST, 
                            port=settings.PORT,
                            workers=settings.WORKERS,  
                            log_level="error")
    server = uvicorn.Server(config)
    server.run()
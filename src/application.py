from fastapi import FastAPI, APIRouter
import uvicorn

from .peer_connections_manager import PeerConnectionsManager


class Application():
    app = FastAPI(root_path_in_servers=False)
    routers: list[APIRouter] = []

    @classmethod
    def include_routers(cls) -> FastAPI:
        for router in cls.routers:
            cls.app.include_router(router)
        return cls.app

class WebRTCApplication(Application):
    app = FastAPI(root_path_in_servers=False)
    routers: list[APIRouter] = []
    conn_manager = PeerConnectionsManager

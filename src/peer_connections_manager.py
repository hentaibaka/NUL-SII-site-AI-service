import asyncio
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from aiortc import RTCPeerConnection

class PeerConnectionsManager():
    logger = logging.getLogger('pc manager')
    _pcs: set[RTCPeerConnection] | None = None

    @classmethod
    @property
    def pcs(cls) -> set[RTCPeerConnection] | None:
        return cls._pcs
    
    @classmethod
    def add(cls, pc: RTCPeerConnection) -> None:
        cls._pcs.add(pc)
        cls.logger.info(f"added pc, total: {len(cls.pcs)}")
        

    @classmethod
    def discard(cls, pc: RTCPeerConnection) -> None:
        cls._pcs.discard(pc)
        cls.logger.info(f"discarded pc, total: {len(cls.pcs)}")

    @classmethod
    @asynccontextmanager
    async def lifespan(cls, app: FastAPI):
        # on app starting up
        cls._pcs = set()
        
        yield

        # on app shutting down
        coros = [pc.close for pc in cls._pcs]
        await asyncio.gather(*coros)
        cls._pcs.clear()

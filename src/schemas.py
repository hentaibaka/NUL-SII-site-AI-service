from pydantic import BaseModel


class Offer(BaseModel):
    pass

class OfferRTC(BaseModel):
    sdp: str
    type: str

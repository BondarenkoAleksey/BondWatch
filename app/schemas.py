from pydantic import BaseModel
from typing import Optional

class BondCreate(BaseModel):
    isin: str
    name: str
    yield_percent: float

class BondUpdate(BaseModel):
    name: Optional[str] = None
    yield_percent: Optional[float] = None

class BondRead(BaseModel):
    isin: str
    name: str
    yield_percent: float

    model_config = {"from_attributes": True}

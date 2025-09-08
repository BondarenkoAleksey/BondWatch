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

from pydantic import BaseModel
from typing import Optional

class MoexBond(BaseModel):
    isin: str
    secid: str
    shortname: str
    matdate: Optional[str]      # дата погашения
    facevalue: Optional[float]  # текущий номинал
    initial_facevalue: Optional[float]  # изначальный номинал
    coupon_percent: Optional[float]     # ставка купона (% годовых)
    coupon_value: Optional[float]       # сумма купона
    coupon_date: Optional[str]          # дата ближайшего купона

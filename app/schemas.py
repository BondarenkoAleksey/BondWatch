from datetime import date
from pydantic import BaseModel
from typing import List, Optional


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


class MoexBond(BaseModel):
    isin: str
    secid: str
    shortname: str
    matdate: Optional[date]
    facevalue: Optional[float]
    initial_facevalue: Optional[float]
    coupon_percent: Optional[float]
    coupon_value: Optional[float]
    coupon_date: Optional[date]


class Coupon(BaseModel):
    value: Optional[float] = None
    valueprc: Optional[float] = None
    bond_id: int

    class Config:
        from_attributes = True
        fields = {'value': 'COUPONVALUE',
                  'valueprc': 'COUPONPERCENT'}


class BondWithCoupons(MoexBond):
    coupons: List[Coupon] = []

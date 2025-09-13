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
    has_offer: Optional[bool] = False
    offer_date: Optional[date] = None

    model_config = {"from_attributes": True}


class BondWithOffer(BondRead):
    has_offer: bool = False
    offer_date: Optional[date] = None


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
    has_offer: Optional[bool] = False
    offer_date: Optional[date] = None


class Coupon(BaseModel):
    value: Optional[float] = None
    valueprc: Optional[float] = None
    coupon_date: Optional[date] = None
    bond_id: int
    currency: Optional[str] = None

    model_config = {"from_attributes": True}


class BondWithCoupons(MoexBond):
    coupons: List[Coupon] = []

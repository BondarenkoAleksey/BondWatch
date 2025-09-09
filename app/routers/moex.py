from fastapi import APIRouter, HTTPException
from app.schemas import MoexBond
from app.services.moex_client import get_bond_info

router = APIRouter(prefix="/moex", tags=["MOEX"])

@router.get("/bonds/{isin}", response_model=MoexBond)
async def get_moex_bond(isin: str):
    """
    Fetch bond information from MOEX by ISIN.

    Returns basic bond fields:
    - isin
    - secid
    - shortname
    - matdate
    - facevalue
    - initial_facevalue
    - coupon_percent
    - coupon_value
    - coupon_date

    If bond is not found on MOEX, returns 404 Not Found.
    """
    data = await get_bond_info(isin)
    if not data:
        raise HTTPException(status_code=404, detail="Bond not found on MOEX")

    return MoexBond(
        isin=data.get("ISIN"),
        secid=data.get("SECID"),
        shortname=data.get("SHORTNAME"),
        matdate=data.get("MATDATE"),
        facevalue=data.get("FACEVALUE"),
        initial_facevalue=data.get("INITIALFACEVALUE"),
        coupon_percent=data.get("COUPONPERCENT"),
        coupon_value=data.get("COUPONVALUE"),
        coupon_date=data.get("COUPONDATE"),
    )

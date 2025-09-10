from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.routers.bonds import upsert_bond, get_db
from app.schemas import MoexBond
from app.services.moex_client import get_bond_info

router = APIRouter(prefix="/moex", tags=["MOEX"])

@router.get("/bonds/{isin}", response_model=MoexBond)
async def get_moex_bond(isin: str):
    """
    Fetch bond information from MOEX by ISIN.
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

@router.post("/bonds/{isin}/sync")
async def sync_moex_bond(isin: str, db: Session = Depends(get_db)):
    data = await get_bond_info(isin)
    print("DEBUG MOEX RESPONSE:", data)

    if not data:
        raise HTTPException(status_code=404, detail="Bond not found")

    bond_schema = MoexBond(
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

    db_bond = upsert_bond(db, bond_schema)
    return db_bond

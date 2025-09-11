from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import crud
from app.crud import create_coupons, upsert_bond
from app.models import CouponSchedule, Bond
from app.routers.bonds import get_db
from app.schemas import MoexBond, Coupon
from app.services.moex_client import get_bond_info, get_coupon_schedule

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


@router.post("/bonds/{isin}/sync")
async def sync_moex_bond(isin: str, db: Session = Depends(get_db)):
    """
    Sync bond and coupon schedule from MOEX into local database.
    """
    data = await get_bond_info(isin)
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

    # Insert or update bond
    db_bond = upsert_bond(db, bond_schema)

    # Insert coupon schedule
    coupon_list = await get_coupon_schedule(isin, db_bond.id)
    create_coupons(db, [
        CouponSchedule(
            bond_id=c.bond_id,
            coupon_date=c.coupon_date,
            value=c.value,
            valueprc=c.valueprc
        ) for c in coupon_list
    ])

    return db_bond


@router.get("/bonds/{isin}/coupons", response_model=List[Coupon])
async def get_bond_coupons(isin: str, db: Session = Depends(get_db)):
    """
    Get coupons for a bond by ISIN from the local database.
    """
    db_bond = crud.get_bond(db, isin)
    if not db_bond:
        raise HTTPException(status_code=404, detail="Bond not found")

    coupons = db.query(CouponSchedule).filter(CouponSchedule.bond_id == db_bond.id).all()
    if not coupons:
        raise HTTPException(status_code=404, detail="Coupons not found")

    return [Coupon.from_orm(c) for c in coupons]

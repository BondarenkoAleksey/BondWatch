from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import crud
from app.crud import upsert_bond
from app.models import CouponSchedule, Bond
from app.routers.bonds import get_db
from app.schemas import MoexBond, Coupon, BondWithCoupons
from app.services.moex_client import get_bond_info, get_coupon_schedule

router = APIRouter(prefix="/moex", tags=["MOEX"])


@router.get("/bonds/{isin}", response_model=MoexBond)
async def get_moex_bond(isin: str):

    """
    Получение инфо об облигации из MOEX по ISIN.

    Возвращаются следующие поля:
    - isin
    - secid
    - shortname
    - matdate
    - facevalue
    - initial_facevalue
    - coupon_percent
    - coupon_value
    - coupon_date

    Возвращает 404 при отсутствии облигации в MOEX.
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


@router.post("/bonds/{isin}/sync", response_model=BondWithCoupons)
async def sync_moex_bond(isin: str, db: Session = Depends(get_db)):
    """
    Синхронизация облигаций и купонов из MOEX в БД.
    """
    data = await get_bond_info(isin)
    if not data:
        raise HTTPException(status_code=404, detail="Bond not found")

    # Сохраняем облигацию
    buyback_raw = data.get("BUYBACKDATE")
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
        has_offer=bool(buyback_raw),
        offer_date=buyback_raw
    )
    db_bond = upsert_bond(db, bond_schema)

    # Получаем купоны из MOEX
    coupon_list = await get_coupon_schedule(isin, db_bond.id)

    # Обновляем/добавляем купоны в базе
    crud.upsert_coupons(db, coupon_list)

    db.commit()
    db.refresh(db_bond)  # Важно: подгружаем отношения

    # Формируем Pydantic объект с купонами
    bond_with_coupons = BondWithCoupons(
        **db_bond.__dict__,
        coupons=db_bond.coupons
    )

    return bond_with_coupons


@router.get("/bonds/{isin}/coupons", response_model=List[Coupon])
async def get_bond_coupons(isin: str, db: Session = Depends(get_db)):
    """
    Получение купонов из БД.
    """
    db_bond = crud.get_bond(db, isin)
    if not db_bond:
        raise HTTPException(status_code=404, detail="Bond not found")

    coupons = db.query(CouponSchedule).filter(CouponSchedule.bond_id == db_bond.id).all()
    if not coupons:
        raise HTTPException(status_code=404, detail="Coupons not found")

    return [Coupon.from_orm(c) for c in coupons]

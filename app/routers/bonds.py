from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import and_, or_, extract
from sqlalchemy.orm import Session, joinedload
from app import crud, schemas
from app.database import SessionLocal
from app.models import Bond, CouponSchedule
from app.schemas import BondWithCoupons


router = APIRouter(prefix="/bonds", tags=["bonds"])

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.BondRead)
def create_bond(bond: schemas.BondCreate=Body(
        ...,
        example={
            "isin": "RU000A107RZ0",
            "shortname": "СамолетP13",
            "yield_percent": 14.75
        }
    ), db: Session = Depends(get_db)):
    if crud.get_bond(db, bond.isin):
        raise HTTPException(status_code=400, detail="Bond already exists")
    return crud.create_bond(db, bond)


@router.get("/", response_model=list[schemas.BondRead])
def read_bonds(min_yield: float | None = None, max_yield: float | None = None, db: Session = Depends(get_db)):
    if min_yield is not None or max_yield is not None:
        return crud.search_bonds(db, min_yield, max_yield)
    return crud.get_bonds(db)


@router.get("/upcoming_coupons", response_model=list[BondWithCoupons])
def get_bonds_with_upcoming_coupons(db: Session = Depends(get_db)):
    today = date.today()

    # фильтрация по месяцам: текущий или следующий
    query = (
        db.query(Bond)
        .join(CouponSchedule)
        .options(joinedload(Bond.coupons))
        .filter(
            or_(
                and_(
                    extract("year", CouponSchedule.coupon_date) == today.year,
                    extract("month", CouponSchedule.coupon_date) == today.month,
                ),
                and_(
                    extract("year", CouponSchedule.coupon_date)
                    == (today.replace(day=1).month == 12 and today.year + 1 or today.year),
                    extract("month", CouponSchedule.coupon_date)
                    == (today.month % 12) + 1,
                ),
            )
        )
        .order_by(CouponSchedule.coupon_date.asc())
    )

    bonds = query.all()

    result = []
    seen = set()

    for bond in bonds:
        if bond.isin in seen:
            continue
        seen.add(bond.isin)

        # фильтруем только те купоны, что попадают в условие
        filtered_coupons = [
            c for c in bond.coupons
            if (c.coupon_date.year == today.year and c.coupon_date.month in {today.month, (today.month % 12) + 1})
        ]

        bond_data = {
            "isin": bond.isin,
            "secid": bond.secid,
            "shortname": bond.shortname,
            "matdate": bond.matdate,
            "facevalue": bond.facevalue,
            "initial_facevalue": bond.initial_facevalue,
            "coupon_percent": bond.coupon_percent,
            "coupon_value": bond.coupon_value,
            "coupon_date": bond.coupon_date,
            "yield_percent": bond.yield_percent,
            "has_offer": bond.has_offer,
            "offer_date": bond.offer_date,
            "coupons": filtered_coupons,
        }

        result.append(BondWithCoupons(**bond_data))

    return result


@router.get("/{isin}", response_model=schemas.BondRead)
def read_bond(isin: str, db: Session = Depends(get_db)):
    db_bond = crud.get_bond(db, isin)
    if not db_bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    return db_bond


@router.patch("/{isin}", response_model=schemas.BondRead)
def patch_bond(
    isin: str,
    bond_update: schemas.BondUpdate = Body(
        ...,
        example={
            "shortname": "СамолетP13",
            "yield_percent": 15.5,
            "has_offer": True,
            "offer_date": "2026-02-03"
        }
    ),
    db: Session = Depends(get_db)
):
    db_bond = crud.get_bond(db, isin)
    if not db_bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    return crud.update_bond(db, db_bond, bond_update)

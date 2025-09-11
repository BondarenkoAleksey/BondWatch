from sqlalchemy.orm import Session
from app import models, schemas
from app.models import CouponSchedule, Bond
from app.schemas import MoexBond


def get_bond(db: Session, isin: str):
    return db.query(models.Bond).filter(models.Bond.isin == isin).first()

def get_bonds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bond).offset(skip).limit(limit).all()

def create_bond(db: Session, bond: schemas.BondCreate):
    db_bond = models.Bond(isin=bond.isin, name=bond.name, yield_percent=bond.yield_percent)
    db.add(db_bond)
    db.commit()
    db.refresh(db_bond)
    return db_bond

def update_bond(db: Session, db_bond: models.Bond, bond_update: schemas.BondUpdate):
    update_data = bond_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bond, key, value)
    db.commit()
    db.refresh(db_bond)
    return db_bond

def search_bonds(db: Session, min_yield=None, max_yield=None):
    q = db.query(models.Bond)
    if min_yield is not None:
        q = q.filter(models.Bond.yield_percent >= min_yield)
    if max_yield is not None:
        q = q.filter(models.Bond.yield_percent <= max_yield)
    return q.all()

def upsert_bond(db: Session, bond_data: MoexBond) -> Bond:
    """
    Insert or update bond in the database by ISIN.
    """
    db_bond = db.query(Bond).filter(Bond.isin == bond_data.isin).first()
    if db_bond:
        # update existing
        for field, value in bond_data.dict().items():
            setattr(db_bond, field, value)
    else:
        # create new
        db_bond = Bond(**bond_data.dict())
        db.add(db_bond)

    db.commit()
    db.refresh(db_bond)
    return db_bond

def create_coupons(db: Session, coupons: list[CouponSchedule]):
    for c in coupons:
        db.add(c)
    db.commit()
    return coupons

from sqlalchemy.orm import Session
from app import models, schemas

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

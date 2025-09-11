from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import SessionLocal
from app.models import Bond
from app.schemas import MoexBond


router = APIRouter(prefix="/bonds", tags=["bonds"])

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.BondRead)
def create_bond(bond: schemas.BondCreate, db: Session = Depends(get_db)):
    if crud.get_bond(db, bond.isin):
        raise HTTPException(status_code=400, detail="Bond already exists")
    return crud.create_bond(db, bond)


@router.get("/", response_model=list[schemas.BondRead])
def read_bonds(min_yield: float | None = None, max_yield: float | None = None, db: Session = Depends(get_db)):
    if min_yield is not None or max_yield is not None:
        return crud.search_bonds(db, min_yield, max_yield)
    return crud.get_bonds(db)


@router.get("/{isin}", response_model=schemas.BondRead)
def read_bond(isin: str, db: Session = Depends(get_db)):
    db_bond = crud.get_bond(db, isin)
    if not db_bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    return db_bond


@router.patch("/{isin}", response_model=schemas.BondRead)
def patch_bond(isin: str, bond_update: schemas.BondUpdate, db: Session = Depends(get_db)):
    db_bond = crud.get_bond(db, isin)
    if not db_bond:
        raise HTTPException(status_code=404, detail="Bond not found")
    return crud.update_bond(db, db_bond, bond_update)

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

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="BondWatch API", version="0.1")

# Pydantic модель для облигации
class Bond(BaseModel):
    isin: str
    name: str
    yield_percent: float

class BondUpdate(BaseModel):
    name: Optional[str] = None
    yield_percent: Optional[float] = None

# Временное хранилище облигаций в памяти
bonds_db: List[Bond] = []

# Список всех облигаций
@app.get("/bonds", response_model=List[Bond])
async def get_bonds():
    return bonds_db

# Добавление новой облигации
@app.post("/bonds", response_model=Bond)
async def create_bond(bond: Bond):
    if any(b.isin == bond.isin for b in bonds_db):
        raise HTTPException(status_code=400, detail="Bond is already exists")
    bonds_db.append(bond)
    return bond


# Поиск облигаций по процентам
@app.get("/bonds/search", response_model=List[Bond])
async def search_bonds(min_yield: Optional[float] = None, max_yield: Optional[float] = None):
    results = bonds_db
    if min_yield is not None:
        results = [bond for bond in results if bond.yield_percent >= min_yield]
    if max_yield is not None:
        results = [bond for bond in results if bond.yield_percent <= max_yield]
    return results

# Получение облигации по isin
@app.get("/bonds/{isin}", response_model=Bond)
async def get_bond_by_isin(isin: str):
    for bond in bonds_db:
        if bond.isin == isin:
            return bond
    raise HTTPException(status_code=404, detail="Bond not found")

@app.patch("/bonds/{isin}", response_model=Bond)
async def update_bond(isin: str, bond_update: BondUpdate):
    for idx, bond in enumerate(bonds_db):
        if bond.isin == isin:
            updated_data = bond.model_dump()
            update_fields = bond_update.model_dump(exclude_unset=True)
            updated_data.update(update_fields)
            updated_bond = Bond(**updated_data)
            bonds_db[idx] = updated_bond
            return updated_bond
    raise HTTPException(status_code=404, detail="Bond not found")

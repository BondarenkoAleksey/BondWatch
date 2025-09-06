from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List


app = FastAPI(title="BondWatch API", version="0.1")

# Pydantic модель для облигации
class Bond(BaseModel):
    isin: str
    name: str
    yield_percent: float

# Временное хранилище облигаций в памяти
bonds_db: List[Bond] = []

# Список всех облигаций
@app.get("/bonds", response_model=List[Bond])
async def get_bonds():
    return bonds_db

# Добавление новой облигации
@app.post("/bonds", response_model=Bond)
async def create_bond(bond: Bond):
    bonds_db.append(bond)
    return bond

# Получение облигации по isin
@app.get("/bonds/{isin}", response_model=Bond)
async def get_bond_by_isin(isin: str):
    for bond in bonds_db:
        if bond.isin == isin:
            return bond
    raise HTTPException(status_code=404, detail="Bond not found")

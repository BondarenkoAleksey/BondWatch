from fastapi import FastAPI
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

# GET /bonds — список всех облигаций
@app.get("/bonds", response_model=List[Bond])
async def get_bonds():
    return bonds_db

# POST /bonds — добавление новой облигации
@app.post("/bonds", response_model=Bond)
async def create_bond(bond: Bond):
    bonds_db.append(bond)
    return bond

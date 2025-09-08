from fastapi import FastAPI
# from app.database import engine, Base
from app.routers import bonds, moex

app = FastAPI(title="BondWatch API", version="0.2")

app.include_router(bonds.router)
app.include_router(moex.router)

# Base.metadata.create_all(bind=engine)

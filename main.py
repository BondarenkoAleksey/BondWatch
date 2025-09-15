from fastapi import FastAPI
# from app.database import engine, Base
from app.routers import bonds, moex, tasks

app = FastAPI(title="BondWatch API", version="0.4")

app.include_router(bonds.router)
app.include_router(moex.router)
app.include_router(tasks.router)


# Base.metadata.create_all(bind=engine)

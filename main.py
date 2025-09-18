from fastapi import FastAPI

from app.core.logging_config import setup_logging
from app.routers import bonds, moex, tasks, portfolio

app = FastAPI(title="BondWatch API", version="0.7")

app.include_router(bonds.router)
app.include_router(moex.router)
app.include_router(tasks.router)
app.include_router(portfolio.router)

setup_logging()

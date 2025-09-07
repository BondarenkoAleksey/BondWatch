from sqlalchemy import Column, String, Float
from app.database import Base

class Bond(Base):
    __tablename__ = "bonds"

    isin = Column(String, primary_key=True, index=True)  # PK
    name = Column(String, nullable=False)
    yield_percent = Column(Float, nullable=False)

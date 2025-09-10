from sqlalchemy import Column, String, Float, Date
from app.database import Base

class Bond(Base):
    __tablename__ = "bonds"

    isin = Column(String, primary_key=True, index=True)
    secid = Column(String, index=True, nullable=True)
    shortname = Column(String, nullable=True)
    matdate = Column(Date, nullable=True)
    facevalue = Column(Float, nullable=True)
    initial_facevalue = Column(Float, nullable=True)
    coupon_percent = Column(Float, nullable=True)
    coupon_value = Column(Float, nullable=True)
    coupon_date = Column(Date, nullable=True)

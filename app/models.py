from sqlalchemy import Column, String, Float, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Bond(Base):
    __tablename__ = "bonds"

    id = Column(Integer, primary_key=True)
    isin = Column(String, unique=True, index=True)
    secid = Column(String, index=True)
    shortname = Column(String)
    matdate = Column(Date, nullable=True)
    facevalue = Column(Float, nullable=True)
    initial_facevalue = Column(Float, nullable=True)
    coupon_percent = Column(Float, nullable=True)
    coupon_value = Column(Float, nullable=True)
    coupon_date = Column(Date, nullable=True)

    coupons = relationship("CouponSchedule",
                           back_populates="bond",
                           cascade="all, delete-orphan")


class CouponSchedule(Base):
    __tablename__ = "coupon_schedule"

    id = Column(Integer, primary_key=True, index=True)
    bond_id = Column(Integer, ForeignKey("bonds.id", ondelete="CASCADE"))
    coupon_date = Column(Date, nullable=True)
    value = Column(Float, nullable=True)
    valueprc = Column(Float, nullable=True)

    bond = relationship("Bond", back_populates="coupons")

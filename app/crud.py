from typing import Iterable, List, Union

from sqlalchemy.orm import Session
from app import models, schemas
from app.models import CouponSchedule, Bond
from app.schemas import MoexBond


def get_bond(db: Session, isin: str):
    return db.query(models.Bond).filter(models.Bond.isin == isin).first()

def get_bonds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bond).offset(skip).limit(limit).all()

def create_bond(db: Session, bond: schemas.BondCreate):
    db_bond = models.Bond(isin=bond.isin, name=bond.name, yield_percent=bond.yield_percent)
    db.add(db_bond)
    db.commit()
    db.refresh(db_bond)
    return db_bond

def update_bond(db: Session, db_bond: models.Bond, bond_update: schemas.BondUpdate):
    update_data = bond_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bond, key, value)
    db.commit()
    db.refresh(db_bond)
    return db_bond

def search_bonds(db: Session, min_yield=None, max_yield=None):
    q = db.query(models.Bond)
    if min_yield is not None:
        q = q.filter(models.Bond.yield_percent >= min_yield)
    if max_yield is not None:
        q = q.filter(models.Bond.yield_percent <= max_yield)
    return q.all()

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

def upsert_coupons(db: Session, coupons: Iterable[Union[schemas.Coupon, dict]]) -> List[CouponSchedule]:
    """
    Вставляет или обновляет список купонов (bulk upsert-like, but implemented in Python).
    Принимает и Pydantic объекты (schemas.Coupon) и dict-подобные записи.
    Возвращает список ORM-объектов CouponSchedule (новых и обновлённых).
    """
    coupons = list(coupons)
    if not coupons:
        return []

    # Преобразуем вход в удобный список кортежей (bond_id, coupon_date, value, valueprc, currency, original)
    normalized = []
    for c in coupons:
        if isinstance(c, dict):
            bond_id = c.get("bond_id")
            coupon_date = c.get("coupon_date")
            value = c.get("value")
            valueprc = c.get("valueprc")
            currency = c.get("currency", None)
        else:
            # Pydantic model / ORM-like
            bond_id = getattr(c, "bond_id", None)
            coupon_date = getattr(c, "coupon_date", None)
            value = getattr(c, "value", None)
            valueprc = getattr(c, "valueprc", None)
            currency = getattr(c, "currency", None)

        # normalize date-like (if string -> try parse?) — ожидаем уже date или None
        normalized.append((bond_id, coupon_date, value, valueprc, currency, c))

    # Группируем по bond_id чтобы меньше запросов к БД
    from collections import defaultdict
    by_bond = defaultdict(list)
    for tup in normalized:
        bond_id = tup[0]
        by_bond[bond_id].append(tup)

    result: List[CouponSchedule] = []

    for bond_id, rows in by_bond.items():
        # Список дат, исключая None (sqlite/SQAlchemy .in_() не любит None в списке)
        non_null_dates = [r[1] for r in rows if r[1] is not None]

        # Получаем существующие купоны для bond_id и дат (если есть)
        existing = []
        if non_null_dates:
            existing = db.query(CouponSchedule).filter(
                CouponSchedule.bond_id == bond_id,
                CouponSchedule.coupon_date.in_(non_null_dates)
            ).all()
        # map key -> object
        existing_map = {(e.bond_id, e.coupon_date): e for e in existing}

        to_add: List[CouponSchedule] = []

        for bond_id, coupon_date, value, valueprc, currency, original in rows:
            key = (bond_id, coupon_date)
            if key in existing_map:
                # Обновляем существующий
                e = existing_map[key]
                e.value = value
                e.valueprc = valueprc
                # поддерживаем поле currency, если он есть в модели
                if hasattr(e, "currency") and currency is not None:
                    setattr(e, "currency", currency)
                result.append(e)
            else:
                # Создаём новый объект
                new = CouponSchedule(
                    bond_id=bond_id,
                    coupon_date=coupon_date,
                    value=value,
                    valueprc=valueprc
                )
                if hasattr(new, "currency") and currency is not None:
                    setattr(new, "currency", currency)
                to_add.append(new)
                result.append(new)

        if to_add:
            db.add_all(to_add)

    # В конце один коммит (атомарно для всех вставок/обновлений)
    db.commit()

    # Попытка обновить объекты (refresh) — безопасно пропускаем, если не удалось
    for obj in result:
        try:
            db.refresh(obj)
        except Exception:
            # Если объект новый и DB не возвращает поля сразу — ничего страшного
            pass

    return result

def create_coupons(db: Session, coupons: list[CouponSchedule]):
    for c in coupons:
        db.add(c)
    db.commit()
    return coupons

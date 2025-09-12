from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import HTTPException

from app.schemas import Coupon

BASE_URL = "https://iss.moex.com/iss"

async def get_bond_info(isin: str) -> Optional[dict]:
    url = f"https://iss.moex.com/iss/securities/{isin}.json"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None  # возвращаем None, чтобы роут вернул 404
        raise HTTPException(status_code=502, detail="MOEX API error") from e
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail="Network error") from e

    data = response.json()
    rows = data.get("description", {}).get("data", [])
    columns = data.get("description", {}).get("columns", [])
    if not rows:
        return None

    return {row[0]: row[2] for row in rows}


async def get_coupon_schedule(isin: str, bond_id: int) -> list[Coupon]:
    """
    Получаем купоны облигации с MOEX и возвращаем список Pydantic моделей Coupon.
    """
    import httpx

    url = f"https://iss.moex.com/iss/securities/{isin}/bondization.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    coupons_data = data.get("coupons", {}).get("data", [])
    coupons_columns = data.get("coupons", {}).get("columns", [])

    # Найдем индексы нужных полей
    idx_coupon_date = coupons_columns.index("coupondate")
    idx_value = coupons_columns.index("value")
    idx_valueprc = coupons_columns.index("valueprc")

    coupons = []
    for row in coupons_data:
        # Преобразуем дату из строки в datetime.date
        raw_date = row[idx_coupon_date]
        coupon_date = datetime.strptime(raw_date, "%Y-%m-%d").date() if raw_date else None

        coupons.append(
            Coupon(
                bond_id=bond_id,
                value=row[idx_value],
                valueprc=row[idx_valueprc],
                coupon_date=coupon_date
            )
        )

    return coupons

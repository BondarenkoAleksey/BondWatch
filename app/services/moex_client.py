from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import HTTPException

from app.schemas import Coupon

BASE_URL = "https://iss.moex.com/iss"

async def get_bond_info(isin: str) -> Optional[dict]:
    url = f"{BASE_URL}/securities/{isin}.json"

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
    bond_data = {row[0]: row[2] for row in rows}
    # print(bond_data)
    return bond_data


async def get_coupon_schedule(isin: str, bond_id: int) -> List[Coupon]:
    """
    Получаем купоны облигации с MOEX и возвращаем список Pydantic моделей Coupon.
    """
    url = f"{BASE_URL}/securities/{isin}/bondization.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    coupons_data = data.get("coupons", {}).get("data", [])
    coupons_columns = data.get("coupons", {}).get("columns", [])

    # приводим к нижнему регистру, чтобы не зависеть от регистра в API
    cols = [c.lower() for c in coupons_columns]
    idx = {c: i for i, c in enumerate(cols)}

    coupons = []
    for row in coupons_data:
        # coupon_date
        raw_date = row[idx["coupondate"]] if "coupondate" in idx else None
        coupon_date = datetime.strptime(raw_date, "%Y-%m-%d").date() if raw_date else None

        # value / valueprc
        value = row[idx["value"]] if "value" in idx else None
        valueprc = row[idx["valueprc"]] if "valueprc" in idx else None

        # currency: обычно в колонке faceunit
        currency = None
        if "faceunit" in idx:
            currency = row[idx["faceunit"]]
        elif "currency" in idx:
            currency = row[idx["currency"]]

        coupons.append(
            Coupon(
                bond_id=bond_id,
                value=value,
                valueprc=valueprc,
                coupon_date=coupon_date,
                currency=currency
            )
        )
    # print(coupons)
    return coupons

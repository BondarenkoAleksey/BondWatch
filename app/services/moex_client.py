import httpx
from typing import Dict, Optional
from fastapi import HTTPException

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

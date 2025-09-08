import httpx
from typing import Dict, Optional

BASE_URL = "https://iss.moex.com/iss"

async def get_bond_info(isin: str) -> Optional[dict]:
    url = f"https://iss.moex.com/iss/securities/{isin}.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return None
        data = response.json()
        columns = data["description"]["columns"]
        values = data["description"]["data"]
        info = {row[0]: row[2] for row in values}  # name → value
        return info

from fastapi import APIRouter
from app.t_investicii.portfolio import get_portfolio_info

router = APIRouter()


@router.get("/portfolio", tags=["portfolio"])
def portfolio():
    """Получение информации о портфеле в Т-инвестициях."""
    return get_portfolio_info()

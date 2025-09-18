import os
from tinkoff.invest import Client
from tinkoff.invest.constants import INVEST_GRPC_API

TINKOFF_TOKEN = os.getenv("TINKOFF_TOKEN")

def get_portfolio_info():
    if not TINKOFF_TOKEN:
        raise RuntimeError("Не найден TINKOFF_TOKEN в переменных окружениях")

    with Client(TINKOFF_TOKEN, target=INVEST_GRPC_API) as client:
        accounts = client.users.get_accounts()
        result = []

        for account in accounts.accounts:
            portfolio = client.operations.get_portfolio(account_id=account.id)
            positions = []

            for position in portfolio.positions:
                positions.append({
                    "figi": position.figi,
                    "quantity": float(position.quantity.units),
                })

            result.append({
                "account_id": account.id,
                "account_name": account.name,
                "positions": positions,
            })

        return result

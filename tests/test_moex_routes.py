from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import pytest
from fastapi import HTTPException

from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def no_external_requests(monkeypatch):
    """
    Safety fixture: по умолчанию предотвращаем реальные сетевые вызовы
    к app.services.moex_client.get_bond_info — в тестах мы будем мокать.
    """
    # если кто-то случайно попытается вызвать реальный клиент — заменим заглушкой,
    # которая возвращает None (поведение "не найдено").
    monkeypatch.setattr("app.routers.moex.get_bond_info", AsyncMock(return_value=None))
    yield


def test_get_moex_bond_success(monkeypatch):
    """
    Happy path: get_bond_info возвращает полный набор полей (как MOEX),
    роут должен вернуть 200 и корректно преобразовать поля в ответ.
    """
    fake_moex_response = {
        "ISIN": "RU000A10C8A4",
        "SECID": "RU000A10C8A4",
        "SHORTNAME": "ПолиплП2Б8",
        "MATDATE": "2027-01-22",
        "FACEVALUE": "100",
        "INITIALFACEVALUE": "100",
        "COUPONPERCENT": "13.95",
        "COUPONVALUE": "1.15",
        "COUPONDATE": "2025-09-29",
    }

    # Патчим функцию, которую реально вызывает роут (см. app/routers/moex.py)
    monkeypatch.setattr("app.routers.moex.get_bond_info", AsyncMock(return_value=fake_moex_response))

    resp = client.get("/moex/bonds/RU000A10C8A4")
    assert resp.status_code == 200

    body = resp.json()
    # Проверяем наличие основных полей и их типы/значения.
    assert body["isin"] == "RU000A10C8A4"
    assert body["secid"] == "RU000A10C8A4"
    assert body["shortname"] == "ПолиплП2Б8"
    assert body["matdate"] == "2027-01-22"
    # response_model может привести строки к числам — проверяем только to float/int via conversion
    assert float(body["facevalue"]) == 100.0
    assert float(body["initial_facevalue"]) == 100.0
    assert float(body["coupon_percent"]) == 13.95
    assert float(body["coupon_value"]) == 1.15
    assert body["coupon_date"] == "2025-09-29"


def test_get_moex_bond_not_found(monkeypatch):
    """
    Если клиент вернул None (MOEX не нашёл ISIN), роут должен вернуть 404.
    """
    monkeypatch.setattr("app.routers.moex.get_bond_info", AsyncMock(return_value=None))

    resp = client.get("/moex/bonds/UNKNOWN_ISIN")
    assert resp.status_code == 404
    assert resp.json().get("detail") is not None


def test_get_moex_bond_partial_data(monkeypatch):
    """
    Клиент вернул только пару полей (ISIN и SECID). Остальные — отсутствуют.
    Роут должен вернуть объект, где отсутствующие поля — null.
    """
    partial = {
        "ISIN": "RU000XXXXX",
        "SECID": "RU000XXXXX",
        # остальное отсутствует
    }
    monkeypatch.setattr("app.routers.moex.get_bond_info", AsyncMock(return_value=partial))

    resp = client.get("/moex/bonds/RU000XXXXX")
    assert resp.status_code == 200
    body = resp.json()
    assert body["isin"] == "RU000XXXXX"
    assert body["secid"] == "RU000XXXXX"
    # поля, которые опциональны — должны быть null в JSON
    assert body.get("shortname") is None
    assert body.get("coupon_percent") is None
    assert body.get("facevalue") is None


def test_get_moex_bond_moex_error(monkeypatch):
    """
    Если клиент поднял HTTPException(502) — роут должен вернуть 502.
    """
    async def raiser(isin: str):
        raise HTTPException(status_code=502, detail="MOEX API error")

    monkeypatch.setattr("app.routers.moex.get_bond_info", AsyncMock(side_effect=raiser))

    resp = client.get("/moex/bonds/RU000A10C8A4")
    assert resp.status_code == 502
    assert "MOEX" in resp.json().get("detail", "")

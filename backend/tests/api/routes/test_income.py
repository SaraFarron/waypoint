import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.income import create_random_income


def test_create_income(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Salary", "category": "Work", "amount": 4200.0}
    response = client.post(
        f"{settings.API_V1_STR}/income/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["category"] == data["category"]
    assert content["amount"] == data["amount"]
    assert "id" in content
    assert "owner_id" in content


def test_read_income(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    income = create_random_income(db)
    response = client.get(
        f"{settings.API_V1_STR}/income/{income.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == income.title
    assert content["category"] == income.category
    assert content["amount"] == income.amount
    assert content["id"] == str(income.id)
    assert content["owner_id"] == str(income.owner_id)


def test_read_income_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/income/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Income not found"


def test_read_income_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    income = create_random_income(db)
    response = client.get(
        f"{settings.API_V1_STR}/income/{income.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_incomes(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_income(db)
    create_random_income(db)
    response = client.get(
        f"{settings.API_V1_STR}/income/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2


def test_update_income(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    income = create_random_income(db)
    data = {"title": "Updated title", "category": "Updated category", "amount": 99.99}
    response = client.put(
        f"{settings.API_V1_STR}/income/{income.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["category"] == data["category"]
    assert content["amount"] == data["amount"]
    assert content["id"] == str(income.id)
    assert content["owner_id"] == str(income.owner_id)


def test_update_income_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "category": "Updated category", "amount": 99.99}
    response = client.put(
        f"{settings.API_V1_STR}/income/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Income not found"


def test_update_income_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    income = create_random_income(db)
    data = {"title": "Updated title", "category": "Updated category", "amount": 99.99}
    response = client.put(
        f"{settings.API_V1_STR}/income/{income.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"

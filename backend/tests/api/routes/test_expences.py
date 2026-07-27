import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.expence import create_random_expence


def test_create_expence(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Groceries", "category": "Food", "amount": 42.5}
    response = client.post(
        f"{settings.API_V1_STR}/expences/",
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


def test_read_expence(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    expence = create_random_expence(db)
    response = client.get(
        f"{settings.API_V1_STR}/expences/{expence.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == expence.title
    assert content["category"] == expence.category
    assert content["amount"] == expence.amount
    assert content["id"] == str(expence.id)
    assert content["owner_id"] == str(expence.owner_id)


def test_read_expence_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/expences/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Expence not found"


def test_read_expence_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    expence = create_random_expence(db)
    response = client.get(
        f"{settings.API_V1_STR}/expences/{expence.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_expences(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_expence(db)
    create_random_expence(db)
    response = client.get(
        f"{settings.API_V1_STR}/expences/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2


def test_update_expence(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    expence = create_random_expence(db)
    data = {"title": "Updated title", "category": "Updated category", "amount": 99.99}
    response = client.put(
        f"{settings.API_V1_STR}/expences/{expence.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["category"] == data["category"]
    assert content["amount"] == data["amount"]
    assert content["id"] == str(expence.id)
    assert content["owner_id"] == str(expence.owner_id)


def test_update_expence_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "category": "Updated category", "amount": 99.99}
    response = client.put(
        f"{settings.API_V1_STR}/expences/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Expence not found"


def test_update_expence_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    expence = create_random_expence(db)
    data = {"title": "Updated title", "category": "Updated category", "amount": 99.99}
    response = client.put(
        f"{settings.API_V1_STR}/expences/{expence.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"

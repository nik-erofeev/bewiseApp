from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from app.api.application.schemas import ApplicationRespSchema
from app.models import Application


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_name, description, expected_status",
    [
        ("User", "TDescription", 201),
        (1, "TDescription", 422),
        ("User", 1, 422),
    ],
)
async def test_add_application(
    client,
    mock_db_session,
    mock_kafka,
    user_name: str,
    description: str,
    expected_status: int,
):
    CREATED_AT = datetime.now()

    # Устанавливаем side_effect для REFRESH(id и created_at)
    def set_attributes(application):
        application.id = 1
        application.created_at = CREATED_AT

    mock_db_session.refresh.side_effect = set_attributes

    new_application = {"user_name": user_name, "description": description}
    response = await client.post("/v1/applications/", json=new_application)

    assert response.status_code == expected_status
    data = response.json()

    if expected_status == 201:
        assert data["user_name"] == user_name.lower()
        assert data["description"] == description
        assert data["created_at"] == CREATED_AT.isoformat()

        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called()

        mock_kafka.send_message.assert_called()


@pytest.mark.asyncio
async def test_add_application_duplicate_user(client, mock_db_session, mock_kafka):
    # Устанавливаем side_effect для flush, чтобы вызывать IntegrityError(дубль юзера)
    mock_db_session.flush.side_effect = IntegrityError("Duplicate entry", params=None, orig=None)

    new_application = {"user_name": "User", "description": "TDescription"}
    response = await client.post("/v1/applications/", json=new_application)

    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}


cached_data = {
    "user_name": "user_name",
    "description": "Description for the application",
    "created_at": "2025-01-19T17:40:37.875819",
}


mock_data_user_in_db = Application(
    created_at=datetime(2025, 1, 19, 17, 40, 37, 875819),
    description="Description in DB",
    id=10,
    user_name="user_db",
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "application_id, expected_status, data_redis, data_db",
    [
        (999, 404, None, None),  # нет нигде
        (2, 200, cached_data, None),  # в редисе +
        (10, 200, None, mock_data_user_in_db),  # редис-, db +
    ],
)
async def test_get_application(
    client: AsyncClient,
    mock_db_session,
    mock_redis,
    application_id: int,
    expected_status: int,
    data_redis: dict,
    data_db,
):
    mock_redis.cached_application.return_value = data_redis

    with patch("app.api.application.dao.ApplicationDAO.find_one_or_none_by_id", return_value=None) as mock_find:
        mock_find.return_value = data_db

        response = await client.get(f"/v1/applications/{application_id}")

        # Проверяем, что Redis вызваны
        mock_redis.cached_application.assert_called_with(application_id)

        status = response.status_code
        assert status == expected_status

        if status == 404:
            assert response.json() == {"detail": f"Заявка {application_id} не найдена"}

            mock_redis.set_application_cache.assert_not_called()  # сет не вызван

        elif status == 200:
            result = response.json()
            assert result["id"] == application_id

            if not data_db:  # в кеше
                assert result["user_name"] == cached_data["user_name"]
                assert result["description"] == cached_data["description"]
                assert result["created_at"] == cached_data["created_at"]

                mock_redis.set_application_cache.assert_not_called()  # сет не вызван

            else:  # бзе кеша НО в БД
                assert result["user_name"] == data_db.user_name.lower()
                assert result["description"] == data_db.description
                assert result["created_at"] == data_db.created_at.isoformat()

                # сет вызван
                mock_redis.set_application_cache.assert_called()

                # с правильными аргументами
                mock_redis.set_application_cache.assert_called_with(
                    application_id,
                    ApplicationRespSchema.model_validate(data_db).model_dump(),
                )

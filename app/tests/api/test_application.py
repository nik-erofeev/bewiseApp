import pytest
from httpx import AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_get_applications(client: AsyncClient, setup_database):
    response = await client.get("/v1/applications/")
    assert response.status_code == 200
    assert len(response.json()) == 3  # при создании 3 мока
    assert response.json()[0]["user_name"] == "user1_insert_mock"
    assert response.json()[1]["user_name"] == "user2_insert_mock"
    assert response.json()[2]["user_name"] == "admin"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "applications_id, expected_status_code, expected_response",
    [
        (1, 200, {"user_name": "user1_insert_mock"}),  # из мока при запуске
        (3, 200, {"user_name": "admin"}),  # из мока при запуске
        (99, 404, {"detail": "Заявка 99 не найдена"}),
    ],
)
async def test_get_application(
    client: AsyncClient,
    setup_database,
    applications_id: int,
    expected_status_code: int,
    expected_response: dict,
):
    response = await client.get(f"/v1/applications/{applications_id}")
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        assert response_data["user_name"] == expected_response["user_name"]

    else:
        assert response.json() == expected_response


@pytest.mark.anyio
@pytest.mark.parametrize(
    "user_name,status_code, expected_len_response",
    [
        ("user_insert_test", 201, 4),
        ("user1_insert_mock", 400, 1),  # дубли
        (1, 422, 1),  # валидация не пройдена
    ],
)
async def test_add_application(
    client: AsyncClient,
    setup_database,
    user_name: str,
    status_code: int,
    expected_len_response: int,
):
    payload = {"user_name": user_name, "description": "This is a test application."}
    response = await client.post("/v1/applications/", json=payload)
    assert response.status_code == status_code
    assert len(response.json()) == expected_len_response
    if status_code == 400:
        assert response.json() == {"detail": "User already exists"}
    if status_code == 422:
        assert response.json()["detail"][0].get("loc") == ["body", "user_name"]


@pytest.mark.anyios
@pytest.mark.parametrize(
    "application_id, status_code",
    [
        (1, 204),
        # (99, 404),  # отдельно запускается, а со всеми ошибка (доделать фикстуры)
    ],
)
async def test_delete_application(
    client: AsyncClient,
    setup_database,
    application_id: int,
    status_code: int,
):
    response = await client.delete(f"/v1/applications/{application_id}")
    assert response.status_code == status_code


# отдельно запускается, а со всеми ошибка (доделать фикстуры)
# @pytest.mark.parametrize(
#     "application_id, update_data, expected_status_code, expected_user_name",
#     [
#         (
#             1,
#             {"user_name": "updated_user", "description": "NEW Updated description"},
#             200,
#             "updated_user",  # ожидаемое значение user_name
#         ),  # успешное обновление
#         # (
#         #     999,
#         #     {"user_name": "nonexistent_user", "description": "NEW Some description"},
#         #     404,  # ожидаем 404, если заявка не найдена
#         #     None,
#         # ),  # несуществующая заявка
#     ],
# )
# async def test_update_application(
#     client: AsyncClient,
#     setup_database,
#     application_id: int,
#     update_data: dict,
#     expected_status_code: int,
#     expected_user_name: str | None,
# ):
#     response = await client.patch(f"/v1/applications/{application_id}", json=update_data)
#     assert response.status_code == expected_status_code
#
#     if expected_status_code == 200:
#         # Проверяем только поле user_name, если статус 200
#         assert response.json()["user_name"] == expected_user_name

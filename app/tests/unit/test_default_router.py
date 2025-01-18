import pytest


@pytest.mark.asyncio
async def test_ready(client, mock_db_session):
    response = await client.get("/v1/check_database")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Database is ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url, expected_status, expected_data",
    [
        ("/v1/ping", 200, {"message": "pong"}),
        ("/v1/pin1", 404, {"detail": "Not Found"}),
    ],
    # ids=['success', 'url not_found'],
)
async def test_ping(client, url, expected_status, expected_data):
    response = await client.get(url)
    assert response.status_code == expected_status
    data = response.json()
    assert data == expected_data

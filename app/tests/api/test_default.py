import pytest


@pytest.mark.parametrize(
    "url, status, expected_response",
    [
        ("ping", 200, {"message": "pong"}),
        ("pping", 404, {"detail": "Not Found"}),
    ],
)
async def test_ping(client, url: str, status: int, expected_response: dict):
    response = client.get(f"/v1/{url}")
    assert response.status_code == status
    assert response.json() == expected_response


async def test_ready_db(client):
    response = client.get("/v1/check_database")
    assert response.status_code == 200
    assert response.json() == {"status": "Database is ready"}

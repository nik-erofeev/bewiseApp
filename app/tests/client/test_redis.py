import pytest

from app.redis.redis_client import RedisKeys


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "application_id, expected_data",
    [
        (1, {"name": "Test Application"}),
        (2, None),
    ],
)
async def test_cached_application(redis_client, application_id, expected_data):
    redis_client.get_cache.return_value = expected_data

    result = await redis_client.cached_application(application_id)

    assert result == expected_data
    redis_client.get_cache.assert_called_once_with(RedisKeys.APPLICATION, str(application_id))


@pytest.mark.asyncio
async def test_set_application_cache(redis_client):
    application_id = 3
    application_data = {"name": "New Application", "description": "A new app"}

    await redis_client.set_application_cache(application_id, application_data)

    redis_client.set_cache.assert_called_once_with(
        RedisKeys.APPLICATION,
        str(application_id),
        application_data,
        expire=86400,  # ExpireTime.DAY.value
    )


@pytest.mark.asyncio
async def test_update_application_cache(redis_client):
    application_id = 4
    existing_data = {"name": "Old Application"}
    new_data = {"description": "Updated description"}

    # Настраиваем поведение мока
    redis_client.get_cache.return_value = existing_data

    await redis_client.update_application_cache(application_id, new_data)

    redis_client.set_cache.assert_called_once_with(
        RedisKeys.APPLICATION,
        str(application_id),
        {"name": "Old Application", "description": "Updated description"},
        expire=None,
    )


@pytest.mark.asyncio
async def test_delete_application_cache(redis_client):
    application_id = 5

    await redis_client.delete_application_cache(application_id)

    redis_client.del_cache.assert_called_once_with(RedisKeys.APPLICATION, str(application_id))

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.application.schemas import ApplicationCreateSchema, ApplicationRespSchema


@pytest.mark.parametrize(
    "user_name, description, expected_user_name",
    [
        ("JohnDoe", "This is a test application", "johndoe"),
        ("JaneDoe", "Another test application", "janedoe"),
        ("USER_NAME", "Description with uppercase", "user_name"),
        ("", "Empty username", ""),
    ],
)
def test_application_schema(user_name, description, expected_user_name):
    app_schema = ApplicationCreateSchema(user_name=user_name, description=description)

    assert app_schema.user_name == expected_user_name
    assert app_schema.description == description


def test_application_schema_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        ApplicationCreateSchema(user_name="ThisUserNameIsWayTooLong", description="Test")

    assert "user_name" in str(exc_info.value)
    assert "String should have at most 20 characters" in str(exc_info.value)


def test_application_resp_schema():
    created_at = datetime.now()
    app_resp_schema = ApplicationRespSchema(user_name="testuser", description="Test", id=1, created_at=created_at)

    assert app_resp_schema.id == 1
    assert app_resp_schema.user_name == "testuser"
    assert app_resp_schema.created_at == created_at

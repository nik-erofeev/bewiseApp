import pytest

from app.api.application.utils import ActionType, create_message


@pytest.mark.parametrize(
    "action, application_id, new_data, update_data, expected_message",
    [
        (
            ActionType.CREATE_APPLICATION,
            1,
            {"name": "Test Application", "description": "Test Description"},
            None,
            {
                "action": ActionType.CREATE_APPLICATION.value,
                "application_id": 1,
                "new_application": {"name": "Test Application", "description": "Test Description"},
            },
        ),
        (
            ActionType.UPDATE_APPLICATION,
            1,
            None,
            {"name": "Updated Application", "description": "Updated Description"},
            {
                "action": ActionType.UPDATE_APPLICATION.value,
                "application_id": 1,
                "update_application": {"name": "Updated Application", "description": "Updated Description"},
            },
        ),
        (
            ActionType.DELETE_APPLICATION,
            1,
            None,
            None,
            {
                "action": ActionType.DELETE_APPLICATION.value,
                "application_id": 1,
            },
        ),
    ],
)
def test_create_message(action, application_id, new_data, update_data, expected_message):
    assert create_message(action, application_id, new_data, update_data) == expected_message

from enum import Enum
from typing import Any

description = {
    "user_name": "user",
    "description": "Description for the application",
}


class ActionType(str, Enum):
    CREATE_APPLICATION = "create_application"
    UPDATE_APPLICATION = "update_application"
    DELETE_APPLICATION = "delete_application"


def create_message(
    action: ActionType,
    application_id: int | None = None,
    new_data: dict | None = None,
    update_data: dict | None = None,
) -> dict[str, Any]:
    message = {
        "action": action.value,
        "application_id": application_id,
        "new_application": new_data,
        "update_application": update_data,
    }
    # Удаляем ключи с значениями None
    return {k: v for k, v in message.items() if v is not None}

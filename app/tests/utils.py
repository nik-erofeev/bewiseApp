import json
import os

TEST_BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def open_mock_json(model: str):
    with open(os.path.join(TEST_BASE_PATH, f"mock_{model}.json")) as f:
        return json.load(f)

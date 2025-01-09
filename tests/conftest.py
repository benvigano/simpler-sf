import json
import os
import pytest


@pytest.fixture(scope="session")
def soql_queries():
    file_path = os.path.join(os.path.dirname(__file__), "data", "determine_object_queries.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture(scope="session")
def fields_queries():
    file_path = os.path.join(os.path.dirname(__file__), "data", "determine_field_queries.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
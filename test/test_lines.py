from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_line():
    response = client.get("/lines/133")
    assert response.status_code == 200

    with open("test/lines/133.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_line_2():
    response = client.get("/lines/19757")
    assert response.status_code == 200

    with open("test/lines/19757.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_lines():
    response = client.get("/lines/")
    assert response.status_code == 200

    with open("test/lines/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get("/lines/?name=amy&limit=10")
    assert response.status_code == 200

    with open(
        "test/lines/lines-name=amy&limit=10.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get("/lines/?text=said&offset=30&limit=10&sort=conversation")
    assert response.status_code == 200

    with open(
        "test/lines/lines-text=said&offset=30&limit=10&sort=conversation.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/lines/1")
    assert response.status_code == 404

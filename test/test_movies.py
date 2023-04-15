from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_movie():
    response = client.get("/movies/44")
    assert response.status_code == 200

    with open("test/movies/44.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_movie_2():
    response = client.get("/movies/0")
    assert response.status_code == 200

    with open("test/movies/0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_movies():
    response = client.get("/movies/")
    assert response.status_code == 200

    with open("test/movies/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter():
    response = client.get("/movies/?name=big&limit=50&offset=0&sort=rating")
    assert response.status_code == 200

    with open(
        "test/movies/movies-name=big&limit=50&offset=0&sort=rating.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_sort_filter_2():
    response = client.get("/movies/?offset=30&limit=10&sort=rating")
    assert response.status_code == 200

    with open(
        "test/movies/movies-offset=30&limit=10&sort=rating.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/movies/1")
    assert response.status_code == 404

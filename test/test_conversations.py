from fastapi.testclient import TestClient

from src.api.server import app

import json
from src import database as db
import sqlalchemy as s

client = TestClient(app)

def test_get_conversation():
    response = client.get("/conversations/16484")
    assert response.status_code == 200

    with open("test/conversations/16484.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_get_conversation_2():
    response = client.get("/conversations/27564")
    assert response.status_code == 200

    with open("test/conversations/27564.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

def test_404():
    response = client.get("/conversations/201")
    assert response.status_code == 404

def test_add_conversation():
    stmt = (s.select(db.conversations.c.conversation_id).order_by(s.desc('conversation_id')))
    with db.engine.connect() as conn:
        conversations_result = conn.execute(stmt)
    id = conversations_result.first().conversation_id + 1
    response = client.post('movies/3/conversations/',
        json={
            'character_1_id': 49,
            'character_2_id': 55,
            'lines': [
                {
                    'character_id': 49,
                    'line_text': 'testing...'
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json() == {'conversation_id': id}

    stmt = (s.select(db.conversations.c.conversation_id).where(db.conversations.c.conversation_id == id))

    with db.engine.connect() as conn:
        conversations_result = conn.execute(stmt)

    conversation = conversations_result.first()
    assert conversation is not None

def test_add_conversation_2():
    stmt = (s.select(db.conversations.c.conversation_id).order_by(s.desc('conversation_id')))
    with db.engine.connect() as conn:
        conversations_result = conn.execute(stmt)
    id = conversations_result.first().conversation_id + 1
    response = client.post('movies/3/conversations/',
        json={
            'character_1_id': 49,
            'character_2_id': 55,
            'lines': [
                {
                    'character_id': 49,
                    'line_text': 'Stop doing computer science!'
                },
                {
                    'character_id': 55,
                    'line_text': 'Computers were supposed to solve math, NOT to be programmed.'
                },
                {
                    'character_id': 49,
                    'line_text': 'C is a LETTER, not a language.'
                },
                {
                    'character_id': 55,
                    'line_text': 'Wanna print() something? Write it in a PAPER with a PEN.'
                },
                {
                    'character_id': 49,
                    'line_text': 'If programming was real, how come nobody thought of doing while(true){print(money);}?'
                },
                {
                    'character_id': 55,
                    'line_text': 'They have played us for absolute fools.'
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json() == {'conversation_id': id}

    stmt = (s.select(db.conversations.c.conversation_id).where(db.conversations.c.conversation_id == id))

    with db.engine.connect() as conn:
        conversations_result = conn.execute(stmt)

    conversation = conversations_result.first()
    assert conversation is not None

def test_404_2():
    response = client.post('movies/3/conversations/',
        json={
            'character_1_id': 0,
            'character_2_id': 12,
            'lines': [
                {
                    'character_id': 49,
                    'line_text': 'This line should never be uploaded!'
                }
            ]
        }
    )
    assert response.status_code == 404

def test_422():
    response = client.post('movies/0/conversations/',
        json={
            'character_1_id': 3,
            'character_2_id': 3,
            'lines': [
                {
                    'character_id': 3,
                    'line_text': 'This either!'
                }
            ]
        }
    )
    assert response.status_code == 422

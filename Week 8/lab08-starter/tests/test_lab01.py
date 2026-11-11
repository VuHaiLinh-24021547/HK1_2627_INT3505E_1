"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

from jsonschema import validate, ValidationError
import pytest
from tools import get_book_schema

def test_list_books_empty(client):
    r = client.get("/books")

    assert r.status_code == 200
    assert r.content_type == "application/json"
    assert r.get_json() == []

def test_book_not_found(client):
    r = client.get("/books/9999")

    assert r.status_code == 404

def test_post_missing_title(client):
    r = client.post("/books", json={"author":"rifujin"})

    assert r.status_code == 400

    body = r.get_json()
    print(r.get_json())
    fields = {e["field"] for e in body.get("errors", [])} 
    assert "title" in fields

def test_delete_then_get_same_id(client):
    create_res = client.post("/books", json={
        "title": "Clean Code",
        "author": "Robert C. Martin"
    })
    book_id = create_res.get_json()["id"]

    delete_res = client.delete(f"books/{book_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"books/{book_id}")
    assert get_res.status_code == 404

LOGIN_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "token": {"type": "string"}
    },
    "required": ["token"],
    "additionalProperties": False
}

def test_response_extra_field_blocked(client):
    response = client.post("/auth/login", json={"user": "lab", "pwd": "lab"})
    assert response.status_code == 200
    res_data = response.get_json()
    
    validate(instance=res_data, schema=LOGIN_RESPONSE_SCHEMA)

    mock_leaked_response = res_data.copy()
    mock_leaked_response["password_hash"] = "$2b$12$eImiTXuWVfxh0..."

    with pytest.raises(ValidationError):
        validate(instance=mock_leaked_response, schema=LOGIN_RESPONSE_SCHEMA)
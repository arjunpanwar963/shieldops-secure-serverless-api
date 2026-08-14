
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import app  # noqa: E402


def _event(method, path_id=None, body=None):
    return {
        "httpMethod": method,
        "pathParameters": {"id": path_id} if path_id else None,
        "body": json.dumps(body) if body is not None else None,
    }


def setup_function():
    # Reset in-memory store between tests, so tests don't leak into each other
    app._NOTES_STORE.clear()

def test_create_note_success():
    resp = app.lambda_handler(_event("POST", body={"title": "Test", "body": "Hello"}), None)
    assert resp["statusCode"] == 201
    data = json.loads(resp["body"])
    assert data["title"] == "Test"
    assert "id" in data


def test_create_note_missing_title():
    resp = app.lambda_handler(_event("POST", body={"body": "no title"}), None)
    assert resp["statusCode"] == 400


def test_create_note_title_too_long():
    resp = app.lambda_handler(_event("POST", body={"title": "x" * 200}), None)
    assert resp["statusCode"] == 400


def test_list_notes_empty():
    resp = app.lambda_handler(_event("GET"), None)
    assert resp["statusCode"] == 200
    data = json.loads(resp["body"])
    assert data["count"] == 0


def test_get_note_not_found():
    resp = app.lambda_handler(_event("GET", path_id="00000000-0000-4000-8000-000000000000"), None)
    assert resp["statusCode"] == 404


def test_get_note_invalid_id_format_rejected():
    # Guards against path traversal / injection attempts via the id param
    resp = app.lambda_handler(_event("GET", path_id="../../etc/passwd"), None)
    assert resp["statusCode"] == 400


def test_create_then_get_note():
    create_resp = app.lambda_handler(_event("POST", body={"title": "A", "body": "B"}), None)
    note_id = json.loads(create_resp["body"])["id"]
    get_resp = app.lambda_handler(_event("GET", path_id=note_id), None)
    assert get_resp["statusCode"] == 200
    assert json.loads(get_resp["body"])["title"] == "A"


def test_delete_note():
    create_resp = app.lambda_handler(_event("POST", body={"title": "Delete me"}), None)
    note_id = json.loads(create_resp["body"])["id"]
    del_resp = app.lambda_handler(_event("DELETE", path_id=note_id), None)
    assert del_resp["statusCode"] == 200
    get_resp = app.lambda_handler(_event("GET", path_id=note_id), None)
    assert get_resp["statusCode"] == 404


def test_malformed_json_body_rejected():
    bad_event = {"httpMethod": "POST", "pathParameters": None, "body": "{not valid json"}
    resp = app.lambda_handler(bad_event, None)
    assert resp["statusCode"] == 400


def test_unsupported_method():
    resp = app.lambda_handler({"httpMethod": "PATCH", "pathParameters": None, "body": None}, None)
    assert resp["statusCode"] == 405


import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# Simple in-memory store. Resets on cold start - fine for a demo API.
_NOTES_STORE = {}

MAX_TITLE_LEN = 100
MAX_BODY_LEN = 2000
ID_PATTERN = re.compile(r"^[a-f0-9\-]{36}$")  # uuid4 format only
def _response(status_code, body_dict, extra_headers=None):
    headers = {
        "Content-Type": "application/json",
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-store",
    }
    if extra_headers:
        headers.update(extra_headers)
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body_dict),
    }


def _bad_request(msg):
    return _response(400, {"error": msg})


def _not_found():
    return _response(404, {"error": "Note not found"})


def _validate_note_payload(payload):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"
    if not isinstance(title, str) or not title.strip():
        return "Field 'title' is required and must be a non-empty string"
    if len(title) > 5:  # BROKEN ON PURPOSE - was MAX_TITLE_LEN (100)
        return f"Field 'title' must be <= {MAX_TITLE_LEN} characters"
    title = payload.get("title")
    body = payload.get("body", "")

    if not isinstance(title, str) or not title.strip():
        return "Field 'title' is required and must be a non-empty string"
    if len(title) > MAX_TITLE_LEN:
        return f"Field 'title' must be <= {MAX_TITLE_LEN} characters"
    if not isinstance(body, str):
        return "Field 'body' must be a string"
    if len(body) > MAX_BODY_LEN:
        return f"Field 'body' must be <= {MAX_BODY_LEN} characters"
    return None
def create_note(payload):
    error = _validate_note_payload(payload)
    if error:
        return _bad_request(error)

    note_id = str(uuid.uuid4())
    note = {
        "id": note_id,
        "title": payload["title"].strip(),
        "body": payload.get("body", "").strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _NOTES_STORE[note_id] = note
    logger.info("Created note %s", note_id)
    return _response(201, note)


def list_notes():
    return _response(200, {"notes": list(_NOTES_STORE.values()), "count": len(_NOTES_STORE)})


def get_note(note_id):
    if not ID_PATTERN.match(note_id or ""):
        return _bad_request("Invalid note id format")
    note = _NOTES_STORE.get(note_id)
    if not note:
        return _not_found()
    return _response(200, note)


def delete_note(note_id):
    if not ID_PATTERN.match(note_id or ""):
        return _bad_request("Invalid note id format")
    if note_id not in _NOTES_STORE:
        return _not_found()
    del _NOTES_STORE[note_id]
    return _response(200, {"message": "Note deleted"})
def lambda_handler(event, context):
    """
    Entry point wired up in template.yaml.
    `event` is the API Gateway proxy integration event.
    """
    try:
        method = event.get("httpMethod", "")
        path_params = event.get("pathParameters") or {}
        note_id = path_params.get("id")

        raw_body = event.get("body")
        payload = {}
        if raw_body:
            try:
                payload = json.loads(raw_body)
            except (json.JSONDecodeError, TypeError):
                return _bad_request("Request body must be valid JSON")

        if method == "POST" and note_id is None:
            return create_note(payload)
        if method == "GET" and note_id is None:
            return list_notes()
        if method == "GET" and note_id is not None:
            return get_note(note_id)
        if method == "DELETE" and note_id is not None:
            return delete_note(note_id)

        return _response(405, {"error": "Method not allowed"})

    except Exception:
        logger.exception("Unhandled error processing request")
        return _response(500, {"error": "Internal server error"})
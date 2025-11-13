import logging
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, DataError

logger = logging.getLogger(__name__)


def _json_error(status_code: int, message: str, detail: Any | None = None) -> JSONResponse:
	payload: Dict[str, Any] = {"success": False, "error": message}
	if detail is not None:
		payload["detail"] = detail
	return JSONResponse(status_code=status_code, content=payload)


async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
	"""Handle duplicate key and other constraint violations.

	- PostgreSQL duplicate key: SQLSTATE 23505
	- Fallback: look for 'duplicate key' text in error message
	"""
	logger.exception("IntegrityError on %s %s", request.method, request.url.path)
	pgcode = getattr(getattr(exc, "orig", None), "pgcode", None)
	msg = str(getattr(exc, "orig", exc))
	if pgcode == "23505" or "duplicate key" in msg.lower():
		return _json_error(400, "Duplicate field value entered")
	return _json_error(400, "Database integrity error")


async def handle_data_error(request: Request, exc: DataError) -> JSONResponse:
	"""Covers invalid casts/values coming from the DB driver (similar to Mongoose CastError)."""
	logger.exception("DataError on %s %s", request.method, request.url.path)
	return _json_error(400, "Invalid value for one of the fields")


async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
	"""Pydantic/FastAPI validation errors on request body/params."""
	logger.debug("RequestValidationError on %s %s: %s", request.method, request.url.path, exc.errors())
	# Collect human-readable messages similar to the JS version
	messages: List[str] = []
	for err in exc.errors():
		loc = ".".join(map(str, err.get("loc", [])))
		msg = err.get("msg", "Invalid value")
		messages.append(f"{loc}: {msg}" if loc else msg)
	return _json_error(400, ", ".join(messages), detail=exc.errors())


async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
	"""Last-resort handler to standardize 500 responses."""
	logger.exception("Unhandled error on %s %s", request.method, request.url.path)
	return _json_error(500, "Server Error")


def setup_exception_handlers(app: FastAPI) -> None:
	"""Register exception handlers on the FastAPI app.

	Mirrors the intent of the provided Express error middleware:
	- Duplicate key -> 400 with friendly message
	- Validation error -> 400 aggregated messages
	- Invalid/cast-like DB errors -> 400
	- Fallback -> 500
	"""
	app.add_exception_handler(IntegrityError, handle_integrity_error)
	app.add_exception_handler(DataError, handle_data_error)
	app.add_exception_handler(RequestValidationError, handle_request_validation_error)
	# Model-level validators may raise ValueError -> treat as 400
	app.add_exception_handler(ValueError, lambda req, exc: _json_error(400, str(exc)))
	# Keep a generic catch-all to ensure JSON shape consistency
	app.add_exception_handler(Exception, handle_unhandled_exception)


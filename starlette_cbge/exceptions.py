import http

from typing import Dict, Any

from starlette.exceptions import HTTPException


INVALID_REQUEST = "Invalid request"
CONFLICT = "Conflict"
NOT_FOUND = "Not found"


class ExtendedHTTPException(HTTPException):
    def __init__(
        self, status_code: int, detail: str = None, errors: Dict = None
    ) -> None:
        super(ExtendedHTTPException, self).__init__(status_code, detail)
        self.errors = errors

    def to_dict(self) -> Dict[str, Any]:
        return {"description": self.detail, "errors": self.errors}

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        return {
            "title": cls.__class__.__name__,
            "type": "object",
            "properties": {
                "detail": {"title": "Detail", "type": "string"},
                "errors": {
                    "title": "Errors",
                    "default": [],
                    "type": "array",
                    "items": {"type": "object"},
                },
            },
            "required": ["detail"],
        }


class InvalidRequestException(ExtendedHTTPException):
    def __init__(
        self, status_code: int = 422, detail: str = INVALID_REQUEST, errors: Dict = None
    ) -> None:
        super(InvalidRequestException, self).__init__(status_code, detail)
        self.errors = errors

    @classmethod
    def description(cls) -> str:
        return INVALID_REQUEST


class ConflictException(ExtendedHTTPException):
    def __init__(self, status_code: int = 409, detail: str = CONFLICT) -> None:
        super(ConflictException, self).__init__(status_code, detail)


class NotFoundException(ExtendedHTTPException):
    def __init__(self, status_code: int = 404, detail: str = NOT_FOUND) -> None:
        super(NotFoundException, self).__init__(status_code, detail)

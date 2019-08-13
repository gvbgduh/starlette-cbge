import http

from typing import Dict, Any

from starlette.exceptions import HTTPException


class ExtendedHTTPException(HTTPException):
    def __init__(
        self, status_code: int, detail: str = None, errors: Dict = None
    ) -> None:
        super(ExtendedHTTPException, self).__init__(status_code, detail)
        self.errors = errors

    def to_dict(self) -> Dict[str, Any]:
        return {"description": self.detail, "errors": self.errors}

    def schema(self) -> Dict[str, Any]:
        return {
            "title": self.__class__.__name__,
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
        self,
        status_code: int = 422,
        detail: str = "Invalid request",
        errors: Dict = None,
    ) -> None:
        super(InvalidRequestException, self).__init__(status_code, detail)
        self.errors = errors


class ConflictException(ExtendedHTTPException):
    def __init__(self, status_code: int = 409, detail: str = "Conflict") -> None:
        super(ConflictException, self).__init__(status_code, detail)

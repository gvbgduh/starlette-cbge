from typing import Dict, List, Any

from pydantic import BaseModel, ValidationError

from starlette_cbge.interfaces import (
    SchemaInterface,
    ListSchemaInterface,
    ValidationErrorInterface,
)


class PydanticSchema(SchemaInterface, BaseModel):
    @classmethod
    def perform_load(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return cls(**data).dict()

    @classmethod
    def perform_dump(cls, data: Any) -> Dict[str, Any]:
        return cls(**data).dict()

    @classmethod
    def openapi_schema(cls) -> Dict[str, Any]:
        return cls.schema()


class PydanticListSchema(ListSchemaInterface, BaseModel):
    @classmethod
    def perform_load(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [cls(**item_data).dict() for item_data in data]

    @classmethod
    def perform_dump(cls, data: List[Any]) -> List[Dict[str, Any]]:
        return [cls(**item_data).dict() for item_data in data]

    @classmethod
    def openapi_schema(cls) -> Dict[str, Any]:
        # TODO adjust for List
        return cls.schema()


class PydanticValidationError(ValidationErrorInterface, ValidationError):
    def get_errors(self) -> Any:
        return self.errors


class PydanticErrorResponse(BaseModel):
    description: str
    errors: List[Dict[str, Any]] = []

"""
Pydantic schema backend
"""
from typing import Dict, List, Any

try:
    import pydantic
except ImportError:
    pydantic = None  # type: ignore

from starlette_cbge.interfaces import SchemaInterface, ListSchemaInterface


class PydanticSchema(SchemaInterface, pydantic.BaseModel):
    @classmethod
    def perform_load(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return cls(**data).dict()

    @classmethod
    def perform_dump(cls, data: Any) -> Dict[str, Any]:
        return cls(**data).dict()

    @classmethod
    def openapi_schema(cls) -> Dict[str, Any]:
        return cls.schema()


class PydanticListSchema(ListSchemaInterface, pydantic.BaseModel):
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

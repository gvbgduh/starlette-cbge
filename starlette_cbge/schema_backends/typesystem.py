"""
Typesystem schema backend
"""

from typing import Dict, List, Any

try:
    import typesystem
except ImportError:
    typesystem = None  # type: ignore

from starlette_cbge.interfaces import SchemaInterface, ListSchemaInterface


typesystem_fields = typesystem.fields


class TypesystemSchema(SchemaInterface, typesystem.Schema):
    @classmethod
    def perform_load(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return dict(cls.validate(data))

    @classmethod
    def perform_dump(cls, data: Any) -> Dict[str, Any]:
        return dict(cls.validate(dict(data)))

    @classmethod
    def openapi_schema(cls) -> Dict[str, Any]:
        schema = typesystem.to_json_schema(cls)

        if not isinstance(schema, dict):
            return {}

        return schema


class TypesystemListSchema(ListSchemaInterface, typesystem.Schema):
    @classmethod
    def perform_load(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [dict(cls.validate(dict(item_data))) for item_data in data]

    @classmethod
    def perform_dump(cls, data: List[Any]) -> List[Dict[str, Any]]:
        return [dict(cls.validate(dict(item_data))) for item_data in data]

    @classmethod
    def openapi_schema(cls) -> Dict[str, Any]:
        # TODO adjust for List
        schema = typesystem.to_json_schema(cls)

        if not isinstance(schema, dict):
            return {}

        return schema

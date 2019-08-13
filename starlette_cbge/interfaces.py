from typing import Dict, List, Any


class SchemaInterface:
    @classmethod
    def perform_load(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()

    def perform_loads(self, data: Dict[str, Any]) -> str:
        raise NotImplementedError()

    @classmethod
    def perform_dump(cls, data: Any) -> Dict[str, Any]:
        raise NotImplementedError()

    def perform_dumps(self, data: Any) -> str:
        raise NotImplementedError()

    @classmethod
    def openapi_schema(cls) -> Dict[str, Any]:
        raise NotImplementedError()


class ListSchemaInterface:
    @classmethod
    def perform_load(cls, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    def perform_loads(self, data: List[Dict[str, Any]]) -> str:
        raise NotImplementedError()

    @classmethod
    def perform_dump(cls, data: List[Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    def perform_dumps(self, data: List[Any]) -> str:
        raise NotImplementedError()

    @classmethod
    def openapi_schema(cls) -> Dict[str, Any]:
        raise NotImplementedError()


class ValidationErrorInterface:
    def get_errors(self) -> Any:
        raise NotImplementedError()


class SchemaGeneratorInterface:
    pass


class ModelInterface:
    async def create(self) -> None:
        raise NotImplementedError()

    async def read(self) -> None:
        raise NotImplementedError()

    async def update(self) -> None:
        raise NotImplementedError()

    async def delete(self) -> None:
        raise NotImplementedError()

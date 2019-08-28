from starlette.applications import Starlette
from starlette.routing import Route, Router
from starlette.schemas import SchemaGenerator

from example_app.db import database
from example_app.base_api import base_pydantic
from example_app.base_api import base_typesystem


base_pydantic_api = Router(
    [
        Route("/authors", endpoint=base_pydantic.Authors, methods=["GET", "POST"]),
        Route(
            "/authors/{id}",
            endpoint=base_pydantic.Author,
            methods=["GET", "PUT", "DELETE"],
        ),
    ]
)

base_typesystem_api = Router(
    [
        Route("/authors", endpoint=base_typesystem.Authors, methods=["GET", "POST"]),
        Route(
            "/authors/{id}",
            endpoint=base_typesystem.Author,
            methods=["GET", "PUT", "DELETE"],
        ),
    ]
)


base_pydantic_schemas = SchemaGenerator(
    {
        "openapi": "3.0.0",
        "info": {"title": "Example API with Pydantic schemas", "version": "0.1.0"},
    }
)

app = Starlette()

app.mount("/base_pydantic_api", app=base_pydantic_api)
app.mount("/base_typesystem_api", app=base_typesystem_api)


@app.on_event("startup")
async def startup() -> None:
    """
    Sets environment vars and creates db connections on the server start up.
    """
    await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    """
    Closes db connections on the server shut down.
    """
    await database.disconnect()

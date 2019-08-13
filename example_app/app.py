from starlette.applications import Starlette
from starlette.routing import Route, Router
from starlette.schemas import SchemaGenerator

from example_app.db import database
from example_app.base_pydantic_api.base_pydantic import Authors, Author


base_pydantic_api = Router(
    [
        Route("/authors", endpoint=Authors, methods=["GET", "POST"]),
        Route("/authors/{id}", endpoint=Author, methods=["GET", "PUT", "DELETE"]),
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


# @app.exception_handler(HTTPException)
# async def http_exception(request, exc):
#     return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


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
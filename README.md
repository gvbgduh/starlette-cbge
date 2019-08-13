# Starlette Class Based Generic Endpoints

Extension for `starlette` endpoint classes with following goals:
- Generic endpoints
    - Implement a flexibly customisable and easy to use generic endpoint as a high level abstraction on top of the `starlette.endpoints.HTTPEndpoint`
    - Provide a set of higher level endpoints that implements common cases, eg. _CollectionEndpoint_, _ItemEndpoint_
    - Provide an interface to easily customise the class by users needs
- Schemas backends (deserialization, validation, serialization)
    - Implement a generic interface for different schema backends bootstrapping
    - Provide a set of common schema backend implementations: `pydantic`, `typesystem`, `marshmallow`
    - Provide an interface for the user custom implementations
- Schema generation backends
    - Extend the existing (`starlette.schemas.SchemaGenerator`) utilising the schema backend and generic endpoints implementation to automatically generate the API schema
    - Implement `Open API v3` automatic schema generator backend that complies with the specs
    - Provide an interface for the user custom implementations
- (Possibly) DB Models interface
    - Implement a generic model interface to allow generalising common DB operations in the related endpoints utilising the schema details, so common endpoints will require only schemas implementations, eg:
        - pagination fetch for `CollectionEndpoint.get` or item creation in `CollectionEndpoint.post`
        - item read/update/delete as `ItemEndpoint.get`, `ItemEndpoint.put` and `ItemEndpoint.delete` accordingly

---

### Current state

The current state of the library is the proof of concept (POC)

---

### Installation

TBD

---

### Example usage

Endpoint and schemas definitions

_authors.py_

```python
import typing

import aiosqlite

from starlette_cbge.endpoints import BaseEndpoint

from example_app.db import database
from starlette_cbge.schema_backends import PydanticSchema, PydanticListSchema


class AuthorGetCoolectionRequestSchema(PydanticSchema):
    limit: int = 100
    offset: int = 0


class AuthorPostRequestSchema(PydanticSchema):
    name: str


class AuthorResponseSchema(PydanticSchema):
    id: int
    name: str


class AuthorResponseListSchema(PydanticListSchema):
    id: int
    name: str


class Authors(BaseEndpoint):
    """
    Collection endpoint.
    """
    request_schema = (
        ("GET", AuthorGetCoolectionRequestSchema),
        ("POST", AuthorPostRequestSchema),
    )
    response_schema = (
        ("GET", AuthorResponseListSchema),
        ("POST", AuthorResponseSchema),
    )

    async def get(self, request_data: typing.Dict) -> typing.List[aiosqlite.Row]:
        """
        Retrieves the list of authors.
        List is limited with `limit` and `offset` fields.
        """
        async with database.connection() as connection:
            raw_connection = connection.raw_connection
            raw_connection.row_factory = aiosqlite.Row
            query = """SELECT * FROM authors LIMIT :limit OFFSET :offset"""
            cursor = await raw_connection.execute(query, request_data)
            return await cursor.fetchall()

    async def post(self, request_data: typing.Dict) -> aiosqlite.Row:
        """
        Creates a new authors and returns the created record
        """
        async with database.connection() as connection:
            raw_connection = connection.raw_connection
            raw_connection.row_factory = aiosqlite.Row
            query = "INSERT INTO authors (name) VALUES (:name);"
            await raw_connection.execute(query, request_data)
            query = "SELECT * FROM authors where id = last_insert_rowid();"
            cursor = await raw_connection.execute(query)
            return await cursor.fetchone()
```

Schema generation

```python
from starlette_cbge.schema_generator_backends import OpenAPIv3SchemaGenerator
from example_app.app import app

schemas = OpenAPIv3SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}}
    )

schema = schemas.get_schema(routes=app.routes)
```

Generated schema
> NOTE: it's not finalised output

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Example API",
    "version": "1.0"
  },
  "paths": {
    "/authors": {
      "get": {
        "description": "Retrieves the list of authors. List is limited with `limit` and `offset` fields.",
        "parameters": {
          "title": "AuthorGetCoolectionRequestSchema",
          "type": "object",
          "properties": {
            "limit": {
              "title": "Limit",
              "default": 100,
              "type": "integer"
            },
            "offset": {
              "title": "Offset",
              "default": 0,
              "type": "integer"
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful response"
          },
          "content": {
            "application/json": {
              "schema": {
                "title": "AuthorResponseListSchema",
                "type": "object",
                "properties": {
                  "id": {
                    "title": "Id",
                    "type": "integer"
                  },
                  "name": {
                    "title": "Name",
                    "type": "string"
                  }
                },
                "required": [
                  "id",
                  "name"
                ]
              }
            }
          }
        }
      },
      "post": {
        "description": "Creates a new authors and returns the created record",
        "parameters": {
          "title": "AuthorPostRequestSchema",
          "type": "object",
          "properties": {
            "name": {
              "title": "Name",
              "type": "string"
            }
          },
          "required": [
            "name"
          ]
        },
        "responses": {
          "200": {
            "description": "Successful response"
          },
          "content": {
            "application/json": {
              "schema": {
                "title": "AuthorResponseSchema",
                "type": "object",
                "properties": {
                  "id": {
                    "title": "Id",
                    "type": "integer"
                  },
                  "name": {
                    "title": "Name",
                    "type": "string"
                  }
                },
                "required": [
                  "id",
                  "name"
                ]
              }
            }
          }
        }
      }
    }
  }
}
```

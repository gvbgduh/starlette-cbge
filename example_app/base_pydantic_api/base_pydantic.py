import typing

import aiosqlite

from starlette_cbge.endpoints import BaseEndpoint

from example_app.db import database
from starlette_cbge.schema_backends import (
    PydanticSchema,
    PydanticListSchema,
    PydanticValidationError,
    PydanticErrorResponse,
)


class AuthorGetCoolectionRequestSchema(PydanticSchema):
    limit: int = 100
    offset: int = 0


class AuthorPostRequestSchema(PydanticSchema):
    name: str


class AuthorIDRequestSchema(PydanticSchema):
    id: int


class AuthorPutReuqestSchema(PydanticSchema):
    id: int
    name: str


class AuthorResponseSchema(PydanticSchema):
    id: int
    name: str


class AuthorResponseListSchema(PydanticListSchema):
    id: int
    name: str


class BlankResponseSchema(PydanticSchema):
    pass


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
    validation_error_class = PydanticValidationError
    error_response_schema = PydanticErrorResponse

    async def get(self, request_data: typing.Dict) -> typing.List[aiosqlite.Row]:
        """
        Retrieves the list of authors.
        List is limited with `limit` and `offset` fields.
        """
        async with database.connection() as connection:
            raw_connection = connection.raw_connection
            raw_connection.row_factory = aiosqlite.Row
            query = "SELECT * FROM authors LIMIT :limit OFFSET :offset;"
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


class Author(BaseEndpoint):
    """
    Item endpoint.
    """

    request_schema = (
        ("GET", AuthorIDRequestSchema),
        ("PUT", AuthorPutReuqestSchema),
        ("DELETE", AuthorIDRequestSchema),
    )
    response_schema = (
        ("GET", AuthorResponseSchema),
        ("PUT", AuthorResponseSchema),
        ("DELETE", BlankResponseSchema),
    )

    async def get(self, request_data: typing.Dict) -> aiosqlite.Row:
        """
        Retrieves the author for the given id.
        """
        async with database.connection() as connection:
            raw_connection = connection.raw_connection
            raw_connection.row_factory = aiosqlite.Row
            query = "SELECT * FROM authors WHERE id = :id;"
            cursor = await raw_connection.execute(query, request_data)
            return await cursor.fetchone()

    async def put(self, request_data: typing.Dict) -> aiosqlite.Row:
        """
        Retrieves the author for the given id.
        """
        async with database.connection() as connection:
            raw_connection = connection.raw_connection
            raw_connection.row_factory = aiosqlite.Row
            query = "UPDATE authors SET name = :name WHERE id = :id;"
            await raw_connection.execute(query, request_data)
            query = "SELECT * FROM authors where id = :id;"
            cursor = await raw_connection.execute(query, request_data)
            return await cursor.fetchone()

    async def delete(self, request_data: typing.Dict) -> None:
        """
        Deletes the record
        """
        async with database.connection() as connection:
            raw_connection = connection.raw_connection
            raw_connection.row_factory = aiosqlite.Row
            query = """DELETE FROM authors WHERE id = :id;"""
            await raw_connection.execute(query, request_data)
            return None

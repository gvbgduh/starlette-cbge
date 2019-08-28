import typing

import aiosqlite

from example_app.db import database
from starlette_cbge.exceptions import NotFoundException


class AuthorsEndpoint:
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
        Creates a new author and returns the created record
        """
        async with database.connection() as connection:
            raw_connection = connection.raw_connection
            raw_connection.row_factory = aiosqlite.Row
            query = "INSERT INTO authors (name) VALUES (:name);"
            await raw_connection.execute(query, request_data)
            query = "SELECT * FROM authors where id = last_insert_rowid();"
            cursor = await raw_connection.execute(query)
            return await cursor.fetchone()


class AuthorEndpoint:
    async def validate_get_action(self, payload: typing.Dict[str, typing.Any]) -> None:
        """
        Check if it exists
        """
        async with database.connection() as connection:
            query = "SELECT EXISTS(SELECT 1 FROM authors WHERE id = :id);"
            exists = await connection.fetch_val(query, payload)
            if not exists:
                raise NotFoundException()

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
        Updates the author for the given id.
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

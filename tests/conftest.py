"""
Global test fixtures definitions.
"""

import asyncio
import typing

import pytest

from starlette.testclient import TestClient
from starlette_cbge.test_client import AsyncTestClient


@pytest.yield_fixture(scope="session")
def event_loop() -> typing.Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client() -> typing.Generator:
    """
    Sync test client.
    """
    from example_app.app import app

    with TestClient(app=app) as client:
        yield client


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def async_client() -> typing.AsyncGenerator:
    """
    Async test client
    """
    from example_app.app import app

    async with AsyncTestClient(app=app) as async_client:
        yield async_client


@pytest.fixture(scope="session", autouse=True)
async def create_db_tables() -> typing.AsyncGenerator:
    """
    Creates tables using the helper func from the example app.
    Also drops them when tests are complete.
    """
    from example_app.db import create_tables, drop_tables

    await create_tables()
    yield
    await drop_tables()


@pytest.fixture(scope="function", autouse=True)
async def truncate_tables() -> typing.AsyncGenerator:
    """
    Truncates tables before every test,
    basically to allow transactional operations complete.
    """
    from example_app.db import truncate_tables

    await truncate_tables()
    yield

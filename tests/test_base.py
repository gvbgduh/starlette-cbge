import pytest

from starlette_cbge.schema_generator_backends import OpenAPIv3SchemaGenerator
from starlette_cbge.test_client import AsyncTestClient

from example_app.db import insert_data


API_PYDANTIC_BASE_URL = "/base_pydantic_api"
API_TYPESYSTEM_BASE_URL = "/base_typesystem_api"

BASE_URLS = [API_PYDANTIC_BASE_URL, API_TYPESYSTEM_BASE_URL]


@pytest.mark.parametrize("base_url", BASE_URLS)
@pytest.mark.asyncio
async def test_authors_endpoint_get_collection(
    async_client: AsyncTestClient, base_url: str
) -> None:
    """
    Test the get collection method.
    """
    await insert_data()

    response = await async_client.get(f"{base_url}/authors")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Author 1"},
        {"id": 2, "name": "Author 2"},
        {"id": 3, "name": "Author 3"},
    ]


@pytest.mark.parametrize("base_url", BASE_URLS)
@pytest.mark.asyncio
async def test_authors_endpoint_post(
    async_client: AsyncTestClient, base_url: str
) -> None:
    """
    Test the post method and the get one afterwards.
    """
    await insert_data()

    response = await async_client.post(
        f"{API_PYDANTIC_BASE_URL}/authors", json={"name": "Author X"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": 4, "name": "Author X"}

    response = await async_client.get(f"{base_url}/authors")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Author 1"},
        {"id": 2, "name": "Author 2"},
        {"id": 3, "name": "Author 3"},
        {"id": 4, "name": "Author X"},
    ]


@pytest.mark.parametrize("base_url", BASE_URLS)
@pytest.mark.asyncio
async def test_authors_endpoint_post_invalid_payload(
    async_client: AsyncTestClient, base_url: str
) -> None:
    """
    Test the post method with invalid payload.
    """
    response = await async_client.post(f"{base_url}/authors", json={"foo": "bar"})
    assert response.status_code == 422

    if base_url == API_PYDANTIC_BASE_URL:
        assert response.json() == {
            "description": "Invalid request",
            "errors": [
                {
                    "loc": ["name"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ],
        }
    elif base_url == API_TYPESYSTEM_BASE_URL:
        assert response.json() == {
            "description": "Invalid request",
            "errors": {"name": "This field is required."},
        }


@pytest.mark.parametrize("base_url", BASE_URLS)
@pytest.mark.asyncio
async def test_author_endpoint_get_item(
    async_client: AsyncTestClient, base_url: str
) -> None:
    """
    Test the get item endpoint.
    """
    await insert_data()

    response = await async_client.get(f"{base_url}/authors/3")
    assert response.status_code == 200
    assert response.json() == {"id": 3, "name": "Author 3"}


@pytest.mark.parametrize("base_url", BASE_URLS)
@pytest.mark.asyncio
async def test_author_endpoint_get_missing_item(
    async_client: AsyncTestClient, base_url: str
) -> None:
    """
    Test the get item endpoint.
    """
    await insert_data()

    response = await async_client.get(f"{base_url}/authors/333")
    assert response.status_code == 404
    assert response.json() == {"description": "Not found", "errors": None}


@pytest.mark.parametrize("base_url", BASE_URLS)
@pytest.mark.asyncio
async def test_author_endpoint_put_item(
    async_client: AsyncTestClient, base_url: str
) -> None:
    """
    Test the put item endpoint.
    """
    await insert_data()

    response = await async_client.put(
        f"{base_url}/authors/3", json={"name": "Author 3 changed"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": 3, "name": "Author 3 changed"}


@pytest.mark.parametrize("base_url", BASE_URLS)
@pytest.mark.asyncio
async def test_author_endpoint_delete_item(
    async_client: AsyncTestClient, base_url: str
) -> None:
    """
    Test the put item endpoint.
    """
    await insert_data()

    response = await async_client.delete(f"{base_url}/authors/3")
    assert response.status_code == 204
    assert response.json() == None

    response = await async_client.get(f"{base_url}/authors")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Author 1"},
        {"id": 2, "name": "Author 2"},
    ]


@pytest.mark.asyncio
async def test_the_schema_generation(async_client: AsyncTestClient) -> None:

    schemas = OpenAPIv3SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}}
    )

    schema = schemas.get_schema(routes=async_client.app.routes)
    # Just check if it works for now
    assert schema

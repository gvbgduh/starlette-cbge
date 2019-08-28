"""
Example endpoints with the pydantic backend
"""

from starlette_cbge.endpoints import PydanticBaseEndpoint
from starlette_cbge.schema_backends import PydanticSchema, PydanticListSchema

from example_app.base_api.base_common import AuthorsEndpoint, AuthorEndpoint


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


class Authors(PydanticBaseEndpoint, AuthorsEndpoint):
    """
    Collection endpoint.
    """

    request_schemas = (
        ("GET", AuthorGetCoolectionRequestSchema),
        ("POST", AuthorPostRequestSchema),
    )
    response_schemas = (
        ("GET", AuthorResponseListSchema),
        ("POST", AuthorResponseSchema),
    )


class Author(PydanticBaseEndpoint, AuthorEndpoint):
    """
    Item endpoint.
    """

    request_schemas = (
        ("GET", AuthorIDRequestSchema),
        ("PUT", AuthorPutReuqestSchema),
        ("DELETE", AuthorIDRequestSchema),
    )
    response_schemas = (
        ("GET", AuthorResponseSchema),
        ("PUT", AuthorResponseSchema),
        ("DELETE", BlankResponseSchema),
    )

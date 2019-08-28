"""
Example endpoints with the typesystem backend
"""

from starlette_cbge.endpoints import TypesystemBaseEndpoint
from starlette_cbge.schema_backends import (
    TypesystemSchema,
    TypesystemListSchema,
    typesystem_fields,
)

from example_app.base_api.base_common import AuthorsEndpoint, AuthorEndpoint


class AuthorGetCoolectionRequestSchema(TypesystemSchema):
    limit = typesystem_fields.Integer(default=100)
    offset = typesystem_fields.Integer(default=0)


class AuthorPostRequestSchema(TypesystemSchema):
    name = typesystem_fields.String()


class AuthorIDRequestSchema(TypesystemSchema):
    id = typesystem_fields.Integer()


class AuthorPutReuqestSchema(TypesystemSchema):
    id = typesystem_fields.Integer()
    name = typesystem_fields.String()


class AuthorResponseSchema(TypesystemSchema):
    id = typesystem_fields.Integer()
    name = typesystem_fields.String()


class AuthorResponseListSchema(TypesystemListSchema):
    id = typesystem_fields.Integer()
    name = typesystem_fields.String()


class BlankResponseSchema(TypesystemSchema):
    pass


class Authors(TypesystemBaseEndpoint, AuthorsEndpoint):
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


class Author(TypesystemBaseEndpoint, AuthorEndpoint):
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

"""
Implementation of the Open API v3 schema generator.
"""

import inspect
import typing
import yaml

from typing import Union

from starlette.schemas import SchemaGenerator
from starlette.routing import BaseRoute, Mount, Route
from starlette_cbge.endpoints import BaseEndpoint


class ExtendedEndpointInfo(typing.NamedTuple):
    path: str
    http_method: str
    func: typing.Callable
    endpoint: BaseEndpoint
    # endpoint: typing.Callable[BaseEndpoint]


class OpenAPIv3SchemaGenerator(SchemaGenerator):
    def parse_docstring(self, func_or_method: typing.Callable) -> dict:
        """
        Given a function, parse the docstring as YAML and return a dictionary of info.
        """
        docstring = func_or_method.__doc__
        if not docstring:
            return {}

        # We support having regular docstrings before the schema
        # definition. Here we return just the schema part from
        # the docstring.
        docstring = docstring.split("---")[-1]

        parsed = yaml.safe_load(docstring)

        return parsed

    def get_extended_endpoints(
        self, routes: typing.List[BaseRoute]
    ) -> typing.List[ExtendedEndpointInfo]:
        """
        Given the routes, yields the following information:

        - path
            eg: /users/
        - http_method
            one of 'get', 'post', 'put', 'patch', 'delete', 'options'
        - func
            method ready to extract the docstring
        """
        endpoints_info: list = []

        for route in routes:
            if isinstance(route, Mount):
                routes = route.routes or []
                sub_endpoints = [
                    ExtendedEndpointInfo(
                        path="".join((route.path, sub_endpoint.path)),
                        http_method=sub_endpoint.http_method,
                        func=sub_endpoint.func,
                        endpoint=sub_endpoint.endpoint,  # TODO check
                    )
                    for sub_endpoint in self.get_extended_endpoints(routes)
                ]
                endpoints_info.extend(sub_endpoints)

            elif not isinstance(route, Route) or not route.include_in_schema:
                continue

            elif inspect.isfunction(route.endpoint) or inspect.ismethod(route.endpoint):
                # TODO add support later
                # for method in route.methods or ["GET"]:
                #     if method == "HEAD":
                #         continue
                #     endpoints_info.append(
                #         ExtendedEndpointInfo(
                #             route.path, method.lower(), route.endpoint, None
                #         )  # TODO check
                #     )
                continue
            else:
                for method in ["get", "post", "put", "patch", "delete", "options"]:
                    if not hasattr(route.endpoint, method):
                        continue
                    func = getattr(route.endpoint, method)
                    endpoint = route.endpoint
                    endpoints_info.append(
                        ExtendedEndpointInfo(  # type: ignore  # TODO resolve!
                            route.path, method.lower(), func, endpoint
                        )
                    )

        return endpoints_info

    def get_schema(self, routes: typing.List[BaseRoute]) -> dict:
        """
        NOTE: a pretty rough and approx implementation, POC only

        TODO use schemas for OpenAPI specs?
        TODO check if it's a subclass of the BaseEndpoint
        """
        schema = dict(self.base_schema)
        schema.setdefault("paths", {})
        endpoints_info = self.get_extended_endpoints(routes)

        for endpoint in endpoints_info:
            if endpoint.path not in schema["paths"]:
                schema["paths"][endpoint.path] = {}

            schema["paths"][endpoint.path][endpoint.http_method] = {}
            target = schema["paths"][endpoint.path][endpoint.http_method]

            target["description"] = self.parse_docstring(endpoint.func)
            # TODO distinguish body and parameters below
            request_schema_class = dict(endpoint.endpoint.request_schemas).get(
                endpoint.http_method.upper()
            )
            if request_schema_class:
                # TODO there probably should be always a schema, or default as a black schema
                target["parameters"] = request_schema_class.openapi_schema()

            # TODO account responses for exceptions
            target["responses"] = {}

            response_schema_class = dict(endpoint.endpoint.response_schemas).get(
                endpoint.http_method.upper()
            )
            response_schema = (
                response_schema_class.openapi_schema() if response_schema_class else {}
            )

            # TODO account non-std success status codes
            # TODO refactor
            target["responses"]["200"] = {}
            target["responses"]["200"]["description"] = "Successful response"
            target["responses"]["200"]["content"] = {}
            target["responses"]["200"]["content"][
                endpoint.endpoint.response_class.media_type
            ] = {}
            target["responses"]["200"]["content"][
                endpoint.endpoint.response_class.media_type
            ]["schema"] = response_schema

            # Add exception responses
            for status, exception in dict(endpoint.endpoint.exception_classes).items():
                target["responses"][status] = {}
                target["responses"][status]["description"] = exception.description()
                target["responses"][status]["content"] = {}
                target["responses"][status]["content"][
                    endpoint.endpoint.response_class.media_type
                ] = {}
                target["responses"][status]["content"][
                    endpoint.endpoint.response_class.media_type
                ]["schema"] = exception.schema()

            # TODO hook exceptions
        return schema

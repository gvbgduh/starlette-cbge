"""
Implementation of the Base endpoint class.

TODO exceptions handling
TODO custom exception - custom fields
TODO custom error schema
"""
import asyncio
import typing

from typing import Dict, Any, Union, Optional, Tuple, Iterable

from starlette.background import BackgroundTasks
from starlette.concurrency import run_in_threadpool
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import (
    UJSONResponse,
    Response,
)  # TODO make optional UJSONResponse
from starlette.types import Message, Receive, Scope, Send

from starlette_cbge.exceptions import ExtendedHTTPException, InvalidRequestException


class BaseEndpoint(HTTPEndpoint):
    request_schemas: Iterable[Tuple[str, Any]]
    response_schemas: Iterable[Tuple[str, Any]]

    # TODO run with `exception_handler`?
    exception_classes: Iterable[Tuple[str, Any]] = (("422", InvalidRequestException),)

    # TODO make it vary per method (?)
    response_class = UJSONResponse
    base_exception_class = ExtendedHTTPException

    @property
    def request_schema(self) -> Dict[str, Any]:
        if self.request_schemas:
            return dict(self.request_schemas)
        else:
            raise NotImplementedError("No request schemas provided")

    @property
    def response_schema(self) -> Dict[str, Any]:
        if self.response_schemas:
            return dict(self.response_schemas)
        else:
            raise NotImplementedError("No response schemas provided")

    @property
    def exception_class(self) -> Dict[str, Any]:
        if self.exception_classes:
            return dict(self.exception_classes)
        else:
            raise NotImplementedError("No exception classes provided")

    def get_resource(self, key: str, resource_name: str) -> Any:
        """
        Get a resource class depending on the request method (for schemas)
        or status code (for exceptions),
        be it a request or response schema or an exception class.
        """
        resources = getattr(self, resource_name, None)
        if resources is None:
            raise NotImplementedError(
                f"Resources of {resource_name} type are not provided"
            )

        resource = resources.get(key.upper(), None)
        if resource is None:
            raise NotImplementedError(
                f"Resource {resource_name} has no class for {key} {'status code' if resource_name == 'exception_class' else 'method'}."
            )

        return resource

    def get_request_schema(self, method: str) -> Any:
        """
        Request schema look up
        """
        return self.get_resource(method, resource_name="request_schema")

    def get_response_schema(self, method: str) -> Any:  # TODO !?
        """
        Response schema look up
        """
        return self.get_resource(method, resource_name="response_schema")

    def get_exception_class(self, status: str) -> Any:
        """
        Exception class look up
        """
        return self.get_resource(status, resource_name="exception_class")

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Adds the background tasks pool.
        """
        super().__init__(scope, receive, send)
        self.tasks = BackgroundTasks()

    async def dispatch(self) -> None:
        """
        Overriding of the existing method.
        """
        request = Request(self.scope, receive=self.receive)
        handler = self.perform_action
        # In case the `perform_action` method is overridden with a sync one.
        is_async = asyncio.iscoroutinefunction(handler)
        if is_async:
            response = await handler(request)
        else:
            response = await run_in_threadpool(handler, request)
        await response(self.scope, self.receive, self.send)

    async def acquire_request_payload(self, request: Request) -> Dict[str, Any]:
        """
        Grab all details from the request, including:
        - path params
        - query params
        - json payload
        - form data payload

        # TODO implement dispatcher for a particular payload
        # TODO depending on the request content type
        """
        payload = {
            "path_params": request.path_params,
            "query_params": dict(request.query_params),
        }

        if request.method not in ["POST", "PUT", "PATCH"]:
            return payload

        try:
            json_data = await request.json()
        except Exception:  # TODO More sophisticated approach
            json_data = {}

        payload["json_data"] = json_data

        form_data = await request.form()
        payload["form_data"] = dict(form_data)

        return payload

    async def shape_request_data(self, request: Request) -> Dict[str, Any]:
        """
        Shaping of the raw request data to the form required for the request schema.

        TODO: Implement `request` and `params` parts for the OpenAPI v3
        """
        # Place to override
        request_payload = await self.acquire_request_payload(request)

        data: Dict[str, Any] = {}

        for section, data_dict in request_payload.items():
            # TODO check fields are not overridden
            data.update(data_dict)

        return data

    async def deserialize_payload(self, request: Request) -> Dict[str, Any]:
        """
        Run the shaped raw request data through the request model to perform:
        - deserialization where/if required
        - request data validation
        - request data post-processing if required

        Should be implemented in the particular schema back-end class.
        """
        raise NotImplementedError()

    async def acquire_request_context(self, request: Request) -> Dict[str, Any]:
        """
        Get additional context required for the request schema.
        """
        deserialized_payload = await self.deserialize_payload(request)
        # TODO to implement custom context
        return deserialized_payload

    async def validate_action(self, request: Request) -> Dict[str, Any]:
        """
        Performs user defined validation.
        Can be done here by overriding this method or by per method definitions
        defining new method as `async def validate_{request.method}_action`.
        """
        payload = await self.acquire_request_context(request)

        # TODO to implement custom validation

        validate_method_action = getattr(
            self, f"validate_{request.method}_action", None
        )

        if validate_method_action is not None:
            await validate_method_action(payload)

        return payload

    # async def acquire_query_results(self, request):
    #     """
    #     For common queries usage, per method??
    #     """
    #     raise NotImplementedError()

    async def collect_background_tasks(
        self, request_data: Dict[str, Any], raw_response: Any
    ) -> None:
        """
        Method to be overridden to set all user defined background tasks.
        """
        pass

    async def perform_action(self, request: Request) -> Response:
        """
        The heartbeat of the endpoint - method triggered by dispatch.
        Orchestrates request data retrieval, method call and response processing.
        Also handles user defined exception that are subclassed from `self.base_exception_class`.
        """
        handler_name = "get" if request.method == "HEAD" else request.method.lower()
        handler = getattr(self, handler_name, None)

        if handler is None:
            return await self.method_not_allowed(request)

        try:
            request_data = await self.validate_action(request)
            is_async = asyncio.iscoroutinefunction(handler)
            if is_async:
                raw_response = await handler(request_data)
            else:
                raw_response = await run_in_threadpool(handler, request_data)

            # Collect background tasks
            await self.collect_background_tasks(request_data, raw_response)

            return await self.process_response(request, request_data, raw_response)

        except self.base_exception_class as exception:
            return await self.process_failure(exception)

    async def acquire_response_context(
        self, request_data: Dict[str, Any], raw_response: Any
    ) -> Any:
        """
        User defined procedure to acquire additional context required for the response schema.
        """
        return raw_response

    async def serialise_response(
        self, request: Request, request_data: Dict[str, Any], raw_response: Any
    ) -> Dict[str, Any]:
        """
        Run the raw response data through the request model to perform:
        - response data validation (not handled exception)
        - response data post-processing if required
        - response data serialization

        Should be implemented in the particular schema back-end class.
        """
        raise NotImplementedError()

    async def process_response(
        self, request: Request, request_data: Dict[str, Any], raw_response: Any
    ) -> Response:
        """
        Orchestrates the response processing flow.
        """
        if request.method.lower() == "delete" and raw_response is None:
            return await self.process_success(response_data=None, status_code=204)

        response_data = await self.serialise_response(
            request, request_data, raw_response
        )
        return await self.process_success(response_data)

    async def process_failure(self, exception: ExtendedHTTPException) -> Response:
        """
        Handles failure during this request for handled exceptions.
        """
        return self.response_class(
            exception.to_dict(), status_code=exception.status_code
        )

    async def process_success(
        self, response_data: Optional[Dict[str, Any]], status_code: int = 200
    ) -> Response:
        """
        Handles final response wrapping to the Response class
        """
        return self.response_class(
            response_data, background=self.tasks, status_code=status_code
        )

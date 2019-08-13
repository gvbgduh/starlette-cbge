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
from starlette.responses import UJSONResponse, Response  # TODO make optional
from starlette.types import Message, Receive, Scope, Send

from starlette_cbge.exceptions import ExtendedHTTPException, InvalidRequestException


class BaseEndpoint(HTTPEndpoint):
    request_schema: Iterable[Tuple[str, Any]]
    response_schema: Iterable[Tuple[str, Any]]

    # TODO make it vary per method (?)
    response_class = UJSONResponse
    validation_error_class: Optional[Any] = None
    error_response_schema: Optional[Any] = None

    @property
    def request_schemas(self) -> Dict[str, Any]:
        if self.request_schema:
            return dict(self.request_schema)
        else:
            raise NotImplementedError()

    @property
    def response_schemas(self) -> Dict[str, Any]:
        if self.response_schema:
            return dict(self.response_schema)
        else:
            raise NotImplementedError()

    def get_request_schema(self, method: str) -> Any:  # TODO !?
        # TODO Consider common schema
        request_schema = self.request_schemas.get(method)
        if not request_schema:
            raise NotImplementedError("No schema provided")
        return request_schema

    def get_response_schema(self, method: str) -> Any:  # TODO !?
        # TODO Consider common schema
        response_schema = self.response_schemas.get(method)
        if not response_schema:
            raise NotImplementedError("No schema provided")
        return response_schema

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        super().__init__(scope, receive, send)
        self.tasks = BackgroundTasks()

    async def dispatch(self) -> None:
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
        # Place to override
        request_payload = await self.acquire_request_payload(request)

        data: Dict[str, Any] = {}

        for section, data_dict in request_payload.items():
            # TODO check fields are not overridden
            data.update(data_dict)

        return data

    async def deserialize_payload(self, request: Request) -> Dict[str, Any]:
        # raise NotImplementedError()
        # TODO move to backend !!!
        request_payload = await self.shape_request_data(request)
        request_schema = self.get_request_schema(request.method)
        try:
            deserialized_payload = request_schema.perform_load(request_payload)
        except Exception as exc:
            if issubclass(self.validation_error_class, exc.__class__):
                raise InvalidRequestException(errors=exc.errors())
        return deserialized_payload

    async def acquire_request_context(self, request: Request) -> Dict[str, Any]:
        deserialized_payload = await self.deserialize_payload(request)
        # TODO to implement custom context
        return deserialized_payload

    async def validate_action(self, request: Request) -> Dict[str, Any]:
        payload = await self.acquire_request_context(request)

        # TODO to implement custom validation

        validate_method_action = getattr(
            self, f"validate_{request.method}_action", None
        )

        if validate_method_action is not None:
            await validate_method_action(payload)

        return payload

    # async def acquire_query_results(self, request):
    #     raise NotImplementedError()

    async def collect_background_tasks(
        self, request_data: Dict[str, Any], raw_response: Any
    ) -> None:
        pass

    async def perform_action(self, request: Request) -> Response:
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

        except ExtendedHTTPException as exception:
            return await self.process_failure(exception)

    async def acquire_response_context(
        self, request_data: Dict[str, Any], raw_response: Any
    ) -> Any:  # TODO !?
        return raw_response

    async def serialise_response(
        self, request: Request, request_data: Dict[str, Any], raw_response: Any
    ) -> Dict[str, Any]:
        # raise NotImplementedError()
        # TODO move to backend !!!
        response_schema = self.get_response_schema(request.method)
        raw_response = await self.acquire_response_context(request_data, raw_response)
        response_data = response_schema.perform_dump(raw_response)
        return response_data

    async def process_response(
        self, request: Request, request_data: Dict[str, Any], raw_response: Any
    ) -> Response:
        if request.method.lower() == "delete" and raw_response is None:
            return await self.process_success(response_data=None, status_code=204)

        response_data = await self.serialise_response(
            request, request_data, raw_response
        )
        return await self.process_success(response_data)

    async def process_failure(self, exception: ExtendedHTTPException) -> Response:
        # TODO define the schema !!
        return self.response_class(
            exception.to_dict(), status_code=exception.status_code
        )

    async def process_success(
        self, response_data: Optional[Dict[str, Any]], status_code: int = 200
    ) -> Response:
        return self.response_class(
            response_data, background=self.tasks, status_code=status_code
        )

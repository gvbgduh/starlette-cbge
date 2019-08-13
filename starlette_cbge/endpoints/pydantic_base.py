"""
Implementation of the base pydantic endpoint
"""

from typing import Dict, Any

from starlette.requests import Request

from starlette_cbge.endpoints import BaseEndpoint

try:
    import pydantic
except ImportError:
    pydantic = None  # type: ignore


class PydanticBaseEndpoint(BaseEndpoint):
    async def deserialize_payload(self, request: Request) -> Dict[str, Any]:
        """
        Run the shaped raw response data through the request model to perform:
        - deserialization where/if required
        - request data validation
        - request data post-processing if required

        Implementation for the pydantic schema back-end.
        """
        request_payload = await self.shape_request_data(request)
        request_schema = self.get_request_schema(request.method)
        try:
            deserialized_payload = request_schema.perform_load(request_payload)
        except pydantic.ValidationError as exc:
            raise self.get_exception_class("422")(errors=exc.errors())

        return deserialized_payload

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
        response_schema = self.get_response_schema(request.method)
        raw_response = await self.acquire_response_context(request_data, raw_response)
        response_data = response_schema.perform_dump(raw_response)
        return response_data

from pydantic import validate_arguments
from types import NoneType
import requests
import json

from .config import ADULT, MAINSTREAM, BASE_URL

class ShrtFlyError(Exception):
    @validate_arguments
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"ShrtFlyError({self.message})"

class ShrtFlyResponse:
    @validate_arguments
    def __init__(
        self,
        response: str,
        is_text_format: bool
    ) -> None:
        self.response = response
        self.is_text_format = is_text_format
        self.json_response: dict = json.loads(self.response)
        self.result = self.json_response["result"]

    def get_raw_data(self) -> str | dict:
        if self.is_text_format:
            return self.response

        return self.json_response

    def get_shortened_url(self) -> str | None:
        if self.is_text_format:
            raise ShrtFlyError("It is not possible to get this data because you passed 'is_text_format' as True")

        return self.result["shorten_url"]

    def get_status(self) -> str | None:
        if self.is_text_format:
            raise ShrtFlyError("It is not possible to get this data because you passed 'is_text_format' as True")

        return self.result["status"]

class ShrtFly:
    @validate_arguments
    def __init__(
        self,
        api_token: str,
    ) -> None:
        self.__api_token = api_token

    @validate_arguments
    def shorten(
        self,
        url: str,
        alias: str | NoneType = None,
        is_text_format: bool = False,
        ads_type: int | NoneType = None,
    ) -> ShrtFlyResponse:
        params = {
            "api": self.__api_token,
            "url": url,
        }

        if alias:
            params["alias"] = alias

        if is_text_format:
            params["format"] = "text"

        if ads_type != None:
            if ads_type == MAINSTREAM:
                params["type"] = MAINSTREAM

            elif ads_type == ADULT:
                params["type"] = ADULT

            else:
                raise ShrtFlyError(f"{ads_type} is not valid ads type")

        response = requests.get(BASE_URL, params)
        json_response = response.json()

        if response.status_code != 200:
            raise ShrtFlyError(f"[Request Error] Status code: {response.status_code}")

        if response.text == "" or json_response["status"] == "error":
            message = json_response["result"]
            raise ShrtFlyError(message)

        return ShrtFlyResponse(response.text, is_text_format)

__all__ = [ ShrtFly ]
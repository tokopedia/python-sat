from dataclasses import dataclass, field
from typing import List

from dataclasses_json import Undefined, dataclass_json

from py_sat.models.base import BaseResponse


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ErrorObject:
    """
    Error object, represent error detail from SAT API
    """

    id: str = field(default="")
    title: str = field(default="")
    detail: str = field(default="")
    status: str = field(default="")
    code: str = field(default="")
    meta: dict = field(default_factory=dict)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ErrorResponse(BaseResponse):
    """
    Error response object, represent error response from SAT API
    """

    errors: List[ErrorObject] = field(default_factory=list)

    def get_error_messages(self) -> str:
        """
        Get error messages from errors
        :return: string of error messages, separated by new line
        """
        if len(self.errors) <= 0:
            return ""

        messages = [
            f"{error.status} - {error.code} - {error.detail}" for error in self.errors
        ]
        return "\n".join(messages)

    def get_error_codes(self) -> str:
        """
        Get error codes from errors
        :return: string of error codes, separated by comma
        """
        if len(self.errors) <= 0:
            return ""

        return ", ".join([error.code for error in self.errors])

    def get_error_statuses(self) -> str:
        """
        Get error statuses from errors
        :return: string of error statuses, separated by comma
        """
        if len(self.errors) <= 0:
            return ""

        return ", ".join([error.status for error in self.errors])

    def get_error_details(self) -> str:
        """
        Get error details from errors
        :return: string of error details, separated by comma
        """

        if len(self.errors) <= 0:
            return ""

        return ", ".join([error.detail for error in self.errors])

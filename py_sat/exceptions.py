from requests import HTTPError, Request, Response


class InvalidInputException(Exception):
    pass


class UnauthenticatedException(Exception):
    pass


class SignatureErrorException(Exception):
    pass


class ResponseGeneralException(Exception):
    _raw_request: Request
    _raw_response: Response

    def __init__(self, exc: HTTPError):
        if isinstance(exc, HTTPError):
            self._raw_response = exc.response
            self._raw_request = exc.request

        super().__init__(exc)

    def get_raw_response(self) -> Response:
        return self._raw_response


class GeneralException(Exception):
    def __init__(
        self,
        original_exception,
        message="An error occurred",
    ):
        self.message = f"{message}: {original_exception}"
        super().__init__(self.message)

import logging
from datetime import datetime, timezone

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from py_sat.constant import DATE_TIME_FORMAT, SDK_LABEL


class HTTPClient:
    _base_url: str
    _oauth_base_url: str
    _access_token: str
    _client_id: str
    _client_secret: str
    _session: requests.Session
    _auth: OAuth2Session
    _logger: logging.Logger
    _is_debug: bool

    def __init__(
        self,
        base_url: str,
        oauth_base_url: str,
        client_id: str,
        client_secret: str,
        logger: logging.Logger,
        is_debug: bool = False,
    ):
        self._base_url = base_url
        self._oauth_base_url = oauth_base_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = self._prepare_session()
        self._logger = logger
        self._is_debug = is_debug

        self._auth = OAuth2Session(
            client=BackendApplicationClient(client_id),
            client_id=client_id,
            token_updater=lambda token: self._save_token(token),
            auto_refresh_url=self._oauth_base_url,
            auto_refresh_kwargs={
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        self._access_token = self.get_access_token()

    def _save_token(self, token):
        self._access_token = token

    @staticmethod
    def _prepare_session():
        session = requests.Session()
        session.headers.update({})

        return session

    def get_access_token(self):
        token = self._auth.fetch_token(
            token_url=self._oauth_base_url,
            client_id=self._client_id,
            client_secret=self._client_secret,
        )

        return token.get("access_token")

    def send_request(self, request: requests.Request) -> requests.Response:
        """Sends a prepared Request object and returns the response."""
        request.headers["Date"] = datetime.now(timezone.utc).strftime(DATE_TIME_FORMAT)
        request.headers["Content-Type"] = "application/json"
        request.headers["Accept"] = "application/json"
        request.headers["X-Sat-Sdk-Version"] = SDK_LABEL
        request.headers["Authorization"] = f"Bearer {self._access_token}"

        prepared_request = self._auth.prepare_request(request)

        response = self._session.send(prepared_request)

        self._logger.info(
            f"Request: {response.request.url}, {response.request.method} {response.request.body} {response.request.headers}"
        )

        return response

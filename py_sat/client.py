"""
client package contains the main class to interact with the SAT service.
"""

import json
import logging
from typing import Any, Callable, Dict, Optional, Union

import requests
from requests.exceptions import HTTPError

from py_sat.constant import (ACCESS_TOKEN_URL, ACCOUNT_PATH, CHECK_STATUS_PATH,
                             CHECKOUT_PATH, INQUIRY_PATH, PING_PATH,
                             PLAYGROUND_SAT_BASE_URL, PRODUCT_LIST_PATH)
from py_sat.exceptions import (GeneralException, InvalidInputException,
                               ResponseGeneralException,
                               UnauthenticatedException)
from py_sat.http_client import HTTPClient
from py_sat.models import (Account, ErrorResponse, InquiryRequest,
                           InquiryResponse, OrderDetail, OrderRequest,
                           PartnerProduct, PingResponse, ProductListResponse)
from py_sat.signature import Signature, SignatureType
from py_sat.utils import (generate_json_api_request,
                          parse_json_api_list_response,
                          parse_json_api_response)


class SATClientConfig:
    """
    SATClientConfig is a configuration class to initialize the SATClient
    """

    # Required
    client_id: str
    client_secret: str
    private_key: str

    # Optional
    public_key: Optional[str]
    padding_type: SignatureType
    is_debug: bool
    sat_base_url: str
    access_token_base_url: str
    timeout: int
    logger: logging.Logger

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        private_key: str,
    ):
        if not client_id or not isinstance(client_id, str):
            raise InvalidInputException("Client ID are required and must be a string")

        if not client_secret or not isinstance(client_secret, str):
            raise InvalidInputException(
                "Client Secret are required and must be a string"
            )

        if not private_key or not isinstance(private_key, str):
            raise InvalidInputException("Private key is required and must be a string")

        self.client_id = client_id
        self.client_secret = client_secret
        self.private_key = private_key

        self._set_default_value()

    def _set_default_value(self):
        logger: logging.Logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        self.logger = logger

        self.public_key = None
        self.padding_type = SignatureType.PSS
        self.is_debug = False
        self.sat_base_url = PLAYGROUND_SAT_BASE_URL
        self.access_token_base_url = ACCESS_TOKEN_URL
        self.timeout = 30

    def with_logger(self, logger: logging.Logger):
        self.logger = logger
        return self

    def with_public_key(self, public_key: str):
        self.public_key = public_key
        return self

    def with_padding_type(self, padding_type: SignatureType):
        self.padding_type = padding_type
        return self

    def with_is_debug(self, is_debug: bool):
        self.is_debug = is_debug
        return self

    def with_sat_base_url(self, sat_base_url: str):
        self.sat_base_url = sat_base_url
        return self

    def with_timeout(self, timeout: int):
        self.timeout = timeout
        return self

    def with_access_token_base_url(self, access_token_base_url: str):
        self.access_token_base_url = access_token_base_url
        return self


class SATClient:
    """
    SATClient is a main class for SAT SDK, this class contains all the method to interact with SAT service
    """

    _config: SATClientConfig
    signature: Signature
    _logger: logging.Logger
    _http_client: HTTPClient

    def __init__(self, config: SATClientConfig):
        self._config = config
        self.signature = Signature(
            config.private_key, config.public_key, config.padding_type
        )
        self._logger = config.logger
        self._http_client = HTTPClient(
            base_url=config.sat_base_url,
            oauth_base_url=config.access_token_base_url,
            client_id=config.client_id,
            client_secret=config.client_secret,
            logger=config.logger,
        )

    def ping(self) -> Union[PingResponse, ErrorResponse]:
        """
        Ping is a method to check the SAT server health
               :return: PingResponse or ErrorResponse
               :raise ResponseGeneralException: if there are unexpected error when hitting SAT (403 forbidden, network error)
               :raise GeneralException: if there is an unexpected exception when pinging
        """
        try:
            url = f"{self._config.sat_base_url}{PING_PATH}"

            req = requests.Request(method="GET", url=url)
            response = self._http_client.send_request(req)
            response.raise_for_status()

            json_response = response.json()
            return PingResponse.from_dict(json_response).with_raw_response(response)
        except HTTPError as exc:
            return self._handle_http_error(exc)
        except Exception as exc:
            self._logger.error(f"Error when pinging: {exc}")
            raise GeneralException(exc)

    def inquiry(self, req: InquiryRequest) -> Union[InquiryResponse, ErrorResponse]:
        """
        Inquiry is a method to get user bills based on client number and product code
               :param req: InquiryRequest
               :return:  InquiryBaseResponse or ErrorResponse
               :raise ResponseGeneralException: if there are unexpected error when hitting SAT (403 forbidden, network error)
               :raise GeneralException: if there is an unexpected exception when inquiring
        """
        try:
            url = f"{self._config.sat_base_url}{INQUIRY_PATH}"

            body = generate_json_api_request(req.to_dict())
            http_req = requests.Request(method="POST", url=url, json=body)
            response = self._http_client.send_request(http_req)
            response.raise_for_status()

            json_response = response.json()
            data = parse_json_api_response(json_response)

            return InquiryResponse.from_dict(data).with_raw_response(response)
        except HTTPError as exc:
            return self._handle_http_error(exc)
        except Exception as exc:
            self._logger.error(f"Error when inquiry: {exc}")
            raise GeneralException(exc)

    def checkout(self, req: OrderRequest) -> Union[OrderDetail, ErrorResponse]:
        """
        Checkout is a method to do payment an order based on client number, product code and request id.
        Request ID should use unique identifier for each transaction
               :param req: OrderRequest
               :return: OrderDetail or ErrorResponse
               :raise ResponseGeneralException: if there are unexpected error when hitting SAT (403 forbidden, network error)
               :raise GeneralException: if there is an unexpected exception when checking out
        """
        try:
            url = f"{self._config.sat_base_url}{CHECKOUT_PATH}"

            body = generate_json_api_request(req.to_dict())
            body_str = json.dumps(body)
            signature = self.signature.sign(body_str)

            http_req = requests.Request(
                method="POST",
                url=url,
                json=body,
                headers={"signature": signature},
            )
            response = self._http_client.send_request(http_req)
            response.raise_for_status()

            json_response = response.json()
            data = parse_json_api_response(json_response)

            return OrderDetail.from_dict(data).with_raw_response(response)
        except HTTPError as exc:
            return self._handle_http_error(exc)
        except Exception as exc:
            self._logger.error(f"Error when checkout: {exc}")
            raise GeneralException(exc)

    def check_status(self, request_id: str) -> Union[OrderDetail, ErrorResponse]:
        """
        CheckStatus is a method to check the final status of an order.
        request id is must be filled
               :param request_id: request id to check the status
               :return: OrderDetail or ErrorResponse
               :raise ResponseGeneralException: if there are unexpected error when hitting SAT (403 forbidden, network error)
               :raise GeneralException: if there is an unexpected exception when checking status
        """
        try:
            url = f"{self._config.sat_base_url}{CHECK_STATUS_PATH.format(request_id=request_id)}"

            http_req = requests.Request(
                method="GET",
                url=url,
            )
            response = self._http_client.send_request(http_req)
            response.raise_for_status()

            json_response = response.json()
            data = parse_json_api_response(json_response)

            return OrderDetail.from_dict(data).with_raw_response(response)
        except HTTPError as exc:
            return self._handle_http_error(exc)
        except Exception as exc:
            self._logger.error(f"Error when check status: {exc}")
            raise GeneralException(exc)

    def list_product(
        self, code: Optional[str] = None
    ) -> Union[ProductListResponse, ErrorResponse]:
        """
        ListProduct is a method to get all the product list enabled on your credentials.
        you can also specify the product code, to get only one product detail.
        specify product code will be very beneficial to sync product status on your engine
        it will come with low bandwidth and fast response
               :param code: product code to filter the product list
               :return: ProductListResponse or ErrorResponse
               :raise ResponseGeneralException: if there are unexpected error when hitting SAT (403 forbidden, network error)
               :raise GeneralException: if there is an unexpected exception when listing product
        """
        try:
            url = f"{self._config.sat_base_url}{PRODUCT_LIST_PATH}"

            http_req = requests.Request(
                method="GET",
                url=url,
                params={"product_code": code},
            )
            response = self._http_client.send_request(http_req)
            response.raise_for_status()

            json_response = response.json()
            data = parse_json_api_list_response(json_response)
            products = [
                PartnerProduct.from_dict(item).with_raw_response(response)
                for item in data
            ]

            return ProductListResponse(products=products).with_raw_response(response)
        except HTTPError as exc:
            return self._handle_http_error(exc)
        except Exception as exc:
            self._logger.error(f"Error when list product: {exc}")
            raise GeneralException(exc)

    def account(self) -> Union[Account, ErrorResponse]:
        """
        Account is a method to check account balance
               :return: Account or ErrorResponse
               :raise ResponseGeneralException: if there are unexpected error when hitting SAT (403 forbidden, network error)
               :raise GeneralException: if there is an unexpected exception when checking account
        """

        try:
            url = f"{self._config.sat_base_url}{ACCOUNT_PATH}"

            http_req = requests.Request(
                method="GET",
                url=url,
            )
            response = self._http_client.send_request(http_req)
            response.raise_for_status()

            json_response = response.json()
            data = parse_json_api_response(json_response)

            return Account.from_dict(data).with_raw_response(response)
        except HTTPError as exc:
            return self._handle_http_error(exc)
        except Exception as exc:
            self._logger.error(f"Error when checking balance: {exc}")
            raise GeneralException(exc)

    def handle_callback(
        self,
        sat_response_data: Dict[str, Any],
        sat_response_headers: Dict[str, Any],
        do: Callable[[OrderDetail], None],
    ):
        """
        HandleCallback is method http.HandlerFunc to handle callback request from SAT
        you can customize the implementation based on this interface Callback
           :param sat_response_data: JSON API response data from SAT webhook, must be a dictionary
           :param sat_response_headers: HTTP headers from SAT webhook, must be a dictionary
           :param do: Your custom function to handle the callback, must be a function with OrderDetail as
                      parameter and return void
           :raise InvalidInputException: if the header does not contain the signature
           :raise UnauthenticatedException: if the signature is not valid
        """
        signature: Optional[str] = sat_response_headers.get(
            "signature"
        ) or sat_response_headers.get("Signature")
        if signature is None:
            raise InvalidInputException(
                "Signature is not present in the header, please check the request"
            )

        verify = self.signature.verify(json.dumps(sat_response_data), signature)
        if not verify:
            raise UnauthenticatedException("Signature is not valid")

        data = parse_json_api_response(sat_response_data)
        order_detail = OrderDetail.from_dict(data)

        do(order_detail)

    def get_http_client(self) -> HTTPClient:
        """
        GetHTTTPClient will return http client which already wrapped to support oauth2
        for custom integration to SAT Service
                :return: HTTPClient
        """
        return self._http_client

    def get_signature(self) -> Signature:
        """
        GetSignature will return signature object which already wrapped to support RSA signature
        for custom integration to SAT Service
                :return: Signature
        """
        return self.signature

    def _handle_http_error(self, exc: HTTPError):
        try:
            status = exc.response.status_code
            message = exc.response.text
            self._logger.debug(f"HTTP Error: {status}, {message}")

            data = exc.response.json()
            resp = ErrorResponse.from_dict(data).with_raw_response(exc.response)
            return resp
        except Exception as e:
            raise ResponseGeneralException(exc)

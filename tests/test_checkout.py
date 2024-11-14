"""
Test checkout endpoint

This example shows how to use the checkout endpoint to create an order in the SAT server.

For more information, please refer to "Checkout" section in the SAT documentation.
"""

import json

from conftest import TestUtil
from pytest_httpserver import HTTPServer
from pytest_httpserver.httpserver import HandlerType

from py_sat import SATClient
from py_sat.constant import CHECKOUT_PATH, SDK_LABEL
from py_sat.models import (ErrorObject, ErrorResponse, Field, OrderDetail,
                           OrderRequest)
from py_sat.utils import generate_json_api_request


def test_checkout(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    util: TestUtil,
):
    """
    Example of checkout endpoint success

    :param make_httpserver:
    :param sat_client:
    :param util:
    """
    random_string = "PYSAT" + util.generate_random_string(8)
    req = OrderRequest(
        id=random_string,
        product_code="pln-postpaid",
        client_number="2121212",
        amount=12500,
        fields=[
            Field(name="optional", value="optional"),
        ],
    )
    body = generate_json_api_request(req.to_dict())
    body_str = json.dumps(body)
    signature = sat_client.signature.sign(body_str)

    make_httpserver.expect_request(
        CHECKOUT_PATH,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
        json={
            "data": {
                "attributes": {
                    "amount": 12500,
                    "client_number": "2121212",
                    "fields": [{"name": "optional", "value": "optional"}],
                    "product_code": "pln-postpaid",
                },
                "id": random_string,
                "type": "order",
            }
        },
    ).respond_with_json(
        response_json={
            "data": {
                "type": "order",
                "id": random_string,
                "attributes": {
                    "client_number": "2121212",
                    "error_code": "",
                    "error_detail": "",
                    "fields": [{"name": "optional", "value": "optional"}],
                    "fulfilled_at": None,
                    "partner_fee": 1000,
                    "product_code": "pln-postpaid",
                    "sales_price": 12500,
                    "serial_number": "",
                    "status": "Pending",
                },
            }
        },
        status=200,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.checkout(req)

    assert response.to_json(indent=4)
    assert response.is_success()
    assert response.get_raw_response().status_code == 200
    assert response == OrderDetail(
        client_number="2121212",
        fields=[
            Field(name="optional", value="optional"),
        ],
        partner_fee=1000,
        product_code="pln-postpaid",
        sales_price=12500,
        status="Pending",
        id=random_string,
    )


def test_checkout_product_not_found(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    util: TestUtil,
):
    """
    Example of checkout endpoint product not found

    :param make_httpserver:
    :param sat_client:
    :param util:
    """
    random_string = "PYSAT" + util.generate_random_string(8)
    req = OrderRequest(
        id=random_string,
        product_code="non-exist-product",
        client_number="102111496000",
        amount=12500,
        fields=[
            Field(name="optional", value="optional"),
        ],
    )
    body = generate_json_api_request(req.to_dict())
    body_str = json.dumps(body)
    signature = sat_client.signature.sign(body_str)

    make_httpserver.expect_request(
        CHECKOUT_PATH,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
        json={
            "data": {
                "id": random_string,
                "type": "order",
                "attributes": {
                    "product_code": "non-exist-product",
                    "client_number": "102111496000",
                    "amount": 12500,
                    "fields": [{"name": "optional", "value": "optional"}],
                },
            }
        },
    ).respond_with_json(
        response_json={
            "errors": [{"code": "P04", "detail": "Product not found", "status": "400"}]
        },
        status=400,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.checkout(req)

    assert not response.is_success()
    assert response.get_raw_response().status_code == 400
    assert response == ErrorResponse(
        errors=[ErrorObject(code="P04", detail="Product not found", status="400")]
    )


def test_checkout_duplicate_request_id(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    util: TestUtil,
):
    """
    Example of checkout endpoint duplicate request id

    :param make_httpserver:
    :param sat_client:
    :param util:
    """
    random_string = "PYSAT" + util.generate_random_string(8)
    req = OrderRequest(
        id=random_string,
        product_code="pln-postpaid",
        client_number="2121212",
        amount=12500,
        fields=[
            Field(name="optional", value="optional"),
        ],
    )
    body = generate_json_api_request(req.to_dict())
    body_str = json.dumps(body)
    signature = sat_client.signature.sign(body_str)

    make_httpserver.expect_request(
        CHECKOUT_PATH,
        handler_type=HandlerType.ONESHOT,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
        json={
            "data": {
                "attributes": {
                    "amount": 12500,
                    "client_number": "2121212",
                    "fields": [{"name": "optional", "value": "optional"}],
                    "product_code": "pln-postpaid",
                },
                "id": random_string,
                "type": "order",
            }
        },
    ).respond_with_json(
        response_json={
            "data": {
                "type": "order",
                "id": random_string,
                "attributes": {
                    "client_number": "2121212",
                    "error_code": "",
                    "error_detail": "",
                    "fields": [{"name": "optional", "value": "optional"}],
                    "fulfilled_at": None,
                    "partner_fee": 1000,
                    "product_code": "pln-postpaid",
                    "sales_price": 12500,
                    "serial_number": "",
                    "status": "Pending",
                },
            }
        },
        status=200,
        headers={"Content-Type": "application/json"},
    )

    make_httpserver.expect_request(
        CHECKOUT_PATH,
        handler_type=HandlerType.ONESHOT,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
        json={
            "data": {
                "attributes": {
                    "amount": 12500,
                    "client_number": "2121212",
                    "fields": [{"name": "optional", "value": "optional"}],
                    "product_code": "pln-postpaid",
                },
                "id": random_string,
                "type": "order",
            }
        },
    ).respond_with_json(
        response_json={
            "errors": [
                {
                    "code": "P03",
                    "detail": "Duplicate Request ID, please check your system",
                    "status": "400",
                }
            ]
        },
        status=400,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.checkout(req)

    assert response.is_success()
    assert response.get_raw_response().status_code == 200
    assert response == OrderDetail(
        client_number="2121212",
        fields=[
            Field(name="optional", value="optional"),
        ],
        partner_fee=1000,
        product_code="pln-postpaid",
        sales_price=12500,
        status="Pending",
        id=random_string,
    )

    response = sat_client.checkout(req)

    assert not response.is_success()
    assert response.get_raw_response().status_code == 400
    assert response == ErrorResponse(
        errors=[
            ErrorObject(
                code="P03",
                detail="Duplicate Request ID, please check your system",
                status="400",
            )
        ]
    )

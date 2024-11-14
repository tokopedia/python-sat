"""
This module contains the tests for the check_status method in the SATClient class.

This example shows how to use the check_status method to check the status of a transaction from the SAT server.

For more information, please refer to "Check Status" section in the SAT documentation.
"""

import datetime
import json
import time

from conftest import TestUtil
from pytest_httpserver import HTTPServer

from py_sat import SATClient
from py_sat.constant import CHECK_STATUS_PATH, CHECKOUT_PATH, SDK_LABEL
from py_sat.models import (ErrorObject, ErrorResponse, Field, OrderDetail,
                           OrderRequest)
from py_sat.signature import Signature
from py_sat.utils import generate_json_api_request


def test_check_status_success(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    util: TestUtil,
    sat_signer: Signature,
):
    """
    Test check status success

    :param make_httpserver:
    :param sat_client:
    :param util:
    """
    random_string = "PYSAT" + util.generate_random_string(8)
    random_client_id = util.generate_client_number()

    req = OrderRequest(
        id=random_string,
        product_code="speedy-indihome",
        client_number=random_client_id,
        amount=3500,
    )
    body = generate_json_api_request(req.to_dict())

    make_httpserver.expect_request(
        CHECKOUT_PATH,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
        json={
            "data": {
                "type": "order",
                "id": random_string,
                "attributes": {
                    "product_code": "speedy-indihome",
                    "client_number": random_client_id,
                    "amount": 3500,
                },
            }
        },
    ).respond_with_json(
        response_json={
            "data": {
                "type": "order",
                "id": random_string,
                "attributes": {
                    "client_number": random_client_id,
                    "error_code": "",
                    "error_detail": "",
                    "fields": None,
                    "fulfilled_at": None,
                    "partner_fee": 2000,
                    "product_code": "speedy-indihome",
                    "sales_price": 3500,
                    "serial_number": "",
                    "status": "Pending",
                },
            }
        },
        status=200,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.checkout(req)

    assert response.is_success()
    assert response.to_json()
    assert response.to_dict()
    assert response.get_raw_response().status_code == 200
    assert response == OrderDetail(
        partner_fee=2000,
        product_code="speedy-indihome",
        client_number=random_client_id,
        sales_price=3500,
        status="Pending",
        id=random_string,
    )

    body = {
        "data": {
            "type": "order",
            "id": random_string,
            "attributes": {
                "admin_fee": 2500,
                "client_name": "Tokopedia User Default",
                "client_number": random_client_id,
                "error_code": "",
                "error_detail": "",
                "fields": None,
                "fulfilled_at": datetime.datetime.now(
                    tz=datetime.timezone.utc
                ).isoformat(),
                "fulfillment_result": [
                    {"name": "Nomor Referensi", "value": "174298636"},
                    {"name": "Nama Pelanggan", "value": "Tokopedia User Default"},
                    {"name": "Nomor Pelanggan", "value": "611981111"},
                    {"name": "Jumlah Tagihan", "value": "1"},
                    {"name": "Periode Bayar", "value": "Maret 2022"},
                    {"name": "Total Tagihan", "value": "Rp 1.000"},
                    {"name": "Biaya Admin", "value": "Rp 2.500"},
                    {"name": "Total Bayar", "value": "Rp 3.500"},
                ],
                "partner_fee": 2000,
                "product_code": "speedy-indihome",
                "sales_price": 3500,
                "serial_number": "174298636",
                "status": "Success",
                "voucher_code": "",
            },
        }
    }

    make_httpserver.expect_request(
        CHECK_STATUS_PATH.format(request_id=random_string),
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
    ).respond_with_data(
        response_data=json.dumps(body),
        status=200,
        headers={
            "Content-Type": "application/json",
            "signature": sat_signer.sign(json.dumps(body)),
        },
    )

    times = 1
    while True:
        time.sleep(1)
        response = sat_client.check_status(random_string)
        if response.status != "Pending" or times > 3:
            break

        times += 1

    assert response.is_success()
    assert response.to_json()
    assert response.to_dict()
    assert response.get_raw_response().status_code == 200
    assert response.product_code == "speedy-indihome"
    assert response.client_number == random_client_id
    assert response.status == "Success"
    assert response.id == random_string
    assert response.fulfilled_at is not None
    assert datetime.datetime.now(
        datetime.timezone.utc
    ) - response.fulfilled_at < datetime.timedelta(seconds=10)


def test_check_status_failed(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    sat_signer: Signature,
    util: TestUtil,
):
    """
    Test check status failed

    :param make_httpserver:
    :param sat_client:
    :param util:
    """
    random_string = "PYSAT" + util.generate_random_string(8)
    from py_sat.models import Field

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

    body = {
        "data": {
            "type": "order",
            "id": random_string,
            "attributes": {
                "client_number": "2121212",
                "error_code": "S02",
                "error_detail": "Product is not available",
                "fields": [{"name": "optional", "value": "optional"}],
                "fulfilled_at": None,
                "partner_fee": 1000,
                "product_code": "pln-postpaid",
                "sales_price": 12500,
                "serial_number": "",
                "status": "Failed",
            },
        }
    }
    make_httpserver.expect_request(
        CHECK_STATUS_PATH.format(request_id=random_string),
        method="GET",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
    ).respond_with_data(
        response_data=json.dumps(body),
        status=200,
        headers={
            "Content-Type": "application/json",
            "signature": sat_signer.sign(json.dumps(body)),
        },
    )

    times = 1
    while True:
        time.sleep(1)
        response = sat_client.check_status(random_string)
        if response.status != "Pending" or times > 3:
            break

        times += 1

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
        status="Failed",
        error_code="S02",
        error_detail="Product is not available",
        id=random_string,
    )


def test_check_status_not_found(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    util: TestUtil,
):
    """
    Test check status not found

    :param make_httpserver:
    :param sat_client:
    :param util:
    """
    random_string = "PYSAT" + util.generate_random_string(8)

    make_httpserver.expect_request(
        CHECK_STATUS_PATH.format(request_id=random_string),
        method="GET",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
    ).respond_with_json(
        response_json={
            "errors": [
                {"code": "P02", "detail": "Transaction is not found", "status": "400"}
            ]
        },
        status=400,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.check_status(random_string)

    assert not response.is_success()
    assert response.get_raw_response().status_code == 400
    assert response == ErrorResponse(
        errors=[
            ErrorObject(
                detail="Transaction is not found",
                status="400",
                code="P02",
            )
        ]
    )

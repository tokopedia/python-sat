"""
Test Inquiry API

This example shows how to use the inquiry endpoint to get the inquiry result from the SAT server.

For more information, please refer to "Inquiry" section in the SAT documentation.
"""

from conftest import TestEnvironment
from pytest_httpserver import HTTPServer
from pytest_httpserver.httpserver import HandlerType

from py_sat import SATClient
from py_sat.constant import INQUIRY_PATH, SDK_LABEL
from py_sat.models import (ErrorObject, ErrorResponse, InquiryRequest,
                           InquiryResponse)
from py_sat.models.inquiry import Field


def test_inquiry(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
):
    """
    Example of inquiry endpoint success

    :param make_httpserver:
    :param sat_client:
    """
    make_httpserver.expect_request(
        INQUIRY_PATH,
        method="POST",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
        json={
            "data": {
                "type": "inquiry",
                "attributes": {
                    "product_code": "pln-postpaid",
                    "client_number": "2121212",
                    "fields": [{"name": "optional", "value": "optional"}],
                },
            }
        },
        handler_type=HandlerType.ONESHOT,
    ).respond_with_json(
        response_json={
            "data": {
                "type": "inquiry",
                "id": "2121212",
                "attributes": {
                    "admin_fee": 2500,
                    "base_price": 25000,
                    "client_name": "TOKOPXXXX UXX",
                    "client_number": "2121212",
                    "fields": [{"name": "optional", "value": "optional"}],
                    "inquiry_result": [
                        {"name": "ID Pelanggan", "value": "2121212"},
                        {"name": "Nama", "value": "TOKOPXXXX UXX"},
                        {"name": "Total Bayar", "value": "Rp 27.500"},
                        {"name": "IDPEL", "value": "2121212"},
                        {"name": "NAMA", "value": "Tokopedia User Default"},
                        {"name": "TOTAL TAGIHAN", "value": "1 BULAN"},
                        {"name": "BL/TH", "value": "MAR20"},
                        {"name": "RP TAG PLN", "value": "Rp 25.000"},
                        {"name": "ADMIN BANK", "value": "Rp 2.500"},
                        {"name": "TOTAL BAYAR", "value": "Rp 27.500"},
                    ],
                    "meter_id": "2121212",
                    "product_code": "pln-postpaid",
                    "sales_price": 27500,
                },
            }
        },
        status=200,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.inquiry(
        req=InquiryRequest(
            product_code="pln-postpaid",
            client_number="2121212",
            fields=[Field(name="optional", value="optional")],
        )
    )

    assert response.is_success()
    assert response == InquiryResponse(
        id="2121212",
        product_code="pln-postpaid",
        sales_price=27500,
        fields=[Field(name="optional", value="optional")],
        inquiry_result=[
            Field(name="ID Pelanggan", value="2121212"),
            Field(name="Nama", value="TOKOPXXXX UXX"),
            Field(name="Total Bayar", value="Rp 27.500"),
            Field(name="IDPEL", value="2121212"),
            Field(name="NAMA", value="Tokopedia User Default"),
            Field(name="TOTAL TAGIHAN", value="1 BULAN"),
            Field(name="BL/TH", value="MAR20"),
            Field(name="RP TAG PLN", value="Rp 25.000"),
            Field(name="ADMIN BANK", value="Rp 2.500"),
            Field(name="TOTAL BAYAR", value="Rp 27.500"),
        ],
        base_price=25000,
        admin_fee=2500,
        client_name="TOKOPXXXX UXX",
        client_number="2121212",
        meter_id="2121212",
        ref_id="",
        max_payment=0,
        min_payment=0,
    )


def test_inquiry_product_not_found(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    env: TestEnvironment,
):
    """
    Example of inquiry endpoint product not found

    :param make_httpserver:
    :param sat_client:
    :param env:
    """
    make_httpserver.expect_request(
        INQUIRY_PATH,
        method="POST",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
        json={
            "data": {
                "type": "inquiry",
                "attributes": {
                    "product_code": "not-found-product",
                    "client_number": "2121212",
                },
            }
        },
        handler_type=HandlerType.ONESHOT,
    ).respond_with_json(
        response_json={
            "errors": [{"detail": "Product not found", "status": "400", "code": "P04"}]
        },
        status=400,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.inquiry(
        req=InquiryRequest(
            product_code="not-found-product",
            client_number="2121212",
        )
    )

    assert not response.is_success()
    assert response.get_raw_response().status_code == 400
    assert response == ErrorResponse(
        errors=[ErrorObject(detail="Product not found", status="400", code="P04")]
    )
    assert response.get_error_messages() == "400 - P04 - Product not found"
    assert response.get_error_codes() == "P04"
    assert response.get_error_statuses() == "400"


def test_inquiry_s00(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    env: TestEnvironment,
):
    """
    Example of inquiry endpoint internal server error

    :param make_httpserver:
    :param sat_client:
    :param env:
    """
    make_httpserver.expect_request(
        INQUIRY_PATH,
        method="POST",
        headers={
            "content-type": "application/json",
            "authorization": "Bearer testingToken",
            "X-Sat-Sdk-Version": SDK_LABEL,
        },
        json={
            "data": {
                "type": "inquiry",
                "attributes": {
                    "product_code": "speedy-indihome",
                    "client_number": "102111496000",
                },
            }
        },
        handler_type=HandlerType.ONESHOT,
    ).respond_with_json(
        response_json={
            "errors": [
                {"code": "S00", "detail": "Internal Server Error", "status": "500"}
            ]
        },
        status=500,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.inquiry(
        req=InquiryRequest(
            product_code="speedy-indihome",
            client_number="102111496000",
        )
    )

    assert not response.is_success()
    assert response.get_raw_response().status_code == 500
    assert response == ErrorResponse(
        errors=[ErrorObject(detail="Internal Server Error", status="500", code="S00")]
    )
    assert response.get_error_messages() == "500 - S00 - Internal Server Error"
    assert response.get_error_codes() == "S00"
    assert response.get_error_statuses() == "500"
    assert response.get_error_details() == "Internal Server Error"

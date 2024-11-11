"""
Example of using product list endpoint

This example shows how to use the product list endpoint to get a list of products available in the SAT server.

For more information, please refer to "Web Services Details" section in the SAT documentation.
"""

from pytest_httpserver import HTTPServer
from pytest_httpserver.httpserver import HandlerType

from py_sat import SATClient
from py_sat.constant import PRODUCT_LIST_PATH
from py_sat.models import ErrorObject, ErrorResponse, ProductStatus


def test_product_list_success(
    sat_client: SATClient,
    make_httpserver: HTTPServer,
):
    """
    Example of product list endpoint success

    :param sat_client:
    :param make_httpserver:
    """
    make_httpserver.expect_request(
        PRODUCT_LIST_PATH,
        method="GET",
        headers={
            "authorization": "Bearer testingToken",
        },
        handler_type=HandlerType.ONESHOT,
    ).respond_with_json(
        response_json={
            "data": [
                {
                    "attributes": {
                        "is_inquiry": False,
                        "price": 24913,
                        "product_name": "XL 25,000",
                        "status": 1,
                    },
                    "id": "25k-xl",
                    "type": "product",
                },
                {
                    "attributes": {
                        "is_inquiry": False,
                        "price": 25100,
                        "product_name": "Three 25,000",
                        "status": 1,
                    },
                    "id": "25k-three",
                    "type": "product",
                },
                {
                    "attributes": {
                        "is_inquiry": False,
                        "price": 0,
                        "product_name": "test-product",
                        "status": 1,
                    },
                    "id": "test-1",
                    "type": "product",
                },
                {
                    "attributes": {
                        "is_inquiry": False,
                        "price": 0,
                        "product_name": "",
                        "status": 1,
                    },
                    "id": "test2",
                    "type": "product",
                },
                {
                    "attributes": {
                        "is_inquiry": False,
                        "price": 0,
                        "product_name": "",
                        "status": 1,
                    },
                    "id": "test4",
                    "type": "product",
                },
                {
                    "attributes": {
                        "is_inquiry": True,
                        "price": 4797124,
                        "product_name": "Bank DBS KTA Bank DBS",
                        "status": 1,
                    },
                    "id": "kta-bank-dbs",
                    "type": "product",
                },
            ]
        },
        status=200,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.list_product()
    assert response.is_success()
    assert response.get_raw_response().status_code == 200
    assert len(response.products) > 3
    for product in response.products:
        assert product.id
        assert product.status == ProductStatus.Active


def test_product_list_one_item(
    sat_client: SATClient,
    make_httpserver: HTTPServer,
):
    """
    Example of product list endpoint with one item

    :param sat_client:
    :param make_httpserver:
    """
    make_httpserver.expect_request(
        PRODUCT_LIST_PATH,
        method="GET",
        headers={
            "authorization": "Bearer testingToken",
        },
        handler_type=HandlerType.ONESHOT,
    ).respond_with_json(
        response_json={
            "data": [
                {
                    "attributes": {
                        "is_inquiry": False,
                        "price": 24913,
                        "product_name": "XL 25,000",
                        "status": 1,
                    },
                    "id": "25k-xl",
                    "type": "product",
                }
            ]
        },
        status=200,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.list_product("25k-xl")
    assert response.is_success()
    assert response.get_raw_response().status_code == 200
    assert len(response.products) == 1
    for product in response.products:
        assert product.id
        assert product.status == ProductStatus.Active


def test_product_not_exists(
    sat_client: SATClient,
    make_httpserver: HTTPServer,
):
    """
    Example of product list endpoint with product not exists

    :param sat_client:
    :param make_httpserver:
    """
    make_httpserver.expect_request(
        PRODUCT_LIST_PATH,
        method="GET",
        headers={
            "authorization": "Bearer testingToken",
        },
        handler_type=HandlerType.ONESHOT,
    ).respond_with_json(
        response_json={
            "errors": [{"code": "P04", "detail": "Product not found", "status": "400"}]
        },
        status=400,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.list_product("not-exists-product")
    assert not response.is_success()
    assert response.get_raw_response().status_code == 400
    assert response == ErrorResponse(
        errors=[
            ErrorObject(
                code="P04",
                detail="Product not found",
                status="400",
            )
        ]
    )

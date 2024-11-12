"""
This file is used to test the callback mechanism from SAT

For partners that need the callback mechanism from SAT
follow these callback requirements below:
1. Your service should be using SSL (HTTPS)
2. Your service should whitelist our IP (52.74.35.225/32) to hit your service
3. Your service should allow method POST
4. Your service should allow Content-type application/vnd.api+json

For more detail, see "Callback for Partner" section in the documentation
"""

import json
import logging

import requests
from pytest_httpserver import HTTPServer
from werkzeug.wrappers import Request, Response

from py_sat import SATClient
from py_sat.models import OrderDetail
from py_sat.utils import parse_json_api_response


def test_callback(make_httpserver: HTTPServer, sat_client: SATClient):
    """
    Example of how to handle the callback from SAT using SAT Python SDK
    """
    make_httpserver.expect_request(
        "/callback",
        method="POST",
        headers={
            "content-type": "application/vnd.api+json",
        },
    ).respond_with_handler(create_handler(sat_client))

    # Simulate the callback from SAT
    body = {
        "data": {
            "type": "order",
            "id": "1231231",
            "attributes": {
                "admin_fee": 0,
                "client_name": "User",
                "client_number": "102111106111",
                "error_code": "",
                "error_detail": "",
                "fields": None,
                "fulfilled_at": "2020-12-09T10:48:45Z",
                "fulfillment_result": [],
                "partner_fee": 0,
                "product_code": "pln-prepaid-token-100k",
                "sales_price": 102500,
                "serial_number": "5196 15840828 2085 4701",
                "status": "Success",
                "voucher_code": "5196 1584 0828 2085 4701",
            },
        }
    }
    signature = sat_client.signature.sign(json.dumps(body))
    headers = {
        "content-type": "application/vnd.api+json",
        "signature": signature,
    }
    response = requests.post(
        make_httpserver.url_for("/callback"),
        json=body,
        headers=headers,
    )

    assert response.json() == {"message": "OK"}
    assert response.status_code == 200


def create_handler(sat_client: SATClient):
    def handler(request: Request) -> Response:
        try:
            data = request.json
            headers = dict(request.headers)

            def do_action(order_detail: OrderDetail):
                assert isinstance(order_detail, OrderDetail)
                assert order_detail.id == "1231231"
                assert order_detail.status == "Success"
                assert order_detail.product_code == "pln-prepaid-token-100k"
                assert order_detail.sales_price == 102500
                assert order_detail.client_name == "User"
                assert order_detail.client_number == "102111106111"

                # Do your action here
                # For example, update your database
                # or send a notification to the customer
                logging.info("Order detail: %s", order_detail)

            sat_client.handle_callback(
                sat_response_data=data,
                sat_response_headers=headers,
                do=do_action,
            )

            return Response(status=200, response=json.dumps({"message": "OK"}))
        except Exception as e:
            logging.exception("Error handling callback")
            return Response(
                status=500,
                response=json.dumps({"error": str(e)}),
            )

    return handler


def test_callback_signature(make_httpserver: HTTPServer, sat_client: SATClient):
    """
    Example of how to handle the callback from SAT without using SATClient handle_callback function
    but only using the signature verification
    """
    make_httpserver.expect_request(
        "/callback",
        method="POST",
        headers={
            "content-type": "application/vnd.api+json",
        },
    ).respond_with_handler(create_signature_only_handler(sat_client))

    # Simulate the callback from SAT
    body = {
        "data": {
            "type": "order",
            "id": "1231231",
            "attributes": {
                "admin_fee": 0,
                "client_name": "User",
                "client_number": "102111106111",
                "error_code": "",
                "error_detail": "",
                "fields": None,
                "fulfilled_at": "2020-12-09T10:48:45Z",
                "fulfillment_result": [],
                "partner_fee": 0,
                "product_code": "pln-prepaid-token-100k",
                "sales_price": 102500,
                "serial_number": "5196 15840828 2085 4701",
                "status": "Success",
                "voucher_code": "5196 1584 0828 2085 4701",
            },
        }
    }
    signature = sat_client.signature.sign(json.dumps(body))
    headers = {
        "content-type": "application/vnd.api+json",
        "signature": signature,
    }
    response = requests.post(
        make_httpserver.url_for("/callback"),
        json=body,
        headers=headers,
    )

    assert response.json() == {"message": "OK"}
    assert response.status_code == 200


def create_signature_only_handler(sat_client: SATClient):
    def handler(request: Request) -> Response:
        try:
            data = request.json
            headers = dict(request.headers)

            # Custom logic here
            logging.info("Data: %s", data)
            logging.info("Headers: %s", headers)

            # Do signature verification
            signature = headers.get("signature") or headers.get("Signature")
            if not signature:
                return Response(
                    status=400,
                    response=json.dumps({"error": "Signature is required"}),
                )

            if not sat_client.signature.verify(json.dumps(data), signature):
                return Response(
                    status=400,
                    response=json.dumps({"error": "Invalid signature"}),
                )

            input = parse_json_api_response(data)
            order_detail = OrderDetail.from_dict(input)
            assert isinstance(order_detail, OrderDetail)
            assert order_detail.id == "1231231"
            assert order_detail.status == "Success"
            assert order_detail.product_code == "pln-prepaid-token-100k"
            # Do your action here
            # For example, update your database
            # or send a notification to the customer
            logging.info("Order detail: %s", order_detail)

            return Response(status=200, response=json.dumps({"message": "OK"}))
        except Exception as e:
            logging.exception("Error handling callback")
            return Response(
                status=500,
                response=json.dumps({"error": str(e)}),
            )

    return handler

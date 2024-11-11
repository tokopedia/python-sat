"""
Test account endpoint

This example shows how to use the account endpoint to get the account balance from the SAT server.

For more information, please refer to "Account Balance" section in the SAT documentation.
"""

from pytest_httpserver import HTTPServer

from py_sat import SATClient
from py_sat.constant import ACCOUNT_PATH


def test_account_success(
    sat_client: SATClient,
    make_httpserver: HTTPServer,
):
    """
    Example of account endpoint success

    :param sat_client:
    :param make_httpserver:
    """
    make_httpserver.expect_request(
        ACCOUNT_PATH,
        method="GET",
        headers={
            "authorization": "Bearer testingToken",
        },
    ).respond_with_json(
        response_json={
            "data": {
                "type": "account",
                "id": "2203",
                "attributes": {
                    "saldo": 50000000,
                },
            }
        },
        status=200,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.account()
    assert response.is_success()
    assert response.get_raw_response().status_code == 200
    assert response.id == 2203
    assert response.saldo == 50000000

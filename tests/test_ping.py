"""
Test the ping method of the SATClient class.

This example shows how to use the ping method to get the ping result from the SAT server.

For more information, please refer to "Ping" section in the SAT documentation.
"""

from conftest import TestEnvironment
from pytest_httpserver import HTTPServer

from py_sat import SATClient
from py_sat.constant import PING_PATH


def test_ping(
    make_httpserver: HTTPServer,
    sat_client: SATClient,
    env: TestEnvironment,
):
    """
    Example of ping endpoint success

    :param make_httpserver:
    :param sat_client:
    :param env:
    """
    make_httpserver.expect_request(PING_PATH).respond_with_json(
        response_json={"buildhash": "b05b97a", "sandbox": True, "status": "ok"},
        status=200,
        headers={"Content-Type": "application/json"},
    )

    response = sat_client.ping()

    if env == TestEnvironment.LOCAL:
        assert response.buildhash == "b05b97a"
        assert response.sandbox is True
        assert response.status == "ok"

    if env == TestEnvironment.SANDBOX:
        assert response.sandbox is True
        assert response.status == "ok"

"""
Test cases for SATClient class.

This example shows how to use the SATClient class.
"""

import pytest
from conftest import TESTING_PRIVATE_KEY

from py_sat import SATClient, SATClientConfig
from py_sat.exceptions import InvalidInputException


def test_sat_client_required_param(sat_client: SATClient):
    """
    Test SATClient class with required parameters.
    :param sat_client:
    :return:
    """
    assert sat_client is not None
    assert isinstance(sat_client, SATClient)


def test_sat_client_error_input():
    """
    Test SATClient class with error input.
    :return:
    """
    with pytest.raises(InvalidInputException):
        config = SATClientConfig(
            client_id="client_id",
            client_secret="client_secret",
            private_key=None,
        )
        http_client = SATClient(config)


def test_sat_client_error_padding_input():
    """
    Test SATClient class with error padding input.
    :return:
    """
    with pytest.raises(InvalidInputException):
        config = SATClientConfig(
            client_id="client_id",
            client_secret="client_secret",
            private_key=TESTING_PRIVATE_KEY,
        ).with_padding_type("test")
        http_client = SATClient(config)


def test_sat_client_invalid_private_key():
    """
    Test SATClient class with invalid private key.
    :return:
    """
    with pytest.raises(InvalidInputException) as exc_info:
        config = SATClientConfig(
            client_id="client_id",
            client_secret="client_secret",
            private_key="invalid_private_key",
        )
        _ = SATClient(config)

    assert "Invalid RSA private key" in str(exc_info.value)


def test_sat_client_invalid_public_key():
    """
    Test SATClient class with invalid public key.
    :return:
    """
    with pytest.raises(InvalidInputException) as exc_info:
        config = SATClientConfig(
            client_id="client_id",
            client_secret="client_secret",
            private_key=TESTING_PRIVATE_KEY,
        ).with_public_key("invalid_public_key")
        _ = SATClient(config)

    assert "Invalid RSA public key" in str(exc_info.value)

"""
Test signature module.

This example shows how to use the signature module to sign and verify a message.

For more information, please refer to "Signature" section in the SAT documentation.
"""

import pytest

from py_sat import SATClient, SATClientConfig


@pytest.mark.parametrize(
    "test_input, test_message, verified",
    [
        ("Hello, World!", "signature", False),
        ("Hello, World!", "Hello, World! ", False),
        (
            '{"test_message": "Hello, World!!"}',
            '{"test_message": "Hello, World!!"}',
            True,
        ),
        (
            '{"test_message": "Hello, World!!"}',
            '{"test_message": "Hello, Not World!!"}',
            False,
        ),
    ],
)
def test_signature(test_input, test_message, verified, sat_client: SATClient):
    """
    Test signature module.

    :param test_input:
    :param test_message:
    :param verified:
    :param sat_client:
    """
    signature = sat_client.signature.sign(test_input)
    assert signature

    is_verified = sat_client.signature.verify(test_message, signature)
    assert verified == is_verified

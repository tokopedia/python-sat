"""
Test signature module.

This example shows how to use the signature module to sign and verify a message.

For more information, please refer to "Signature" section in the SAT documentation.
"""

import pytest
from conftest import TESTING_CLIENT_PRIVATE_KEY, TESTING_CLIENT_PUBLIC_KEY

from py_sat.signature import Signature, SignatureType


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
def test_signature(test_input, test_message, verified):
    """
    Test signature module.

    :param test_input:
    :param test_message:
    :param verified:
    :param sat_client:
    """
    signature = Signature(
        private_key_str=TESTING_CLIENT_PRIVATE_KEY,
        sat_public_key_str=TESTING_CLIENT_PUBLIC_KEY,
        padding_type=SignatureType.PSS,
    )

    sig = signature.sign(test_input)
    assert sig

    is_verified = signature.verify(test_message, sig)
    assert verified == is_verified

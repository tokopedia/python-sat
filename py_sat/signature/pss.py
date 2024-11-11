import base64
from typing import Union

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pss

from py_sat.signature.interface import SignatureAlgorithm


class PSSPaddingAlgorithm(SignatureAlgorithm):
    def verify(
        self, public_key: RSA, msg: Union[str, bytes], signature_base64: str
    ) -> bool:
        """Verifies a PKCS1v15 signature using SHA-256.

        Args:
            public_key: The RSA public key used for verification.
            msg: The message (either a string or bytes) to verify.
            signature_base64: The base64-encoded signature to verify.

        Returns:
            True if the signature is valid, False otherwise.
        """

        if not signature_base64.strip():
            raise ValueError("Signature is empty")

        if isinstance(msg, str):
            msg = msg.encode("utf-8")

        try:
            signature_bytes = base64.b64decode(signature_base64)
        except ValueError:
            raise ValueError("Invalid base64 signature")

        hash_message = SHA256.new(msg)
        salt = int(public_key.n.bit_length() / 8) - hash_message.digest_size - 2
        verifier = pss.new(public_key, salt_bytes=salt)

        try:
            verifier.verify(hash_message, signature_bytes)
            return True
        except (ValueError, TypeError):
            return False

    def sign(self, private_key: RSA, msg: Union[str, bytes]) -> str:
        """Signs a message using PSS padding and RSA algorithm.

        Args:
            private_key: The RSA private key used for signing.
            msg: The message (either a string or bytes) to sign.

        Returns:
            The base64-encoded signature as a string.
        """
        if isinstance(msg, str):
            msg = msg.encode("utf-8")

        hash = SHA256.new(msg)
        salt = int(private_key.n.bit_length() / 8) - hash.digest_size - 2
        signature = pss.new(private_key, salt_bytes=salt).sign(hash)

        base64_signature = base64.b64encode(signature)
        encoded_signature = str(base64_signature, "utf-8")
        return encoded_signature

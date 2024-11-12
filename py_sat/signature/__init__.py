from enum import Enum
from typing import Optional

from Crypto.PublicKey import RSA

from py_sat.exceptions import InvalidInputException, SignatureErrorException
from py_sat.signature.interface import SignatureAlgorithm
from py_sat.signature.pss import PSSPaddingAlgorithm


class SignatureType(Enum):
    PSS = "PSS"


class Signature:
    """
    Signature to hold that signature needs, and contain parsed public and private key
    """

    _private_key: Optional[RSA.RsaKey]
    _public_key: Optional[RSA.RsaKey]
    _algorithm: SignatureAlgorithm

    def __init__(
        self,
        private_key_str: Optional[str],
        public_key_str: Optional[str],
        padding_type: SignatureType,
    ):
        if not padding_type:
            raise InvalidInputException("Padding type is required")

        self._private_key = self._parse_rsa_private_key_from_pem_str(private_key_str)
        self._public_key = self._parse_public_key(public_key_str)
        self._algorithm = self.__decide_padding_algorithm(padding_type)

    def verify(self, msg: str, signature: str) -> bool:
        """
        Verify the signature of the message, return True if the signature is valid, False otherwise

        :param msg: message to verify, must be a string
        :param signature: signature to verify, must be a string
        :return: True if the signature is valid, False otherwise
        :raise InvalidInputException: if the message or signature is not a string or public key is not set
        :raise SignatureErrorException: if there is an error verifying the signature
        """
        if not isinstance(msg, str) or not isinstance(signature, str):
            raise InvalidInputException("Message and signature must be strings")

        if not self._public_key:
            raise InvalidInputException("Public key not set")

        try:
            return self._algorithm.verify(self._public_key, msg, signature)
        except Exception as exc:
            raise SignatureErrorException(f"Error verifying signature: {exc}")

    def sign(self, msg: str) -> str:
        """
        Sign the message and return the signature

        :param msg: to sign, must be a string
        :return: the signature as a string
        :raises InvalidInputException: if the message is not a string or private key is not set
        :raises SignatureErrorException: if there is an error signing the message
        """
        if not isinstance(msg, str):
            raise InvalidInputException("Message must be a string")

        if not self._private_key:
            raise InvalidInputException("Private key not set")

        try:
            return self._algorithm.sign(self._private_key, msg)
        except Exception as exc:
            raise SignatureErrorException(f"Error signing message: {exc}")

    @staticmethod
    def __decide_padding_algorithm(padding_type: SignatureType) -> SignatureAlgorithm:
        if padding_type == SignatureType.PSS:
            return PSSPaddingAlgorithm()
        else:
            raise InvalidInputException(f"Unknown padding type: {padding_type}")

    @staticmethod
    def _parse_rsa_private_key_from_pem_str(
        private_key_pem: Optional[str],
    ) -> Optional[RSA.RsaKey]:
        try:
            """Parses an RSA private key from a PEM-encoded string."""
            if not private_key_pem:
                return None

            private_key = RSA.import_key(private_key_pem.encode())
            if not isinstance(private_key, RSA.RsaKey):
                raise InvalidInputException("Key is not a valid RSA public key")

            return private_key
        except (ValueError, IndexError, TypeError) as exc:
            raise InvalidInputException(f"Invalid RSA private key PEM: {exc}")

    @staticmethod
    def _parse_public_key(public_key_pem: Optional[str]) -> Optional[RSA.RsaKey]:
        """Parses an RSA public key from a PEM-encoded string."""
        try:
            if not public_key_pem:
                return None

            public_key = RSA.import_key(public_key_pem.encode())

            if not isinstance(public_key, RSA.RsaKey):
                raise InvalidInputException("Key is not a valid RSA public key")
            return public_key
        except (ValueError, IndexError, TypeError) as exc:
            raise InvalidInputException(f"Invalid RSA public key PEM: {exc}")

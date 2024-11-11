from abc import ABC, abstractmethod
from typing import Union

from Crypto.PublicKey import RSA


class SignatureAlgorithm(ABC):
    @abstractmethod
    def verify(
        self, public_key: RSA.RsaKey, msg: Union[str, bytes], signature: str
    ) -> bool:
        """Verifies a signature"""
        pass

    @abstractmethod
    def sign(self, private_key: RSA.RsaKey, msg: Union[str, bytes]) -> str:
        """Signs a message"""
        pass

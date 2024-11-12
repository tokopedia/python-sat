import enum
import os
import random
import string

import pytest
from pytest_httpserver import HTTPServer

from py_sat import SATClient, SATClientConfig
from py_sat.constant import ACCESS_TOKEN_URL, PLAYGROUND_SAT_BASE_URL

TESTING_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDyR0kXD0bu1nl8
nZP+GLI8bSVFbk5yKTu99LlLevTTFLx6sIXfabgKPHIpwr0xGf99yobD1ZNZ276x
ffnMAeILNA5XsvaMnPpVB4kNoqlDaQdd4ICelKQwt90QD9CIGptNLL2wtUgEn1g9
BV6k5xcT8L9Dw/ZqpMCnfBeGRsWJd84LBfN4lLe5k9MXxE4MLUfTC1xxLmO9C9xw
d92aucyRPkv8n+B9dOlYS8C29huTbregl2rEF32dMyYG1qmVH7ufjM4CX9KdNKA7
hwnJExqrPvhAtj92Ar0Z5JnPfm8SUjQQhFeySeqSHS+kVEsd/AhrsqMsdUSt9ou2
xJTJmiL9AgMBAAECggEANHOO5Q1jZassn3gs9T6K/c6CWmr0VD5NhwUfhXIP5U/Q
sz4aqYDFfX/TFmvo0iPG/oh1TxninfpXKS11Aj/pHFRPg5iEzHHitzxbpUZRHz0y
gVYsekiDWGHB2+uUkZazBwz33zUL66ZEr+dE823tPt2oxsa6xyE2bTwOCr2xH96S
eE6280gJ1LtgGKD4TFsmXSkgJIDyF2rT6ZkPeUR36N0zWiSRQbskLaTqwJSpT6mY
hdZRQBvH/6X2JJgOmWWVizE1ChdOVB7rN3tb7NBSbwf5TWNGsNdhQQoTPxAtGiX8
O+jXilCIjLSqudIDv20jCa8spFuXwpIeBhR/7394GQKBgQD6+g4yZSybGMnMgNM6
OrL1GnJbxtnuMENMi7e2NgeLxKmpWE3cPqTNe9uWNxXYexDgDLNtAfjw7+UZxO6f
e3cPXuyVsr2xTkEscLBNDXrwQV3phnfwpxX++8Flv0xP34TocWAIKXPcQj8h2SYr
6/zhY40YnRsUgsR0x4eAlqJHBQKBgQD3IKl15jjzHEyqVvWuAjsw3LO8rA96i7vg
WDV5LBrsJgE11M7iurwZxZ71STPVzWK5UzxsZBCJgK41NIvgVx6QIuU0HXw9taXY
7PrAwNcpx7yKksXPYsTGhKumLvFQBY/R9qP2RcFN5WQjTSBxp0B5QMDHNz01dPi6
l0TfjKO9mQKBgQCZRRJcdmsaQLYkfNwCaIyXoNIL+FFo4/KFkaHc1fwfwDd4ouPR
yDPvBV/hybw+m1F/8mG1BYpY4bhA14J+xPC941OKTEEKQecNU7hnJf9ZMCJBFgyz
W+bT9D10fLIG6VMKfQqPkXkfHxnc+vcTxaeGobwuNuutx/pf8uZugg+SXQKBgQC3
qjOnpxHeRMMJuhVfXNMm7nA6odnjJuTbyFL9mnTr2xb9LgsQYN4ZfVE1VVFL7hgY
Si9XE0tjFhri+gmXEshpMTYNdHh42H7I6N830FpY99Q9XPXcurgqHkIAAVVhNrD7
yAV1q8QNo5W30sNxFG+Lbj+YD4rTJvsQmgoa5shuyQKBgQCDJuBgjNgyHqWrKEEt
76OJDiXI4mXDg3N6oCjsP/ZsP7mhkmUsokDS1paSnQxtt0tbft+fpbQSFtDGkRKr
OM5SBQhJEa//gFAofgYt+Fo6wcj1NSgBeLspsYx/avRdj9drVGyxOKJX0zsWQemU
Gf6bGumDG6hy0wu4aWDjSvTmww==
-----END PRIVATE KEY-----
"""

TESTING_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8kdJFw9G7tZ5fJ2T/hiy
PG0lRW5Ocik7vfS5S3r00xS8erCF32m4CjxyKcK9MRn/fcqGw9WTWdu+sX35zAHi
CzQOV7L2jJz6VQeJDaKpQ2kHXeCAnpSkMLfdEA/QiBqbTSy9sLVIBJ9YPQVepOcX
E/C/Q8P2aqTAp3wXhkbFiXfOCwXzeJS3uZPTF8RODC1H0wtccS5jvQvccHfdmrnM
kT5L/J/gfXTpWEvAtvYbk263oJdqxBd9nTMmBtaplR+7n4zOAl/SnTSgO4cJyRMa
qz74QLY/dgK9GeSZz35vElI0EIRXsknqkh0vpFRLHfwIa7KjLHVErfaLtsSUyZoi
/QIDAQAB
-----END PUBLIC KEY-----
"""


class TestEnvironment(str, enum.Enum):
    __test__ = False
    LOCAL = "local"
    SANDBOX = "sandbox"


@pytest.fixture(scope="session")
def env():
    env = os.getenv("PY_SAT_TEST_ENV", "local")
    return TestEnvironment[env.upper()]


def __construct_local_test_config(make_httpserver: HTTPServer):
    base_url = make_httpserver.url_for("")
    base_url_without_trailing_slash = base_url[:-1]

    access_token_base_url = make_httpserver.url_for("token")

    config = (
        SATClientConfig(
            client_id="client_id",
            client_secret="client_secret",
            private_key=TESTING_PRIVATE_KEY,
        )
        .with_timeout(15)
        .with_public_key(TESTING_PUBLIC_KEY)
        .with_sat_base_url(base_url_without_trailing_slash)
        .with_access_token_base_url(access_token_base_url)
        .with_is_debug(True)
    )
    # Allow insecure transport for testing
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    make_httpserver.expect_request("/token", method="POST").respond_with_json(
        response_json={
            "access_token": "testingToken",
            "token_type": "bearer",
            "expires_in": 3600,
        }
    )
    return config


def __construct_sandbox_test_config():
    client_id = os.getenv("PY_SAT_TEST_CLIENT_ID")
    client_secret = os.getenv("PY_SAT_TEST_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("Missing client id or client secret for sandbox testing")

    private_key = os.getenv("PY_SAT_TEST_PRIVATE_KEY")
    private_key = bytes(private_key, "utf-8").decode("unicode_escape")
    public_key = os.getenv("PY_SAT_TEST_PUBLIC_KEY")
    public_key = bytes(public_key, "utf-8").decode("unicode_escape")
    if not private_key or not public_key:
        raise ValueError("Missing private key or public key for sandbox testing")

    config = (
        SATClientConfig(
            client_id=client_id,
            client_secret=client_secret,
            private_key=private_key,
        )
        .with_timeout(10)
        .with_public_key(public_key)
        .with_is_debug(True)
    )

    return config


@pytest.fixture(scope="session")
def sat_config(make_httpserver: HTTPServer, env: TestEnvironment):
    if env == TestEnvironment.LOCAL:
        return __construct_local_test_config(make_httpserver)
    elif env == TestEnvironment.SANDBOX:
        return __construct_sandbox_test_config()
    else:
        raise ValueError(f"Invalid environment: {env}")


@pytest.fixture(scope="session")
def sat_client(sat_config: SATClientConfig):
    sat_client = SATClient(sat_config)

    return sat_client


class TestUtil:
    @staticmethod
    def generate_random_string(length: int) -> str:
        return "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
        )

    @staticmethod
    def generate_random_number(length: int) -> str:
        return "".join(random.choice(string.digits) for _ in range(length))

    @staticmethod
    def generate_client_number() -> str:
        return TestUtil.generate_random_number(5) + "1111"


@pytest.fixture(scope="session")
def util():
    return TestUtil()

import enum
import logging
import os
import random
import string

import pytest
from pytest_httpserver import HTTPServer

from py_sat import SATClient, SATClientConfig
from py_sat.constant import ACCESS_TOKEN_URL, PLAYGROUND_SAT_BASE_URL
from py_sat.signature import Signature, SignatureType

TESTING_CLIENT_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCmoG7sJRcmHmDK
wQoPn94VLAvxZtxV2cqG/xEGW+LdREqMzbGHhTrKWMp3MODC2gyoyJ9GVMNG8qxX
R8j+d2BqlI3vIP79fyLG56eGudqRkphhD4RNZiybuK8W0QZGmt86MMrZvubjUgWu
lyX7gFWyjGwAZIFVZSrJe0YdiafgH9VKLrDOTRyqgbJ6Eo3v9VP/Px2AwOCH7HIe
R3XI5ubPcxuzMeKREAlFdrF/b/18vShBaCaAZinQdS7DdcyNu5RwEe2kR8Yga/0X
pklsnYUefes2Yf7W+RjgseSbPINkLUFLAwiS3VGO+bzKCMqGlL1WXuyw2d66KEcM
rTN78TY1AgMBAAECggEAMldWK9Io5ENZSuh3ebD7D7p3AT/qYaWjIpX9NsacC+2N
+GxMrnz5/hhFUy1ZOoVWPcgfFsiVFuJKXzQ47WhzoL+xAgYeA8hdYWqrmnCcME7x
6qEdf6TW5VUu0N3l33764kHLh229pAAr50uTFiD3wzHZj2TODla6TpUH4fSs23FF
2phan8enc4mFHKXUng+e36pjFkdhaVI5kzmtOIzUYukT9KuiEVc6H3eG/aTOukXj
6203BODN/Zfs2gj75cxi9ta3N3UuzcRXrZls2W5exfQERBYpuIkknjejy5EYw7QZ
r0w9nXaRJ3HEcey1J48LeVIquFWeYjNcwQykIt+VIQKBgQDPrCcmzv8DyQQTiZHE
0S9PcISiwZWzwjlyAsk2yBLs/8KLs8sQcrkoJ5vn7AZgUudqBjv6yvjiJqnQlQL1
2C6D6N4wEl66DOYVb9fDaxsr0kUrpIF52CPEeTfnw9Q4+yo/p11yTbPz691sae4k
IZwwg1XtSotF+mQ9fths2gmaXwKBgQDNZwaKaMdVCdFKdRFe18NDw+CcdS5ipwkf
sBYU+uff9MCBi8Rx9rUQMjW54/BVFOGpUgRRH/duXlB0zuc6pHsOn+a1Ai7jSPU7
uPZq3oG5vv9qwJkTIYzb6VXCdoeTRPQlR7hzs3jSO73uepGCCKc2JEL42da7m9n6
mjmpKPEf6wKBgQCFWUOildQGODNX4EQrny7D0bo5UBiyXorIfKV7eak9aVUgo4hG
vYPLFvPzTgkiHNnfqLUm6uI5RR5Rgv1toyzrIsJZF9KfoNy08yYWo1XFI7Wqum0x
Mep1pGiTd5l0JUMRsIQ+e0qL2+5ISRTTOomyVQL95Znci1WGb0bFTpRP/QKBgBrB
leeHuJeKPNofH9Ej+AqmxGZ9GTq+mYCoNmgrOvNAdacqZr+VrIZclAUP/SmIG9Er
nuZWbKvS21Yr8ZEBBgqkp6/ihesTgOZztJ29OFbS24Czb/0+/JNU9NftCsITVF5a
1ls0AMQaBia/jp7Ks8VoudSiw8cSiTWMy4AOlkJbAoGADIta0IWTIHmpbAYq0M8w
MnaKTiinUhhZe+Q5PVZeZjdzt+nt71xk5DmJkSZa8v6FFu18ddRf8CzylFUCFRPp
wC6by4FSjc2APGAKVvZA070W/pxUqG6RjAeZyiLZxOCg5CvGzW+7ZnWFziuBFP20
CJC5sJrsitvtv5BG64biA88=
-----END PRIVATE KEY-----

"""

TESTING_CLIENT_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApqBu7CUXJh5gysEKD5/e
FSwL8WbcVdnKhv8RBlvi3URKjM2xh4U6yljKdzDgwtoMqMifRlTDRvKsV0fI/ndg
apSN7yD+/X8ixuenhrnakZKYYQ+ETWYsm7ivFtEGRprfOjDK2b7m41IFrpcl+4BV
soxsAGSBVWUqyXtGHYmn4B/VSi6wzk0cqoGyehKN7/VT/z8dgMDgh+xyHkd1yObm
z3MbszHikRAJRXaxf2/9fL0oQWgmgGYp0HUuw3XMjbuUcBHtpEfGIGv9F6ZJbJ2F
Hn3rNmH+1vkY4LHkmzyDZC1BSwMIkt1Rjvm8ygjKhpS9Vl7ssNneuihHDK0ze/E2
NQIDAQAB
-----END PUBLIC KEY-----
"""

TESTING_SAT_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCutVhWwBYr32Y5
ZQw4k6E/dctBKN4F3FETS9QsRbbVKJlX/UHnm4O9K+D9WO4cOUSyaznUfCNL38zY
u90n7kAr/wFA9a75lvnn1m2D95K5EJzh4RtjIwhCozB7kl2gdjUTgZpn1u0IlG0e
Ofwnb/UBiJJ0E+uvAcHrfz5pgsvhHoD1PLeB5o73bpB71BSI4Uay1NoSeZob1vC9
s4AjmvmZEXtQ8m91aZhvySkjupkbshGheoMwJz6stwdCecVk7G/EeeI8zSH7e5GA
p99I/FgfDY1tzX2l8whziqzmmocO+x7sUXeWB8FzLbhIust7Evt+i5H1sLub/9Jh
5+gN+7UtAgMBAAECggEABHN6ITFHcodNPbtNbbTHkzjUKVntS8Ptst3bNX3yZwlG
Qt+6cDhEY0TwOGdg7AopFGY3KBE5/i+UMsj/UCQGflIPltD+y/AYEagjMsBtFgoo
A3jU1eVC5OoiDMi3wIqFo3R8jRaEna1xmQ2lvXfhcgN02I0+k3JdhCHCFgKvLavE
KoEMPIOYWynXlMSWvAwsNNW/SxrC3NCitHl9Rp3lOcVP/kOWlgIZTrSJeFBGFCni
9zyeu0/Pzwys5VKGPQkED1Is6cEFxr89ZRJ4SzSVMogYxLzZf0KP5yxmGadXIb4X
CMOqfdUdFhRpzgsTOn/+rzXfG1cbtOTP40cxY/nclwKBgQDmljw4C//0AvOhyaA6
CqfhlqOcBKhGZUg2UOFziFhXCdXjYPlOf0NDW8e5tE7OGWBxBGGty/hhjLmNMDpF
mVVzI6dbY8/64eBrp+IBP87O3xxh/07i2TY7M8fBAnsK1aSUC/FFNcWcspK55IOS
CkgpSwUkn5WYDoClkjGm4OoKGwKBgQDB9o6+LLdDrPymgtS7l+OWmdiSkma6XXp0
xRKqknbNuXtxHsEVEHouYRqZXFtIETYtrkF72Nab7GpX1cZxZ5XmJU01fbI0baOH
MDuL3/vvtkLAcGCrzTQnB0Mpw23CAMJgbcyKRnA2sSKrd4GubaVGcsrGYiOv3ysB
MW0kAPsyVwKBgB1yF/SMS74sVlJVvhlLXQ7ovrHgwmBi9KrC/1dSlP1gayjjLFMC
22MRqFqllN6qzO8BwTuBbZF/d/54pyhWIVxXtDpub5O5HoCA6tKABHfUc/prsPY1
CMDcpuiV2YKTr7WcJM5SxI5zG1uTu919ZKOpSdnYazEEwRbjqWWHGTv7AoGAFz9l
Bng3kv313kNKGh3vYkqYQaEYfPfdSIeiYB1j7e5wVDOactrhuhNba8w9CJs/giQj
pyNrPY8Ng++UdF01AzuvUFz7cfs+IWLvkClNegK/Z29QtubGfHMLYsMQsbMDmSkv
3dbpdjSu8hxFx9FOgO4bTcHPgzHdZqw0557SfMsCgYB7oKwXz899tx5+c+D4LXgV
cSdlE/anH8RG6fc0HN8CYuWLnZRtiVKEePhomkql0j16xiQXpypFa01OykXaDQT3
gkQ02Ye6HHcsfaZdw3Nzp30OyrR9Do9/LHfviesR7larEVvSpMPscbmIJc20lACE
m44DCWLirq3PJ1tHkSvhdQ==
-----END PRIVATE KEY-----
"""

TESTING_SAT_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArrVYVsAWK99mOWUMOJOh
P3XLQSjeBdxRE0vULEW21SiZV/1B55uDvSvg/VjuHDlEsms51HwjS9/M2LvdJ+5A
K/8BQPWu+Zb559Ztg/eSuRCc4eEbYyMIQqMwe5JdoHY1E4GaZ9btCJRtHjn8J2/1
AYiSdBPrrwHB638+aYLL4R6A9Ty3geaO926Qe9QUiOFGstTaEnmaG9bwvbOAI5r5
mRF7UPJvdWmYb8kpI7qZG7IRoXqDMCc+rLcHQnnFZOxvxHniPM0h+3uRgKffSPxY
Hw2Nbc19pfMIc4qs5pqHDvse7FF3lgfBcy24SLrLexL7fouR9bC7m//SYefoDfu1
LQIDAQAB
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


@pytest.fixture(scope="session")
def local_config(make_httpserver: HTTPServer):
    base_url = make_httpserver.url_for("")
    base_url_without_trailing_slash = base_url[:-1]

    access_token_base_url = make_httpserver.url_for("token")

    config = (
        SATClientConfig(
            client_id="client_id",
            client_secret="client_secret",
            private_key=TESTING_CLIENT_PRIVATE_KEY,
            sat_public_key=TESTING_SAT_PUBLIC_KEY,
        )
        .with_timeout(15)
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


@pytest.fixture(scope="session")
def sandbox_config():
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
            sat_public_key=public_key,
        )
        .with_timeout(10)
        .with_is_debug(True)
    )

    return config


@pytest.fixture(scope="session")
def sat_config(
    local_config: SATClientConfig, sandbox_config: SATClientConfig, env: TestEnvironment
):
    if env == TestEnvironment.LOCAL:
        logging.info("Using local test config")
        return local_config
    elif env == TestEnvironment.SANDBOX:
        logging.info("Using sandbox test config")
        return sandbox_config
    else:
        raise ValueError(f"Invalid environment: {env}")


@pytest.fixture(scope="session")
def sat_client(sat_config: SATClientConfig):
    sat_client = SATClient(sat_config)

    return sat_client


@pytest.fixture(scope="session")
def sat_signer():
    return Signature(
        padding_type=SignatureType.PSS,
        private_key_str=TESTING_SAT_PRIVATE_KEY,
        sat_public_key_str=TESTING_SAT_PUBLIC_KEY,
    )


@pytest.fixture(scope="session")
def client_signer():
    return Signature(
        padding_type=SignatureType.PSS,
        private_key_str=TESTING_CLIENT_PRIVATE_KEY,
        sat_public_key_str=TESTING_CLIENT_PUBLIC_KEY,
    )


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

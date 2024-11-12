from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import dateutil.parser
import requests
from dataclasses_json import (DataClassJsonMixin, Undefined, config,
                              dataclass_json)


class BaseResponse(DataClassJsonMixin):
    _raw_response: requests.Response

    def get_raw_response(self) -> requests.Response:
        return self._raw_response

    def with_raw_response(self, raw_response: requests.Response):
        self._raw_response = raw_response
        return self

    def is_success(self):
        return 200 <= self._raw_response.status_code < 300


class BaseRequest(DataClassJsonMixin):
    pass


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Field:
    name: str
    value: str


def datetime_encoder(input: Optional[datetime]) -> str:
    if input is None:
        return None

    return input.isoformat()


def datetime_decoder(input: Optional[str]) -> Optional[datetime]:
    if input is None:
        return None

    return dateutil.parser.isoparse(input)


datetime_config = config(
    encoder=datetime_encoder,
    decoder=datetime_decoder,
)

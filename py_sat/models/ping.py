from dataclasses import dataclass

from dataclasses_json import Undefined, dataclass_json

from py_sat.models.base import BaseResponse


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class PingResponse(BaseResponse):
    buildhash: str
    sandbox: bool
    status: str

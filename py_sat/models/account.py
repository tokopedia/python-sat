from dataclasses import dataclass, field

from dataclasses_json import Undefined, dataclass_json

from py_sat.models.base import BaseResponse


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Account(BaseResponse):
    """
    Account is a schema related with account entity
    """

    id: int
    saldo: int

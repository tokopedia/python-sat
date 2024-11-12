from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from dataclasses_json import Undefined, config, dataclass_json

from py_sat.models.base import (BaseRequest, BaseResponse, Field,
                                datetime_config)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class OrderRequest(BaseRequest):
    id: str = field(default="")
    product_code: str = field(default="")
    client_number: str = field(default="")
    amount: float = field(default=0.0)
    fields: Optional[List[Field]] = field(default=None)
    downline_id: Optional[str] = field(default=None)

    type: str = field(default="order", init=False)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class OrderDetail(BaseResponse):
    id: str = field(default="")
    fields: Optional[List[Field]] = field(default=None)
    fulfillment_result: List[Field] = field(default_factory=list)
    fulfilled_at: Optional[datetime] = field(
        default=None,
        metadata=datetime_config,
    )
    error_code: str = field(default="")
    error_detail: str = field(default="")
    product_code: str = field(default="")
    status: str = field(default="")
    partner_fee: int = field(default=0)
    sales_price: int = field(default=0)
    admin_fee: int = field(default=0)
    client_name: str = field(default="")
    client_number: str = field(default="")
    voucher_code: str = field(default="")
    serial_number: str = field(default="")

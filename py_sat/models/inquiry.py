from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import Undefined, dataclass_json

from py_sat.models.base import BaseRequest, BaseResponse, Field


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class InquiryRequest(BaseRequest):
    """
    InquiryRequest to hold inquiry request data
    """

    product_code: str
    client_number: str
    amount: Optional[int] = field(default=None)
    id: Optional[str] = field(default=None)
    fields: Optional[List[Field]] = field(default=None)

    type: str = field(default="inquiry", init=False)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class InquiryResponse(BaseResponse):
    """
    InquiryResponse to hold inquiry response
    """

    id: str = field(default="")
    product_code: str = field(default="")
    sales_price: float = field(default=0.0)
    fields: List[Field] = field(default_factory=list)
    inquiry_result: List[Field] = field(default_factory=list)
    base_price: float = field(default=0.0)
    admin_fee: float = field(default=0.0)
    client_name: str = field(default="")
    client_number: str = field(default="")
    meter_id: str = field(default="")
    ref_id: str = field(default="")
    max_payment: int = field(default=0)
    min_payment: int = field(default=0)

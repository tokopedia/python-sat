import enum
from dataclasses import dataclass, field
from typing import List

from dataclasses_json import Undefined, dataclass_json

from py_sat.models.base import BaseResponse


class ProductStatus(enum.Enum):
    Active = 1
    Inactive = 2


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class PartnerProduct(BaseResponse):
    id: str = field(default="")
    name: str = field(default="")
    operator_name: str = field(default="")
    category_name: str = field(default="")
    is_inquiry: bool = field(default=False)
    sales_price: int = field(default=0)
    status: ProductStatus = field(default=ProductStatus.Active)
    client_number: str = field(default="")


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class ProductListResponse(BaseResponse):
    products: List[PartnerProduct] = field(default_factory=list)

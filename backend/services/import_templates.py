"""Excel import template definitions.

A template declares how to map an Excel sheet (Chinese headers, free-text
cells) into rows targeted at a SQLAlchemy business model. Each column
describes its parse type, whether it is required, and an optional dictionary
lookup that resolves a human-readable cell value (e.g. plate number) into
a foreign-key id (e.g. vehicle_id).
"""
from dataclasses import dataclass, field
from typing import Any

from models.business import DeliveryRecord
from models.dict import DictPerson, DictRoute, DictVehicle


@dataclass(frozen=True)
class Lookup:
    """Resolve a cell value into an FK id via a dictionary table."""
    model: Any              # SQLAlchemy model class
    by: str                 # dict field to match against (e.g. "plate_number")
    out_field: str          # target field name on the business row (e.g. "vehicle_id")
    require_active: bool = True


@dataclass(frozen=True)
class ImportColumn:
    header: str             # Chinese header expected in the Excel sheet
    field: str              # raw parsed field name
    type: str = "str"       # "str" | "int" | "float" | "date"
    required: bool = False
    lookup: Lookup | None = None
    warn_min: float | None = None
    warn_max: float | None = None


@dataclass(frozen=True)
class ImportTemplate:
    key: str
    name: str
    description: str
    model: Any              # target SQLAlchemy model
    columns: list[ImportColumn] = field(default_factory=list)


# ── Templates ──

DELIVERY_RECORD = ImportTemplate(
    key="delivery_record",
    name="送货流水",
    description="每日送货流水（按行登记日期/车辆/线路/驾驶员/送货员/客户与送货数量）",
    model=DeliveryRecord,
    columns=[
        ImportColumn(header="日期", field="record_date", type="date", required=True),
        ImportColumn(
            header="车牌号", field="plate_number", type="str", required=True,
            lookup=Lookup(model=DictVehicle, by="plate_number", out_field="vehicle_id"),
        ),
        ImportColumn(
            header="驾驶员", field="driver_name", type="str", required=True,
            lookup=Lookup(model=DictPerson, by="name", out_field="driver_id"),
        ),
        ImportColumn(
            header="送货员", field="deliverer_name", type="str", required=False,
            lookup=Lookup(model=DictPerson, by="name", out_field="deliverer_id"),
        ),
        ImportColumn(
            header="线路编码", field="route_code", type="str", required=True,
            lookup=Lookup(model=DictRoute, by="route_code", out_field="route_id"),
        ),
        ImportColumn(header="客户数", field="customer_count", type="int", warn_max=200),
        ImportColumn(header="送货数", field="delivery_count", type="int", warn_max=500),
        ImportColumn(header="备注", field="remark", type="str"),
    ],
)


TEMPLATES: dict[str, ImportTemplate] = {
    DELIVERY_RECORD.key: DELIVERY_RECORD,
}


def get_template(key: str) -> ImportTemplate | None:
    return TEMPLATES.get(key)

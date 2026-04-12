from datetime import date, datetime
from pydantic import BaseModel


# ── Person ──

class PersonCreate(BaseModel):
    name: str
    id_card: str
    birth_date: date | None = None
    join_date: date | None = None
    position: str | None = None
    department: str | None = None
    employment_type: str | None = None
    school: str | None = None
    degree: str | None = None
    extra: dict | None = None


class PersonUpdate(BaseModel):
    name: str | None = None
    id_card: str | None = None
    birth_date: date | None = None
    join_date: date | None = None
    position: str | None = None
    department: str | None = None
    employment_type: str | None = None
    school: str | None = None
    degree: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class PersonOut(BaseModel):
    id: int
    name: str
    id_card: str
    birth_date: date | None = None
    join_date: date | None = None
    position: str | None = None
    department: str | None = None
    employment_type: str | None = None
    school: str | None = None
    degree: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Vehicle ──

class VehicleCreate(BaseModel):
    plate_number: str
    model: str | None = None
    driver_id: int | None = None
    cargo_size: str | None = None
    vehicle_type: str | None = None
    tank_or_battery_size: float | None = None
    mileage: float | None = None
    status: str | None = "在用"
    extra: dict | None = None


class VehicleUpdate(BaseModel):
    plate_number: str | None = None
    model: str | None = None
    driver_id: int | None = None
    cargo_size: str | None = None
    vehicle_type: str | None = None
    tank_or_battery_size: float | None = None
    mileage: float | None = None
    status: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class VehicleOut(BaseModel):
    id: int
    plate_number: str
    model: str | None = None
    driver_id: int | None = None
    cargo_size: str | None = None
    vehicle_type: str | None = None
    tank_or_battery_size: float | None = None
    mileage: float | None = None
    status: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Route ──

class RouteCreate(BaseModel):
    route_code: str
    route_name: str
    driver_id: int | None = None
    deliverer_id: int | None = None
    customer_count: int | None = None
    delivery_count: int | None = None
    delivery_time: str | None = None
    settlement_time: str | None = None
    response_time_calc: str | None = None
    toll_fee: float | None = None
    delivery_cycle: str | None = None
    extra: dict | None = None


class RouteUpdate(BaseModel):
    route_code: str | None = None
    route_name: str | None = None
    driver_id: int | None = None
    deliverer_id: int | None = None
    customer_count: int | None = None
    delivery_count: int | None = None
    delivery_time: str | None = None
    settlement_time: str | None = None
    response_time_calc: str | None = None
    toll_fee: float | None = None
    delivery_cycle: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class RouteOut(BaseModel):
    id: int
    route_code: str
    route_name: str
    driver_id: int | None = None
    deliverer_id: int | None = None
    customer_count: int | None = None
    delivery_count: int | None = None
    delivery_time: str | None = None
    settlement_time: str | None = None
    response_time_calc: str | None = None
    toll_fee: float | None = None
    delivery_cycle: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Customer ──

class CustomerCreate(BaseModel):
    customer_code: str
    customer_name: str
    address: str | None = None
    phone: str | None = None
    settlement_method: str | None = None
    department: str | None = None
    route_id: int | None = None
    delivery_zone: str | None = None
    delivery_order: int | None = None
    market_type: str | None = None
    extra: dict | None = None


class CustomerUpdate(BaseModel):
    customer_code: str | None = None
    customer_name: str | None = None
    address: str | None = None
    phone: str | None = None
    settlement_method: str | None = None
    department: str | None = None
    route_id: int | None = None
    delivery_zone: str | None = None
    delivery_order: int | None = None
    market_type: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class CustomerOut(BaseModel):
    id: int
    customer_code: str
    customer_name: str
    address: str | None = None
    phone: str | None = None
    settlement_method: str | None = None
    department: str | None = None
    route_id: int | None = None
    delivery_zone: str | None = None
    delivery_order: int | None = None
    market_type: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Cigarette ──

class CigaretteCreate(BaseModel):
    product_code: str
    product_name: str
    brand_owner: str | None = None
    price_category: str | None = None
    extra: dict | None = None


class CigaretteUpdate(BaseModel):
    product_code: str | None = None
    product_name: str | None = None
    brand_owner: str | None = None
    price_category: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class CigaretteOut(BaseModel):
    id: int
    product_code: str
    product_name: str
    brand_owner: str | None = None
    price_category: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Options (for foreign key dropdowns) ──

class OptionItem(BaseModel):
    id: int
    label: str

    model_config = {"from_attributes": True}

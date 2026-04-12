from sqlalchemy import String, Date, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.base import DictBase


class DictPerson(DictBase, Base):
    __tablename__ = "dict_person"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    id_card: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    birth_date: Mapped[str | None] = mapped_column(Date)
    join_date: Mapped[str | None] = mapped_column(Date)
    position: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(50))
    employment_type: Mapped[str | None] = mapped_column(String(30))
    school: Mapped[str | None] = mapped_column(String(100))
    degree: Mapped[str | None] = mapped_column(String(30))


class DictVehicle(DictBase, Base):
    __tablename__ = "dict_vehicle"

    plate_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    model: Mapped[str | None] = mapped_column(String(50))
    driver_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_person.id"))
    cargo_size: Mapped[str | None] = mapped_column(String(30))
    vehicle_type: Mapped[str | None] = mapped_column(String(20))
    tank_or_battery_size: Mapped[float | None] = mapped_column(Numeric(10, 2))
    mileage: Mapped[float | None] = mapped_column(Numeric(12, 2))
    status: Mapped[str | None] = mapped_column(String(20), default="在用")


class DictRoute(DictBase, Base):
    __tablename__ = "dict_route"

    route_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    route_name: Mapped[str] = mapped_column(String(100), nullable=False)
    driver_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_person.id"))
    deliverer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_person.id"))
    customer_count: Mapped[int | None] = mapped_column(Integer)
    delivery_count: Mapped[int | None] = mapped_column(Integer)
    delivery_time: Mapped[str | None] = mapped_column(String(50))
    settlement_time: Mapped[str | None] = mapped_column(String(50))
    response_time_calc: Mapped[str | None] = mapped_column(String(100))
    toll_fee: Mapped[float | None] = mapped_column(Numeric(10, 2))
    delivery_cycle: Mapped[str | None] = mapped_column(String(30))


class DictCustomer(DictBase, Base):
    __tablename__ = "dict_customer"

    customer_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(20))
    settlement_method: Mapped[str | None] = mapped_column(String(30))
    department: Mapped[str | None] = mapped_column(String(50))
    route_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_route.id"))
    delivery_zone: Mapped[str | None] = mapped_column(String(50))
    delivery_order: Mapped[int | None] = mapped_column(Integer)
    market_type: Mapped[str | None] = mapped_column(String(30))


class DictCigarette(DictBase, Base):
    __tablename__ = "dict_cigarette"

    product_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand_owner: Mapped[str | None] = mapped_column(String(100))
    price_category: Mapped[str | None] = mapped_column(String(30))

from fastapi import APIRouter

from models.dict import DictPerson, DictVehicle, DictRoute, DictCustomer, DictCigarette
from schemas.dict import (
    PersonCreate, PersonUpdate, PersonOut,
    VehicleCreate, VehicleUpdate, VehicleOut,
    RouteCreate, RouteUpdate, RouteOut,
    CustomerCreate, CustomerUpdate, CustomerOut,
    CigaretteCreate, CigaretteUpdate, CigaretteOut,
)
from services.crud_factory import create_crud_router

person_router = create_crud_router(
    model=DictPerson,
    create_schema=PersonCreate,
    update_schema=PersonUpdate,
    out_schema=PersonOut,
    prefix="person",
    tag="人员管理",
    search_fields=["name", "id_card", "department", "position"],
    label_field="name",
)

vehicle_router = create_crud_router(
    model=DictVehicle,
    create_schema=VehicleCreate,
    update_schema=VehicleUpdate,
    out_schema=VehicleOut,
    prefix="vehicle",
    tag="车辆管理",
    search_fields=["plate_number", "model"],
    label_field="plate_number",
)

route_router = create_crud_router(
    model=DictRoute,
    create_schema=RouteCreate,
    update_schema=RouteUpdate,
    out_schema=RouteOut,
    prefix="route",
    tag="线路管理",
    search_fields=["route_code", "route_name"],
    label_field="route_name",
)

customer_router = create_crud_router(
    model=DictCustomer,
    create_schema=CustomerCreate,
    update_schema=CustomerUpdate,
    out_schema=CustomerOut,
    prefix="customer",
    tag="零售客户",
    search_fields=["customer_code", "customer_name", "address"],
    label_field="customer_name",
)

cigarette_router = create_crud_router(
    model=DictCigarette,
    create_schema=CigaretteCreate,
    update_schema=CigaretteUpdate,
    out_schema=CigaretteOut,
    prefix="cigarette",
    tag="卷烟品牌",
    search_fields=["product_code", "product_name", "brand_owner"],
    label_field="product_name",
)

router = APIRouter()
router.include_router(person_router)
router.include_router(vehicle_router)
router.include_router(route_router)
router.include_router(customer_router)
router.include_router(cigarette_router)

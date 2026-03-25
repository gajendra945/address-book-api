from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import Address
from app.logger import get_logger
from app.schemas.address import AddressCreate, AddressUpdate
from app.utils import calculate_distance

logger = get_logger(__name__)


class AddressNotFoundError(Exception):
    """Raised when an address record cannot be found."""


@dataclass(slots=True)
class NearbyAddressMatch:
    """Service-layer result for nearby address searches."""

    address: Address
    distance: float


def create_address(db: Session, payload: AddressCreate) -> Address:
    address = Address(**payload.model_dump())
    try:
        db.add(address)
        db.commit()
        db.refresh(address)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating an address")
        raise
    return address


def list_addresses(db: Session, skip: int, limit: int) -> list[Address]:
    return db.query(Address).offset(skip).limit(limit).all()


def get_address_by_id(db: Session, address_id: int) -> Address:
    address = db.get(Address, address_id)
    if address is None:
        raise AddressNotFoundError(f"Address {address_id} not found")
    return address


def update_address(db: Session, address_id: int, payload: AddressUpdate) -> Address:
    address = get_address_by_id(db, address_id)
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(address, field, value)

    try:
        db.commit()
        db.refresh(address)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while updating address %s", address_id)
        raise
    return address


def delete_address(db: Session, address_id: int) -> None:
    address = get_address_by_id(db, address_id)
    try:
        db.delete(address)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while deleting address %s", address_id)
        raise


def find_nearby_addresses(
    db: Session,
    latitude: float,
    longitude: float,
    distance: float,
    unit: str,
) -> list[NearbyAddressMatch]:
    addresses = db.query(Address).all()
    matches: list[NearbyAddressMatch] = []

    for address in addresses:
        try:
            distance_value = calculate_distance(
                latitude,
                longitude,
                address.latitude,
                address.longitude,
                unit,
            )
        except ValueError:
            logger.warning(
                "Skipping address %s during nearby search because stored coordinates are invalid",
                address.id,
            )
            continue

        if distance_value <= distance:
            matches.append(
                NearbyAddressMatch(address=address, distance=round(distance_value, 2))
            )

    matches.sort(key=lambda match: match.distance)
    return matches

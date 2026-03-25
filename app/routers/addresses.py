from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.logger import get_logger
from app.schemas.address import AddressCreate, AddressRead, AddressUpdate, NearbyAddressRead
from app.services import addresses as address_service
from app.services.addresses import AddressNotFoundError
from config import settings

logger = get_logger(__name__)
router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/addresses", tags=["Addresses"])
DbSession = Annotated[Session, Depends(get_db)]


class DistanceUnit(str, Enum):
    KM = "km"
    MILES = "miles"


@router.post("/", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
def create_address(payload: AddressCreate, db: DbSession) -> AddressRead:
    logger.info(
        "Create address request received for street=%s city=%s country=%s",
        payload.street,
        payload.city,
        payload.country,
    )
    try:
        address = address_service.create_address(db, payload)
    except SQLAlchemyError as exc:
        logger.exception("Failed to create address for street=%s city=%s", payload.street, payload.city)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create address.",
        ) from exc

    logger.info("Address %s created successfully", address.id)
    return AddressRead.model_validate(address)


@router.get("/", response_model=list[AddressRead])
def list_addresses(
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1, le=settings.MAX_PAGE_LIMIT),
) -> list[AddressRead]:
    logger.info("List addresses request received with skip=%s limit=%s", skip, limit)
    try:
        addresses = address_service.list_addresses(db, skip, limit)
    except SQLAlchemyError as exc:
        logger.exception("Failed to list addresses")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve addresses.",
        ) from exc

    logger.info("Returning %s addresses", len(addresses))
    return [AddressRead.model_validate(address) for address in addresses]


@router.get("/nearby", response_model=list[NearbyAddressRead])
def list_nearby_addresses(
    db: DbSession,
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    distance: float = Query(..., gt=0),
    unit: DistanceUnit = Query(DistanceUnit.KM),
) -> list[NearbyAddressRead]:
    logger.info(
        "Nearby search request received for latitude=%s longitude=%s distance=%s unit=%s",
        latitude,
        longitude,
        distance,
        unit.value,
    )
    try:
        matches = address_service.find_nearby_addresses(
            db=db,
            latitude=latitude,
            longitude=longitude,
            distance=distance,
            unit=unit.value,
        )
    except SQLAlchemyError as exc:
        logger.exception("Failed to search nearby addresses")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search nearby addresses.",
        ) from exc

    logger.info("Nearby search returned %s matching addresses", len(matches))
    return [
        NearbyAddressRead(
            **AddressRead.model_validate(match.address).model_dump(),
            distance=match.distance,
        )
        for match in matches
    ]


@router.get("/{address_id}", response_model=AddressRead)
def get_address(address_id: int, db: DbSession) -> AddressRead:
    logger.info("Fetch address request received for address %s", address_id)
    try:
        address = address_service.get_address_by_id(db, address_id)
    except AddressNotFoundError:
        logger.warning("Address %s not found", address_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
    except SQLAlchemyError as exc:
        logger.exception("Failed to retrieve address %s", address_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve address from the database.",
        ) from exc

    logger.info("Returning address %s", address.id)
    return AddressRead.model_validate(address)


@router.put("/{address_id}", response_model=AddressRead)
def update_address(address_id: int, payload: AddressUpdate, db: DbSession) -> AddressRead:
    logger.info("Update request received for address %s", address_id)
    logger.info("Applying %s field updates to address %s", len(payload.model_fields_set), address_id)
    try:
        address = address_service.update_address(db, address_id, payload)
    except AddressNotFoundError:
        logger.warning("Address %s not found for update", address_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
    except SQLAlchemyError as exc:
        logger.exception("Failed to update address %s", address_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update address.",
        ) from exc

    logger.info("Address %s updated successfully", address.id)
    return AddressRead.model_validate(address)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db: DbSession) -> Response:
    logger.info("Delete request received for address %s", address_id)
    try:
        address_service.delete_address(db, address_id)
    except AddressNotFoundError:
        logger.warning("Address %s not found for deletion", address_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")
    except SQLAlchemyError as exc:
        logger.exception("Failed to delete address %s", address_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete address.",
        ) from exc

    logger.info("Address %s deleted successfully", address_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

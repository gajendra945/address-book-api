# Address Book API Interview Notes

## Project Summary

This is a FastAPI-based Address Book API.

It stores addresses in SQLite and supports:

- create address
- list addresses
- get one address
- update address
- delete address
- search nearby addresses using latitude, longitude, distance, and unit

## Main Goal

The assignment was to build a minimal API with FastAPI where users can manage addresses and search addresses near a location.

## Tech Stack

- Python 3
- FastAPI
- SQLAlchemy ORM
- SQLite
- Pydantic
- Geopy
- Uvicorn
- Pytest
- Docker

## Why These Technologies

- FastAPI: simple, fast, automatic Swagger docs
- SQLAlchemy ORM: cleaner and safer than raw SQL
- SQLite: easy setup and required by assignment
- Pydantic: request validation and response schemas
- Geopy: reliable geodesic distance calculation
- Pytest: automated testing
- Docker: easy local setup and reproducibility

## Project Structure

```text
app/
|-- database/
|   |-- models.py
|   `-- session.py
|-- routers/
|   `-- addresses.py
|-- schemas/
|   `-- address.py
|-- services/
|   `-- addresses.py
|-- logger.py
`-- utils.py
```

## What Each Part Does

- `main.py`: app startup, middleware, health routes, router registration
- `routers`: API endpoints and HTTP responses
- `services`: business logic and database operations
- `schemas`: request validation and response models
- `database/models.py`: ORM model
- `database/session.py`: DB connection and session dependency
- `config.py`: environment-based settings
- `logger.py`: logging setup
- `utils.py`: distance calculation helper

## API Endpoints

- `GET /` -> welcome message
- `GET /health` -> health check
- `POST /api/v1/addresses/` -> create address
- `GET /api/v1/addresses/` -> list addresses
- `GET /api/v1/addresses/{address_id}` -> get one address
- `PUT /api/v1/addresses/{address_id}` -> update address
- `DELETE /api/v1/addresses/{address_id}` -> delete address
- `GET /api/v1/addresses/nearby` -> search nearby addresses

## Important Input Fields

Required on create:

- `street`
- `city`
- `country`
- `latitude`
- `longitude`

Optional on create:

- `name`
- `state`
- `postal_code`

Important behavior:

- if `name` is missing, it is auto-generated from street and city

## Validation

Validation happens at the API boundary using Pydantic.

Examples:

- latitude must be between `-90` and `90`
- longitude must be between `-180` and `180`
- blank required strings are rejected
- empty update payloads are rejected
- invalid query params return `422`

## Error Handling

- `422` for invalid input
- `404` if address is not found
- `500` for database or unexpected server errors
- database session rolls back on failure

## Logging

The app logs:

- startup and shutdown
- request start and completion
- create, update, and delete operations
- validation problems
- not-found cases
- database errors

## Nearby Search Logic

The nearby endpoint:

1. gets all saved addresses
2. calculates geodesic distance using `geopy`
3. filters addresses within the requested radius
4. sorts results by nearest first

This is fine for a small assignment project. For large-scale production, geospatial DB support would be better.

## Testing

Tests cover:

- create
- list
- get by ID
- update
- delete
- nearby search
- validation failures
- not-found behavior

## Configuration

Settings come from `.env`.

Examples:

- `APP_HOST`
- `APP_PORT`
- `API_V1_PREFIX`
- `DATABASE_URL`
- `LOG_LEVEL`

## Docker

The project includes:

- `Dockerfile`
- `.dockerignore`

This makes the app easier to run in a clean environment.

## Good Points To Say In Interview

- I used SQLAlchemy ORM instead of raw SQL for cleaner and safer DB access.
- I kept validation in request schemas so bad data is rejected early.
- I separated routers, services, schemas, and models to keep the project readable.
- I used `geopy` instead of a custom formula for distance calculation.
- I added logging, tests, Docker support, and environment-based configuration to make the project more professional.

## Short Answer: Explain The Project

"This project is a FastAPI Address Book API that stores addresses with coordinates in SQLite. It supports full CRUD operations and nearby search based on latitude and longitude. I used SQLAlchemy ORM for database access, Pydantic for validation, geopy for distance calculation, and pytest for testing."

## Short Answer: Explain The Structure

"Routers handle HTTP requests, services contain business logic, schemas validate input and shape responses, models define the database structure, and config manages environment-based settings."

## Short Answer: What Would You Improve Next

- add authentication
- use PostgreSQL/PostGIS for large-scale geospatial search
- add CI pipeline
- add filtering, sorting, and pagination metadata
- add linting and static type checks

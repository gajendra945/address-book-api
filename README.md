# Address Book API

A minimal FastAPI project for creating, reading, updating, deleting, and searching addresses by distance. The API stores data in SQLite, validates request data with Pydantic, calculates geodesic distance with `geopy`, and exposes interactive documentation through FastAPI Swagger UI.

## Features

- Full CRUD for address records
- Nearby-address search using latitude, longitude, distance, and unit
- SQLite persistence with SQLAlchemy
- Boundary validation with Pydantic
- Request and error logging for key application events
- Clear module separation for routes, services, models, schemas, and configuration
- Docker support for quick, reproducible local runs
- Swagger UI and ReDoc out of the box

## Tech Stack

- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Geopy
- Uvicorn
- Pytest

## Quick Start

Use these exact commands after cloning the repository.

### Windows PowerShell

```powershell
git clone https://github.com/gajendra945/address-book-api.git
cd address-book-api
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

### macOS / Linux

```bash
git clone https://github.com/gajendra945/address-book-api.git
cd address-book-api
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

The API will be available at:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Run With Docker

If you prefer containerized setup, use these exact commands:

```bash
docker build -t address-book-api .
docker run --rm -p 8000:8000 address-book-api
```

The container uses environment-driven settings from `config.py`. By default it starts the app on `0.0.0.0:8000`.

## Run Tests

Install the development dependencies first:

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

### macOS / Linux

```bash
source venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Configuration

The repository includes a ready-to-use `.env` file for local execution. You can edit it if you want to change the host, port, database path, or pagination defaults.

Current values:

```env
APP_HOST=127.0.0.1
APP_PORT=8000
API_V1_PREFIX=/api/v1
DATABASE_URL=sqlite:///./address_book.db
DEBUG=true
LOG_LEVEL=INFO
DEFAULT_PAGE_LIMIT=20
MAX_PAGE_LIMIT=100
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Welcome message |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/addresses/` | Create an address |
| `GET` | `/api/v1/addresses/` | List addresses |
| `GET` | `/api/v1/addresses/{address_id}` | Get one address |
| `PUT` | `/api/v1/addresses/{address_id}` | Update an address |
| `DELETE` | `/api/v1/addresses/{address_id}` | Delete an address |
| `GET` | `/api/v1/addresses/nearby` | Find nearby addresses |

## Example Request

```json
{
  "street": "123 Main Street",
  "city": "Springfield",
  "country": "United States",
  "latitude": 39.7817,
  "longitude": -89.6501
}
```

Optional create fields:

- `name`
- `state`
- `postal_code`

## Project Structure

```text
address-book-api/
|-- app/
|   |-- database/
|   |   |-- models.py
|   |   `-- session.py
|   |-- routers/
|   |   `-- addresses.py
|   |-- schemas/
|   |   `-- address.py
|   |-- services/
|   |   `-- addresses.py
|   |-- logger.py
|   `-- utils.py
|-- tests/
|   |-- conftest.py
|   `-- test_addresses.py
|-- .env
|-- .dockerignore
|-- Dockerfile
|-- config.py
|-- main.py
|-- requirements.txt
|-- requirements-dev.txt
`-- README.md
```

## Notes

- `requirements.txt` contains only runtime dependencies.
- `requirements-dev.txt` contains test-only tooling layered on top of the runtime set.
- `config.py` centralizes environment-driven values such as host, port, API prefix, pagination limits, logging level, and database URL.
- `.gitignore` and `.dockerignore` keep caches, local databases, and editor files out of version control and Docker build context.
- `.env` is committed intentionally in this recruiter-focused project because it contains only safe local defaults and removes setup friction.
- SQLite tables are created automatically on startup.
- Swagger UI is sufficient for exploring the API; no separate GUI is required.

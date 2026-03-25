ADDRESS_PAYLOAD = {
    "name": "Home",
    "street": "123 Main Street",
    "city": "Springfield",
    "state": "Illinois",
    "postal_code": "62701",
    "country": "United States",
    "latitude": 39.7817,
    "longitude": -89.6501,
}


def test_create_address(client):
    response = client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == 1
    assert payload["name"] == ADDRESS_PAYLOAD["name"]
    assert "created_at" in payload
    assert "updated_at" in payload


def test_create_address_with_minimal_required_fields(client):
    response = client.post(
        "/api/v1/addresses/",
        json={
            "street": "456 Oak Avenue",
            "city": "Boston",
            "country": "United States",
            "latitude": 42.3601,
            "longitude": -71.0589,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "456 Oak Avenue, Boston"
    assert payload["state"] is None
    assert payload["postal_code"] is None


def test_list_addresses(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    office_payload = ADDRESS_PAYLOAD.copy()
    office_payload["name"] = "Office"
    office_payload["latitude"] = 39.7820
    office_payload["longitude"] = -89.6499
    client.post("/api/v1/addresses/", json=office_payload)

    response = client.get("/api/v1/addresses/?skip=0&limit=10")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["name"] == "Home"
    assert payload[1]["name"] == "Office"


def test_get_address(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    response = client.get("/api/v1/addresses/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_update_address(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    response = client.put(
        "/api/v1/addresses/1",
        json={"name": "Home Updated", "city": "Chicago"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Home Updated"
    assert payload["city"] == "Chicago"


def test_optional_update_fields_can_be_cleared(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    response = client.put("/api/v1/addresses/1", json={"state": None, "postal_code": None})

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] is None
    assert payload["postal_code"] is None


def test_delete_address(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    delete_response = client.delete("/api/v1/addresses/1")
    get_response = client.get("/api/v1/addresses/1")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_nearby_search_filters_and_sorts_results(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    nearby_payload = ADDRESS_PAYLOAD.copy()
    nearby_payload["name"] = "Nearby"
    nearby_payload["latitude"] = 39.7900
    client.post("/api/v1/addresses/", json=nearby_payload)

    far_payload = ADDRESS_PAYLOAD.copy()
    far_payload["name"] = "Far Away"
    far_payload["latitude"] = 41.8781
    far_payload["longitude"] = -87.6298
    far_payload["city"] = "Chicago"
    far_payload["state"] = "Illinois"
    far_payload["postal_code"] = "60601"
    client.post("/api/v1/addresses/", json=far_payload)

    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 39.7817,
            "longitude": -89.6501,
            "distance": 10,
            "unit": "km",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["name"] == "Home"
    assert payload[1]["name"] == "Nearby"
    assert payload[0]["distance"] <= payload[1]["distance"]


def test_nearby_search_supports_miles(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    nearby_payload = ADDRESS_PAYLOAD.copy()
    nearby_payload["name"] = "Nearby"
    nearby_payload["latitude"] = 39.7900
    client.post("/api/v1/addresses/", json=nearby_payload)

    response = client.get(
        "/api/v1/addresses/nearby",
        params={
            "latitude": 39.7817,
            "longitude": -89.6501,
            "distance": 10,
            "unit": "miles",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["name"] == "Home"
    assert payload[1]["name"] == "Nearby"


def test_invalid_coordinates_are_rejected(client):
    invalid_payload = ADDRESS_PAYLOAD.copy()
    invalid_payload["latitude"] = 120

    response = client.post("/api/v1/addresses/", json=invalid_payload)

    assert response.status_code == 422


def test_blank_required_text_is_rejected(client):
    invalid_payload = ADDRESS_PAYLOAD.copy()
    invalid_payload["street"] = "   "

    response = client.post("/api/v1/addresses/", json=invalid_payload)

    assert response.status_code == 422


def test_empty_update_payload_is_rejected(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    response = client.put("/api/v1/addresses/1", json={})

    assert response.status_code == 422


def test_required_update_field_cannot_be_null(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)

    response = client.put("/api/v1/addresses/1", json={"street": None})

    assert response.status_code == 422


def test_missing_address_returns_not_found(client):
    response = client.get("/api/v1/addresses/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Address not found."

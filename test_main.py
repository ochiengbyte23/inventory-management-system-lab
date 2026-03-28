import pytest
from unittest.mock import patch, MagicMock
import main  # imports your main.py


# ── Setup ─────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_inventory():
    """
    Runs automatically before every test.
    Resets the inventory list and next_id counter so tests don't affect each other.
    """
    main.inventory.clear()
    main.next_id = 1
    yield  # test runs here


@pytest.fixture
def client():
    """Creates a Flask test client so we can make requests without a running server."""
    main.app.config["TESTING"] = True
    with main.app.test_client() as client:
        yield client


# ── Mock product data ─────────────────────────────────────────────────────────

# This is what we pretend Open Food Facts returns so we don't make real API calls
MOCK_PRODUCT = {
    "barcode": "3274080005003",
    "name": "Evian",
    "brand": "Evian",
    "quantity": "500ml",
}

# This is the raw Open Food Facts API response structure we mock
MOCK_OFF_RESPONSE = {
    "status": 1,
    "product": {
        "product_name": "Evian",
        "brands": "Evian",
        "quantity": "500ml",
    }
}


# ── Helper to add a product ───────────────────────────────────────────────────

def add_mock_item(client):
    """Reusable helper that adds one item to the inventory using the POST route."""
    with patch("main.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_OFF_RESPONSE
        mock_get.return_value = mock_response

        return client.post(
            "/inventory",
            json={"barcode": "3274080005003", "stock": 5}
        )


# ── GET /inventory ────────────────────────────────────────────────────────────

class TestGetAllItems:

    def test_returns_empty_list_on_start(self, client):
        """Inventory should be empty when no items have been added."""
        response = client.get("/inventory")
        data = response.get_json()

        assert response.status_code == 200
        assert data["items"] == []
        assert data["total"] == 0

    def test_returns_items_after_adding(self, client):
        """Inventory should contain the item after a successful POST."""
        add_mock_item(client)

        response = client.get("/inventory")
        data = response.get_json()

        assert response.status_code == 200
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Evian"


# ── GET /inventory/<id> ───────────────────────────────────────────────────────

class TestGetSingleItem:

    def test_returns_item_by_id(self, client):
        """Should return the correct item when given a valid id."""
        add_mock_item(client)

        response = client.get("/inventory/1")
        data = response.get_json()

        assert response.status_code == 200
        assert data["id"] == 1
        assert data["name"] == "Evian"

    def test_returns_404_for_missing_item(self, client):
        """Should return 404 when the item id does not exist."""
        response = client.get("/inventory/999")
        data = response.get_json()

        assert response.status_code == 404
        assert "not found" in data["error"]


# ── POST /inventory ───────────────────────────────────────────────────────────

class TestAddItem:

    def test_adds_item_successfully(self, client):
        """Should add an item and return 201 when a valid barcode is provided."""
        response = add_mock_item(client)
        data = response.get_json()

        assert response.status_code == 201
        assert data["message"] == "Item added successfully"
        assert data["item"]["name"] == "Evian"
        assert data["item"]["stock"] == 5

    def test_returns_400_when_barcode_missing(self, client):
        """Should return 400 when no barcode is provided in the request body."""
        response = client.post("/inventory", json={"stock": 3})
        data = response.get_json()

        assert response.status_code == 400
        assert "barcode" in data["error"]

    def test_returns_400_when_body_empty(self, client):
        """Should return 400 when the request body is completely empty."""
        response = client.post("/inventory", json={})
        data = response.get_json()

        assert response.status_code == 400

    def test_returns_409_when_barcode_already_exists(self, client):
        """Should return 409 when trying to add a product that already exists."""
        add_mock_item(client)  # add it once

        response = add_mock_item(client)  # try adding again
        data = response.get_json()

        assert response.status_code == 409
        assert "already exists" in data["error"]

    def test_returns_404_when_barcode_not_on_off(self, client):
        """Should return 404 when Open Food Facts doesn't recognise the barcode."""
        with patch("main.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": 0}  # product not found on OFF
            mock_get.return_value = mock_response

            response = client.post("/inventory", json={"barcode": "0000000000000"})
            data = response.get_json()

            assert response.status_code == 404
            assert "not found" in data["error"]

    def test_returns_404_when_off_api_is_down(self, client):
        """Should return 404 when the Open Food Facts API returns a non-200 status."""
        with patch("main.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500  # simulate server error
            mock_get.return_value = mock_response

            response = client.post("/inventory", json={"barcode": "3274080005003"})
            data = response.get_json()

            assert response.status_code == 404


# ── PATCH /inventory/<id> ─────────────────────────────────────────────────────

class TestUpdateItem:

    def test_updates_stock_successfully(self, client):
        """Should update the stock value and return the updated item."""
        add_mock_item(client)

        response = client.patch("/inventory/1", json={"stock": 99})
        data = response.get_json()

        assert response.status_code == 200
        assert data["item"]["stock"] == 99

    def test_returns_404_for_missing_item(self, client):
        """Should return 404 when trying to update an item that doesn't exist."""
        response = client.patch("/inventory/999", json={"stock": 10})
        data = response.get_json()

        assert response.status_code == 404
        assert "not found" in data["error"]

    def test_returns_400_when_body_missing(self, client):
        """Should return 400 or 415 when no request body is sent."""
        add_mock_item(client)

        response = client.patch("/inventory/1", json=None)

        assert response.status_code in (400, 415)


# ── DELETE /inventory/<id> ────────────────────────────────────────────────────

class TestDeleteItem:

    def test_deletes_item_successfully(self, client):
        """Should remove the item from inventory and return a success message."""
        add_mock_item(client)

        response = client.delete("/inventory/1")
        data = response.get_json()

        assert response.status_code == 200
        assert "removed successfully" in data["message"]

        # confirm it's actually gone
        get_response = client.get("/inventory/1")
        assert get_response.status_code == 404

    def test_returns_404_for_missing_item(self, client):
        """Should return 404 when trying to delete an item that doesn't exist."""
        response = client.delete("/inventory/999")
        data = response.get_json()

        assert response.status_code == 404
        assert "not found" in data["error"]


# ── External API (fetch_product) ──────────────────────────────────────────────

class TestFetchProduct:

    def test_returns_product_data_for_valid_barcode(self):
        """fetch_product() should return a dict with product info for a valid barcode."""
        with patch("main.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = MOCK_OFF_RESPONSE
            mock_get.return_value = mock_response

            result = main.fetch_product("3274080005003")

            assert result is not None
            assert result["name"] == "Evian"
            assert result["brand"] == "Evian"
            assert result["barcode"] == "3274080005003"

    def test_returns_none_when_api_fails(self):
        """fetch_product() should return None when the API returns a non-200 status."""
        with patch("main.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            result = main.fetch_product("3274080005003")

            assert result is None

    def test_returns_none_when_product_not_found(self):
        """fetch_product() should return None when Open Food Facts status is 0."""
        with patch("main.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": 0}  # OFF says product doesn't exist
            mock_get.return_value = mock_response

            result = main.fetch_product("0000000000000")

            assert result is None
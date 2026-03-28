# Inventory Management System

A RESTful API built with Flask that manages a food product inventory using the [Open Food Facts API](https://world.openfoodfacts.org/) to automatically fetch product details from a barcode.

---

## Table of Contents

- [Requirements](#requirements)
- [Installation and Setup](#installation-and-setup)
- [Running the App](#running-the-app)
- [API Endpoints](#api-endpoints)
- [Example Usage](#example-usage)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)

---

## Requirements

- Python 3.12
- [Pipenv](https://pipenv.pypa.io/en/latest/)

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd inventory-management-system-lab
```

### 2. Install Pipenv if you don't have it

```bash
pip install pipenv
```

**3. Install project dependencies

```bash
pipenv install
```

### 4. Install dev dependencies (for running tests)

```bash
pipenv install pytest --dev
```

**5. Activate the virtual environment

```bash
pipenv shell
```

---

## Running the App

```bash
pipenv run python main.py
```

The server starts at `http://127.0.0.1:5000` with debug mode enabled.

> **Note:** Data is stored in memory and resets every time the server restarts. This is intentional for this practice project.

---

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/inventory` | Fetch all items in the inventory |
| GET | `/inventory/<id>` | Fetch a single item by its ID |
| POST | `/inventory` | Add a new item using a product barcode |
| PATCH | `/inventory/<id>` | Update the stock count of an item |
| DELETE | `/inventory/<id>` | Remove an item from the inventory |

---

### GET /inventory

Returns all items currently in the inventory.

**Response

```json
{
  "items": [...],
  "total": 2
}
```

---

### GET /inventory/\<id\>

Returns a single item by its ID.

**Response `200 OK`**

```json
{
  "id": 1,
  "barcode": "3274080005003",
  "name": "Evian",
  "brand": "Evian",
  "quantity": "500ml",
  "stock": 5
}
```

**Response `404 Not Found`**

```json
{
  "error": "Item with id 99 not found"
}
```

---

### POST /inventory

Adds a new product to the inventory. Requires a `barcode` in the request body. Product details are automatically fetched from the Open Food Facts API.

**Request body

```json
{
  "barcode": "3274080005003",
  "stock": 10
}
```

> `stock` is optional and defaults to `1` if not provided.

**Response `201 Created`**

```json
{
  "message": "Item added successfully",
  "item": {
    "id": 1,
    "barcode": "3274080005003",
    "name": "Evian",
    "brand": "Evian",
    "quantity": "500ml",
    "stock": 10
  }
}
```

**Error responses

| Status | Reason |
| --- | --- |
| `400` | No barcode provided in request body |
| `404` | Barcode not found on Open Food Facts |
| `409` | Product with this barcode already exists in inventory |

---

### PATCH /inventory/\<id\>

Updates the stock count of an existing item.

**Request body

```json
{
  "stock": 25
}
```

**Response `200 OK`**

```json
{
  "message": "Item updated successfully",
  "item": {
    "id": 1,
    "name": "Evian",
    "stock": 25
  }
}
```

---

### DELETE /inventory/\<id\>

Removes an item from the inventory by its ID.

**Response `200 OK`**

```json
{
  "message": "Item 'Evian' removed successfully"
}
```

---

## Example Usage

You can test the API using `curl` in your terminal or a tool like [Postman](https://www.postman.com/).

**Add a product by barcode

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"barcode": "3274080005003", "stock": 5}'
```

**Get all inventory items

```bash
curl http://127.0.0.1:5000/inventory
```

**Get a single item

```bash
curl http://127.0.0.1:5000/inventory/1
```

**Update stock

```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"stock": 20}'
```

### Delete an item

```bash
curl -X DELETE http://127.0.0.1:5000/inventory/1
```

### Some barcodes to test with

| Product | Barcode |
| --- | --- |
| Evian Water 500ml | `3274080005003` |
| Nutella 400g | `3017620422003` |
| Coca-Cola 330ml | `5449000000996` |
| Kellogg's Corn Flakes | `5010029013393` |

You can find more barcodes by browsing [world.openfoodfacts.org](https://world.openfoodfacts.org) — the barcode is in the product's URL.

---

## Running Tests

Make sure dev dependencies are installed, then run:

```bash
pipenv run pytest test_main.py -v
```

The test suite covers:

- All 5 API endpoints (GET, POST, PATCH, DELETE)
- Edge cases like missing fields, duplicate barcodes, and invalid IDs
- External API interactions using mocks (no real network calls are made during tests)

Expected output:

```text
PASSED test_main.py::TestGetAllItems::test_returns_empty_list_on_start
PASSED test_main.py::TestGetAllItems::test_returns_items_after_adding
PASSED test_main.py::TestGetSingleItem::test_returns_item_by_id
...
18 passed in 0.46s
```

---

## Project Structure

```text
inventory-management-system-lab/
├── main.py          # Flask app — routes and API logic
├── test_main.py     # Pytest unit tests
├── Pipfile          # Project dependencies
├── Pipfile.lock     # Locked dependency versions
└── README.md        # Project documentation
```

---

## How It Works

1. You send a `POST` request with a product barcode
2. The app calls the Open Food Facts API to look up the product
3. Product details (name, brand, quantity) are saved into the in-memory inventory
4. You can then retrieve, update, or delete items using their assigned ID

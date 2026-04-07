import argparse
import sys
import requests

BASE_URL = "http://127.0.0.1:5000"


def list_items():
    response = requests.get(f"{BASE_URL}/inventory")
    data = response.json()
    items = data.get("items", [])

    if not items:
        print("Inventory is empty.")
        return

    print(f"\n{'ID':<5} {'Name':<25} {'Brand':<20} {'Qty':<12} {'Stock'}")
    print("-" * 70)
    for item in items:
        print(f"{item['id']:<5} {item['name']:<25} {item['brand']:<20} {item['quantity']:<12} {item['stock']}")
    print(f"\nTotal: {data['total']} item(s)")


def get_item(item_id):
    response = requests.get(f"{BASE_URL}/inventory/{item_id}")
    if response.status_code == 404:
        print(f"Error: {response.json()['error']}")
        return
    item = response.json()
    print(f"\nID:       {item['id']}")
    print(f"Name:     {item['name']}")
    print(f"Brand:    {item['brand']}")
    print(f"Quantity: {item['quantity']}")
    print(f"Barcode:  {item['barcode']}")
    print(f"Stock:    {item['stock']}")


def add_item(barcode, stock):
    payload = {"barcode": barcode, "stock": stock}
    response = requests.post(f"{BASE_URL}/inventory", json=payload)
    data = response.json()

    if response.status_code == 201:
        item = data["item"]
        print(f"Added: {item['name']} (ID: {item['id']}, stock: {item['stock']})")
    else:
        print(f"Error ({response.status_code}): {data.get('error')}")


def update_item(item_id, stock):
    response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json={"stock": stock})
    data = response.json()

    if response.status_code == 200:
        print(f"Updated item {item_id} — new stock: {data['item']['stock']}")
    else:
        print(f"Error ({response.status_code}): {data.get('error')}")


def delete_item(item_id):
    response = requests.delete(f"{BASE_URL}/inventory/{item_id}")
    data = response.json()

    if response.status_code == 200:
        print(data["message"])
    else:
        print(f"Error ({response.status_code}): {data.get('error')}")


def main():
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Interact with the Inventory Management API"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="Show all inventory items")

    # get
    get_parser = subparsers.add_parser("get", help="Get a single item by ID")
    get_parser.add_argument("id", type=int, help="Item ID")

    # add
    add_parser = subparsers.add_parser("add", help="Add an item by barcode")
    add_parser.add_argument("barcode", type=str, help="Product barcode")
    add_parser.add_argument("--stock", type=int, default=1, help="Initial stock count (default: 1)")

    # update
    update_parser = subparsers.add_parser("update", help="Update stock for an item")
    update_parser.add_argument("id", type=int, help="Item ID")
    update_parser.add_argument("--stock", type=int, required=True, help="New stock count")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete an item by ID")
    delete_parser.add_argument("id", type=int, help="Item ID")

    args = parser.parse_args()

    try:
        if args.command == "list":
            list_items()
        elif args.command == "get":
            get_item(args.id)
        elif args.command == "add":
            add_item(args.barcode, args.stock)
        elif args.command == "update":
            update_item(args.id, args.stock)
        elif args.command == "delete":
            delete_item(args.id)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Is the Flask server running?")
        print("  Run: pipenv run python main.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

inventory = [{
        "barcode": "3017620422003",
        "brand": "Nutella",
        "name": "Nutella",
        "quantity": "400g"
    }]
next_id = 1

def fetch_product(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    headers = {"User-Agent": "InventoryPracticeApp/1.0 (bildad.masaga@student.moringaschool.com)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    data = response.json()
    if data.get("status") != 1:
        return None
    
    product = data['product']
    
    return {
        "barcode": barcode,
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", "Unknown"),
        "quantity": product.get("quantity", "Unknown"),
    }
#Fetching all items in the inventory
@app.route('/inventory', methods=['GET'])
def get_all_items():
    return jsonify({'items': inventory, 'total': len(inventory)})

#fetching a single item in the inventory
@app.route('/inventory/<int: item_id>', methods=['GET'])
def get_item(item_id):
    item = next((i for i in inventory if i['id'] == item_id), None)
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    return jsonify(item), 200



if __name__ == '__main__':
    app.run(debug=True)
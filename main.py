from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

inventory = []
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
@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((i for i in inventory if i['id'] == item_id), None)
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    return jsonify(item), 200

#adding a new item y barcode
@app.route("/inventory", methods=["POST"])
def add_item():
    global next_id
    body = request.get_json()
    
    if not body or 'barcode' not in body:
        return jsonify({"error": "A 'barcode' field is required in the request body"}), 400
    
    barcode = body['barcode']
    existing = next((i for i in inventory if i['barcode'] == barcode), None)
    if existing:
        return jsonify({"error": "Item with this barcode already exists", "item": existing}), 409
    
    product_data = fetch_product(barcode)
 
    if not product_data:
        return jsonify({"error": f"Product with barcode '{barcode}' not found on Open Food Facts"}), 404
    
    new_item = {
        'id': next_id,
        'stock': body.get('stock', 1),
        **product_data,
    }
    inventory.append(new_item)
    next_id += 1
    
    return jsonify({"message": "Item added successfully", "item": new_item}), 201
#updating item content
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
 
    body = request.get_json()
    if not body:
        return jsonify({"error": "Request body is required"}), 400
 
    # Only allow updating the stock quantity
    if "stock" in body:
        item["stock"] = body["stock"]
 
    return jsonify({"message": "Item updated successfully", "item": item}), 200

@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global inventory
 
    item = next((i for i in inventory if i["id"] == item_id), None)
 
    if not item:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
 
    inventory = [i for i in inventory if i["id"] != item_id]
 
    return jsonify({"message": f"Item '{item['name']}' removed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
import requests

BASE_URL = "http://localhost:8000"

products = [
    {
        "name": "Nüsslisalat (Lamb's Lettuce)",
        "category": "Blattgemüse",
        "price_per_unit": 6.50,
        "unit": "kg",
        "origin": "Schweiz, Seeland",
        "stock_quantity": 40.0,
        "certification": "Bio Suisse (Knospe)",
        "is_seasonal": True,
        "description": "Typischer Schweizer Wintersalat."
    },
    {
        "name": "Pastinaken",
        "category": "Wurzelgemüse",
        "price_per_unit": 4.20,
        "unit": "kg",
        "origin": "Schweiz, Thurgau",
        "stock_quantity": 120.0,
        "certification": "Demeter",
        "is_seasonal": True,
        "description": "Bio-Pastinaken, perfekt für Eintöpfe."
    },
    {
        "name": "Federkohl (Kale)",
        "category": "Kohlgemüse",
        "price_per_unit": 5.50,
        "unit": "kg",
        "origin": "Schweiz, Zürich",
        "stock_quantity": 60.0,
        "certification": "Bio Suisse (Knospe)",
        "is_seasonal": True,
        "description": "Nährstoffreicher Federkohl."
    }
]

def add_products():
    for product in products:
        response = requests.post(f"{BASE_URL}/products", json=product)
        if response.status_code == 201:
            print(f"Added: {product['name']}")
        else:
            print(f"Failed to add {product['name']}: {response.text}")

if __name__ == "__main__":
    add_products()

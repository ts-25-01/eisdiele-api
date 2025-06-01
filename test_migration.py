import requests
import json
BASE_URL = "http://127.0.0.1:5000"
def test_old_vs_new():
    """Vergleiche alte Listen-API mit neuer SQLite-API"""



print("=== MIGRATION TEST ===")
# Test 1: GET alle Sorten
response = requests.get(f"{BASE_URL}/api/flavours")
print(f"✅ GET all flavours: {len(response.json())} Sorten gefunden")
# Test 2: POST neue Sorte (ohne ID!)
new_flavour = {
"name": "pistazie",
"type": "nuss",
"price_per_serving": 1.8
}
response = requests.post(f"{BASE_URL}/api/flavours", json=new_flavour)
print(f"✅ POST new flavour: {response.status_code}")
# Test 3: DELETE by ID (nicht Name!)
# response = requests.delete(f"{BASE_URL}/api/flavours/1")
# print(f"✅ DELETE by ID: {response.status_code}")
print("🎉 Migration erfolgreich!")
if __name__ == "__main__":
    test_old_vs_new()
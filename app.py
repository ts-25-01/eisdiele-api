from flask import Flask, jsonify, request

app = Flask(__name__)

flavours = [

    {"id": 1, "name": "schokolade", "type": "milch", "price per serving": 1.5},
    {"id": 2, "name": "vanille", "type": "milch", "price per serving": 1.5},
    {"id": 3, "name": "zitrone", "type": "frucht", "price per serving": 1.3}
]

@app.route("/")
def welkome():
    return "Wilkommen auf der Homepage unserer Eisdiele"

@app.route('/api/flavours', methods=["GET"])
def get_flavours():
    return jsonify(flavours), 200

@app.route("/api/flavours", methods=["POST"])
def post_flavours():
    new_flavour = request.get_json()
    flavours.append(new_flavour)
    return jsonify({"message": "Sorten hinzugefügt"}), 201

@app.route("/api/flavours/<name>", methods=['DELETE'])
def delete_flavour(name):
    for flavour in flavours:
        if flavour["name"] == name:
            flavours.remove(flavour)
            return jsonify({"message": "Sorte wurde erfolgreich gelöscht"}), 200
    return jsonify({"message":"Sorte nicht gefunden"}), 404

@app.route("/api/flavours/<name>", methods=["PUT"])
def put_flavours(name):
    updatet_flavour = request.get_json()
    for flavour in flavours:
        if flavour["name"] == name:
            flavour.clear()
            flavour.update(updatet_flavour)
            return jsonify({"message": "Sorte wurde erfolgreich geupdatet"}), 200
    return jsonify({"message":"Sorte nicht gefunden"}), 404

@app.route("/api/flavours/<name>", methods=["PATCH"])
def patch_flavours(name):
    updatet_flavour = request.get_json()
    for flavour in flavours:
        if flavour["name"] == name:
            flavour.update(updatet_flavour)
            return jsonify({"message": "Sorte wurde erfolgreich geupdatet"}), 200
    return jsonify({"message":"Sorte nicht gefunden"}), 404

if __name__ == "__main__":
    app.run(debug=True)

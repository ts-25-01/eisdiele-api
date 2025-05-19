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
    return jsonify(flavours)

if __name__ == "__main__":
    app.run(debug=True)


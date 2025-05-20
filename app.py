from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

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
    """
    Liste aller Geschmackssorten
    ---
    responses:
        200:
            description: JSON-Liste aller Geschmackssorten
            examples:
                application/json:
                    - id: 1
                      name: schokolade
                      type: milch
                      price per serving: 1.5
                    - id: 2
                      name: vanille
                      type: frucht
                      price per serving: 1.5
    """
    return jsonify(flavours), 200

@app.route("/api/flavours", methods=["POST"])
def post_flavours():
    """
    Neue Geschmackssorte hinzufügen
    ---
    consumes:
        - application/json
    parameters:
        - in: body
          name: flavour
          required: true
          schema:
            type: object
            properties:
                id:
                    type: integer
                    example: 1
                name:
                    type: string
                    example: schokolade
                type:
                    type: string
                    example: milch
                price per serving:
                    type: number
                    example: 1.5
    responses:
        201:
            description: Sorten hinzugefügt
        400:
            description: Fehler, kein Objekt übergeben
    """
    new_flavour = request.get_json()
    if not new_flavour:
        return jsonify({"message": "Fehler, kein Objekt übergeben"}), 400
    flavours.append(new_flavour)
    return jsonify({"message": "Sorten hinzugefügt"}), 201


@app.route("/api/flavours/<name>", methods=['DELETE'])
def delete_flavour(name):
    """
    Eine Geschmackssorte löschen
    ---
    parameters:
        - name: name
          in: path
          type: string
          required: true
          description: die zu löschende Geschmackssorte
    responses:
        200:
            description: Sorte wurde erfolgreich gelöscht
        404:
            description: Sorte nicht gefunden
    """
    for flavour in flavours:
        if flavour["name"] == name:
            flavours.remove(flavour)
            return jsonify({"message": "Sorte wurde erfolgreich gelöscht"}), 200
    return jsonify({"message":"Sorte nicht gefunden"}), 404

@app.route("/api/flavours/<name>", methods=["PUT"])
def put_flavours(name):
    """
        Eine komplette Geschmackssorte mit neuen Werten überschreiben
        ---
        parameters:
            - name: name
              in: path
              type: string
              required: true
              description: Der Name der Geschmackssorte bei der ein Wert überschrieben werden soll
            - in: body
              name: flavour
              required: true
              schema:
                type: object
                properties:
                    id:
                        type: integer
                        example: 1
                    name:
                        type: string
                        example: schokolade
                    type:
                        type: string
                        example: milch
                    price per serving:
                        type: float
                        example: 1.5
        responses:
            200:
                description: Sorte wurde erfolgreich geupdatet
            400:
                description: Sorte nicht gefunden
        """
    updatet_flavour = request.get_json()
    for flavour in flavours:
        if flavour["name"] == name:
            flavour.clear()
            flavour.update(updatet_flavour)
            return jsonify({"message": "Sorte wurde erfolgreich geupdatet"}), 200
    return jsonify({"message":"Sorte nicht gefunden"}), 404

@app.route("/api/flavours/<name>", methods=["PATCH"])
def patch_flavours(name):
    """
    Einen einzelnen Wert einer vorhandene Geschmackssorte überschreiben
    ---
    parameters:
        - name: name
          in: path
          type: string
          required: true
          description: Der Name der Geschmackssorte bei der ein Wert überschrieben werden soll
        - in: body
          name: flavour
          required: anyOf
          schema:
            type: object
            properties:
                id:
                    type: integer
                    example: 1
                name:
                    type: string
                    example: schokolade
                type:
                    type: string
                    example: milch
                price per serving:
                    type: float
                    example: 1.5
    responses:
        200:
            description: Sorte wurde erfolgreich geupdatet
        400:
            description: Sorte nicht gefunden
    """
    updatet_flavour = request.get_json()
    for flavour in flavours:
        if flavour["name"] == name:
            flavour.update(updatet_flavour)
            return jsonify({"message": "Sorte wurde erfolgreich geupdatet"}), 200
    return jsonify({"message":"Sorte nicht gefunden"}), 404

if __name__ == "__main__":
    app.run(debug=True)

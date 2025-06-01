from flask import Flask, jsonify, request
from flasgger import Swagger
import sqlite3

app = Flask(__name__)
#swagger-Objekt von der Klasse Swagger initialisieren;app-Objekt dabei übergeben
swagger = Swagger(app)

#Lege Konstante an, der den Pfad zur Datenbank-Datei beschreibt
#DATABASE-URL = "http://127.0.0.1:5432" # ist später für die Postgres-DB
DATABASE = "./ice_cream.db" # unsere Eisdielen-DB

#Datenbank-Hilfsfunktionen
## Funktion, um sich mit der Datenbank zu verbinden 

def get_db_connection():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row #für Ergebnisse v.SQL-Befehlen im dict/JSON Format
    return con


#Seeding Scripts für die DB
#Funktion um die Datenbank zu initialisieren
def init_db():
    #Initialisieren der DB
    con = get_db_connection() # rufe Hilfsfunktion auf
    cur = con.cursor()
    cur.execute('''
                CREATE TABLE Flavours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                price_per_serving FLOAT
                )
                ''')
    #Initialisieren der KD-DB
def init_customers_table():
    con = get_db_connection() #rufe Hilfsfunktion auf
    cur = con.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                loyalty_points INTEGER DEFAULT 0
                )
                ''')
    
    #Initialisieren der Bestell-Tabelle
def init_orders_table():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                flavour_id INTEGER,
                quantity INTEGER DEFAULT 1,
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (flavour_id) REFERENCES flavours (id)
                )
                ''')
    
    #Überprüfen, ob Zeilen, also Datensätze in der Tabelle drin sind
    count = cur.execute('SELECT COUNT(*) FROM Flavours').fetchone()[0] #gibt uns ein Tupel zurück (z.B. (1, )), aber wir greifen nur auf den ersten Index zu
    if count == 0:
        data = [
            ('schokolade','milch', 1.5),
            ('vanille','milch', 1.5),
            ('zitrone','frucht', 1.3)
        ]
        cur.executemany('INSERT INTO Flavours (name, type, price_per_serving) VALUES (?,?,?)', data) # das geht sie für jeweils jeden Eintrag durch
        con.commit() # an dieser Stelle werden die Änderungen persistiert und gespeichert
    
    # Beispiel-Kunden einfügen
    count = cur.execute('SELECT COUNT(*) FROM customers').fetchone()[0] 
    if count == 0:
        customers_data = [
            ('Max Mustermann', 'max@email.com', 50),
            ('Anna Schmidt', 'anna@email.com', 30),
            ('Tom Weber', 'tom@email.com', 80)
        ]
        cur.executemany('INSERT INTO customers (name, email, loyalty_points) VALUES (?,?,?)', customers_data)
        con.commit()
    con.close()

#flavours = [

#    {"id": 1, "name": "schokolade", "type": "milch", "price per serving": 1.5},
#    {"id": 2, "name": "vanille", "type": "milch", "price per serving": 1.5},
#    {"id": 3, "name": "zitrone", "type": "frucht", "price per serving": 1.3}
#]

#Test-Route für die Startseite
@app.route("/")
def welcome():
    return "Willkommen auf der Homepage unserer Eisdiele"

#GET-Route implementieren, d.h. Daten abrufen bzw.alle Eissorten anzeigen
@app.route("/api/flavours", methods=['GET'])
def show_flavours():
    """
    Liste aller Eis-Sorten:
    ---
    responses:
    200:
        description: JSON-Liste aller Eissorten
        examples:
         application/json:
             - id: 1
               name: schokolade
               type: milch
               price_per_serving: 1.5
             - id: 2
               name: vanille
               type: milch
               price_per_serving: 1.5
             - id: 3
               name: zitrone
               type: frucht
               price_per_serving: 1.3
    """
    # Daten abrufen von der DB
    con = get_db_connection() #Verbindung mit der DB
    cur = con.cursor()
    flavours =cur.execute('SELECT * FROM Flavours').fetchall()
    con.close()    
    return jsonify([dict(flavour) for flavour in flavours]), 200

## GET-Route implementieren, um Daten von einer Eissorte anzuzeigen
@app.route("/api/flavours/<int:flavour_id>", methods=['GET'])
def show_flavour(flavour_id):
    """
    Liste aller Eissorten
    ---
        parameters:
        - name: id
          in: path
          type: integer
          required: true
          description: Der Name der anzuzeigenden Eissorte
    responses:
        200:
            description: JSON-Objekt von einer Sorte
            examples:
                application/json:
                    - id: 1
                      name: Schokolade
                      type: milch
                      price_per_serving: 1.5
                    - id: 2
                      name: Vanille
                      type: milch
                      price_per_serving: 1.5
    """
    con = get_db_connection()
    cur = con.cursor()
    flavour = cur.execute('SELECT * FROM Flavours WHERE id = ?', (flavour_id,)).fetchone()
    if flavour is None:
        return jsonify({"message": "Geschmacksrichtung mit der ID existiert nicht"}), 404

    con.close()
    return jsonify(dict(flavour)), 200
    # # Daten abrufen von der DB
    # con = get_db_connection() # Verbindung mit der DB
    # cur = con.cursor()
    # flavours = cur.execute('SELECT * FROM flavours').fetchall()
    # con.close()
    # return jsonify([dict(flavour) for flavour in flavours]), 200



## POST-Route implementieren, d.h. neue Sorte hinzufügen
@app.route("/api/flavours", methods=['POST'])
def add_flavour():
    """
    Neue Sorte hinzufügen
    ---
    consumes:
        - application/json
    parameters:
        - in: body
          name: sorte
          required: true
          schema:
            type: object
            properties:
                name:
                    type: string
                    example: zitrone
                type:
                    type: string
                    example: frucht
                price_per_serving:
                    type: float
                    example: 1.3
    responses:
        201:
            description: Sorte wurde erfolgreich hinzugefuegt
        400:
            description: Fehler, kein Objekt übergeben
    """
    new_flavour = request.get_json() # {"name": "stracciatella", "type:": milch, "price_per_serving": "1.8"}
    if not new_flavour or 'name' not in new_flavour:
        return jsonify({"message": "Keine oder fehlerhafte Daten übertragen"}), 400
    con = get_db_connection() # Schritt 1: DB-Verbindung
    cur = con.cursor() # Schritt 2: Cursor-Objekt definieren
    # Schritt 3: Befehl ausführen
    cur.execute('INSERT INTO Flavours (name, type, price_per_serving) VALUES (?,?,?)', 
                (new_flavour['name'],
                 new_flavour['type'],
                 new_flavour['price_per_serving'])
                ) # An dieser Stelle SQL-Befehl zum Hinzufügen des neuen Objektes
    con.commit() # Schritt 4: Persistieren der Veränderungen
    con.close() # Schritt 5: Verbindung zur DB wieder schließen
#    flavours.append(new_flavour)
    return jsonify({"message": "Sorte wurde erfolgreich hinzugefuegt"}), 201


## DELETE-Route, um eine Sorte aus der Liste zu löschen
@app.route("/api/flavours/<int:flavour_id>", methods=['DELETE'])
def delete_flavour(flavour_id):
    """
    Eine Sorte löschen
    ---
    parameters:
        - name: id
          in: path
          type: string
          required: true
          description: to be deleted name of the flavour     
    responses:
        200:
            description: Sorte wurde erfolgreich geloescht
            examples:
                application/json:
                    - message: Sorte wurde geloescht
        404:
            description: Sorte nicht gefunden! 
    """
#    for flavour in flavours:
#        if flavour["name"] == name:
#            flavours.remove(flavour)
#            return jsonify({"message": "Sorte wurde erfolgreich geloescht"}), 200
    con = get_db_connection() 
    cur = con.cursor()
    # Überprüfe, ob die Sorte mit der angegebenen ID überhaupt existiert
    flavour = cur.execute('SELECT * FROM Flavours WHERE id = ?', (flavour_id,)).fetchone() # 4 OR 1=! --
    if flavour is None:
        return jsonify({"message":"Sorte mit dieser ID existiert nicht"}), 404
    cur.execute('DELETE FROM Flavours WHERE id = ?', (flavour_id,) )
    ## Achtung: Nutz bitte die ?-Funktion, um SQL-Injection zu verhindern, sonst sähe es so aus:
    # cur.execute(f'DELETE FROM flavours WHERE id = {flavour_id}') # 4 OR 1=! --
    con.commit()
    con.close()
    return jsonify({"message": "Sorte wurde erfolgreich gelöscht"}), 200

## Baue eine Funktion, zum Updaten
## PUT-Route -> Ersetze alle Eigenschaften einer Sorte, d.h. hier schicken wir alle Eigenschaften im Body als JSON mit

@app.route("/api/flavours/<int:flavour_id>", methods=['PUT'])
def put_flavour(flavour_id):
    
    updated_flavour = request.get_json() # Speichere dir das Objekt im Body aus dem Request des Clients
    if not updated_flavour or 'name' not in updated_flavour:
        return jsonify({"message": "Fehlende Daten"}), 400
    # Überprüfe, ob die Sorte überhaupt existiert in der DB mit dieser ID
    con = get_db_connection() # Schritt 1
    cur = con.cursor() # Schritt 2
    # Schritt 3
    flavour = cur.execute('SELECT * FROM Flavours WHERE id = ?', (flavour_id,)).fetchone()
    if flavour is None:
#    for flavour in flavours:
#        if flavour["name"] == name:
#           flavour.clear()
#            flavour.update(updated_flavour)
#            return jsonify({"message": "Sorte wurde erfolgreich geupdatet"}), 200
        return jsonify({"message":"Sorte mit dieser ID nicht in der DB gefunden"}), 404
    
    # Update jetzt die Sorte mit der übergebenen ID und mit den übergebenen Daten
    cur.execute('UPDATE Flavours SET name = ?, type = ?, price_per_serving = ? WHERE id = ?', (updated_flavour['name'], updated_flavour['type'], updated_flavour['price_per_serving'], flavour_id))
    con.commit()
    con.close()
    return jsonify({"message": "Sorteninhalt wurde erfolgreich ersetzt"}), 200


## PATCH-Route -> Ersetze spezifisch einzelne Eigenschaften, d.h. hier schicken wir nur die zu ändernden Eigenschaften im Body als JSON mit
@app.route("/api/flavours/<int:flavour_id>", methods=["PATCH"])
def patch_flavour(flavour_id):
    """
    Sorte teilweise ändern (z.B. nur den Type)
    ---
     parameters:
        - name: name
          in: path
          type: string
          required: true
          description: Der Name des Types, der ersetzt werden soll
        - in: body
          name: type
          required: anyOf
          schema: 
            type: object
            properties:
                id:
                    type: integer
                    example: 3
                name:
                    type: string
                    example: erdbeer
                type:
                    type: string
                    example: frucht
                price_per_serving:
                    type: float
                    example: 1.4
     responses:
        200:
            description: Sorte wurde geupdated
            examples:
                application/json:
                    - message: Sorte wurde geupdated
        404:
            description: Sorte wurde nicht gefunden
            examples:
                application/json:
                    - message: Sorte wurde nicht gefunden

    """
    updated_flavour = request.get_json() # name, type, price_per_serving
    if not updated_flavour:
        return jsonify({"message": "Fehlende Daten"}), 400
    con = get_db_connection()
    cur = con.cursor()
    flavour = cur.execute('SELECT * FROM Flavours WHERE id = ?', (flavour_id,)).fetchone()
    if flavour is None:
#    for flavour in flavours:
#        if flavour["name"] == name:
#+            flavour.update(updatet_flavour)
#            return jsonify({"message": "Sorte wurde erfolgreich geupdatet"}), 200
        return jsonify({"message":"Sorte mit dieser ID nicht in der DB gefunden"}), 404
    # Leere Liste, wo wir die Felder mitgeben, die wir speziell updaten wollen
    update_fields = [] # Notizzettel, wo wir alle Spalten reinschreiben, die der Client updaten möchte, z.B. nur name: elephant Joel, age = 24
    # Leere Liste, wo wir die Werte der Felder mitgeben, die wir updaten wollen
    update_values = [] # Notizzettel, wo wir die entsprechenden Werte reinschreiben von den Spalten, die wir aktualisieren wollen

    for field in ['name', 'type', 'price_per_serving']: # Iteriere über alle möglichen, vorhandenen Spalte der Tabelle
        if field in updated_flavour:
            update_fields.append(f'{field} = ?') # name = ?, type = ?
            update_values.append(updated_flavour[field]) # Sorte Maracuja, Frucht
    
    if update_fields:
        update_values.append(flavour_id)
        query = f'UPDATE Flavours SET {", ".join(update_fields)} WHERE id = ?' # UPDATE Flavours SET name = ?, type = ? WHERE id = ?
        cur.execute(query, update_values)
        con.commit()
    con.close()
    return jsonify({"message": "Sorte wurde erfolgreich geupdatet"}), 200

#####################
# Sorten nach Typ filtern
@app.route("/api/flavours/type/<flavour_type>", methods=["GET"])
def flavours_by_type(flavour_type):
    """
    Sorten nach Typ filtern (hier milch oder frucht)
    ---
    parameters:
      - name: flavour_type
        in: path
        type: string
        required: true
        description: Art der Sorte (z.B. milch oder frucht)
    responses:
      200:
        description: Liste von Sorten des angegebenen Typs
    """
    con = get_db_connection()
    cur = con.cursor()
    flavours = cur.execute('SELECT * FROM Flavours WHERE type = ?', (flavour_type,)).fetchall()
    con.close()
    if not flavours:
        return jsonify({"message": f"Keine Sorten vom Typ '{flavour_type}' gefunden."}), 404
    return jsonify([dict(flavour) for flavour in flavours]), 200

# Nach Preis filtern
@app.route("/api/flavours/price/<float:min_price>/<float:max_price>", methods=["GET"])
def flavours_by_price_range(min_price, max_price):
    """
    Sorten in Preisrange anzeigen (Aufgabe hier: zwischen 1.0€ und 1.50€)
    ---
    parameters:
      - name: min_price
        in: path
        type: float
        required: true
        description: Mindestpreis
      - name: max_price
        in: path
        type: float
        required: true
        description: Maximalpreis
    responses:
      200:
        description: Liste von Sorten im angegebenen Preisbereich
    """
    con = get_db_connection()
    cur = con.cursor()
    flavours = cur.execute('SELECT * FROM Flavours WHERE price_per_serving BETWEEN ? AND ?', (min_price, max_price)).fetchall()
    con.close()
    if not flavours:
        return jsonify({
            "message": f"Keine Sorten zwischen {min_price:.2f}€ und {max_price:.2f}€ gefunden."
        }), 404
    result = []
    for flavour in flavours:
        f = dict(flavour)
        f['price_per_serving'] = "{:.2f}".format(f['price_per_serving'])
        result.append(f)
    return jsonify(result), 200

#    return jsonify([dict(flavour) for flavour in flavours]), 200


# Nach günstigster Sorte filtern
@app.route("/api/flavours/cheapest", methods=["GET"])
def cheapest_flavours():
    """
    Die 3 günstigsten Sorten anzeigen
    ---
    responses:
      200:
        description: Liste der günstigsten Sorten
    """
    con = get_db_connection()
    cur = con.cursor()
    flavours = cur.execute('SELECT * FROM Flavours ORDER BY price_per_serving ASC LIMIT 3').fetchall()
    con.close()
    return jsonify([dict(flavour) for flavour in flavours]), 200

# Nach teuerster Sorte filtern
@app.route("/api/flavours/priciest", methods=["GET"])
def priciest_flavours():
    """
    Die 3 teuersten Sorten anzeigen
    ---
    responses:
      200:
        description: Liste der teuersten Sorten
    """
    con = get_db_connection()
    cur = con.cursor()
    flavours = cur.execute('SELECT * FROM Flavours ORDER BY price_per_serving DESC LIMIT 3').fetchall()
    con.close()
    return jsonify([dict(flavour) for flavour in flavours]), 200

# Zeit für Statistik
@app.route("/api/flavours/stats", methods=["GET"])
def flavour_statistics():
    """
    Eisdiele-Statistiken
    ---
    responses:
      200:
        description: Verschiedene Statistiken
        examples:
          application/json:
            total_flavours: 10
            average_price: 1.45
            cheapest_price: 1.20
            most_expensive_price: 1.80
            types_count:
              milch: 5
              frucht: 3
              vegan: 2
    """
    con = get_db_connection()
    cur = con.cursor()

    # Einzelne Statistiken berechnen
    total = cur.execute('SELECT COUNT(*) FROM Flavours').fetchone()[0]
    avg_price = cur.execute('SELECT AVG(price_per_serving) FROM Flavours').fetchone()[0]
    min_price = cur.execute('SELECT MIN(price_per_serving) FROM Flavours').fetchone()[0]
    max_price = cur.execute('SELECT MAX(price_per_serving) FROM Flavours').fetchone()[0]

    # Anzahl der Sorten je Typ (milch, frucht, vegan, ...)
    type_counts = cur.execute('SELECT type, COUNT(*) FROM Flavours GROUP BY type').fetchall()
    types_count = {row["type"]: row["COUNT(*)"] for row in type_counts}

    con.close()

    stats = {
        "total_flavours": total,
        "average_price": round(avg_price, 2),
        "cheapest_price": min_price,
        "most_expensive_price": max_price,
        "types_count": types_count
    }

    return jsonify(stats), 200

############################### KUNDEN_CRUDs ####################
## GET-Route, Alle Kunden anzeigen
@app.route("/api/customers", methods=["GET"])
def get_customers():
    con = get_db_connection()
    cur = con.cursor()
    rows = cur.execute("SELECT * FROM customers").fetchall()
    con.close()
    result = [dict(row) for row in rows]
    return jsonify(result), 200


## POST-Route,  Neuen Kunden hinzufügen
@app.route("/api/customers", methods=["POST"])
def add_customer():
    """
    Neuen Kunden hinzufügen
    ---
    tags:
      - Kunden
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - loyalty_points
          properties:
            name:
              type: string
              example: Max Mustermann
            loyalty_points:
              type: integer
              example: 100
    responses:
      201:
        description: Kunde erfolgreich hinzugefügt
        schema:
          type: object
          properties:
            message:
              type: string
              example: Neuer Kunde wurde erfolgreich hinzugefügt.
      400:
        description: Ungültige Eingabe
        schema:
          type: object
          properties:
            message:
              type: string
              example: Ungültige Anfrage. Name und loyalty_points werden benötigt.
    """
    data = request.get_json()
    name = data.get("name")
    email = data.get("email", "")
    loyalty_points = data.get("loyalty_points", 0)

    if not name or not email:
        return jsonify({"message": "Name und Email sind erforderlich."}), 400

    try:
        with sqlite3.connect("ice_cream.db") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO customers (name, email, loyalty_points) VALUES (?, ?, ?)",
                (name, email, loyalty_points)
            )
            con.commit()
        return jsonify({"message": "Kunde wurde erfolgreich hinzugefügt."}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"message": "Ein Kunde mit dieser E-Mail existiert bereits."}), 409
    except Exception as e:
        return jsonify({"message": f"Fehler beim Hinzufügen des Kunden: {str(e)}"}), 500

## DELETE-Route, um einen Kunden aus der Liste zu löschen
@app.route("/api/customers/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    """
    Einen Kunden löschen
    ---
    parameters:
        - name: id
          in: path
          type: string
          required: true
          description: to be deleted name of the customer     
    responses:
        200:
            description: Kunde wurde erfolgreich geloescht
            examples:
                application/json:
                    - message: Kunde wurde geloescht
        404:
            description: Kunde nicht gefunden! 
    """

    con = get_db_connection() 
    cur = con.cursor()
    # Überprüfe, ob der Kunde mit der angegebenen ID überhaupt existiert
    customer = cur.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone() # 4 OR 1=! --
    if customer is None:
        return jsonify({"message":"Kunde mit dieser ID existiert nicht"}), 404
    cur.execute('DELETE FROM customers WHERE id = ?', (customer_id,) )
    ## Achtung: Nutz bitte die ?-Funktion, um SQL-Injection zu verhindern, sonst sähe es so aus:
    # cur.execute(f'DELETE FROM customers WHERE id = {customer_id}') # 4 OR 1=! --
    con.commit()
    con.close()
    return jsonify({"message": "Kunde wurde erfolgreich geloescht"}), 200

## PUT-Route , Einen Kunden-Datensatz ersetzen
@app.route("/api/customers/<int:customer_id>", methods=['PUT'])
def put_customer(customer_id):
    
    updated_customer = request.get_json() # Speichere dir das Objekt im Body aus dem Request des Clients
    if not updated_customer or 'name' not in updated_customer:
        return jsonify({"message": "Fehlende Daten"}), 400
    # Überprüfe, ob der Kunde überhaupt existiert in der DB mit dieser ID
    con = get_db_connection() # Schritt 1
    cur = con.cursor() # Schritt 2
    # Schritt 3
    customer = cur.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    if customer is None:
        return jsonify({"message":"Kunde mit dieser ID nicht in der DB gefunden"}), 404
    
    # Update jetzt den Kunden mit der übergebenen ID und mit den übergebenen Daten
    cur.execute('UPDATE customers SET name = ?, email = ?, loyalty_points = ? WHERE id = ?', (updated_customer['name'], updated_customer['email'], updated_customer['loyalty_points'], customer_id))
    con.commit()
    con.close()
    return jsonify({"message": "Kunden-Datensatz wurde erfolgreich ersetzt"}), 200

## PATCH-Route -> Ersetze spezifisch einzelne Eigenschaften, d.h. hier schicken wir nur die zu ändernden Eigenschaften im Body als JSON mit
@app.route("/api/customers/<int:customer_id>", methods=["PATCH"])
def patch_customer(customer_id):
    """
    KD-Datensatz teilweise ändern (z.B. nur den Type)
    ---
     parameters:
        - name: name
          in: path
          type: string
          required: true
          description: Der Name des Types, der ersetzt werden soll
        - in: body
          name: type
          required: anyOf
          schema: 
            type: object
            properties:
                id:
                    type: integer
                    example: 3
                name:
                    type: string
                    example: Tim Werner
                email:
                    type: string
                    example: timwerner@outlook.de
                loyalty-points:
                    type: integer
                    example: 100
     responses:
        200:
            description: KD-Datensatz wurde geupdated
            examples:
                application/json:
                    - message: KD-Datensatz wurde geupdated
        404:
            description: KD-Datensatz wurde nicht gefunden
            examples:
                application/json:
                    - message: KD-Datensatz wurde nicht gefunden

    """
    updated_customer = request.get_json() # name, email loyalty-points
    if not updated_customer:
        return jsonify({"message": "Fehlende Daten"}), 400
    con = get_db_connection()
    cur = con.cursor()
    customer = cur.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    if customer is None:
        return jsonify({"message":"Kunden mit dieser ID nicht in der DB gefunden"}), 404
    # Leere Liste, wo wir die Felder mitgeben, die wir speziell updaten wollen
    update_fields = [] # Notizzettel, wo wir alle Spalten reinschreiben, die der Client updaten möchte, z.B. nur name: Testuser1, email testuser@testhausen.de
    # Leere Liste, wo wir die Werte der Felder mitgeben, die wir updaten wollen
    update_values = [] # Notizzettel, wo wir die entsprechenden Werte reinschreiben von den Spalten, die wir aktualisieren wollen

    for field in ['name', 'email', 'loyalty_points']: # Iteriere über alle möglichen, vorhandenen Spalte der Tabelle
        if field in updated_customer:
            update_fields.append(f'{field} = ?') # name = ?, email = ?
            update_values.append(updated_customer[field]) # Name Testmann, Mustermann
    
    if update_fields:
        update_values.append(customer_id)
        query = f'UPDATE customers SET {", ".join(update_fields)} WHERE id = ?' # UPDATE customers SET name = ?, email = ? WHERE id = ?
        cur.execute(query, update_values)
        con.commit()
    con.close()
    return jsonify({"message": "KD-Datensatz wurde erfolgreich geupdatet"}), 200

######################## BESTELLUNGEN-CRUDs ############################
@app.route("/api/orders", methods=["POST"])
def create_order():
    """
    Neue Bestellung erstellen
    ---
    parameters:
      - in: body
        name: Bestellung
        schema:
          type: object
          properties:
            customer_id:
              type: integer
              example: 1
            flavour_id:
              type: integer
              example: 2
            quantity:
              type: integer
              example: 3
    responses:
      201:
        description: Bestellung wurde erfolgreich erstellt
      400:
        description: Ungültige Eingabedaten
    """
    data = request.get_json()
    if not data or not all(k in data for k in ("customer_id", "flavour_id", "quantity")):
        return jsonify({"message": "Ungültige Eingabe"}), 400

    customer_id = data["customer_id"]
    flavour_id = data["flavour_id"]
    quantity = data["quantity"]

    con = get_db_connection()
    cur = con.cursor()

    # Preis pro Kugel abfragen
    cur.execute("SELECT price_per_serving FROM Flavours WHERE id = ?", (flavour_id,))
    row = cur.fetchone()
    if row is None:
        con.close()
        return jsonify({"message": "Flavour nicht gefunden"}), 404

    price_per_serving = row["price_per_serving"]
    total_price = round(quantity * price_per_serving, 2)

    # Bestellung einfügen
    cur.execute(
        "INSERT INTO Orders (customer_id, flavour_id, quantity, total_price) VALUES (?, ?, ?, ?)",
        (customer_id, flavour_id, quantity, total_price)
    )
    con.commit()
    con.close()

    return jsonify({"message": "Bestellung erstellt", "total_price": total_price}), 201



# Bestellungen eines Kunden anzeigen 
@app.route("/api/customers/<int:customer_id>/orders", methods=["GET"])
def get_orders_customer(customer_id):
    """
    Alle Bestellungen eines Kunden
    ---
    parameters:
        - name: customer_id
        in: path
        required: true
        type: integer
    responses:
        200:
          description: Liste aller Bestellungen des Kunden
    """
    con = get_db_connection()
    cur = con.cursor()

    query = """
        SELECT 
            Orders.id AS order_id,
            Flavours.name AS flavour,
            Orders.quantity,
            Orders.total_price
        FROM Orders
        JOIN Flavours ON Orders.flavour_id = Flavours.id
        WHERE Orders.customer_id = ?
    """

    orders = cur.execute(query, (customer_id,)).fetchall()
    con.close()

    return jsonify([dict(order) for order in orders]), 200


# Bestellung erstellen + Gesamtpreis berechnen  
#@app.route("/api/customers/<int:customer_id>/orders")
#def customer_orders(customer_id):
#   """Alle Bestellungen eines Kunden"""
# JOIN zwischen customers, orders und flavours



# App starten
if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
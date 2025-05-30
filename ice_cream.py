from flask import Flask, jsonify, request
from flasgger import Swagger 
import sqlite3


app = Flask(__name__)
swagger = Swagger(app)

DATABASE = "./ice_cream.db"

def get_db_connection():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_db_connection
    cur = con.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS Flavours (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    typ TEXT NOT NULL,
                    price_per_serving REAL
                )
                ''')
    count = cur.execute('SELECT COUNT(*) FROM flavours').fetchone()[0]
    if count == 0:
        data = [
            ('schoko', 'milch', 1.80),
            ('zitrone', 'frucht', 2.80),
            ('vanille', 'kokos', 3.80)
        ]
        cur.executmany('INSERT INTO flavours (name, type, price_per_serving) VALUES (?,?,?)', data)
        con.commit()
    con.close()


@app.route('/api/flavours', methods=["GET"])
def get_flavours(flavour_id):
    """
    Liste aller Geschmackssorten
    ---
    # hier Swagger Docs rein
    """
    con = get_db_connection()
    cur = con.cursor()
    flavour = cur.execute('SELECT * FROM Flavours WHERE id = ?', (flavour_id,)).fetchone()
    if flavour is None:
        return jsonify({"message": "there is no such flavour"}), 404
    con.commit()
    con.close()
    return jsonify(dict(flavour)), 200

@app.route('/api/flavours/<int:flavour_id>', methods=["GET"])
def get_single_flavour(flavour_id):
    


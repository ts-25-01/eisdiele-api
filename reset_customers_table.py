import sqlite3

def reset_table():
    con = sqlite3.connect("ice_cream.db")  # Passe ggf. den Pfad an
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS customers;")
    cur.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            loyalty_points INTEGER DEFAULT 0
        );
    """)
    con.commit()
    con.close()
    print("Tabelle erfolgreich neu erstellt.")

if __name__ == "__main__":
    reset_table()

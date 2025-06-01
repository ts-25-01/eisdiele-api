#@app.route("/debug/check_indexes")
#def check_indexes():
#    con = get_db_connection()
#    cur = con.cursor()
#    cur.execute("PRAGMA index_list(customers)")
#    indexes = cur.fetchall()
#    return jsonify(indexes)

#@app.route("/debug/table_info")
#def table_info():
#    con = get_db_connection()
#    cur = con.cursor()
#    cur.execute("PRAGMA table_info(customers)")
#    info = cur.fetchall()
#    return jsonify(info)
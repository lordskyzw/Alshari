import sqlite3


def query_db_for_plate(plate_number):
    # Query the database to recognize the plate number
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM plates WHERE plate_number=?", (plate_number,))
    result = c.fetchone()
    conn.close()
    if result:
        return result
    else:
        return None

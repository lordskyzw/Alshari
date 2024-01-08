import sqlite3
import requests
import logging

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


def handle_rfid_scan(rfid_tag):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Check if the RFID tag exists in the database
    c.execute("SELECT employee_name FROM rfid_tags WHERE rfid_tag = ?", (rfid_tag,))
    employee = c.fetchone()

    if employee:
        employee_name = employee[0]
        # Log the entry by sending a POST request to the Flask server
        response = requests.post(url='http://127.0.0.1:5000/record_rfid', json={'employee': employee_name})
        if response.status_code == 200:
            logging.info("Entry logged successfully for %s", employee_name)
        else:
            logging.error("Error logging entry for %s", employee_name)
    else:
        logging.error("RFID tag %s not found in the database", rfid_tag)

    conn.close()
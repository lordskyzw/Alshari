################################################ This is the barebones of the app. ########################################################

from roboflow import Roboflow
from utils.ocr import text_extractor, get_license_plate_region
from utils.dbops import query_db_for_plate
import serial, sqlite3, cv2
import logging
import requests

def setup():
    ###################################################### ROBOFLOW OPERATIONS ######################################################
    robo_api_key = "" #stored in Documents/api_keys
    workspace_name = "myfirstworkspace"
    project_name = "alshari"
    version_number = "1"
    rf = Roboflow(api_key=robo_api_key)
    project = rf.workspace(workspace_name).project(project_name)
    model = project.version(version_number).model


    ###################################################### ARDUINO OPERATIONS ######################################################
    # Open a serial connection to ESP32
    arduino_port = "COMX"  # Replace "COMX" with the actual port ESP32 is connected to
    arduino_baudrate = 9600  # Use the baud rate configured on the Arduino
    ser = serial.Serial(arduino_port, arduino_baudrate, timeout=1)


    ##################################################### DATABASE OPERATIONS ######################################################
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS plates (plate_number text, owner text)''')
    conn.commit()
    conn.close()
    
    return (model, ser)

###################################################### APP LOGIC ######################################################


def mainloop(model, ser):
    
    while True:
    # Read from the serial port
    if ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        if line == "Vehicle detected":
            vehicle_present = True
        else:
            vehicle_present = False
    
    if vehicle_present:
        ret, frame = cap.read()
        
        if ret:
            cv2.imwrite("live.jpg", frame)
            for attempt in range(max_attempts):
                
                prediction = model.predict("live.jpg")
                for pred in prediction.predictions:

                    plate_region = get_license_plate_region(image="live.jpg", prediction=pred)
                    cv2.imwrite("plate_region.jpg", plate_region)
                    try:
                        plate_number = text_extractor(image_path="plate_region.jpg")
                        result = query_db_for_plate(plate_number=plate_number)
                        
                        if result:
                            ser.write(b'OPEN_GATE\n')
                            # record the entry in the db
                            response = requests.post(url='http://127.0.0.1:5000/record_entry', json={'plate': plate_number})
                            if response.status_code == 200:
                                #send a message to the owner of the premise to notify them of the entry
                                pass
                            else:
                                logging.error("Failed to record entry")
                
                        else:
                            #send a message to the owner of the premise to notify them of the new visitor
                            pass
                        
                    except Exception as e:
                        logging.error(e)
                        logging.error("Failed to recognize plate number. Retrying...")
                        continue
        else:
            continue


if __name__ == "__main__":
    model, ser = setup()
    cap = cv2.VideoCapture('rtsp://your_camera_ip:554/live/main/av_stream')
    mainloop(model=model, ser=ser)
    
    
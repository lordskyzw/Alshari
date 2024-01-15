################################################ This is the barebones of the app. ########################################################
import threading, logging, requests
from roboflow import Roboflow
from utils.ocr import text_extractor, get_license_plate_region, is_image_clear
from utils.dbops import query_db_for_plate, handle_rfid_scan
from utils.anon import new_arrival
import serial, sqlite3, cv2
from datetime import datetime
import redis


def setup():
    ###################################################### ROBOFLOW OPERATIONS ######################################################
    robo_api_key = "Oi9c0U3HvSRVsLSqzxZE" #stored in Documents/api_keys
    workspace_name = "myfirstworkspace"
    project_name = "alshari"
    version_number = "1"
    rf = Roboflow(api_key=robo_api_key)
    project = rf.workspace(workspace_name).project(project_name)
    model = project.version(version_number).model


    ###################################################### ARDUINO OPERATIONS ######################################################
    arduino_port = "COM4"  
    arduino_baudrate = 115200
    ser = serial.Serial(arduino_port, arduino_baudrate, timeout=1)


    ##################################################### DATABASE OPERATIONS ######################################################
    conn = sqlite3.connect('interface/instance/database.db')
    c = conn.cursor()
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Table for RFID tags
    c.execute('''CREATE TABLE IF NOT EXISTS rfid_tag (
                    rfid_tag TEXT,
                    employee_name TEXT
                )''')

    conn.commit()
    conn.close()
    
    

    return (model, ser, r)



###################################################### APP LOGIC ######################################################


def mainloop(model, ser, r):
    tries = 0
    max_attempts = 5
    while True:
        
        
        vehicle_present = False
        # Read from the serial port
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            
            if line == "Vehicle detected":
                vehicle_present = True
                with open("log.txt", "a") as f:
                    f.write(f"Vehicle detected at {datetime.now()}\n")
                print(line)
            elif line.startswith("RFID:"):
                rfid_tag = line.split("RFID:")[1].strip()
                with open("log.txt", "a") as f:
                    f.write(f"RFID tag scanned at {datetime.now()}\n")
                handle_rfid_scan(rfid_tag)
                
        
        if vehicle_present:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            
            if ret:
                cv2.imwrite("live.jpg", frame)
                
                if is_image_clear("live.jpg"):
                    cap.release()
                    prediction = model.predict("live.jpg")
                    
                    if prediction.predictions == []:
                        print("No prediction")
                        tries = tries-1
                        continue
                    
                    else:
                    
                        for pred in prediction.predictions:

                            plate_region = get_license_plate_region(image="live.jpg", prediction=pred)
                            cv2.imwrite("plate_region.jpg", plate_region)
                            try:
                                plate_number = text_extractor(image_path="plate_region.jpg")
                                new_gate_approach = new_arrival(r=r, number_plate=plate_number, current_time=(datetime.now()))
                                
                                if new_gate_approach:
                                    result = query_db_for_plate(plate_number=plate_number)
                                    
                                    if result:
                                        ser.write(b'OPEN_GATE\n')
                                        response = requests.post(url='http://127.0.0.1:5000/record_entry', json={'plate': plate_number})
                                        
                                        if response.status_code == 200:
                                            with open('logs.txt', 'a') as logs:
                                                logs.write(str(response.status_code))
                                        else:
                                            with open('error_logs.txt', 'a') as err_logs:
                                                err_logs.write(str(response.status_code))
                            
                                    else:
                                        with open("log.txt", "a") as f:
                                            f.write(f"Unrecognized vehicle detected at {datetime.now()}\nPlate number: {plate_number}\n")
                                        # ring buzzer and initiate an intercom call (to be added when i get extra hardware)
                                else:
                                    # not a new approach and the sensor is acting up
                                    tries= tries-1
                                    continue
                                
                            except Exception as e:
                                logging.error(e)
                                logging.error("Failed to recognize plate number. Retrying...")
                                with open("log.txt", "a") as f:
                                    f.write(f"=====================Error in the TRY block at {datetime.now()}\nError: {e}\n=====================\n")  
                                continue
                else:
                    tries = tries-1
                    continue
            else:
                continue
        else:
            continue

if __name__ == "__main__":
    model, ser, r = setup()
    mainloop_thread = threading.Thread(target=mainloop, args=(model, ser, r))
    mainloop_thread.start()
    
    
################################################ This is the barebones of the app. ########################################################
import threading, logging, requests
from roboflow import Roboflow
from utils.ocr import text_extractor, get_license_plate_region, is_image_clear
from utils.dbops import query_db_for_plate, handle_rfid_scan
from utils.anon import new_arrival
import serial, sqlite3, cv2
from datetime import datetime
from time import sleep
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
                          

def mainloop(model, ser: serial.Serial, r: redis.Redis):
    while True:
        
        vehicle_present = False
        # Read from the serial port
        if ser.in_waiting:
            line = ser.readline().decode('iso-8859-1').rstrip()
            
            if line.lower() == "vehicle detected":
                vehicle_present = True
                with open("log.txt", "a") as f:
                    f.write(f"Vehicle detected at {datetime.now()}\n")
                print(line)
                try:
                    handle_vehicle_present(vehicle_present=vehicle_present, model=model, r=r)
                except Exception as e:
                    logging.error(e)
                    logging.error("Failed to handle vehicle present. Retrying...")
                    with open("log.txt", "a") as f:
                        f.write(f"=====================Error in TRYING HANDLE_VEHICLE_PRESENT() at {datetime.now()}\nError: {e}\n=====================\n")
                    continue
            elif line.lower().startswith("rfid:"):
                rfid_tag = line.split("RFID:")[1].strip()
                with open("log.txt", "a") as f:
                    f.write(f"RFID tag scanned at {datetime.now()}\n")
                handle_rfid_scan(rfid_tag)
        ser.reset_input_buffer()
                
        
######################################################### HANDLE VEHICLE PRESENT ######################################################       
        
        
def handle_vehicle_present(vehicle_present: bool, model, r: redis.Redis):
            if vehicle_present:
                cap = cv2.VideoCapture(1)
                ret, frame = cap.read()
        
                if ret:
                    cv2.imwrite("live.jpg", frame)
                    print("Image captured in line 92")
        
                    if is_image_clear("live.jpg"):
                        cap.release()
                        try:
                            prediction = model.predict("live.jpg")
                        except Exception as e:
                            print(f"Error during prediction: {e}")
                            exit(1)
                        prediction_tries = 0
                        while prediction_tries <= 3 and prediction.predictions == []:
                            if prediction.predictions == []:
                                print("no predictions, trying again, we are at try number: ", prediction_tries + 1)
                                cap = cv2.VideoCapture(1)
                                ret, frame = cap.read()
                        
                                if ret:
                                    cv2.imwrite("live.jpg", frame)
                                    print("Image captured in line 110")
                                    cap.release()
                                    if is_image_clear("live.jpg"):
                                        try:
                                            prediction = model.predict("live.jpg")
                                        except Exception as e:
                                            print(f"Error during prediction: {e}")
                                            exit(1)
                                prediction = model.predict("live.jpg")
                                prediction_tries += 1
                            else:
                                break
                        if prediction_tries > 3 and prediction.predictions == []:
                            print("We have tried 3 times and we still have no predictions but opening and closing boom gate to show functionality")
                            ser.write(b'openGate\n')
                            sleep(5)
                            ser.write(b'closeGate\n')
                            return
        
                        for pred in prediction.predictions:
    
                            plate_region = get_license_plate_region(image="live.jpg", prediction=pred)
                            cv2.imwrite("plate_region.jpg", plate_region)
                            try:
                                plate_number = text_extractor(image_path="plate_region.jpg")
                                new_gate_approach = new_arrival(r=r, number_plate=plate_number, current_time=(datetime.now()))
    
                                if new_gate_approach:
                                    result = query_db_for_plate(plate_number=plate_number)
    
                                    if result:
                                        ser.write(b'openGate\n')
                                        try:
                                            response = requests.post(url='http://127.0.0.1:5000/record_entry', json={'plate': plate_number})
                                        except Exception as e:
                                            logging.error(e)
                                            logging.error("Failed to send request to the server. Retrying...")
                                            with open("log.txt", "a") as f:
                                                f.write(f"=====================Error in TRYING TO SEND REQUEST at {datetime.now()}\nError: {e}\n=====================\n")
                                            continue
    
                                        if response.status_code == 200:
                                            with open('logs.txt', 'a') as logs:
                                                logs.write(str(response.status_code))
                                        else:
                                            with open('error_logs.txt', 'a') as err_logs:
                                                err_logs.write(str(response.status_code))
    
                                    else:
                                        with open("log.txt", "a") as f:
                                            f.write(f"Unrecognized vehicle detected at {datetime.now()}\nPlate number: {plate_number}\n")
                                            print("Unrecognized vehicle detected")
                                        # ring buzzer and initiate an intercom call (to be added when i get extra hardware)
                                else:
                                    # not a new approach and the sensor is acting up
                                    continue
    
                            except Exception as e:
                                logging.error(e)
                                logging.error("Failed to recognize plate number. Retrying...")
                                with open("log.txt", "a") as f:
                                    f.write(f"=====================Error in the TRY block at {datetime.now()}\nError: {e}\n=====================\n")
                                continue
                    else:
                        # image is not clear
                        print("image is not clear and entering the else statement in line 170")
                        ret, frame = cap.read()
                        handle_vehicle_present(vehicle_present=vehicle_present, model=model, r=r)
                else:
                    # camera is not working
                    print("camera is not working we are now exiting the function")
                    exit(1)
            else:
                # vehicle is not present
                print("There is no vehicle present")
                return
                    

# Run the app
if __name__ == "__main__":
    model, ser, r = setup()
    mainloop_thread = threading.Thread(target=mainloop, args=(model, ser, r))
    mainloop_thread.start()
    
    
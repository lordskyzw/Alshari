from roboflow import Roboflow
from utils.ocr import text_extractor, get_license_plate_region
from utils.dbops import query_db_for_plate
import serial, sqlite3, cv2
from time import sleep

# Constants
MAX_ATTEMPS = 3
MOTION_THRESHOLD = 100
GATE_OPEN_DELAY = 20
INTERCOM_NOTIFY_DELAY = 120

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
    # Open a serial connection to the Arduino
    arduino_port = "COMX"  # Replace "COMX" with the actual port the Arduino is connected to
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
        while True:
            ret, frame = cap.read()
            if ret:
                #captured frame so break out of the capture loop
                break
            else:
                #failed to capture frame so try again
                continue
        
        #special attention is needed here        
        fgmask = fgbg.apply(frame)
        motion_detected = cv2.countNonZero(fgmask) > MOTION_THRESHOLD  # Adjust the threshold

        if motion_detected:
            cv2.imwrite("live.jpg", frame)
            for attempt in range(MAX_ATTEMPS):
            
                prediction = model.predict("live.jpg")
                for pred in prediction.predictions:

                    plate_region = get_license_plate_region(image="live.jpg", prediction=pred)
                    cv2.imwrite("plate_region.jpg", plate_region)
                    try:
                        plate_number = text_extractor(image_path="plate_region.jpg")
                        result = query_db_for_plate(plate_number=plate_number)
                        
                        if result:
                            try:
                                with open(file='success_logs.txt', mode='a') as success_logs:
                                    success_logs.write(f'ADMITTED ========================================: {result}')
                            except Exception as e:
                                with open(file='err_logs.txt', mode='a') as err_logs:
                                    err_logs.write(str(e))
                                    err_logs.close()
                            ser.write(b'OPEN_GATE\n')
                            sleep(GATE_OPEN_DELAY)
                            continue
                        else:
                            # Send a signal to the Arduino to ring the intercom
                            ser.write(b'RING_INTERCOM\n')
                            sleep(INTERCOM_NOTIFY_DELAY)
                            pass
                        
                    except Exception as e:
                        with open(file='err_logs.txt', mode='a') as err_logs:
                            err_logs.write(str(e))
                            err_logs.close()
                        continue
        else:
            continue


if __name__ == "__main__":
    model, ser = setup()
    cap = cv2.VideoCapture('rtsp://your_camera_ip:554/live/main/av_stream')
    fgbg = cv2.createBackgroundSubtractorMOG2()
    mainloop(model=model, ser=ser)
    
    # Release the camera and close the window
    # cap.release()
    # cv2.destroyAllWindows()
    
    
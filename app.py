from roboflow import Roboflow
from utils.ocr import text_extractor, get_license_plate_region
import serial, sqlite3, cv2


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


###################################################### APP LOGIC ######################################################
cap = cv2.VideoCapture('rtsp://your_camera_ip:554/live/main/av_stream')
fgbg = cv2.createBackgroundSubtractorMOG2()

max_attempts = 3

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame.")
        break

    fgmask = fgbg.apply(frame)
    # Check if motion is detected
    motion_detected = cv2.countNonZero(fgmask) > 100  # Adjust the threshold as needed

    if motion_detected:
        cv2.imwrite("live.jpg", frame)
        for attempt in range(max_attempts):
        
            prediction = model.predict("live.jpg")
            for pred in prediction['predictions']:

                plate_region = get_license_plate_region(image="live.jpg", prediction=pred)
                cv2.imwrite("plate_region.jpg", plate_region)
                try:
                    plate_number = text_extractor(image_path="plate_region.jpg")
                
                    # Query the database to recognize the plate number
                    conn = sqlite3.connect('database.db')
                    c = conn.cursor()
                    c.execute("SELECT * FROM plates WHERE plate_number=?", (plate_number,))
                    result = c.fetchone()
                    conn.close()
                    
                    if result:
                        #if the number plate is recognized, send a signal to the microcontroller to open the gate
                        ser.write(b'OPEN_GATE\n')
                        break
                    else:
                        #send a message to the owner of the premise to notify them of the new visitor
                        pass
                    # Break the loop when a plate is successfully detected
                    break
                except Exception as e:
                    print(e)
                    print("Failed to recognize plate number. Retrying...")
                    continue

            # If a plate is detected, exit the loop
            if plate_number:
                break

        # Display the captured frame
        cv2.imshow('Number Plate Recognition', frame)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()

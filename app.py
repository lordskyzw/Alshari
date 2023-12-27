from roboflow import Roboflow
import cv2
import pytesseract


api_key = "YOUR_PRIVATE_API_KEY"
workspace_name = "YOUR_WORKSPACE"
project_name = "YOUR_PROJECT"
version_number = "VERSION_NUMBER"


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


rf = Roboflow(api_key=api_key)
project = rf.workspace(workspace_name).project(project_name)
model = project.version(version_number, local="http://localhost:9001/").model


cap = cv2.VideoCapture(0)

# Initialize the background subtractor for motion detection
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
        for attempt in range(max_attempts):
            _, image_encoded = cv2.imencode('.jpg', frame)
            image_bytes = image_encoded.tobytes()
            # Send the image to the Roboflow Inference Server for predictions
            prediction = model.predict(image_bytes)

            # Extract and process the predictions
            for pred in prediction['predictions']:
                # Extract the coordinates of the detected region
                x, y, w, h = map(int, pred['bbox'])
                
                # Extract the region containing the number plate
                plate_region = frame[y:y+h, x:x+w]
                
                # Perform OCR on the number plate region
                plate_number = pytesseract.image_to_string(plate_region, config='--psm 8')
                
                # Display the detected plate number
                print("Detected Plate Number:", plate_number)

                # Break the loop when a plate is successfully detected
                break

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

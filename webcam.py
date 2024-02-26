import cv2

# Initialize the webcam (0 is the default webcam)
cap = cv2.VideoCapture(1)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly, ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    cv2.imwrite("webcamlive.jpg", frame)
    print("Image captured")
    # Display the resulting frame
    cv2.imshow('frame', frame)
    

    break

# When everything is done, release the capture and close the windows
cap.release()
cv2.destroyAllWindows()

# License Plate Recognition System with Roboflow and OpenAI Vision Models

This project implements a License Plate Recognition (LPR) system using Roboflow for object detection and vision capable LLMs for Optical Character Recognition (OCR). The system is designed to run on a Raspberry Pi and is capable of detecting and extracting license plate numbers from video frames captured by a camera.

## Requirements

- Python 3.x
- OpenCV
- Roboflow SDK

## Setup

1. Install the required Python packages:

    ```bash
    pip install opencv-python roboflow openai
    ```

2. Set up a Roboflow account and create a project with a trained YOLOv8 model for license plate detection.

3. Replace the placeholders in the script with your Roboflow API key, workspace, project, and model version.

4. Run the script on your Raspberry Pi:

    ```bash
    python license_plate_recognition.py
    ```

## Configuration

- Adjust the camera index in the script if needed (`cap = cv2.VideoCapture(0)`).
- Fine-tune motion detection parameters (`cv2.createBackgroundSubtractorMOG2()` and `cv2.countNonZero(fgmask)`).
- Customize the number of detection attempts (`max_attempts`).

## Notes

- Ensure the script has access to the camera device (`/dev/video0` by default).
- The script will display the video feed with detected license plate numbers.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

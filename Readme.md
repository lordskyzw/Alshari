# Video Intercom System

This is a simple Flask application that streams video from a camera connected to a Raspberry Pi. The video is streamed over HTTP using the multipart/x-mixed-replace content type.

## Requirements

- Python 3.x
- Flask
- OpenCV

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/username/flask-video-streaming.git
   ```

2. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

## Usage

1. Connect a camera to the Raspberry Pi.

2. Run the Flask application:

   ```
   python app.py
   ```

3. Open a web browser and navigate to `http://<raspberry-pi-ip-address>:5000/video_feed`.

   Note: Replace `<raspberry-pi-ip-address>` with the IP address of the Raspberry Pi.

4. The video stream should start playing in the web browser.

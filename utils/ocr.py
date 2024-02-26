import os, base64, requests
import cv2

api_key=os.environ.get("OPENAI_API_KEY")


def is_image_clear(image_path, threshold=0):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    return laplacian_var > threshold


def get_license_plate_region(image_path, prediction):
    image = cv2.imread(image_path)
    x, y, width, height = map(int, (prediction.predictions[0]["x"], prediction.predictions[0]["y"], prediction.predictions[0]["width"], prediction.predictions[0]["height"]))
    plate_region = image[max(0, y-height):min(image.shape[0], y+height), max(0, x-width):min(image.shape[1], x+width)]
    cv2.imwrite("plate_region.jpg", plate_region)
    return plate_region

    
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def text_extractor(image_path):
    encoded_image = encode_image(image_path=image_path)
    
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }
    payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "return only the text in this image"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return (response.json())
import time

import cv2 as cv
import requests

from app.detect_image import show_inference
import os


def notify_image_to_line(image_path, token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": "new image"}
    files = {'imageFile': open(image_path, 'rb')}
    r = requests.post(url, headers=headers, params=payload, files=files)
    print(r.status_code, r.text)


token = os.getenv("LINE_INKO_TOKEN")
capture = cv.VideoCapture(os.getenv("WEBCOM_URL"))
timeout_second = int(os.getenv("INKO_TIMEOUT", 3600))
bird_count = int(os.getenv("BIRD_COUNT", 2))
start = time.time()
while True:
    if time.time() - start > timeout_second:
        capture.release()
        exit(0)
    ret, frame = capture.read()
    birds = show_inference(frame)
    if birds >= bird_count:
        cv.imwrite('output.jpg', frame[:, :])
        notify_image_to_line(image_path="output.jpg", token=token)
        capture.release()
        print("Program complete")
        exit(0)
    time.sleep(0.01)

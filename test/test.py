import requests
import json
import cv2


data = {'filename':'010010'}
url = "http://e8c4613c847d.ngrok.io"

resp = requests.post(f"{url}/inference_human", data=data,
                     files={"image": open('0.png','rb')})
print(resp.json())

resp = requests.post(f"{url}/inference_clothes", data=data,
                     files={"image": open('clothes104.png','rb')})

print(resp.json())
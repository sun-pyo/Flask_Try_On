from flask import Flask, jsonify, send_file, request, Response, make_response
from flask_ngrok import run_with_ngrok
import numpy as np
import cv2
import jsonpickle
import io
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import json

from clothes.clotehs_unet import Clothes_Unet


app = Flask(__name__)
run_with_ngrok(app)
imagenet_class_index = json.load(open('imagenet_class_index.json'))
model = models.densenet121(pretrained=True)
model.eval()
clothes_unet = Clothes_Unet()

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/get_image')
def get_image():
    filename = 'clothes104.jpg'
    return send_file(filename, mimetype='image/jpg')

@app.route('/api/test', methods=['POST'])
def test():
    r = request
    nparr = np.fromstring(r.data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0])
                }
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")


def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return imagenet_class_index[predicted_idx]


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['image']
        img_bytes = file.read()
        class_id, class_name = get_prediction(image_bytes=img_bytes)
        return jsonify({'class_id': class_id, 'class_name': class_name})

@app.route('/predict', methods=['GET'])
def predict_get():
    with open("clothes104.jpg", 'rb') as f:
        image_bytes = f.read()
        print(get_prediction(image_bytes=image_bytes))
    img = cv2.imread('clothes104.jpg')
    img_str = cv2.imencode('.png', img)[1].tostring()
    f = io.BytesIO()
    f.write(img_str)
    f.seek(0)
    #return Response(bytes, mimetype='image/jpeg')
    return send_file(f, mimetype='image/png')

@app.route('/image')
def image():
    img = cv2.imread('clothes104.jpg')
    data = cv2.imencode('.png', img)[1].tobytes()
    return Response(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n\r\n', 
                    mimetype='multipart/x-mixed-replace; boundary=frame')
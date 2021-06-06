from flask import Flask, send_file, request, Response, make_response, jsonify
from flask_ngrok import run_with_ngrok
import cv2
import io

import json

from .clothes.clothes_unet import Clothes_Unet
from .util.file import FileManager
from .human.openpose import OpenPose
from .human.human_parsing import Human_Parsing
from .tryon.acgpn import ACGPN

app = Flask(__name__)
run_with_ngrok(app)

filemanager = FileManager()
clothes_unet = Clothes_Unet()
openpose = OpenPose()
human_parsing = Human_Parsing()
acgpn = ACGPN()

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/clothes', methods=['POST'])
def inference_clothes():
    if request.method == 'POST':
        try:
            file = request.files['image']
            img_bytes = file.read()
        except:
            return jsonify({'msg': "Fail"})
        # get clothes filename
        filename = filemanager.get_clothes_filename()  
        # RGB image load
        image = filemanager.bytes_image_open(img_bytes)
        # save clothes image
        filemanager.save_clothes(image, filename) 

        # Generate clotehs mask
        clothes_mask = clothes_unet.predict(image)
        # save clothes mask image
        filemanager.save_mask(clothes_mask, filename)

        msg = "Success"
        return jsonify({'msg': msg, 'filename':filename})

@app.route('/clothes/<string:filename>', methods=['DELETE'])
def delete_clothes(filename):
    filemanager.remove_clothes(filename)
    return jsonify({'msg':"Delete"})

@app.route('/human', methods=['POST'])
def inference_human():
    if request.method == 'POST':
        try:
            file = request.files['image']
            img_bytes = file.read()
        except:
            return jsonify({'msg': "Fail"})
        # get human filename
        filename = filemanager.get_human_filename() 
        # RGB image load
        image = filemanager.bytes_image_open(img_bytes)
        # human image save
        filemanager.save_human(image, filename)

        # human parsing
        output_parsing = human_parsing.predict(image)
        # save output
        filemanager.save_human_parsing(output_parsing, filename)

        # human pose estimation
        json_data = openpose.predict(image)
        if json_data == None:
            filemanager.remove_human(filename)
            msg = "Fail"
        else:
            filemanager.save_pose(json_data, filename)
            msg = "Success"

        return jsonify({'msg':msg, 'filename':filename})

@app.route('/human/<string:filename>', methods=['DELETE'])
def delete_human(filename):
    filemanager.remove_human(filename)
    return jsonify({'msg':"Delete"})
    
@app.route('/result', methods=['GET'])
def tryon():
    try:
        c_name = request.args.get('c')
        h_name = request.args.get('h')
    except:
        return jsonify({'msg': "Fail"})

    try:
        clothes = filemanager.load_clothes(c_name)
        mask = filemanager.load_mask(c_name)
        human = filemanager.load_human(h_name)
        parse = filemanager.load_human_parse(h_name)
        pose = filemanager.load_pose(h_name)
    except FileNotFoundError:
        return jsonify({'msg':"Fail", 'clothes_filename':c_name, 'humna_filename' : h_name})

    input_data = {'clothes' : clothes, 'mask' : mask, 'human' : human, 'parse':parse, 'pose' : pose}

    output = acgpn.predict(input_data)
    
    img_str = cv2.imencode('.png', output)[1].tostring()
    f = io.BytesIO()
    f.write(img_str)
    f.seek(0)
    #return Response(bytes, mimetype='image/jpeg')
    return send_file(f, mimetype='image/png')

# @app.route('/image', methods=['GET'])
# def image():
#     img = cv2.imread('clothes104.jpg')
#     data = cv2.imencode('.png', img)[1].tobytes()
#     return Response(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n\r\n', 
#                     mimetype='multipart/x-mixed-replace; boundary=frame')
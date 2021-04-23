import cv2
import numpy as np
from PIL import Image
import io
import json

class FileManager:
    def __init__(self):
        self.human_root = "flaskapp/img/human"
        self.parse_root = "flaskapp/img/parse"
        self.clothes_root = "flaskapp/img/clothes"
        self.mask_root = "flaskapp/img/mask"
        self.pose_root = "flaskapp/img/pose"
        
        # self.human_file_list = []
        # self.clothes_file_list = []

        self.clothes_name = 0
        self.human_name = 0

    def bytes_image_open(image_bytes):
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('RGB')
        image = image.resize((192, 256))
        return image

    def get_clothes_filename(self):
        filename = self.clothes_name
        self.clothes_name += 1
        return str(filename)

    def get_human_filename(self):
        filename = self.human_name
        self.human_name += 1
        return str(filename)

    def save_clothes(self, image, filename):
        clothes_path = self.clothes_root + '/' + filename + '.png'
        #self.clothes_file_list.append(filename)
        cv2.imwrite(clothes_path, image)
        print(clothes_path, 'save!')

    def save_mask(self, image, filename):
        mask_path = self.mask_root + '/' + filename + '.png'
        cv2.imwrite(mask_path, image)
        print(mask_path, 'save!')

    def save_pose(self, json_data, filename):
        pose_path = self.pose_root + '/' + filename + 'json'
        with open(pose_path, 'w') as outfile:
            json.dump(json_data, outfile)
        print(pose_path, 'save!')
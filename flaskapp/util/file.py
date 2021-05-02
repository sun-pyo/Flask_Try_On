import cv2
import numpy as np
from PIL import Image
import io
import json
import os

class FileManager:
    def __init__(self):
        self.human_root = "flaskapp/img/human"
        self.parse_root = "flaskapp/img/parse"
        self.clothes_root = "flaskapp/img/clothes"
        self.mask_root = "flaskapp/img/mask"
        self.pose_root = "flaskapp/img/pose"
        
        # self.human_file_list = []
        # self.clothes_file_list = []

        self.clothes_name = len(os.listdir(self.human_root))
        self.human_name = len(os.listdir(self.clothes_root))

    def bytes_image_open(self,image_bytes):
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('RGB')
        image = image.resize((192, 256))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

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
        pose_path = self.pose_root + '/' + filename + '.json'
        with open(pose_path, 'w') as outfile:
            json.dump(json_data, outfile)
        print(pose_path, 'save!')

    def save_human(self, image, filename):
        human_path = self.human_root + '/' + filename + '.png'
        cv2.imwrite(human_path, image)
        print(human_path, 'save!')

    def save_human_parsing(self, image, filename):
        parse_path = self.parse_root + '/' + filename + '.png'
        image.save(parse_path)

    def load_clothes(self, filename):
        clothes_path = self.clothes_root + '/' + filename + '.png'
        clothes = Image.open(clothes_path).convert('RGB')
        return clothes

    def load_mask(self, filename):
        mask_path = self.mask_root + '/' + filename + '.png'
        mask = Image.open(mask_path).convert('L')
        return mask

    def load_pose(self, filename):
        pose_path = self.pose_root + '/' + filename + '.json'
        with open(pose_path, 'r') as f:
            pose_label = json.load(f)
            pose_data = pose_label['people'][0]['pose_keypoints']
            pose_data = np.array(pose_data)
            pose_data = pose_data.reshape((-1, 3))
        return pose_data

    def load_human(self, filename):
        human_path = self.human_root + '/' + filename + '.png'
        human = Image.open(human_path).convert('RGB')
        return human

    def load_human_parse(self, filename):
        parse_path = self.parse_root + '/' + filename + '.png'
        parse = Image.open(parse_path).convert('L')
        return parse

    def remove_human(self, filename):
        human_path = self.human_root + '/' + filename + '.png'
        pose_path = self.pose_root + '/' + filename + '.json'
        parse_path = self.parse_root + '/' + filename + '.png'
        if os.path.isfile(human_path):
            os.remove(human_path)
        if os.path.isfile(pose_path):
            os.remove(pose_path)
        if os.path.isfile(parse_path):
            os.remove(parse_path)
        print(f"remove human - {filename}")

    def remove_clothes(self, filename):
        clothes_path = self.clothes_root + '/' + filename + '.png'
        mask_path = self.mask_root + '/' + filename + '.png'
        if os.path.isfile(clothes_path):
            os.remove(clothes_path)
        if os.path.isfile(mask_path):
            os.remove(mask_path)
        print(f"remove clothes - {filename}")
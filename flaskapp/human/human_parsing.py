import os
import torch
import argparse
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

from torch.utils.data import DataLoader
import torchvision.transforms as transforms

import networks
import logging
from utils.transforms import transform_logits
from utils.transforms import get_affine_transform
from collections import OrderedDict
from networks.AugmentCE2P import resnet101

class Human_Parsing:
    def __init__(self, filemanager):
        self.filemanager = filemanager
        self.input_size = [473, 473]
        num_class = 20
        self.model_path = "flaskapp/model/human_parsing.pth"
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logging.info(f'Using device {self.device}')

        logging.info("Loading Human Parsing model {}".format(self.model_path))
        self.model = resnet101(num_classes=num_class, pretrained=None)
        state_dict = torch.load(self.model_path)['state_dict']
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]  # remove `module.`
            new_state_dict[name] = v
        self.model.load_state_dict(new_state_dict)
        logging.info("Human Parsing Model loaded !")
        self.model.to(device=self.device)
        self.model.eval()

        self.trans_dict = {
            0:0,
            1:1, 2:1,
            5:4, 6:4, 7:4, 
            18:5,
            19:6,
            9:8, 12:8,
            16:9,
            17:10,
            14:11,
            4:12, 13:12,
            15:13
        }

    def _xywh2cs(self, x, y, w, h):
        center = np.zeros((2), dtype=np.float32)
        center[0] = x + w * 0.5
        center[1] = y + h * 0.5
        if w > self.aspect_ratio * h:
            h = w * 1.0 / self.aspect_ratio
        elif w < self.aspect_ratio * h:
            w = h * self.aspect_ratio
        scale = np.array([w, h], dtype=np.float32)
        return center, scale

    def _box2cs(self, box):
        x, y, w, h = box[:4]
        return self._xywh2cs(x, y, w, h)
    

    def get_data(self, img):
        h, w, _ = img.shape

        # Get person center and scale
        person_center, s = self._box2cs([0, 0, w - 1, h - 1])
        r = 0
        trans = get_affine_transform(person_center, s, r, self.input_size)
        input = cv2.warpAffine(
            img,
            trans,
            (int(self.input_size[1]), int(self.input_size[0])),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0))

        input = self.transform(input)
        meta = {
            'center': person_center,
            'height': h,
            'width': w,
            'scale': s,
            'rotation': r
        }

        return input, meta



    def predict(self, img, filename):
        with torch.no_grad():
            image, meta = self.get_data(img)
            c = meta['center'].numpy()[0]
            s = meta['scale'].numpy()[0]
            w = meta['width'].numpy()[0]
            h = meta['height'].numpy()[0]

            output = self.model(image.cuda())
            upsample = torch.nn.Upsample(size=self.input_size, mode='bicubic', align_corners=True)
            upsample_output = upsample(output[0][-1][0].unsqueeze(0))
            upsample_output = upsample_output.squeeze()
            upsample_output = upsample_output.permute(1, 2, 0)  # CHW -> HWC

            logits_result = transform_logits(upsample_output.data.cpu().numpy(), c, s, w, h, input_size=self.input_size)
            parsing_result = np.argmax(logits_result, axis=2)

            output_arr = np.asarray(parsing_result, dtype=np.uint8)

            new_arr = np.full(output_arr.shape, 7)
            for old, new in self.trans_dict.items():
                new_arr = np.where(output_arr == old, new, new_arr)
            output_img = Image.fromarray(np.asarray(new_arr, dtype=np.uint8))

            self.filemanager.save_human_parsing(output_img, filename)
            return
import logging
import cv2
import numpy as np
from PIL import Image
import io

import torch
from torchvision import transforms

from unet import UNet

class Clothes_Unet:
    def __init__(self):
        self.model_path = "img/model/clothes_unet.pth"
        self.clothes_path = "img/clothes"
        self.mask_path = "img/mask"
        self.scale = 0.5
        self.out_threshold = 0.5
        self.net = UNet(n_channels=3, n_classes=1)
        logging.info("Loading Clothes Unet model {}".format(self.model_path))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logging.info(f'Using device {self.device}')
        self.net.to(device=self.device)
        self.net.load_state_dict(torch.load(self.model_path, map_location=self.device))
        logging.info("Clothes Unet Model loaded !")
        self.net.eval()

    def get_filename():
        return "1.png"

    def mask_to_image(self, mask):
        return Image.fromarray((mask * 255).astype(np.uint8))

    def img_resize(self, image, file_name,img_width = 192,img_high=256, width=256, hight=256):
        diff = (width - img_width)//2
        image = cv2.resize(image, (img_width, img_high))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(self.clothes_path + '/' + file_name + '.png')
        im = np.ones((width, hight, 3), dtype=np.uint8) * 255
        im[:, diff:diff+img_width, :] = image
        return Image.fromarray(im)

    def remove_padding(image ,img_width = 192, img_high=256, width=256, hight=256, padding_color="white"):
        diff = (width - img_width)//2
        image = image[:, diff:diff+img_width]
        k = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, k)
        return Image.fromarray(image)

    def preprocess(self, pil_img, scale):
        w, h = pil_img.size
        newW, newH = int(scale * w), int(scale * h)
        assert newW > 0 and newH > 0, 'Scale is too small'
        pil_img = pil_img.resize((newW, newH))

        img_nd = np.array(pil_img)

        if len(img_nd.shape) == 2:
            img_nd = np.expand_dims(img_nd, axis=2)

        # HWC to CHW
        img_trans = img_nd.transpose((2, 0, 1))
        if img_trans.max() > 1:
            img_trans = img_trans / 255

        return img_trans

    def predict_img(self, full_img):
        img = torch.from_numpy(self.preprocess(full_img, self.scale))

        img = img.unsqueeze(0)
        img = img.to(device=self.device, dtype=torch.float32)

        with torch.no_grad():
            output = self.net(img)

            probs = torch.sigmoid(output)
            
            probs = probs.squeeze(0)

            tf = transforms.Compose(
                [
                    transforms.ToPILImage(),
                    transforms.Resize(full_img.size[1]), 
                    transforms.ToTensor()
                ]
            )

            probs = tf(probs.cpu())
            full_mask = probs.squeeze().cpu().numpy()
        return full_mask > self.out_threshold

    def predict(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        filename = self.get_filename()
        img = self.img_resize(np.array(img), filename)

        mask = self.predict_img(full_img=img)

        result = self.mask_to_image(mask)
        result = self.remove_padding(np.array(result))
        
        output_file = self.mask_path + '/' + filename + '.png'
        result.save(output_file)
        logging.info("Mask saved to {}".format(output_file))
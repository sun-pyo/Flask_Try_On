import numpy as np
import torch
from torch.autograd import Variable

from .options.test_options import TestOptions
from .model.pix2pixHD_model import InferenceModel
from .data.data import *
import util.util as util


SIZE = 320
NC = 14

class ACGPN():
    def __init__(self, filemanager):
        self.filemanager = filemanager
        self.model_root = "flaskapp/model"
        self.opt = TestOptions().parse()
        self.opt.model_root = self.model_root
        self.model = InferenceModel()
        self.model.initialize(self.opt)
        self.fine_height = 256
        self.fine_width = 192
        self.radius = 5

    def get_data(self, c_name, h_name):
        clothes = self.filemanager.load_clothes(c_name)
        mask = self.filemanager.load_mask(c_name)

        human = self.filemanager.load_human(h_name)
        parse = self.filemanager.load_human_parse(h_name)
        pose_data = self.filemanager.load_pose(h_name)

        params = get_params(self.opt, parse.size)

        ### human parse transform
        transform_A = get_transform(
            self.opt, params, method=Image.NEAREST, normalize=False)
        parse_tensor = transform_A(parse) * 255.0

        ### human image transform
        transform_B = get_transform(self.opt, params)
        human_tensor = transform_B(human)

        ### clothes transform
        clothes_tensor = transform_B(clothes)

        ### clothes mask
        mask_tensor = transform_A(mask)

        # Pose
        point_num = pose_data.shape[0]
        pose_map = torch.zeros(point_num, self.fine_height, self.fine_width)
        r = self.radius
        im_pose = Image.new('L', (self.fine_width, self.fine_height))
        pose_draw = ImageDraw.Draw(im_pose)
        for i in range(point_num):
            one_map = Image.new('L', (self.fine_width, self.fine_height))
            draw = ImageDraw.Draw(one_map)
            pointx = pose_data[i, 0]
            pointy = pose_data[i, 1]
            if pointx > 1 and pointy > 1:
                draw.rectangle((pointx-r, pointy-r, pointx +
                                r, pointy+r), 'white', 'white')
                pose_draw.rectangle(
                    (pointx-r, pointy-r, pointx+r, pointy+r), 'white', 'white')
            one_map = transform_B(one_map.convert('RGB'))
            pose_map[i] = one_map[0]
        pose_tensor = pose_map

        input_dict = {'parse': parse_tensor, 'human': human_tensor,
                        'mask': mask_tensor, 'clothes': clothes_tensor, 
                        'pose': pose_tensor
                    }

        return input_dict

    def predict(self, c_name, h_name):
        data = self.get_data(c_name, h_name)
        mask_clothes = torch.FloatTensor(
        (data['parse'].cpu().numpy() == 4).astype(np.int))
        mask_fore = torch.FloatTensor(
            (data['parse'].cpu().numpy() > 0).astype(np.int))
        mask_back = torch.FloatTensor(
            (data['parse'].cpu().numpy() == 0).astype(np.int))

        img_fore = data['human'] * mask_fore
        img_back = data['human'] * mask_back

        all_clothes_label = changearm(data['parse'])

        ############## Forward Pass ######################
        fake_image, warped_cloth, refined_cloth = self.model(Variable(data['parse'].cuda()), Variable(data['mask'].cuda()), 
                                            Variable(img_fore.cuda()), Variable(mask_clothes.cuda()), 
                                            Variable(data['clothes'].cuda()), Variable(all_clothes_label.cuda()), 
                                            Variable(data['human'].cuda()), Variable(data['pose'].cuda()), 
                                            Variable(data['human'].cuda()), Variable(mask_fore.cuda()))


        # Restore Background 
        fake_image = fake_image*mask_fore.cuda() + img_back.cuda()

        output = util.tensor_to_image(fake_image)
        return output
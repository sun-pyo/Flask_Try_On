import sys
sys.path.append('../')

import cv2
from openpose.body.estimator import BodyPoseEstimator
from openpose.utils import draw_body_connections, draw_keypoints
import numpy as np
import torch
import json 

class OpenPose:
    def __init__(self, filemanager):
        self.model = BodyPoseEstimator(pretrained=True)
        self.filemanager = filemanager
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(device=self.device)
        self.model.eval()


    def predict(self, image, filename):
        keypoints = self.model(image.to(device=self.device))
        pose_keypoints = []

        if len(keypoints) > 0:
            for keypoint in keypoints[0]:
                pose_keypoints.append(keypoint[0].astype(float))
                pose_keypoints.append(keypoint[1].astype(float))
                pose_keypoints.append(keypoint[2].astype(float))

            json_data = {"version": 1.0, "people": [
                        {"person_id": [-1],
                        "face_keypoints":[],
                        "pose_keypoints":[pose_keypoints],
                        "hand_right_keypoints": [], 
                        "hand_left_keypoints":[],
                        }]}

            self.filemanager.save_pose(json_data, filename)
        else:
            self.filemanager.remove_human(filename)

import sys
sys.path.append('../')

import cv2
from openpose.body.estimator import BodyPoseEstimator
from openpose.utils import draw_body_connections, draw_keypoints
import numpy as np
import json 

class OpenPose:
    def __init__(self):
        self.model = BodyPoseEstimator(pretrained=True)
        self.pose_path = 'flasapp/img/pose'

    def get_filename(self):
        return "1"

    def predict(self, image, filename):
        keypoints = self.model(image)
        pose_keypoints = []

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

        with open(self.pose_path + filename, 'w') as outfile:
            json.dump(json_data, outfile)

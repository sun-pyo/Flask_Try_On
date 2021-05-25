import sys
sys.path.append('../')

from openpose.body.estimator import BodyPoseEstimator


class OpenPose:
    def __init__(self):
        self.model = BodyPoseEstimator(pretrained=True)

    def predict(self, image):
        keypoints = self.model(image)
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
            return json_data 
        else:
            return None
        

#!/usr/bin/python
# coding: utf8

import sys
import os
sys.path.append((os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+ '/common/'))
import time
from face import FaceDetection
import cv2
from config import MMConfig
import signal



MMConfig.toNode("status", "Facerecognition started...")

current_user = None
last_match = None
detection_active = True
login_timestamp = time.time()
same_user_detected_in_row = 0

# Load training data into model
MMConfig.toNode("status", 'Loading training data...')

# load the model
model = cv2.face.LBPHFaceRecognizer_create(threshold=MMConfig.getThreshold())

# Load training file specified in config.js
model.read(MMConfig.getTrainingFile())
MMConfig.toNode("status", 'Training data loaded!')

# get camera
camera = MMConfig.getCamera()

def shutdown(self, signum):
    MMConfig.toNode("status", 'Shutdown: Cleaning up camera...')
    camera.stop()
    quit()

signal.signal(signal.SIGINT, shutdown)

# sleep for a second to let the camera warm up
time.sleep(1)

face = MMConfig.getFaceDetection()

while True:
    time.sleep(MMConfig.getInterval())
    if detection_active is True:
        image = camera.read()
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        result = face.detect_single(image)
        if result is None:
            if (current_user is not None and time.time() - login_timestamp > MMConfig.getLogoutDelay()):
                MMConfig.toNode("logout", {"user": current_user})
                same_user_detected_in_row = 0
                current_user = None
            continue
        x, y, w, h = result
        crop = face.crop(image, x, y, w, h,int(MMConfig.getFaceFactor() * w))
        label, confidence = model.predict(crop)
        if (label != -1 and label != 0):
            login_timestamp = time.time()
            if (label == last_match and same_user_detected_in_row < 2):
                # if same user as last time increment same_user_detected_in_row +1
                same_user_detected_in_row += 1
            if label != last_match:
                # if the user is diffrent reset same_user_detected_in_row back to 0
                same_user_detected_in_row = 0
            # A user only gets logged in if he is predicted twice in a row minimizing prediction errors.
            if (label != current_user and same_user_detected_in_row > 1):
                current_user = label
                # Callback current user to node helper
                MMConfig.toNode("login", {"user": label, "confidence": str(confidence)})
            # set last_match to current prediction
            last_match = label
        elif (current_user != 0 and time.time() - login_timestamp > 5):
            login_timestamp = time.time()
            current_user = 0

            MMConfig.toNode("login", {"user": current_user, "confidence": None})
        else:
            continue

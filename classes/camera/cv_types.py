"""
Some classes and type aliases that imitate the structure of OpenCV types such as VideoCapture
"""

import cv2

class VideoCapture:
    def read() -> cv2.Mat:
        ...
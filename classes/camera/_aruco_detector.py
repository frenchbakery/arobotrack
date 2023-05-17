
#! /usr/local/bin/python3

# Based on information from: https://pyframesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/

import cv2
import numpy as np
from ..utilities import Vec2
from .marker import Marker


# ArUco dictionary name to object map
ARUCO_DICTS = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

COLOR_ACCEPTED = (0, 255, 0)
COLOR_REJECTED = (0, 0, 255)


class ArucoDetector:
    def __init__(self, aruco_dict_type):
        print(type(aruco_dict_type))
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
        self.aruco_parameters = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_parameters)
        self.markers: dict[int, Marker] = {}

    def process_detected_markers(self, frame, corners, ids):
        # process the results
        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            # loop over the detected ArUCo corners
            for (marker_corner, marker_id) in zip(corners, ids):
                # extract the marker corners (which are always returned in
                # top-left, top-right, bottom-right, and bottom-left order)
                corners = marker_corner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
                # convert each of the (x, y)-coordinate pairs to integers
                top_left = Vec2(int(topLeft[0]), int(topLeft[1]))
                top_right = Vec2(int(topRight[0]), int(topRight[1]))
                bottom_left = Vec2(int(bottomLeft[0]), int(bottomLeft[1]))
                bottom_right = Vec2(int(bottomRight[0]), int(bottomRight[1]))
                    
                if marker_id not in self.markers:
                    self.markers[marker_id] = Marker(marker_id)
                
                current_marker = self.markers[marker_id]
                current_marker.move((top_left, top_right, bottom_left, bottom_right))


    def process_rejected_markers(self, frame, corners):
        # process the results
        if len(corners) > 0:
            # loop over the detected ArUCo corners
            for marker_corner in corners:
                # extract the marker corners (which ar returned in
                # top-left, top-right, bottom-right, and bottom-left order)
                current_corners = marker_corner.reshape((4, 2))
                #(topLeft, topRight, bottomRight, bottomLeft) = current_corners
                (topLeft, topRight,  bottomRight, bottomLeft) = current_corners
                # convert each of the (x, y)-coordinate pairs to integers
                top_left = Vec2(int(topLeft[0]), int(topLeft[1]))
                top_right = Vec2(int(topRight[0]), int(topRight[1]))
                bottom_left = Vec2(int(bottomLeft[0]), int(bottomLeft[1]))
                bottom_right = Vec2(int(bottomRight[0]), int(bottomRight[1]))

                for _, marker in self.markers.items():
                    if marker.maybe_move((top_left, top_right, bottom_left, bottom_right)):
                        break
    
    def detect(self, frame: np.ndarray):
        (corners, ids, rejected) = self.aruco_detector.detectMarkers(frame)
        
        self.process_detected_markers(frame, corners, ids)
        self.process_rejected_markers(frame, rejected)
    
    def draw_markers_on_frame(self, frame: np.ndarray):
        color = COLOR_ACCEPTED

        for _, marker in self.markers.items():
            cv2.line(frame, marker.top_left.icart, marker.top_right.icart, color, 2)
            cv2.line(frame, marker.top_right.icart, marker.bottom_right.icart, color, 2)
            cv2.line(frame, marker.bottom_right.icart, marker.bottom_left.icart, color, 2)
            cv2.line(frame, marker.bottom_left.icart, marker.top_left.icart, color, 2)
            cv2.circle(frame, marker.center.icart, 4, (0, 255, 0), -1)
            cv2.putText(frame, str(marker.id),
                (marker.top_left - Vec2(15, 15)).icart, cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2)



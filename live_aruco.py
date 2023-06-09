#! /usr/local/bin/python3

# Based on information from: https://pyframesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/

import argparse
import imutils
import cv2
import sys
from classes.utilities import Vec2
from classes.camera import Marker
import numpy as np


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


markers: dict[int, Marker] = {}


tracked_id: int = 0
points: list[Vec2] = []
trace_length = 100



COLOR_ACCEPTED = (0, 255, 0)
COLOR_REJECTED = (0, 0, 255)



def processDetectedMarkers(frame, corners, ids):
    # process the results
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned in
            # top-left, top-right, bottom-right, and bottom-left order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = Vec2(int(topRight[0]), int(topRight[1]))
            bottomRight = Vec2(int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = Vec2(int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = Vec2(int(topLeft[0]), int(topLeft[1]))
            # draw the bounding box of the ArUCo marker
            cv2.line(frame, topLeft.icart, topRight.icart, COLOR_ACCEPTED, 2)
            cv2.line(frame, topRight.icart, bottomRight.icart, COLOR_ACCEPTED, 2)
            cv2.line(frame, bottomRight.icart, bottomLeft.icart, COLOR_ACCEPTED, 2)
            cv2.line(frame, bottomLeft.icart, topLeft.icart, COLOR_ACCEPTED, 2)
            # compute and draw the center (x, y)-coordinates of the ArUco
            # marker
            center = Vec2.between(topLeft, bottomRight)
            cv2.circle(frame, center.icart, 4, (0, 0, 255), -1)
                
            if markerID not in markers:
                markers[markerID] = Marker(markerID)
            else:
                markers[markerID].move(center)

            # draw the ArUco marker ID on the frame
            cv2.putText(frame, str(markerID),
                (topLeft - Vec2(0, 15)).icart, cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)
            #print("[INFO] ArUco marker ID: {}".format(markerID))

def processRejectedMarkers(frame, corners):
    # process the results
    if len(corners) > 0:
        # loop over the detected ArUCo corners
        for markerCorner in corners:
            # extract the marker corners (which are always returned in
            # top-left, top-right, bottom-right, and bottom-left order)
            current_corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = current_corners
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = Vec2(int(topRight[0]), int(topRight[1]))
            bottomRight = Vec2(int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = Vec2(int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = Vec2(int(topLeft[0]), int(topLeft[1]))

            # compute and draw the center (x, y)-coordinates of the ArUco
            # marker
            center = Vec2.between(topLeft, bottomRight)
            cv2.circle(frame, center.icart, 4, (0, 255, 0), -1)

            markerID: int = None

            for id, marker in markers.items():
                if marker.maybe_move(center):
                    markerID = id
                    break

            color = COLOR_REJECTED            
            if markerID is not None:
                color = COLOR_ACCEPTED
                

            # draw the bounding box of the ArUCo marker
            cv2.line(frame, topLeft.icart, topRight.icart, color, 2)
            cv2.line(frame, topRight.icart, bottomRight.icart, color, 2)
            cv2.line(frame, bottomRight.icart, bottomLeft.icart, color, 2)
            cv2.line(frame, bottomLeft.icart, topLeft.icart, color, 2)




def sharpen_image(image: np.ndarray) -> np.ndarray:
    """
    sharpen an image (in form of a np.ndarray)
    :param image: input image
    :return: processed image
    """
    # Define the kernel for sharpening
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

    # Apply the kernel to the input image
    sharpened_image = cv2.filter2D(image, -1, kernel)

    return sharpened_image


def main(args: dict[str, any]):
    global tracked_id
    
    type_arg = ARUCO_DICTS.get(args["type"], None)
    if type_arg is None:
        print(f"[ERROR] ArUco dictionary '{args['type']}' is not supported or invalid")
        sys.exit(1)

    video_arg: int = 0
    if args["video"] is not None:
        video_arg = int(args["video"])

    path_arg: int = 0
    if args["path"] is not None:
        path_arg = int(args["path"])
    tracked_id = path_arg

    # initialize the camera feed
    vid = cv2.VideoCapture(video_arg)
    # initialize the aruco detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(type_arg)
    aruco_parameters = cv2.aruco.DetectorParameters()
    aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_parameters)

    while (True):
        # read a frame
        ret, frame = vid.read()
        if frame is None:
            continue

        #frame = imutils.resize(frame, height=900)

        framebw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #_, framebw = cv2.threshold(framebw, 127, 255, cv2.THRESH_BINARY)
        #framebw = cv2.fastNlMeansDenoising(framebw, None, 30, 7, 21)
        framebw = sharpen_image(framebw)

        #detect marcers
        (corners, ids, rejected) = aruco_detector.detectMarkers(framebw)
        
        processDetectedMarkers(frame, corners, ids)
        processRejectedMarkers(frame, rejected)

        # draw the path
        if len(points) > 0:
            last_point = points[0]
            for point in points:
                cv2.line(frame, last_point.icart, point.icart, (0, 127, 255), 2)
                last_point = point

        cv2.imshow("frame", frame)
        #cv2.imshow("framebw", framebw)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cv2.destroyAllWindows()
    sys.exit(0)


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", required=False,
                    help="Video ID for live tracking")
    ap.add_argument("-p", "--path", required=False,
                    help="ID of the marker whose path should be tracked")
    ap.add_argument("-t", "--type", required=True,
                    help="type (aka. dictionary) of ArUco tag to detect")
    return vars(ap.parse_args())


if __name__ == "__main__":
    main(get_args())

#! /usr/local/bin/python3

# Based on information from: https://pyframesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/

import argparse
import cv2
import sys
import numpy as np
from classes.utilities import Vec2
from classes.camera import Marker, ARUCO_DICTS
from classes.camera import FrameTracker



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
    
    detector = FrameTracker(type_arg)

    video_arg1: int = 0
    if args["video1"] is not None:
        video_arg1 = int(args["video1"])
    video_arg2: int = 0
    if args["video2"] is not None:
        video_arg2 = int(args["video2"])
    print("vid1: ", video_arg1)
    print("vid2: ", video_arg2)

    path_arg: int = 0
    if args["path"] is not None:
        path_arg = int(args["path"])
    tracked_id = path_arg

    # initialize the camera feed
    vid1 = cv2.VideoCapture(video_arg1)
    #vid2 = cv2.VideoCapture(video_arg2)

    while (True):
        # read a frame from camera 1
        ret, frame1 = vid1.read()
        if frame1 is None:
            continue
        # read a frame from camera 2
        #ret, frame2 = vid2.read()
        #if frame2 is None:
        #    continue


        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
        #frame = imutils.resize(frame, height=900)

        framebw = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        #_, framebw = cv2.threshold(framebw, 127, 255, cv2.THRESH_BINARY)
        #framebw = cv2.fastNlMeansDenoising(framebw, None, 30, 7, 21)
        framebw = sharpen_image(framebw)

        #detect marcers
        detector.detect(framebw)
        detector.draw_markers_on_frame(frame1)

        cv2.imshow("frame", frame1)
        #cv2.imshow("framebw", framebw)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cv2.destroyAllWindows()
    sys.exit(0)


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v1", "--video1", required=False,
                    help="Video ID for live tracking")
    ap.add_argument("-v2", "--video2", required=False,
                    help="Video ID for live tracking")
    ap.add_argument("-p", "--path", required=False,
                    help="ID of the marker whose path should be tracked")
    ap.add_argument("-t", "--type", required=True,
                    help="type (aka. dictionary) of ArUco tag to detect")
    return vars(ap.parse_args())


if __name__ == "__main__":
    main(get_args())

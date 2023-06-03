#! /usr/local/bin/python3 
 
# Based on information from: https://pyframesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/

import argparse
import cv2
import sys
import numpy as np

from classes.camera import ArucoDetector, CameraDevice,  CameraParams, ARUCO_DICTS
from classes.ui import MainWindow
from classes.utilities import Vec2


params_matteo = CameraParams().load("calibration/data_046d_0825/20230529_214338/params_20230529_221724.pickle")
params_signitzer = CameraParams().load("calibration/data_046d_081b/20230529_222038/params_20230529_222038.pickle")


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


def main(args: dict[str, any]) -> int:
    type_arg = ARUCO_DICTS.get(args["type"], None)
    if type_arg is None:
        type_arg = ARUCO_DICTS["DICT_4X4_50"]
    
    detector = ArucoDetector(type_arg)

    video_arg1: CameraDevice | None = None
    if args["video1"] is not None:
        video_arg1 = CameraDevice.by_video_index(int(args["video1"]))
    video_arg2: CameraDevice | None = None
    if args["video2"] is not None:
        video_arg2 = CameraDevice.by_video_index(int(args["video2"]))
    
    print("vid1: ", video_arg1)
    print("vid2: ", video_arg2)


    # start window thread
    app_window = MainWindow()


    # initialize the camera feed
    vid1 = video_arg1.open() if video_arg1 is not None else None
    vid2 = video_arg2.open() if video_arg2 is not None else None

    orig_corners = (
        Vec2(100, 150),
        Vec2(400, 20),
        Vec2(422, 422),
        Vec2(100, 300)
    )


    goal_corners = (
        Vec2(0, 0),
        Vec2(400, 0),
        Vec2(400, 400),
        Vec2(0, 400)
    )



    transform_matrix = cv2.getPerspectiveTransform(
        np.float32([v.icart for v in orig_corners]),
        np.float32([v.icart for v in goal_corners]),
    )


    print(transform_matrix)

    while (True):
        frame1: cv2.Mat
        frame2: cv2.Mat

        # read a frame from camera 1
        if vid1 is not None:
            _, frame1 = vid1.read()
            if frame1 is None:
                continue
        # read a frame from camera 2
        if vid2 is not None:
            _, frame2 = vid2.read()
            if frame2 is None:
                continue

        # exit key
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
        #frame = imutils.resize(frame, height=900)

        # camera calibration according to previously recorded values
        # for now we are assuming that camera 1 is Matteo's camera (C270) and
        # camera 2 is Signitzer's camera (C310)
        """
        if vid1 is not None:
            h1, w1 = frame1.shape[:2]
            newmatrix1, roi1 = cv2.getOptimalNewCameraMatrix(
                params_matteo.matrix, 
                params_matteo.distortion,
                (w1, h1), 0, (w1, h1)
            )
            frame1 = cv2.undistort(
                frame1,
                params_matteo.matrix,
                params_matteo.distortion,
                None, newmatrix1
            )
        if vid2 is not None:
            h2, w2 = frame2.shape[:2]
            newmatrix2, roi2 = cv2.getOptimalNewCameraMatrix(
                params_signitzer.matrix, 
                params_signitzer.distortion,
                (w2, h2), 0, (w2, h2)
            )
            frame2 = cv2.undistort(
                frame2,
                params_signitzer.matrix,
                params_signitzer.distortion,
                None, newmatrix2
            )
        """

        framebw = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        #_, framebw = cv2.threshold(framebw, 127, 255, cv2.THRESH_BINARY)
        #framebw = cv2.fastNlMeansDenoising(framebw, None, 30, 7, 21)
        framebw = sharpen_image(framebw)

        #detect marcers
        detector.detect(framebw)
        detector.draw_markers_on_frame(frame1)

        if vid1 is not None:
            warped = cv2.warpPerspective(frame1, transform_matrix, (400, 400), flags=cv2.INTER_LINEAR)

            orig_point = np.array([orig_corners[0].x, orig_corners[0].y, 1])
            print(orig_point)
            cv2.circle(frame1, orig_point[0:2], 5, (0, 128, 255))

            # Perspective transform on single coordinate mathematically:
            # https://forum.opencv.org/t/perspective-transform-on-single-coordinate/733/5

            #goal_point = np.matmul(np.linalg.inv(cv2.invert(transform_matrix)), orig_point)
            #goal_point = goal_point*(1/goal_point[2])
            # Transform a point: https://stackoverflow.com/questions/31147438/how-to-undo-a-perspective-transform-for-a-single-point-in-opencv
            goal_point = cv2.perspectiveTransform(np.array([[[100, 150]]], dtype=np.float32), transform_matrix)
            print(goal_point)
            cv2.circle(warped, np.int32(goal_point[0][0]), 5, (0, 128, 255))


            cv2.imshow("Camera 1", frame1)
            cv2.imshow("Warped Camera 1", warped)

        if vid2 is not None:
            cv2.imshow("Camera 2", frame2)
        #app_window.update_video(frame1)

        if app_window.update():
            break
        
    
    cv2.destroyAllWindows()
    return 0


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v1", "--video1", required=False,
                    help="Video ID for live tracking")
    ap.add_argument("-v2", "--video2", required=False,
                    help="Video ID for live tracking")
    ap.add_argument("-t", "--type", required=False,
                    help="type (aka. dictionary) of ArUco tag to detect")
    return vars(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main(get_args()))

#! /usr/local/bin/python3 
 
# Based on information from: https://pyframesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/

import argparse
import cv2
import sys
import numpy as np

from classes.camera import ArucoDetector, CameraDevice, CameraParams, TrackingStream, ARUCO_DICTS
from classes.ui import MainWindow
from classes.utilities import Vec2


params_matteo = CameraParams().load("calibration/data_046d_0825/20230529_214338/params_20230529_221724.pickle")
params_signitzer = CameraParams().load("calibration/data_046d_081b/20230529_222038/params_20230529_222038.pickle")
params_laptop_matteo = CameraParams().load("calibration/data_0408_5343/20230604_215358/params_20230604_215358.pickle")


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

    stream1 = TrackingStream(video_arg1, camera_params=params_laptop_matteo)
    stream1._configure_source_area(np.float32(
        [
            [468, 392],
            [133, 394],
            [195, 233],
            [415, 233]
        ]
    ))
    #stream2 = TrackingStream(video_arg2)

    while (True):
        # frame1: cv2.Mat
        # frame2: cv2.Mat

        # # read a frame from camera 1
        # if vid1 is not None:
        #     _, frame1 = vid1.read()
        #     if frame1 is None:
        #         continue
        # # read a frame from camera 2
        # if vid2 is not None:
        #     _, frame2 = vid2.read()
        #     if frame2 is None:
        #         continue

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

        # framebw = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        # #_, framebw = cv2.threshold(framebw, 127, 255, cv2.THRESH_BINARY)
        # #framebw = cv2.fastNlMeansDenoising(framebw, None, 30, 7, 21)
        # framebw = sharpen_image(framebw)

        # #detect markers
        # detector.detect(framebw)
        # detector.draw_markers_on_frame(frame1)

        # if vid1 is not None:
        #     # Geometrical transformation: https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html
        #     warped = cv2.warpPerspective(frame1, transform_matrix, (800, 400), flags=cv2.INTER_LINEAR)

        #     for corner in orig_corners:
        #         cv2.drawMarker(frame1, corner.icart, (0, 128, 255), thickness=2)

        #     # Transform a point: https://stackoverflow.com/questions/31147438/how-to-undo-a-perspective-transform-for-a-single-point-in-opencv
        #     transformed_corners: np.ndarray = cv2.perspectiveTransform(np.array([[v.icart for v in orig_corners]], dtype=np.float32), transform_matrix)
        #     for corner in transformed_corners[0]:
        #         cv2.drawMarker(warped, np.int32(corner), (0, 255, 0), thickness=2)


        #     cv2.imshow("Camera 1", frame1)
        #     cv2.imshow("Warped Camera 1", warped)

        # if vid2 is not None:
        #     cv2.imshow("Camera 2", frame2)
        # #app_window.update_video(frame1)

        frame1 = stream1.update()
        #frame2 = stream2.update()
        #both = np.concatenate((frame1, frame2), axis=1)
        cv2.imshow("Camera 1", frame1)
        #cv2.imshow("Camera 2", frame2)
        #cv2.imshow("Both", both)

        if app_window.update():
            break
        
    
    cv2.destroyAllWindows()
    return 0


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v1", "--video1", required=False, default=0,
                    help="Video ID for live tracking")
    ap.add_argument("-v2", "--video2", required=False,
                    help="Video ID for live tracking")
    ap.add_argument("-t", "--type", required=False,
                    help="type (aka. dictionary) of ArUco tag to detect")
    return vars(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main(get_args()))

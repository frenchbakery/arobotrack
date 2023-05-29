"""
Interactive camera calibration.
References:
https://learnopencv.com/camera-calibration-using-opencv/
https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

"""



import numpy as np
import cv2
import glob
import time as t
import os
from classes.camera import CameraParams

# create output constants
DATECODE = t.strftime("%Y%m%d_%H%M%S")
LIVE_SAVE_PREFIX = "calibration/data_046d_081b/"
output_folder_path: str = ""

# chessboard format (x, y)
CHESSBOARD = (6, 7)

# output image counter
image_counter: int = 0

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points representing the theoretical 3D-points of the board corner points
# on the chessboard on the chessboard plane. These should be the same for each frame
# objp will look something like ((0,0,0), (1,0,0), (2,0,0) ..., (6,5,0))
objp = np.zeros((CHESSBOARD[0] * CHESSBOARD[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# Shape of the image. This will be updated on every new processed image
# but should always be the same. This is needed at the end for calibrating
frame_shape: any = None


def process_calib_image(src_frame: cv2.Mat, save: bool = False):
    """
    Takes a frame and tries to find the chessboard corners. If it does,
    it saves them to the calibration values to perform calibration at the end.
    """
    global image_counter, frame_shape

    gray = cv2.cvtColor(src_frame, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6), cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    print(ret)
    # If found, add object points, image points (after refining them)
    if ret == True:
        # save the frame shape for later
        frame_shape = gray.shape[::-1]

        # add a new entry of real-world 3D positions
        objpoints.append(objp)

        # determine accurate point position of the corners and save the 2D positions
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

        if save:
            # save the original image for reference if requested
            cv2.imwrite(output_folder_path + str(image_counter).zfill(3) + ".png", src_frame)

        # Draw and display the corners
        cv2.drawChessboardCorners(src_frame, (7,6), corners2, ret)
        cv2.imshow('Last Capture', src_frame)

        if save:
            # save the marked image for reference if requested
            cv2.imwrite(output_folder_path + str(image_counter).zfill(3) + "m.png", src_frame)
            # next image next time
            image_counter += 1
        

def calibrate():
    """
    performs the calibration calculations using the previously stored 
    calibration points
    """
    global frame_shape

    # calculate calib values
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frame_shape, None, None)
    print("Calibration results:")
    print("ret:", ret)
    print("matrix:", mtx)
    print("distortion:", dist)

    # save calibration values
    CameraParams(mtx, dist).save(output_folder_path + "params_" + DATECODE + ".pickle")
    

if __name__ == "__main__":
    user_choice = input("Image source folder or 'live' for live camera to take calibration data: ")

    if user_choice == "live":
        # prepare output folder
        output_folder_path = LIVE_SAVE_PREFIX + DATECODE + "/"
        os.makedirs(output_folder_path, exist_ok=True)
        # setup the video capture for interactive input
        vidcap = cv2.VideoCapture(4)
        while True:
            _, img = vidcap.read()
            if img is None:
                continue

            # show live feed
            cv2.imshow("Live", img)

            key = cv2.waitKey(1) & 0xFF
            # q for quit
            if key == ord("q"):
                break
            # space for trigger
            elif key == ord(" "):
                process_calib_image(img, save=True)
            # c for calibrate 
            elif key == ord("c"):
                calibrate()
            
    else:
        # prepare output folder
        output_folder_path = user_choice + "/"
        # process all the images
        images = glob.glob(user_choice + "/[0-9][0-9][0-9].png")
        for image in images:
            print("processing: ", image)
            img = cv2.imread(image)
            process_calib_image(img, save=False)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        
        calibrate()

    cv2.destroyAllWindows()

#! /usr/local/bin/python3

# Based on information from: https://pyimagesearch.com/2020/12/14/generating-aruco-markers-with-opencv-and-python/

import argparse
import numpy as np
import cv2
import sys


# ArUco dictionary name to object map
ARUCO_DICT = {
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


def main(args: dict[str, any]):
    type_arg = ARUCO_DICT.get(args["type"], None)
    if type_arg is None:
        print(
            f"[ERROR] ArUco dictionary '{args['type']}' is not supported or invalid")
        sys.exit(1)
    selected_dict = cv2.aruco.getPredefinedDictionary(type_arg)

    id_arg = int(args["id"])
    size_arg: int = 1000
    if args["size"] is not None:
        size_arg = int(args["size"])

    output_arg = args["output"]
    if output_arg == None:
        output_arg = "tags/" + args["type"] + f"_ID{id_arg}.png"

    print(
        f"[INFO] Generating ArUco tag for dictionary '{args['type']}' with ID {id_arg} to '{output_arg}'")

    tag = np.zeros((size_arg, size_arg, 1), dtype="uint8")
    cv2.aruco.generateImageMarker(selected_dict, id_arg, size_arg, tag, 1)

    cv2.imwrite(output_arg, tag)
    #cv2.imshow("ArUco Tag", tag)
    #cv2.waitKey()

    sys.exit(0)


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=False,
                    help="Filepath to save output image containing ArUco tag to")
    ap.add_argument("-i", "--id", required=True,
                    help="ID of the ArUco tag to generate")
    ap.add_argument("-t", "--type", required=True,
                    help="type (aka. dictionary) of ArUco tag to generate")
    ap.add_argument("-s", "--size", required=False,
                    help="Size of the output image in pixels (square)")
    return vars(ap.parse_args())


if __name__ == "__main__":
    main(get_args())

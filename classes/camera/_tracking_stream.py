"""

Information on trapezoid transformation, warping images and transforming single points:
https://stackoverflow.com/questions/22037946/fast-trapezoid-to-rectangle-for-video
https://theailearner.com/tag/cv2-getperspectivetransform/
https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html
https://stackoverflow.com/questions/31147438/how-to-undo-a-perspective-transform-for-a-single-point-in-opencv (also contains info about forward transformation)
"""




import cv2
import numpy as np
from ._camera_device import CameraDevice
from ._aruco_detector import ArucoDetector, ARUCO_DICTS
from ._sharpen import sharpen_image


TRACKER_OUTPUT_SHAPE = (400, 400)


class TrackingStream:
    """
    The class that performs the reading of images from the camera, finding markers on the image,
    detecting playing field corners and warping the perspective to match those corners to a nice, rectangular frame.
    
    It also handles camera errors, detects when cameras are connected and automatically pauses/resumes the stream if
    the specified source camera is disconnected/connected (TBD).
    """

    def __init__(self, source: CameraDevice, aruco_dict: int = ARUCO_DICTS["DICT_4X4_50"]):
        self._source_device = source
        self._aruco_dict = aruco_dict
        self._input_stream = self._source_device.open()
        self._input_shape = (
            int(self._input_stream.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self._input_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )
        self._detector = ArucoDetector(self._aruco_dict)

        # the output frame is stored, so in case the camera disconnects, the old frame can be shown for the time being
        self._output_frame: cv2.Mat = np.zeros(TRACKER_OUTPUT_SHAPE)

        # variables for perspective transformation
        self._transformation_matrix: np.ndarray
        self._source_corners: np.ndarray
        self._dest_corners: np.ndarray
        # by default, the source area is the entire frame
        self._configure_source_area(np.float32(
            [
                [0, 0],                                         # tl
                [self._input_shape[0], 0],                      # tr
                [self._input_shape[0], self._input_shape[1]],   # br
                [0, self._input_shape[1]]                       # bl
            ]
        ))
    
    def _configure_source_area(self, source_corners: np.ndarray):
        """
        Calculates the internal transformation matrix so the output image will be exactly 
        the area of the source image contained by the provided points.

        @param source_corners array of 4 2d points in (tl, tr, br, bl) order
        """

        self._source_corners = source_corners
        print(type(source_corners))
        self._dest_corners: np.ndarray = np.float32([
            [0, 0],                                             # tl
            [TRACKER_OUTPUT_SHAPE[0], 0],                       # tr
            [TRACKER_OUTPUT_SHAPE[0], TRACKER_OUTPUT_SHAPE[1]], # br
            [0, TRACKER_OUTPUT_SHAPE[1]]                        # bl
        ])

        self._transformation_matrix = cv2.getPerspectiveTransform(
            self._source_corners,
            self._dest_corners
        )


    def update(self) -> cv2.Mat:
        """
        Reads a new frame from the camera and performs all tracking operations

        @returns the finished and and transformed frame of the 
        """
        
        # read frame
        status, frame_raw = self._input_stream.read()

        # if there is no frame, don't do anything
        if frame_raw is None:
            return self._output_frame
        
        # image preprocessing
        frame_bw = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2GRAY)
        frame_bw = sharpen_image(frame_bw)

        # detect markers
        self._detector.detect(frame_bw)
        self._detector.draw_markers_on_frame(frame_raw)

        # warp image to output perspective
        self._output_frame = cv2.warpPerspective(
            frame_raw,
            self._transformation_matrix,
            TRACKER_OUTPUT_SHAPE,
            flags=cv2.INTER_LINEAR
        )

        # show direct camera image with overlays
        cv2.imshow(self._source_device.display_name, frame_raw)

        return self._output_frame
        


        
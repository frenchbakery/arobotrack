
import subprocess
import cv2
from . import cv_types

class CameraDevice:
    """
    Class representing a camera device in terms of its logical properties
    such as serial number, video index, model name and others.
    This class provides functionality to find cameras by various attributes
    but not for processing video.
    """

    available_cameras: list["CameraDevice"] = []

    def __init__(self, video_index: int, display_name: str = "Camera"):
        self.video_index: int = video_index
        self.display_name: str = display_name
        self._udev_parameters: dict[str, str] = {}

        # read udev parameters to get serial number and other info
        self._get_udev_parameters()
        self._abc = "hsdf"
    
    def __repr__(self) -> str:
        return f"{self.display_name} ({self.serial_number}, {self.vendor_id}:{self.model_id}): /dev/video{self.video_index}"
        
    @property
    def serial_number(self) -> str:
        if "ID_SERIAL_SHORT" not in self._udev_parameters:
            raise ValueError(f"Serial number of camera {self.video_index} could not be detected.")
        return self._udev_parameters["ID_SERIAL_SHORT"]
    
    @property
    def vendor_id(self) -> str:
        if "ID_VENDOR_ID" not in self._udev_parameters:
            raise ValueError(f"Vendor id of camera {self.video_index} could not be detected.")
        return self._udev_parameters["ID_VENDOR_ID"]
    
    @property
    def model_id(self) -> str:
        if "ID_MODEL_ID" not in self._udev_parameters:
            raise ValueError(f"Model id of camera {self.video_index} could not be detected.")
        return self._udev_parameters["ID_MODEL_ID"]

    def _get_udev_parameters(self):
        """
        Reads the udev parameters of the camera device with the internally stored ID
        and stores all parameters and their values in the _udev_parameters dictionary.

        Info: identify cameras by serial number:
        https://superuser.com/questions/902012/how-to-identify-usb-webcam-by-serial-number-from-the-linux-command-line
        """

        # run udevadmin to get some info on the device
        process = subprocess.Popen(
            ["udevadm", "info", "--query=all", "/dev/video" + str(self.video_index), "|", "grep", "'VENDOR_ID\|MODEL_ID\|SERIAL_SHORT'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, _ = process.communicate()
        
        # go through all of the lines to load the parameters
        output_lines = stdout.decode('UTF-8').splitlines()

        # check for error output
        if len(output_lines) == 1 and output_lines[0].startswith("Unknown"):
            raise IndexError(f"Could not find camera with video index {self.video_index}")
        
        # extract all parameters
        for output_line in output_lines:
            # only the ones starting with "E: " prefix are interesting
            LINE_PREFIX = "E: "
            if not output_line.startswith(LINE_PREFIX):
                continue
            
            parameter = output_line.removeprefix(LINE_PREFIX)
            param_name, param_value = parameter.split("=", 1)
            self._udev_parameters[param_name] = param_value

    def open(self) -> cv_types.VideoCapture:
        """
        Opens an OpenCV video capture of the camera object
        """
        return cv2.VideoCapture(self.video_index)
    
    @classmethod
    def _supports_video_stream(cls, camera_device: str) -> bool:
        """
        @param camera_device: camera device path such as /dev/video0
        @retval True if a provided camera device supports any video stream formats
        @retval False if the device is not found or doesn't support any video stream format (i.e. is not a usable video input device)
        """
        # run v4l2-ctl to get the info
        process = subprocess.Popen(
            ["v4l2-ctl", "--list-formats", "--device=" + camera_device],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, _ = process.communicate()
        output_text = stdout.decode('UTF-8')

        # video formats are prefixed with a menu id in square brackets, so if there are any square brackets
        # there must be some supported video formats. If the provided device name is invalid, 
        # there are no brackets either
        if "[" in output_text and "]" in output_text:
            return True
        return False

    @classmethod
    def update_available_cameras(cls) -> list["CameraDevice"]:
        """
        updates the internally stored dict of available cameras 
        and their serial numbers and returns it.
        """

        # clear old available devices
        cls.available_cameras.clear()

        # run v4l2-ctl to get list of available devices
        process = subprocess.Popen(
            ["v4l2-ctl", "--list-devices"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, _ = process.communicate()
        
        # go through all of the lines individually
        output_lines: list[str] = stdout.decode('UTF-8').splitlines()
        # variable that is set whenever a name line is encountered
        current_name: str = None

        output_line: str
        for output_line in output_lines:

            # lines that start with some name indicate a new physical device. store name
            if not output_line.startswith(" ") and ":" in output_line:
                current_name = output_line.split(":")[0]
                continue

            # remove leading spaces
            output_line = output_line.strip()

            # ignore media devices and others that are not /dev/video*
            if not output_line.startswith("/dev/video"):
                continue

            # ignore any alternate function video devices that don't support video input streams
            if not cls._supports_video_stream(output_line):
                continue
            
            # create camera device instance and save it
            cls.available_cameras.append(CameraDevice(
                int(output_line.removeprefix("/dev/video")),
                current_name
            ))
        
        return cls.available_cameras
    
    @classmethod
    def by_serial_number(cls, serial_nr: str, update: bool = False) -> "CameraDevice":
        """
        Returns the first available CameraDevice matching a serial number.
        Raises IndexError if not found.

        Set update to true to update available cameras before searching.
        """

        if update:
            cls.update_available_cameras()

        for cam in cls.available_cameras:
            if cam.serial_number == serial_nr:
                return cam
        
        raise IndexError(f"No camera with serial number {serial_nr} available.")

    @classmethod
    def by_video_index(cls, video_index: int, update: bool = False) -> "CameraDevice":
        """
        Returns the CameraDevice with the video index if available.
        Raises IndexError if not found.

        Set update to true to update available cameras before searching.
        """

        if update:
            cls.update_available_cameras()

        for cam in cls.available_cameras:
            if cam.video_index == video_index:
                return cam
        
        raise IndexError(f"No camera with video index {video_index} available.")


# update global list of available devices when loaded
CameraDevice.update_available_cameras()


# test code
if __name__ == "__main__":

    for cam in CameraDevice.available_cameras:
        print(cam)
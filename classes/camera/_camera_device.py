
import subprocess


class CameraDevice:
    video_id: int
    udev_parameters: dict[str, str]

    def __init__(self, video_id: int):
        self._video_id = video_id

    def _get_udev_parameters(self):
        process = subprocess.Popen(
            ["udevadm", "info", "--query=all", "/dev/video" + str(self.video_id), "|", "grep", "'VENDOR_ID\|MODEL_ID\|SERIAL_SHORT'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, _ = process.communicate()
        
        output_lines = stdout.decode('UTF-8').splitlines()
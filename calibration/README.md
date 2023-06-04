# Calibration

You can run the script camera_calib.py to take calibration images with the chessboard and generate the calibration parameters. when doing so, make sure to adjust the camera index and output folders in the script beforehand.

**Important: If the calibration images created by the calibration script show any people, don't ever commit them!!**

## Structure

```opencv_chessboard.png```: Calibration chessboard from https://github.com/opencv/opencv/blob/4.x/samples/data/chessboard.png

```data_046d_0825```: Calibration data for Logitech (VID=046d) camera C270 (PID=0825) (Matteo's camera)

```data_046d_081d```: Calibration data for Logitech (VID=046d) camera C310 (PID=081d) (Signitzer's camera)

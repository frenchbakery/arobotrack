# arobotrack
Visual tracking software using ArUco tags for developing robots

## Environment

It is recommended to create a Python VENV with the listed [requirements](requirements.txt) (most IDEs like VSCode and PyCharm can do that automatically).

## Info

To debug and find out all about Cameras, use v4l-ctl:

```bash
sudo apt install v4l-utils
```

List available video devices:

```bash
v4l-ctl --list-devices
```

Often, there are multiple logical video interfaces for a single physical device.
Usually it's one or two per physical device, in this example it's even more:

```
HP HD Camera: HP HD Camera (usb-0000:05:00.4-2):
	/dev/video0
	/dev/video1
	/dev/video2
	/dev/video3
	/dev/media0
	/dev/media1
```

Show all info about a video device

```bash
v4l-ctl --device=/dev/video0 --all
```

Show List of supported controls of a device:

```bash
v4l2-ctl --device=/dev/video0 --list-ctrls-menu
```

The output might look something like this:

```bash

User Controls

                     brightness 0x00980900 (int)    : min=-64 max=64 step=1 default=0 value=0
                       contrast 0x00980901 (int)    : min=0 max=64 step=1 default=32 value=32
                     saturation 0x00980902 (int)    : min=0 max=128 step=1 default=64 value=64
                            hue 0x00980903 (int)    : min=-40 max=40 step=1 default=0 value=0
        white_balance_automatic 0x0098090c (bool)   : default=1 value=1
                          gamma 0x00980910 (int)    : min=72 max=500 step=1 default=100 value=100
           power_line_frequency 0x00980918 (menu)   : min=0 max=2 default=1 value=1 (50 Hz)
				0: Disabled
				1: 50 Hz
				2: 60 Hz
      white_balance_temperature 0x0098091a (int)    : min=2800 max=6500 step=10 default=4000 value=4000 flags=inactive
                      sharpness 0x0098091b (int)    : min=0 max=5 step=1 default=0 value=0
         backlight_compensation 0x0098091c (int)    : min=0 max=1 step=1 default=0 value=0

Camera Controls

                  auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=3 (Aperture Priority Mode)
				1: Manual Mode
				3: Aperture Priority Mode
         exposure_time_absolute 0x009a0902 (int)    : min=50 max=10000 step=1 default=300 value=300 flags=inactive
     exposure_dynamic_framerate 0x009a0903 (bool)   : default=0 value=1

```

Change controls of a device:

```bash
# some example controls
v4l2-ctl --device=/dev/video0 -c brightness=0
v4l2-ctl --device=/dev/video0 -c contrast=120
v4l2-ctl --device=/dev/video0 -c white_balance_temperature_auto=0
v4l2-ctl --device=/dev/video0 -c gamma=120
v4l2-ctl --device=/dev/video0 -c white_balance_temperature=4700
v4l2-ctl --device=/dev/video0 -c sharpness=100
v4l2-ctl --device=/dev/video0 -c backlight_compensation=0
v4l2-ctl --device=/dev/video0 -c focus_absolute=10e
v4l2-ctl --device=/dev/video0 -c auto_exposure=1
v4l2-ctl --device=/dev/video0 -c focus_auto=0
```
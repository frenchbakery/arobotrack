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

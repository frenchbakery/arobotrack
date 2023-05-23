
from dataclasses import dataclass
import subprocess


@dataclass
class UCVControl:
    name: str
    type: type 
    values: tuple[int | str, ...]
    menu_name_map: tuple[str, ...]
    value: int | str = 0


class V4L2Ctl:
    _device_path: str
    _supported_controls: list[UCVControl]

    def __init__(self, device: str | int = 0):
        if isinstance(device, int):
            self._device_path = f"/dev/video{device}"
        elif isinstance(device, str) and device.startswith("/dev/video"):
            self._device_path = device
        else:
            raise ValueError(f"Device must be a video device path or number, not {device}.")
        
    def update_controls(self):
        """
        Updates the list of available UVC controlls for the video device and
        their values.
        """
        v4l_process = subprocess.Popen(
            ['v4l2-ctl', '-d', self._device_path, '--list-ctrls-menu'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, _ = v4l_process.communicate()
        
        v4l_output_lines = stdout.decode('UTF-8').splitlines()

        for i, line in enumerate(v4l_output_lines):
            # Skip menu legend lines which are denoted by 4 tabs
            if v4l_output_lines[i].startswith('\t\t\t\t'):
                continue

            # Skip Header lines and empty lines which don't start with spaces
            if not v4l_output_lines[i].startswith(' '):
                continue
            
            # === continue here
            a = dict()

            # parse the setting name, ID and datatype from the line
            setting = line.split(':',1)[0].split()
            print("setting=" + str(setting))
                    # ['brightness', '0x00980900', '(int)']

            # parse parameters from the line
            # some menu controls stuff after the parameter list in parentheses so we ignore any split results that don't contain an equal sign
            params = [param for param in (v4l_output_lines[i].split(':',1)[1].split()) if "=" in param]
            print("param=" + str(params))
                    # ['min=-64', 'max=64', 'step=1', 'default=0', 'value=0']

            # Put paramaters into a dictionary
            for j in range(0, len(params)):
            a.update({params[j].split('=',1)[0]: params[j].split('=',1)[1]})
            # Add bitName and setting type to params dictionary 
            a.update({'bitName': setting[1]})
            a.update({'type': setting[2].strip("()")})
            # Create a legend for menu entries and add to dictionary with other params
            if a['type'] == 'menu':
            h = 0
            legend = ''
            while h >= 0:
                h += 1
                ih = i + h
                if v4l_output_lines[ih].startswith('\t\t\t\t') and (ih) <= nLines:
                legend = legend + v4l_output_lines[i+h].strip() + "   "
                else:
                h = -1
            a.update({'legend': legend})    # additional data on settings
            a.update({'step': 1})           # adding to work with updateUVCsetting()
            # Use setting name as key and dictionary of params as value
            camSettings.update({setting[0]: a})

        for x in camSettings:
            print(x,'\n   ',camSettings[x])
        
        return camSettings

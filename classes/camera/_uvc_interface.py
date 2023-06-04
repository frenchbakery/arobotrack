
from dataclasses import dataclass
import subprocess
from typing import Any


MENU_LEGEND_LINE_PREFIX = "\t\t\t\t"

# The menu type of UVC controls basically is a dictionary
menu = dict


def invert_dict(dictionary: dict) -> dict:
    return {v: k for k, v in dictionary.items()}


@dataclass
class UVCControl:
    name: str = ""
    id: int = 0
    datatype: type = None
    min: int | None = None
    max: int | None = None
    step: int | None = None
    default: int = 0
    # bidirectional maps for performance
    menu_val_to_name: dict[int, str] | None = None
    menu_name_to_val: dict[str, int] | None = None
    value: int = 0
    
    @property
    def option(self) -> str:
        """
        menu option text if applicable, exception otherwise
        """
        if self.datatype is menu and self.menu_val_to_name is not None:
            return self.menu_val_to_name[self.value]
        else:
            raise ValueError(f"Non-menu UVC control '{self.name}' cannot be converted to string")

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name} ({self.datatype.__name__}, {str(self.min) + '-' + str(self.max)  + ', ' if self.min is not None and self.max is not None else ''}{'step=' + str(self.step) + ', ' if self.step is not None else ''}default={self.default}): {self.value}{' ' + self.menu_val_to_name[self.value] if self.datatype is menu else ''})"


class UVCInterface:

    def __init__(self, device: str | int = 0):
        self._device_path: str
        self._controls: dict[str, UVCControl] = {}

        if isinstance(device, int):
            self._device_path = f"/dev/video{device}"
        elif isinstance(device, str) and device.startswith("/dev/video"):
            self._device_path = device
        else:
            raise ValueError(f"Device must be a video device path or number, not {device}.")
        
    def load_controls(self):
        """
        Updates the list of available UVC controls for the video device and
        their values.
        """
        
        # delete old supported controls
        self._controls.clear()

        # get new controls and values
        v4l_process = subprocess.Popen(
            ["v4l2-ctl", "-d", self._device_path, "--list-ctrls-menu"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        v4l_process.wait
        stdout, _ = v4l_process.communicate()
        
        v4l_output_lines = stdout.decode('UTF-8').splitlines()

        for i, line in enumerate(v4l_output_lines):
            # Skip menu legend lines which are denoted by a special prefix (usually 4 tabs)
            if v4l_output_lines[i].startswith(MENU_LEGEND_LINE_PREFIX):
                continue

            # Skip Header lines and empty lines which don't start with spaces
            if not v4l_output_lines[i].startswith(' '):
                continue
            
            new_control = UVCControl()

            # separate the info section from the parameters section
            control_section_info, control_section_parameters = (p.strip() for p in line.split(":", 1))
            # control_section_info == "brightness 0x00980900 (int)"
            # control_section_parameters == "min=-64 max=64 step=1 default=0 value=0" [""]
            
            # split the info into the control name, ID and datatype and save the info
            control_info = control_section_info.split()
            #print(f"{control_info=}")  # ["brighness", "0x00980900", "(int)"]
            new_control.name = control_info[0]
            new_control.id = int(control_info[1], 16)
            try:
                new_control.datatype = {
                    "(int)": int,
                    "(bool)": bool,
                    "(menu)": menu
                }[control_info[2]]
            except KeyError:
                print(f"Warning: UVC control with unknown datatype: {control_info[2]}, ignoring")
                continue
            

            # split the values section into the separate value parameters 
            # som menu controls have additional human readable information appended to the end that is not interesting to us
            # so we ignore any split results that don't contain an equals sign. We also ignore flags
            control_parameters = {param.split("=", 1)[0]: int(param.split("=", 1)[1]) for param in (control_section_parameters.split()) if "=" in param and not "flags=" in param}
            #print(f"{control_parameters=}") # {"min": -64, "max": 64, "step": 1, "default": 0, "value": 0}

            # store all the parameters
            for name, val in control_parameters.items():
                setattr(new_control, name, val)

            # if the parameter is a menu, parse all the menu options from the legend
            if new_control.datatype is menu:
                # initialize menu map
                new_control.menu_val_to_name = {}
                
                legend_line_index = i + 1
                # menu lines always start with four tabs, so if a line starts with a space
                while True:
                    legend_line: str = v4l_output_lines[legend_line_index]
                    # menu lines always start with a prefix (4 tabs), so if a line doesn't start with that, we have reached the ned of the legend
                    if not legend_line.startswith(MENU_LEGEND_LINE_PREFIX):
                        break
                    option_value, option_name = legend_line.split(":", 1)
                    # save the option
                    new_control.menu_val_to_name[int(option_value)] = option_name.strip()
                    # next line
                    legend_line_index += 1
                
                # save the reverser map as well for performance
                new_control.menu_name_to_val = invert_dict(new_control.menu_val_to_name)
            
            # save the control
            self._controls[new_control.name] = new_control
        
    def set_to_defaults(self):
        """
        Sets all the UVC Parameters back to their default settings
        """
        for control in self._controls.values():
            self._write_control(control, default=True)

    
    def _write_control(self, control: UVCControl, default: bool = False):
        """
        Writes the current or default value of a UVCControl object to the camera using
        the v4l2-ctl command.

        @param control the control that should be written
        @param default True to write the default value instead of the current value
        """
        value = control.default if default else control.value
        v4l_process = subprocess.Popen(
            ["v4l2-ctl", "-d", self._device_path, "-c", f"{control.name}={value}"]
        )

        match errcode := v4l_process.wait():
            case 0:
                control.value = value   # in case default was written, store it as the new value
                return
            case 1:
                raise RuntimeError(f"v4l2-ctl: '{control.name}' is not a valid UVC control for camera '{self._device_path}'")
            case 255:
                raise RuntimeError(f"v4l2-ctl: UVC control '{control.name}' of camera '{self._device_path}' cannot be set to {value}")
            case _:
                raise RuntimeError(f"v4l2-ctl: Unknown error {errcode} while writing UVC control '{control.name}' of camera '{self._device_path}'")

    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        Allows directly assigning any available UVC controls which are dynamically loaded at runtime
        """

        if "_controls" in self.__dict__ and __name in self.__dict__["_controls"]:
            target_control: UVCControl = self.__dict__["_controls"][__name]
            old_value = target_control.value
            if isinstance(__value, int):
                target_control.value = __value
            elif isinstance(__value, str):
                if target_control.datatype is not menu or target_control.menu_name_to_val is None:
                    raise TypeError(f"UVC control '{target_control.name}' is not a menu and cannot be set to '{__value}'")
                if __value not in target_control.menu_name_to_val:
                    raise ValueError(f"'{__value}' is not a valid menu option for UVC control '{target_control.name}' of camera '{self._device_path}'")
                target_control.value = target_control.menu_name_to_val[__value]
            else:
                raise TypeError(f"UVC control cannot be assigned a value of type '{type(__value).__name__}'")

            # make sure the value is in allowed
            if target_control.datatype is int and target_control.min is not None and target_control.max is not None:
                if target_control.value < target_control.min or target_control.value > target_control.max:
                    raise ValueError(f"UVC control '{target_control.name}' of camera '{self._device_path}' must be within {target_control.min} and {target_control.max}")
            if target_control.datatype is bool:
                if target_control.value not in (0, 1):
                    raise ValueError(f"UVC control '{target_control.name}' of camera '{self._device_path}' must be boolean")
            if target_control.datatype is menu:
                if target_control.value not in target_control.menu_val_to_name:
                    raise ValueError(f"UVC control '{target_control.name}' of camera '{self._device_path}' must be one of {target_control.menu_val_to_name}")

            # actually perform the write operation
            self._write_control(target_control)

        else:
            super().__setattr__(__name, __value)
    
    def __getattr__(self, __name: str) -> UVCControl:
        """
        Allows directly accessing the UVC controls as properties
        """
        if __name in self.__dict__["_controls"]:
            return self.__dict__["_controls"][__name]
        else:
            raise AttributeError(f"'{self.__dict__['_device_path']}' has no UVC control '{__name}'")
            


# testing
if __name__ == "__main__":
    test_interface = UVCInterface(2)
    test_interface.load_controls()
    for ctrl in test_interface._controls.values():
        print(ctrl)

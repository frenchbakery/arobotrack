

import numpy as np
import threading as th
import customtkinter as ctk
import cv2
from PIL import Image

from ..utilities.errors import DuplicateCallError, ProgramLogicError

class MainWindow(ctk.CTk):
    video_frame: ctk.CTkLabel = None
    exit_flag: bool = False

    def __init__(self):
        super().__init__()

        # handle exit
        self.protocol("WM_DELETE_WINDOW", self.exit_handler)

        # add UI elements
        self.video_frame = ctk.CTkLabel(self)
        self.video_frame.pack(expand=True)

    def exit_handler(self):
        self.exit_flag = True

    def update_video(self, frame: np.ndarray):
        """
        Updates the video frame displayed in the UI with a new OpenCV 
        video frame
        """
        if self.exit_flag: return

        reordered_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        pil_frame = Image.fromarray(reordered_frame)
        ctk_frame = ctk.CTkImage(light_image=pil_frame, size=pil_frame.size)
        self.video_frame.configure(image=ctk_frame)
    
    def update(self) -> bool:
        """
        Enter event loop until all pending events have been processed by Tcl.
        Returns false during normal operation and true when the window was closed.
        """
        super().update()
        return self.exit_flag
        

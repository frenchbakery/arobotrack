
from dataclasses import dataclass
import numpy as np
import pickle

FORMAT_VERSION = 1

@dataclass
class CameraParams:
    matrix: np.ndarray
    distortion: np.ndarray

    def load(self, file: str) -> "CameraParams":
        """
        loads parameters from a 
        """
        with open(file, "rb") as f:
            data = pickle.load(f)
            if data["version"] != FORMAT_VERSION:
                raise ValueError("Cannot load CameraParams from file " + file + ": invalid structure or format version")
            self.matrix = data["matrix"]
            self.distortion = data["distortion"]
        return self
    
    def save(self, file: str) -> "CameraParams":
        with open(file, "wb") as f:
            pickle.dump({
                "version": FORMAT_VERSION,
                "matrix": self.matrix, 
                "distortion": self.distortion
            }, f)
        return self

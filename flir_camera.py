import PySpin
from PySpin import Camera
import numpy as np
import matplotlib.pyplot as plt

class FLIRCamera:
    """Class for control of the FLIR Blackfly S (BFS-U3-244S8M-C)."""

    def __init__(self, index=0):
        """
        Initialize and open a camera by index.

        Args:
            index: which camera to use (0 = first camera)
        """
        self.system = None
        self.cam_list = None
        self.cam = None
        # TODO: add other camera properties
        # get them from the  

        try:
            self.system = PySpin.System.GetInstance()
            self.cam_list = self.system.GetCameras()
            num_cameras = self.cam_list.GetSize()
            if num_cameras == 0:
                raise RuntimeError("No FLIR cameras detected.")
            if index >= num_cameras:
                raise RuntimeError(f"Requested camera index {index} but only {num_cameras} camera(s) found.")
            self.cam = self.cam_list[index]
            self.cam.Init()
        except Exception as e:
            self._cleanup()
            raise

    def is_connected(self):
        return self.cam is not None and self.cam.IsInitialized()
    
    def _cleanup(self):
        try:
            if self.cam is not None and self.cam.IsInitialized():
                self.cam.DeInit()
        except:
            pass
        try:
            if self.cam_list is not None:
                self.cam_list.Clear()
        except:
            pass
    
    def close(self):
        self._cleanup()
        self.cam = None
        self.cam_list = None
        self.system = None

    def __enter__(self):
        """Context manager support (for 'with')."""
        return self
    
    def __exit__(self, *args):
        """Cleanup when exiting context (for 'with')."""
        self.close()

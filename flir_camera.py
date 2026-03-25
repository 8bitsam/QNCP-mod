import os
import traceback
from datetime import datetime
import PySpin


class FLIRCamera:
    """Class for control of the FLIR Blackfly S (BFS-U3-244S8M-C)."""
    def __init__(self, index=0):
        self.system = None
        self.cam_list = None
        self.cam = None
        try:
            print("[init] getting system")
            self.system = PySpin.System.GetInstance()
            print("[init] getting camera list")
            self.cam_list = self.system.GetCameras()
            num_cameras = self.cam_list.GetSize()
            print(f"[init] cameras found: {num_cameras}")
            if num_cameras == 0:
                raise RuntimeError("No FLIR cameras detected.")
            if index >= num_cameras:
                raise RuntimeError(
                    f"Requested camera index {index} but only {num_cameras} camera(s) found."
                )
            print(f"[init] selecting camera index {index}")
            print(self.cam_list)
            self.cam = self.cam_list[index]
            print("[init] initializing camera")
            self.cam.Init()
            print("[init] camera initialized")
        except Exception:
            print("[init] FAILED")
            traceback.print_exc()
            self._cleanup()
            raise

    def is_connected(self):
        return self.cam is not None and self.cam.IsInitialized()

    def _cleanup(self):
        try:
            if self.cam is not None and self.cam.IsInitialized():
                print("[cleanup] deinitializing camera")
                self.cam.DeInit()
        except Exception:
            print("[cleanup] camera deinit failed")
            traceback.print_exc()
        try:
            if self.cam_list is not None:
                print("[cleanup] clearing camera list")
                self.cam_list.Clear()
        except Exception:
            print("[cleanup] cam_list clear failed")
            traceback.print_exc()

    def close(self):
        print("[close]")
        self._cleanup()
        self.cam = None
        self.cam_list = None
        self.system = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
        return False

    def snap_and_save(self, filename=None, folder="images", timeout_ms=1000):
        os.makedirs(folder, exist_ok=True)
        if filename is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = os.path.join(folder, f"flir_{ts}.png")
        print(f"[capture] output path: {filename}")
        try:
            print("[capture] setting AcquisitionMode = Continuous")
            self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        except Exception:
            print("[capture] FAILED while setting acquisition mode")
            traceback.print_exc()
            raise
        try:
            print("[capture] BeginAcquisition")
            self.cam.BeginAcquisition()
        except Exception:
            print("[capture] setup/acquisition failed")
            traceback.print_exc()
            raise
        img = None
        try:
            try:
                print(f"[capture] GetNextImage timeout={timeout_ms} ms")
                img = self.cam.GetNextImage(timeout_ms)
                print("[capture] image received")
            except Exception:
                print("[capture] FAILED at GetNextImage")
                traceback.print_exc()
                raise
            try:
                incomplete = img.IsIncomplete()
                print(f"[capture] IsIncomplete = {incomplete}")
                if incomplete:
                    raise RuntimeError(f"Incomplete image: {img.GetImageStatus()}")
            except Exception:
                print("[capture] FAILED while checking image completeness")
                traceback.print_exc()
                raise
            try:
                print("[capture] saving image")
                img.Save(filename)
                print("[capture] save successful")
            except Exception:
                print("[capture] FAILED at img.Save")
                traceback.print_exc()
                raise
            return filename
        finally:
            if img is not None:
                try:
                    print("[capture] releasing image")
                    img.Release()
                except Exception:
                    print("[capture] FAILED at img.Release")
                    traceback.print_exc()
            try:
                print("[capture] EndAcquisition")
                self.cam.EndAcquisition()
            except Exception:
                print("[capture] FAILED at EndAcquisition")
                traceback.print_exc()

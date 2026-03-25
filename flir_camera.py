import os
import gc
import PySpin
from datetime import datetime


class FLIRCamera:
    def __init__(self, serial):
        self.system = None
        self.cam_list = None
        self.cam = None
        self.serial = str(serial)
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        if self.cam_list.GetSize() == 0:
            self.close()
            raise RuntimeError("No FLIR cameras detected.")
        self.cam = self.cam_list.GetBySerial(self.serial)
        if not self.cam.IsValid():
            self.close()
            raise RuntimeError(f"Camera with serial {self.serial} not found.")
        self.cam.Init()

    @staticmethod
    def list_cameras():
        system = None
        cam_list = None
        out = []
        try:
            system = PySpin.System.GetInstance()
            cam_list = system.GetCameras()
            n = cam_list.GetSize()
            for i in range(n):
                cam = None
                tlmap = None
                sn_node = None
                model_node = None
                cam = cam_list.GetByIndex(i)
                tlmap = cam.GetTLDeviceNodeMap()
                sn_node = PySpin.CStringPtr(tlmap.GetNode("DeviceSerialNumber"))
                serial = None
                if PySpin.IsAvailable(sn_node) and PySpin.IsReadable(sn_node):
                    serial = sn_node.GetValue()
                model_node = PySpin.CStringPtr(tlmap.GetNode("DeviceModelName"))
                model = None
                if PySpin.IsAvailable(model_node) and PySpin.IsReadable(model_node):
                    model = model_node.GetValue()
                out.append({
                    "serial": serial,
                    "model": model
                })
                del model_node
                del sn_node
                del tlmap
                del cam
            return out

        finally:
            if cam_list is not None:
                cam_list.Clear()
            if system is not None:
                system.ReleaseInstance()

    def is_connected(self):
        return self.cam is not None and self.cam.IsInitialized()

    def configure(self):
        nodemap = self.cam.GetNodeMap()
        print("[configure] AcquisitionMode = Continuous")
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        for t in ["Mode", "Source", "Selector"]:
            node = PySpin.CEnumerationPtr(nodemap.GetNode(f"Trigger{t}"))
            if PySpin.IsAvailable(node) and PySpin.IsReadable(node):
                print(f"[configure] Trigger{t} = {node.GetCurrentEntry().GetSymbolic()}")
            else:
                print(f"[configure] Trigger{t} = (not readable)")
    
    def capture(self, n_frames, folder="captures", prefix="frame", timeout_ms=5000):
        run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(folder, f"run_{run_ts}")
        os.makedirs(run_dir, exist_ok=True)
        saved = []
        self.cam.BeginAcquisition()
        print(f"[capture] acquisition started, saving {n_frames} frame(s) to: {run_dir}")
        try:
            for k in range(n_frames):
                img = None
                try:
                    img = self.cam.GetNextImage(timeout_ms)
                    if img.IsIncomplete():
                        raise RuntimeError(f"Frame {k} incomplete: {img.GetImageStatus()}")
                    path = os.path.join(run_dir, f"{prefix}_{k:04d}.pgm")
                    img.Save(path)
                    saved.append(path)
                    print(f"[capture] frame {k:04d} -> {path}")
                finally:
                    if img is not None:
                        img.Release()
        finally:
            self.cam.EndAcquisition()
            print("[capture] acquisition ended")
        return saved

    def close(self):
        if self.cam is not None:
            try:
                if self.cam.IsInitialized():
                    self.cam.DeInit()
            finally:
                self.cam = None
                gc.collect()
        if self.cam_list is not None:
            self.cam_list.Clear()
            self.cam_list = None
        if self.system is not None:
            self.system.ReleaseInstance()
            self.system = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
        return False

import PySpin


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

    def close(self):
        if self.cam is not None:
            try:
                if self.cam.IsInitialized():
                    self.cam.DeInit()
            finally:
                self.cam = None
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

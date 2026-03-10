from QNCP import device
from qncp_funcs import get_devices
from flir_camera import FLIRCamera

# Get all QC's
baud = 38400
devices = get_devices(baud, devicetype=device.Quantum_Composers)
QC = devices[2]
print(QC)

# QC
composer = device.Quantum_Composers(QC, baud)
# TODO: write some stuff to qc...

# Camera
try:
    with FLIRCamera(index=0) as cam:
        print("Camera connected:", cam.is_connected())
        path = cam.snap_and_save(folder="captures")
        print(f"Image saved: {path}")
except Exception as e:
    print("Camera connection failed:", e)

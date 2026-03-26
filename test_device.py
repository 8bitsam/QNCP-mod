from QNCP import device
from qncp_funcs import get_devices
from flir_camera import FLIRCamera

# Get all QC's
baud = 38400
devices = get_devices(baud, devicetype=device.Quantum_Composers)
print(devices)
QC = 'ASRL6::INSTR'

# QC
composer = device.Quantum_Composers(QC, baud)
pulse_width = composer.read_value(':PULSE1:WIDT?')
print(pulse_width)

# TODO: write some stuff to qc...

# Camera
cams = FLIRCamera.list_cameras()
print(cams)
blackfly_serial = 23319486

try:
    with FLIRCamera(serial=blackfly_serial) as cam:
        print("Camera connected:", cam.is_connected())
        cam.configure()
        paths = cam.capture(n_frames=30, timeout_ms=5000, folder="captures", prefix="blackfly")
except Exception as e:
    print("Camera connection failed:", e)

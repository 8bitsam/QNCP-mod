from QNCP import device
from qncp_funcs import setup_qc_from_csv, enable_qc, disable_qc
from flir_camera import FLIRCamera


### HARDWARE INFORMATION ###
baud = 38400

# devices = get_devices(baud, devicetype=device.Quantum_Composers)
# print(devices)
# cams = FLIRCamera.list_cameras()
# print(cams)

QC = 'ASRL6::INSTR'
blackfly_serial = 23319486


### QUANTUM COMPOSER SETUP ###
composer = device.Quantum_Composers(QC, baud)
composer.clear_buffer()

# Set system options
composer.sys_mode('NORM')
composer.t0(0.05)          # 50 ms period
composer.trig(mode='DIS', edge='RIS', level=2.5)
composer.gate(mode='DIS', logic='LOW', level=2.5)
# TODO: missing puslse mode?

# Set channels
setup_qc_from_csv(composer=composer, csv_path='qc_channels.csv')


### RUN AND TAKE PICTURE
try:
    with FLIRCamera(serial=blackfly_serial) as cam:
        print("Camera connected:", cam.is_connected())
        cam.configure()
        enable_qc(composer=composer)
        paths = cam.capture(n_frames=30, timeout_ms=5000, folder="captures", prefix="blackfly")
        disable_qc(composer=composer)
        print("Run complete")
except Exception as e:
    print("Camera connection failed:", e)

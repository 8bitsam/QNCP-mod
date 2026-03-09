import pyvisa
from QNCP import search, device

def get_devices(baud: int, devicetype) -> list[str]:
    """Find all connected devices"""
    rm = pyvisa.ResourceManager()
    rm.close()
    QC = search.get_resource('ASRL', devicetype, baud)
    return QC

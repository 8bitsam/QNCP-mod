import pyvisa
import time
import pandas as pd
from QNCP import search, device


def get_devices(baud: int, devicetype) -> list[str]:
    """Find all connected devices"""
    rm = pyvisa.ResourceManager()
    rm.close()
    QC = search.get_resource('ASRL', devicetype, baud)
    return QC

def setup_qc_from_csv(composer: device.Quantum_Composers, csv_path: str):
    """Configure all channels of a Quantum Composer from a CSV file without enabling outputs."""
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        ch          = int(row['channel'])
        delay       = float(row['delay_s'])
        width       = float(row['width_s'])
        cmode       = str(row['cmode']).upper()
        burst_count = int(row['burst_count'])
        polarity    = str(row['polarity'])
        out_mode    = str(row['out_mode']).upper()
        amplitude   = float(row['amplitude_v'])
        sync_src    = str(row['sync'])
        duty_on     = int(row['duty_on'])
        duty_off    = int(row['duty_off'])
        wait_count  = int(row['wait_count'])
        mux_timers  = [int(t) for t in str(row['mux']).split(',')]
        gate_mode   = str(row['gate_mode'])

        # Set values
        composer.dly(ch, delay)
        composer.wid(ch, width)
        # composer.sync(ch, sync_src)
        composer.wcount(ch, wait_count)
        composer.pol(ch, polarity)
        if out_mode == 'TTL':
            composer.lev(ch)
        else:
            composer.lev(ch, amplitude)
        if cmode == 'DCYC':
            composer.dcycl(ch, duty_on, duty_off)
        elif cmode == 'BURS':
            composer.dev.write(':PULSE{}:CMOD BURS'.format(ch))
            composer.dev.write(':PULSE{}:BCOU {}'.format(ch, burst_count))
        elif cmode == 'SING':
            composer.dev.write(':PULSE{}:CMOD SING'.format(ch))
        else:
            composer.norm(ch)
        composer.mux(ch, *mux_timers)
        # composer.ch_gate(ch, gate_mode)

def enable_qc(composer: device.Quantum_Composers, channels=[1, 2, 3, 4, 5, 6, 7, 8]):
    for ch in channels:
        composer.on(ch)

def disable_qc(composer: device.Quantum_Composers, channels=[1, 2, 3, 4, 5, 6, 7, 8]):
    for ch in channels:
        composer.off(ch)

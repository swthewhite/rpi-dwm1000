"""
This python script uses the DW1000 as a sniffer device
"""

from DW1000 import DW1000
import time
import DW1000Constants as C
import MAC
from datetime import datetime, timedelta

PIN_IRQ = 16
PIN_CS = 8
PIN_RST = 12
EID = "7D:00:22:EA:82:60:3B:FF"
PAN = 0xdeca
dw1000 = None

def interruptCB():
    # First read sysstatus to get interrupt reason
    dw1000.readRegister(dw1000.sysstatus)
    dw1000.printStatusRegister()
    print("")
    if dw1000.sysstatus.getBit(C.RXDFR_BIT) or dw1000.sysstatus.getBit(C.RXFCG_BIT):
        message = dw1000.getMessage()
        dw1000.toggleHSRBP()
        try:
            MAC.printHeader(message)
        except:
            print("Not a valid 802.15.4 frame")


def setup():
    global dw1000
    dw1000 = DW1000(PIN_CS, PIN_RST, PIN_IRQ)
    dw1000.begin()
    print("DW1000 initialized")
    print("############### Test sender ##############")	

    dw1000.generalConfiguration(EID, PAN, C.MODE_STANDARD)
    dw1000.setAntennaDelay(C.ANTENNA_DELAY_RASPI)
    dw1000.interruptCallback = interruptCB

    # Enable automatic rx reenable
    # Disable smart tx power, frame crc checks
    dw1000.syscfg.setBits((C.DIS_STXP_BIT, C.DIS_FCE_BIT, C.RXAUTR_BIT), True)
    dw1000.writeRegister(dw1000.syscfg)

    dw1000.resetHSRBP()

    # Enable receiver buffer overrun detection, data frame receive
    dw1000.sysmask.clear()
    dw1000.sysmask.setBits((C.MRXOVRR_BIT, C.MRXDFR_BIT, C.MRXFCG_BIT, C.MRXFCE_BIT), True)
    dw1000.writeRegister(dw1000.sysmask)

    dw1000.clearAllStatus()

    dw1000.printDeviceInfo()


def main():
    try:
        setup()
        dw1000.newReceive()
        dw1000.startReceive()

        while 1:
            pass

    except KeyboardInterrupt:
        dw1000.stop()


if __name__ == "__main__":
    main()
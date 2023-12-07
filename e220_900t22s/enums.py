
import re
from enum import IntEnum, auto

from .base_enums import IntegerChoices


def get_num_only(s: str):
    return int(re.sub(r'\D', '', s))


class SerialPortRateChoices(IntegerChoices):
    BPS1200 = 0, '1,200[bps]'
    BPS2400 = 1, '2,400[bps]'
    BPS4800 = 2, '4,800[bps]'
    BPS9600 = 3, '9,600[bps]'
    BPS19200 = 4, '19,200[bps]'
    BPS38400 = 5, '38,400[bps]'
    BPS57600 = 6, '57,600[bps]'
    BPS115200 = 7, '115,200[bps]'

    @property
    def num(self):
        return get_num_only(self.label)


class AirDataRateChoices(IntegerChoices):
    BPS15625_SF5_BW125KHZ = 0, '15,625[bps]/SF 5/BW 125[kHz]'
    BPS9375_SF6_BW125KHZ = 4, '9,375[bps]/SF 6/BW 125[kHz]'
    BPS5469_SF7_BW125KHZ = 8, '5,496[bps]/SF 7/BW 125[kHz]'
    BPS3125_SF8_BW125KHZ = 12, '3,125[bps]/SF 8/BW 125[kHz]'
    BPS1758_SF9_BW125KHZ = 16, '1,758[bps]/SF 9/BW 125[kHz]'
    BPS31250_SF5_BW250KHZ = 1, '31,250[bps]/SF 5/BW 250[kHz]'
    BPS18750_SF6_BW250KHZ = 5, '18,750[bps]/SF 6/BW 250[kHz]'
    BPS10938_SF7_BW250KHZ = 9, '10,938[bps]/SF 7/BW 250[kHz]'
    BPS6250_SF8_BW250KHZ = 13, '6,250[bps]/SF 8/BW 250[kHz]'
    BPS3516_SF9_BW250KHZ = 17, '3,516[bps]/SF 9/BW 250[kHz]'
    BPS1953_SF10_BW250KHZ = 21, '1,953[bps]/SF 10/BW 250[kHz]'
    BPS62500_SF5_BW500KHZ = 2, '62,500[bps]/SF 5/BW 500[kHz]'
    BPS37500_SF6_BW500KHZ = 6, '37,500[bps]/SF 6/BW 500[kHz]'
    BPS21875_SF7_BW500KHZ = 10, '21,875[bps]/SF 7/BW 500[kHz]'
    BPS12500_SF8_BW500KHZ = 14, '12,500[bps]/SF 8/BW 500[kHz]'
    BPS7031_SF9_BW500KHZ = 18, '7,031[bps]/SF 9/BW 500[kHz]'
    BPS3906_SF10_BW500KHZ = 22, '3,906[bps]/SF 10/BW 500[kHz]'
    BPS2148_SF11_BW500KHZ = 26, '2,148[bps]/SF 11/BW 500[kHz]'

    @property
    def num(self):
        arr = self.label.split('/')
        return [get_num_only(a) for a in arr]


class SubPacketLengthChoices(IntegerChoices):
    BYTE200 = 0, '200[byte]'
    BYTE128 = 1, '128[byte]'
    BYTE64 = 2, '64[byte]'
    BYTE32 = 3, '32[byte]'

    @property
    def num(self):
        return get_num_only(self.label)


class TxPowerChoices(IntegerChoices):
    DBM13 = 0, '13[dBm]'
    DBM12 = 1, '12[dBm]'
    DBM7 = 2, '7[dBm]'
    DBM0 = 3, '0[dBm]'

    @property
    def num(self):
        return get_num_only(self.label)


class TxMethodChoices(IntegerChoices):
    TRANSPARENT = 0, 'トランスペアレント送信モード'
    FIX = 1, '固定送信モード'


class WORCycleChoices(IntegerChoices):
    MS500 = 0, '500[ms]'
    MS1000 = 1, '1000[ms]'
    MS1500 = 2, '1500[ms]'
    MS2000 = 3, '2000[ms]'
    MS2500 = 4, '2500[ms]'
    MS3000 = 5, '3000[ms]'

    @property
    def num(self):
        return get_num_only(self.label)


class Mode(IntEnum):
    NORMAL = auto()
    WOR_SEND = auto()
    WOR_RECV = auto()
    SLEEP = auto()

    @classmethod
    def parse(cls, m0, m1):
        MODES = {
            (False, False): Mode.NORMAL,
            (False, True): Mode.WOR_SEND,
            (True, False): Mode.WOR_RECV,
            (True, True): Mode.SLEEP,
        }
        return MODES[(m1, m0)]

    def pins(self):
        MODES = {
            Mode.NORMAL: (False, False),
            Mode.WOR_SEND: (False, True),
            Mode.WOR_RECV: (True, False),
            Mode.SLEEP: (True, True),
        }

        return MODES[self]

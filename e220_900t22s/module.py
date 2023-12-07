import threading
import time
import typing as typ

from RPi_GPIO_Helper import GPIO, Pin
from serial import Serial

from e220_900t22s import calc_rssi
from e220_900t22s.enums import Mode, TxMethodChoices
from e220_900t22s.register import ExtendRegister, Register


class E220_900T22S:
    SLEEP = 0.2

    @classmethod
    def create(cls, register: Register, ser_name: str, m0_pin: int, m1_pin: int, aux_pin: int, timeout=SLEEP, pull_up_down=GPIO.PUD_OFF, **kwargs):
        ser = Serial(ser_name, timeout=timeout, **kwargs)
        m0 = Pin(m0_pin, GPIO.OUT, initial=GPIO.HIGH)
        m1 = Pin(m1_pin, GPIO.OUT, initial=GPIO.HIGH)
        aux = Pin(aux_pin, GPIO.IN, pull_up_down=pull_up_down)
        return E220_900T22S(register, ser, m0, m1, aux)

    def __init__(self, register: Register, ser: Serial, m0: Pin, m1: Pin, aux: Pin):
        self.__reg: Register = register
        self.__ser: Serial = ser
        self.__m0: Pin = m0
        self.__m1: Pin = m1
        self.__aux: Pin = aux
        self.__mutex = threading.RLock()
        self.__mode = Mode.parse(m0.initial, m1.initial)
        self
        time.sleep(self.SLEEP)

    @property
    def mode(self):
        return self.__mode

    def __del__(self):
        self.__ser.close()

    def __exit__(self):
        self.__ser.close()

    def mutex_func(self, func: typ.Callable, *args, **kwargs) -> typ.Any:
        ret = None
        self.__mutex.acquire()
        try:
            ret = func(*args, **kwargs)
        except BaseException:
            raise
        finally:
            self.__mutex.release()

        return ret

    def change_mode(self, mode: Mode):
        def func():
            self.mode = mode
            m0, m1 = mode.pins()
            self.__m0.output(m0)
            self.__m1.output(m1)
            time.sleep(self.SLEEP)

        self.mutex_func(func)

    def get_aux(self) -> bool:
        def func():
            return self.__aux.input()

        return self.mutex_func(func)

    def write(self, data: bytes) -> int:
        def func():
            return self.__ser.write(data)

        return self.mutex_func(func)

    def send(self, address: int, channel: int, data: bytes) -> int:
        addh = address & 0xff00 >> 8
        addl = address & 0x00ff
        prefix_data = {
            TxMethodChoices.TRANSPARENT: bytes(),
            TxMethodChoices.FIX: bytes([addh, addl, channel]),
        }
        wdata = prefix_data[self.__reg.tx_method] + data

        return self.__ser.write(wdata)

    def read(self, read_len: typ.Optional[int] = None) -> bytes:
        def func(size):
            return self.__ser.read(size)

        max_len = self.__reg.sub_packet_length
        read_len = read_len or max_len
        if max_len < read_len:
            raise ValueError(f'exceeded max length. max {max_len}, in {read_len}.')

        ret = bytes()
        try:
            ret = self.mutex_func(func, read_len)
        except BaseException:
            pass

        return ret

    def get_rssi(self, data: bytes):
        return self.__reg.rssi_byte_enable and calc_rssi(data[-1])

    def configure(self) -> bool:
        wdata = bytes([0xc0, 0x00, 0x08]) + self.__reg.to_data()
        self.change_mode(Mode.SLEEP)
        wlen = self.write(wdata)
        rdata = self.read(len(wdata))
        res = wlen == len(rdata)

        return res

    def read_ex_reg(self) -> ExtendRegister:
        ret = ExtendRegister(0, 0)
        if not (self.__reg.rssi_noise_enable or (self.mode in [Mode.NORMAL, Mode.WOR_SEND])):
            return ret
        wdata = bytes([0xc0, 0xc1, 0xc2, 0xc3])
        wlen = self.write(wdata)
        rdata = self.read(len(wdata))
        if wlen == len(rdata):
            ret = ExtendRegister.parse(rdata)

        return ret

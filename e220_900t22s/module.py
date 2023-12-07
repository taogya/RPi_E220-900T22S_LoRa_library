import threading
import time
import typing as typ

from serial import Serial
from RPi_GPIO_Helper import GPIO, Pin
from e220_900t22s.register import Register
from e220_900t22s.enums import TxMethodChoices, Mode


class E220_900T22S:
    SLEEP = 0.1
    MODES = {
        Mode.NORMAL: (False, False),
        Mode.WOR_SEND: (False, True),
        Mode.WOR_RECV: (True, False),
        Mode.SLEEP: (True, True),
    }

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
        m0, m1 = self.MODES[mode]

        def func():
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

    def configure(self) -> bool:
        print(self.__reg)
        wdata = bytes([0xc0, 0x00, 0x08]) + self.__reg.to_data()
        print(wdata)
        self.change_mode(Mode.SLEEP)
        wlen = self.write(wdata)
        rdata = self.read(len(wdata))
        print(rdata)
        res = wlen == len(rdata)

        return res

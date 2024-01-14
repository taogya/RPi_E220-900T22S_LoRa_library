import datetime as dt
import threading
import time
import traceback

from e220_900t22s.enums import (AirDataRateChoices, SerialPortRateChoices,
                                SubPacketLengthChoices, TxMethodChoices,
                                TxPowerChoices, WORCycleChoices)
from e220_900t22s.module import E220_900T22S
from e220_900t22s.register import Register
from RPi_GPIO_Helper import GPIO, Pin
from serial import Serial

# Register Setting
address = 0x0000
target_address = 0x0001
channel = 0
reg = Register(
    address=address,
    serial_port_rate=SerialPortRateChoices.BPS9600,
    air_data_rate=AirDataRateChoices.BPS1758_SF9_BW125KHZ,
    sub_packet_length=SubPacketLengthChoices.BYTE200,
    rssi_noise_enable=True,
    tx_power=TxPowerChoices.DBM13,
    channel=channel,
    rssi_byte_enable=True,
    tx_method=TxMethodChoices.FIX,
    wor_cycle=WORCycleChoices.MS2000,
    crypt_key=0x0000,
)
# Port Initialize
ser = Serial('/dev/ttyS0', 9600, 8, 'N', 1, 0.2)
m0 = Pin(23, GPIO.OUT, initial=GPIO.HIGH)
m1 = Pin(24, GPIO.OUT, initial=GPIO.HIGH)
aux = Pin(25, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

running = True

with E220_900T22S(reg, ser, m0, m1, aux) as device:
    device: E220_900T22S = device

    def recv():
        global running
        while running:
            try:
                data = device.read()
                if not data:
                    continue
                print(f'received: {data}({data.hex()})')
            except BaseException:
                traceback.print_exc()

    recv_th = threading.Thread(target=recv)

    def send():
        global running
        while running:
            try:
                time.sleep(3)
                data = bytes(dt.datetime.now().isoformat().encode('utf8'))
                device.send(target_address, channel, data)
                print(f'sent: {data}(0x{data.hex()})')
            except KeyboardInterrupt:
                print('KeyboardInterrupt')
                running = False
                recv_th.join()
            except BaseException:
                traceback.print_exc()

    recv_th.start()
    send()

print('finished')

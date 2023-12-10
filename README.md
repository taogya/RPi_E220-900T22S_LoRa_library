# RPi_E220-900T22S_LoRa_library
E220-900T22S Python Library for Raspberry Pi

# Installation
```
pip install rpi-e220-900t22s-lora-library
```

# Example
```sh
# uart setup
sudo usermod -aG dialout <username>
sudo usermod -aG gpio <username>
sudo raspi-config
    -> Interface Options
    -> Serial Port
    -> PC serial: no
    -> Hardware serial: yes
    -> ok
# reboot
```
```python
from e220_900t22s.module import E220_900T22S
from e220_900t22s.register import Register
from e220_900t22s.enums import (SerialPortRateChoices, AirDataRateChoices, 
                                SubPacketLengthChoices, TxPowerChoices, 
                                TxMethodChoices, WORCycleChoices, Mode)
from RPi_GPIO_Helper import GPIO

# Port Initialize
dev = '/dev/ttyS0'
m0 = 23
m1 = 24
aux = 25
GPIO.cleanup(m0)
GPIO.cleanup(m1)
GPIO.cleanup(aux)
GPIO.setmode(GPIO.BCM)

# Register Setting
reg = Register(
    address=0x0000,
    serial_port_rate=SerialPortRateChoices.BPS9600,
    air_data_rate=AirDataRateChoices.BPS1758_SF9_BW125KHZ,
    sub_packet_length=SubPacketLengthChoices.BYTE200,
    rssi_noise_enable=True,
    tx_power=TxPowerChoices.DBM13,
    channel=0,
    rssi_byte_enable=True,
    tx_method=TxMethodChoices.FIX,
    wor_cycle=WORCycleChoices.MS2000,
    crypt_key=0x0000,
)
module = E220_900T22S.create(reg, dev, m0, m1, aux)
module.configure()
module.change_mode(Mode.NORMAL)

# Sender
ret = module.send(0x0000, 0, bytes('Hello world'))

# Receiver
ret = module.read()
print(ret)

module.change_mode(Mode.SLEEP)
module.close()
```

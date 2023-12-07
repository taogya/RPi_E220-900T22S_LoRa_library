# RPi_E220-900T22S_LoRa_library
E220-900T22S Python Library for Raspberry Pi

# Installation
```
pip install rpi-e220-900t22s-lora-library
```

# Example
```sh
# uart setup
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
                                TxMethodChoices, WORCycleChoices)
from RPi_GPIO_Helper import GPIO

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

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
module = E220_900T22S.create(
    reg,
    '/dev/ttyS0',
    23,
    24,
    25,
)
module.configure()

```

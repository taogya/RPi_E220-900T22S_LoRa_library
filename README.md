# RPi_E220-900T22S_LoRa_library
E220-900T22S Python Library for Raspberry Pi

# Installation
```
pip install e220-900t22s
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
[Sample Code](example/sample.py)

import typing as typ

from RPi_GPIO_Helper import Pin

from e220_900t22s import calc_rssi
from e220_900t22s.enums import (AirDataRateChoices, SerialPortRateChoices,
                                SubPacketLengthChoices, TxMethodChoices,
                                TxPowerChoices, WORCycleChoices)


class Register(typ.NamedTuple):
    # モジュールアドレス
    address: int = 0x0000
    # シリアルポートレート
    serial_port_rate: SerialPortRateChoices = SerialPortRateChoices.BPS9600
    # 空間伝送レート
    air_data_rate: AirDataRateChoices = AirDataRateChoices.BPS1758_SF9_BW125KHZ
    # サブパケット長
    sub_packet_length: SubPacketLengthChoices = SubPacketLengthChoices.BYTE200
    # RSSI 環境ノイズの有効化
    rssi_noise_enable: bool = True
    # 送信出力電力
    tx_power: TxPowerChoices = TxPowerChoices.DBM13
    # 周波数チャンネル
    channel: int = 0
    # RSSI バイトの有効化
    rssi_byte_enable: bool = True
    # 送信方法
    tx_method: TxMethodChoices = TxMethodChoices.FIX
    # WOR サイクル
    wor_cycle: WORCycleChoices = WORCycleChoices.MS2000
    # 暗号化キー
    crypt_key: int = 0x0000

    @property
    def ADDH(self):
        return self.address & 0xff00 >> 8

    @property
    def ADDL(self):
        return self.address & 0x00ff

    @property
    def REG0(self):
        return self.serial_port_rate << 5 | self.air_data_rate

    @property
    def REG1(self):
        return self.sub_packet_length << 6 | self.rssi_noise_enable << 5 | self.tx_power

    @property
    def REG2(self):
        return self.channel

    @property
    def REG3(self):
        return self.rssi_byte_enable << 7 | self.tx_method << 6 | self.wor_cycle

    @property
    def CRYPT_H(self):
        return self.crypt_key & 0xff00 >> 8

    @property
    def CRYPT_L(self):
        return self.crypt_key & 0x00ff

    def to_data(self):
        return bytes([
            self.ADDH,
            self.ADDL,
            self.REG0,
            self.REG1,
            self.REG2,
            self.REG3,
            self.CRYPT_H,
            self.CRYPT_L,
        ])

    @classmethod
    def valid_address(cls, address):
        if not (0 <= address <= 65535):
            raise ValueError(f'address out of range -> {address}')

    @classmethod
    def valid_crypt_key(cls, crypt_key):
        if not (0 <= crypt_key <= 65535):
            raise ValueError(f'crypt_key out of range -> {crypt_key}')

    @classmethod
    def valid_channel(cls, air_data_rate, channel):
        adrc = AirDataRateChoices
        if (air_data_rate in [adrc.BPS15625_SF5_BW125KHZ,
                              adrc.BPS9375_SF6_BW125KHZ,
                              adrc.BPS5469_SF7_BW125KHZ,
                              adrc.BPS3125_SF8_BW125KHZ,
                              adrc.BPS1758_SF9_BW125KHZ]):
            if (channel > 37):
                raise ValueError(f'channel out of range -> {air_data_rate} > 37')
        elif (air_data_rate in [adrc.BPS31250_SF5_BW250KHZ,
                                adrc.BPS18750_SF6_BW250KHZ,
                                adrc.BPS10938_SF7_BW250KHZ,
                                adrc.BPS6250_SF8_BW250KHZ,
                                adrc.BPS3516_SF9_BW250KHZ,
                                adrc.BPS1953_SF10_BW250KHZ]):
            if (channel > 36):
                raise ValueError(f'channel out of range -> {air_data_rate} > 36')
        elif (air_data_rate in [adrc.BPS62500_SF5_BW500KHZ,
                                adrc.BPS37500_SF6_BW500KHZ,
                                adrc.BPS21875_SF7_BW500KHZ,
                                adrc.BPS12500_SF8_BW500KHZ,
                                adrc.BPS7031_SF9_BW500KHZ,
                                adrc.BPS3906_SF10_BW500KHZ,
                                adrc.BPS2148_SF11_BW500KHZ]):
            if (channel > 30):
                raise ValueError(f'channel out of range -> {air_data_rate} > 30')

    def valid(self):
        self.valid_address(self.address)
        self.valid_crypt_key(self.crypt_key)
        self.valid_channel(self.air_data_rate, self.channel)

    @classmethod
    def parse(cls, data: bytes) -> 'Register':
        obj = Register(
            address=data[0] << 8 | data[1],
            serial_port_rate=SerialPortRateChoices(data[2] >> 5),
            air_data_rate=AirDataRateChoices(data[2] & 0x1f),
            sub_packet_length=SubPacketLengthChoices(data[3] >> 6),
            rssi_noise_enable=(data[3] >> 5) & 0x01,
            tx_power=data[3] & 0x03,
            channel=data[4],
            rssi_byte_enable=data[5] >> 7,
            tx_method=TxMethodChoices((data[5] >> 6) & 0x01),
            wor_cycle=WORCycleChoices(data[5] & 0x07),
            crypt_key=data[6] << 8 | data[7],
        )

        obj.valid(obj)

        return obj


class ExtendRegister(typ.NamedTuple):
    # 現在のRSSI環境ノイズ
    now_rssi: int = 0
    # 前回のRSSI
    before_rssi: int = 0

    @classmethod
    def parse(cls, data: bytes) -> 'ExtendRegister':
        obj = ExtendRegister(
            now_rssi=calc_rssi(data[0]),
            before_rssi=calc_rssi(data[1]),
        )

        return obj

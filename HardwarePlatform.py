# Soubor pripravujici nazvy funkci jake pouziva microbit
from adafruit_ticks import ticks_diff as adf_ticks_diff, ticks_ms as adf_ticks_ms
from time import monotonic_ns, sleep as time_sleep
from board import P0, P1, P8, P12, P13, P14, P15, P19, P20
from digitalio import DigitalInOut, Direction
from picoed import display, i2c as pico_i2c
from pwmio import PWMOut

class I2C:
    def __init__(self) -> None:
        self.picoed_i2c = pico_i2c
        
    def init(self, freq:int=100_000, sda=P20, scl=P19):
        pass
    
    def __lock(self) -> None:
        while not self.picoed_i2c.try_lock():
            pass

    def __unlock(self) -> None:
        self.picoed_i2c.unlock()
        
    def scan(self) -> list[int]:
        self.__lock()
        ret = self.picoed_i2c.scan()
        self.__unlock()
        return ret
       
    def read(self, addr:int, n:int, repeat:bool=False) -> bytearray:
        self.__lock()
        buffer = bytearray(n)
        self.picoed_i2c.readfrom_into(addr, buffer, start=0, end=n)
        self.__unlock()
        return buffer
    
    def write(self, addr:int, buf:bytearray, repeat:bool=False) -> None:
        self.__lock()
        self.picoed_i2c.writeto(addr, buf)
        self.__unlock()

i2c = I2C()

class PinPWM:
    def __init__(self, pin) -> None:
        self.pinName = pin
        self.pwm = None
        
    def set_analog_period(self, periodMS:int) -> None:
        freq = int(1 / (periodMS / 1000))
        self.pwm = PWMOut(self.pinName, frequency=freq)

    def write_analog(self, value) -> None:
        self.pwm.duty_cycle = int(value)

class PinDigital:
    def __init__(self, pin) -> None:
        self.pinName = pin
        self.pin = DigitalInOut(self.pinName)
        
    def read_digital(self) -> int:
        if self.pin.value:
            return 1
        return 0

    def write_digital(self, value) -> None:
        self.pin.direction = Direction.OUTPUT    
        self.pin.value = (value!=1)

pin0 = P0
pin1 = PinPWM(P1)
pin8 = PinDigital(P8)
pin12 = PinDigital(P12)
pin13 = PinPWM(P13)
pin14 = PinDigital(P14)
pin15 = PinDigital(P15)

def sleep(ms) -> None:
    time_sleep(ms / 1000)

def ticks_ms() -> int:
    return adf_ticks_ms()

def ticks_us() -> int:
    return monotonic_ns() // 1_000

def ticks_diff(ticks1:int, ticks2:int) -> int:
    return adf_ticks_diff(ticks1, ticks2)

def time_pulse_us(pin, pulse_level: int, timeout_us=1000000) -> int:
    start = ticks_us()
    while pin.read_digital() != pulse_level:
        if ticks_diff(ticks_us(), start) > timeout_us:
            return -1  # Timeout
    start = ticks_us()
    while pin.read_digital() == pulse_level:
        if ticks_diff(ticks_us(), start) > timeout_us:
            return -1  # Timeout
    return ticks_diff(ticks_us(), start)

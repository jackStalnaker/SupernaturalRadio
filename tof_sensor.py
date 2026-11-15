import board
import busio
import adafruit_vl53l0x


def initialize_vL53l0x():
    """Initialize the I2C bus and the VL53L0X sensor."""
    print("Initializing TOF sensor...")
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_vl53l0x.VL53L0X(i2c)
    print("Initializing TOF sensor done.")
    return sensor

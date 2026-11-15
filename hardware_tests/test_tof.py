import time
import board
import busio
import adafruit_vl53l0x

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)

start = time.monotonic()

while True:
    mm = sensor.range
    elapsed = time.monotonic() - start

    if mm > 2000:
        print(f"{elapsed:6.2f}s     NO TARGET")
    else:
        inches = mm / 25.4
        print(f"{elapsed:6.2f}s     {inches:6.2f} inches ({mm} mm)")
    time.sleep(0.1)

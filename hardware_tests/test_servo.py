import time
from rpi_hardware_pwm import HardwarePWM

# GPIO12 uses PWM channel 0
pwm = HardwarePWM(pwm_channel=0, hz=50)

MIN_PULSE_US = 700
MAX_PULSE_US = 2300
PWM_FREQUENCY = 50

def set_angle(angle):
    # Map -90..+90 degrees to 1..2 ms pulses
    angle = max(-90, min(90, angle))

    fraction = (angle + 90) / 180.0
    pulse_us = MIN_PULSE_US + fraction * (MAX_PULSE_US - MIN_PULSE_US)

    period_us = 1_000_000 / PWM_FREQUENCY
    duty_cycle = pulse_us / period_us * 100.0

    pwm.change_duty_cycle(duty_cycle)

try:
    pwm.start(7.5)

    #for angle in [0, -90, 0, 90, 0]:
    while True:
        text = input("Angle or q: ").strip()

        if text.lower() == "q":
            break

        try:
            angle = int(text)
            print(f"Moving to {angle} degrees")
            set_angle(angle)
        except ValueError:
            print("Enter an integer number")

finally:
    pwm.stop()

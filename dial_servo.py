import time
import random
from rpi_hardware_pwm import HardwarePWM


class DialServo:
    MIN_PULSE_US = 700
    MAX_PULSE_US = 2300
    PWM_FREQUENCY = 50
    MIN_ANGLE = -90.0
    MAX_ANGLE = 90.0
    MAX_ROTATION = 180.0
    CENTER_ANGLE = 0.0
    MALACHI_ANGLE = 90.0  # Where malachi is on the dial

    def __init__(self):
        print("Initializing DialServo...")
        # GPIO12 uses PWM channel 0
        self.pwm = HardwarePWM(pwm_channel=0, hz=50)
        self.pwm.start(7.5)
        print("Initializing DialServo done.")

    def __del__(self):
        self.pwm.stop()

    def set_angle(self, angle):
        # Map -90..+90 degrees to 1..2 ms pulses
        angle = max(self.MIN_ANGLE, min(self.MAX_ANGLE, angle))

        fraction = (angle + self.MAX_ANGLE) / self.MAX_ROTATION
        pulse_us = self.MIN_PULSE_US + fraction * (self.MAX_PULSE_US - self.MIN_PULSE_US)

        period_us = 1_000_000 / self.PWM_FREQUENCY
        duty_cycle = pulse_us / period_us * 100.0

        self.pwm.change_duty_cycle(duty_cycle)

    def center(self):
        self.set_angle(self.CENTER_ANGLE)

    def go_to_malachi(self):
        self.set_angle(self.MALACHI_ANGLE)

    def random_sweep_during(self, process, min_segment=0.3, max_segment=0.8):
        '''Sweep the servo back and forth while some process runs.
        
        Args:
            process:
                subprocess to sweep during. Sweep ends when the process ends, 
                though it will continue to its last ordered position.
            min_segment:
                minimum random sweep movement duration
            max_segment:
                maximum random sweep movement duration
        '''
        last_change = 0
        segment_duration = 0
        angles = [self.MIN_ANGLE + 20, self.MAX_ANGLE - 20]
        direction = 0

        while process.poll() is None:
            now = time.monotonic()
            if now - last_change > segment_duration:
                segment_duration = random.uniform(min_segment, max_segment)
                last_change = now

                direction = not direction
                self.set_angle(angles[direction])
    
class MockProcess:
    '''Mock process for testing random_sweep_during'''
    def __init__(self, duration):
        self.end_time = time.monotonic() + duration

    def poll(self):
        if time.monotonic() < self.end_time:
            return None
        return 0


def main():
    dial_servo = DialServo()

    try:
        for angle in [0, -90, 0, 90]:
            dial_servo.set_angle(angle)
            time.sleep(3)

        proc = MockProcess(3)
        dial_servo.random_sweep_during(proc)

    finally:
        dial_servo.center()


if __name__ == "__main__":
    main()

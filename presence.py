import time
import threading
from enum import Enum, auto
from tof_sensor import initialize_vL53l0x

class PresenceState(Enum):
    ABSENT = auto()
    PRESENT_CANDIDATE = auto()
    PRESENT = auto()
    ABSENT_CANDIDATE = auto()

class Presence:
    """Detect presence or absence of a target with a time of flight (ToF) sensor."""

    OUT_OF_RANGE = 8190
    MAX_DISTANCE = 50.0  # Max detection distance in inches
    PRESENT_THRESHOLD = 1.0  # Time required to consider guest present
    ABSENT_THRESHOLD = 5.0   # Time required to consider guest absent
    DETECTION_POLL = 0.25

    def __init__(self, sensor):
        print("Initializing Presence...")
        self.sensor = sensor
        self.present_start_time = None
        self.absent_start_time = None
        self.state = PresenceState.ABSENT
        self.distance = None
        self._became_present = threading.Event()
        self._became_absent = threading.Event()
        self._monitoring = False
        self._monitor_thread = None
        print("Initializing Presence done.")

    def start_monitoring(self):
        # Make this function safe to call repeatedly even if thread is already running
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()

    def _monitor(self):
        while self._monitoring:
            self.update()
            time.sleep(self.DETECTION_POLL)

    def stop_monitoring(self):
        self._monitoring = False
        if self._monitor_thread is not None:
            self._monitor_thread.join()

    def read_distance(self):
        """Read the distance from the sensor."""
        self.distance = self.sensor.range
        if self.distance >= self.OUT_OF_RANGE:
            self.distance = None
        return self.distance

    @property
    def distance_inches(self):
        if self.distance is None:
            return None
        else:
            return self.distance / 25.4

    def update(self):
        self.read_distance()
        detected = self.distance_inches is not None and self.distance_inches < self.MAX_DISTANCE
        if (detected):
            print("detected presence")

        if detected:
            if self.state == PresenceState.ABSENT:
                self.state = PresenceState.PRESENT_CANDIDATE
                self.present_start_time = time.monotonic()

            elif self.state == PresenceState.PRESENT_CANDIDATE:
                if self.threshold_reached(self.present_start_time, self.PRESENT_THRESHOLD):
                    print("Presence threshold reached")
                    self.state = PresenceState.PRESENT
                    self._became_present.set()
                    self._became_absent.clear()  # just in case there was an unhandled absent event
                    
            elif self.state == PresenceState.ABSENT_CANDIDATE:
                self.absent_start_time = None
                self.state = PresenceState.PRESENT
                

        else:
            if self.state == PresenceState.PRESENT:
               self.state = PresenceState.ABSENT_CANDIDATE
               self.absent_start_time = time.monotonic()

            elif self.state == PresenceState.ABSENT_CANDIDATE:
                if self.threshold_reached(self.absent_start_time, self.ABSENT_THRESHOLD):
                    print("Absence threshold reached")
                    self.state = PresenceState.ABSENT
                    self._became_absent.set()
                    self._became_present.clear()  # just in case there was an unhandled present event

            elif self.state == PresenceState.PRESENT_CANDIDATE:
                self.present_start_time = None
                self.state = PresenceState.ABSENT

    def threshold_reached(self, start_time, threshold):
        elapsed_time = time.monotonic() - start_time
        return elapsed_time >= threshold

    def wait_until_present(self, timeout=None):
        detected = self._became_present.wait(timeout=timeout)
        if detected: 
            self._became_present.clear()
        return detected

    def wait_until_absent(self, timeout=None):
        detected = self._became_absent.wait(timeout=timeout)
        if detected:
            self._became_absent.clear()
        return detected


    @property
    def is_present(self):
        return self.state in (PresenceState.PRESENT, PresenceState.ABSENT_CANDIDATE)

    @property
    def is_absent(self):
        return self.state in (PresenceState.ABSENT, PresenceState.PRESENT_CANDIDATE)

    def became_present(self):
        if self._became_present.is_set():
            self._became_present.clear()
            return True
        return False

    def became_absent(self):
        if self._became_absent.is_set():
            self._became_absent.clear()
            return True
        return False    

class MockSensor():
    """A mock sensor for testing."""
    def __init__(self):
        self.start_time = time.monotonic()

    @property
    def range(self):
        elapsed = time.monotonic() - self.start_time
        if elapsed <= 2.0:
            return 8190  # Out of range
        if elapsed <= 4.0:
            return 4000  # Past max distance
        elif elapsed <= 8.0:
            return 1     # Detected
        else:
            self.start_time = time.monotonic()
            return 1


def main():
    # sensor = MockSensor()
    sensor = initialize_vL53l0x()
    presence = Presence(sensor)

    # Run one cyle of tne mock sensor
    start = time.monotonic()
    while time.monotonic() - start < 12.0:
        presence.update()
        time.sleep(0.25)
        if presence.distance is None:
            print("Out of range")
        else:
            print(f"{presence.distance} mm, {presence.distance_inches:6.2f} inches")
        print(f"{presence.state}")
        print(f"is present? {presence.is_present}, is absent? {presence.is_absent}")
        print(f"became present? {presence.became_present()}, became absent? {presence.became_absent()}")

    # Now test the monitoring service
    presence.start_monitoring()
    presence.wait_until_present()
    print("Present event detected")
    presence.wait_until_absent()
    print("Absent event detected")

    # test the timeout
    if not presence.wait_until_present(timeout=1):
        print("Present event monitor timed out.")
    if not presence.wait_until_absent(timeout=1):
        print("Absent event monitor timed out.")
    presence.stop_monitoring()


if __name__ == "__main__":
    main()

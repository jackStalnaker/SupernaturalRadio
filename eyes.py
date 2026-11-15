import time
import cv2
import base64
from picamera2 import Picamera2

class Eyes:
    """Malachi's eyes. Handle capturing and encoding images."""
    def __init__(self):
        print("Eyes initializing...")
        self.CAMERA_FILENAME = "haunt_scene.jpg"  # Output filename for camera capture
        self.CAMERA_ENC_FILENAME = "haunt_scene.txt"  # Output filename for encoded camera capture

        self.camera = Picamera2()

        config = self.camera.create_preview_configuration(
                main={"size": (1280, 720), "format": "RGB888"},
                buffer_count=3
        )
        
        self.camera.configure(config)
        self.camera.start()
        print("Eyes done initializing.")

    def capture_frame(self):
        """Capture a camera image as an OpenCV-compatible array."""
        return self.camera.capture_array()

    def encode_frame(self, frame):
        """Encode image as text."""
        success, buffer = cv2.imencode('.jpg', frame)

        if not success:
            raise RuntimeError("Failed to encode image to JPEG format.")
        
        return base64.b64encode(buffer).decode('utf-8')

    def capture_encoded_frame(self):
        frame = self.capture_frame()
        return self.encode_frame(frame)

    def write_frame(self, frame):
        cv2.imwrite(self.CAMERA_FILENAME, frame)

    def write_encoded_frame(self, encoded_frame):
        with open(self.CAMERA_ENC_FILENAME, "w") as f:
            f.write(encoded_frame)

    def close(self):
        """Release camera resources."""
        self.camera.stop()
        self.camera.close()

def main():
    eyes = Eyes()

    try:
        time.sleep(2)  # Allow auto-exposure and white balance to settle

        frame = eyes.capture_frame()
        eyes.write_frame(frame)
        encoded_frame = eyes.encode_frame(frame)
        eyes.write_encoded_frame(encoded_frame)

    finally:
        eyes.close()

if __name__ == "__main__":
    main()

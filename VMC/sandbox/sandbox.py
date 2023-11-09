# Imports
import time
from threading import Thread
from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrApriltagsRawPayload

# Loguru is good for logging.
# https://loguru.readthedocs.io/en/stable/
from loguru import logger


# Sandbox class
class Sandbox(MQTTModule):
    def __init__(self) -> None:
        super().__init__()
        #                  message that the | method that runs
        #                  code is          | when message is received
        #                  listening for    |
        self.topic_map = {"avr/apriltags/raw": self.handle_apriltag}

    def handle_apriltag(self) -> None:
        payload = AvrApriltagsRawPayload
        # Flashes green, blue, green on AprilTag 0 (Total duration 0.75 seconds)
        if payload["tags"][0]["id"] == 0:
            self.flash_led([0, 0, 255, 0], 0.25)
            print("Flashing green...")
            time.sleep(0.25)
            self.flash_led([0, 0, 0, 255], 0.25)
            print("Flashing blue...")
            time.sleep(0.25)
            self.flash_led([0, 0, 255, 0], 0.25)
            print("Flashing green...")
            time.sleep(0.25)
        # Flashed red 3 times on AprilTag 4/5/6 (Total duration 0.75 seconds)
        if payload["tags"][0]["id"] == 4 or payload["tags"][0]["id"] == 5 or payload["tags"][0]["id"] == 6:
            for _ in range(3):
                print("Flashing red...")
                self.flash_led([255, 0, 0, 0], 0.125)
                time.sleep(0.125)
                self.flash_led([0, 0, 0, 0], 0.125)
                time.sleep(0.125)

    def flash_led(self, color: list, duration: float) -> None:
        # Colors LED temporarily
        self.send_message(
            "avr/pcm/set_temp_color",
            {"wrgb": color, "duration": duration}
        )

if __name__ == "__main__":
    box = Sandbox()
    
    # Run method lets sandbox listen for MQTT messages
    box.run()

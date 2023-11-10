# Imports
import time
from threading import Thread, Event
from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrApriltagsRawPayload

# Loguru is good for logging.
# https://loguru.readthedocs.io/en/stable/
from loguru import logger


# Sandbox class
class Sandbox(MQTTModule):
    def __init__(self) -> None:
        super().__init__()
        self.flash_event = Event()
        #                  message that the | method that runs
        #                  code is          | when message is received
        #                  listening for    |
        self.topic_map = {"avr/apriltags/raw": self.handle_apriltag,
                          "avr/go": self.recon_path}

    def recon_path(self) -> None:
        # fingers crossed
        self.send_message(
            "avr/fcm/capture_home",
            {}
        )
        self.send_message(
            "avr/fcm/actions",
            {"action": "arm", "payload": {}}
        )
        self.send_message(
            "avr/fcm/actions",
            {"action": "takeoff", "payload": {}}
        )
        self.send_message(
            "avr/fcm/actions",
            {
                "action": "goto_location_ned",
                "payload": {
                    "n": 0.0,
                    "e": 0.0,
                    "d": -3.7544,
                    "heading": 359.99
                }
            }
        self.send_message(
            "avr/fcm/actions",
            {
                "action": "goto_location_ned",
                "payload": {
                    "n": 5.6896,
                    "e": -1.778,
                    "d": -3.7544,
                    "heading": 359.99
                }
            }
        )
        self.send_message(
            "avr/fcm/actions",
            {
                "action": "goto_location_ned",
                "payload": {
                    "n": 0.0,
                    "e": 0.0,
                    "d": -3.7544,
                    "heading": 359.99
                }
            }
        )
        self.send_message(
            "avr/fcm/actions",
            {
                "action": "land",
                "payload": {}
            }
        )

    def handle_apriltag(self, payload: AvrApriltagsRawPayload) -> None:
        payload = AvrApriltagsRawPayload
        try:
            id = payload["tags"][0]["id"]
        except Exception as e:
            print(e)
            id = -1
        # Flashes green, blue, green on AprilTag 0 (Total duration 0.625 seconds)
        if id == 0:
            self.flash_led([0, 0, 255, 0], 0.125)
            self.flash_event.wait(0.125)
            self.flash_led([0, 0, 0, 255], 0.125)
            self.flash_event.wait(0.125)
            self.flash_led([0, 0, 255, 0], 0.125)
        # Flashed red 3 times on AprilTag 4/5/6 (Total duration 0.75 seconds)
        if id == 4 or id == 5 or id == 6:
            for _ in range(3):
                self.flash_event.wait(0.125)
                self.flash_led([255, 0, 0, 0], 0.125)

    def flash_led(self, color: list, duration: float) -> None:
        # Colors LED temporarily
        self.send_message(
            "avr/pcm/set_temp_color",
            {"wrgb": color, "duration": duration}
        )

if __name__ == "__main__":
    box = Sandbox()
    # Threading methods makes sure that time.sleep() doesn't make the whole code just stop running.
    # Separates the method's timing system from the rest of the code.
    apriltag_thread = Thread(target=box.handle_apriltag, args=(AvrApriltagsRawPayload,))
    apriltag_thread.setDaemon(True)
    apriltag_thread.start()
    # Run method lets sandbox listen for MQTT messages
    box.run()

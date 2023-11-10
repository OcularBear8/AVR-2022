# Imports
import time
from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrApriltagsRawPayload

# Loguru is good for logging.
# https://loguru.readthedocs.io/en/stable/
from loguru import logger


# Sandbox class
class Sandbox(MQTTModule):
    def __init__(self) -> None:
        super().__init__()
        self.recon1 = False
        self.recon2 = False
        self.recon3 = False
        self.hotspot1 = False
        self.hotspot2 = False
        self.hotspot3 = False
        #                  message that the | method that runs
        #                  code is          | when message is received
        #                  listening for    |
        self.topic_map = {"avr/apriltags/raw": self.handle_apriltag,
                          "avr/go": self.recon_path}

    def recon_path(self, payload) -> None:
        # fingers crossed
        home_captured = False
        armed = False
        takeoff = False
        up = False
        building = False
        back = False
        down = False
        land = False
        path_completed = False
        current_time = time.time()
        while not path_completed:
            if not home_captured:
                self.send_message(
                    "avr/fcm/capture_home",
                    {}
                )
                home_captured = True
            if not armed:
                self.send_message(
                    "avr/fcm/actions",
                    {"action": "arm", "payload": {}}
                )
                armed = True
            if not takeoff and time.time() - current_time > 1:
                self.send_message(
                    "avr/fcm/actions",
                    {"action": "takeoff", "payload": {}}
                )
                takeoff = True
            if not up and time.time() - current_time > 2:
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
                up = True
            if not building and time.time() - current_time > 5:
                self.send_message(
                    "avr/fcm/actions",
                    {
                        "action": "goto_location_ned",
                        "payload": {
                            "n": 5.6896,
                            "e": -1.778,
                            "d": -3.7544,
                            "heading": 180.00
                        }
                    }
                )
                building = True
            if not back and time.time() - current_time > 15:
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
                back = True
            if not down and time.time() - current_time > 22:
                self.send_message(
                    "avr/fcm/actions",
                    {
                        "action": "goto_location_ned",
                        "payload": {
                            "n": 0.0,
                            "e": 0.0,
                            "d": -1,
                            "heading": 359.99
                        }
                    }
                )
                down = True
            if not land and time.time() - current_time > 25:
                self.send_message(
                    "avr/fcm/actions",
                    {
                        "action": "land",
                        "payload": {}
                    }
                )
                land = True
                path_completed = True

    def handle_apriltag(self, payload: AvrApriltagsRawPayload) -> None:
        # Flashes green, blue, green on AprilTag 0 (Total duration 0.625 seconds)
        if id == 0:
            current_time = time.time()
            if not self.recon1:
                self.flash_led([0, 0, 255, 0], 0.25)
                self.recon1 = True
            if time.time() - current_time > 0.25 and not self.recon2:
                self.flash_led([0, 0, 0, 255], 0.25)
                self.recon2 = True
            if time.time() - current_time > 0.5 and not self.recon3:
                self.flash_led([0, 0, 255, 0], 0.25)
                self.recon3 = True
        # Flashed red 3 times on AprilTag 4/5/6 (Total duration 0.75 seconds)
        if id == 4 or id == 5 or id == 6:
            current_time = time.time()
            if not self.hotspot1:
                self.flash_led([0, 255, 0, 0], 0.125)
                self.hotspot1 = True
            if time.time() - current_time > 0.25 and not self.hotspot2:
                self.flash_led([0, 255, 0, 0], 0.125)
                self.hotspot2 = True
            if time.time() - current_time > 0.5 and not self.hotspot3:
                self.flash_led([0, 255, 0, 0], 0.125)
                self.hotspot3 = True

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

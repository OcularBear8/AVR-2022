# Imports
import time
from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrApriltagsVisiblePayload

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
        self.topic_map = {"avr/apriltags/visible": self.handle_apriltag,
                          "avr/go": self.recon_path,
                          "avr/test_recon": self.recon_test,
                          "avr/yes": self.trigger}

    def trigger(self, payload) -> None:
        self.flash_led([0, 255, 255, 255], 0.5)

    def recon_test(self, payload) -> None:
        home_captured = False
        armed = False
        takeoff = False
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
            if not takeoff and time.time() - current_time > 1.0:
                self.send_message(
                    "avr/fcm/actions",
                    {"action": "takeoff", "payload": {"alt": 0.5}}
                )
                takeoff = True
            if not land and time.time() - current_time > 5.0:
                self.send_message(
                    "avr/fcm/actions",
                    {
                        "action": "land",
                        "payload": {}
                    }
                )
                land = True
                path_completed = True

    def recon_path(self, payload) -> None:
        # fingers crossed
        home_captured = False
        armed = False
        takeoff = False
        up = False
        building = False
        flash1 = False
        flash2 = False
        flash3 = False
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
            if not armed and time.time() - current_time > 0.01:
                self.send_message(
                    "avr/fcm/actions",
                    {"action": "arm", "payload": {}}
                )
                armed = True
            if not takeoff and time.time() - current_time > 1.0:
                self.send_message(
                    "avr/fcm/actions",
                    {"action": "takeoff", "payload": {"alt": 0.5}}
                )
                takeoff = True
            if not up and time.time() - current_time > 2.0:
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
            if not building and time.time() - current_time > 5.0:
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
            # flash
            if not flash1 and time.time() - current_time > 12.0:
                self.flash_led([0, 0, 255, 0], 0.125)
                flash1 = True
            if not flash2 and time.time() - current_time > 12.25:
                self.flash_led([0, 0, 0, 255], 0.125)
                flash2 = True
            if not flash3 and time.time() - current_time > 12.5:
                self.flash_led([0, 0, 255, 0], 0.125)
                flash3 = True
            if not back and time.time() - current_time > 15.0:
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
            if not down and time.time() - current_time > 22.0:
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
            if not land and time.time() - current_time > 25.0:
                self.send_message(
                    "avr/fcm/actions",
                    {
                        "action": "land",
                        "payload": {}
                    }
                )
                land = True
                path_completed = True

    def handle_apriltag(self, payload: AvrApriltagsVisiblePayload) -> None:
        # Flashes green, blue, green on AprilTag 0
        id = payload["tags"][0]["id"]
        if id == 0:
            self.flash_led([0, 0, 255, 0], 0.25)
        # Autonomous water drop
        if id == 1 or id == 2 or id == 3:
            self.flash_led([0, 0, 255, 255], 0.25)
        # Flashes red 3 times on AprilTag 4/5/6
        if id == 4 or id == 5 or id == 6:
            self.flash_led([0, 255, 0, 0], 0.25)

    def flash_led(self, color: list, duration: float) -> None:
        # Colors LED temporarily
        self.send_message(
            "avr/pcm/set_temp_color",
            {"wrgb": color, "duration": duration}
        )

if __name__ == "__main__":
    box = Sandbox()
    box.run_non_blocking()
    # Run method lets sandbox listen for MQTT messages
    box.run()

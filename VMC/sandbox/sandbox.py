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
                          "avr/test_recon": self.recon_test}
        # Initializes variables for time control
        self.last_recon_flash_time = 0
        self.last_servo_move = 0

    def recon_test(self, payload) -> None:
        home_captured = False
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
        id = payload["tags"][0]["id"]
        current_time = time.time()
        # Flashes green on 0
        if id == 0 and current_time - self.last_recon_flash_time > 15:
            self.flash_led([0, 0, 255, 0], 0.25)
            time.sleep(0.25)
            self.flash_led([0, 0, 0, 255], 0.25)
            time.sleep(0.25)
            self.flash_led([0, 0, 255, 0], 0.25)
        # Water drop on 1/2/3
        if id in [1, 2, 3] and current_time - self.last_servo_move > 10:
            self.flash_led([0, 0, 255, 255], 0.25)
            self.drop_water()
        # Flashes red on 4/5/6
        if id in [4, 5, 6]:
            self.flash_led([0, 255, 0, 0], 0.25)

    def flash_led(self, color: list, duration: float) -> None:
        # Colors LED temporarily
        self.send_message(
            "avr/pcm/set_temp_color",
            {"wrgb": color, "duration": duration}
        )

    def drop_water(self) -> None:
        self.send_message(
            "avr/pcm/set_servo_open_close",
            {"servo": 0,
             "action": "open"}
        )
        time.sleep(0.05)
        self.send_message(
            "avr/pcm/set_servo_open_close",
            {"servo": 1,
             "action": "open"}
        )
        time.sleep(1.5)
        self.send_message(
            "avr/pcm/set_servo_open_close",
            {"servo": 0,
             "action": "close"}
        )
        time.sleep(0.05)
        self.send_message(
            "avr/pcm/set_servo_open_close",
            {"servo": 1,
             "action": "close"}
        )

if __name__ == "__main__":
    box = Sandbox()
    # Run method lets sandbox listen for MQTT messages
    box.run()

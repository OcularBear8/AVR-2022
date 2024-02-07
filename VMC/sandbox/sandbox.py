# Imports
import time
from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrApriltagsVisiblePayload


# Sandbox class
class Sandbox(MQTTModule):
    def __init__(self) -> None:
        super().__init__()
        #                  message that the | method that runs
        #                  code is          | when message is received
        #                  listening for    |
        self.topic_map = {"avr/apriltags/visible": self.handle_apriltag,
                          "avr/test_led": self.test_led,
                          "avr/test_flight": self.test_flight}

    def handle_apriltag(self, payload: AvrApriltagsVisiblePayload) -> None:
        id = payload["tags"][0]["id"]
        # Flashes green on 0
        if id == 0:
            self.flash_led([0, 0, 255, 0], 0.25)
        # Flashes cyan on 1/2/3
        if id == 1 or id == 2 or id == 3:
            self.flash_led([0, 0, 255, 255], 0.25)
        # Flashes red on 4/5/6
        if id == 4 or id == 5 or id == 6:
            self.flash_led([0, 255, 0, 0], 0.25)

    def test_led(self, payload) -> None:
        color_list = [
            [0, 255, 0, 0],
            [0, 0, 255, 0],
            [0, 0, 0, 255],
            [0, 255, 255, 0],
            [0, 0, 255, 255],
            [0, 255, 0, 255],
            [0, 255, 255, 255]
        ]
        for i in range(7):
            start = time.time()
            while time.time() - start < 0.5:
                pass
            self.send_message(
                "avr/pcm/set_temp_color",
                {"wrgb": color_list[i], "duration": 0.25}
            )
    
    def flash_led(self, color: list, duration: float) -> None:
        # Colors LED temporarily
        self.send_message(
            "avr/pcm/set_temp_color",
            {"wrgb": color, "duration": duration}
        )

    def test_flight(self, payload) -> None:
        # Takes off, waits, lands
        self.send_message(
            "avr/fcm/actions",
            {"action": "arm", "payload": {}}
        )
        time.sleep(2)
        self.send_message(
            "avr/fcm/actions",
            {"action": "takeoff", "payload": {"alt": 0.5}}
        )
        time.sleep(5)
        self.send_message(
            "avr/fcm/actions",
            {"action": "land", "payload": {}}
        )
        time.sleep(2)
        self.send_message(
            "avr/fcm/actions",
            {"action": "disarm", "payload": {}}
        )

if __name__ == "__main__":
    box = Sandbox()
    # Run method lets sandbox listen for MQTT messages
    box.run()

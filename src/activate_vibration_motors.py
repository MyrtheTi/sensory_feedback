"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-02-22 11:33:31
 * @desc [description]
"""

import time

import board
import digitalio


class ActivateVibrationMotor():
    def __init__(self, left_leg=True):
        self.pins = [board.D0, board.D1, board.D2, board.D3,
                     board.D4, board.D5, board.D8]  # level 3 to -3
        self.level_list = [
            {"LEVEL": -4, "PIN": [4, 5, 6], "PREV_TIME": -1,
             "VIBRATION_TIME": -1},
            {"LEVEL": -3, "PIN": [6], "PREV_TIME": -1, "VIBRATION_TIME": -1},
            {"LEVEL": -2, "PIN": [5], "PREV_TIME": -1, "VIBRATION_TIME": -1},
            {"LEVEL": -1, "PIN": [4], "PREV_TIME": -1, "VIBRATION_TIME": -1},
            {"LEVEL": 0, "PIN": [3], "PREV_TIME": -1, "VIBRATION_TIME": -1},
            {"LEVEL": 1, "PIN": [2], "PREV_TIME": -1, "VIBRATION_TIME": -1},
            {"LEVEL": 2, "PIN": [1], "PREV_TIME": -1, "VIBRATION_TIME": -1},
            {"LEVEL": 3, "PIN": [0], "PREV_TIME": -1, "VIBRATION_TIME": -1},
            {"LEVEL": 4, "PIN": [0, 1, 2], "PREV_TIME": -1,
             "VIBRATION_TIME": -1}]
        self.left_leg = left_leg
        self.min_off_time = 0.100  # seconds
        self.max_off_time = 1.000  # seconds
        self.vibration_time = 0.004  # seconds

    def initiate_pin_output(self):
        """ Initiate pins and set the direction to output.
        """
        for i, vibrator in enumerate(self.pins):
            vibrator = digitalio.DigitalInOut(vibrator)
            vibrator.direction = digitalio.Direction.OUTPUT
            self.pins[i] = vibrator

    def configure_levels(self):
        """ Configures the pins for each level. If the right leg is used, the
        pins are reversed, so the cables can always be guided down the leg.
        TODO retrieve the vibration time for each level from a file after calibration
        """
        if not self.left_leg:
            self.pins.reverse()
        for level_conf in self.level_list:
            # level = level_conf["LEVEL"]
            level_conf["PIN"] = [self.pins[i] for i in level_conf["PIN"]]
            level_conf["VIBRATION_TIME"] = self.vibration_time * abs(level_conf["LEVEL"])

    def set_motor_value(self, vibrator_level, value=False):
        """ Turns on or off the vibrating motor by setting the pin value to
        True or False, on or off respectively.

        Args:
            vibrator_list (list of dict): List with instance from level_list.
            value (bool, optional): Sets the pin value. Defaults to False.
        """
        for pin in vibrator_level["PIN"]:
            pin.value = value

    def check_time_to_change(self, level, now):
        """Checks the value of the pins and whether it is time to turn them on
        or off.

        Args:
            level (dict): The level information
            now (timestamp): timestamp of loop
        """
        pin_value = [pin.value for pin in level["PIN"]]

        if all(pin_value) is False:
            # check whether it is time to turn on
            if now >= level["PREV_TIME"] + self.min_off_time:
                level["PREV_TIME"] = now
                self.set_motor_value(level, True)

        else:   # pin_value is True
            # check whether it is time to turn off
            if now >= level["PREV_TIME"] + level["VIBRATION_TIME"]:
                level["PREV_TIME"] = now
                self.set_motor_value(level, False)


if __name__ == "__main__":
    motors = ActivateVibrationMotor()
    motors.initiate_pin_output()
    motors.configure_levels()

    for vibrator_level in motors.level_list:  # loop through levels
        print('level', vibrator_level)

        start = time.monotonic()
        while time.monotonic() - start < 5:  # vibrate each level for 5 seconds
            now = time.monotonic()
            motors.check_time_to_change(vibrator_level, now)

        motors.set_motor_value(vibrator_level, False)  # turn all motors off
    print(motors.level_list)

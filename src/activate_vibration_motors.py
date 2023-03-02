"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-02-22 11:33:31
 * @desc Class for activating the vibration motors to deliver the sensory
 feedback according to predefined levels.
"""

import time

import board
import digitalio


class ActivateVibrationMotor():
    def __init__(self, user, date, left_leg=True):
        self.pins = [board.D0, board.D1, board.D2, board.D3,
                     board.D4, board.D5, board.D8]  # level 3 to -3
        self.level_list = [
            {"LEVEL": -4, "PIN": [4, 5, 6], "PIN_INDEX": [4, 5, 6],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": -3, "PIN": [6], "PIN_INDEX": [6],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": -2, "PIN": [5], "PIN_INDEX": [5],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": -1, "PIN": [4], "PIN_INDEX": [4],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 0, "PIN": [3], "PIN_INDEX": [3],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 1, "PIN": [2], "PIN_INDEX": [2],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 2, "PIN": [1], "PIN_INDEX": [1],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 3, "PIN": [0], "PIN_INDEX": [0],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 4, "PIN": [0, 1, 2], "PIN_INDEX": [0, 1, 2],
             "PREV_TIME": -1, "VIBRATION_TIME": -1}]

        self.pin_index = list(range(0, len(self.pins)))  # 0 to 7
        self.left_leg = left_leg
        self.min_off_time = 0.100  # seconds
        self.max_off_time = 1.000  # seconds
        self.off_time = self.min_off_time

        self.vib_count = 0  # counts the times a motor is turned on
        self.prev_level = None

        self.path = user + '/' + date + '/'

        self.initiate_pin_output()
        self.configure_pins()

    def initiate_pin_output(self):
        """ Initiate pins and set the direction to output.
        """
        for i, vibrator in enumerate(self.pins):
            vibrator = digitalio.DigitalInOut(vibrator)
            vibrator.direction = digitalio.Direction.OUTPUT
            self.pins[i] = vibrator

    def configure_pins(self):
        """ Configures the pins for each level. If the right leg is used, the
        pins are reversed, so the cables can always be guided down the leg.
        """
        if not self.left_leg:
            self.pins.reverse()
        for level_conf in self.level_list:
            # level = level_conf["LEVEL"]
            level_conf["PIN"] = [self.pins[i] for i in level_conf["PIN"]]

    def get_perception_thresholds(self):
        """ Opens file with perceptual thresholds, converts the numbers to
         floats and saves them in a list.
        """
        with open(self.path + 'perceptual_thresholds.csv', 'r') as file:
            lines = file.read()

        names = lines.split(',')
        self.thresholds = [float(t) for t in names]

    def set_thresholds(self):
        """ Configures the vibration time for each level.
        """
        for index, level_conf in enumerate(self.level_list):
            level_conf["VIBRATION_TIME"] = self.thresholds[index]

    def set_motor_value(self, pin_list, value=False):
        """ Turns on or off the vibrating motor by setting the pin value to
        True or False, on or off respectively.

        Args:
            pin_list (list): List with digital output pin.
            value (bool, optional): Sets the pin value. Defaults to False.
        """
        for pin in pin_list:
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
            if now >= level["PREV_TIME"] + self.off_time:
                level["PREV_TIME"] = now
                self.set_motor_value(level["PIN"], True)
                self.vib_count += 1

        else:   # pin_value is True
            # check whether it is time to turn off
            if now >= level["PREV_TIME"] + level["VIBRATION_TIME"]:
                level["PREV_TIME"] = now
                self.set_motor_value(level["PIN"], False)

    def adjust_off_time(self, level):
        """ Adjusts time the vibrators are turned off. If the level is the
        same, the motors are vibrating with a longer interval. If the level
        changes, the motors are vibrating faster again.

        Args:
            level (int): Defines current level.
        """
        if level != self.prev_level:
            # increase frequency if EMG activation changes
            self.off_time = self.min_off_time
            self.vib_count = 0
            self.prev_count = 0
            self.prev_level = level
        else:
            if self.prev_count != self.vib_count:
                # decrease frequency if the EMG activation is the same
                self.off_time += 0.100
                self.prev_count += 1
                if self.off_time > self.max_off_time:
                    self.off_time = self.max_off_time


if __name__ == "__main__":
    user = 'me'
    date = '2023_03_02'  # make sure this folder exists

    motors = ActivateVibrationMotor(user, date)
    motors.get_perception_thresholds()
    motors.set_thresholds()

    for vibrator_level in motors.level_list:  # loop through levels
        print('level', vibrator_level)

        start = time.monotonic()
        while time.monotonic() - start < 5:  # vibrate each level for 5 seconds
            now = time.monotonic()
            motors.check_time_to_change(vibrator_level, now)

        motors.set_motor_value(vibrator_level["PIN"], False)  # turn off
    print(motors.level_list)

"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-11 10:29:57
 * @desc Process EMG data from file: normalise and define activation level
"""

from utils import read_file


class PreprocessEMG():
    def __init__(self, user, date, folder='user_files/',
                 extend='BSMB_MUSCLE_EXTEND', flex='BSMB_MUSCLE_FLEX'):
        self.folder = folder
        self.user = user
        self.date = date
        self.path = f'{self.folder}{self.user}/{self.date}/'

        self.extend = extend
        self.flex = flex
        self.levels = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        self.upper_bound = 500  # upper and lower bound for EMG values
        self.lower_bound = 0
        self.mvc_percentage = 1.0  # mvc percentage to normalise over

        self.mvc = self.create_dict('mvc.csv')
        self.rest = self.create_dict('rest_activity.csv')

    def create_dict(self, file_name):
        """ Loads file with calibration data and saves it in a dict.

        Args:
            file_name (string): file to load

        Returns:
            dict: dict with emg calibration data.
        """
        names, emg = read_file(self.path, file_name, [None, 'float'])
        extend = 1  # order of uart data
        flex = 0

        if 'EXTEND' in names[0]:  # if first column is extend emg
            emg_extend = emg[0]
            emg_flex = emg[1]
        else:
            emg_extend = emg[1]
            emg_flex = emg[0]

        save_dict = {names[0]: emg[0], names[1]: emg[1],
                     flex: emg_flex, extend: emg_extend}
        return save_dict

    def normalise_data_MVC(self, data):
        """
        Clips EMG values to 0 - 500 values to decrease random noise.
        Subtracts the average rest activity from the data.
        Normalises data according to mvc_percentage of the maximum voluntary
        contraction (MVC).

        Args:
            data: raw EMG data of 100 previous measurements

        Returns:
            data frame: with 1 row with the normalised EMG data
        """
        normalised = data

        for muscle in [self.extend, self.flex]:
            emg_value = max(self.lower_bound,
                            min(data[muscle], self.upper_bound))
            emg_signal = emg_value - self.rest[muscle]
            normalised[muscle] = emg_signal / (
                self.mvc_percentage * (self.mvc[muscle] - self.rest[muscle]))

        return normalised

    def threshold_reached(self, data, vib_emg=False):
        """ Sets vib_emg to True when the EMG threshold is reached, EMG > 0.1.

        Args:
            data: normalised EMG data
            vib_emg (bool, optional): Sets feedback activation.
            Defaults to False.

        Returns:
            bool: is True when EMG threshold is reached and feedback should be
            activated.
        """
        if (data[self.extend] > 0.1) | (data[self.flex] > 0.1):
            vib_emg = True
        return vib_emg

    def define_dominant_muscle(self, data):
        """
        Defines vibrator level based on muscle activation based on the
        difference in activation between the extensor and the flexor.
        Subtracts extensor EMG from flexor EMG. Thresholds for the levels
        have been based on the paper from Tchimino et al., 2022.

        Args:
            data: preprocessed and normalised EMG data from both
            flexor and extensor

        Returns:
            int: level, ranging from -4 to 4, -4 = extensor min & flexor max,
            0 = equal contracted, 4 = extensor max & flexor min
        """
        dominant_muscle = data[self.extend] - data[self.flex]
        thresholds = [-0.65, -0.4, -0.2, -0.1, 0.1, 0.2, 0.4, 0.65]
        if dominant_muscle <= thresholds[0]:  # smaller than -0.65
            level = self.levels[0]
        elif dominant_muscle >= thresholds[-1]:  # larger than 0.65
            level = self.levels[-1]
        else:
            for i, t in enumerate(thresholds[:-1]):
                if t <= dominant_muscle < thresholds[i + 1]:
                    level = self.levels[i + 1]
        # print(dominant_muscle)
        return level

"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-11 10:29:57
 * @desc Process EMG data from file: normalise and define activation level
"""


class PreprocessEMG():
    def __init__(self, user, date, folder='', extend='BSMB_MUSCLE_EXTEND',
                 flex='BSMB_MUSCLE_FLEX'):
        self.folder = folder
        self.user = user
        self.date = date
        self.path = self.folder + self.user + '/' + self.date + '/'

        self.extend = extend
        self.flex = flex
        self.levels = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        self.get_MVC()
        self.get_rest_activity()

    def get_rest_activity(self):
        """ Opens file with the average rest activity in each muscle
        and saves these values in a dict.
        """
        with open(self.path + 'rest_activity.csv', 'r') as file:
            lines = file.read().splitlines()

        names = lines[0].split(',')

        extend = 1  # order of uart data
        flex = 0

        emg = lines[1].split(',')

        emg_0 = float(emg[0])  # convert to int
        emg_1 = float(emg[1])

        if 'EXTEND' in names[0]:  # if first column is extend emg
            emg_extend = emg_0
            emg_flex = emg_1
        else:
            emg_extend = emg_1
            emg_flex = emg_0

        self.rest = {names[0]: emg_0, names[1]: emg_1,
                     flex: emg_flex, extend: emg_extend}

    def get_MVC(self):
        """ Opens file with maximum voluntary contraction (mvc) values of the
        user. Reads the file and saves the mvc values in a dict.
        """
        with open(self.path + 'mvc.csv', 'r') as file:
            lines = file.read().splitlines()

        names = lines[0].split(',')

        extend = 1  # order of uart data
        flex = 0

        emg = lines[1].split(',')

        emg_0 = float(emg[0])  # convert to int
        emg_1 = float(emg[1])

        if 'EXTEND' in names[0]:  # if first column is extend emg
            emg_extend = emg_0
            emg_flex = emg_1
        else:
            emg_extend = emg_1
            emg_flex = emg_0

        self.mvc = {names[0]: emg_0, names[1]: emg_1,
                    flex: emg_flex, extend: emg_extend}

    def normalise_data_RMS(self, data):
        """
        Take the root mean square and normalises data according to 40% of the
        maximum voluntary contraction (MVC).

        Args:
            data: raw EMG data of 100 previous measurements

        Returns:
            data frame: with 1 row with the normalised EMG data
        """
        normalised = data.iloc[-1]
        RMS_window = data[[self.extend, self.flex]]
        rms = {self.extend: [], self.flex: []}

        for muscle in [self.extend, self.flex]:
            square = RMS_window[muscle].pow(2)
            rms[muscle] = square.mean(axis=0) ** 0.5 / (0.4 * self.mvc[muscle])

        normalised[self.extend] = rms[self.extend]
        normalised[self.flex] = rms[self.flex]
        return normalised

    def normalise_data_MVC(self, data):
        """
        Subtracts the average rest activity from the data.
        Normalises data according to 40% of the maximum voluntary contraction
        (MVC)

        Args:
            data: raw EMG data of 100 previous measurements

        Returns:
            data frame: with 1 row with the normalised EMG data
        """
        normalised = data
        for muscle in [self.extend, self.flex]:
            emg_signal = data[muscle] - self.rest[muscle]
            normalised[muscle] = emg_signal / (0.4 * self.mvc[muscle])

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

    def define_level(self, data):
        """
        Defines vibrator level based on muscle activation. First, the level is
        defined for each muscle. The final level is the difference between
        the extension and flexion level.

        Args:
            data_frame (data frame): Normalised EMG data from both extensor and
            flexor muscle

        Returns:
            int: level, ranging from -4 to 4, -4 = extensor min & flexor max,
            0 = equal contracted, 4 = extensor max & flexor min
        """
        thresholds = [0.0, 0.1, 0.2, 0.4, 0.65]  # levels 0-4 from Tchimino '22
        level_extend = None
        level_flex = None
        # print(data_frame[[extend, flex]])
        for i, t in enumerate(thresholds[:-1]):
            if data[self.extend] >= thresholds[-1]:  # larger than 0.65
                level_extend = 4
            elif t <= data[self.extend] < thresholds[i + 1]:
                level_extend = i

            if data[self.flex] >= thresholds[-1]:  # larger than 0.65
                level_flex = 4
            elif t <= data[self.flex] < thresholds[i + 1]:
                level_flex = i

        level = level_extend - level_flex
        return level

"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-16 13:46:52
 * @desc [description]
"""


import warnings

import matplotlib.pyplot as plt
import pandas as pd
from mpl_interactions import panhandler, zoom_factory
from mpl_point_clicker import clicker

from postprocessing import extract_data


class EmgCalibration():
    def __init__(self, user, sampling_rate=100):
        self.folder = "C:/Users/mtillerman/OneDrive - Ossur hf/Documents/Scripts/sensory_feedback/emg_files/"
        self.user = user
        self.path = self.folder + self.user + '/'

        self.rest_file = "rest.csv"
        self.flex_file = "flex.csv"
        self.extend_file = "extend.csv"

        self.sampling_rate = sampling_rate
        self.extend = 'BSMB_MUSCLE_EXTEND'
        self.flex = 'BSMB_MUSCLE_FLEX'

    def load_data(self):
        """ Loads the data files for EMG calibration of a user.
        """
        self.rest_data = extract_data(self.path + self.rest_file)
        self.flex_data = extract_data(self.path + self.flex_file)
        self.extend_data = extract_data(self.path + self.extend_file)

    def calculate_rest_activity(self):
        """ Calculate rest activity based on a recording.
        First and last seconds are discarded and at most 10 seconds is taken
        for calculating the average. Values are saved in a file.
        Gives a warning when the data used for calculating the average is less
        than 8 seconds.
        Method based on Tchimino et al. 2022.
        """
        rest_start = sampling_rate
        if len(self.rest_data) < 12 * sampling_rate:
            rest_end = len(self.rest_data) - sampling_rate
        else:
            rest_end = rest_start + 10 * sampling_rate

        selected_data = self.rest_data.iloc[rest_start:rest_end]
        if len(selected_data) < 8 * self.sampling_rate:
            warnings.warn("Total rest contraction recorded is less than 8 \
                seconds. Consider recording again.")

        avg_rest = pd.DataFrame(
            {self.extend: [selected_data[self.extend].mean()],
             self.flex: [selected_data[self.flex].mean()]})
        avg_rest.to_csv(self.path + 'rest_activity.csv', index=False)

    def calculate_MVC(self):
        """ Calculates the maximum voluntary contraction (MVC) for both flexor
        and extensor muscles based on the selected data.

        Each muscle is contracted maximally for 5 s, 3 times with rest in
        between. The mean is taken over these 5 seconds and the average of
        these 3 values is taken as the mvc for each muscle.
        The values are then saved in a file.
        """
        # TODO check whether there are already times saved, display and ask if it needs to be redone
        start_flex, end_flex = self.extract_contraction_times(self.flex_data)
        avg_flex = self.select_data(self.flex_data, start_flex, end_flex)

        start_extend, end_extend = self.extract_contraction_times(
            self.extend_data)
        avg_extend = self.select_data(
            self.extend_data, start_extend, end_extend)

        mvc_flex = avg_flex.mean()
        mvc_extend = avg_extend.mean()
        print(mvc_flex, mvc_extend)

        mvc = pd.DataFrame({self.extend: [mvc_extend[self.extend]],
                            self.flex: [mvc_flex[self.flex]]})
        mvc.to_csv(self.path + 'mvc.csv', index=False)

    def extract_contraction_times(self, data_frame):
        """ Plots data and mark with cursor when contraction starts and ends.
        Saves starting and ending points in a list and sorts these.

        Args:
            data_frame (data frame): data frame of recording

        Returns:
            list: 2 lists of timestamps (int)
        """
        fig, ax = plt.subplots(constrained_layout=True)

        data_frame.plot(
            kind='line', x='timestamp', y=self.extend, color='blue', ax=ax)
        data_frame.plot(
            kind='line', x='timestamp', y=self.flex, color='green', ax=ax)

        zoom_factory(ax)
        panhandler(fig, button=2)
        klicker = clicker(ax, ['start', 'end'], markers=['o', 'o'])
        plt.show()

        start = klicker.get_positions()['start'][:, 0]
        end = klicker.get_positions()['end'][:, 0]

        start.sort()  # order based on timestamp
        end.sort()
        # TODO save these in file
        return start, end

    def select_data(self, data_frame, start, end):
        """ Select data and calculate average based on starting and ending
        contraction times. Save means in a data_frame and give a warning when
        the total recorded time for muscle contraction is short (<10 seconds).

        Args:
            data_frame (data frame): data frame of recording
            start (list of int): list of timestamps, start points
            end (list of int): list of timestamps, endpoints

        Returns:
            data_frame: average of selected muscle contraction
        """
        avg_contraction = pd.DataFrame(columns=[self.extend, self.flex])
        contraction_length = 0
        for i, (x, y) in enumerate(zip(start, end)):
            contraction_data = data_frame[
                (data_frame['timestamp'] >= x) &
                (data_frame['timestamp'] <= y)]

            mean_contraction = contraction_data[
                [self.extend, self.flex]].mean()
            avg_contraction.loc[i] = mean_contraction
            contraction_length += len(contraction_data)

        if contraction_length < 10 * self.sampling_rate:
            warnings.warn("Total muscle contraction recorded is less than 10 \
                seconds. Consider recording again.")

        return avg_contraction

    def visualise_data(self, data_frame):
        """ Visualise recorded data in plot over time.

        Args:
            data_frame (data frame): timestamp, flex, and extend data
        """
        ax = plt.gca()
        data_frame.plot(
            kind='line', x='timestamp', y=self.extend, color='blue', ax=ax)
        data_frame.plot(
            kind='line', x='timestamp', y=self.flex, color='green', ax=ax)
        plt.grid()
        plt.title('EMG activity over time')
        plt.show()


if __name__ == "__main__":
    user = "me"
    sampling_rate = 10

    emg = EmgCalibration(user, sampling_rate)
    emg.load_data()
    emg.calculate_rest_activity()
    print(emg.flex_data.head())
    # emg.visualise_data(emg.flex_data)
    # emg.extract_contraction_times(emg.flex_data)
    emg.calculate_MVC()

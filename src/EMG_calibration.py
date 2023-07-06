"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-16 13:46:52
 * @desc Class and script for calculating the mvc and average rest activity in
 both flexor and extensor muscles. Then saves these values in a file.
"""


import warnings

import matplotlib.pyplot as plt
import pandas as pd
from mpl_interactions import panhandler, zoom_factory
from mpl_point_clicker import clicker

from postprocessing import extract_data


class EmgCalibration():
    def __init__(self, user, date, sampling_rate=100):
        self.folder = 'user_files/'
        self.user = user
        self.date = date
        self.path = f'{self.folder}{self.user}/{self.date}/'

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
        if len(selected_data) < 6 * self.sampling_rate:
            message = 'Total rest contraction recorded is '\
                f'{len(selected_data) / self.sampling_rate} seconds. '\
                'Consider recording again.'
            warnings.warn(message)

        avg_rest = pd.DataFrame(
            {self.extend: [selected_data[self.extend].mean()],
             self.flex: [selected_data[self.flex].mean()]})
        avg_rest.to_csv(f'{self.path}rest_activity.csv', index=False)

    def calculate_MVC(self):
        """ Calculates the maximum voluntary contraction (MVC) for both flexor
        and extensor muscles based on the selected data.

        Each muscle is contracted maximally for 5 s, 3 times with rest in
        between. The mean is taken over these 5 seconds and the average of
        these 3 values is taken as the mvc for each muscle.
        Checks whether there are already saved start/end positions for each
        muscle. If there are saved values, asks whether these are okay.
        Otherwise, new values will be selected.
        The values are then saved in a file.
        """
        try:
            positions_flex = pd.read_csv(
                f'{self.path}mvc_positions_flexion.csv')
            start_flex = positions_flex.start.to_list()
            end_flex = positions_flex.end.to_list()
            self.visualise_data(
                self.flex_data, 'flexion', start_flex, end_flex)
            user_input = input(
                "Are you happy with the start and end positions?\n"
                "Press y when happy."
                "Press any other key when you want to reset the boundaries.\n")
            if user_input != 'y':
                start_flex, end_flex = self.extract_contraction_times(
                    self.flex_data, 'flexion')
        except FileNotFoundError:
            start_flex, end_flex = self.extract_contraction_times(
                self.flex_data, 'flexion')

        try:
            positions_extend = pd.read_csv(
                f'{self.path}mvc_positions_extension.csv')
            start_extend = positions_extend.start.to_list()
            end_extend = positions_extend.end.to_list()
            self.visualise_data(
                self.extend_data, 'extension', start_extend, end_extend)
            user_input = input(
                "Are you happy with the start and end positions?\n"
                "Press y when happy. "
                "Press any other key when you want to reset the boundaries.\n")
            if user_input != 'y':
                start_extend, end_extend = self.extract_contraction_times(
                    self.extend_data, 'extension')
        except FileNotFoundError:
            start_extend, end_extend = self.extract_contraction_times(
                self.extend_data, 'extension')

        avg_flex = self.select_data(self.flex_data, start_flex, end_flex)
        avg_extend = self.select_data(
            self.extend_data, start_extend, end_extend)

        mvc_flex = avg_flex.mean()
        mvc_extend = avg_extend.mean()

        mvc = pd.DataFrame({self.extend: [mvc_extend[self.extend]],
                            self.flex: [mvc_flex[self.flex]]})
        mvc.to_csv(f'{self.path}mvc.csv', index=False)

    def extract_contraction_times(self, data_frame, muscle):
        """ Plots data and mark with cursor when contraction starts and ends.
        Saves starting and ending points in a list and sorts these. Then saves
        the values in a file.

        Args:
            data_frame (data frame): data frame of recording

        Returns:
            list: 2 lists of timestamps (int)
        """
        fig, ax = plt.subplots(constrained_layout=True)

        data_frame.plot(
            kind='line', x='timestamp', y=[self.extend, self.flex], ax=ax)

        plt.title(f'EMG activity over time during {muscle}')

        zoom_factory(ax)
        panhandler(fig, button=2)
        klicker = clicker(ax, ['start', 'end'], markers=['o', 'o'])
        plt.show()

        start = klicker.get_positions()['start'][:, 0]
        end = klicker.get_positions()['end'][:, 0]

        start.sort()  # order based on timestamp
        end.sort()
        positions = pd.DataFrame({"start": start, "end": end})
        positions.to_csv(f'{self.path}mvc_positions_{muscle}.csv', index=False)
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

        if contraction_length < 6 * self.sampling_rate:
            message = 'Total muscle contraction recorded is '\
                f'{contraction_length / self.sampling_rate} seconds. '\
                'Consider recording again.'
            warnings.warn(message)

        return avg_contraction

    def visualise_data(self, data_frame, activity, start_markers=None,
                       end_markers=None):
        """ Visualise recorded data in plot over time.

        Args:
            data_frame (data frame): timestamp, flex, and extend data.
            activity (str): activity name.
            start_markers (list): x coordinates for muscle contraction start.
            end_markers (list): x coordinates for muscle contraction end.
        """
        ax = plt.gca()
        data_frame.plot(
            kind='line', x='timestamp', y=[self.extend, self.flex], ax=ax)

        if start_markers:
            for x_coordinates in start_markers:
                plt.axvline(x_coordinates, color='green')
        if end_markers:
            for x_coordinates in end_markers:
                plt.axvline(x_coordinates, color='red')

        plt.grid()
        plt.title(f'EMG activity over time during {activity}')
        plt.show()


if __name__ == "__main__":
    user = 'me'
    date = '2023_02_24'
    sampling_rate = 10

    emg = EmgCalibration(user, date, sampling_rate)
    emg.load_data()
    # emg.visualise_data(emg.flex_data, 'flexion')
    # emg.visualise_data(emg.extend_data, 'extension')
    # emg.visualise_data(emg.rest_data, 'rest')

    emg.calculate_rest_activity()
    emg.calculate_MVC()

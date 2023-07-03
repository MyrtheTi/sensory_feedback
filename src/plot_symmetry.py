"""
 * @author Myrthe Tilleman
 * @email metill@utu.fi
 * @create date 2023-05-17 11:59:14
 * @desc Class to analyse the results from the treadmill. Loads the parameters,
 calculates the absolute symmetry index, and plots and saves the results under
 /user_files/results/.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tikzplotlib

from utils import read_file, tikzplotlib_fix_ncols


class AnalyseGaitData():
    def __init__(self, user='', date='', prosthetic_side='R'):
        self.user = user
        self.date = date
        self.path = f'user_files/{self.user}/{self.date}/treadmill_data/'
        self.prosthetic_side = prosthetic_side

        self.num_blocks = 4
        self.num_activities = 2
        self.extract_param()

    def extract_param(self):
        """ Extract parameters for the treadmill data from a .csv file.
        """
        param = read_file('src/', 'Treadmill parameters names.csv')

        list_param = list(filter(None, param))  # remove None
        list_param = ['.'.join(parameter) for parameter in list_param]
        self.list_param = [['Parameters'] + list_param]

    def get_symmetry_data(self):
        """ Loads excel files with treadmill data one by one.
        Calculates the asymmetry data.

        Returns:
            DataFrame: absolute symmetry index for each of the recorded files
        """
        dir = os.listdir(self.path)
        folders = [folder for folder in dir if '.pdf' not in folder]
        folders.sort()
        data = pd.DataFrame()

        blocks = list(np.arange(1, self.num_blocks + 1)) * self.num_activities
        blocks.sort()
        activities = ['Ground level walking',
                      'Ascending slope'] * self.num_blocks
        index = pd.MultiIndex.from_arrays([blocks, activities],
                                          names=('Block', 'Activity'))
        symmetry_index = pd.DataFrame({
            'User': [f'{self.user}'] * self.num_blocks * self.num_activities,
            'ASI': [np.nan] * self.num_blocks * self.num_activities},
            index=index)

        for i, folder in zip(index, folders):
            trial = pd.read_csv(self.path + folder + '\\parameters.csv').T
            trial.dropna(inplace=True)
            trial = trial.set_axis(self.list_param, axis=0)
            data[i] = trial
            asi = self.calculate_asymmetry(trial)
            symmetry_index.loc[[i], 'ASI'] = asi
        return symmetry_index

    def calculate_asymmetry(self, data):
        """ Calculates the absolute symmetry index of the input data.
        i indicates the intact side, p the prosthetic side.

        Args:
            data (DataFrame): Contains swing and stance info per leg.

        Returns:
            float: absolute symmetry index score. 0 means perfect symmetry.
        """
        if self.prosthetic_side == 'R':
            p_side = 'R'
            i_side = 'L'
        elif self.prosthetic_side == 'L':
            p_side = 'L'
            i_side = 'R'

        stance_i = data[0].loc[f'Stance phase {i_side} %'].to_numpy()
        swing_i = data[0].loc[f'Swing phase {i_side} %'].to_numpy()
        stance_p = data[0].loc[f'Stance phase {p_side} %'].to_numpy()
        swing_p = data[0].loc[f'Swing phase {p_side} %'].to_numpy()

        i = stance_i / swing_i
        p = stance_p / swing_p
        asi = (i - p) / (0.5 * (i + p)) * 100
        return asi

    def plot_asi(self, data):
        """ Plots the symmetry score of one participant over one session.

        Args:
            data (DataFrame): Contains symmetry scores for each activity
            and block.
        """
        data.unstack()['ASI'].plot.bar(y=[
            'Ground level walking', 'Ascending slope'], rot=45,
            label=['Level ground', 'Inclined'])
        plt.xticks(np.arange(4), labels=[
            'Baseline', 'EMG before SF', 'EMG + SF', 'EMG after SF'])
        plt.ylabel('ASI (%)')
        plt.hlines(10, -1, 4, colors='black', linestyles='dashed',
                   label='Healthy asymmetry')
        plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")

        plt.title('Absolute symmetry index')
        plt.xlabel('')
        plt.grid()

        fig = plt.gcf()
        tikzplotlib_fix_ncols(fig)
        tikzplotlib.save(
            f'user_files/results/{self.user}_{self.date}_ASI.tex')

    def analyse_data(self, users, dates, prosthetic_sides):
        """ Loops through user list to load the data for each user.
        Then analyses the data per session/date. Then plots and saves the
        results.

        Args:
            users (list): List of user IDs as string
            dates (list): List of dates corresponding to user testing sessions.
            prosthetic_sides (list): List of prosthetic sides corresponding to
            the users.
        """
        for user, date, p_side in zip(users, dates, prosthetic_sides):
            self.user = user
            self.date = date
            self.path = f'user_files/{self.user}/{self.date}/treadmill_data/'
            self.prosthetic_side = p_side
            symmetry_data = self.get_symmetry_data()
            self.plot_asi(symmetry_data)


if __name__ == '__main__':
    users = ['U401', 'U412', 'U412', 'U412', 'U747']
    dates = ['2023_04_25', '2023_04_26', '2023_04_27', '2023_04_28',
             '2023_05_03']
    prosthetic_sides = ['R', 'L', 'L', 'L', 'R']
    plot = AnalyseGaitData()
    plot.analyse_data(users, dates, prosthetic_sides)

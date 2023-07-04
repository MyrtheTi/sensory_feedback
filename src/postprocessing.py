"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-02-13 09:01:22
 * @desc Script for processing logged EMG data from a csv.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tikzplotlib

from preprocessing import PreprocessEMG
from utils import tikzplotlib_fix_ncols


def extract_data(filename, verbose=True, comma=False):
    """
    Extracts data and returns a reshaped data frame with each variable type
    in a different column, ordered by timestamp.

    Args:
        filename (data frame): csv file with EMG data recorded using Ossur
        Toolbox.
        verbose (bool, optional): _description_. Defaults to True.
        comma (bool, optional): Whether decimals are denoted after a comma.
        Defaults to False.

    Returns:
        data frame
    """
    if comma:
        dec = ','
    else:
        dec = '.'
    df = pd.read_csv(filename, delimiter=';', decimal=dec, header=0, quoting=3)
    df = df.pivot(columns="variableType", values="numValue", index="timestamp")
    df = df.reset_index(level=0)
    return df


def visualise_data(raw_data, normal_data, data_file,
                   extend='BSMB_MUSCLE_EXTEND', flex='BSMB_MUSCLE_FLEX',
                   all=True):
    """ Plots data in subplots of raw data, normalised data, and difference
    data and vibration levels. Saves data in .tex files.

    Args:
        raw_data (data frame): data frame with raw data
        normal_data (data frame): data frame with normalised data and levels
        data_file (str): name of data file used
        extend (str, optional): column name for extension data.
        Defaults to 'BSMB_MUSCLE_EXTEND'.
        flex (str, optional): column name for flexion data.
        Defaults to 'BSMB_MUSCLE_FLEX'.
        all (boolean, optional): Indicates if all diagrams are plotted or just
        the raw EMG data. Defaults to True.
    """
    if all:
        THRESHOLDS = [-1, -0.65, -0.4, -0.2, -0.1, 0.1, 0.2, 0.4, 0.65, 1]

        text = ['Level -4', 'Level -3', 'Level -2', 'Level -1', 'Level 0',
                'Level 1', 'Level 2', 'Level 3', 'Level 4']
        data_list = [raw_data, normal_data, normal_data]
        y_list = [[extend, flex], [extend, flex],
                  ['difference', 'threshold level']]
        y_label_list = ['Raw EMG data (V)', 'Normalised EMG data',
                        'Normalised extension - flexion']
        label_list = [['Extension muscle', 'Flexion muscle'],
                      ['Extension muscle', 'Flexion muscle'],
                      ['Extension - Flexion', 'Feedback level']]
        name_list = ['raw', 'normal', 'difference_level']
        color_blocks = ['', 'deadzone', 'levels']
        normal_data['difference'] = normal_data[extend] - normal_data[flex]
    else:
        data_list = [raw_data]
        y_list = [[extend, flex]]
        y_label_list = ['Raw EMG data (V)']
        label_list = [['Extension muscle', 'Flexion muscle']]
        color_blocks = ['']
        name_list = ['raw']

    for data, y, y_label, label, color, name in zip(
            data_list, y_list, y_label_list, label_list, color_blocks,
            name_list):
        fig, ax1 = plt.subplots(figsize=(15, 7))

        if color == 'deadzone':
            ax1.axhspan(-0.1, 0.1, facecolor='grey', alpha=0.5)
            ax1.text(normal_data['timestamp'].iloc[1], 0.01, 'Dead zone')
        elif color == 'levels':
            ax1.hlines(THRESHOLDS[1:-1], 0, normal_data['timestamp'].iloc[-1],
                       color='black')
            ax1.set_yticks(THRESHOLDS)
            ax1.set_ylim(-1, 1)
            threshold_middle = []
            for i, t in enumerate(THRESHOLDS[:-1]):  # place text
                middle = np.mean([t, THRESHOLDS[i + 1]])
                threshold_middle.append(middle)
                ax1.text(normal_data['timestamp'].iloc[1],
                         middle - 0.01, text[i])
                if middle < 0:  # flexion - orange
                    ax1.axhspan(t, THRESHOLDS[i + 1], facecolor='orange',
                                alpha=0.2)
                elif middle > 0:  # extension
                    ax1.axhspan(t, THRESHOLDS[i + 1], facecolor='blue',
                                alpha=0.2)
                else:  # co-contraction
                    ax1.axhspan(t, THRESHOLDS[i + 1], facecolor='grey',
                                alpha=0.2)
            threshold_levels = [
                threshold_middle[int(t + 4)] if not np.isnan(t)
                else np.nan for t in normal_data.loc[:, 'LEVEL']]
            normal_data['threshold level'] = threshold_levels

        data.plot(kind='line', x='timestamp', y=y, ax=ax1, label=label)
        ax1.set_ylabel(y_label)
        ax1.set_xlabel('Time (s)')
        ax1.set_xlim(normal_data['timestamp'].iloc[0],
                     normal_data['timestamp'].iloc[-1])
        ax1.legend(loc='upper left')
        plt.grid()

        tikzplotlib_fix_ncols(fig)
        file_name = data_file.split('.')[0] + f'_{name}.tex'
        tikzplotlib.save(f'user_files/results/{file_name}')
        plt.show()


def simulate_online(user, emg_folder, data_folder, data_file,
                    folder='user_files/',
                    extend='BSMB_MUSCLE_EXTEND', flex='BSMB_MUSCLE_FLEX',
                    from_log=True):
    """ Create loop as if the recorded data was coming in through the online
    system. Preprocess EMG and calculate level. Then plots the data.

    Args:
        user (str): user name / number, folder where all user files are saved.
        emg_folder (str): date of the emg calibration.
        data_folder (str): date of the recorded file to analyse.
        data_file (str): name of the recorded file to analyse.
        folder (str): folder where all user files are located. Defaults to
        'user_files/'.
        extend (str): name of column with emg data from extension muscle.
        flex (str): name of column with emg data from flexion muscle.
        from_log (bool): whether the data comes from a log from the panda or
        another Össur device. Defaults to True.
    """
    data_path = f'{folder}{user}/{data_folder}/{data_file}'

    if from_log:
        data = extract_data(data_path)
    else:
        data = pd.read_csv(data_path)

    data['timestamp'] = (data['timestamp'] - data['timestamp'].iloc[0]) / 1000
    raw_data = data[['timestamp', extend, flex]]

    levels = []
    normalised_flex = []
    normalised_extend = []

    process_EMG = PreprocessEMG(user, emg_folder)
    vib_emg = False

    for _, row in data.iterrows():  # loop through data as if live data
        row = row.to_frame().T

        normal = process_EMG.normalise_data_MVC(row.iloc[0])
        normalised_flex.append(normal[flex])
        normalised_extend.append(normal[extend])
        vib_emg = process_EMG.threshold_reached(normal)

        if vib_emg:
            level = process_EMG.define_dominant_muscle(normal)
            levels.append(level)
        else:
            levels.append(None)

    normal_data = pd.DataFrame({
        'timestamp': data['timestamp'], flex: normalised_flex,
        extend: normalised_extend, 'LEVEL': levels})
    return raw_data, normal_data


if __name__ == "__main__":
    user = 'U401'
    data_folder = '2023_03_17'
    emg_calibration = '2023_03_17'
    data_file = 'plantar_flexion.csv'
    from_log = False

    raw, normal = simulate_online(user, emg_calibration, data_folder,
                                  data_file, from_log=from_log)

    visualise_data(raw, normal, data_file, all=True)

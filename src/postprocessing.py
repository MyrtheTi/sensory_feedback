"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-02-13 09:01:22
 * @desc Script for processing logged EMG data from a csv.
"""

import pandas as pd

from preprocessing import PreprocessEMG


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


def simulate_online(user, emg_folder, data_folder, data_file):
    """ Create loop as if the recorded data was coming in through the online
    system. Preprocess EMG and calculate level.

    Args:
        user (str): user name / number, folder where all user files are saved.
        emg_folder (str): date of the emg calibration.
        data_folder (str): date of the recorded file to analyse.
        data_file (str): name of the recorded file to analyse.
    """
    folder = "C:/Users/mtillerman/OneDrive - Ossur hf/Documents/" \
             "Scripts/sensory_feedback/user_files/"
    data_path = folder + f'{user}/{data_folder}/{data_file}'

    columns = [
        'timestamp', 'BSMB_MUSCLE_EXTEND', 'BSMB_MUSCLE_FLEX']
    temp = pd.DataFrame(columns=columns)

    # select columns to process
    data = extract_data(data_path)
    data = data[columns]
    print(data.head())

    process_EMG = PreprocessEMG(user, emg_folder)
    vib_emg = False

    for _, row in data.iterrows():  # loop through data as if live data
        row = row.to_frame().T
        temp = pd.concat([temp, row], ignore_index=True)
        if len(temp) > 100:  # take out first line
            temp.drop(axis=0, index=0, inplace=True)

        normal = process_EMG.normalise_data_MVC(row.iloc[0])
        print(normal)
        # normal = process_EMG.normalise_data_RMS(temp)
        vib_emg = process_EMG.threshold_reached(normal)

        if vib_emg:
            level_l = process_EMG.define_level(normal)
            level_m = process_EMG.define_dominant_muscle(normal)
            if level_l != level_m:
                print(level_l, level_m)


if __name__ == "__main__":
    folder = "C:/Users/mtillerman/OneDrive - Ossur hf/Documents/EMG_data/"
    # data_file = "20230111151536909_210000.8.Variables.csv"
    # data_file = "ramp descend.csv"
    # data_file = "signal check sitting.csv"
    data_file = "stairs prev settings.csv"

    user = "me"
    emg_calibration = '2023_02_24'

    simulate_online(user, emg_calibration, emg_calibration, 'extend.csv')

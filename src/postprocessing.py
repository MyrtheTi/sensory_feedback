"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-02-13 09:01:22
 * @desc [description]
"""

import pandas as pd

from preprocessing import (define_dominant_muscle, define_level,
                           normalise_data_MVC, normalise_data_RMS,
                           threshold_reached)
from utils import get_MVC


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
    print(df)
    df = df.pivot(columns="variableType", values="numValue", index="timestamp")
    df = df.reset_index(level=0)

    return df


if __name__ == "__main__":
    vib_emg = False
    level = None
    columns = [
        'timestamp',
        'BASE_ACTIVITY', 'BASE_GAIT_PHASE',
        'BSMB_MUSCLE_EXTEND', 'BSMB_MUSCLE_FLEX']
    temp = pd.DataFrame(columns=columns)

    folder = "C:/Users/mtillerman/OneDrive - Ossur hf/Documents/EMG_data/"
    # data_file = "20230111151536909_210000.8.Variables.csv"
    # data_file = "ramp descend.csv"
    # data_file = "signal check sitting.csv"
    data_file = "stairs prev settings.csv"
    data = extract_data(folder + data_file)

    # select columns to process
    data = data[columns]
    print(data.head())
    mvc = get_MVC('emg_files/MVC.csv')
    print(mvc)
    for _, row in data.iterrows():  # loop through data as if live data
        row = row.to_frame().T
        temp = pd.concat([temp, row], ignore_index=True)
        if len(temp) > 100:  # take out first line
            temp.drop(axis=0, index=0, inplace=True)

        # TODO subtract 'rest' activity
        normal = normalise_data_MVC(row.iloc[0], mvc)
        print(normal)
        # normal = normalise_data_RMS(temp)
        vib_emg = threshold_reached(normal)

        if vib_emg:
            level_l = define_level(normal)
            level_m = define_dominant_muscle(normal)
            if level_l != level_m:
                print(level_l, level_m)

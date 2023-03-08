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

    calibration_folder = "C:/Users/mtillerman/OneDrive - Ossur hf/Documents/" \
                         "Scripts/sensory_feedback/user_files/"
    user = "me"
    date = '2023_02_24'

    process_EMG = PreprocessEMG(user, date, calibration_folder)

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

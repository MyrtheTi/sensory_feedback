"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-11 10:29:57
 * @desc [description]
"""

import pandas as pd
import numpy as np


def extract_data(filename, verbose=True, comma=False):
    """
    Extracts data and returns a reshaped data frame with each variable type
    in a different column, ordered by timestamp.

    Args:
        filename (data frame): csv file with EMG data recorded using Ossur Toolbox.
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


def normalise_data(data_frame):
    """
    Take the root mean square and normalises data according to 40% of the
    maximum voluntary contraction (MVC).

    Args:
        data_frame (data frame): _description_
    """
    cols = ['BSMB_MUSCLE_EXTEND', 'BSMB_MUSCLE_FLEX']
    MVC = data_frame[cols].abs().max()  # TODO retrieve this from file after EMG calibration

    normalised = pd.DataFrame(data_frame.iloc[100:, 0])  # take the timestamp
    RMS_column = pd.DataFrame(columns=cols)

    for i in range(100, len(data_frame)):  # use the previous 100 points
        RMS_window = data_frame.iloc[i - 100:i, 1:]  # exclude timestamp
        square = RMS_window.pow(2)
        RMS = square.mean(axis=0).pow(0.5) / MVC

        RMS_df = pd.DataFrame(np.expand_dims(RMS.to_numpy(), axis=0),
                              columns=cols, index=[i])
        RMS_column = pd.concat([RMS_column, RMS_df], ignore_index=False)

    normalised = pd.concat([normalised, RMS_column], axis=1)
    return normalised


def define_dominant_muscle(data_frame):
    """
    Defines which muscle is the dominant one, the extensor or the flexor.
    Subtracts extensor EMG from flexor EMG.

    Args:
        data_frame(data frame): preprocessed and normalised EMG data from both
        flexor and extensor

    Returns:
        float    1 - extensor is maximally contracted without flexor
                -1 - flexor is maximally contracted without extensor
                 0 - both flexor and extensor are equally contracted
    """
    dominant_muscle = data_frame['BSMB_MUSCLE_EXTEND'] - data_frame['BSMB_MUSCLE_FLEX']
    return dominant_muscle


if __name__ == "__main__":
    data_file = r"C:\Users\mtillerman\OneDrive - Ossur hf\Documents\Ossur\Ossur Toolbox 1.4 Dev\tmp\20230111151536909_210000.8.Variables.csv"
    data = extract_data(data_file)
    data = data[['timestamp', 'BSMB_MUSCLE_EXTEND', 'BSMB_MUSCLE_FLEX']]
    print(data)
    normal = normalise_data(data)
    print('normal\n', normal)
    dom = define_dominant_muscle(normal)
    print(dom)

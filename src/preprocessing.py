"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-11 10:29:57
 * @desc Process EMG data from file: normalise and define activation level
"""

import pandas as pd

from utils import EXTEND, FLEX, LEVELS, MVC


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


def normalise_data_RMS(data_frame):
    """
    Take the root mean square and normalises data according to 40% of the
    maximum voluntary contraction (MVC).

    Args:
        data_frame (data frame): raw EMG data of 100 previous measurements

    Returns:
        data frame: with 1 row with the normalised EMG data
    """
    normalised = data_frame.iloc[-1]
    RMS_window = data_frame[[EXTEND, FLEX]]

    square = RMS_window.pow(2)
    rms = square.mean(axis=0).pow(0.5) / (0.4 * MVC)

    normalised[EXTEND] = rms[EXTEND]
    normalised[FLEX] = rms[FLEX]
    return normalised


def normalise_data_MVC(data_frame):
    """
    Normalises data according to 40% of the maximum voluntary contraction (MVC)

    Args:
        data_frame (data frame): raw EMG data of 100 previous measurements

    Returns:
        data frame: with 1 row with the normalised EMG data
    """
    normalised = data_frame.reset_index(drop=True)

    for muscle in [EXTEND, FLEX]:
        emg_signal = data_frame[muscle].reset_index(drop=True)
        normalised[muscle] = emg_signal / (0.4 * MVC[muscle])

    return normalised


def threshold_reached(data_frame, vib_emg=False):
    """ Sets vib_emg to True when the EMG threshold is reached, EMG > 0.1.

    Args:
        data_frame (data frame): normalised EMG data
        vib_emg (bool, optional): Sets feedback activation. Defaults to False.

    Returns:
        bool: is True when EMG threshold is reached and feedback should be
        activated.
    """
    if (data_frame[EXTEND] > 0.1) | (data_frame[FLEX] > 0.1):
        vib_emg = True
    return vib_emg


def define_dominant_muscle(data_frame):
    """
    Defines vibrator level based on muscle activation based on the difference
    in activation between the extensor and the flexor.
    Subtracts extensor EMG from flexor EMG.

    Args:
        data_frame(data frame): preprocessed and normalised EMG data from both
        flexor and extensor

    Returns:
        int: level, ranging from -4 to 4, -4 = extensor min & flexor max,
        0 = equal contracted, 4 = extensor max & flexor min
    """
    dominant_muscle = data_frame[EXTEND] - data_frame[FLEX]
    thresholds = [-0.65, -0.4, -0.2, -0.1, 0.1, 0.2, 0.4, 0.65]  # from Tchimino, 2022
    if dominant_muscle <= thresholds[0]:  # smaller than -0.65
        level = LEVELS[0]
    elif dominant_muscle >= thresholds[-1]:  # larger than 0.65
        level = LEVELS[-1]
    else:
        for i, t in enumerate(thresholds[:-1]):
            if t <= dominant_muscle < thresholds[i + 1]:
                level = LEVELS[i + 1]
    # print(dominant_muscle)
    return level


def define_level(data_frame):
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
    # print(data_frame[[EXTEND, FLEX]])
    for i, t in enumerate(thresholds[:-1]):
        if data_frame[EXTEND] >= thresholds[-1]:  # larger than 0.65
            level_extend = 4
        elif t <= data_frame[EXTEND] < thresholds[i + 1]:
            level_extend = i

        if data_frame[FLEX] >= thresholds[-1]:  # larger than 0.65
            level_flex = 4
        elif t <= data_frame[FLEX] < thresholds[i + 1]:
            level_flex = i

    print(data_frame[EXTEND], data_frame[FLEX])
    level = level_extend - level_flex
    return level


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
    data_file = "ramp descend.csv"
    # data_file = "signal check sitting.csv"
    # data_file = "stairs prev settings.csv"
    data = extract_data(folder + data_file)

    # select columns to process
    data = data[columns]
    print(data.head())

    for _, row in data.iterrows():  # loop through data as if live data
        row = row.to_frame().T
        temp = pd.concat([temp, row], ignore_index=True)
        if len(temp) > 100:  # take out first line
            temp.drop(axis=0, index=0, inplace=True)

        # TODO subtract 'rest' activity
        normal = normalise_data_MVC(row)
        print(normal)
        normal = normalise_data_RMS(temp)
        print(normal)
        # vib_emg = threshold_reached(normal)

        if vib_emg:
            level_l = define_level(normal)
            level_m = define_dominant_muscle(normal)
            if level_l != level_m:
                print(level_l, level_m)

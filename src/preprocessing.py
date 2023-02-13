"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-11 10:29:57
 * @desc Process EMG data from file: normalise and define activation level
"""

from utils import LEVELS


def normalise_data_RMS(data_frame, mvc, extend='BSMB_MUSCLE_EXTEND',
                       flex='BSMB_MUSCLE_FLEX'):
    """
    Take the root mean square and normalises data according to 40% of the
    maximum voluntary contraction (MVC).

    Args:
        data_frame (data frame): raw EMG data of 100 previous measurements

    Returns:
        data frame: with 1 row with the normalised EMG data
    """
    normalised = data_frame.iloc[-1]
    RMS_window = data_frame[[extend, flex]]

    square = RMS_window.pow(2)
    rms = square.mean(axis=0).pow(0.5) / (0.4 * mvc)

    normalised[extend] = rms[extend]
    normalised[flex] = rms[flex]
    return normalised


def normalise_data_MVC(data_frame, mvc, extend='BSMB_MUSCLE_EXTEND',
                       flex='BSMB_MUSCLE_FLEX'):
    """
    Normalises data according to 40% of the maximum voluntary contraction (MVC)

    Args:
        data_frame (data frame): raw EMG data of 100 previous measurements

    Returns:
        data frame: with 1 row with the normalised EMG data
    """
    normalised = data_frame

    for muscle in [extend, flex]:
        emg_signal = data_frame[muscle]
        normalised[muscle] = emg_signal / (0.4 * mvc[muscle])

    return normalised


def threshold_reached(data_frame, vib_emg=False, extend='BSMB_MUSCLE_EXTEND',
                      flex='BSMB_MUSCLE_FLEX'):
    """ Sets vib_emg to True when the EMG threshold is reached, EMG > 0.1.

    Args:
        data_frame (data frame): normalised EMG data
        vib_emg (bool, optional): Sets feedback activation. Defaults to False.

    Returns:
        bool: is True when EMG threshold is reached and feedback should be
        activated.
    """
    if (data_frame[extend] > 0.1) | (data_frame[flex] > 0.1):
        vib_emg = True
    return vib_emg


def define_dominant_muscle(data_frame, extend='BSMB_MUSCLE_EXTEND',
                           flex='BSMB_MUSCLE_FLEX'):
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
    dominant_muscle = data_frame[extend] - data_frame[flex]
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


def define_level(data_frame, extend='BSMB_MUSCLE_EXTEND',
                 flex='BSMB_MUSCLE_FLEX'):
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
        if data_frame[extend] >= thresholds[-1]:  # larger than 0.65
            level_extend = 4
        elif t <= data_frame[extend] < thresholds[i + 1]:
            level_extend = i

        if data_frame[flex] >= thresholds[-1]:  # larger than 0.65
            level_flex = 4
        elif t <= data_frame[flex] < thresholds[i + 1]:
            level_flex = i

    level = level_extend - level_flex
    return level

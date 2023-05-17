"""
 * @author Myrthe Tilleman
 * @email metill@utu.fi
 * @create date 2023-05-03 10:16:11
 * @desc [description]
"""

import matplotlib.pyplot as plt
import numpy as np
from postprocessing import simulate_online

THRESHOLDS = [-1, -0.65, -0.4, -0.2, -0.1, 0.1, 0.2, 0.4, 0.65, 1]

text = ['Level -4', 'Level -3', 'Level -2', 'Level -1', 'Level 0',
        'Level 1', 'Level 2', 'Level 3', 'Level 4']

x = 0.4
# y = [ for n, t in enumerate(THRESHOLDS[:-1])]


def plot_levels():
    plt.figure(figsize=[5, 10])
    plt.hlines(THRESHOLDS[1:-1], 0, 1, color='black')
    plt.yticks(THRESHOLDS)

    for i, t in enumerate(THRESHOLDS[:-1]):  # place text
        middle = np.mean([t, THRESHOLDS[i + 1]])
        plt.text(x, middle - 0.01, text[i])
        if middle < 0:  # flexion - orange
            plt.axhspan(t, THRESHOLDS[i + 1], facecolor='orange', alpha=0.5)
        elif middle > 0:  # extension
            plt.axhspan(t, THRESHOLDS[i + 1], facecolor='blue', alpha=0.5)
        else:  # cocontraction
            plt.axhspan(t, THRESHOLDS[i + 1], facecolor='grey', alpha=0.5)

    plt.ylim(-1, 1)
    plt.xlim(0, 1)
    plt.xticks([], [])
    plt.ylabel('Normalised EMG signal: extension - flexion')
    plt.tight_layout()
    plt.show()


def visualise_data(raw_data, normal_data, data_file,
                   extend='BSMB_MUSCLE_EXTEND', flex='BSMB_MUSCLE_FLEX'):
    """ Plots data in subplots of raw data, normalised data, and difference
    data with defined vibration levels.

    Args:
        raw_data (data frame): data frame with raw data
        normal_data (data frame): data frame with normalised data and levels
        data_file (str): name of data file used
        extend (str, optional): column name for extension data.
        Defaults to 'BSMB_MUSCLE_EXTEND'.
        flex (str, optional): column name for flexion data.
        Defaults to 'BSMB_MUSCLE_FLEX'.
    """
    fig, axes = plt.subplots(ncols=3, figsize=(20, 10))
    ax1, ax2, ax3 = axes.flatten()

    raw_data.plot(kind='line', x='timestamp', y=[extend, flex], ax=ax1,
                  label=['Extension muscle', 'Flexion muscle'])
    ax1.set_ylabel('Raw EMG data (V)')
    ax1.set_xlabel('Timestamp (ms)')
    ax1.set_ylim(0, 250)
    ax1.set_xlim(0, len(raw_data))
    ax1.set_title('A. Raw EMG signal')

    print(normal_data.iloc[1:10])
    normal_data.plot(kind='line', x='timestamp', y=[extend, flex], ax=ax2,
                     label=['Extension muscle', 'Flexion muscle'])
    ax2.set_ylabel('Normalised EMG data')
    ax2.axhspan(-0.1, 0.1, facecolor='grey', alpha=0.5)
    ax2.text(10, 0.01, 'Dead zone')
    ax2.set_xlim(0, len(raw_data))
    ax2.set_ylim(0, 2.5)
    ax2.set_title('B. Normalised EMG signal')
    ax2.set_xlabel('Timestamp (ms)')

    normal_data['difference'] = normal_data[extend] - normal_data[flex]
    normal_data.plot(kind='line', x='timestamp', y='difference', ax=ax3,
                     label='Extension - Flexion', color='purple')
    ax3.set_ylabel('Normalised extension - flexion')
    ax3.hlines(THRESHOLDS[1:-1], 0, len(raw_data), color='black')
    ax3.set_yticks(THRESHOLDS)
    ax3.set_ylim(-1, 1)
    ax3.set_title('C. Level discretisation')
    ax3.set_xlabel('Timestamp (ms)')

    ax3.set_xlim(0, len(raw_data))
    ax3.legend(loc='upper left')
    threshold_middle = []
    for i, t in enumerate(THRESHOLDS[:-1]):  # place text
        middle = np.mean([t, THRESHOLDS[i + 1]])
        threshold_middle.append(middle)
        ax3.text(10, middle - 0.01, text[i])
        if middle < 0:  # flexion - orange
            ax3.axhspan(t, THRESHOLDS[i + 1], facecolor='orange', alpha=0.5)
        elif middle > 0:  # extension
            ax3.axhspan(t, THRESHOLDS[i + 1], facecolor='blue', alpha=0.5)
        else:  # cocontraction
            ax3.axhspan(t, THRESHOLDS[i + 1], facecolor='grey', alpha=0.5)

    # print(np.isnan(normal_data['LEVEL']))
    threshold_levels = [threshold_middle[int(t + 4)] if not np.isnan(t) else np.nan for t in normal_data.loc[:, 'LEVEL']]
    normal_data['threshold level'] = threshold_levels

    ax4 = ax3.twinx()
    ax4.set_ylim(-1, 1)
    ax4.set_yticks([], [])
    normal_data.plot(
        kind='line', x='timestamp', y='threshold level', color='red',
        ax=ax4, label='Feedback level')
    # ax4.set_ylabel('Vibration level')
    ax4.legend(loc='upper right')

    plt.grid()
    # plt.suptitle('EMG processing')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # plot_levels()
    user = 'U401'
    # date = '2023_04_25'
    date = '2023_03_17'
    file = 'plantar_flexion.csv'
    # file = '20230425_U401_ground_level_SF_EMG_PA_second_half.csv'
    raw, normal, data_file = simulate_online(user, date, date, file, from_log=False)
    print(len(raw))
    visualise_data(raw.iloc[:800], normal.iloc[:800], data_file)

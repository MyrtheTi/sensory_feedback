"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-03-16 13:16:04
 * @desc Loads a txt file with the output of run.py with raw emg values and
 level information. Then converts this into a csv file that can be read easily
 by pandas.
"""

import pandas as pd
import numpy as np
# from utils import read_file
# first emg is printed, then the corresponding level


def read_file(path, file_name, data_type=[None]):
    """ Opens a file and reads the lines. Then splits the entities by comma.
    If provided, it converts the data to a different type than strings.

    Args:
        path (string): path of the file to read.
        file_name (): name of the file to read.
        data_type (str, optional): Converts to this data type. Defaults to None

    Returns:
        list: list of lists with data of each line from the file
    """
    with open(path + file_name, 'r') as file:
        lines = file.read().splitlines()

    data = []
    level = []
    length = len(lines)
    data_type = data_type * int(length / 2)
    for line, data_type in zip(lines, data_type):
        split_line = line.split(',')

        if data_type == 'int':
            first = split_line[0][1:]
            second = split_line[1][1:-1]
            split_line = [first, second]
            names = [int(t) for t in split_line]
            data.append(names)
        elif data_type == 'float':
            names = [float(t) for t in split_line]
        else:
            names = split_line
            if names[0] == 'False':
                lev = None
            else:
                lev = names[0][6:]
            level.append(lev)
    return data, level


if __name__ == '__main__':
    file_name = 'hold_150ms'
    user = 'me'
    date = '2023_03_23'

    path = f'user_files/{user}/{date}/'
    data, level = read_file(path, f'{file_name}.txt', ['int', None])
    data_array = np.array(data)

    data_frame = pd.DataFrame({
        'BSMB_MUSCLE_FLEX': data_array[:, 0],
        'BSMB_MUSCLE_EXTEND': data_array[:, 1],
        'LEVEL': level, 'timestamp': np.arange(len(level))})
    print(data_frame.head())
    data_frame.to_csv(path + f'{file_name}.csv', index=False)

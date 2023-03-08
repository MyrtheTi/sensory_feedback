"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-03-08 10:37:29
 * @desc Script with general useful functions.
"""


def mean(data):
    """ Calculate the mean of a list.

    Args:
        data (list): data to calculate mean from

    Returns:
        float: mean of data
    """
    avg = sum(data) / len(data)
    return avg


def write_file(path, file_name, data):
    """ Writes data to a file.

    Args:
        path (string): path of file to write data to
        file_name (string): filename of the file to write data to
        data (list): list of data to write in file
    """
    with open(path + file_name, 'w') as file:
        file.write("%s" % ','.join(str(col) for col in data))


def read_file(path, file_name, data_type=None):
    """ Opens a file and reads the lines. Then splits the entities by comma.
    If provided, it converts the data to a different type than strings.

    Args:
        path (string): path of the file to read.
        file_name (): name of the file to read.
        data_type (str, optional): Converts to this data type. Defaults to None

    Returns:
        _type_: _description_
    """
    with open(path + file_name, 'r') as file:
        lines = file.read()

    data = lines.split(',')

    if data_type == 'int':
        names = [int(t) for t in data]
    elif data_type == 'float':
        names = [float(t) for t in data]
    return names

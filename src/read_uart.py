"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-02-12 16:52:16
 * @desc script to read serial uart EMG data from Panda
"""

import struct

import board
import busio

from preprocessing import normalise_data_MVC, define_dominant_muscle


uart = busio.UART(board.TX, board.RX, baudrate=921600)  # 1000000)

num_variables = 2  # EMG_Flex, EMG_Extend
data_num_bytes = 2
start_num_bytes = 8
array_length = 14
raw_data = bytearray(array_length)
all_data = []
if data_num_bytes == 2:
    data_type = 'h'     # 2 byte integer
elif data_num_bytes == 4:
    data_type = 'f'     # 4 byte float

x = 0

extend = 1
flex = 0


while True:
    # emg_data = uart.read(14)  # read up to 32 bytes
    # print(emg_data)  # this is a bytearray type
    uart.readinto(raw_data)
    start_index = raw_data.find(b'\xaa\n\xb1')  # find starting byte
    private_data = raw_data[start_index:]
    # private_data = copy.deepcopy(raw_data[:])
    read_next = uart.read(start_index)  # read extra bytes if necessary
    private_data += bytearray(read_next)  # add extra bytes to make length 14
    # print(raw_data)
    # print(read_next)
    # print(private_data)

    x += 1

    emg_data = [private_data[start_num_bytes + i * data_num_bytes:
                start_num_bytes + data_num_bytes + i * data_num_bytes]
                for i in range(num_variables)]

    # convert bytes to int
    emg_value = [struct.unpack(data_type, data)[0] for data in emg_data]  
    level = define_dominant_muscle(emg_value, extend, flex)
    # print(level)
    all_data.append(emg_value)
    # print(emg_value)

    if x == 500:  # stop
        break

print(all_data)

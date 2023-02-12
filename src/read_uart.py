
import struct
import sys

import board
import busio

uart = busio.UART(board.TX, board.RX, baudrate=921600)  # 1000000)

num_variables = 2  # EMG_Flex, EMG_Extend
data_num_bytes = 2
start_num_bytes = 8
raw_data = bytearray(14)
all_data = []
if data_num_bytes == 2:
    data_type = 'h'     # 2 byte integer
elif data_num_bytes == 4:
    data_type = 'f'     # 4 byte float

for i in range(num_variables):   # give an array for each type of data and store them in a list
    # first flex, then extent emg data
    all_data.append([0])

x = 0

while True:
    # emg_data = uart.read(14)  # read up to 32 bytes
    # print(emg_data)  # this is a bytearray type
    uart.readinto(raw_data)
    start_index = raw_data.find(b'\xaa\n\xb1')
    private_data = raw_data[start_index:]  # should start with \xaa
    # private_data = copy.deepcopy(raw_data[:])

    # print(raw_data)

    # while private_data[0] != 170:  # not the start bit
    #    private_data = private_data[1:]

    # print(private_data)

    if len(private_data) == 14 and private_data[0] == 170:  # correct length and starting bit
    # if private_data.startswith(b'\xaa'):
        x += 1
        for i in range(num_variables):
            # data = private_data[(4 + i * data_num_bytes):(data_num_bytes + 4+i*data_num_bytes)]
            data = private_data[(8 + i * data_num_bytes):
                                (data_num_bytes + 8 + i * data_num_bytes)]

            value,  = struct.unpack(data_type, data)  # unpacks and converts to int (same as int.from_bytes)

            print(value)
            all_data[i].append(value)  # we get the latest data point and append it to our array

        # emg_data = [private_data[start_num_bytes + i * data_num_bytes:
        #             start_num_bytes + data_num_bytes + i * data_num_bytes] for i in range(num_variables)]
        # emg_value = [struct.unpack(data_type, data) for data in emg_data]
        # print(emg_value)
    # if data is not None:
        # if first byte is not AA, check next
        # emg_1 = private_data[8:10]
        # emg_2 = private_data[10:12]

        # int_values = int.from_bytes(emg_1, "little")
        # int_values_2 = int.from_bytes(emg_2, "little")

        # print(int_values, int_values_2)

    if x == 100:  # stop
        break

print(all_data)

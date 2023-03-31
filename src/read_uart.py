"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-02-12 16:52:16
 * @desc script to read serial uart EMG data from Panda
"""
import gc
import struct

import board
import busio

from preprocessing import PreprocessEMG


class ReadUart():
    def __init__(self, array_length=14, baud_rate=921600, data_num_bytes=2,
                 start_num_bytes=8):
        self.num_variables = 2  # EMG_Flex, EMG_Extend
        self.array_length = array_length  # num bytes to read at a time
        self.baud_rate = baud_rate
        self.data_num_bytes = data_num_bytes
        self.start_num_bytes = start_num_bytes  # bytes before EMG data
        self.starting_byte = b'\xaa\n\xb1'

        if self.data_num_bytes == 2:
            self.data_type = 'h'     # 2 byte integer
        elif self.data_num_bytes == 4:
            self.data_type = 'f'     # 4 byte float

    def initialise_uart(self):
        """ Initialise UART port and set baud rate.
        Read up to array_length bytes at a time, or until timeout (s).
        """
        self.uart = busio.UART(board.TX, board.RX, baudrate=self.baud_rate,
                               timeout=0.00001)
        self.raw_data = bytearray(self.array_length)

    def get_serial_data(self):
        """ Reads array_length bytes. Then checks whether the starting byte
        is present and reads additional bytes, so the whole byte array is the
        correct length.

        Returns:
            bytearray: array of bytes starting with the start byte if data is
            available before timeout
        """
        self.uart.readinto(self.raw_data)
        start_index = self.raw_data.find(self.starting_byte)  # find start byte
        private_data = self.raw_data[start_index:]

        if start_index != 0:
            read_next = bytearray()
            self.uart.readinto(read_next)  # read extra bytes
            private_data += read_next  # add extra bytes to the end
        return private_data

    def extract_emg_data(self, private_data):
        """ Extracts the EMG data from the byte array and converts the bytes
        to integers.

        Args:
            private_data (bytearray): byte array of array_length

        Returns:
            list: emg data in ints for flex and extend muscle
        """
        emg = private_data[
            self.start_num_bytes:
            self.start_num_bytes + self.data_num_bytes * self.num_variables]
        emg_data = [emg[:self.data_num_bytes], emg[self.data_num_bytes:]]

        # convert bytes to int
        emg_value = [struct.unpack(self.data_type, data)[0]
                     for data in emg_data]
        return emg_value


if __name__ == '__main__':
    gc.collect()
    start_mem = gc.mem_free()
    print('start memory', start_mem)

    read_uart = ReadUart()
    read_uart.initialise_uart()

    user = "me"
    date = '2023_02_24'
    process_EMG = PreprocessEMG(user, date, extend=1, flex=0)

    x = 0

    gc.collect()
    initialised_mem = gc.mem_free()
    print('initialised memory', initialised_mem)

    while True:
        x += 1
        data = read_uart.get_serial_data()
        emg_value = read_uart.extract_emg_data(data)
        print(emg_value)

        normal = process_EMG.normalise_data_MVC(emg_value)
        level = process_EMG.define_dominant_muscle(normal)
        print(normal)
        print(level)

        if x == 100:  # stop
            break

        gc.collect()
        # loop_mem = gc.mem_free()
        # print('loop memory', x, loop_mem)

    gc.collect()
    end_mem = gc.mem_free()
    print('end memory', end_mem)

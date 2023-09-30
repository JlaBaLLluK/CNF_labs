import pyStuffing


class ByteStuffing:
    flag = chr(int(b'01111110', 2))

    def __init__(self, data='', escape='e'):
        self.data = data
        self.escape = escape

    def stuff(self):
        stuffed_chars = [self.flag, ]
        for char in self.data[1:]:
            if char == self.flag or char == self.escape:
                stuffed_chars.append(self.escape)

            stuffed_chars.append(char)

        stuffed_data = ''.join(stuffed_chars)
        return stuffed_data

    def un_stuff(self, data_from_package):
        un_stuffed_data = ""
        index = 0
        while index < len(data_from_package):
            if data_from_package[index] != self.escape:
                un_stuffed_data += data_from_package[index]
                index += 1
            else:
                un_stuffed_data += data_from_package[index + 1]
                index += 2

        return un_stuffed_data

class Package:
    flag = chr(int(b'01111110', 2))
    max_data_length = 25

    def __init__(self, data, sender_port):
        self.data = data
        self.sender_port = sender_port

    def make_packages(self):
        packages = []
        while len(self.data) > self.max_data_length:
            data_for_package = self.data[0:self.max_data_length]
            crc = crc_calculation(self.data)
            packages.append(f"{self.flag}0{self.sender_port}{data_for_package}{crc}")
            self.data = self.data[self.max_data_length:]

        packages.append(f"{self.flag}0{self.sender_port}{self.data}{crc_calculation(self.data)}")
        return packages


def crc_calculation(data):
    crc = 0
    for byte in data:
        byte = ord(byte)
        for _ in range(0, 8):
            if (crc >> 7) ^ (byte & 0x01):
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF

            byte = byte >> 1

    crc = str(crc)
    while len(crc) < 3:
        crc = '0' + crc

    return crc

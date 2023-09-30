class Package:
    flag = chr(int(b'01111110', 2))
    max_data_length = 25

    def __init__(self, data, sender_port):
        self.data = data
        self.sender_port = sender_port

    def make_packages(self):
        packages = []
        while len(self.data) > self.max_data_length:
            packages.append(f"{self.flag}0{self.sender_port}{self.data[0:self.max_data_length]}0")
            self.data = self.data[self.max_data_length:]

        packages.append(f"{self.flag}0{self.sender_port}{self.data}0")
        return packages

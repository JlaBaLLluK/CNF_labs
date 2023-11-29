import tkinter
from tkinter import messagebox
import serial
import package
import byte_stuffing
import random
import time


class Application:
    window = tkinter.Tk()
    input_data_label = tkinter.Label()
    input_data_entry = tkinter.Entry()
    output_data_label = tkinter.Label()
    output_data_entry = tkinter.Entry()
    send_button = tkinter.Button()
    state_label = tkinter.Label()
    input_packages_text_area = tkinter.Text()
    output_packages_text_area = tkinter.Text()
    input_packages_label = tkinter.Label()
    output_packages_label = tkinter.Label()
    collisions_entry = tkinter.Entry()

    choose_pair_menu = None
    choose_parity_manu = None

    font = 'Arial 14'
    sent_bytes = 0
    parities_dict = {
        'None': serial.PARITY_NONE,
        'Even': serial.PARITY_EVEN,
        'Odd': serial.PARITY_ODD,
        'Mark': serial.PARITY_MARK,
        'Space': serial.PARITY_SPACE,
    }
    port_pairs = [
        'COM3->COM8',
        'COM7->COM4',
    ]

    def __init__(self):
        self.configure_window()
        self.configure_input_widgets()
        self.configure_output_widgets()
        self.configure_send_button()
        self.configure_state_label()
        self.configure_packages_areas()
        self.choose_pair_menu, self.pairs = self.get_port_pair_choose_menu()
        self.choose_parity_menu, self.parities = self.get_parity_choose_menu()
        self.configure_packages_labels()
        self.configure_collisions_entry()
        self.input_data_label.place(x=10, y=10)
        self.input_data_entry.place(x=65, y=10)
        self.output_data_label.place(x=0, y=45)
        self.output_data_entry.place(x=65, y=45)
        self.send_button.place(x=300, y=10)
        self.state_label.place(x=10, y=75)
        self.choose_parity_menu.place(x=350, y=10)
        self.choose_pair_menu.place(x=425, y=10)
        self.input_packages_label.place(x=5, y=150)
        self.output_packages_label.place(x=285, y=150)
        self.input_packages_text_area.place(x=5, y=180)
        self.output_packages_text_area.place(x=285, y=180)
        self.collisions_entry.place(x=5, y=280)

    def configure_window(self):
        self.window.title("COM communication")
        height, width = 320, 550
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(False, False)

    def configure_input_widgets(self):
        self.input_data_label = tkinter.Label(self.window, text='Input', font=self.font)
        self.input_data_entry = tkinter.Entry(self.window, font=self.font)

    def configure_output_widgets(self):
        self.output_data_label = tkinter.Label(self.window, text='Output', font=self.font)
        self.output_data_entry = tkinter.Entry(self.window, font=self.font)
        self.output_data_entry.config(state='readonly')

    def configure_send_button(self):
        self.send_button = tkinter.Button(self.window, text='Send', font='Arial 12',
                                          command=lambda: self.data_send_handling(), width=4)
        self.window.bind('<Return>', lambda event: self.enter_handler(event))

    def configure_packages_areas(self):
        self.input_packages_text_area = tkinter.Text(self.window, font='Arial 11', height=5, width=32)
        self.output_packages_text_area = tkinter.Text(self.window, font='Arial 11', height=5, width=32)
        self.input_packages_text_area.config(state='disabled')
        self.output_packages_text_area.config(state='disabled')

    def configure_packages_labels(self):
        self.input_packages_label = tkinter.Label(self.window, font=self.font, text='Input packages')
        self.output_packages_label = tkinter.Label(self.window, font=self.font, text='Output packages')

    def get_port_pair_choose_menu(self):
        value = tkinter.StringVar(self.window)
        value.set(self.port_pairs[0])
        choose_pair_manu = tkinter.OptionMenu(self.window, value, *self.port_pairs)
        return choose_pair_manu, value

    def configure_state_label(self):
        self.state_label = tkinter.Label(self.window, text='', font=self.font)

    def configure_collisions_entry(self):
        self.collisions_entry = tkinter.Entry(self.window, font=self.font, width=49)
        self.collisions_entry.config(state='readonly')

    def data_send_handling(self):
        inputted_text = self.input_data_entry.get()
        self.input_data_entry.delete(0, tkinter.END)
        data = self.send_using_comport(inputted_text)
        self.output_data_entry.config(state='normal')
        self.output_data_entry.delete(0, tkinter.END)
        self.output_data_entry.insert(0, data)
        self.output_data_entry.config(state='readonly')
        self.sent_bytes += len(data)
        self.state_label.config(text=f'{self.sent_bytes} bytes were sent\nport pair: {self.pairs.get()}')

    def get_parity_choose_menu(self):
        parities = list(self.parities_dict.keys())
        value = tkinter.StringVar(self.window)
        value.set(parities[0])
        choose_parity_menu = tkinter.OptionMenu(self.window, value, *parities)
        return choose_parity_menu, value

    def send_using_comport(self, text):
        parity = self.parities_dict[self.parities.get()]
        ports_pair = self.pairs.get()
        if self.is_busy():
            ports_pair = self.swap_ports(ports_pair)
            messagebox.showinfo("Information", "Selected pair is busy. Ports pair was changed.")

        write_port = serial.Serial(
            port=ports_pair.split('->')[0],
            parity=parity,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
        )
        read_port = serial.Serial(
            port=ports_pair.split('->')[1],
            parity=parity,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
        )

        self.collisions_entry.config(state='normal')
        self.collisions_entry.delete(0, tkinter.END)
        self.collisions_entry.config(state='readonly')
        collisions_amount = 0
        were_collisions = False
        signal = ""
        while self.is_collision():
            collisions_amount += 1
            signal = self.handle_collision(write_port, read_port, collisions_amount)
            were_collisions = True

        packages = self.get_packages(text, ports_pair)
        stuffed_packages = self.stuff_packages(packages)
        write_port.write(str.encode(''.join(stuffed_packages)))

        read_data = str(read_port.read(len(''.join(stuffed_packages))))[2:-1]
        read_packages = self.get_read_packages(read_data)
        whole_message = self.get_whole_message(packages, read_packages)
        self.set_input_output_packages(packages, read_packages)
        write_port.close()
        read_port.close()
        if were_collisions:
            return signal

        return whole_message

    @staticmethod
    def get_packages(text, ports_pair):
        pack = package.Package(
            data=text,
            sender_port=ports_pair.split('->')[0][-1],
            receiver_port=ports_pair.split('->')[1][-1]
        )
        packages = pack.make_packages()
        return packages

    def stuff_packages(self, packages):
        stuffed_packages = []
        for single_package in packages:
            stuff = byte_stuffing.ByteStuffing()
            stuff.data = single_package
            stuffed_package = stuff.stuff()
            if not stuff.is_stuffed:
                stuffed_package = self.make_error(single_package)

            stuffed_packages.append(stuffed_package)

        return stuffed_packages

    @staticmethod
    def make_error(single_package):
        if random.randint(0, 99) % 2 == 0:  # no error
            return single_package

        data = single_package[3:-3]
        num_byte_to_change = random.randint(0, len(data) - 1)
        num_bit_to_change = random.randint(0, 7)
        byte_to_change = data[num_byte_to_change]
        bits = format(ord(byte_to_change), '08b')
        new_bit = '0' if bits[num_bit_to_change] == '1' else '1'
        bits_with_error = bits[:num_bit_to_change] + new_bit + bits[num_bit_to_change + 1:]
        data_with_error = data[:num_byte_to_change] + chr(int(bits_with_error, 2)) + data[num_byte_to_change + 1:]
        return single_package[0:3] + data_with_error + single_package[3 + len(data_with_error):]

    @staticmethod
    def fix_error(written_package, read_package):
        data_with_error = read_package[3:-3]
        true_crc = written_package[-3:]
        for i, char in enumerate(data_with_error):
            bits_of_char = format(ord(char), "08b")
            for j, bit in enumerate(bits_of_char):
                bit = '0' if bit == '1' else '1'
                char = chr(int(bits_of_char[:j] + bit + bits_of_char[j + 1:], 2))
                data = data_with_error[:i] + char + data_with_error[i + 1:]
                if package.crc_calculation(data) == true_crc:
                    return data

        return data_with_error

    @staticmethod
    def get_read_packages(read_data):
        read_packages = []
        package_begin = 0
        stuff = byte_stuffing.ByteStuffing()
        for i, char in enumerate(read_data):
            if char == stuff.flag and read_data[i - 1] != stuff.escape and i != 0:
                read_packages.append(read_data[package_begin:i])
                package_begin = i

        read_packages.append(read_data[package_begin:])
        for i, read_package in enumerate(read_packages):
            crc = package.crc_calculation(read_package[3:-3])
            read_packages[i] = read_package[0:-3] + crc

        return read_packages

    def get_whole_message(self, written_packages, read_packages):
        stuff = byte_stuffing.ByteStuffing()
        whole_message = ''
        for i, read_package in enumerate(read_packages):
            if written_packages[i][-3:] != read_package[-3:]:
                whole_message += self.fix_error(written_packages[i], read_package)
            else:
                whole_message += stuff.un_stuff(read_package[3:-3])

        return whole_message

    def set_input_output_packages(self, un_stuffed_packages, stuffed_packages):
        self.input_packages_text_area.config(state='normal')
        self.output_packages_text_area.config(state='normal')
        self.input_packages_text_area.delete(1.0, tkinter.END)
        self.output_packages_text_area.delete(1.0, tkinter.END)
        un_stuffed_packages = '\n'.join(un_stuffed_packages)
        stuffed_packages = '\n'.join(stuffed_packages)
        self.input_packages_text_area.insert(1.0, un_stuffed_packages)
        self.output_packages_text_area.insert(1.0, stuffed_packages)
        self.input_packages_text_area.config(state='disabled')
        self.output_packages_text_area.config(state='disabled')

    @staticmethod
    def is_busy():
        return random.randint(0, 1)

    def swap_ports(self, selected_pair):
        selected_pair_index = self.port_pairs.index(selected_pair)
        new_pair = self.port_pairs[int(not selected_pair_index)]
        self.pairs.set(new_pair)
        return new_pair

    @staticmethod
    def is_collision():
        return random.randint(0, 3) == 3

    @staticmethod
    def send_jam_signal(sender, receiver):
        signal = "JAM-signal"
        sender.write(str.encode(signal))
        data = receiver.read(len(signal))
        return data

    def handle_collision(self, sender, receiver, collision_number):
        signal = self.send_jam_signal(sender, receiver)
        sleep_time = random.randint(0, 2 ** collision_number - 1)
        self.collisions_entry.config(state='normal')
        self.collisions_entry.insert(tkinter.END, f"collision {collision_number}({sleep_time}s); ")
        self.collisions_entry.config(state='readonly')
        time.sleep(sleep_time)
        return signal

    def enter_handler(self, event):
        self.data_send_handling()

    def start(self):
        self.window.mainloop()

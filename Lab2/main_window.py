import tkinter
import serial
import package
import byte_stuffing


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

    def configure_window(self):
        self.window.title("COM communication")
        height, width = 300, 550
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
                                          command=lambda: self.send_text(), width=4)
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
        pairs = [
            'COM3->COM8',
            'COM7->COM4',
        ]

        value = tkinter.StringVar(self.window)
        value.set(pairs[0])
        choose_pair_manu = tkinter.OptionMenu(self.window, value, *pairs)
        return choose_pair_manu, value

    def configure_state_label(self):
        self.state_label = tkinter.Label(self.window, text='', font=self.font)

    def send_text(self):
        inputted_text = self.input_data_entry.get()
        self.input_data_entry.delete(0, tkinter.END)

        data = self.send_using_comport(inputted_text)

        self.output_data_entry.config(state='normal')
        self.output_data_entry.delete(0, tkinter.END)
        self.output_data_entry.insert(0, data)
        self.output_data_entry.config(state='readonly')
        self.sent_bytes += len(data)
        self.state_label.config(text=f'{self.sent_bytes} bytes were sent\nport pair: {self.pairs.get()}')
        self.choose_pair_menu.destroy()

    def get_parity_choose_menu(self):
        parities = list(self.parities_dict.keys())
        value = tkinter.StringVar(self.window)
        value.set(parities[0])
        choose_parity_menu = tkinter.OptionMenu(self.window, value, *parities)
        return choose_parity_menu, value

    def send_using_comport(self, text):
        parity = self.parities_dict[self.parities.get()]
        ports_pair = self.pairs.get()
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
        packages = self.get_packages(text, ports_pair)
        stuffed_packages = self.stuff_packages(packages)
        write_port.write(str.encode(''.join(stuffed_packages)))
        while not read_port.in_waiting:
            continue

        read_data = str(read_port.read(len(''.join(stuffed_packages))))[2:-1]
        read_packages = self.get_read_packages(read_data)
        whole_message = self.get_whole_message(read_packages)
        self.set_input_output_packages(packages, stuffed_packages)
        write_port.close()
        read_port.close()
        return whole_message

    @staticmethod
    def get_packages(text, ports_pair):
        pack = package.Package(
            data=text,
            sender_port=ports_pair.split('->')[0][-1]
        )
        packages = pack.make_packages()
        return packages

    @staticmethod
    def stuff_packages(packages):
        stuffed_packages = []
        stuff = byte_stuffing.ByteStuffing()
        for single_package in packages:
            stuff.data = single_package
            stuffed_packages.append(stuff.stuff())

        return stuffed_packages

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
        return read_packages

    @staticmethod
    def get_whole_message(read_packages):
        stuff = byte_stuffing.ByteStuffing()
        whole_message = ''
        for read_package in read_packages:
            whole_message += stuff.un_stuff(read_package[3:-1])

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

    def enter_handler(self, event):
        self.send_text()

    def start(self):
        self.window.mainloop()

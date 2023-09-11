import tkinter
import serial

sent_bytes = 0
parities_dict = {
    'None': serial.PARITY_NONE,
    'Even': serial.PARITY_EVEN,
    'Odd': serial.PARITY_ODD,
    'Mark': serial.PARITY_MARK,
    'Space': serial.PARITY_SPACE,
}


def draw_main_window():
    window = configure_window()

    font = 'Arial 14'
    input_data_label, input_data_entry = get_input_widgets(window, font)
    output_data_label, output_data_entry = get_output_widgets(window, font)
    choose_pair_menu, ports_pairs = get_port_pair_choose_menu(window)
    choose_parity_manu, parities = get_parity_choose_menu(window)
    state_label = get_state_label(window, font)
    send_button = get_send_button(window=window, input_data_entry=input_data_entry, output_data_entry=output_data_entry,
                                  ports_pairs=ports_pairs, state_label=state_label, parities=parities,
                                  choose_pair_menu=choose_pair_menu)

    input_data_label.place(x=0, y=150)
    input_data_entry.place(x=50, y=150)
    output_data_label.place(x=310, y=150)
    output_data_entry.place(x=375, y=150)
    send_button.place(x=225, y=147)
    choose_pair_menu.place(x=40, y=10)
    state_label.place(x=300, y=200)
    choose_parity_manu.place(x=400, y=10)

    window.mainloop()


def configure_window():
    window = tkinter.Tk()
    window.title("COM communication")
    height, width = 300, 550
    window.geometry(f"{width}x{height}")
    window.resizable(False, False)
    return window


def get_input_widgets(window, font):
    input_data_label = tkinter.Label(window, text='Input', font=font)
    input_data_entry = tkinter.Entry(window, width=15, font=font)
    return input_data_label, input_data_entry


def get_output_widgets(window, font):
    output_data_label = tkinter.Label(window, text='Output', font=font)
    output_data_entry = tkinter.Entry(window, width=15, font=font)
    output_data_entry.config(state='readonly')
    return output_data_label, output_data_entry


def get_send_button(**kwargs):
    window = kwargs['window']
    send_button = tkinter.Button(window, text='Send', font='Arial 12',
                                 command=lambda: send_text(kwargs['input_data_entry'], kwargs['output_data_entry'],
                                                           kwargs['ports_pairs'].get(),
                                                           kwargs['state_label'], kwargs['parities'].get(),
                                                           kwargs['choose_pair_menu']), width=4)
    window.bind('<Return>',
                lambda event: handler_enter(event, kwargs['input_data_entry'], kwargs['output_data_entry'],
                                            kwargs['ports_pairs'].get(),
                                            kwargs['state_label'], kwargs['parities'].get(),
                                            kwargs['choose_pair_menu']))
    return send_button


def get_port_pair_choose_menu(window):
    pairs = [
        'COM3->COM8',
        'COM7->COM4',
    ]
    value = tkinter.StringVar(window)
    value.set(pairs[0])
    choose_pair_manu = tkinter.OptionMenu(window, value, *pairs)
    return choose_pair_manu, value


def get_parity_choose_menu(window):
    global parities_dict
    parities = list(parities_dict.keys())
    value = tkinter.StringVar(window)
    value.set(parities[0])
    choose_parity_menu = tkinter.OptionMenu(window, value, *parities)
    return choose_parity_menu, value


def get_state_label(window, font):
    state_label = tkinter.Label(window, text='', font=font)
    return state_label


def send_text(input_data_entry, output_data_entry, ports_pair, state_label, parity, choose_pair_manu):
    inputted_text = input_data_entry.get()
    input_data_entry.delete(0, tkinter.END)

    data = send_using_comport(inputted_text, ports_pair, parity)

    output_data_entry.config(state='normal')
    output_data_entry.delete(0, tkinter.END)
    output_data_entry.insert(0, data)
    output_data_entry.config(state='readonly')
    global sent_bytes
    sent_bytes += len(inputted_text)
    state_label.config(text=f'{sent_bytes} bytes where sent\nport pair: {ports_pair}')
    choose_pair_manu.destroy()


def handler_enter(event, input_data_entry, output_data_entry, ports_pair, state_label, parity_pairs, choose_pair_manu):
    send_text(input_data_entry, output_data_entry, ports_pair, state_label, parity_pairs, choose_pair_manu)


def send_using_comport(text, ports_pairs, parity):
    global parities_dict
    parity = parities_dict[parity]

    write_port = serial.Serial(
        port=ports_pairs.split('->')[0],
        parity=parity,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
    )
    read_port = serial.Serial(
        port=ports_pairs.split('->')[1],
        parity=parity,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
    )
    write_port.write(str.encode(text))
    while not read_port.in_waiting:
        continue

    read_data = read_port.read(len(text))
    write_port.close()
    read_port.close()
    return read_data

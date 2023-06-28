from six.moves import tkinter


def attach_scrollbar(frame: tkinter.Frame, text_area: tkinter.Text, row: int):
    scrollbar = tkinter.Scrollbar(frame, command=text_area.yview)
    scrollbar.grid(row=row, column=1, sticky='nsew')
    text_area['yscrollcommand'] = scrollbar.set


class CodeRegion:
    def __init__(self, top) -> None:
        # The frame that will vertically align all widgets
        self.frame = tkinter.Frame(top)
        self.frame.grid(column=1, row=1, padx=10, pady=10)

        # A simple label
        tkinter.Label(self.frame, text="Code Area:").grid(column=0, row=0)

        # Main text area for the code
        self.text_area = tkinter.Text(self.frame, width=40, height=20)
        self.text_area.grid(column=0, row=1)
        attach_scrollbar(self.frame, self.text_area, 1)

        # Button to execute the code
        self.button_execute = tkinter.Button(self.frame, text="Execute", default="normal", command=self.callback_execute)
        self.button_execute.grid(column=0, row=2)

        # A simple label
        tkinter.Label(self.frame, text="Console Log:").grid(column=0, row=3)

        # Console log
        self.console_log = tkinter.Text(self.frame, width=40, height=8)
        self.console_log.grid(column=0, row=4)
        attach_scrollbar(self.frame, self.console_log, 4)


    def callback_execute(self):
        print("Executing command!")



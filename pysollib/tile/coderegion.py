import traceback
import sys

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

        # Represents the Game class
        # Initialized from the app.py
        self.game = None

    def connectGame(self, game):
        self.game = game

    def get_code(self) -> str:
        return self.text_area.get("1.0", tkinter.END)
    
    def reset_console_log(self):
        self.console_log.delete("1.0", tkinter.END)
    
    def add_console_log(self, value: str):
        self.console_log.insert(tkinter.END, value)

    def action_deal_cards(self):
        self.add_console_log("Dealing cards")
        self.game.dealCards()

    def callback_execute(self):
        print("Executing command!")
        self.game.dealCards()
        self.reset_console_log()

        code = self.get_code()

        exec_globals = {
            "deal_cards": self.action_deal_cards,
        }
        
        try:
            exec(code, exec_globals)
        except Exception as e:
            print(e)
            # Find the correct traceback frame for the "exec"
            # and print the error for that line.
            frames = traceback.extract_tb(e.__traceback__)
            for frame in frames:
                print(f"Error at: {frame.filename}:{frame.lineno} {frame.name}")
                if frame.filename == "<string>":
                    self.add_console_log(f"Error at line {frame.lineno}: {str(e)}")

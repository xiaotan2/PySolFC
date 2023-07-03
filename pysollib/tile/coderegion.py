import traceback
import sys
import tempfile
import os

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
        self.text_area = tkinter.Text(self.frame, width=40, height=20, font='TkFixedFont')
        self.text_area.grid(column=0, row=1)
        attach_scrollbar(self.frame, self.text_area, 1)

        # Button group
        self.button_group = tkinter.Frame(self.frame)
        self.button_group.grid(column=0, row=2)

        # Button to execute the code
        self.button_execute = tkinter.Button(self.button_group, text="Execute",
                                             default="normal", command=self.callback_execute)
        self.button_execute.grid(column=0, row=0)

        # Button to restore the state back
        self.button_restore = tkinter.Button(self.button_group, text="Restore",
                                             default="normal", command=self.callback_restore)
        self.button_restore.grid(column=1, row=0)

        # A simple label
        tkinter.Label(self.frame, text="Console Log:").grid(column=0, row=3)

        # Console log
        self.console_log = tkinter.Text(self.frame, width=40, height=8, font='TkFixedFont')
        self.console_log.grid(column=0, row=4)
        attach_scrollbar(self.frame, self.console_log, 4)

        # Represents the Game class
        # Initialized from the app.py
        self.game = None

        # Creates a temporary file that will be used to write the game save into.
        # We will use it to restore the state.
        self.state_directory = tempfile.TemporaryDirectory()
        self.state_directory.__enter__()

    def finalize(self):
        self.state_directory.__exit__()

    def connectGame(self, game):
        self.game = game

    def get_code(self) -> str:
        return self.text_area.get("1.0", tkinter.END)
    
    def reset_console_log(self):
        self.console_log.delete("1.0", tkinter.END)
    
    def add_console_log(self, value: str):
        self.console_log.insert(tkinter.END, value)

    def action_deal_cards(self):
        num_cards = self.game.dealCards()
        self.add_console_log(f"Dealed {num_cards} cards from Stock\n")

    def action_print(self, text: str):
        self.add_console_log(text + "\n")
        print(text)
    
    def action_move_waste_to_fundation(self):
        waste = self.game.s.waste
        to_stack, ncards = waste.canDropCards(self.game.s.foundations)
        if to_stack:
            # each single drop is undo-able (note that this call
            # is before the actual move)
            self.game.finishMove()
            waste.moveMove(ncards, to_stack)
            self.add_console_log(f"Move {ncards} cards from waste to {to_stack}\n")

    def action_move_waste_to_tableau(self):
        waste = self.game.s.waste
        to_stack, ncards = waste.canDropCards(self.game.s.rows)
        if to_stack:
            # each single drop is undo-able (note that this call
            # is before the actual move)
            self.game.finishMove()
            waste.moveMove(ncards, to_stack)
            self.add_console_log(f"Move {ncards} cards from waste to {to_stack}\n")

    def action_move_tableau_to_fundation(self):
        row_stacks = self.game.s.rows
        for s in row_stacks:
            to_stack, ncards = s.canDropCards(self.game.s.foundations)
            if to_stack:
                # each single drop is undo-able (note that this call
                # is before the actual move)
                self.game.finishMove()
                s.moveMove(ncards, to_stack)
                if s.canFlipCard():
                    s.flipMove(animation=True)
                self.add_console_log(f"Move {ncards} cards from {s} to {to_stack}\n")

    def action_move_tableau_to_tableau(self):
        row_stacks = self.game.s.rows
        for s in row_stacks:
            to_stack, ncards = s.canDropCards(self.game.s.rows)
            if to_stack:
                # each single drop is undo-able (note that this call
                # is before the actual move)
                self.game.finishMove()
                s.moveMove(ncards, to_stack)
                if s.canFlipCard():
                    s.flipMove(animation=True)
                self.add_console_log(f"Move {ncards} cards from {s} to {to_stack}\n")

    def callback_restore(self):
        self.game.loadGame(os.path.join(self.state_directory.name, "state.data"), skip_check=True)
        self.reset_console_log()

    def callback_execute(self):
        self.game.saveGame(os.path.join(self.state_directory.name, "state.data"))
        
        print("Executing command!")
        self.reset_console_log()

        code = self.get_code()

        exec_globals = {
            "deal_cards": self.action_deal_cards,
            "print": self.action_print,
            "move_waste_to_fundation" : self.action_move_waste_to_fundation,
            "move_waste_to_tableau" : self.action_move_waste_to_tableau,
            "move_tableau_to_fundation" : self.action_move_tableau_to_fundation,
            "move_tableau_to_tableau" : self.action_move_tableau_to_tableau,
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

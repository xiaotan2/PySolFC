import traceback
import sys
import tempfile
import os

from typing import List, Optional
from enum import Enum
from pysollib.acard import AbstractCard

from six.moves import tkinter


class Suit(Enum):
    ANY = -1
    CLUB = 0
    SPADE = 1
    HEART = 2
    DIAMOND = 3


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

        # A simple step count to prevent infinite loop per player code execution
        self.step_count = 0
        self.step_max = 150 # In average, players makes 45 moves in a single game

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

    def action_print(self, text: any):
        self.add_console_log(str(text) + "\n")
        print(text)

    # function that returns stack or stacks
    def waste(self):
        return self.game.s.waste # single stack (pysollib.stack.WasteStack)

    def foundation(self):
        return self.game.s.foundations # multiple stacks (tuple)

    def tableau(self):
        return self.game.s.rows # multiple stacks (tuple)

    def column(self, index):
        if index < 0 or index > 6:
            raise Exception(f"Index {index} out of range for columns.\n"
                "Tip: valid column index is from 0 to 6")
        return self.game.s.rows[index] # single stack (pysollib.stack.KingAC_RowStack)

    def check_move(self, from_stacks, to_stacks):
        # first convert to_stacks to a tuple list that canDropCards accepts
        if not isinstance(to_stacks, tuple):
            to_stacks = (to_stacks,)

        canMove = False
        # handle from_stacks if it is a tuple list
        if isinstance(from_stacks, tuple):
            for s in from_stacks:
                toStack, ncards = s.canDropCards(to_stacks)
                if toStack:
                    canMove = True
                    break
        # handle from_stacks if it is a single stack
        else:
            toStack, ncards = from_stacks.canDropCards(to_stacks)
            if toStack:
                canMove = True
        return canMove

    def action_move(self, from_stacks, to_stacks):
        # First check if we have reached the maximum steps
        if self.step_count >= self.step_max:
            raise Exception(f"You have made more moves than allowed {self.step_max}\n"
                "Is there an infinite loop in your code?")

        # first convert to_stacks to a tuple list that canDropCards accepts
        if not isinstance(to_stacks, tuple):
            to_stacks = (to_stacks,)

        # handle from_stacks if it is a tuple list
        if isinstance(from_stacks, tuple):
            moved = False
            for s in from_stacks:
                to_stack, ncards = s.canDropCards(to_stacks)
                if to_stack:
                    # each single drop is undo-able (note that this call
                    # is before the actual move)
                    self.game.finishMove()
                    s.moveMove(ncards, to_stack)
                    if s.canFlipCard():
                        s.flipMove(animation=True)
                    self.add_console_log(f"Move {ncards} cards from {s} to {to_stack}\n")
                    moved = True
                    self.step_count += 1
                    break
            # raise an exception if we end up not moving. It forces
            # the player to check before move
            if not moved:
                raise Exception(f"Can't move from {s} to {to_stack}\n")
        # handle from_stacks if it is a single stack
        else:
            to_stack, ncards = from_stacks.canDropCards(to_stacks)
            if to_stack:
                # each single drop is undo-able (note that this call
                # is before the actual move)
                self.game.finishMove()
                from_stacks.moveMove(ncards, to_stack)
                if from_stacks.canFlipCard():
                    from_stacks.flipMove(animation=True)
                self.add_console_log(f"Move {ncards} cards from {from_stacks} to {to_stack}\n")
                self.step_count += 1
            # raise an exception if we end up not moving. It forces
            # the player to check before move
            else:
                raise Exception(f"Can't move from {from_stacks} to {to_stack}\n")

    def action_undo(self):
        self.game.finishMove()
        self.game.undo()
    
    def check_size(self, stack):
        if isinstance(stack, tuple):
            raise Exception("Can't check the size of multiple stacks of cards.\n"
                "Tip: Use waste() or column(index) for check_size()")
        return len(stack.cards)

    def check_face_up_size(self, stack):
        if isinstance(stack, tuple):
            raise Exception("Can't check the size of multiple stacks of cards.\n"
                "Tip: Use waste() or column(index) for check_size()")
        num_face_up = len([c for c in stack.cards if c.face_up])
        return num_face_up

    def check_face_down_size(self, stack):
        num_face_down = self.check_size(stack) - self.check_face_up_size(stack)
        return num_face_down
    
    def check_exists(self, stack: object, rank: int, suit: Suit):
        """
        Returns true if any of the cards in the stack match the criteria.
        """
        
        if isinstance(stack, tuple):
            raise Exception("Can't check the the presence of a card in multiple stacks.\n"
                "Tip: Use waste() or column(index) for check_size()")
        if not isinstance(suit, Suit):
            raise Exception("suit must be one of the following: ANY, SPADE, HEART, DIAMOND, CLUB")
                
        def predicate(card: AbstractCard) -> bool:
            return card.rank == rank and (card.suit == suit.value or suit == Suit.ANY) and card.face_up
        
        return any([predicate(card) for card in stack.cards])
    
    def check_top(self, stack: object, rank: int, suit: Suit):
        """
        Returns true if the top card in the stack matches the criteria.
        """
        
        if isinstance(stack, tuple):
            raise Exception("Can't check the the presence of a card in multiple stacks.\n"
                "Tip: Use waste() or column(index) for check_size()")
        if not isinstance(suit, Suit):
            raise Exception("suit must be one of the following: ANY, SPADE, HEART, DIAMOND, CLUB")
                
        def predicate(card: AbstractCard) -> bool:
            return card.rank == rank and (card.suit == suit.value or suit == Suit.ANY)
        
        return len(stack.cards) > 0 and predicate(stack.cards[-1])

    def callback_restore(self):
        self.game.loadGame(os.path.join(self.state_directory.name, "state.data"), skip_check=True)
        self.reset_console_log()

    def callback_execute(self):
        self.game.saveGame(os.path.join(self.state_directory.name, "state.data"))
        
        print("Executing command!")
        self.reset_console_log()

        code = self.get_code()

        exec_globals = {
            "waste": self.waste,
            "foundation": self.foundation,
            "tableau": self.tableau,
            "column": self.column,
            "deal_cards": self.action_deal_cards,
            "print": self.action_print,
            "check_move": self.check_move,
            "check_size": self.check_size,
            "check_face_up_size": self.check_face_up_size,
            "check_face_down_size": self.check_face_down_size,
            "check_exists": self.check_exists,
            "check_top": self.check_top,
            "move": self.action_move,
            "undo": self.action_undo,
            "ANY": Suit.ANY,
            "SPADE": Suit.SPADE,
            "HEART": Suit.HEART,
            "DIAMOND": Suit.DIAMOND,
            "CLUB": Suit.CLUB,
        }

        # Reset step count every time we execute the code
        step_count = 0
        
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

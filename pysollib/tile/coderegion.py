import traceback
import sys
import tempfile
import os

from typing import List, Optional, Callable
from types import MethodType
from enum import Enum
from pysollib.acard import AbstractCard
from pysollib.pysoltk import MfxMessageDialog

from six.moves import tkinter

class Suit(Enum):
    ANY = -1
    CLUB = 0
    SPADE = 1
    HEART = 2
    DIAMOND = 3

suite_to_letter = [
    "c",
    "s",
    "h",
    "d"
]

def attach_scrollbar(frame: tkinter.Frame, text_area: tkinter.Text, row: int):
    scrollbar = tkinter.Scrollbar(frame, command=text_area.yview)
    scrollbar.grid(row=row, column=1, sticky='nsew')
    text_area['yscrollcommand'] = scrollbar.set


function_tutorials = {
# Format:
# . function name : [function signature, instruction, usage]
    "print" : ["print(object) returns None",
               "Printing the given object on the Console window.",
               "Usage: \n\nprint(\"Hello World\")\nprint(check_size(column(0)))"],
    "waste" : ["waste() returns 1 card stack",
               "Get the stack of cards from Waste area.",
               "Usage: \n\nwaste()\ncheck_size(waste())"],
    "foundation" : ["foundation() returns 4 card stacks",
                    "Get the stacks of cards from all suites in Foundation area.",
                    "Usage: \n\nfoundation()\nmove(waste(), foundation())"],
    "tableau" : ["tableau() returns 7 card stacks",
                 "Get the stacks of cards from all columns in Tableau area",
                 "Usage: \n\ntableau()\nmove(tableau(), tableau())"],
    "column" : ["column(index) returns 1 card stack",
                "Get the stack of cards from a specified column in the Tableau area. The index is from 0 to 6.",
                "Usage: \n\ncolumn(2)\ncheck_size(column(6))"],
    "deal_cards" : ["deal_cards() returns None",
                    "Deal 1 card from the Stock to the Waste.",
                    "Usage: \n\ndeal_cards()"],
    "move" : ["move(source, destination) returns None",
               "Moving 1 card or multiple cards from source to destination, if the move is valid.\n"
               "Both source and destination can be a single card stack like column(index), or multiple card stacks like tableau()\n"
               "When source or destination is multiple card stacks like tableau(), the program automatically finds the first valid move.\n"
               "If the move is invalid, the function throws an exception and the player program stops.",
               "Usage: \n\nmove(waste(), foundation())\nmove(tableau(), column(0))\nmove(tableau(), foundation())"],
    "check_move" : ["check_move(source, destination) returns True or False",
                    "Check if calling move(source, destination) is valid. Returns True if it is valid, otherwise returns False.\n"
                    "Inputs source and destination share the same properties with the inputs for move(source, destination).",
                    "Usage: \n\ncheck_move(waste(), foundation())"],
    "undo" : ["undo() returns None",
              "Undo the last move.",
              "Usage: \n\nundo()"],
    "check_size" : ["check_size(cards) returns size",
                    "Check the total size of given card stack.\nInput cards must be a single card stack column(index).\n"
                    "tableau() and foundation() gets multiple card stacks and are invalid input for cards.",
                    "Usage: \n\ncheck_size(column(2))"],
    "check_face_up_size" : ["check_face_up_size(cards) returns size",
                    "Check the size of face-up cards in a given card stack.\nInput cards must be a single card stack column(index).\n"
                    "tableau() and foundation() gets multiple card stacks and are invalid input for cards.",
                    "Usage: \n\ncheck_face_up_size(column(2))"],
    "check_face_down_size" : ["check_face_down_size(cards) returns size",
                    "Check the size of face-down cards of a given card stack.\nInput cards must be a single card stack column(index).\n"
                    "tableau() and foundation() gets multiple card stacks and are invalid input for cards.",
                    "Usage: \n\ncheck_face_down_size(column(2))"],
    "check_exists" : ["check_exists(cards, rank, suite) returns True or False",
                    "Check if a given card stack contains a specific card. Returns True if exist, otherwise returns False.\n"
                    "tableau() and foundation() gets multiple card stacks and are invalid input for cards.\n"
                    "rank is from 1 to 13. suite is a value from these variables: [ANY, SPADE, HEART, DIAMOND, CLUB].",
                    "Usage: \n\ncheck_exists(column(4), 13, CLUB)\ncheck_exists(column(2), 1, ANY)"],
    "check_top" : ["check_top(cards, rank, suite) returns True or False",
                    "Check if the top card of the given card stack matches a specific card. Returns True if match, otherwise returns False.\n"
                    "tableau() and foundation() gets multiple card stacks and are invalid input for cards.\n"
                    "rank is from 1 to 13. suite is a value from these variables: [ANY, SPADE, HEART, DIAMOND, CLUB].",
                    "Usage: \n\ncheck_top(column(4), 13, CLUB)\ncheck_top(column(2), 1, ANY)"],
}


# Use an ordered list to enforce the order of tutorial buttons
# for the available functions
function_tutorial_list = [
    "print",
    "waste",
    "foundation",
    "tableau",
    "column",
    "deal_cards",
    "move",
    "check_move",
    "undo",
    "check_size",
    "check_face_up_size",
    "check_face_down_size",
    "check_exists",
    "check_top",

]


class CodeRegion:
    def __init__(self, top) -> None:
        self.top = top

        # The frame that will vertically align all widgets
        self.frame = tkinter.Frame(top)
        self.frame.grid(column=1, row=1, padx=10, pady=10)

        # Create a tutorial frame
        self.tutorial = tkinter.Frame(top)
        self.tutorial.grid(column=3, row=1, padx=10, pady=10)
        tkinter.Label(self.tutorial, text="Functions:").grid(column=0, row=0)

        self.tutorial_button_group = tkinter.Frame(self.tutorial)
        self.tutorial_button_group.grid(column=0, row=1)

        self.tutorial_buttons = []
        for index in range(0, len(function_tutorial_list)):
            function_name = function_tutorial_list[index]
            tutorial_info = function_tutorials[function_name]
            self.tutorial_buttons.append(
                tkinter.Button(self.tutorial_button_group,
                    text=tutorial_info[0], default="normal",
                    command=lambda name=function_name: self.callback_tutorial_button(name))
            )
            self.tutorial_buttons[index].grid(column=0, row=index)

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

        self.state_set = set()

    # Calculate a state represented by a single string for the current
    # top cards of all card stacks in the game
    def _get_current_state(self):
        state = ""
        # adding all top cars from tableau()
        tableau = self.tableau()
        for row in tableau:
            if len(row.cards) > 0:
                top = row.cards[-1]
                state += f"{suite_to_letter[top.suit]}{top.rank},"
            else:
                state += "-1,"
        # adding all top cars from foundations()
        foundations = self.foundation()
        for row in foundations:
            if len(row.cards) > 0:
                top = row.cards[-1]
                state += f"{suite_to_letter[top.suit]}{top.rank},"
            else:
                state += "-1,"
        # adding top card from waste()
        if len(self.waste().cards) > 0:
            top = self.waste().cards[-1]
            state += f"{suite_to_letter[top.suit]}{top.rank},"
        else:
            state += "-1,"

        return state

    # Calculate a state represented by a single string for the future
    # top cards of all cards after a move is performed
    def _get_future_state(self, from_stack, ncards, to_stack):
        # get the state of the top after a move is carried out
        def get_future_top_state(stack, from_stack, ncards, to_stack):
            new_top = stack.cards[-1] if len(stack.cards) > 0 else None
            # current top card comes from from_stack
            if stack == from_stack:
                # after moving ncards, from_stack will be empty
                if len(from_stack.cards) <= ncards:
                    new_top = None
                # after moving ncards, there is still card at the from_stack
                else:
                    new_top = from_stack.cards[-(ncards + 1)]
            # current top card comes from to_stack
            elif stack == to_stack:
                new_top = from_stack.cards[-1]

            if new_top is None:
                return "-1,"
            else:
                return f"{suite_to_letter[new_top.suit]}{new_top.rank},"
            

        state = ""
        # adding all top cars from tableau()
        tableau = self.tableau()
        for row in tableau:
            state += get_future_top_state(row, from_stack, ncards, to_stack)
        # adding all top cars from foundations()
        foundations = self.foundation()
        for row in foundations:
            state += get_future_top_state(row, from_stack, ncards, to_stack)
        # adding top card from waste()
        state += get_future_top_state(self.waste(), from_stack, ncards, to_stack)
        return state

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
        print(str(text))

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
                    # check the state after the move, if future state has occured
                    # before, it isn't the best strategy
                    future_state = self._get_future_state(s, ncards, toStack)
                    if future_state in self.state_set:
                        continue
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
                    # check the state after the move, if future state has occured
                    # before, it isn't the best strategy
                    future_state = self._get_future_state(s, ncards, to_stack)
                    print(future_state)
                    if future_state in self.state_set:
                        continue

                    # each single drop is undo-able (note that this call
                    # is before the actual move)
                    self.game.finishMove()
                    self.game.update_moves_by_code(1)
                    s.moveMove(ncards, to_stack)
                    self.game.checkForWin()
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
            else:
                new_state = self._get_current_state()
                if new_state not in self.state_set:
                    self.state_set.add(new_state)
                    print(new_state)
        # handle from_stacks if it is a single stack
        else:
            # note: we don't check state duplication if moving from a single stack
            to_stack, ncards = from_stacks.canDropCards(to_stacks)
            if to_stack:
                # each single drop is undo-able (note that this call
                # is before the actual move)
                self.game.finishMove()
                self.game.update_moves_by_code(1)
                from_stacks.moveMove(ncards, to_stack)
                self.game.checkForWin()
                if from_stacks.canFlipCard():
                    from_stacks.flipMove(animation=True)
                self.add_console_log(f"Move {ncards} cards from {from_stacks} to {to_stack}\n")
                self.step_count += 1

                new_state = self._get_current_state()
                if new_state not in self.state_set:
                    self.state_set.add(new_state)
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

        # convert from 1-based index to 0-based index
        rank -= 1

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

        # convert from 1-based index to 0-based index
        rank -= 1

        def predicate(card: AbstractCard) -> bool:
            return card.rank == rank and (card.suit == suit.value or suit == Suit.ANY)
        
        return len(stack.cards) > 0 and predicate(stack.cards[-1])

    # callback function when tutorial button is invoked
    # tutorial_info has the format [function signature, instruction, usage]
    def callback_tutorial_button(self, name):
        tutorial_info = function_tutorials[name]
        d = MfxMessageDialog(self.top, title=name,
                             text="Function:\n\n" + tutorial_info[0] + "\n\n"
                                + tutorial_info[1] + "\n\n" + tutorial_info[2],
                             justify="left")

    def callback_restore(self):
        self.game.loadGame(os.path.join(self.state_directory.name, "state.data"), skip_check=True)
        self.reset_console_log()

    def callback_execute(self):
        self.game.saveGame(os.path.join(self.state_directory.name, "state.data"))
        
        self.reset_console_log()

        code = self.get_code()

        # A function decorator to check if the game has finished before
        # executing the function.
        def check_for_win_wrapper(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                if self.game.finished:
                    raise Exception("Execution stop, the game has finished!")
                return func(*args, **kwargs)
            return wrapper


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
        
        # Wraps all functions in the exec_globals with the function decorator
        for key, item in exec_globals.items():
            if isinstance(item, MethodType):
                exec_globals[key] = check_for_win_wrapper(item)

        # Reset step count every time we execute the code
        self.step_count = 0
        
        try:
            exec(code, exec_globals)
        except SyntaxError as e:
            self.add_console_log(f"Error at line {e.lineno}: {str(e.msg)}")
        except Exception as e:
            print(e, type(e))

            # Find the correct traceback frame for the "exec"
            # and print the error for that line.
            frames = traceback.extract_tb(e.__traceback__)
            lineno: int = None
            for frame in frames:
                print(f"Error at: {frame.filename}:{frame.lineno} {frame.name}")
                if frame.filename == "<string>":
                    lineno = frame.lineno
            

            if lineno is not None:
                self.add_console_log(f"Error at line {lineno}: {str(e)}")
            else:
                self.add_console_log(str(e))

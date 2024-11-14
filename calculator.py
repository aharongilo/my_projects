import re
import tkinter as tk
from typing import Union

INNER_STATES = {"c": "IDLE", "+": "add", "-": "subtract", "*": "mult", "/": "divide", "=": "result"}
NUMBERS_STRING = "0123456789."


class Calculator:
    """ this class define a calculator: functions and GUI using tkinter module"""

    def __init__(self, screen_name=None, base_name=None, class_name="project calculator"):
        self.calculator_gui = tk.Tk(screenName=screen_name, baseName=base_name, className=class_name)
        self._current_state = 0
        self._display_entry = None
        self._current = None
        # indicate the math operation the user want to do. have few states:
        # "IDLE" - before an operand was inserted
        # "add" - if a plus operand was inserted
        # "subtract" - if a minus operand was inserted
        # "mult" - if a multiplication operand was inserted
        # "divide" - if a deviation operand was inserted
        self._inner_state = "IDLE"

    @staticmethod
    def float_fix(num1: Union[int, float], num2: Union[int, float]) -> float:
        """ python have a problem with float number multiplication. the explanation can be
        found here: https://docs.python.org/3/tutorial/floatingpoint.html
        this function will deal with the problem. it will convert the float numbers to int (remove the decimal point),
        multiply the number, and divide by 10 power the num of digit after decimal point in the original numbers.
        for example: 9.1 * 6
        1. 9.1 will become 91
        2. multiply: 91 * 6
        3. result of 2 will be divide by 10 ** 1
        Args:
            num1(int or float): first number to multiply
            num2(int or float): second number to multiply
        Return:
            float: multiplication result
        """
        a1 = str(num1).index(".") if "." in str(num1) else 0
        a2 = str(num2).index(".") if "." in str(num2) else 0
        b1 = int(str(num1).replace(".", "")) if "." in str(num1) else num1
        b2 = int(str(num2).replace(".", "")) if "." in str(num2) else num2
        return (b1 * b2) / ((10 ** a1) * (10 ** a2))

    def get_display_entry(self) -> tk.Entry:
        """ get function for display entry
        Return:
            tk.Entry: entry of the calculator"""
        return self._display_entry

    def set_display_entry(self, entry: tk.Entry):
        """ set function for display entry
        Args:
            entry(tk.Entry): entry to display calculator current state
        """
        if type(entry) == tk.Entry:
            self._display_entry = entry
        else:
            raise ValueError("entry inserted isn't of tk.inter entry type")

    def get_current(self) -> Union[int, float]:
        """ get function for the current parameter of the instance
        Return:
            int or float: current value in the calculator"""
        return self._current

    def set_current(self, new_value: Union[int, float]):
        """ set function for the current parameter of the instance
        Args:
            new_value(int or float): new value for the current state
         """
        if isinstance(new_value, (int, float)):
            self._current = new_value
        else:
            raise TypeError

    def get_inner_state(self) -> str:
        """ get function for the inner_state parameter of the instance
        Return:
            str: inner status of the calculator
            """
        return self._inner_state

    def set_inner_state(self, new_state: str):
        """ set function for the current parameter of the instance
         Args:
            new_state(str): new state of teh calculator
         """
        if new_state in INNER_STATES.values():
            self._inner_state = new_state
        else:
            assert False, "no such state in the calculator"

    def entry_update(self, c: str = None, action: str = "insert"):
        """ is function will insert the clicked button symbol to the calculator Entry
        Args:
            action(str): "insert" or "delete" from GUI entry
            c(str): character to insert the entry
        """
        entry = self.get_display_entry()
        if entry:
            if action == "insert":
                entry.insert(index="end", string="%s" % c)
            elif action == "delete":
                entry.delete(first=0, last=len(entry.get()))
            else:
                assert False, "no such action exist to entry"
        else:
            print("no display entry was inserted to GUI")

    def keyboard_pressed(self, event):
        """ this function is the reaction for keyboard pressing. with it we could use keyboard in the calculator
        Args:
            event(keyboard_pressed event): the event of keyboard pressing
        """
        key = event.char
        if key in NUMBERS_STRING:
            self.number_handler(num=key)
        elif key == "c":
            self.clear_handler(op=key)
        elif key == "-" and self.get_inner_state() == "IDLE":  # inserting negative number at the start
            self.entry_update(key)
        elif key in INNER_STATES.keys():
            self.math_operation_handler(op=key)
        elif (key == '\r') or (key == '='):  # Enter button could also show the result
            self.math_operation_handler(op='=')
        else:
            print("%s button is not part of the calculator" % key)

    def clear_handler(self, op: str):
        """ this function will handle the clear button in the calculator. this function will also be activated if
        the "=" button was pressed, and after that a number button was pressed.
        Args:
            op(str): operation of button ("c")
        """
        self.entry_update(action="delete")
        self.set_inner_state(INNER_STATES[op])

    def number_handler(self, num: str):
        """ this function handle the number buttons and dot button
        Args:
            num(str): inserted num according to the clicked button in the GUI
        """
        if self.get_inner_state() == "result":
            # the last pressed button is "=", we will want to clear the entry and display the new pucked digit
            self.clear_handler(op="c")
        self.entry_update(c=num)

    def math_operation_handler(self, op: str):
        """ this function handle the math operation chosen by the user
        Args:
            op(str): chosen operation according to the clicked button in the GUI
        """
        display = self.get_display_entry().get()
        # if (self.get_inner_state() != "IDLE") and (self.get_inner_state() != "result"):
        if self.get_inner_state() not in ["IDLE", "result"]:
            display = re.split('\+|-|\*|/', display)[-1]
        try:
            entry_value = int(display)
        except ValueError:
            try:
                entry_value = float(display)
            except ValueError as e:
                raise e.__str__("incorrect number inserted")
        finally:
            if self.get_inner_state() == "IDLE":
                # if it's the first operation chosen
                self.set_current(entry_value)
            else:
                # if it's not the first operation chosen
                # calculate and update current state
                self.calculate_result(entry_value)
                # delete entry content and insert new current and last operation (if it's not =)
                self.entry_update(action="delete")
                self.entry_update(c=str(self.get_current()))
            if op != "=":
                self.entry_update(c=op)
            self.set_inner_state(INNER_STATES[op])

    def calculate_result(self, num: Union[int, float]):
        """ this function will calculate the result and update current state. it's activated in to ways:
        1. the user enter the "=" button
        2. the user choose another operand when the inner state isn't IDLE (another operand already chosen but the
           corresponding math operation hasn't been activated yet
        Args:
            num(int or float): the number displayed in the GUI entry
           """
        if self.get_inner_state() == "add":
            self.set_current(self.get_current() + num if type(self.get_current()) == type(num) else float(
                self.get_current()) + float(num))
        elif self.get_inner_state() == "subtract":
            self.set_current(self.get_current() - num if type(self.get_current()) == type(num) else float(
                self.get_current()) - float(num))
        elif self.get_inner_state() == "mult":
            self.set_current(Calculator.float_fix(self.get_current(), num))
        elif self.get_inner_state() == "divide":
            self.set_current(self.get_current() / num if type(self.get_current()) == type(num) else float(
                self.get_current()) / float(num))


def main():
    """ main """
    ##########
    # GUI
    ##########
    calc_window = Calculator()
    top_label = tk.Label(calc_window.calculator_gui, text="my python calculator")
    top_label.pack(side="top")
    equations_entry = tk.Entry(calc_window.calculator_gui, width=24)
    equations_entry.pack(side="top")
    calc_window.set_display_entry(entry=equations_entry)
    top_buttons_row = tk.Frame(calc_window.calculator_gui)
    top_buttons_row.pack(side="top")
    first_row_num = tk.Frame(calc_window.calculator_gui)
    first_row_num.pack(side="top")
    second_row_num = tk.Frame(calc_window.calculator_gui)
    second_row_num.pack(side="top")
    fourth_row_num = tk.Frame(calc_window.calculator_gui)
    fourth_row_num.pack(side="bottom")
    third_row_num = tk.Frame(calc_window.calculator_gui)
    third_row_num.pack(side="bottom")

    # numbers buttons
    button0 = tk.Button(fourth_row_num, text="0", command=lambda: calc_window.number_handler(num="0"),
                        fg="BLUE", width=17, height=2)
    button1 = tk.Button(first_row_num, text="1", command=lambda: calc_window.number_handler(num="1"),
                        fg="BLUE", width=8, height=2)
    button2 = tk.Button(first_row_num, text="2", command=lambda: calc_window.number_handler(num="2"),
                        fg="BLUE", width=8, height=2)
    button3 = tk.Button(first_row_num, text="3", command=lambda: calc_window.number_handler(num="3"),
                        fg="BLUE", width=8, height=2)
    button4 = tk.Button(second_row_num, text="4", command=lambda: calc_window.number_handler(num="4"),
                        fg="BLUE", width=8, height=2)
    button5 = tk.Button(second_row_num, text="5", command=lambda: calc_window.number_handler(num="5"),
                        fg="BLUE", width=8, height=2)
    button6 = tk.Button(second_row_num, text="6", command=lambda: calc_window.number_handler(num="6"),
                        fg="BLUE", width=8, height=2)
    button7 = tk.Button(third_row_num, text="7", command=lambda: calc_window.number_handler(num="7"),
                        fg="BLUE", width=8, height=2)
    button8 = tk.Button(third_row_num, text="8", command=lambda: calc_window.number_handler(num="8"),
                        fg="BLUE", width=8, height=2)
    button9 = tk.Button(third_row_num, text="9", command=lambda: calc_window.number_handler(num="9"),
                        fg="BLUE", width=8, height=2)
    dot_button = tk.Button(fourth_row_num, text=".", command=lambda: calc_window.number_handler(num="."), fg="BLUE",
                           width=8, height=2)
    # math operations buttons
    plus_button = tk.Button(fourth_row_num, text="+",
                            command=lambda: calc_window.math_operation_handler(op="+"), fg="BLUE", width=8,
                            height=2)
    minus_button = tk.Button(third_row_num, text="-",
                             command=lambda: calc_window.math_operation_handler(op="-"), fg="BLUE", width=8,
                             height=2)
    mult_button = tk.Button(second_row_num, text="*",
                            command=lambda: calc_window.math_operation_handler(op="*"), fg="BLUE", width=8,
                            height=2)
    deviate_button = tk.Button(first_row_num, text="/",
                               command=lambda: calc_window.math_operation_handler(op="/"), fg="BLUE", width=8,
                               height=2)
    result_button = tk.Button(top_buttons_row, text="=", command=lambda: calc_window.math_operation_handler(op="="),
                              fg="BLUE", width=8, height=2)
    clear_button = tk.Button(top_buttons_row, text="C", command=lambda: calc_window.clear_handler(op="c"), fg="BLUE",
                             width=8, height=2)

    # packing the buttons in the window
    button0.pack(side="left")
    dot_button.pack(side="left")
    plus_button.pack(side="right")
    deviate_button.pack(side="right")
    minus_button.pack(side="right")
    mult_button.pack(side="right")
    button1.pack(side="left")
    button2.pack(side="left")
    button3.pack(side="right")
    button4.pack(side="left")
    button5.pack(side="left")
    button6.pack(side="right")
    button7.pack(side="left")
    button8.pack(side="left")
    button9.pack(side="right")
    result_button.pack(side="right")
    clear_button.pack(side="left")
    # connect keyboard buttons to the calculator
    calc_window.calculator_gui.bind(sequence='<Key>', func=calc_window.keyboard_pressed)

    calc_window.calculator_gui.mainloop()


if __name__ == "__main__":
    main()

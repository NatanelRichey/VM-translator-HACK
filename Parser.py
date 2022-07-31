"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        input_lines_raw = input_file.read().splitlines()
        input_lines_ntab = []
        input_lines_ncmt = []
        self.input_lines = []
        self.counter = 1

        for word in input_lines_raw:
            input_lines_ntab.append(word.strip(' \t'))

        for word in input_lines_ntab:
            input_lines_ncmt.append(word.split('//')[0])

        while '' in input_lines_ncmt:
            input_lines_ncmt.remove('')

        for word in input_lines_ncmt:
            self.input_lines.append(word.strip())

        if self.input_lines:
            self.cur_command = self.input_lines[0]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        while self.counter != len(self.input_lines) + 1:
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if Parser.has_more_commands(self):
            self.cur_command = self.input_lines[self.counter]
            self.counter += 1


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        command_dict = {"push":"C_PUSH","pop":"C_POP","label":"C_LABEL","goto":"C_GOTO","if":"C_IF",
                        "function":"C_FUNCTION","return":"C_RETURN","call":"C_CALL"}

        command_key = self.find_command_key()
        if command_key not in command_dict.keys():
            return "C_ARITHMETIC"
        return command_dict[command_key]

    def find_command_key(self):
        if '-' in self.cur_command.split(' ')[0]:
            command_key = self.cur_command.split('-')[0]
        else:
            command_key = self.cur_command.split(' ')[0]
        return command_key

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == "C_ARITHMETIC":
            return self.cur_command
        return self.cur_command.split(' ')[1]


    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.cur_command.split(' ')[2])


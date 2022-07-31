"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Opens the output file and gets ready to write into it

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_lines = []
        self.file_name = ""
        self.rtn_function_name = "null"
        self.call_count = 0
        self.code_line = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.file_name = filename

    def set_rtn_label(self, function_name):
        self.rtn_function_name = function_name
        self.call_count = 0


    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        if command == "add":
            self.output_lines.append("\n" + "// add: adds top two stack values")
            self.add_pointer_address_cmds()
            self.output_lines.append("D=M   // pops *SP to D")
            self.add_pointer_address_cmds()
            self.output_lines.append("M=D+M   // pops D+*SP to D")
            self.add_spfwd_cmds()
            self.code_line += 10

        elif command == "sub":
            self.output_lines.append("\n" + "// sub: subtracts top two stack values")
            self.add_pointer_address_cmds()
            self.output_lines.append("D=-M   // pops -*SP to D")
            self.add_pointer_address_cmds()
            self.output_lines.append("M=D+M   // pops D+*SP to D")
            self.add_spfwd_cmds()
            self.code_line += 10

        elif command == "neg":
            self.output_lines.append("\n" + "// negates SP value:")
            self.add_pointer_address_cmds()
            self.output_lines.append("M=-M   // pops -*SP to D")
            # self.add_pushd_cmds()
            self.add_spfwd_cmds()
            self.code_line += 6

        elif command == "eq":
            self.output_lines.append("\n" + "// eq: checks if top two stack values are equal")
            self.add_relative_equal_cmds()
            self.output_lines.append("// check if x != y")
            self.output_lines.append('@' + str(self.code_line + 5))
            self.output_lines.append("D;JNE")
            self.output_lines.append("// when x == y")
            self.output_lines.append("D=-1")
            self.code_line += 3
            self.output_lines.append('@' + str(self.code_line + 3) + "   // if x == y")
            self.output_lines.append("0;JMP")
            self.output_lines.append("// when x != y")
            self.output_lines.append("D=0")
            self.add_pushd_cmds()
            self.add_spfwd_cmds()
            self.code_line += 8

        elif command == "gt":
            self.output_lines.append("\n" + "// gt: checks if SP-1 > SP")
            self.add_relative_value_cmds(a=15, b=6) #+24
            self.output_lines.append('@' + str(self.code_line + 5) + "   // if x <= y")
            self.output_lines.append("D;JGT")
            self.output_lines.append("D=0")
            self.code_line += 3
            self.output_lines.append('@' + str(self.code_line + 3) + "   // if x > y")
            self.output_lines.append("0;JMP")
            self.output_lines.append("D=-1")
            self.add_pushd_cmds()
            self.add_spfwd_cmds()
            self.code_line += 8

        elif command == "lt":
            self.output_lines.append("\n" + "// lt: checks if SP-1 < SP")
            self.add_relative_value_cmds(a=12, b=9)
            self.output_lines.append('@' + str(self.code_line + 5) + "   // if x <= y")
            self.output_lines.append("D;JLT")
            self.output_lines.append("D=0")
            self.code_line += 3
            self.output_lines.append('@' + str(self.code_line + 3) + "   // if x > y")
            self.output_lines.append("0;JMP")
            self.output_lines.append("D=-1")
            self.add_pushd_cmds()
            self.add_spfwd_cmds()
            self.code_line += 8

        elif command == "and":
            self.output_lines.append("\n" + "// and: bitwise and on top two stack values")
            self.add_pointer_address_cmds()
            self.output_lines.append("D=M   // pops *SP to D")
            self.add_pointer_address_cmds()
            self.output_lines.append("D=D&M   // pops D&*SP to D")
            self.add_pushd_cmds()
            self.add_spfwd_cmds()
            self.code_line += 13

        elif command == "or":
            self.output_lines.append("\n" + "// or: bitwise or on top two stack values")
            self.add_pointer_address_cmds()
            self.output_lines.append("D=M   // pops *SP to D")
            self.add_pointer_address_cmds()
            self.output_lines.append("D=D|M   // pops D|*SP to D")
            self.add_pushd_cmds()
            self.add_spfwd_cmds()
            self.code_line += 13

        elif command == "not":
            self.output_lines.append("\n" + "// and: bitwise not on top stack value")
            self.add_pointer_address_cmds()
            self.output_lines.append("D=!M   // pops !*SP to D")
            self.add_pushd_cmds()
            self.add_spfwd_cmds()
            self.code_line += 9

    def add_relative_value_cmds(self, a,b):
        self.add_pointer_address_cmds()
        self.output_lines.append("D=M   // pops *SP to D")
        self.output_lines.append("@y")
        self.output_lines.append("M=D")
        self.add_pointer_address_cmds()
        self.output_lines.append("D=M   // pops *SP to D")
        self.output_lines.append("@x")
        self.output_lines.append("M=D")
        self.output_lines.append("// jumps if x is negative")
        self.code_line += 12
        self.output_lines.append('@' + str(self.code_line + 8))
        self.output_lines.append("D;JLT")
        self.output_lines.append("// when x is positive")
        self.output_lines.append("@y")
        self.output_lines.append("D=M")
        self.code_line += 4
        self.output_lines.append("// jumps to false if y is negative because x is positive")
        self.output_lines.append('@' + str(self.code_line + a))
        self.output_lines.append("D;JLT")
        self.code_line += 2
        self.output_lines.append("// jump to x is positive and y is positive")
        self.output_lines.append('@' + str(self.code_line + 6))
        self.output_lines.append("0;JMP")
        self.output_lines.append("// jumps to true because y is positive and x is negative")
        self.output_lines.append("@y")
        self.output_lines.append("D=M")
        self.code_line += 4
        self.output_lines.append('@' + str(self.code_line + b))
        self.output_lines.append("D;JGE")
        self.output_lines.append("// when both are positive or negative")
        self.output_lines.append("@x")
        self.output_lines.append("D=M-D   // D=x-y")
        self.code_line += 4

    def add_relative_equal_cmds(self):
        self.add_pointer_address_cmds()
        self.output_lines.append("D=M   // pops *SP to D")
        self.add_pointer_address_cmds()
        self.output_lines.append("D=D-M   // pops D-*SP to D")
        self.add_pushd_cmds()
        self.code_line += 11

    def add_pointer_address_cmds(self):
        self.output_lines.append("@SP")
        self.output_lines.append("M=M-1")
        self.output_lines.append("A=M   // *SP")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """

        seg_dict = {"local":"LCL","argument":"ARG","this":"THIS","that":"THAT","temp":'R5',"pointer":'R3'}
        if command == "push":
            if segment == "constant":
                self.output_lines.append("\n" + "// push constant " + str(index))
                self.add_store_index_cmds(index) #+2
                self.add_pushd_cmds()
                self.add_spfwd_cmds()
                self.code_line += 7

            elif segment == "local" or segment == "argument" or segment == "this" or segment == "that":
                self.output_lines.append("\n" + "// push " + segment + ' ' + str(index))
                self.add_store_index_cmds(index)
                self.add_store_seg_value_cmds(seg_dict, segment) #+2
                self.add_store_segval_push_cmds() #+2
                self.add_pushd_cmds()
                self.add_spfwd_cmds()
                self.code_line += 11

            elif segment == "temp" or segment == "pointer":
                self.output_lines.append("\n" + "// push " + segment + ' ' + str(index))
                self.add_store_index_cmds(index)
                self.add_store_tmpseg_value_cmds(seg_dict, segment)
                self.add_store_segval_push_cmds()
                self.add_pushd_cmds()
                self.add_spfwd_cmds()
                self.code_line += 11

            elif segment == "static":
                self.output_lines.append("\n" + "// push " + segment + ' ' + str(index))
                self.output_lines.append('@' + self.file_name + '.' + str(index))
                self.output_lines.append("D=M")
                self.add_pushd_cmds()
                self.add_spfwd_cmds()
                self.code_line += 7

        elif command == "pop":
            if segment == "local" or segment == "argument" or segment == "this" or segment == "that":
                self.output_lines.append("\n" + "// pop " + segment + ' ' + str(index))
                self.add_store_index_cmds(index)
                self.add_store_seg_value_cmds(seg_dict, segment)
                self.output_lines.append("@addr")
                self.output_lines.append("M=D   // creates addr and assigns address")
                self.add_pointer_address_cmds()
                self.add_sp_to_addr_cmds()
                self.code_line += 13


            elif segment == "temp" or segment == "pointer":
                self.output_lines.append("\n" + "// pop " + segment + ' ' + str(index))
                self.add_store_index_cmds(index)
                self.add_store_tmpseg_value_cmds(seg_dict, segment)
                self.output_lines.append("@addr")
                self.output_lines.append("M=D   // creates addr and assigns address")
                self.add_pointer_address_cmds()
                self.add_sp_to_addr_cmds()
                self.code_line += 13

            elif segment == "static":
                self.output_lines.append("\n" + "// pop " + segment + ' ' + str(index))
                self.output_lines.append('@' + self.file_name + '.' + str(index))
                self.output_lines.append("M=A   // stores address as value")
                self.output_lines.append("@SP")
                self.output_lines.append("M=M-1")
                self.output_lines.append("A=M   // *SP")
                self.output_lines.append("D=M")
                self.output_lines.append('@' + self.file_name + '.' + str(index))
                self.output_lines.append("A=M")
                self.output_lines.append("M=D   // *SP = *addr")
                self.code_line += 9

    def add_store_segval_push_cmds(self):
        self.output_lines.append("A=D")
        self.output_lines.append("D=M")

    def add_sp_to_addr_cmds(self):
        self.output_lines.append("D=M")
        self.output_lines.append("@addr")
        self.output_lines.append("A=M")
        self.output_lines.append("M=D   // *SP = *addr")

    def add_store_seg_value_cmds(self, seg_dict, segment):
        self.output_lines.append('@' + seg_dict[segment])
        self.output_lines.append("D=M+D   // stores *seg+i in D")

    def add_store_tmpseg_value_cmds(self, seg_dict, segment):
        self.output_lines.append('@' + seg_dict[segment])
        self.output_lines.append("D=A+D   // stores *seg+i in D")

    def add_store_index_cmds(self, index):
        self.output_lines.append('@' + str(index))
        self.output_lines.append("D=A   // stores constant in D register")

    def add_spfwd_cmds(self):
        self.output_lines.append("@SP")
        self.output_lines.append("M=M+1   // moves stack pointer forward")

    def add_pushd_cmds(self):
        self.output_lines.append("@SP")
        self.output_lines.append("A=M")
        self.output_lines.append("M=D   // pushes D into stack")

    def write_init(self) -> None:
        """Writes the assembly instructions that effects the bootstrap code that initializes the VM.
         This code must be placed at the beginning of the generated *.asm file."""

        self.output_lines.append("// init code starts here:")
        # implement the call sys.init code here:
        self.output_lines.append("// sets SP to 256:")
        self.output_lines.append("@256")
        self.output_lines.append("D=A")
        self.output_lines.append("@SP")
        self.output_lines.append("M=D")  # SP = 256
        self.write_call(function_name="Sys.init", n_args=0)
        self.code_line += 4


    def write_label(self, label: str) -> None:
        """Writes assembly code that effects the "label" command.

        Args:
            label (str): the label to jump to when specified.
        """

        self.output_lines.append("\n\n" + "// label code starts here:")
        self.output_lines.append('(' + self.rtn_function_name + '$' + label + ')')

    def write_goto(self, label: str) -> None:
        """Writes assembly code that effects the "goto" command.

        Args:
            label (str): the label to jump to when specified.
        """

        self.output_lines.append("\n\n" + "// goto code starts here:")
        self.output_lines.append('@' + self.rtn_function_name + '$' + label)
        self.output_lines.append("0;JMP")
        self.code_line += 2

    def write_if(self, label: str) -> None:
        """Writes assembly code that effects the "if-goto" command.

        Args:
            label (str): the label to jump to when specified.
        """

        self.output_lines.append("\n\n" + "// if-goto code starts here:")
        self.output_lines.append("\n" + "// pops top of stack to D:")
        self.add_pointer_address_cmds()
        self.output_lines.append("D=M")
        self.output_lines.append("\n" + "// jump if D!=0:")
        self.output_lines.append('@' + self.rtn_function_name + '$' + label)
        self.output_lines.append("D;JNE")
        self.code_line += 6

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that effects the "function" command.

        Args:
            function_name (str): name of function called.
            n_vars (int): number of variables to assign.
        """

        self.output_lines.append("\n\n" + "// " + function_name + " code starts here: ////////////////////////////////"
                                                                  "//////////////////")
        self.set_rtn_label(function_name)
        # resets call count
        self.output_lines.append('(' + function_name + ')')
        # adds function label
        self.output_lines.append("\n" + "// pushes " + function_name + " local vars to stack:")
        for index in range(n_vars):
            self.add_store_index_cmds(index)
            self.output_lines.append("@LCL")
            self.output_lines.append("A=D+M")
            self.output_lines.append("M=0")
            self.add_spfwd_cmds()
            self.code_line += 7
        # Loads LCL with 0, n_vars times

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that effects the "call" command.

        Args:
            function_name (str): name of function called.
            n_args (int): number of variables to assign.
        """
        self.output_lines.append("\n\n" + "//call to "+ function_name + " code starts here:")
        # prints comment
        self.call_count += 1
        # increases call count
        self.output_lines.append("\n" + "// pushes return address to stack:")
        self.add_push_retAddr_cmds() #+7
        # adds address to top of stack
        self.add_save_seg_cmds() #+28
        # saves segments to stack
        self.output_lines.append("\n" + "// repositions ARG to first function argument:")
        self.add_repos_arg_cmds(n_args) #+9
        # repositions ARG = SP - 5 - n_args
        self.output_lines.append("\n" + "// repositions LCL to SP:")
        self.add_repos_lcl_cmds() #+4
        # repositions LCL = SP
        self.output_lines.append("\n" + "// jumps to " + function_name + " address:")
        self.output_lines.append('@'  + function_name)
        self.output_lines.append("0;JMP")
        # jumps to called function
        self.output_lines.append("\n" + "// creates return address label:")
        self.output_lines.append('(' + self.rtn_function_name + '$' + "ret." + str(self.call_count) + ')')
        self.code_line += 2

    def add_repos_lcl_cmds(self):
        self.output_lines.append("@SP")
        self.output_lines.append("D=M")
        self.output_lines.append("@LCL")
        self.output_lines.append("M=D")
        self.code_line += 4

    def add_repos_arg_cmds(self, n_args):
        self.output_lines.append('@' + str(n_args))
        self.output_lines.append("D=A")
        self.output_lines.append("@5")
        self.output_lines.append("D=A+D")
        self.output_lines.append("@SP")
        self.output_lines.append("A=M")
        self.output_lines.append("D=A-D")
        self.output_lines.append("@ARG")
        self.output_lines.append("M=D")
        self.code_line += 9

    def add_save_seg_cmds(self):
        for seg in ["LCL", "ARG", "THIS", "THAT"]:
            self.output_lines.append("\n" + "// pushes the " + seg + " segment address to stack:")
            self.output_lines.append('@' + seg)
            self.output_lines.append("D=M")
            self.output_lines.append("@SP")
            self.output_lines.append("A=M")
            self.output_lines.append("M=D")
            self.add_spfwd_cmds()
            self.code_line += 7

    def add_push_retAddr_cmds(self):
        self.output_lines.append('@' + self.rtn_function_name + '$ret.' + str(self.call_count))
        self.output_lines.append("D=A")
        self.output_lines.append("@SP")
        self.output_lines.append("A=M")
        self.output_lines.append("M=D")
        self.add_spfwd_cmds()
        self.code_line += 7

    def write_return(self):
        """Writes assembly code that affects the "return" command."""
        self.output_lines.append("\n\n" + "// return code starts here:")
        self.output_lines.append("\n" + "// saves LCL address to endFrame label:")
        self.add_endframe_eq_lcl_cmds() #+4
        # endFrame = LCL
        self.output_lines.append("\n" + "// saves return address to endFrame - 5:")
        self.add_endframe_minus_ind_cmds(index = 5, label = "retAddr") #+7
        # retAddr = *(endFrame - 5)
        self.output_lines.append("\n" + "// pops top of stack (function output) to the first argument:")
        self.add_pop_to_arg_cmds() #+7
        # pop *ARG, SP++
        self.output_lines.append("\n" + "// sets SP to next address after the ARG pointer:")
        self.add_sp_eq_after_arg_cmds() #+4
        # SP = ARG + 1
        self.add_restore_seg_cmds() #+28
        # THAT = *(endFrame-1), THIS = *(endFrame-2), ARG = *(endFrame-3), LCL = *(endFrame-4)
        self.output_lines.append("\n" + "// jumps to the return address:")
        self.add_return_jmp_cmds() #+3
        # goto retAddr and end function

    def add_return_jmp_cmds(self):
        self.output_lines.append("@retAddr")
        self.output_lines.append("A=M")
        self.output_lines.append("0;JMP")
        self.code_line += 3

    def add_restore_seg_cmds(self):
        self.add_endframe_minus_ind_cmds(index=1, label="THAT")
        self.add_endframe_minus_ind_cmds(index=2, label="THIS")
        self.add_endframe_minus_ind_cmds(index=3, label="ARG")
        self.add_endframe_minus_ind_cmds(index=4, label="LCL")

    def add_sp_eq_after_arg_cmds(self):
        self.output_lines.append("@ARG")
        self.output_lines.append("D=M+1")
        self.output_lines.append("@SP")
        self.output_lines.append("M=D")
        self.code_line += 4

    def add_pop_to_arg_cmds(self):
        self.add_pointer_address_cmds()
        self.output_lines.append("D=M")
        self.output_lines.append("@ARG")
        self.output_lines.append("A=M")
        self.output_lines.append("M=D   // pops top of stack to ARG 0")
        self.code_line += 7

    def add_endframe_eq_lcl_cmds(self):
        self.output_lines.append("@LCL")
        self.output_lines.append("D=M")
        self.output_lines.append("@endFrame")
        self.output_lines.append("M=D")
        self.code_line += 4

    def add_endframe_minus_ind_cmds(self, index, label):
        self.output_lines.append("\n" + "// restores " + label + " segment address:")
        self.output_lines.append('@' + str(index))
        self.output_lines.append("D=A")
        self.output_lines.append("@endFrame")
        self.output_lines.append("A=M-D")
        self.output_lines.append("D=M")
        self.output_lines.append('@' + label)
        self.output_lines.append("M=D")
        self.code_line += 7

    def close(self) -> None:
        """Closes the output file."""

        self.output.close()




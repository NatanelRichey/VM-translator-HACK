"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter
INIT_FLAG = True

def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    vmfile = Parser(input_file)
    asmfile = CodeWriter(output_file)
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    asmfile.set_file_name(input_filename)
    global INIT_FLAG
    if INIT_FLAG:
        asmfile.write_init()
        INIT_FLAG = False

    while vmfile.has_more_commands():
        if vmfile.command_type() == "C_FUNCTION":
            function_name = vmfile.arg1()
            n_vars = vmfile.arg2()
            asmfile.write_function(function_name,n_vars)
        elif vmfile.command_type() == "C_ARITHMETIC":
            command = vmfile.arg1()
            asmfile.write_arithmetic(command)
        elif vmfile.command_type() == "C_PUSH" or vmfile.command_type() ==  "C_POP":
            command = vmfile.find_command_key()
            segment = vmfile.arg1()
            index = vmfile.arg2()
            asmfile.write_push_pop(command, segment, index)
        elif vmfile.command_type() == "C_LABEL":
            label = vmfile.arg1()
            asmfile.write_label(label)
        elif vmfile.command_type() == "C_GOTO":
            label = vmfile.arg1()
            asmfile.write_goto(label)
        elif vmfile.command_type() == "C_IF":
            label = vmfile.arg1()
            asmfile.write_if(label)
        elif vmfile.command_type() == "C_CALL":
            function_name = vmfile.arg1()
            n_args = vmfile.arg2()
            asmfile.write_call(function_name, n_args)
            # increases number of call in function by one
        elif vmfile.command_type() == "C_RETURN":
            asmfile.write_return()


        if vmfile.counter == len(vmfile.input_lines):
            break
        vmfile.advance()

    for cmd in asmfile.output_lines:
        output_file.write(cmd + '\n')

    return


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file)
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import numpy
import re

import bpy

# do:     apply lexer to Python Attributes string, producing output with positions of attributes from input string
# input:  string type value with Python Attributes, '.' between attributes, '[]' indexed value is treated similar
#         to '.' separated attribute, opening '(' and closing ')' are matched and included in name of attribute
# output: array of 2-tuples with attribute (start, end) position for all attributes in 'input_str',
#         if attribute is indexed then separate attribute is created for '[]', where start is position of opening '[',
#         and end is position of closing ']'
#         otherwise attribute start position is '.' (or beginning of string, edge case), and
#                   attribute end position is end of attribute name (or closing ')', edge case)
#
# important characters:
# . ( ) [ ] ' "

# Regular Expression includes alphanumeric and underscore
ALPHANUM_RE_STR = "^[A-Za-z0-9_]+$"

# state names
START_STATE = "start"
STOP_STATE = "stop"
READ_BEGIN_STATE = "read_begin"
READ_PERIOD_STATE = "read_period"
READ_ALPHA_CONTINUE_STATE = "read_alpha_continue"
READ_BRACKET_CONTINUE_STATE = "read_bracket_continue"
READ_BRACKET_END_STATE = "read_bracket_end"
READ_QUOTE_STATE = "read_quote"
READ_ESCAPE_CHAR_STATE = "read_escape_char"
READ_TRAIL_SPACE_STATE = "read_trail_space"

# state variable names
OUTPUT_VAR = "output"
ERROR_VAR = "error"
NAME_BEGIN_POS_VAR = "name_begin_pos"
NAME_END_POS_VAR = "name_end_pos"
BRACKET_TYPE_VAR = "bracket_type"   # None, or '[' square , or '(' round
BRACKET_DEPTH_VAR = "bracket_depth"
QUOTE_TYPE_VAR = "quote_type"   # None, or (') single , or (") double

close_bracket = {
    "[": "]",
    "(": ")",
}

def create_output_token(state_vars):
    # append to output
    state_vars[OUTPUT_VAR].append( (state_vars[NAME_BEGIN_POS_VAR], state_vars[NAME_END_POS_VAR]+1) )
    # set position variables to current character
    state_vars[NAME_BEGIN_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
    state_vars[NAME_END_POS_VAR] = state_vars[NAME_BEGIN_POS_VAR]

def start_func(input_char, state_vars):
    # None is 'End Of Input' marker
    if input_char is None:
        return STOP_STATE
    # ignore leading space before first attribute
    elif input_char.isspace():
        state_vars[NAME_BEGIN_POS_VAR] = state_vars[NAME_BEGIN_POS_VAR] + 1
        return START_STATE
    # only alphanumeric and underscore characters used in Python variable/attribute names
    elif re.match(ALPHANUM_RE_STR, input_char):
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_BEGIN_POS_VAR]
        return READ_ALPHA_CONTINUE_STATE
    else:
        state_vars[ERROR_VAR] = "'%s' is unrecognized character, expected start of Python attribute name " \
            "(alphanumeric/underscore characters only)" % input_char
        return STOP_STATE

def read_begin_func(input_char, state_vars):
    # None is 'End Of Input' marker
    if input_char is None:
        return STOP_STATE
    elif input_char == ".":
        state_vars[ERROR_VAR] = "'.' without preceding attribute name"
        return STOP_STATE
    elif input_char in ["[", "("]:
        state_vars[BRACKET_TYPE_VAR] = input_char
        state_vars[BRACKET_DEPTH_VAR] = 1
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        return READ_BRACKET_CONTINUE_STATE
    elif re.match(ALPHANUM_RE_STR, input_char):
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        state_vars[NAME_BEGIN_POS_VAR] = state_vars[NAME_END_POS_VAR]
        return READ_ALPHA_CONTINUE_STATE
    else:
        state_vars[ERROR_VAR] = "'%s' is unrecognized character, expected only alphanumeric/underscore in Python " \
            "attribute name" % input_char
        return STOP_STATE

def read_period_func(input_char, state_vars):
    if input_char is None:
        state_vars[ERROR_VAR] = "unexpected end of input string after '.' character"
        return STOP_STATE
    elif re.match(ALPHANUM_RE_STR, input_char):
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        state_vars[NAME_BEGIN_POS_VAR] = state_vars[NAME_END_POS_VAR]
        return READ_ALPHA_CONTINUE_STATE
    else:
        state_vars[ERROR_VAR] = "'%s' is unrecognized character after '.' character, expected only " \
            "alphanumeric/underscore in Python attribute name" % input_char
        return STOP_STATE

def read_alpha_continue_func(input_char, state_vars):
    # None is 'End Of Input' marker, and trailing spaces are ignored
    if input_char is None or input_char.isspace():
        if state_vars[BRACKET_DEPTH_VAR] == 0:
            create_output_token(state_vars)
        if input_char is None:
            return STOP_STATE
        return READ_TRAIL_SPACE_STATE
    elif input_char in [".", "[", "("]:
        if state_vars[BRACKET_DEPTH_VAR] == 0:
            create_output_token(state_vars)
        if input_char == ".":
            return READ_PERIOD_STATE
        else:
            state_vars[BRACKET_TYPE_VAR] = input_char
            state_vars[BRACKET_DEPTH_VAR] = 1
            return READ_BRACKET_CONTINUE_STATE
    elif re.match(ALPHANUM_RE_STR, input_char):
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        return READ_ALPHA_CONTINUE_STATE
    else:
        state_vars[ERROR_VAR] = "'%s' is unrecognized character, expected only alphanumeric/underscore in Python " \
            "attribute name" % input_char
        return STOP_STATE

def read_bracket_continue_func(input_char, state_vars):
    # None is 'End Of Input' marker
    if input_char is None:
        state_vars[ERROR_VAR] = "unexpected end of string found, expected closing ']'"
        return STOP_STATE
    # if 'open' bracket, then increment bracket depth
    elif input_char == state_vars[BRACKET_TYPE_VAR]:
        state_vars[BRACKET_DEPTH_VAR] = state_vars[BRACKET_DEPTH_VAR] + 1
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        return READ_BRACKET_CONTINUE_STATE
    # if 'close' bracket, then decrement bracket depth and check if final closing bracket
    elif input_char == close_bracket[state_vars[BRACKET_TYPE_VAR]]:
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        state_vars[BRACKET_DEPTH_VAR] = state_vars[BRACKET_DEPTH_VAR] - 1
        # if final closing ']' found then ...
        if state_vars[BRACKET_DEPTH_VAR] == 0:
            state_vars[BRACKET_TYPE_VAR] = None
            return READ_BRACKET_END_STATE
        else:
            return READ_BRACKET_CONTINUE_STATE
    elif input_char in ["\"", "'"]:
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        state_vars[QUOTE_TYPE_VAR] = input_char
        return READ_QUOTE_STATE
    else:
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        return READ_BRACKET_CONTINUE_STATE

def read_bracket_end_func(input_char, state_vars):
    # None is 'End Of Input' marker
    if input_char is None or input_char.isspace():
        create_output_token(state_vars)
        if input_char is None:
            return STOP_STATE
        return READ_TRAIL_SPACE_STATE
    elif input_char in ["[", "("]:
        create_output_token(state_vars)
        state_vars[BRACKET_TYPE_VAR] = input_char
        state_vars[BRACKET_DEPTH_VAR] = 1
        return READ_BRACKET_CONTINUE_STATE
    elif input_char == ".":
        create_output_token(state_vars)
        return READ_PERIOD_STATE
    else:
        state_vars[ERROR_VAR] = "'%s' is unrecognized character, expected only alphanumeric/underscore characters" \
            "in Python attribute name" % input_char
        return STOP_STATE

def read_quote_func(input_char, state_vars):
    # None is 'End Of Input' marker
    if input_char is None:
        state_vars[ERROR_VAR] = "unexpected end of input string while inside quote (%s) block" % \
            str(state_vars[QUOTE_TYPE_VAR])
        return STOP_STATE
    elif input_char == state_vars[QUOTE_TYPE_VAR]:
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        return READ_BRACKET_CONTINUE_STATE
    elif input_char == "\\":
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        return READ_ESCAPE_CHAR_STATE
    else:
        state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
        return READ_QUOTE_STATE

def read_escape_char_func(input_char, state_vars):
    state_vars[NAME_END_POS_VAR] = state_vars[NAME_END_POS_VAR] + 1
    return READ_QUOTE_STATE

def trail_space_func(input_char, state_vars):
    if input_char is None:
        return STOP_STATE
    elif input_char.isspace():
        return READ_TRAIL_SPACE_STATE
    else:
        state_vars[ERROR_VAR] = "'%s' is unrecognized character, expected only trailing space after final Python " \
                "attribute name of input string" % input_char
        return STOP_STATE

STATE_FUNCTIONS = {
    START_STATE: start_func,
    READ_BEGIN_STATE: read_begin_func,
    READ_PERIOD_STATE: read_period_func,
    READ_ALPHA_CONTINUE_STATE: read_alpha_continue_func,
    READ_BRACKET_CONTINUE_STATE: read_bracket_continue_func,
    READ_BRACKET_END_STATE: read_bracket_end_func,
    READ_QUOTE_STATE: read_quote_func,
    READ_ESCAPE_CHAR_STATE: read_escape_char_func,
    READ_TRAIL_SPACE_STATE: trail_space_func,
}

def get_init_state_vars():
    return {
        OUTPUT_VAR: [],
        ERROR_VAR: None,
        NAME_BEGIN_POS_VAR: 0,
        NAME_END_POS_VAR: None,
        BRACKET_DEPTH_VAR: 0,
        BRACKET_TYPE_VAR: None,
        QUOTE_TYPE_VAR: None,
    }

# following functions are intended for export, prior functions are intended for internal usage

def lex_py_attributes(input_str, verbose=0):
    state_vars = get_init_state_vars()
    current_state = START_STATE
    if verbose > 1: print("x   current_state  initial = " + str(current_state))
    i = 0
    input_len = len(input_str)
    while current_state != STOP_STATE:
        # read a character and process state
        if i < input_len:
            c = input_str[i]
            i = i + 1
        else:
            c = None
        if verbose > 1: print("x   c = " + str(c))
        if verbose > 1: print("x       current_state  before = " + str(current_state))
        state_func = STATE_FUNCTIONS[current_state]
        if verbose > 1: print("x       state_func = " + str(state_func))
        current_state = state_func(c, state_vars)
        if verbose > 1: print("x       current_state  after = " + str(current_state))
    if verbose > 1: print("x   current_state  final = " + str(current_state))
    return state_vars[OUTPUT_VAR], state_vars[ERROR_VAR]

#### test suite follows ####

test_data = [
    ("f", True, [ (0, 1) ]),
    ("  bpy.data.objects  ", True, [ (2, 5), (6, 10), (11, 18) ]),
    ("  bpy.data.objects[]  ", True, [ (2, 5), (6, 10), (11, 18), (18, 20) ]),
    ("s['\\'']", True, [ (0, 1), (1, 7) ]),
    ("b['asdfe']", True, [ (0, 1), (1, 10) ]),
    ("b[\"asdfe\"]", True, [ (0, 1), (1, 10) ]),
    ("b[\"as'd''dfe\"]", True, [ (0, 1), (1, 14) ]),
    ("b['as\"d\"\"dfe']", True, [ (0, 1), (1, 14) ]),
    ("bpy.data.objects", True, [(0, 3), (4, 8), (9, 16) ]),
    ("bpy.data.objects()", True, [ (0, 3), (4, 8), (9, 16), (16, 18) ]),
    ("bpy.data.objects[]()", True, [ (0, 3), (4, 8), (9, 16), (16, 18), (18, 20) ]),
    ("bpy.data.objects[]", True, [ (0, 3), (4, 8), (9, 16), (16, 18) ]),
    ("bpy.data.objects(asfd]][sdaf[sdf]])", True, [ (0, 3), (4, 8), (9, 16), (16, 35) ]),
    ("bpy.data.objects[f(((fdas))(ds))))sd))]", True, [ (0, 3), (4, 8), (9, 16), (16, 39) ]),
    ("bpy.data.objects[0]", True, [ (0, 3), (4, 8), (9, 16), (16, 19) ]),
    ("bpy.data.objects[f].name", True, [ (0, 3), (4, 8), (9, 16), (16, 19), (20, 24) ]),
    ("bpy.data.objects[f][g].name", True, [ (0, 3), (4, 8), (9, 16), (16, 19), (19, 22), (23, 27) ]),
    ("bpy.data.objects[f].name[h]", True, [ (0, 3), (4, 8), (9, 16), (16, 19), (20, 24), (24, 27) ]),
    ("a[]", True, [ (0, 1), (1, 3) ]),
    ("a[][]", True, [ (0, 1), (1, 3), (3, 5) ]),
    ("a[f][g]", True, [ (0, 1), (1, 4), (4, 7) ]),
    ("a()", True, [ (0, 1), (1, 3) ]),
    ("a()()", True, [ (0, 1), (1, 3), (3, 5) ]),
    ("a(f)(g)", True, [ (0, 1), (1, 4), (4, 7) ]),
    ("a[", False, [ (0, 1) ]),
    ("a]", False, []),
    ("a(", False, [ (0, 1) ]),
    ("a)", False, []),
    ("a(]", False, [ (0, 1) ]),
    ("a[)", False, [ (0, 1) ]),
    ("a[[[]", False, [ (0, 1) ]),
    ("a[[[ ]]]]", False, [ (0, 1) ]),
    ("a((( ))))", False, [ (0, 1) ]),
    ("a[]b", False, [ (0, 1) ]),
    ("a()b", False, [ (0, 1) ]),
    ("bpy.data.", False, [ (0, 3), (4, 8) ]),
    ("bpy.data..", False, [ (0, 3), (4, 8) ]),
    ("bpy..data", False, [ (0, 3) ]),
    (".data.objects", False, []),
    ("[]", False, []),
    ("a[].", False, [ (0, 1), (1, 3) ]),
    ("()", False, []),
    ("a().", False, [ (0, 1), (1, 3) ]),
    ("s['\\\\'']", False, [ (0, 1) ]),
    ("s[''']", False, [ (0, 1) ]),
    ("f a", False, [ (0, 1) ]),
    ("f [a]", False, [ (0, 1) ]),
    ("f (a)", False, [ (0, 1) ]),
]

def run_tests(verbose=1):
    if verbose > 0:
        print("\nStart tests of lexer:")
        print("-----------------------------------------------------------")
    for test_input, exp_correct, exp_output in test_data:
        if verbose > 1:
            print("    test str = " + test_input)
            ec_str = str(exp_correct)
            if not exp_correct:
                ec_str = ec_str + " *******"
            print("        expect correct = " + ec_str)
        output, e = lex_py_attributes(test_input, verbose)
        result_correct = e is None
        if verbose > 1:
            print("        result correct = " + str(result_correct))
            if not result_correct:
                print("******* error = " + str(e))
            print("    output =")
            print(output)
            if output != None:
                for x in output:
                    print("output item =" + test_input[ x[0]:x[1] ] )
            print("    = output")
        if result_correct == exp_correct:
            if verbose > 0: print("    match, test input = " + test_input)
            if output is None and exp_output is None:
                continue
            elif output != None and exp_output != None and len(output) == len(exp_output):
                if numpy.equal(output, exp_output).all():
                    continue
        if verbose > 0:
            print("    ***===--- ATTENTION! Result does not match expected, so debug this! ---===***")
            print("    test input = " + test_input)
            print("    result correct =" + str(result_correct))
            print("    expected correct =" + str(exp_correct))
            print("    result output =" + str(output))
            print("    expected output =" + str(exp_output))
            print("    output strings =")
            print(output)
            for x in output:
                print("output item =" + test_input[ x[0]:x[1] ] )
            print("    = output strings")
            print("-----------------------------------------------------------")
    if verbose > 0: print("End tests of lexer:\n")

#run_tests()

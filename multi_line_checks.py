from cpplint import GetPreviousNonBlankLine
from style_grader_classes import DataStructureTracker
from style_grader_functions import check_if_function, check_if_function_prototype, indent_helper, check_if_struct_or_class, check_if_switch_statement, check_if_cout_block, get_tab_type
from pyparsing import Literal
import re

def check_function_def_above_main(self, clean_lines):
    code = clean_lines.elided[self.current_line_num]

    # Ignore blank lines (obviously not a function definition)
    if re.match(r'^[\s\}\{\};]*$', code) or \
        re.match(r'(^|\s)+#.+', code):
        return

    # Ignore statements after main().
    if len(Literal("int main").searchString(code)):
        return

    # Prototypes and function declarations may have headers that span multiple lines
    code = get_full_statement(clean_lines.elided, self.current_line_num)

    prototype = check_if_function_prototype(code)
    function = check_if_function(code)

    if function and not prototype and self.outside_main:
        # pattern for return type (with or with ::) and function name (with or without ::)
        match = re.search(r"^\s*(?:\w+\s*\:\:\s*)*([\w_]+)\s+([\w\d_]+::)*([\w_][\w_\d]*)\s*\(", code)
        function_name = str(match.group(2)) + match.group(3) + '()' if match else code # show whole line if function name isn't found
        self.add_error(label="DEFINITION_ABOVE_MAIN", data={'function': function_name})

def check_statements_per_line(self, clean_lines):
    cleansed_line = clean_lines.elided[self.current_line_num]
    # This code is taken directly from cpplint lines 3430-3440
    if (cleansed_line.count(';') > 1 and
       # for loops are allowed two ;'s (and may run over two lines).
       cleansed_line.find('for') == -1 and
       (GetPreviousNonBlankLine(clean_lines, self.current_line_num)[0].find('for') == -1 or
       GetPreviousNonBlankLine(clean_lines, self.current_line_num)[0].find(';') != -1) and
       # It's ok to have many commands in a switch case that fits in 1 line
       not ((cleansed_line.find('case ') != -1 or
       cleansed_line.find('default:') != -1) and
       cleansed_line.find('break;') != -1)):
        self.add_error(label="STATEMENTS_PER_LINE")

def check_brace_consistency(self, clean_lines):
    code = clean_lines.elided[self.current_line_num]
    stripped_code = code.strip()

    function = check_if_function(code)

    # Check if this is really a function and not just a prototype.
    if (function):
        endOfFunctionHeader = self.current_line_num
        endCode = clean_lines.elided[endOfFunctionHeader].strip()
        while endCode.find(';') == -1 and endCode.find('{') == -1:
            endOfFunctionHeader += 1
            endCode = clean_lines.elided[endOfFunctionHeader].strip()

        semicolonIndex = endCode.find(';')
        brackIndex = endCode.find('{')
        if semicolonIndex != -1 and (brackIndex == -1 or semicolonIndex < brackIndex):
            function = False

    if_statement = re.search(r'^if\s*\(\s*', stripped_code)
    else_if_statement = re.search(r'^else\s*\(', code)
    else_statement = re.search(r'^else\s+', code)
    switch_statement = re.search(r'^switch\s*\(', stripped_code)

    current = self.current_line_num
    if function or if_statement or else_if_statement or else_statement or switch_statement:
        try:
            is_egyptian = deep_egyptian_check(clean_lines.elided, current)
            if is_egyptian:
                self.egyptian = True
                if self.not_egyptian is None:
                    self.not_egyptian = False
            elif is_egyptian is not None:
                 self.not_egyptian = True
                 if self.egyptian is None:
                    self.egyptian = False

            #if both of these are true, they are not consistent, therefore error.
            if self.not_egyptian and self.egyptian and not self.braces_error:
                self.add_error(label="BRACE_CONSISTENCY")
                self.braces_error = True

        except IndexError:
            # cannot access next line of end of file, rubric properties don't matter
            return

def check_block_indentation(self, clean_lines):


    code = clean_lines.elided[self.current_line_num]

    if check_if_struct_or_class(code):
        self.global_in_object = True

    if self.global_in_object and code.find('{') != -1:
        self.add_global_brace('{')
    elif self.global_in_object and code.find('}') != -1:
        self.pop_global_brace()

    indentation = re.search(r'^([ \t]*)\S', code)
    if not indentation:
        return

    function = check_if_function(code)
    prototype = check_if_function_prototype(code)
    struct_or_class = check_if_struct_or_class(code)

    indentation = indentation.group()
    indentation_size = len(indentation) - len(indentation.strip())

    if indentation[0] in ['\t', ' ']:
        hard_tabs = indentation[0] == '\t'
    else:
        hard_tabs = get_tab_type(clean_lines.elided) == '\t'

    #TODO: Load from config file?
    if hard_tabs:
        tab_size = 1
    else:
        tab_size = 4

    if function and indentation_size != 0 and not self.global_in_object and code.find('else if') == -1:
        data = {'expected': 0, 'found': indentation_size}
        self.add_error(label="BLOCK_INDENTATION", data=data)

    if function and not prototype:
        self.current_line_num = find_function_end(clean_lines.elided, self.current_line_num)

    if (function and not self.outside_main) or struct_or_class:
        #if not Egyptian style
        if code.find('{') == -1:
            if code.find('{'):
                temp_line_num = self.current_line_num + 1
                data_structure_tracker = DataStructureTracker()
                data_structure_tracker.brace_stack.append('{')

                if check_if_struct_or_class(code):
                    data_structure_tracker.in_class_or_struct = True
                if self.global_in_object:
                    self.add_global_brace('{')
                    data_structure_tracker.add_object_brace('{')

                results = indent_helper(indentation, tab_size, clean_lines,
                                        data_structure_tracker, temp_line_num)

                for error in results:
                    self.add_error(**error)
            else:
                #TODO Figure out what it means to not have braces in the right place
                pass
        else:
            openCurlyLoc = code.find('{')
            closeCurlyLoc = code.rfind('}')
            if (openCurlyLoc == -1 or closeCurlyLoc == -1 or openCurlyLoc > closeCurlyLoc):
                temp_line_num = self.current_line_num
                data_structure_tracker = DataStructureTracker()

                if check_if_struct_or_class(code):
                    data_structure_tracker.add_object_brace("{")
                    data_structure_tracker.in_class_or_struct = True
                elif check_if_switch_statement(code):
                    data_structure_tracker.in_switch = True
                    data_structure_tracker.add_switch_brace('{', indentation)

                data_structure_tracker.brace_stack.append('{')
                results = indent_helper(indentation, tab_size, clean_lines,
                                        data_structure_tracker, temp_line_num)
                for error in results:
                    if not self.contains_error(**error):
                        self.add_error(**error)


# New operator spacing function
def check_operator_spacing(self, clean_lines):


    code = get_full_statement(clean_lines.elided, self.current_line_num)

    # Check if this is a continuation of the previous line.
    first_line = self.current_line_num
    if(first_line > 1):
        prev_line = clean_lines.elided[ first_line - 1]
        if (len(get_full_statement(clean_lines.elided, first_line - 1)) > len(prev_line)):
            return # Already checked this line

    code = get_full_statement(clean_lines.elided, self.current_line_num)

    # TODO: Temporary fix to ignore & and * operators in function params
    if check_if_function(code) or check_if_function_prototype(code) or \
            '#include' in code: return
    # Check normal operators
    # account for *=, %=, /=, +=, -=
    indexes = []
    for operator in list('+-%*/!><=&|'):
        indexes += findOccurences(code, operator)
    indexes.sort()  # Force compound operator indexes to be correctly ordered

    skip_next = False
    for operator_index in indexes:
        if skip_next:
            # skip second operator in compound/increment/decrement operator
            skip_next = False
            continue

        if skip_operator(code, operator_index):
            skip_next = True
        elif is_compound_operator(code, operator_index):
            # Always use front char in compound operators, therefore need to skip second char
            skip_next = True
            if not operator_helper(True, code, operator_index):
                self.add_error(label='OPERATOR_SPACING', column=operator_index,
                                data={'operator': code[operator_index:operator_index + 2]})
        elif is_cast_operator(code, operator_index):
            continue # for example: static_cast<int>(x);
        elif is_unary_operator(code, operator_index):
            # Checking for unary operators (!, +, -)
            prev_index = operator_index - 1
            # Only check for spacing in front of unary operator
            if code[prev_index] and code[prev_index] not in ['\t', ' ', '\r', '\n', '(']:
                self.add_error(label='OPERATOR_SPACING', column=operator_index, data={'operator': code[operator_index]})
            elif code[operator_index + 1] and code[operator_index + 1] in ['\t', ' ', '\r', '\n']:
                # There should be no space after a unary operator
                self.add_error(label='OPERATOR_SPACING', column=operator_index, data={'operator': code[operator_index]})
        elif not operator_helper(False, code, operator_index):
            operator = code[operator_index]
            prev_index = operator_index - 1
            # If there is a space before a +/- but not after it, then maybe it is a unary operator we missed.
            if ((not code[prev_index]) or (code[prev_index] in ['\t', ' ', '\r', '\n', '('])):
                if (operator == '+'):
                    operator += '. If this is the unary +, you may ignore this error'
                elif (operator == '-'):
                    operator += '. If this is the unary -, you may ignore this error'
            self.add_error(label='OPERATOR_SPACING', column=operator_index, data={'operator': operator})

def find_function_end(code, current_line):
    # Go to the next line if we are not on the last line and there is no '{'
    while (current_line < len(code) - 1) and code[current_line].find('{') == -1:
        current_line += 1

    if len(code[current_line].strip()) == 1:
        current_line -= 1

    return current_line

# Returns true, false, or None (if unknown)
def deep_egyptian_check(code, current_line):
    # Find line where the conditional or argument list ends
    lineNum = find_end_of_parens(code, current_line)

    # Egyptian if opening curly brace is on the same line as the conditional/args
    if code[lineNum].find('{') != -1:
        return True

    # Maybe there are no braces. Check if a semicolon comes first.
    while code[lineNum].find(';') == -1 and code[lineNum].find('{') == -1:
        lineNum += 1

    if code[lineNum].find(';') != -1:
        return None

    return False


# Used for brace consistency check
def find_end_of_parens(code, current_line):
    pstack = []

    # Find the next line where there is a '('
    lineNum = current_line
    try:
        openParenIndex = code[lineNum].find('(')
        while openParenIndex == -1:
            lineNum += 1
            openParenIndex = code[lineNum].find('(')

        # Look through this line and onward until every '(' is matched with a ')'
        code_line = code[lineNum]
        while True:
            for i, c in enumerate(code_line):
                if c == '(':
                    pstack.append(i)
                elif c == ')':
                    if len(pstack) == 0:
                        raise IndexError("No matching closing parens at: " + str(i))
                    pstack.pop()
            if len(pstack) == 0:
                break;
            else:
                lineNum += 1
                code_line = code[lineNum]

    except IndexError:
        # cannot access next line of end of file or bad parenthesis
        return lineNum

    return lineNum

# Returns a single line containing the current line and subsequent lines until the statement ends.
def get_full_statement(clean_lines, current_line):
    code = clean_lines[current_line]
    if code.isspace():
        return code

    next_line = current_line + 1
    while (code.find(';') < 0 and code.find('{') < 0 and code.find('}') < 0 and next_line < len(clean_lines)):
        code += clean_lines[next_line]
        next_line += 1

    return re.sub('[\r\n]', ' ', code) # remove newlines (make code a single line)

def findOccurences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

def skip_operator(code, index):
    # Don't worry about increment/decrement/pointer-arrow operators
    return is_increment_decrement(code, index) or is_pointer_arrow(code, index)

def is_increment_decrement(code, index):
    return code[index + 1] and code[index] in ['+', '-'] and code[index + 1] == code[index]

def is_unary_operator(code, index):
    return (code[index] == '!' and code[index + 1] and code[index + 1] != '=') or \
        re.search('[\(\+\-\*\%<>=\&\|\!]\s*[\-\+]$', code[:index + 1]) is not None  or \
        re.match('\s*[\+\-]$', code[:index + 1]) is not None or \
        re.search('return\s+[\-\+]$', code[:index + 1]) is not None

def is_cast_operator(code, index):
    check = re.search('(?:const|dynamic|reinterpret|static)_cast\s*(<)\s*[_\w\d]+\s*(>)', code)
    return check and (check.span(1)[0] == index or check.span(2)[0] == index)


def is_pointer_arrow(code, index):
    return code[index + 1] and code[index:(index+2)] == '->'

def is_compound_operator(code, index):
    if code[index + 1]:
        # Check for >=, <=, >>, <<
        if code[index] in ['>', '<']:
            if code[index + 1] == '=' or code[index + 1] == code[index]:
                return True
        # Check for +=, -=, *=, /=, %=, ==, !=
        if code[index] in ['*', '/', '+', '-', '!', '=', '%']:
            if code[index + 1] == '=':
                return True
        # Check &&, ||, &=, |=
        elif code[index] in ['&', '|']:
            if code[index + 1] == code[index] or code[index + 1] == '=':
                return True
    return False

def operator_helper(compound, code, index):
    correct_spacing = True
    if compound:
        correct_spacing = ((len(code) < index + 3) or re.match(r'\s', code[index + 2])) and \
            ((index == 0) or re.match(r'[ \t]', code[index - 1]))
    else:
        if code[index + 1] and code[index + 1] not in [' ', '\t', '\r', '\n']:
            correct_spacing = False
        if code[index - 1] and code[index - 1] not in [' ', '\t']:
            correct_spacing = False
    return correct_spacing
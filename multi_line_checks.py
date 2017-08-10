from cpplint import GetPreviousNonBlankLine
from style_grader_classes import DataStructureTracker
from style_grader_functions import check_if_function, check_if_function_prototype, indent_helper, check_if_struct_or_class, check_if_switch_statement, check_if_cout_block
from pyparsing import Literal
import re

def check_function_def_above_main(self, clean_lines):
    code = clean_lines.lines[self.current_line_num]

    # Ignore blank lines (obviously not a function definition)
    if (code.isspace()):
        return

    # Ignore statements after main().
    if len(Literal("int main").searchString(code)):
        return

    # Prototypes and function declarations may have headers that span multiple lines
    next_line = self.current_line_num + 1
    while (code.find(';') < 0 and code.find('{') < 0 and code.find('}') < 0 and next_line < len(clean_lines.lines)):
        code += clean_lines.lines[next_line]
        next_line += 1

    code = re.sub('[\r\n]', ' ', code) # remove newlines (make code a single line)

    prototype = check_if_function_prototype(code)
    function = check_if_function(code)

    if function and not prototype and self.outside_main:
        function_regex = re.compile("^\s*(\w+)\s+(\w+)")
        match = function_regex.search(code)
        function_name = match.group(2) if match else code # show whole line if function name isn't found
        self.add_error(label="DEFINITION_ABOVE_MAIN", data={'function': function_name})

def check_statements_per_line(self, clean_lines):
    cleansed_line = clean_lines.lines[self.current_line_num]
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
    code = clean_lines.lines[self.current_line_num]
    stripped_code = code.strip()
    function = check_if_function(code)
    if_statement = re.search(r'^if\s*\(\s*', stripped_code)
    else_if_statement = re.search(r'^else\s*\(', code)
    else_statement = re.search(r'^else\s+', code)
    switch_statement = re.search(r'^switch\s*\(', stripped_code)
    indentation = re.search(r'^( *)\S', code)

    if indentation:
        indentation = indentation.group()
        indentation_size = len(indentation) - len(indentation.strip())
    else:
        indentation_size = 0

    current = self.current_line_num
    if function or if_statement or else_statement or switch_statement:
        try:
            if function or \
                else_if_statement or\
                else_statement  or\
                switch_statement or\
                if_statement:
                    if deep_egyptian_check(clean_lines.lines, indentation_size, current):
                        self.egyptian = True
                    else:
                         self.not_egyptian = True

            elif not self.outside_main:
                if not self.braces_error:
                    self.add_error(label="BRACE_CONSISTENCY")
                    self.braces_error = True

            if self.not_egyptian and self.egyptian and not self.braces_error:
                 self.add_error(label="BRACE_CONSISTENCY")
                 self.braces_error = True

            #if both of these are true, they are not consistent, therefore error.
            if self.not_egyptian:
                if self.egyptian and not self.braces_error:
                    self.add_error(label="BRACE_CONSISTENCY")
                    self.braces_error = True

        except IndexError:
            # cannot access next line of end of file, rubric properties don't matter
            return

def check_block_indentation(self, clean_lines):
    #TODO: Load from config file?
    tab_size = 4

    code = clean_lines.lines[self.current_line_num]
    print (code)

    if check_if_struct_or_class(code):
        self.global_in_object = True

    if self.global_in_object and code.find('{') != -1:
        self.add_global_brace('{')
    elif self.global_in_object and code.find('}') != -1:
        self.pop_global_brace()

    function = check_if_function(code)
    prototype = check_if_function_prototype(code)
    struct_or_class = check_if_struct_or_class(code)
    indentation = re.search(r'^( *)\S', code)
    if indentation:
        indentation = indentation.group()
        indentation_size = len(indentation) - len(indentation.strip())
    else:
        return

    if function and indentation_size != 0 and not self.global_in_object and code.find('else if') == -1:
        data = {'expected': 0, 'found': indentation_size}
        self.add_error(label="BLOCK_INDENTATION", data=data)

    if function and not prototype:
        self.current_line_num = find_function_end(clean_lines.lines, self.current_line_num)

    if (function and not self.outside_main) or struct_or_class:
        #if not egyptian style
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
            if not (code.find('{') != -1 and code.rfind('}') != -1 and code.find('{') < code.rfind('}')):
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
    else:
        return


def find_function_end(code, current_line):
    while code[current_line] and code[current_line].find('{') == -1:
        current_line += 1

    if len(code[current_line].strip()) == 1:
        current_line -= 1

    return current_line

def deep_egyptian_check(code, indentation_size, current_line):
        while code[current_line].find('{') == -1:
            current_line += 1
        indent = code[current_line].find('{')
        if code[current_line].find('{') != indentation_size:
            return True
        else:
            return False

from collections import Counter
import getopt
import re

from pyparsing import Literal, Word, Optional, ParseException, alphanums, Keyword, srange, alphas

class EmptyFileException(object):
    pass

def get_indent_level(filename):
    data = filename.readlines()
    indent_re = re.compile('^\s+\w')
    results = []
    for line in data:
        match = indent_re.search(line)
        if match:
            results.append(len(match.group(0))-1)
    return Counter(results).most_common(1)[0] if results else 4

def check_if_function(code):
    return_type = Word(alphas + '_', alphanums + '_&*') # Bad style to have "_" but syntactically valid
    function_name = Word(alphas + '_', alphanums + '_:><')
    args = Word(alphas + '_', alphanums + ',_[]&* ')
    function_open = Literal("{")
    function_close = Literal("}")
    function_declaration = Optional(srange("[a-z]")) + return_type + function_name + "(" + Optional(args) + Optional(Word(' const'))
    grammar = function_declaration + Optional(function_open)
    if len(grammar.searchString(code)):
        return True
    return False

def check_if_function_prototype(code):
    return_type = Word(alphanums + '_[]') # Bad style to have "_" but syntactically valid
    function_name = Word(alphanums + '_:')
    args = Word(alphanums + ',_[]&* ')
    function_open = Literal("{")
    function_close = Literal("}")
    function_declaration = Optional(srange('[a-z]')) + return_type + function_name + "(" + Optional(args) + ")" + Optional(Word(' const')) + Optional(" ") + ";"
    grammar = function_declaration + Optional(function_open)
    if len(grammar.searchString(code)):
        return True
    return False

def check_if_switch_statement(code):
    statement = Keyword('switch')
    args = Word(alphanums + '_')
    grammar = statement + Optional(" ") + "(" + args + ")"
    try:
        grammar.parseString(code)
        return True
    except ParseException:
        return False

def check_if_statement(code):
    statement = Keyword('if')
    args = Word(alphanums + ',_[]&*!=+-%&|/() ')
    grammar = statement + "("
    try:
        grammar.parseString(code)
        return True
    except ParseException:
        return False

def check_else_if(code):
    statement = Keyword('else if')
    args = Word(alphanums + ',_[]&* ')
    grammar = statement + Optional(" ") + "("
    try:
        grammar.parseString(code)
        return True
    except ParseException:
        return False

def check_else(code):
    statement = Keyword('else')
    grammar = statement + Optional(Word("{"))
    try:
        grammar.parseString(code)
        return True and not check_else_if(code)
    except:
        return False

def check_if_case_arg(code):
    statement = (Keyword('case') | Keyword('default'))
    if len(statement.searchString(code)):
        return True
    else:
        return False

def check_if_cout_block(code):
    statement = Keyword('cout')
    grammar = statement + Optional(" ")

    try:
        grammar.parseString(code)
        if code.find(';') == -1:
            return True
        else:
            return False
    except ParseException:
        return False

def indent_helper(indentation, tab_size, clean_lines, data_structure_tracker, temp_line_num):
    indentation = re.search(r'^( *)\S', clean_lines.lines[temp_line_num])
    results = list()
    if not indentation:
        return results
    indentation = indentation.group()
    indentation_size = len(indentation) - len(indentation.strip())
    data_structure_tracker.in_block = True
    next_indentation = indentation_size + tab_size
    while data_structure_tracker.in_block:
        temp_line_num += 1
        try:
            current_indentation = re.search(r'^( *)\S',
                                        clean_lines.lines[temp_line_num])
            print clean_lines.lines[temp_line_num]
            code = erase_string(clean_lines.lines[temp_line_num])
            switch_statement = check_if_switch_statement(code)
            if_statement = check_if_statement(code)
            else_if = check_else_if(code)
            else_statement = check_else(code)
            if not data_structure_tracker.in_cout_block:
                cout_block = check_if_cout_block(code)

            if if_statement or else_if or else_statement:
                # Egyptian or Block style bracing on conditional
                if clean_lines.lines[temp_line_num].find('{') != -1 or \
                    clean_lines.lines[temp_line_num + 1].find('{') == current_indentation:
                    data_structure_tracker.in_if = True
                else:
                    data_structure_tracker.in_single_statement_if = True

            #if you hit a cout that is not finished on one line, it can be indented and still styled correctly
            if cout_block:
                data_structure_tracker.in_cout_block = True
            if switch_statement:
                data_structure_tracker.in_switch = True

            is_break_statement = check_if_break_statement(code)

            if is_break_statement and not data_structure_tracker.in_switch and not cout_block:
                results.append({'label': 'UNNECESSARY_BREAK', 'line': temp_line_num + 1})

            if current_indentation:
                line_start = current_indentation.group()
                current_indentation = len(line_start) - len(line_start.strip())

                if code.find('{') != -1 and code.rfind('}') != -1 and code.find('{') < code.rfind('}'):
                    # ignore lines such as if () { statement; }
                    continue

                if decrease_indentation(code, data_structure_tracker):
                    if code.rfind('}') != -1:
                        data_structure_tracker.pop_brace()
                        if data_structure_tracker.in_switch:
                            brace_info = data_structure_tracker.pop_switch_brace()
                            if not data_structure_tracker.in_switch:
                                next_indentation = brace_info['indentation'] + tab_size # add tab_size to account for -= below
                    next_indentation -= tab_size

                if current_indentation != next_indentation:
                    data = {'expected': next_indentation, 'found': current_indentation}
                    results.append({'label': 'BLOCK_INDENTATION', 'line': temp_line_num + 1, 'data': data})

                if increase_indentation(code, data_structure_tracker):
                    if code.find('{') != -1:
                        if data_structure_tracker.in_switch:
                            data_structure_tracker.add_switch_brace('{', current_indentation)
                        data_structure_tracker.add_brace('{')
                    if data_structure_tracker.in_switch and check_if_case_arg(code):
                        data_structure_tracker.switch_case_index += 1
                    next_indentation += tab_size

        except IndexError:
            data_structure_tracker.in_block = False

    return results


def indent_equals(line_num, code, current_indentation):
    indent_size = current_indentation
    while current_indentation and current_indentation == indent_size:
        line_num += 1
        current_indentation = re.search(r'^( *)\S',
                                    code[line_num])
        if current_indentation:
            line_start = current_indentation.group()
            current_indentation = len(line_start) - len(line_start.strip())

    return line_num

def check_if_public_or_private(code):

    private = Keyword('private')
    public = Keyword('public')

    grammar = (private | public)

    if len(grammar.searchString(code)) >= 1:
        return True
    else:
        return False

def check_if_break_statement(code):

    statement = Keyword('break')
    grammar = statement + Optional(" ") + ";"
    try:
        grammar.parseString(code)
        return True
    except ParseException:
        return False

def check_if_struct_or_class(code):
    class_type = Keyword('class')
    struct_type = Keyword('struct')
    name = Word(alphanums + '_')
    statement = (class_type + name | struct_type + name)

    if len(statement.searchString(code)):
        return True
    return False

def print_success():
    print 'No errors found'

def decrease_indentation(code, tracker):
    return code.rfind('}') != -1 or \
            (check_if_public_or_private(code) and tracker.in_class_or_struct) or \
            (check_if_case_arg(code) and tracker.in_switch and tracker.switch_case_index != 0)

def increase_indentation(code, tracker):
    return code.find('{') != -1 or \
            (check_if_case_arg(code) and tracker.in_switch) or \
            (check_if_public_or_private(code) and tracker.in_class_or_struct)

def erase_string(code):
    # remove contents of literal strings
    code = code.replace("\\\"", "") # remove escaped quotes
    results = re.findall(r'"(.*?)"', code)
    for string in results:
        quote_mark = "\""
        code = code.replace(quote_mark + string + quote_mark, "\"\"")

    # remove contents of literal chars
    code = code.replace('\\\\', '') # replace escaped backslash
    code = code.replace("\\'", "") # remove escaped single quote
    results = re.findall(r"'(.*?)'", code)
    for string in results:
        single_quote_mark = "'"
        code = code.replace(single_quote_mark + string + single_quote_mark, "''")
    return code
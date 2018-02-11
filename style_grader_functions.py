import getopt
import re

from pyparsing import Forward, Group, Suppress, Literal, Word, Optional, ParseException, alphanums, Keyword, srange, alphas, NotAny, delimitedList, ParseResults

class EmptyFileException(object):
    pass

# Detects the length of tabs (returns 1 for hard tabs)
def get_soft_tab_length(file):
    data = file.readlines()
    indentRe = re.compile(r'^[ \t]+[^ \t]')
    indentLengthCount = [0] * 11 # key is space counts and values are number of lines
    numLinesWithTabs = 0
    numLinesWithSpaces = 0

    # count the number of spaces at the beginning of each line.
    for line in data:
        firstSpaces = indentRe.match(line)
        if not firstSpaces:
            continue
        firstSpaces = firstSpaces.group(0)
        spaceChars = len(firstSpaces) - 1

        if firstSpaces[0] == '\t':
            numLinesWithTabs += 1

        # Assume nobody uses single space indentation
        elif spaceChars > 1 and spaceChars <= 10:
            indentLengthCount[spaceChars] += 1
            numLinesWithSpaces += 1

    if numLinesWithTabs >= numLinesWithSpaces:
        return 1 # hard tabs have an indent of 1

    # Assume indent of 4 if no indentation found.
    if all(v == 0 for v in indentLengthCount):
        return 4

    # Calculate "probability" based on the count of first two levels of indentation
    weights = {
        2: indentLengthCount[2] + indentLengthCount[4] / 2,
        3: indentLengthCount[3] + indentLengthCount[6] / 2 - indentLengthCount[1] * 0.75,
        4: indentLengthCount[4] + indentLengthCount[8] / 2,
        5: indentLengthCount[5] + indentLengthCount[10] / 2 - indentLengthCount[1] * 0.75
    }

    # return the value with the max probability
    return max(weights, key=weights.get)


def get_tab_type(code_lines):
    indent_re = re.compile(r'^[ \t]+\w')
    results = []
    for line in code_lines:
        match = indent_re.match(line)
        if match:
            results.append(match.group(0)[0])

    return max(set(results), key=results.count) if len(results) > 0 else '\t'

# Not currently used, but will be very useful for operator spacing
def parse_template_expression(input: str):
    '''
    reads template expression like std::shared_ptr<std::vector<std::map<std::string, int>>>
    >>> parse_template_expression("std::map<std::string, int>")
    ('std::map', ('std::string', 'int'))
    https://gist.github.com/fHachenberg/6cb2a44a904cd62934ef0825660bdc67
    '''

    cpp_name = Word(alphanums + "_:")
    open_bracket  = Literal("<")
    close_bracket = Literal(">")

    expr = Forward()
    expr << cpp_name + Optional(Group(Suppress(open_bracket) + delimitedList(expr) + Suppress(close_bracket)))

    result = expr.parseString(input, parseAll=True)
    def rec_mktpl(lst):
        if isinstance(lst, ParseResults):
            return tuple([rec_mktpl(l) for l in lst])
        else:
            return lst
    return rec_mktpl(result)

def check_if_function(code):
    identifier = Word(alphas + '_', alphanums + '_:')
    return_type = Word(alphas + '_', alphanums + '_&*') # Bad style to have "_" but syntactically valid
    function_name = Word(alphas + '_', alphanums + '_:')
    template = Optional(Group(Suppress(Literal("<")) + identifier + Suppress(Literal(">"))))
    args = Word(alphas + '_', alphanums + ',_[]&*<> ')
    function_open = Literal("{")
    function_close = Literal("}")
    function_declaration = Optional(srange("[a-z]")) + return_type + function_name + Optional(template) + "(" + Optional(args) + Optional(Word(' const'))
    grammar = function_declaration + Optional(function_open)
    results = grammar.searchString(code)
    if len(results) and 'new' not in (results[0]).asList():
        return True
    return False

def check_if_function_prototype(code):

    if not code:
        return False;

    return_type = Word(alphanums + '_[]', alphanums + '_:&*') # Bad style to have "_", but syntactically valid
    function_name = Word(alphanums + '_', alphanums + '_:><')
    args = Word(alphanums + ':,_[]&*<> ="\'') # identifiers are not required, just types
    grammar = Optional(srange('[a-z]')) + return_type + function_name + "(" + Optional(args) + ")" + Optional(Word(' const')) + Optional(" ") + ";"

    results = grammar.searchString(code)

    # should not be preceded by the keyword 'new'
    if len(results) and 'new' not in (results[0]).asList():
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

    results = list()
    if not indentation:
        return results
    #indentation = indentation.group()
    indentation_size = len(indentation) - len(indentation.strip())
    data_structure_tracker.in_block = True
    next_indentation = indentation_size + tab_size
    while data_structure_tracker.in_block:
        temp_line_num += 1
        try:
            current_indentation = re.match(r'^([ \t]*)\S',
                                        clean_lines.raw_lines[temp_line_num])
            #print(clean_lines.lines[temp_line_num])
            switch_statement = check_if_switch_statement(clean_lines.lines[temp_line_num])
            if_statement = check_if_statement(clean_lines.lines[temp_line_num])
            else_if = check_else_if(clean_lines.lines[temp_line_num])
            else_statment = check_else(clean_lines.lines[temp_line_num])
            if not data_structure_tracker.in_cout_block:
                cout_block = check_if_cout_block(clean_lines.lines[temp_line_num])

            if if_statement or else_if:
                # Egyptian or Block style bracing on conditional
                if clean_lines.lines[temp_line_num + 1].find('{') == -1 and clean_lines.lines[temp_line_num].find('{') == -1:
                    data_structure_tracker.in_if = True
                elif clean_lines.lines[temp_line_num +1].find('{') != -1 and current_indentation != clean_lines.lines[temp_line_num].find('{'):
                    data_structure_tracker.in_if = True

            #if you hit a cout that is not finished on one line, it can be indented and still styled correctly
            if cout_block:
                data_structure_tracker.in_cout_block = True
            if switch_statement:
                data_structure_tracker.in_switch = True

            is_break_statement = check_if_break_statement(clean_lines.lines[temp_line_num])

            if is_break_statement and not data_structure_tracker.in_switch and not cout_block:
                results.append({'label': 'UNNECESSARY_BREAK', 'line': temp_line_num + 1})

            if current_indentation:
                line_start = current_indentation.group()
                current_indentation = len(line_start) - len(line_start.strip())

                if data_structure_tracker.in_cout_block and data_structure_tracker.cout_index == 1:
                    next_indentation += tab_size

                if data_structure_tracker.in_cout_block:
                    data_structure_tracker.cout_index += 1

                elif current_indentation != next_indentation and clean_lines.lines[temp_line_num - 1].find('=') != -1 and \
                    clean_lines.lines[temp_line_num - 1].find(';') == -1:

                    temp_line_num = indent_equals(temp_line_num, clean_lines.raw_lines, current_indentation)

                elif current_indentation != next_indentation and line_start.find('}') == -1:
                    #check for public: private: and case: exceptions
                    if(check_if_public_or_private(clean_lines.lines[temp_line_num]) and \
                            data_structure_tracker.in_class_or_struct) or \
                            (check_if_case_arg(clean_lines.lines[temp_line_num]) and \
                            data_structure_tracker.in_switch):

                        next_indentation -= tab_size
                    else:
                        if not data_structure_tracker.in_if and clean_lines.raw_lines[temp_line_num] != '/**/':
                            results.append({'label': 'BLOCK_INDENTATION', 'line': temp_line_num + 1,
                                'data': {'expected': next_indentation, 'found': current_indentation}
                            })


                if clean_lines.lines[temp_line_num].find("{") != -1 and clean_lines.lines[temp_line_num].find("}") != -1:
                    # nothing to adjust
                    continue

                elif clean_lines.lines[temp_line_num].find("{") != -1:
                    if data_structure_tracker.in_switch:
                        data_structure_tracker.add_switch_brace("{", indentation)
                    if data_structure_tracker.in_class_or_struct:
                        data_structure_tracker.add_object_brace("{")
                    data_structure_tracker.add_brace("{")
                    next_indentation = current_indentation + tab_size


                elif clean_lines.lines[temp_line_num].find("}") != -1:
                    end_switch = data_structure_tracker.in_switch
                    if data_structure_tracker.in_switch:
                        data_structure_tracker.pop_switch_brace()
                    if data_structure_tracker.in_class_or_struct:
                        data_structure_tracker.pop_object_brace()
                    data_structure_tracker.pop_brace()
                    next_indentation = next_indentation - tab_size

                    if data_structure_tracker.in_if:
                        data_structure_tracker.in_if = False
                        next_indentation = current_indentation

                    if end_switch and not data_structure_tracker.in_switch:
                        next_indentation = current_indentation

                if(check_if_public_or_private(clean_lines.lines[temp_line_num]) and
                       data_structure_tracker.in_class_or_struct):
                    next_indentation += tab_size

                if check_if_case_arg(clean_lines.lines[temp_line_num]) \
                        and data_structure_tracker.in_switch:
                    next_indentation += tab_size

                if data_structure_tracker.in_cout_block and clean_lines.lines[temp_line_num].find(';') != -1:
                    data_structure_tracker.in_cout_block = False
                    next_indentation -= tab_size
                    data_structure_tracker.cout_index = 0

        except IndexError:
            data_structure_tracker.in_block = False

    return results


def indent_equals(line_num, code, current_indentation):
    indent_size = current_indentation
    while current_indentation and current_indentation == indent_size:
        line_num += 1
        current_indentation = re.search(r'^([ \t]*)\S',
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
    print('No errors found')

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

from style_grader_functions import check_if_function, check_if_function_prototype
from pyparsing import Literal, Word, Optional, ParseException, Group, SkipTo, alphanums, LineStart, srange
import re





def check_int_for_bool(self, code):
    if check_if_function(code):
        function_regex = re.compile("^\s*(\w+)\s+(\w+)")
        match = function_regex.search(code)
        if match:
            self.current_function = (match.group(1), match.group(2))
    current_function = getattr(self, "current_function", ("", ""))

    return_regex = re.compile("\s*return\s+(\w+)")
    match = return_regex.search(code)
    if match and match.group(1).isdigit() and current_function[0] == "bool":
        self.add_error(label="INT_FOR_BOOL")

# New operator spacing function
def check_operator_spacing(self, code):
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
        else:
            # Checking for unary operators (!, +, -)
            if is_unary_operator(code, operator_index):
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
        if code[index + 2] and code[index + 2] != '\r' and code[index + 2] != '\n' and code[index + 2] != ' ':
            correct_spacing = False
        if code[index - 1] and code[index - 1] != ' ':
            correct_spacing = False
    else:
        if code[index + 1] and code[index + 1] != '\r' and code[index + 1] != '\n' and code[index + 1] != ' ':
            correct_spacing = False
        if code[index - 1] and code[index - 1] != ' ':
            correct_spacing = False
    return correct_spacing

def findOccurences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

def check_equals_true(self, code):
    keyword = Literal("true") | Literal("false")
    statement_parser = Group("==" + keyword) | Group(keyword + "==")
    if len(statement_parser.searchString(code)):
        self.add_error(label="EQUALS_TRUE")


def check_goto(self, code):
    # Hacky but gets the job done for now - has holes though
    q_goto = re.compile('\".*goto.*\"')
    r_goto = re.compile('(?:\s+|^|\{)goto\s+')
    if r_goto.search(code) and not q_goto.search(code):
        self.add_error(label="GOTO")


def check_define_statement(self, code):
    q_define = re.compile('\".*(?:\s+|^)#\s*define\s+.*\"')
    r_define = re.compile('(?:\s+|^)#\s*define\s+')
    if r_define.search(code) and not q_define.search(code):
        words = code.split()
        # They shouldn't be using __MY_HEADER_H__ because __-names are
        # reserved, but we'll allow it anyways.
        legal_endings = ["_H", "_H__"]
        if not any(words[-1].endswith(i) for i in legal_endings):
            self.add_error(label="DEFINE_STATEMENT")


def check_continue(self, code):
    # Hacky but gets the job done for now - has holes though
    q_continue = re.compile('\".*continue.*\"')
    r_continue = re.compile('(?:\s+|^|\{)continue\s*;')
    if r_continue.search(code) and not q_continue.search(code):
        self.add_error(label="CONTINUE_STATEMENT")


def check_ternary_operator(self, code):
    q_ternary = re.compile('\".*\?.*\"')
    r_ternary = re.compile('\?')
    if r_ternary.search(code) and not q_ternary.search(code):
        self.add_error(label="TERNARY_OPERATOR")


def check_while_true(self, code):
    statement_parser = Literal("while") + Literal("(") + Literal("true") + Literal(")")
    if len(statement_parser.searchString(code)):
        self.add_error(label="WHILE_TRUE")


def check_non_const_global(self, code):
    inside = Literal("int main")
    if len(inside.searchString(code)):
        self.outside_main = False

    if self.outside_main:
        function = check_if_function(code)
        variables = variables = re.compile("^(?:\w|_)+\s+(?:\w|_|\[|\])+\s*=\s*.+;")
        keywords = re.compile("^\s*(?:using|class|struct)")
        constants = re.compile("^\s*(?:static\s+)?const")
        if not function and variables.search(code) and \
                not keywords.search(code) and \
                not constants.search(code):
            self.add_error(label="NON_CONST_GLOBAL")


def check_main_syntax(self, code):
    # Return value for main is optional in C++11
    parser = Literal("int") + Literal("main") + Literal("(") + SkipTo(Literal(")")) + Literal(")")
    if len(parser.searchString(code)):
        main_prefix = Literal("int") + Literal("main") + Literal("(")
        full_use = Literal("int") + "argc" + "," + Optional("const") + "char" + "*" + "argv" + "[" + "]" + ")"
        # 3 options for main() syntax
        if not len((main_prefix + Literal(")")).searchString(code)) and \
                not len((main_prefix + Literal("void") + Literal(")")).searchString(code)) and \
                not len((main_prefix + full_use).searchString(code)):
            self.add_error(label="MAIN_SYNTAX")

# Make sure identifiers are more than 1 character in length
def check_identifier_length(self, code):
    if re.match(r'^[\s\}\{\};]*$', code): # skip boring lines
        return

    # check for any parameter or variable declaration that is a type followed by 1 or more identifiers
    declaration_check = re.compile(r"(?:^|\s+|\(|\{)(?:class|struct|enum|void|bool|char|short|long|int|float|double|string)[\*&\s]+([\w_][\w\d_]*[\[;,\s\(\)\*\&$]+)+")
    declaration_match = declaration_check.search(code)

    if declaration_match:
        #Find all the single-letter identifiers
        single_letter_ids = re.finditer(r'[\*&\s,]([\w_])[\[;,\s\(\)$]', declaration_match.group(0))
        single_letter_ids = [match.group(1) for match in single_letter_ids]

        if len(single_letter_ids):
            result = ', '.join(single_letter_ids)
            if result == 'i':
                self.add_error(label="IDENTIFIER_I")
            else:
                self.add_error(label="IDENTIFIER_LENGTH", data={"found": str(result)})

def check_first_char(self, code):
    if code.isspace():
        return

    # check if the first char is lower-case alpha or '_'
    lowercase = re.compile("(?:^|\s+)(?:class|struct|enum)\s+(?:[a-z]|_)\w*")
    bad_naming = lowercase.search(code)

    if bad_naming:
        result = bad_naming.group(0).split()
        expected = str(result[1])

        if len(expected) == 1:
            expected = 'A Descriptive Name'
        if (expected and expected[0] == '_'): # Remove leading _ from expected input
            expected = expected[1:]
        self.add_error(label="FIRST_CHAR",
                       data={"keyword": result[0],
                             "style": "capitalized",
                             "expected": expected[0].capitalize() + (expected[1:] if len(expected) > 1 else ''),
                             "found": str(result[1])})
        return

    # Make sure the first letter of non-const variable names are lowercase.
    uppercase = re.compile("(?:^|\s+)(?<!const\s)\s*(?:void|bool|char|short|long|int|float|double|string)\s*[\*\&]*\s*(?:[A-Z]|_)\w+")
    bad_naming = uppercase.search(code)

    if bad_naming:
        result = bad_naming.group(0).split()

        # Create an expected constant name where underscores are converted to camel case
        expected = ''
        var_length = len(result[1])
        cap_next = False;
        for i, ch in enumerate(result[1]):
            if ch == '_':
                cap_next = True;
            elif cap_next:
                expected += ch.upper()
                cap_next = False
            else:
                expected += ch

        if (expected and expected[0] == '_'): # Remove leading _ from expected input
            expected = expected[1:]

        self.add_error(label="FIRST_CHAR",
                       data={"keyword": 'non-constant variable or function',
                             "style": "lowercase",
                             "expected": ((expected[:1].lower() + expected[1:]) if expected else '') if len(expected) > 1 else "a descriptive name",
                             "found": str(result[1])})
        return
    # Make sure const variables are all caps
    if not check_if_function_prototype(code) and not check_if_function(code):
        const_var = re.compile("(?:^|\s+)const\s+(?:void|bool|char|short|long|int|float|double|string)\s*[\*\&]*\s*(?:[\w]|_)\w+")
        const_var = const_var.search(code)
        if const_var:
            const_var = str(const_var.group(0).split()[2])

            # Create an expected constant name where camel case is converted to all caps with underscores
            expected = ''
            var_length = len(const_var)
            for i, ch in enumerate(reversed(const_var)):
                if ch.isupper() and ch != '_' and i < var_length - 1 and i > 0 and const_var[var_length - i - 2] != '_':
                    expected = '_' + ch + expected
                else:
                    expected = ch.upper() + expected

            if (expected and expected[0] == '_'): # Remove leading _ from expected input
                expected = expected[1:]
            if not const_var.isupper():
                self.add_error(label="FIRST_CHAR",
                       data={"keyword": 'constant variable',
                             "style": "uppercase",
                             "expected": expected if len(expected) > 1 else "a descriptive name",
                             "found": const_var})



def check_unnecessary_include(self, code):
    grammar = Literal('#') + Literal('include') + Literal('<') + Word(alphanums)
    try:
        grammar.parseString(code)
        begin = code.find("<")
        end = code.find(">")
        included_library = code[begin + 1:end]
        if included_library not in self.includes:
            self.add_error(label="UNNECESSARY_INCLUDE")
    except ParseException:
        return


def check_local_include(self, code):
    grammar = Literal('#') + Literal('include') + Literal('"') + Word(alphanums)
    try:
        grammar.parseString(code)
        begin = code.find('"')
        included_file = code[begin + 1:]
        end = included_file.find('"')
        included_file = included_file[:end]
        if included_file not in self.includes:
            self.local_includes[self.current_file].append(included_file)
    except ParseException:
        return


def check_for_loop_semicolon_spacing(self, code):
    # Match the semicolons and any whitespace around them.
    for_loop_regex = re.compile(
        r"""
        \s*for\s*\(
            (?P<code1>[^;]*?)

            (?P<semicolon1>\s*;\s*)

            (?P<code2>[^;]*?)

            (?P<semicolon2>\s*;\s*)

            (?P<code3>[^;]*?)
        \)
        """,
        re.VERBOSE
    )
    match = for_loop_regex.search(code)
    if not match:
        return

    self.for_loop_spacing_before = getattr(self, "for_loop_spacing_before", None)
    self.for_loop_spacing_after = getattr(self, "for_loop_spacing_after", None)

    semicolon1 = match.group("semicolon1")
    semicolon2 = match.group("semicolon2")
    code1 = match.group("code1")
    code2 = match.group("code2")
    code3 = match.group("code3")

    def is_spacing_okay(semicolon, before_code, after_code):
        spacing_before = semicolon.startswith(" ")
        spacing_after = semicolon.endswith(" ")

        def check_spacing(convention, actual):
            if convention is None:
                convention = actual

            if convention != actual:
                return convention, False
            else:
                return convention, True

        if before_code or after_code:
            if before_code:
                self.for_loop_spacing_before, result = check_spacing(
                    self.for_loop_spacing_before,
                    spacing_before
                )
                if not result:
                    return False
            if after_code:
                self.for_loop_spacing_after, result = check_spacing(
                    self.for_loop_spacing_after,
                    spacing_after
                )
                if not result:
                    return False
        else:
            # This is a plain semicolon, so we can't infer anything about the
            # spacing convention.
            pass
        return True

    if not (
                is_spacing_okay(semicolon1, code1, code2)
            and is_spacing_okay(semicolon2, code2, code3)
    ):
        self.add_error(
            label="FOR_LOOP_SEMICOLON_SPACING",
            data={"line": self.current_line_num}
        )

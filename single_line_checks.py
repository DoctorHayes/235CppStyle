from style_grader_functions import check_if_function, check_if_function_prototype
from pyparsing import Literal, Word, Optional, ParseException, Group, SkipTo, alphanums, LineStart, srange
import re





def check_int_for_bool(self, code):
    if check_if_function(code):
        function_regex = re.compile(r"^\s*(\w+)\s+(\w+)")
        match = function_regex.search(code)
        if match:
            self.current_function = (match.group(1), match.group(2))
    current_function = getattr(self, "current_function", ("", ""))

    return_regex = re.compile(r"\s*return\s+(\w+)")
    match = return_regex.search(code)
    if match and match.group(1).isdigit() and current_function[0] == "bool":
        self.add_error(label="INT_FOR_BOOL")

def check_equals_true(self, code):
    keyword = Literal("true") | Literal("false")
    statement_parser = Group("==" + keyword) | Group(keyword + "==")
    if len(statement_parser.search_string(code)):
        self.add_error(label="EQUALS_TRUE")

def check_float_type(self, code):
    # ToDo: Ignores #include<cfloat>, but should find static_cast<float>().
    floatPattern = re.compile(r'(?:^|[\s,;\(])float[\s\*&]')
    for match in floatPattern.finditer(code):
        self.add_error(label="FLOAT_TYPE", column=match.span()[0]+1)

def check_goto(self, code):
    # Hacky but gets the job done for now - has holes though
    q_goto = re.compile(r'\".*goto.*\"')
    r_goto = re.compile(r'(?:\s+|^|\{)goto\s+')
    if r_goto.search(code) and not q_goto.search(code):
        self.add_error(label="GOTO")


def check_define_statement(self, code):
    # Skip header files for this check
    if self.allow_define_in_header and re.search(r'\.hpp$', self.current_file):
        return

    q_define = re.compile(r'\".*(?:\s+|^)#\s*define\s+.*\"')
    r_define = re.compile(r'(?:\s+|^)#\s*define\s+')
    if r_define.search(code) and not q_define.search(code):
        words = code.split()
        # They shouldn't be using __MY_HEADER_H__ because __-names are
        # reserved, but we'll allow it anyways.
        legal_endings = ["_H", "_H__"]
        if not any(words[-1].endswith(i) for i in legal_endings):
            self.add_error(label="DEFINE_STATEMENT")


def check_continue(self, code):
    # Hacky but gets the job done for now - has holes though
    q_continue = re.compile(r'\".*continue.*\"')
    r_continue = re.compile(r'(?:\s+|^|\{)continue\s*;')
    if r_continue.search(code) and not q_continue.search(code):
        self.add_error(label="CONTINUE_STATEMENT")


def check_ternary_operator(self, code):
    q_ternary = re.compile(r'\".*\?.*\"')
    r_ternary = re.compile(r'\?')
    if r_ternary.search(code) and not q_ternary.search(code):
        self.add_error(label="TERNARY_OPERATOR")


def check_while_true(self, code):
    keyword = Literal("true") | Literal("1")

    statement_parser = Literal("while") + Literal("(") + keyword + Literal(")")
    if len(statement_parser.search_string(code)):
        self.add_error(label="WHILE_TRUE")


def check_non_const_global(self, code):
    inside = Literal("int main")
    if len(inside.search_string(code)):
        self.outside_main = False

    elif self.outside_main:
        function = check_if_function(code)
        variables = variables = re.compile(r"^(?:\w|_)+\s+(?:\w|_|\[|\])+\s*=\s*.+;")
        keywords = re.compile(r"^\s*(?:using|class|struct)")
        constants = re.compile(r"^\s*(?:static\s+)?(?:const|constexpr)")
        if not function and variables.search(code) and \
                not keywords.search(code) and \
                not constants.search(code):
            self.add_error(label="NON_CONST_GLOBAL")


def check_main_syntax(self, code):
    # Return value for main is optional in C++11
    parser = Literal("int") + Literal("main") + Literal("(") + SkipTo(Literal(")")) + Literal(")")
    if len(parser.search_string(code)):
        main_prefix = Literal("int") + Literal("main") + Literal("(")
        full_use = Literal("int") + "argc" + "," + Optional(Literal("const") | Literal("constexpr")) + "char" + "*" + "argv" + "[" + "]" + ")"
        # 3 options for main() syntax
        if not len((main_prefix + Literal(")")).search_string(code)) and \
                not len((main_prefix + Literal("void") + Literal(")")).search_string(code)) and \
                not len((main_prefix + full_use).search_string(code)):
            self.add_error(label="MAIN_SYNTAX")

# Make sure identifiers are more than 1 character in length
def check_identifier_length(self, code):
    if re.match(r'^[\s\}\{\};]*$', code): # skip boring lines
        return

    # check for any parameter or variable declaration that is a type followed by 1 or more identifiers
    declaration_check = re.compile(r'(?:^|\s+|\(|\{)(?:class|struct|enum|void|bool|char|short|long|int|float|double|string|std::string|string::size_type|std::string::size_type|auto)[\*&\s]+([\w_][\w_]*[\[;,\s\(\)\*\&$]+)+')
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


def _to_pascal_case(identifier: str) -> str:
    # Split on underscores first
    chunks = re.split(r'_+', identifier.strip())
    words = []

    for chunk in chunks:
        if not chunk:
            continue

        # Extract:
        # - sequences of capitals not followed by a lowercase (acronyms)
        # - normal words (optionally followed by lowercase runs)
        #
        # Examples:
        #   "HTTPServer" -> ["HTTP", "Server"]
        #   "myVarName"  -> ["my", "Var", "Name"]
        #   "MyVarName"  -> ["My", "Var", "Name"]
        tokens = re.findall(r'[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+', chunk)
        words.extend(tokens)

    # Capitalize each extracted word for PascalCase
    # If you want to preserve full acronyms like "HTTP", keep them uppercase.
    def cap(word: str) -> str:
        return word if word.isupper() else word.capitalize()

    return ''.join(cap(w) for w in words)

def _to_camel_case(identifier: str) -> str:
    """Convert identifier to camelCase (variableName, functionName)."""
    if not identifier:
        return identifier
    
    # Remove leading underscores, then convert
    clean_id = identifier.lstrip('_')
    if not clean_id:
        return identifier
    
    # Replace underscores with spaces, capitalize each word except first, remove spaces
    chunks = re.split(r'_+', clean_id.strip())
    words = []

    for chunk in chunks:
        if not chunk:
            continue

        # Extract:
        # - sequences of capitals not followed by a lowercase (acronyms)
        # - normal words (optionally followed by lowercase runs)
        #
        # Examples:
        #   "HTTPServer" -> ["HTTP", "Server"]
        #   "myVarName"  -> ["my", "Var", "Name"]
        #   "MyVarName"  -> ["My", "Var", "Name"]
        tokens = re.findall(r'[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+', chunk)
        words.extend(tokens)

    first = words[0].lower()
    rest = ''.join(word.capitalize() for word in words[1:] if word)
    return first + rest

def _to_upper_snake_case(identifier: str) -> str:
    """Convert identifier to UPPER_SNAKE_CASE (CONSTANT_NAME, MAX_VALUE)."""

    _TOKEN_RE = re.compile(r'[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+')

    if not identifier:
        return identifier

    # Remove prior leading/trailing underscores (strip, then re-check)
    clean_id = identifier.strip('_')
    if not clean_id:
        return identifier

    # Identifiers won't have dashes/spaces, but there may be repeated/mixed underscores.
    chunks = re.split(r'_+', clean_id)

    tokens = []
    for chunk in chunks:
        if not chunk:
            continue
        tokens.extend(_TOKEN_RE.findall(chunk))

    return '_'.join(t.upper() for t in tokens)

def check_identifier_case(self, code):
    if code.isspace():
        return

    # ===== Check class/struct/enum names - should be PascalCase =====
    type_pattern = re.compile(r"(?:^|\s+)(?:class|struct|enum)\s+([\w_]+)")
    type_match = type_pattern.search(code)
    
    if type_match:
        found_name = type_match.group(1)
        keyword = type_match.group(0).split()[-2]  # 'class', 'struct', or 'enum'
        
        # Check if not in PascalCase (should start with uppercase letter)
        # Flag errors for: lowercase start or underscore start
        if found_name:
            if found_name[0].islower() or found_name[0] == '_':
                expected_name = _to_pascal_case(found_name)
                self.add_error(
                    label="IDENTIFIER_CASE",
                    data={
                        "type": keyword,
                        "style": "PascalCase (ClassName, StructName)",
                        "expected": expected_name if len(expected_name) > 1 else "A Descriptive Name",
                        "found": found_name
                    }
                )
            return

    # ===== Check non-const variables and parameters =====
    # Skip if line contains 'const' or 'constexpr'
    is_const = re.search(r'\b(?:const|constexpr)\b', code)
    
    if not is_const:
        # Pattern for type declarations (variables/parameters)
        var_pattern = re.compile(
            r'(?:^|\s+)\s*(?:void|bool|char|short|long|int|float|double|string|std::string|auto|ifstream|ofstream)'
            r'[\*\&\s]+(?:[\w_]+\:\:)*([\w_]+)\s*[,\[\(\)\{;=]'
        )
        var_match = var_pattern.search(code)
        
        if var_match:
            found_name = var_match.group(1)
            
            # Check if not in camelCase (should start lowercase and not have underscores)
            if found_name and (found_name[0].isupper() or '_' in found_name):
                expected_name = _to_camel_case(found_name)
                self.add_error(
                    label="IDENTIFIER_CASE",
                    data={
                        "type": "non-constant variable or parameter",
                        "style": "camelCase (variableName, paramName)",
                        "expected": expected_name if len(expected_name) > 1 else "a descriptive name",
                        "found": found_name
                    }
                )
            return

    # ===== Check const variables - should be UPPER_SNAKE_CASE =====
    if not check_if_function_prototype(code) and not check_if_function(code):
        # Pattern for const variable declarations
        const_pattern = re.compile(
            r"(?:^|\s+)(?:const|constexpr)\s+"
            r"(?:(?:signed|unsigned)\s+)?(?:void|bool|char|short|long|int|float|double|string|std::string|auto)[\*\&\s]*\s*"
            r"([\w_]+)"
        )
        const_match = const_pattern.search(code)
        
        if const_match:
            found_name = const_match.group(1)
            
            # Check if not in UPPER_SNAKE_CASE
            if found_name and not found_name.isupper():
                expected_name = _to_upper_snake_case(found_name)
                self.add_error(
                    label="IDENTIFIER_CASE",
                    data={
                        "type": "constant variable",
                        "style": "UPPER_SNAKE_CASE (CONSTANT_NAME, MAX_VALUE)",
                        "expected": expected_name if len(expected_name) > 1 else "A Descriptive Name",
                        "found": found_name
                    }
                )



def check_unnecessary_include(self, code):
    grammar = Literal('#') + Literal('include') + Literal('<') + Word(alphanums + '.' + '_') + Literal('>')
    try:
        grammar.parse_string(code)
        begin = code.find("<")
        end = code.find(">")
        included_library = code[begin + 1:end]
        if included_library not in self.includes:
            self.add_error(label="UNNECESSARY_INCLUDE", data={"library": included_library})
    except ParseException:
        return


def check_local_include(self, code):
    grammar = Literal('#') + Literal('include') + Literal('"') + Word(alphanums)
    try:
        grammar.parse_string(code)
        begin = code.find('"')
        included_file = code[begin + 1:]
        end = included_file.find('"')
        included_file = included_file[:end]
        if included_file not in self.includes:
            self.local_includes[self.current_file].append(included_file)
    except ParseException:
        return

def check_isolated_semicolon(self, code):
    isolated = re.compile(r'\s+;')
    for match in isolated.finditer(code):
        self.add_error(label="ISOLATED_SEMICOLON",column=match.span()[0]+1)

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

def check_system_call(self, code):
    # Check for system calls.
    sys_call = re.search(r"(?:^|\s+|\}|\{|;)system\s*\(\s*\"", code)
    if sys_call:
        self.add_error(label="SYSTEM_CALL")

def check_const_literal(self, code):
    if 'constexpr' in code:
        return
    match = re.search(r'\bconst\s+([a-zA-Z0-9_:\s<>*&]+?)\s+([a-zA-Z0-9_]+)\s*=\s*(.*?)\s*;', code)
    if match:
        val = match.group(3).strip()
        is_literal = False
        if val in ['true', 'false']:
            is_literal = True
        elif val.startswith('"') and val.endswith('"'):
            is_literal = True
        elif val.startswith("'") and val.endswith("'"):
            is_literal = True
        else:
            num_re = r'^-?(?:0x[\da-fA-F]+|0b[01]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)[uUlLfFzZ]*$'
            if re.match(num_re, val):
                is_literal = True
        
        if is_literal:
            self.add_error(label="CONST_LITERAL")
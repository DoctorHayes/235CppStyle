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


def _get_function_name(code: str):
    if not (check_if_function(code) or check_if_function_prototype(code)):
        return None

    match = re.search(r'([A-Za-z_][A-Za-z0-9_]*)\s*\(', code)
    if not match:
        return None

    name = match.group(1)
    if name in {'if', 'for', 'while', 'switch', 'return', 'main'}:
        return None

    return name


def check_identifier_case(self, code):
    if code.isspace():
        return

    # -------------------------------------------------------------------------
    # Statements that are definitely not variable declarations
    # -------------------------------------------------------------------------

    if re.match(
        r'^\s*(?:return|typedef|using|typename|sizeof|alignof|alignas|'
        r'decltype|static_assert|consteval|constinit)\b',
        code,
        re.IGNORECASE
    ):
        return

    # Statements that start with # are preprocessor directives, not declarations.
    if re.match(
        r'^\s*#',
        code
    ):
        return

    # Simple assignment to an existing variable.
    if re.match(
        r'^\s*[A-Za-z_][A-Za-z0-9_]*\s*=(?!=)',
        code
    ):
        return

    # -------------------------------------------------------------------------
    # Class/struct/enum/namespace names - PascalCase
    # -------------------------------------------------------------------------

    identifier = r'[A-Za-z_][A-Za-z0-9_]*'

    type_match = re.search(
        rf'(?:^|\s+)(class|struct|enum|namespace)\s+({identifier})',
        code
    )

    if type_match:
        keyword = type_match.group(1)
        found_name = type_match.group(2)

        if found_name[0].islower() or found_name[0] == '_':
            expected_name = _to_pascal_case(found_name)

            self.add_error(
                label="IDENTIFIER_CASE",
                data={
                    "type": keyword,
                    "style": "PascalCase (ClassName, StructName)",
                    "expected": (
                        expected_name
                        if len(expected_name) > 1
                        else "A Descriptive Name"
                    ),
                    "found": found_name
                }
            )

        return

    # -------------------------------------------------------------------------
    # Function names - camelCase
    # -------------------------------------------------------------------------

    function_name = _get_function_name(code)

    if function_name and (
        function_name[0].isupper() or '_' in function_name
    ):
        expected_name = _to_camel_case(function_name)

        self.add_error(
            label="IDENTIFIER_CASE",
            data={
                "type": "function",
                "style": "camelCase (functionName, methodName)",
                "expected": (
                    expected_name
                    if len(expected_name) > 1
                    else "a descriptive name"
                ),
                "found": function_name
            }
        )

    # -------------------------------------------------------------------------
    # Variable declarations
    #
    # We deliberately recognize only the declaration forms needed by the
    # course/style checker:
    #
    #     int value;
    #     int value = 10;
    #     int foo, bar;
    #     const int VALUE = 10;
    #     int const VALUE = 10;
    #     int *ptr;
    #     int * const PTR;
    #     const int *ptr;
    #     int &ref;
    #     std::string name;
    #     std::vector<int> values;
    #
    # The critical requirement is that a declaration contains:
    #
    #     TYPE [declarator operators] VARIABLE
    #
    # The variable identifier cannot simply be another identifier appearing
    # somewhere later in the expression.
    # -------------------------------------------------------------------------

    declarations = _find_cpp_declarations(self, code)

    for declaration in declarations:
        found_name = declaration["name"]

        # Explicit API exception: the conventional `argv` parameter on `main()`
        # is part of the declaration syntax of the standard entry point and must
        # never be subject to identifier-case validation.
        if found_name == 'argv' and re.search(r'\bint\s+main\s*\(', code, re.IGNORECASE):
            continue

        if declaration["is_const"]:
            # Constant variables must use UPPER_SNAKE_CASE.
            if found_name != found_name.upper():
                expected_name = _to_upper_snake_case(found_name)

                self.add_error(
                    label="IDENTIFIER_CASE",
                    data={
                        "type": "constant variable",
                        "style": "UPPER_SNAKE_CASE (CONSTANT_NAME, MAX_VALUE)",
                        "expected": (
                            expected_name
                            if len(expected_name) > 1
                            else "A Descriptive Name"
                        ),
                        "found": found_name
                    }
                )

        else:
            # Non-constant variables and parameters use camelCase.
            if found_name[0].isupper() or '_' in found_name:
                expected_name = _to_camel_case(found_name)

                self.add_error(
                    label="IDENTIFIER_CASE",
                    data={
                        "type": "non-constant variable or parameter",
                        "style": "camelCase (variableName, paramName)",
                        "expected": (
                            expected_name
                            if len(expected_name) > 1
                            else "a descriptive name"
                        ),
                        "found": found_name
                    }
                )

def _find_cpp_declarations(self, code):
    """Find simple C++ variable declarations and function parameters."""

    identifier = r'[A-Za-z_][A-Za-z0-9_]*'

    # -------------------------------------------------------------------------
    # C++ type names
    # -------------------------------------------------------------------------

    builtin_type = (
        r'(?:'
        r'bool|char|char8_t|char16_t|char32_t|wchar_t|'
        r'short|int|long|float|double|void|'
        r'signed|unsigned'
        r')'
    )

    qualified_type = (
        rf'(?:{identifier}\s*::\s*)*'
        rf'{identifier}'
    )

    template_type = (
        rf'{qualified_type}'
        rf'\s*<[^<>()|&=;]+>'
    )

    type_name = (
        rf'(?:{template_type}|{builtin_type}|{qualified_type})'
    )

    # -------------------------------------------------------------------------
    # Declaration specifiers.
    #
    # constinit is a declaration specifier, but does NOT make the variable
    # constant.
    #
    # consteval is intentionally excluded because it applies to functions.
    # -------------------------------------------------------------------------

    declaration_specifier = (
        r'(?:'
        r'const|constexpr|constinit|static|inline|'
        r'thread_local|volatile|mutable'
        r')'
    )

    declaration_prefix = (
        rf'(?:{declaration_specifier}\s+)*'
        rf'(?:unsigned\s+|signed\s+|short\s+|long\s+)*'
        rf'{type_name}'
    )

    # -------------------------------------------------------------------------
    # A complete declaration prefix + first declarator.
    #
    # IMPORTANT:
    #
    # The * and & are included here rather than being handled by a separate
    # lookahead. This correctly handles all of:
    #
    #     int* ptr
    #     int *ptr
    #     int * ptr
    #     int& ref
    #     int &ref
    #     const int* ptr
    #     int* const ptr
    #
    # There must ultimately be an identifier after the type/declarator
    # operators.
    # -------------------------------------------------------------------------

    first_declarator_pattern = re.compile(
        rf'''
        (?<![A-Za-z0-9_])

        (?P<prefix>
            {declaration_prefix}
        )

        # The type name must end at a word boundary so that "qualified_type"
        # cannot greedily consume part of the variable name as the type.
        \b

        (?P<operators>
            (?:
                \s*
                (?:[*&])
                \s*
            )*
            (?:
                const\s*
            )?
        )

        # When there are no pointer/reference operators the prefix and name
        # must still be separated by whitespace.
        (?(operators)|\ )\s*

        (?P<name>
            {identifier}
        )

        (?=
            \s*
            (?:
                = |
                \[ |
                \{{ |
                , |
                ; |
                \) |
                $
            )
        )
        ''',
        re.VERBOSE
    )

    declarations = []

    for match in first_declarator_pattern.finditer(code):
        prefix = match.group("prefix")
        operators = match.group("operators")
        name = match.group("name")

        start = match.start()
        end = match.end()

        # ---------------------------------------------------------------------
        # Don't recognize a declaration embedded in an expression.
        #
        # For example:
        #
        #     difficulty < 1 || difficulty > MAX
        #
        # must not be interpreted as:
        #
        #     difficulty < 1
        #
        # being a declaration.
        # ---------------------------------------------------------------------

        before = code[:start].rstrip()

        if before and before[-1] in '+-*/%<>=!&|?:':
            continue

        # ---------------------------------------------------------------------
        # Determine whether this is a function parameter.
        #
        # Top-level `const` on a parameter (e.g., `void f(const int x)`) is an
        # implementation detail and does NOT impose UPPER_SNAKE_CASE on the
        # parameter name.  We detect a parameter context by checking whether the
        # text before this match ends with `(` or `,`.
        # ---------------------------------------------------------------------

        is_parameter = bool(
            re.search(r'[,(]\s*$', before)
        )

        # ---------------------------------------------------------------------
        # The conventional `argv` parameter of `main()` is a special standard
        #-library convention; it is exempt from identifier-case checking.
        # Encourage the parser to understand that without ever forwarding it to
        # the reporting loop as a candidate variable name.
        # ---------------------------------------------------------------------

        is_main_argv = (
            name == 'argv'
            and is_parameter
            and re.search(r'\bint\s+main\s*\(', code, re.IGNORECASE)
        )

        if is_main_argv:
            continue

        # ---------------------------------------------------------------------
        # Determine whether the declaration itself contains constexpr/const.
        #
        # For naming purposes we treat any declaration that has `const` anywhere
        # in its prefix (including `const T*` and `const T&`) as a constant
        # that requires UPPER_SNAKE_CASE — UNLESS it is a function parameter,
        # in which case the `const` is just an implementation detail.
        # ---------------------------------------------------------------------

        is_constexpr = bool(
            re.search(r'\bconstexpr\b', prefix)
        )

        prefix_const = bool(
            re.search(r'\bconst\b', prefix)
        )

        declarator_const = bool(
            re.search(r'\bconst\b', operators)
        )

        # constinit does NOT make the variable const.
        declaration_is_constant = is_constexpr

        is_const = (
            # not is_parameter
            # and (
                declaration_is_constant
                or declarator_const
                or prefix_const
            # )
        )

        declarations.append({
            "name": name,
            "is_const": is_const,
            "is_parameter": is_parameter
        })

        # ---------------------------------------------------------------------
        # Handle additional comma-separated declarators.
        #
        # Examples:
        #
        #     int foo, BAR;
        #     int *foo, *BAR;
        #     const int VALUE, OTHER_VALUE;
        #
        # Start immediately after the first declarator and look for:
        #
        #     , [* & const ...] identifier
        #
        # ---------------------------------------------------------------------

        remainder = code[end:]

        comma_pattern = re.compile(
            rf'''
            ^\s*,\s*

            (?P<operators>
                (?:
                    [*&]\s*
                )*
                (?:
                    const\s*
                )?
            )

            (?P<name>{identifier})

            (?=
                \s*
                (?:
                    = |
                    \[ |
                    , |
                    ; |
                    \) |
                    $
                )
            )
            ''',
            re.VERBOSE
        )

        while True:
            comma_match = comma_pattern.match(remainder)

            if not comma_match:
                break

            operators = comma_match.group("operators")
            name = comma_match.group("name")

            has_pointer_or_reference = bool(
                re.search(r'[*&]', operators)
            )

            declarator_const = bool(
                re.search(r'\bconst\b', operators)
            )

            is_const = (
                declaration_is_constant
                or declarator_const
                or (
                    prefix_const
                    and not has_pointer_or_reference
                )
            )

            declarations.append({
                "name": name,
                "is_const": is_const,
                "is_parameter": is_parameter
            })

            remainder = remainder[comma_match.end():]

    return declarations

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
    match = re.search(r'\bconst\s+([a-zA-Z0-9_:\s<>*&]+?)\s+([a-zA-Z0-9_]+)\s*(?:=\s*\{?|\{)\s*(.*?)\s*\}?\s*;', code)
    if match:
        # constexpr std::string cannot be initialized.
        type_str = match.group(1).strip()
        if type_str in ['string', 'std::string']:
            return
            
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

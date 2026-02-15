import re

# Recursive function for compound statements (blocks, functions, etc.)
def validate_statement_indentation(self, code_lines, line_index, indent_min = 0, indent_max = 0, enclosure_stack = None, isNewStatement = True):
    if enclosure_stack is None:
        enclosure_stack = []

    if line_index >= code_lines.num_lines:
        return line_index # No more lines to check

    line_index, indent_min_new, indent_max_new, expected = indent_line_check(self, code_lines, line_index, indent_min, indent_max, isNewStatement, enclosure_stack)

    if line_index >= code_lines.num_lines:
        return line_index # No more lines to check


    # Check for unclosed () and {}
    start_stack_len = len(enclosure_stack)

    # Check if this is an enum declaration
    prev_line = code_lines.elided[line_index - 1] if line_index > 0 else None
    preceding_line_is_enum = is_enum_declaration(code_lines.elided[line_index], prev_line)

    increase = enclosure_nesting(code_lines.elided[line_index], enclosure_stack, expected, preceding_line_is_enum)

    # Setup for next line based on how this one ends
    isNextNewStatement = is_complete_expression(line_index, code_lines, isNewStatement, enclosure_stack)

    if (not isNewStatement) or line_index >= code_lines.num_lines: # Statement start on previous line
        return line_index # Let the previous recursive call handle the next line.


    # compound statement
    # Go through each line until we are back to where we left off.
    while increase >= 0 and line_index + 1 < code_lines.num_lines:

        if is_switch_case(code_lines.elided[line_index]):
            line_index = validate_statement_indentation(self, code_lines, line_index + 1, expected + 1, expected + 1, enclosure_stack, True)
        elif is_access_modifiers(code_lines.elided[line_index]):
            line_index = validate_statement_indentation(self, code_lines, line_index + 1, expected + 1, expected + 1, enclosure_stack, True)
        elif increase == 0:
            line_index = validate_statement_indentation(self, code_lines, line_index + 1, indent_min + (not isNextNewStatement), indent_min + (not isNextNewStatement), enclosure_stack, isNextNewStatement)
        else: # going 1 more level deep
            line_index = validate_statement_indentation(self, code_lines, line_index + 1, expected + 1, expected + increase, enclosure_stack, isNextNewStatement)

        if line_index + 1 >= code_lines.num_lines:
            return line_index

        increase = len(enclosure_stack) - start_stack_len
        isNextNewStatement = is_complete_expression(line_index, code_lines, isNextNewStatement, enclosure_stack)


    if increase < 0:
        return line_index
    return validate_statement_indentation(self, code_lines, line_index + 1, indent_min, indent_min, enclosure_stack, True)


def enclosure_nesting(line_elided, enclosure_stack = None, current_indent = 0, previous_line_is_enum = False):
    """Track nesting level changes due to braces.
    
    Args:
        line_elided: The line content (with strings/comments removed)
        enclosure_stack: Stack tracking open braces and their properties
        current_indent: Current indentation level
        previous_line_is_enum: Whether the previous line was an enum declaration
        
    Returns:
        Change in nesting level (positive for opening braces, negative for closing)
    """
    if enclosure_stack is None:
        enclosure_stack = []
    
    start_stack_len = len(enclosure_stack)
    line_elided = line_elided.strip()
    
    for i, c in enumerate(line_elided):
        if c in list('{'):
            # Check if this brace belongs to an enum
            prefix = line_elided[:i]
            is_enum = previous_line_is_enum or is_enum_declaration(prefix)
            
            enclosure_stack.append({'indent': current_indent, 'is_enum': is_enum})
        elif c in list('}') and len(enclosure_stack):
            enclosure_stack.pop()

    return len(enclosure_stack) - start_stack_len

def is_complete_expression(line_index, code_lines, isPreviousStatementNew, enclosure_stack=None):
    """Check if a line completes an expression/statement.
    
    Args:
        line_index: Index of the line to check
        code_lines: CleansedLines object containing the file content
        isPreviousStatementNew: Whether the previous statement was complete
        enclosure_stack: Stack tracking open braces and their properties
        
    Returns:
        True if the line ends with a statement terminator
    """
    if enclosure_stack is None:
        enclosure_stack = []
        
    if line_index >= code_lines.num_lines:
        return isPreviousStatementNew

    just_code = code_lines.elided[line_index].strip()

    if not just_code:
        return isPreviousStatementNew
    else:
        terminators = list(';{}')
        # In enums, commas terminate declarations
        if enclosure_stack and enclosure_stack[-1].get('is_enum'):
            terminators.append(',')
        return (just_code and just_code[-1] in terminators)

def count_whitespace(text):
    """Count spaces and tabs in a string.
    
    Args:
        text: String to analyze for whitespace
        
    Returns:
        Dictionary with 'space' and 'tab' counts
    """
    counts = {'space': 0, 'tab': 0}
    for ch in text:
        if ch == ' ':
            counts['space'] += 1
        elif ch == '\t':
            counts['tab'] += 1
    return counts

def calculate_indent_level(found_whitespace, tab_size):
    """Calculate indentation level from whitespace counts.
    
    Args:
        found_whitespace: Dictionary with 'space' and 'tab' counts
        tab_size: Size of a tab (1 for hard tabs, 4+ for spaces)
        
    Returns:
        Tuple of (indent_level, tab_type_description, other_whitespace_type)
    """
    if tab_size == 1:
        found_level = found_whitespace['tab']
        tab_type = ' tabs'
        other_type = 'space'
    else:
        found_level = found_whitespace['space'] / tab_size
        tab_type = ' spaces'
        other_type = 'tab'
    
    return found_level, tab_type, other_type

def format_whitespace_message(found_whitespace):
    """Format whitespace counts into a human-readable message.
    
    Args:
        found_whitespace: Dictionary with 'space' and 'tab' counts
        
    Returns:
        String describing the whitespace found
    """
    if found_whitespace['tab'] > 0 and found_whitespace['space'] > 0:
        return str(found_whitespace['tab']) + ' tabs and ' + str(found_whitespace['space']) + ' spaces'
    elif found_whitespace['tab'] > 0:
        return str(found_whitespace['tab']) + ' tabs'
    else:
        return str(found_whitespace['space']) + ' spaces'

def check_indent(style_rubric, line_num, min_level, max_level, found_whitespace, tab_size):
    """Check if indentation is in acceptable range and report errors.
    
    Args:
        style_rubric: StyleRubric instance for error reporting
        line_num: Line number being checked (0-indexed)
        min_level: Minimum acceptable indentation level
        max_level: Maximum acceptable indentation level
        found_whitespace: Dictionary with 'space' and 'tab' counts
        tab_size: Size of a tab (1 for hard tabs, 4+ for spaces)
        
    Returns:
        Expected indentation level (thresholded to min/max range)
    """
    found_level, tab_type, other_type = calculate_indent_level(found_whitespace, tab_size)
    
    # Determine expected level based on found vs. min/max
    if found_level < min_level:
        expected = min_level
    elif found_level > max_level:
        expected = max_level
    else:
        expected = int(found_level)
    
    # Report error if indentation is out of range or mixing tabs/spaces
    if found_level < min_level or found_level > max_level or found_whitespace[other_type] > 0:
        found_msg = format_whitespace_message(found_whitespace)
        style_rubric.add_error(
            label="BLOCK_INDENTATION",
            line=line_num + 1,
            data={'expected': str(min_level * tab_size) + tab_type, 'found': found_msg}
        )
    
    return expected

def indent_line_check(self, code_lines, line_index, indent_min = 0, indent_max = 0, isNewStatement = True, enclosure_stack = None):
    """Check indentation for a single line.
    
    Args:
        self: StyleRubric instance for error reporting
        code_lines: CleansedLines object containing the file content
        line_index: Index of the line to check
        indent_min: Minimum acceptable indentation level
        indent_max: Maximum acceptable indentation level
        isNewStatement: Whether this line starts a new statement
        enclosure_stack: Stack tracking open braces and their properties
        
    Returns:
        Tuple of (line_index, indent_min, indent_max, expected_indent_level)
    """
    if enclosure_stack is None:
        enclosure_stack = []
        
    tab_size = self.current_file_indentation

    if line_index >= code_lines.num_lines:
        return line_index, 0, 0, 0
    leading_whitespace = re.match(r'^(\t*|\s+)\S', code_lines.raw_lines[line_index])
    indent_len = count_whitespace(leading_whitespace.group() if leading_whitespace else '')
    
    #if not isNewStatement:
    #    indent_min = indent_max = indent_min + 1

    if not leading_whitespace or code_lines.raw_lines[line_index] == '/**/': # blank line (also raw_lines are not truly raw for multi-line comments)
        # Go to next line
        return indent_line_check(self, code_lines, line_index + 1, indent_min, indent_max, isNewStatement, enclosure_stack)

    # Check preprocessor directives
    elif re.match(r'\s*#', code_lines.raw_lines[line_index]):
        check_indent(self, line_index, 0, 0, indent_len, tab_size)
        return indent_line_check(self, code_lines, line_index + 1, indent_min, indent_max, isNewStatement, enclosure_stack)

    # Check if line starts with a single-line comment
    elif re.match(r'\s*//', code_lines.raw_lines[line_index]):
        check_indent(self, line_index, indent_min, indent_max, indent_len, tab_size)
        return indent_line_check(self, code_lines, line_index + 1, indent_min, indent_max, isNewStatement, enclosure_stack)

    # Check for multi-line comment
    elif re.match(r'\s*/\*', code_lines.raw_lines[line_index]):
        check_indent(self, line_index, indent_min, indent_max, indent_len, tab_size)

        # Go through comment lines
        while code_lines.raw_lines[line_index].find('*/') < 0 and line_index + 1 < code_lines.num_lines:
            line_index += 1
            indent_len = count_whitespace(re.match(r'^(\t*|\s+)', code_lines.raw_lines[line_index]).group() if re.match(r'^(\t*|\s+)', code_lines.raw_lines[line_index]) else '')
            check_indent(self, line_index, indent_min, indent_max, indent_len, tab_size)

        return indent_line_check(self, code_lines, line_index + 1, indent_min, indent_max, isNewStatement, enclosure_stack)

    # Check if ending a multi-line block
    elif re.match(r'\s*\}', code_lines.elided[line_index]):
        indent_min = enclosure_stack[-1]['indent'] if enclosure_stack else indent_min - 1
        #if not isNewStatement:
        #    indent_min -= 1 # Obviously this is the end of the statement
        indent_max = indent_min

    # Check if current line is starting a multi-line block
    elif not isNewStatement and re.match(r'\s*\{[^\}]*$', code_lines.elided[line_index]):
        indent_min -= 1
        indent_max = indent_min

    # Check for labels and public, private, protected
    elif is_access_modifiers(code_lines.elided[line_index]):
        indent_min = 0
        indent_max = 1

    # Check for switch cases
    elif is_switch_case(code_lines.elided[line_index]):
        if enclosure_stack:
            if 'case_indent' in enclosure_stack[-1]:
                indent_min = indent_max = enclosure_stack[-1]['case_indent']
            else:
                indent_min = enclosure_stack[-1]['indent']
                indent_max = indent_min + 1
        else:
            indent_min -= 1
            indent_max = indent_min + 1


    if (indent_min < 0): # If this happens, clearly it is not right
        indent_min = 0
    if indent_max < indent_min:
        index_max = indent_min

    # Check current line
    expected = check_indent(self, line_index, indent_min, indent_max, indent_len, tab_size)

    if enclosure_stack and is_switch_case(code_lines.elided[line_index]):
        enclosure_stack[-1]['case_indent'] = expected

    return line_index, indent_min, indent_max, expected

def is_access_modifiers(code_line):
    return re.match(r'\s*(public|private|protected)\s*:', code_line)

def is_switch_case(code_line):
    return re.match(r'\s*(case\s+|default\s*:)', code_line)

def is_enum_declaration(current_line, previous_line=None):
    """Check if we're entering an enum block.
    
    Args:
        current_line: The current line to check for enum keyword before brace
        previous_line: The previous line to check for enum declaration
        
    Returns:
        True if this appears to be an enum declaration, False otherwise
    """
    # Check if previous line suggests enum (e.g. "enum Foo")
    if previous_line and re.search(r'\benum\b', previous_line) and '{' not in previous_line:
        return True
    
    # Check content before brace on current line
    if re.search(r'\benum\b', current_line):
        return True
        
    return False

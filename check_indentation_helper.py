import re

# Recursive function for compound statements (blocks, functions, etc.)
def validate_statement_indentation(self, code_lines, line_index, indent_min = 0, indent_max = 0, enclosure_stack = [], isNewStatement = True):

    if line_index >= code_lines.num_lines:
        return line_index # No more lines to check

    line_index, indent_min_new, indent_max_new, expected = indent_line_check(self, code_lines, line_index, indent_min, indent_max, isNewStatement, enclosure_stack)

    if line_index >= code_lines.num_lines:
        return line_index # No more lines to check


    # Check for unclosed () and {}
    start_stack_len = len(enclosure_stack)
    increase = enclosure_nesting(code_lines.elided[line_index], enclosure_stack, expected)

    # Setup for next line based on how this one ends
    isNextNewStatement = is_complete_expression(line_index, code_lines, isNewStatement)

    if (not isNewStatement) or line_index >= code_lines.num_lines: # Statement start on previous line
        return line_index # Let the previous recursive call handle the next line.


    # compound statement
    # Go through each line until we are back to where we left off.
    while increase >= 0 and line_index + 1 < code_lines.num_lines:
        #if line_index in [13]:


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
        isNextNewStatement = is_complete_expression(line_index, code_lines, isNextNewStatement)


    #if isMultiLine:
    #    expected -= 1

    # Check until end of statement (line ends with ';'' or '}'
    #just_code = code_lines.elided[line_index].strip()
    #if (just_code and just_code[-1] not in list(';}')):
    #    return validate_statement_indentation(self, code_lines, line_index + 1, expected + isNextNewStatement, expected + isNextNewStatement, enclosure_stack, False)
    #    line_index += 1
    #else:
    #    if not isNewStatement and just_code and just_code[-1] == ';':
    #        expected -= 1
    if increase < 0:
        return line_index
    return validate_statement_indentation(self, code_lines, line_index + 1, indent_min, indent_min, enclosure_stack, True)


    #while len(enclosure_stack) >= start_stack_len and line_index + 1 < code_lines.num_lines:
    #    increase = len(enclosure_stack) - start_stack_len
    #    line_index = validate_statement_indentation(self, code_lines, line_index + 1, expected, expected, enclosure_stack, True)
    #    line_index += 1

def enclosure_nesting(line_elided, enclosure_stack = [], current_indent = 0):
    # Check for unclosed () and {}
    start_stack_len = len(enclosure_stack)
    line_elided = line_elided.strip()
    for i, c in enumerate(line_elided):
        if c in list('{'):
            enclosure_stack.append({'indent': current_indent})
        elif c in list('}') and len(enclosure_stack): # assume they all match up?
            enclosure_stack.pop()

    return len(enclosure_stack) - start_stack_len

def is_complete_expression(line_index, code_lines, isPreviousStatementNew):
    if line_index >= code_lines.num_lines:
        return isPreviousStatementNew

    just_code = code_lines.elided[line_index].strip()

    if not just_code:
        return isPreviousStatementNew
    else:
        return (just_code and just_code[-1] in list(';{}'))

def indent_line_check(self, code_lines, line_index, indent_min = 0, indent_max = 0, isNewStatement = True, enclosure_stack = []):
    tab_size = self.current_file_indentation

    # Checks if indent is in range, adds error as necessary, return the indention (thresholded)
    def check_indent(line, min, max, found, tab_size = tab_size):
        found_level = found / tab_size
        if (found_level < min):
            expected = min
        elif (found_level > max):
            expected = max
        else:
            expected = int(found_level)

        if (found_level < min or found_level > max):
            self.add_error(label="BLOCK_INDENTATION", line=line+1, data={
                'expected': min * tab_size, 'found': found})

        return expected

    if line_index >= code_lines.num_lines:
        return line_index, 0, 0, 0


    # TODO Make the check its own function.
    leading_whitespace = re.match(r'^(\t*|\s+)\S', code_lines.raw_lines[line_index])
    indent_len = len(leading_whitespace.group()) - 1 if leading_whitespace else 0

    #if not isNewStatement:
    #    indent_min = indent_max = indent_min + 1

    if not leading_whitespace or code_lines.raw_lines[line_index] == '/**/': # blank line (also raw_lines are not truly raw for multi-line comments)
        # Go to next line
        return indent_line_check(self, code_lines, line_index + 1, indent_min, indent_max, isNewStatement, enclosure_stack)

    # Check preprocessor directives
    elif re.match(r'\s*#', code_lines.raw_lines[line_index]):
        check_indent(line_index, 0, 0, indent_len)
        return indent_line_check(self, code_lines, line_index + 1, indent_min, indent_max, isNewStatement, enclosure_stack)

    # Check if line starts with a single-line comment
    elif re.match(r'\s*//', code_lines.raw_lines[line_index]):
        check_indent(line_index, indent_min, indent_max, indent_len)
        return indent_line_check(self, code_lines, line_index + 1, indent_min, indent_max, isNewStatement, enclosure_stack)

    # Check for multi-line comment
    elif re.match(r'\s*/\*', code_lines.raw_lines[line_index]):
        check_indent(line_index, indent_min, indent_max, indent_len)

        # Go through comment lines
        while code_lines.raw_lines[line_index].find('*/') < 0 and line_index + 1 < code_lines.num_lines:
            line_index += 1
            check_indent(line_index, indent_min, indent_max, indent_len)

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
        indent_min = 0;
    if indent_max < indent_min:
        index_max = indent_min

    # Check current line
    expected = check_indent(line_index, indent_min, indent_max, indent_len)

    if enclosure_stack and is_switch_case(code_lines.elided[line_index]):
        enclosure_stack[-1]['case_indent'] = expected

    return line_index, indent_min, indent_max, expected

def is_access_modifiers(code_line):
    return re.match(r'\s*(public|private|protected)\s*:', code_line)

def is_switch_case(code_line):
    return re.match(r'\s*(case\s+|default\s*:)', code_line)
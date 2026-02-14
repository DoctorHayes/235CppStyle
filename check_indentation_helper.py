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

    # Check if preceding line suggests enum (e.g. "enum Foo")
    preceding_line_is_enum = False
    if line_index > 0:
        prev_line = code_lines.elided[line_index - 1]
        if re.search(r'\benum\b', prev_line) and '{' not in prev_line:
             preceding_line_is_enum = True

    increase = enclosure_nesting(code_lines.elided[line_index], enclosure_stack, expected, preceding_line_is_enum)

    # Setup for next line based on how this one ends
    isNextNewStatement = is_complete_expression(line_index, code_lines, isNewStatement, enclosure_stack)

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
        isNextNewStatement = is_complete_expression(line_index, code_lines, isNextNewStatement, enclosure_stack)


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

def enclosure_nesting(line_elided, enclosure_stack = [], current_indent = 0, previous_line_is_enum = False):
    # Check for unclosed () and {}
    start_stack_len = len(enclosure_stack)
    line_elided = line_elided.strip()
    for i, c in enumerate(line_elided):
        if c in list('{'):
            # Check for enum
            is_enum = previous_line_is_enum
            if not is_enum:
                 # Check content before brace on this line
                 prefix = line_elided[:i]
                 if re.search(r'\benum\b', prefix):
                     is_enum = True
            
            enclosure_stack.append({'indent': current_indent, 'is_enum': is_enum})
            previous_line_is_enum = False # Consumed
        elif c in list('}') and len(enclosure_stack): # assume they all match up?
            enclosure_stack.pop()

    return len(enclosure_stack) - start_stack_len

def is_complete_expression(line_index, code_lines, isPreviousStatementNew, enclosure_stack=[]):
    if line_index >= code_lines.num_lines:
        return isPreviousStatementNew

    just_code = code_lines.elided[line_index].strip()

    if not just_code:
        return isPreviousStatementNew
    else:
        terminators = list(';{}')
        if enclosure_stack and enclosure_stack[-1].get('is_enum'):
            terminators.append(',')
        return (just_code and just_code[-1] in terminators)

def indent_line_check(self, code_lines, line_index, indent_min = 0, indent_max = 0, isNewStatement = True, enclosure_stack = []):
    tab_size = self.current_file_indentation


    def count_whitespace(str):
        counts = {'space': 0, 'tab': 0}
        for ch in list(str):
            if ch == ' ':
                counts['space'] += 1
            elif ch == '\t':
                counts['tab'] += 1

        return counts

    # Checks if indent is in range, adds error as necessary, return the indention (thresholded)
    def check_indent(line, min, max, found, tab_size = tab_size):

        found_level = 0
        tab_type = ''
        other_type = ''

        if (tab_size == 1):
            found_level = found['tab']
            tab_type = ' tabs'
            other_type = 'space'
        else:
            found_level = found['space'] / tab_size
            tab_type = ' spaces'
            other_type = 'tab'

        if (found_level < min):
            expected = min
        elif (found_level > max):
            expected = max
        else:
            expected = int(found_level)

        found_msg = ''
        if (found['tab'] > 0 and found['space'] > 0):
            found_msg = str(found['tab']) + ' tabs and ' + str(found['space']) + ' spaces'
        elif (found['tab'] > 0):
            found_msg = str(found['tab']) + ' tabs'
        else:
            found_msg = str(found['space']) + ' spaces'

        if (found_level < min or found_level > max or found[other_type] > 0):
            self.add_error(label="BLOCK_INDENTATION", line=line+1, data={
                'expected': str(min * tab_size) + tab_type, 'found': found_msg})

        return expected

    if line_index >= code_lines.num_lines:
        return line_index, 0, 0, 0
    
    if line_index >= code_lines.num_lines:
        return line_index, 0, 0, 0


    # TODO Make the check its own function.
    leading_whitespace = re.match(r'^(\t*|\s+)\S', code_lines.raw_lines[line_index])
    indent_len = count_whitespace(leading_whitespace.group() if leading_whitespace else '')
    
    print("DEBUG: Checking line {}: '{}' (min={}, max={}, found_len={})".format(line_index + 1, code_lines.raw_lines[line_index].strip(), indent_min, indent_max, indent_len))

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
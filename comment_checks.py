import re
from pyparsing import Word, Literal, alphanums

def check_line_width(self, line):
    max_length = self.max_line_length

    # Remove ending newline from count
    # Also, tabs should be treated as at least 2 chars
    current_length = len(line.strip('\n').strip('\r').replace('\t', '  '))

    # Add error if the line is too long
    if current_length > max_length:
        self.add_error(label="LINE_WIDTH", data={'length': current_length, 'max_length': max_length})

def check_missing_rme(self, lines):
    # RME = A function comment with 3 sections: Requires, Modifies, Effects
    function = Word(alphanums + '_')
    function_syntax = function + Literal('(')
    parsed = function_syntax.searchString(lines[self.current_line_num]).asList()
    function_name = parsed[0][0]
    function_signature = lines[self.current_line_num].strip().replace(';','').strip()
    if function_name != 'main':
        requires = effects = modifies = False
        #Check if there's a complete RME in the last 10 lines
        start = self.current_line_num - 10
        if start < 0:
            start = 0
        for line_num in range(start, self.current_line_num):
            code = lines[line_num].lower()
            if re.search('requires', code): requires = True
            if re.search('effects', code): effects = True
            if re.search('modifies', code): modifies = True
        # If it's not there, maybe they defined it in a header file.
        if not (requires and effects and modifies) and (function_signature not in self.all_rme[self.current_file]):
            # error only in this case
            # prevent double-counting
            if function_signature not in self.missing_rme[self.current_file]:
                self.add_error("MISSING_RME", data={'function': function_name, 'function_signature': function_signature})
                self.missing_rme[self.current_file].add(function_signature)

        elif function_signature not in self.all_rme[self.current_file]:
            self.all_rme[self.current_file].add(function_signature)

def check_missing_prototype_comments(self, lines):
    function = Word(alphanums + '_')
    function_syntax = function + Literal('(')
    parsed = function_syntax.searchString(lines[self.current_line_num]).asList()
    if (len(parsed) > 0):
        function_name = parsed[0][0]
    else:
        return # This must not be a prototype, because the stringSearch failed
    #function_signature = lines[self.current_line_num].strip().replace(';','').strip()

    comment_line = self.current_line_num - 1
    if self.current_line_num != 0 and lines[comment_line] != '/**/' and not re.search(r'^\s*//', lines[comment_line]):
        self.add_error("MISSING_PROTOTYPE_COMMENTS", data={'function': function_name})
        #print( lines[(self.current_line_num - 1) : (self.current_line_num + 1)] )

def check_comment_spacing(self, lines):
    comment_line = self.current_line_num
    prev_line = comment_line - 1

    if self.current_line_num == 0 or (lines[comment_line] != '/**/' and not re.search(r'^\s*//', lines[comment_line])):
        return

    # Check that there is a blank link above a comment.
    if (lines[prev_line] != '/**/' and not re.search(r'^\s*//', lines[prev_line]) and \
        not re.search(r'[\}\{\:]\s*$', lines[prev_line]) and \
        (not lines[prev_line].isspace() and lines[prev_line])):
            # Add 1 to line number because indexes start with 0
            self.add_error("MISSING_COMMENT_SEPERATION", line = comment_line + 1)

    # Check if there is a blank line below a comment.
    next_line = comment_line + 1
    if (len(lines) < next_line and (lines[next_line].isspace() or not lines[next_line])):
        # Make sure this is not the top comment
        while prev_line > 0 and (lines[prev_line] == '/**/' or re.search(r'^\s*//', lines[prev_line])):
            prev_line = prev_line - 1
            #print(prev_line, ": ", lines[prev_line])

        if prev_line > 0:
            self.add_error("EXTRA_COMMENT_SEPERATION", line = comment_line + 1)
            #print("Line ", next_line, ": ", lines[next_line])


def check_missing_type_comments(self, lines):
    current_line = remove_single_line_comment_content(lines[self.current_line_num])
    type = re.search(r"\b(class|struct|enum)(\s+struct|\s+class)*\s+([\w_][\w_\d)]*)\b",
        current_line)

    if (type and (self.current_line_num != 0 and \
        lines[self.current_line_num - 1] != '/**/' and \
        not re.search(r'^\s*//', lines[self.current_line_num - 1]))):

        type_name = type.group(0).split()
        keyword = type_name[0]
        name = type_name[-1]

        self.add_error("MISSING_TYPE_COMMENT", data={'name': name, 'keyword': keyword})
        #print( lines[(self.current_line_num - 1) : (self.current_line_num + 1)] )

def check_min_comments(self, all_lines, clean_lines):
    num_lines = len(all_lines) + 1
    num_comments = 0
    blank_lines_at_end = 0
    for index, line in enumerate(all_lines):
        if line != clean_lines[index]:
            num_comments += 1
        if line[0] == u'\n':
            blank_lines_at_end += 1
        else:
            blank_lines_at_end = 0
    num_lines -= (blank_lines_at_end + 1)
    if num_comments < num_lines * self.min_comments_ratio:
        self.add_error(label='MIN_COMMENTS', line=0, type="WARNING", data={'comments': num_comments, 'lines': num_lines})

# Keeps the //, but removes everything after that on a line
def remove_single_line_comment_content(code):
    #print (re.sub(r'(?<=//)[^\n]*\n', '', code))
    return (re.sub(r'(?<=//)[^\n]*\n', '', code))

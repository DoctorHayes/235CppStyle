class StyleError(object):
    """
    Represents a style error in the student's code.
    """

    def __init__(self):
        self.data = dict()
        self.line_num = 0
        self.column_num = 0
        self.points_worth = 0
        self.type = "ERROR"
        self.message = ""

    def __init__(self, points, label, line_num=0, column_num=0, type="ERROR", data={}):
        """
        Log the line number, type and point value of a specific error.
        points (int): Weight of this error.
        label (str): Key for response lookup in list_of_errors.
        line_num (int): Line number of this error.
        column_num (int): Column number of this error.
        data (dictionary): Additional information about the error,
        """

        self.set_data(data)
        self.set_points_worth(points)
        self.set_line_num(line_num)
        self.set_column_num(column_num)
        self.set_message_from_label(label)
        self.set_type(type)

    def __eq__(self, other):
        return self.data == other.data and self.line_num == other.line_num and \
                self.column_num == other.column_num and self.message == other.message

    def __str__(self):
        output_str = ''
        if self.get_line_number():
            output_str += '{:>3}'.format(self.get_line_number())
            if self.get_column_number():
                output_str += ':' + str(self.get_column_number())
            output_str += '  '
        output_str += str(self.get_message())
        return output_str

    def __gt__(self, other):
        if self.get_line_number() > other.get_line_number():
            return True
        elif self.get_line_number() == other.get_line_number() and self.get_column_number() > other.get_column_number():
            return True
        else:
            return False

    def set_line_num(self, line):
        self.line_num = line
    def set_column_num(self, column):
        self.column_num = column
    def set_message(self, new_message):
        self.message = new_message
    def set_points_worth(self, points):
        self.points_worth = points
    def set_type(self, new_type):
        self.type = new_type
    def set_data(self, new_data):
        self.data = new_data
    def get_points(self):
        return self.points_worth
    def get_message(self):
        return self.message
    def get_line_number(self):
        return self.line_num
    def get_column_number(self):
        return self.column_num
    def get_type(self):
        return self.type
    def get_data(self):
        return self.data

    def set_message_from_label(self, label):
        self.set_message(self.get_error_message(label))

    def get_error_message(self, label):
        return {
            "USING_TABS": "Instead of tabs, you must use spaces (soft tabs).  Fix and resubmit your code :).",
            "OPERATOR_SPACING": "Incorrect spacing around {}.".format(self.get_data().get('operator')),
            "BLOCK_INDENTATION": "Incorrect indentation. Expected: {}, found: {}.".format(self.get_data().get('expected'), self.get_data().get('found')),
            "STATEMENTS_PER_LINE": "There should only be one command (statement) on each line.",
            "IF_ELSE_ERROR": "Every If-Else statement should have brackets.",
            "NON_CONST_GLOBAL": "You should never have a non-const global variable.",
            "FUNCTION_LENGTH_ERROR": "Your function is too long. Break it up into separate functions.",
            "LINE_WIDTH": "Line of {} characters exceeded the limit of {}.".format(self.get_data().get('length'), self.get_data().get("max_length")),
            "INT_FOR_BOOL": "Return 'true' or 'false' instead of a number for functions with a bool return type.",
            "MAGIC_NUMBER": "Store numbers in variables, so that you can give them meaningful names.",
            "BRACE_CONSISTENCY": "All of your opening braces, {, should be either be below the conditions/function-headers or next to the conditions/function-headers; be consistent.",
            "SPACING_ERROR": "Use either tabs or spaces for indentation, not both.",
            "UNNECESSARY_BREAK": "Break statements should ONLY be used in switch statements. Fix your program logic.",
            "GOTO": "Never use the 'goto' statement.",
            "DEFINE_STATEMENT": "While define statements have their applications, they are not allow them in this course.",
            "EQUALS_TRUE": "It is stylistically preferred to use 'if (value)' instead of 'if (value == true)'.",
            "WHILE_TRUE": "It is almost always preferred to use an explicit conditional instead of 'while (true)'.",
            "TERNARY_OPERATOR": "The use of ternary expressions (e.g. return expression ? true : false) is discouraged in this course.",
            "CONTINUE_STATEMENT": "While 'continue' is occasionally appropriate, its use is discouraged in this course.",
            "MAIN_SYNTAX": "Your declaration of main() does not adhere to conventional stylistic guidelines.",
            "STRINGSTREAM": "The use of stringstreams is not allowed in this course to ensure mastery of other IO methods.",
            "UNNECESSARY_INCLUDE": "You have included a library, '{}' that is not allowed in this course.".format(self.get_data().get("library")),
            "FIRST_CHAR": "First character of a {} name must be {}. Expected: {}, found: {}.".format(self.get_data().get("keyword"),
                                                                                                            self.get_data().get("style"),
                                                                                                             self.get_data().get("expected"),
                                                                                                             self.get_data().get("found")),
            "IDENTIFIER_LENGTH": "Identifier '{}' should be longer than 1 character. Use meaningful names.".format(self.get_data().get("found")),
            "IDENTIFIER_I": "Rename variable 'i' to be 'index' or 'iter'. 'i' is a commonly used loop variable. However, our coding style prohibits the use of single-letter identifiers.",
            "OPERATOR_CONSISTENCY": "Your spacing around operators is inconsistent. Pick left, right or both for spacing and stick to it.",
            "POINTER_REFERENCE_CONSISTENCY": "Your use of spacing surrounding '*' and '&' is inconsistent.",
            "MISSING_RME": "{} is missing a complete RME.".format(self.get_data().get("function")),
            "MISSING_PROTOTYPE_COMMENTS": "{}() needs a comment directly preceding the prototype that describes what the function does.".format(self.get_data().get("function")),
            "MIN_COMMENTS": "Potentially too few comments. Found {} {} of comments in {} {} of code.".format(self.get_data().get("comments"),
                                                                                                            'line' if self.get_data().get("comments") == 1 else 'lines',
                                                                                                            self.get_data().get("lines"),
                                                                                                            'line' if self.get_data().get("lines") == 1 else 'lines'),
            "DEFINITION_ABOVE_MAIN": "{} is implemented above main. Keep function definitions below main or in a separate .cpp file.".format(self.get_data().get("function")),
            "FOR_LOOP_SEMICOLON_SPACING": "The loop on line {} doesn't have consistent spacing around its semicolons.".format(self.get_data().get("line")),
            "SYSTEM_CALL": "Remove system call, 'system()', because the command is platform specific (will not run on both macOS and Windows).",
            "FLOAT_TYPE": "Use the double type for all floating-point values. In industry, the float type is only used if there is a compelling reason.",
            "SUCCESSIVE_BLANK_LINES": "Do NOT have consecutive empty lines. Separate sections of code with a single empty line.",
            "ISOLATED_SEMICOLON": "Remove the space directly preceding the semicolon",
            "CPPLINT_ERROR": self.get_data().get('message'),


            "FILENAME_SPACES": "Remove spaces from the filename '{}'. Suggested filename: '{}'.".format(self.get_data().get("filename"),
                                                                                                    self.get_data().get("suggestion"))
        }[label]

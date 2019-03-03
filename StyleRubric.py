'''
Style Grader class with instance-method plugin-based functionality.
'''

import codecs
from configparser import ConfigParser
from collections import defaultdict
import os
import sys
from copy import deepcopy
from glob import glob
import re
from cpplint import CleansedLines, RemoveMultiLineComments
from style_grader_functions import check_if_function, check_if_function_prototype, print_success, get_soft_tab_length
from style_grader_classes import SpacingTracker
from StyleError import StyleError
import filename_checks
import comment_checks
import multi_line_checks
import misc_checks
import single_line_checks
from style_grader_functions import erase_string
import adjustments
import cpplint

LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))

def safely_open(filename):
    try:
        dirty_text = codecs.open(filename, 'r', 'utf8', 'replace').readlines()
        for num, line in enumerate(dirty_text):
            dirty_text[num] = line.rstrip('\r')
        return dirty_text
    except IOError:
        sys.stderr.write('This file could not be read: "%s."  '
                         'Please check filename and resubmit \n' % filename)
        return

class StyleRubric(object):
    '''
    A style grader to generate StyleErrors from a list of C++ files.
    '''
    def __init__(self, student_files=None):
        ''' Load functionality based on config file specifications '''
        self.config = ConfigParser()
        self.config.read(LOCAL_DIR+'/rubric.ini')
        self.error_tracker = dict()
        self.error_types = defaultdict(int)
        self.total_errors = 0
        self.includes = self.config.get('FILES', 'permitted_includes').split(',')
        self.local_includes = dict()
        self.all_rme = dict()
        self.missing_rme = dict()
        self.min_comments_ratio = float(self.config.get('SETTINGS', 'min_comments_ratio'))
        self.max_line_length = int(self.config.get('SETTINGS', 'max_line_length'))
        self.filename_checks = self.load_functions(filename_checks)
        self.single_line_checks = self.load_functions(single_line_checks)
        self.multi_line_checks = self.load_functions(multi_line_checks)
        self.detect_unnecessary_break = self.config.get('SETTINGS', 'unnecessary_break') == 'yes'
        self.allow_define_in_header = self.config.get('SETTINGS', 'allow_define_in_header') == 'yes'
        self.comment_checks = self.load_functions(comment_checks)
        self.misc_checks = self.load_functions(misc_checks)
        self.adjustments = self.load_functions(adjustments, prefix='adjust')
        self.global_in_object = False;
        self.global_object_braces = []
        self.global_in_object_index = 0
        self.file_has_a_main = {}
        self.current_file_indentation = 4

        # Load filters for cpplint
        cpplint.ProcessConfigOverrides('CPPLINT.cfg')

        if student_files:
            self.student_files = student_files
        else:
            self.student_files = self.load_filenames(self.config.get('FILES', 'student_files').split(','))


    def add_global_brace(self, brace):
        self.global_object_braces.append(brace)
        self.global_in_object_index += 1

    def pop_global_brace(self):
        self.global_object_braces.pop()
        if self.global_in_object_index == 0:
            self.global_in_object = False

    def load_functions(self, module, prefix='check'):
        functions = list()
        group = module.__name__.split('.')[-1].upper()
        for check in self.config.options(group):
            if self.config.get(group, check).lower() == 'yes':
                functions.append(getattr(module, prefix + '_' + check))
        return functions

    def load_filenames(self, paths):
        all_files = list()
        for path in paths:
            files = glob(path)
            all_files.extend(files)
        return all_files

    def reset_for_new_file(self, filename):
        self.spacer = SpacingTracker()
        self.outside_main = True
        self.egyptian = None
        self.not_egyptian = None
        self.braces_error = False #To prevent multiple braces errors
        self.in_switch = False
        self.current_file = filename
        self.error_tracker[filename] = list()
        self.all_rme[filename] = set()
        self.missing_rme[filename] = set()
        self.local_includes[filename] = list()
        self.current_file_indentation = get_soft_tab_length(open(filename, 'rU'))

    def add_error(self, label=None, line=-1, column=0, type='ERROR', data=dict()):
        self.total_errors += 1
        self.error_types[label] += 1
        line = line if (line != -1) else self.current_line_num + 1
        self.error_tracker[self.current_file].append(StyleError(1, label, line, column_num=column, type=type, data=data))

    def contains_error(self, label=None, line=-1, column=0, type='ERROR', data=dict()):
        temp_err = StyleError(1, label, line, column_num=column, type=type, data=data)
        return temp_err in self.error_tracker[self.current_file]

    def grade_student_file(self, filename, original_filename):
        extension = filename.split('.')[-1]
        if extension not in ['h', 'cpp']:
            sys.stderr.write('Failed to parse {}: incorrect file type.\n'.format(filename))
            return
        data = safely_open(filename)
        if data:
            self.reset_for_new_file(filename)
            raw_data = deepcopy(data)
            RemoveMultiLineComments(filename, data, '')
            clean_lines = CleansedLines(data)
            clean_code = clean_lines.elided

            for function in self.filename_checks: function(self, original_filename)
            for self.current_line_num, code in enumerate(clean_code):
                code = erase_string(code)
                if self.config.get('SINGLE_LINE_CHECKS', 'tab_type').lower() == 'soft' and code.find('\t') != -1:
                    self.add_error(label='USING_TABS')
                    break

                for function in self.single_line_checks: function(self, code)
                for function in self.multi_line_checks: function(self, clean_lines)

            # COMMENT CHECKS #TODO
            for self.current_line_num, text in enumerate(raw_data):
                if self.config.get('COMMENT_CHECKS', 'line_width').lower() == 'yes':
                    getattr(comment_checks, 'check_line_width')(self, text)
                if check_if_function(text):
                    if self.config.get('COMMENT_CHECKS', 'missing_rme').lower() == 'yes':
                        getattr(comment_checks, 'check_missing_rme')(self, raw_data)
                if check_if_function_prototype(text):
                    if self.config.get('COMMENT_CHECKS', 'missing_prototype_comments').lower() == 'yes':
                        getattr(comment_checks, 'check_missing_prototype_comments')(self, clean_lines.lines_without_raw_strings)
                if self.config.get('COMMENT_CHECKS', 'min_comments').lower() == 'yes':
                    getattr(comment_checks, 'check_min_comments')(self, raw_data, clean_code)
                if self.config.get('COMMENT_CHECKS', 'missing_type_comments').lower() == 'yes':
                    getattr(comment_checks, 'check_missing_type_comments')(self, clean_lines.lines_without_raw_strings)
                if self.config.get('COMMENT_CHECKS', 'comment_spacing').lower() == 'yes':
                   getattr(comment_checks, 'check_comment_spacing')(self, clean_lines.lines_without_raw_strings)
            for function in self.misc_checks: function(self)

            # Run checks directly from cpplint
            # Filters are configurable from the CPPLINT.cfg file
            self.cpplint_tests(filename)

            # Organize the error list for this file
            self.error_tracker[filename].sort()
            self.file_has_a_main[filename] = not self.outside_main
            if not self.file_has_a_main[filename]:
                self.remove_error_by_type(filename, 'DEFINITION_ABOVE_MAIN')

            # This is a bit of a hack, to make the setting work.
            # TODO: make a multi-line check for unnecessary breaks.
            if not self.detect_unnecessary_break:
                self.remove_error_by_type(filename, 'UNNECESSARY_BREAK')

    def html_escape(self, text):
        """Produce entities within text."""
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
        }
        if text:
            return "".join(html_escape_table.get(c,c) for c in text)
        else:
            return text

    def cpplint_tests(self, filename):
        # Run checks directly from cpplint
        from io import TextIOWrapper, BytesIO
        output_string = ''
        real_stderr =  sys.stderr
        fake_out = TextIOWrapper(BytesIO(), sys.stdout.encoding)
        try:
            sys.stderr = fake_out
            cpplint.ProcessFile(filename, 0)
        except TypeError:
            print('TODO: Fix TypeError: must be unicode, not str in Python 2.x')
        finally:
            # get output
            sys.stderr.seek(0)      # jump to the start
            output_string = sys.stderr.read() # read output

            # restore stderr
            sys.stderr = real_stderr
            fake_out.close()

        # Parse output from cpplint
        for line in output_string.splitlines():
            result = re.search(filename + r'\:(\d+)\:\s+(.*)', line)
            if result:
                line_num = int(result.group(1))
                self.add_error(label="CPPLINT_ERROR", line=line_num, data={'message': self.html_escape(result.group(2))})

    def adjust_errors(self):
        for function in self.adjustments:
            function(self)

    def remove_error_by_type(self, filename, error_type='DEFINITION_ABOVE_MAIN'):
        new_error_list = []
        # temp error to generate the DEF_ABOVE_MAIN error message
        temp_err = StyleError(1, error_type, data={'function': '__error_function__'})
        def_above_main_message = temp_err.get_error_message(error_type).replace('__error_function__', '')

        # Remove any errors that deal with function def above main
        saved_errors = 0
        for e in self.error_tracker[filename]:
            if def_above_main_message not in e.message:
                saved_errors += 1
                new_error_list.append(e)
        self.total_errors -= len(self.error_tracker[filename]) - saved_errors
        if error_type in self.error_types.keys():
            self.error_types[error_type] -= len(self.error_tracker[filename]) - saved_errors
            if self.error_types[error_type] == 0:
                self.error_types.pop(error_type, None)
        self.error_tracker[filename] = new_error_list

    # Creates an array that contains the error messages for each file.
    def get_error_summary(self, error_list = []):
        for filename, errors in self.error_tracker.items():
            error_dictionary = {
                'filename': filename.split('/')[-1],
                'errors': []
            }

            for error in errors:
                location = ''
                if error.get_line_number():
                    location = str(error.get_line_number())
                    if error.get_column_number():
                        location += ':' + str(error.get_column_number())
                error_dictionary['errors'].append({'location': location, 'message': error.get_message()})

            error_list.append(error_dictionary)

        return error_list

    def print_errors(self, error_list = []):
        for filename, errors in self.error_tracker.items():

            print('Code-Quality Report for \'{}\''.format(filename.split('/')[-1]))
            if len(errors) == 0:
                 print_success()
            for error in errors:
                if error.get_line_number():
                    print(error)

            print('')

        return self.get_error_summary(error_list)

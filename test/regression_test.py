#!/usr/bin/python
from test import load_code_segment
from style_grader_functions import *
from StyleRubric import *
import unittest

class RegressionTesting(unittest.TestCase):
    styleRubric = StyleRubric()

    @load_code_segment('good.cpp')
    def test_good_file(self): self.assertTrue(len(self.rubric.error_types) == 0)
    @load_code_segment('num_of_commands.cpp')
    def test_statements_per_line(self): self.assertEqual(self.rubric.error_types['STATEMENTS_PER_LINE'], 3)
    @load_code_segment('test_valid_return.cpp')
    def test_int_for_bool(self): self.assertEqual(self.rubric.error_types['INT_FOR_BOOL'], 2)
    #@load_code_segment('if_else_good.cpp')
    #def test_good_if_else(self): self.assertEqual(0, self.rubric.error_types['IF_ELSE_ERROR'])
    #@load_code_segment('if_else_bad.cpp')
    #def test_bad_if_else(self): self.assertEqual(3, self.rubric.error_types['IF_ELSE_ERROR'])
    @load_code_segment('equals_true.cpp')
    def test_equals_true(self): self.assertEqual(5, self.rubric.error_types['EQUALS_TRUE'])
    @load_code_segment('function_def_above_main_good.cpp')
    def test_def_above_main_good(self):
        self.assertEqual(0, self.rubric.error_types['DEFINITION_ABOVE_MAIN'])
        self.assertEqual(1, self.rubric.error_types['SUCCESSIVE_BLANK_LINES'])
    @load_code_segment('function_def_above_main_bad.cpp')
    def test_def_above_main_bad(self): self.assertEqual(8, self.rubric.error_types['DEFINITION_ABOVE_MAIN'])
    @load_code_segment('goto_good.cpp')
    def test_goto_good(self): self.assertEqual(0, self.rubric.error_types['GOTO'])
    @load_code_segment('goto_bad.cpp')
    def test_goto_bad(self): self.assertEqual(3, self.rubric.error_types['GOTO'])
    @load_code_segment('continue_good.cpp')
    def test_continue_good(self): self.assertEqual(0, self.rubric.error_types['CONTINUE_STATEMENT'])
    @load_code_segment('continue_bad.cpp')
    def test_continue_bad(self): self.assertEqual(4, self.rubric.error_types['CONTINUE_STATEMENT'])
    @load_code_segment('define_good.cpp')
    def test_define_good(self): self.assertEqual(0, self.rubric.error_types['DEFINE_STATEMENT'])
    @load_code_segment('define_bad.cpp')
    def test_define_bad(self): self.assertEqual(2, self.rubric.error_types['DEFINE_STATEMENT'])
    @load_code_segment('ternary_good.cpp')
    def test_ternary_good(self): self.assertEqual(0, self.rubric.error_types['TERNARY_OPERATOR'])
    @load_code_segment('func_params_multiline.cpp')
    def test_prototype_comment_bad(self):
        self.assertEqual(0, self.rubric.error_types['MISSING_PROTOTYPE_COMMENTS'])
        self.assertEqual(1, self.rubric.error_types['MISSING_COMMENT_SEPERATION'])


    @load_code_segment('ternary_bad.cpp')
    def test_ternary_bad(self):
        self.assertEqual(\
            3 if self.styleRubric.config.get('SINGLE_LINE_CHECKS', 'ternary_operator') == 'yes' else 0,\
            self.rubric.error_types['TERNARY_OPERATOR'])

    @load_code_segment('while_true_good.cpp')
    def test_while_true_good(self): self.assertEqual(0, self.rubric.error_types['WHILE_TRUE'])
    @load_code_segment('while_true_bad.cpp')
    def test_while_true_bad(self): self.assertEqual(4, self.rubric.error_types['WHILE_TRUE'])

    @load_code_segment('float_type_good.cpp')
    def test_float_type_good(self): self.assertEqual(0, self.rubric.error_types['FLOAT_TYPE'])
    @load_code_segment('float_type_bad.cpp')
    def test_float_type_bad(self): self.assertEqual(7, self.rubric.error_types['FLOAT_TYPE'])

    #@load_code_segment('global_good.cpp')
    #def test_global_good(self): self.assertEqual(0, self.rubric.error_types['NON_CONST_GLOBAL'])
    #@load_code_segment('global_bad.cpp')
    #def test_global_bad(self): self.assertEqual(13, self.rubric.error_types['NON_CONST_GLOBAL'])
    @load_code_segment('main_good.cpp')
    def test_main_good(self): self.assertEqual(0, self.rubric.error_types['MAIN_SYNTAX'])
    @load_code_segment('main_bad.cpp')
    def test_main_bad(self): self.assertEqual(2, self.rubric.error_types['MAIN_SYNTAX'])
    @load_code_segment('first_char_good.cpp')
    def test_first_char_good(self): self.assertEqual(0, self.rubric.error_types['FIRST_CHAR'])
    @load_code_segment('first_char_bad.cpp')
    def test_first_char_bad(self): self.assertEqual(6, self.rubric.error_types['FIRST_CHAR'])

    @load_code_segment('semicolon_comma_spacing_bad.cpp')
    def test_semicolon_spacing_bad1(self): self.assertEqual(4, self.rubric.error_types['ISOLATED_SEMICOLON'])
    @load_code_segment('semicolon_spacing_good1.cpp')
    def test_semicolon_spacing_good1(self): self.assertEqual(0, self.rubric.error_types['FOR_LOOP_SEMICOLON_SPACING'])
    @load_code_segment('semicolon_spacing_good2.cpp')
    def test_semicolon_spacing_good2(self): self.assertEqual(0, self.rubric.error_types['FOR_LOOP_SEMICOLON_SPACING'])
    @load_code_segment('semicolon_spacing_bad.cpp')
    def test_semicolon_spacing_bad2(self): self.assertEqual(4, self.rubric.error_types['FOR_LOOP_SEMICOLON_SPACING'])

    @load_code_segment('logical_AND_OR_spacing_bad.cpp')
    def test_bad_logical_spacing(self): self.assertEqual(3, self.rubric.error_types['OPERATOR_SPACING'])
    @load_code_segment('logical_AND_OR_spacing_good.cpp')
    def test_good_logical_spacing(self): self.assertEqual(0, self.rubric.error_types['OPERATOR_SPACING'])
    @load_code_segment('operator_spacing_bad.cpp')
    def test_bad_operator_spacing(self): self.assertEqual(28, self.rubric.error_types['OPERATOR_SPACING'])
    @load_code_segment('operator_spacing_good.cpp')
    def test_good_operator_spacing(self): self.assertEqual(0, self.rubric.error_types['OPERATOR_SPACING'])

    @load_code_segment('func_def_no_main.cpp')
    def test_func_def_no_main(self): self.assertEqual(0, self.rubric.error_types['DEFINITION_ABOVE_MAIN'])

    @load_code_segment('indent_conditional.cpp')
    def test_simple_conditional_indent(self): self.assertEqual(4, self.rubric.error_types['BLOCK_INDENTATION'])
    @load_code_segment('indent_switch.cpp')
    def test_simple_switch_indent(self): self.assertEqual(9, self.rubric.error_types['BLOCK_INDENTATION'])
    @load_code_segment('indent_classes.h')
    def test_class_indentation_header(self): self.assertEqual(11, self.rubric.error_types['BLOCK_INDENTATION'])
    @load_code_segment('indent_structs.h')
    def test_struct_indentation_header(self): self.assertEqual(11, self.rubric.error_types['BLOCK_INDENTATION'])
    @load_code_segment('indent_if_good.cpp')
    def test_indent_if_good(self): self.assertEqual(0, self.rubric.error_types['BLOCK_INDENTATION'])
    @load_code_segment('indenation_hardtabs.cpp')
    def test_indent_hardtabs_good(self): self.assertEqual(0, self.rubric.error_types['BLOCK_INDENTATION'])
    @load_code_segment('indent_bad_4.cpp')
    def test_indent_soft4(self): self.assertEqual(8, self.rubric.error_types['BLOCK_INDENTATION'])
    @load_code_segment('indent_bad_3.cpp')
    def test_indent_soft3(self): self.assertEqual(8, self.rubric.error_types['BLOCK_INDENTATION'])
    @load_code_segment('indent_bad_2.cpp')
    def test_indent_soft2(self): self.assertEqual(11, self.rubric.error_types['BLOCK_INDENTATION'])

    # Test for too long lines based on the setting in the config (valid for line lengths that are multiples of 10 between 30 and 120)
    @load_code_segment('long_lines.cpp')
    def test_check_line_width(self):
        self.assertEqual(26 - int(self.styleRubric.max_line_length / 5), self.rubric.error_types['LINE_WIDTH'])

    # Test brace consistency
    @load_code_segment('brace_consistancy_allman_good.cpp')
    def test_brace_consistancy_allman_good(self): self.assertEqual(0, self.rubric.error_types['BRACE_CONSISTENCY'])
    @load_code_segment('brace_consistancy_stroustrup_good.cpp')
    def test_brace_consistancy_stroustrup_good(self): self.assertEqual(0, self.rubric.error_types['BRACE_CONSISTENCY'])
    @load_code_segment('brace_consistancy_bad.cpp')
    def test_brace_consistancy_stroustrup_good(self): self.assertEqual(1, self.rubric.error_types['BRACE_CONSISTENCY'])

    # Check identifier style
    @load_code_segment('identifier_case_bad.cpp')
    def test_identifier_case_bad(self): self.assertEqual(34, self.rubric.error_types['FIRST_CHAR'])
    @load_code_segment('identifier_length_bad.cpp')
    def test_check_identifier_length(self):
        self.assertEqual(11, self.rubric.error_types['IDENTIFIER_LENGTH'])
        self.assertEqual(2, self.rubric.error_types['IDENTIFIER_I'])

    @load_code_segment('system_call_bad.cpp')
    def test_bad_system_call(self): self.assertEqual(1, self.rubric.error_types['SYSTEM_CALL'])
    @load_code_segment('system_call_good.cpp')
    def test_good_system_call(self): self.assertEqual(0, self.rubric.error_types['SYSTEM_CALL'])

    @load_code_segment('include_test_good.cpp')
    def test_includes_good(self): self.assertEqual(0, self.rubric.error_types['UNNECESSARY_INCLUDE'])
    @load_code_segment('include_test_bad.cpp')
    def test_includes_good(self):
        if self.styleRubric.config.get('SINGLE_LINE_CHECKS', 'unnecessary_include') == 'yes':
            self.assertEqual(5, self.rubric.error_types['UNNECESSARY_INCLUDE'])
        else:
            pass

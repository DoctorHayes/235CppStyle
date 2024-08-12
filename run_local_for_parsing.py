#!/usr/bin/python
import sys
from StyleRubric import StyleRubric

def main(files):

    rubric = StyleRubric()
    show_errors = []

    for filename in files:
        rubric.grade_student_file(filename, filename)

    rubric.adjust_errors()
    rubric.print_errors_for_parsing()

    sys.exit(rubric.total_errors)


if __name__ == "__main__":
    main(sys.argv[1:])
#!/usr/bin/python
from StyleRubric import StyleRubric

def style_grader_driver(online_files):
    rubric = StyleRubric()
    show_errors = []

    for filename, originalname in online_files.items():
        print('Analyzing {}...'.format(filename.split('/')[-1]))
        rubric.grade_student_file(filename, originalname)

    rubric.adjust_errors()
    show_errors = rubric.get_error_summary(show_errors)

    # #For debugging purposes only
    # print(":\t".join(["Total Errors", str(rubric.total_errors)]))
    # for x, y in rubric.error_types.items():
    #     print(":\t".join([x, str(y)]))


    return show_errors

# if __name__ == '__main__':
#     main()
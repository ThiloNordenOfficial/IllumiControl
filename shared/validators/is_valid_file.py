import os


def is_valid_file(parser_ref, arg):
    if not os.path.exists(arg):
        parser_ref.error("The file %s does not exist!" % arg)
    else:
        return arg

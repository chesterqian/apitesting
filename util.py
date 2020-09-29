import os


def intersection_of_path(file_path):
    relative_file_path = os.path.normpath(file_path)
    relative_list = relative_file_path.split(os.sep)
    sys_path_now_list = os.path.dirname(__file__).split(os.sep)[1:]
    print(sys_path_now_list)
    print(relative_list)
    for i in range(len(sys_path_now_list)):
        if (relative_list[0] == sys_path_now_list[i]): intersection = i
    prepose_path = ''.join(
        ['/%s' % y for y in sys_path_now_list[:intersection]])
    return os.path.join(prepose_path, file_path)

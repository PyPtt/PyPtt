import os
import traceback


def check_range(define_obj, value):
    if value < define_obj.min_value or define_obj.max_value < value:
        return False
    return True


def get_file_name(string):
    result = os.path.basename(string)
    result = result[:result.find('.')]
    return result


# def get_sub_string_list(main_string, target_a, target_b):
#
#     result = []
#
#     if not isinstance(target_b, list):
#         target_b = [target_b]
#
#     while target_a in main_string:
#         temp = main_string[main_string.find(target_a) + len(target_a):]
#
#         # print(f'>{temp}')
#         max_index = len(main_string)
#         best_index = max_index
#         for B in target_b:
#             current_index = temp.find(B)
#             if best_index > current_index >= 0:
#                 best_index = current_index
#         #         print(f'best_index: {best_index}')
#
#         # print(f'QQ best_index: {best_index}')
#         # print(f'QQ len(TargetB): {len(TargetB)}')
#         if best_index != max_index:
#             temp = temp[:best_index].strip()
#             result.append(temp)
#
#         main_string = main_string[main_string.find(target_a) + len(target_a):]
#
#     return result


def get_current_func_name():
    return traceback.extract_stack(None, 2)[0][2]


def findnth(haystack, needle, n):
    parts = haystack.split(needle, n+1)
    if len(parts) <= n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

import re
from .list_utils import argmax_list


def get_chinese(text):
    """process a text to remove all non chinese character"""
    filtrate = re.compile(u'[^\u4E00-\u9FA5]') # non-Chinese unicode range
    text = filtrate.sub(r'', text) # remove all non-Chinese characters
    return text


def rmv_not_chinese(counter):
    """remove non chinese entries in a word frequency counter"""
    for key in counter.copy().keys():
        if get_chinese(key) == '':
            del counter[key]
    return counter


def find_chapter_separator(txt):
    """find the formatting for chapter in a mandarin book
    the format is usually `第*节` or `第*章` or `第*回` with `*` which can
    be a chinese or digit number"""

    # define the different possible separator that can occur (can be extended in the future)
    list_sep = ['节', '章', '回']

    # find the list of chapter separation for all of the separators defined in `list_sep`
    list_count = []
    list_seps = []
    for sep in list_sep:
        seps = re.findall('第[一二三四五六七八九十百零0-9]{1,5}' + sep + '[\n\\s\t　]', txt)
        list_seps.append(seps)
        list_count.append(len(seps))

    # find the index of the longest list
    max_index = argmax_list(list_count)

    # check if there is a non zero lenght list
    if list_count[max_index] == 0:
        max_sep = None
        max_seps = None
    else:
        max_sep = list_sep[max_index]
        max_seps = list_seps[max_index]
    return max_sep, max_seps
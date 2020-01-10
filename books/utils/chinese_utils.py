import re


def get_chinese(context):
#     context = context.decode("utf-8") # convert context from str to unicode
    filtrate = re.compile(u'[^\u4E00-\u9FA5]') # non-Chinese unicode range
    context = filtrate.sub(r'', context) # remove all non-Chinese characters
#     context = context.encode("utf-8") # convert unicode back to str
    return context


def rmv_not_chinese(counter):
    for key in counter.copy().keys():
        if get_chinese(key) == '':
            del counter[key]
    return counter


def find_chapter_separator(txt):
    jie_sep = re.findall('第[一二三四五六七八九十百零0-9]{1,5}节[\n\\s\t]', txt)
    zhang_sep = re.findall('第[一二三四五六七八九十百零0-9]{1,5}章[\n\\s\t]', txt)

    jie_count = len(jie_sep)
    zhang_count = len(zhang_sep)

    count = 0

    if jie_count > zhang_count:
        separator = "节"
        seps = jie_sep
    elif zhang_count > jie_count:
        separator = '章'
        seps = zhang_sep
    elif (zhang_count == 0) & (jie_count == 0):
        separator = False
        seps = []

    return (separator, seps)
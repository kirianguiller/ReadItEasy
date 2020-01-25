import os
import cProfile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReadItEasy.settings')

import django
django.setup()

from dictionary.models import MandarinWord
import time

import jieba

# fetch the root project and other paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path_ce_dict = os.path.join(BASE_DIR, 'data', 'dict', 'tab_cedict_ts.u8')

cedict = {}

# with open(path_ce_dict, 'r', encoding='utf-8') as f:
#     for line in f:
#         line = line.rstrip('\n')
#         splitted_line = line.split('\t')
#         zh_trad = splitted_line[0]
#         zh_simpl = splitted_line[1]
#         pronunciation = splitted_line[2]
#         definitions = splitted_line[3]
#         def_list = []
#         for definition in definitions.split('/'):
#             if definition != '':
#                 def_list.append(definition)
#         list_line = [zh_simpl, zh_trad, pronunciation, def_list]
#         cedict[zh_simpl] = list_line
t1 = time.time()

print(MandarinWord.objects.filter(simplified="沒")[0].definition)
t2 = time.time()
print(t2-t1)

# path_book = "/home/wran/plurital/ReadItEasy/data/books/mandarin/1984_orwell.txt"
# with open(path_book, 'r') as f:
#     txt = f.read()
#
# tokens = list(jieba.tokenize(txt))
# tokens = list(set(tokens))
#
# t1 = time.time()
# for n, token in enumerate(tokens):
#     if n>10000:break
#     MandarinWord.objects.filter(simplified=token)
# t2 = time.time()
#
# print(t2-t1)
# t1 = time.time()
#
# with open(path_ce_dict, 'r', encoding='utf-8') as f:
#     for n, line in enumerate(f):
#         line = line.rstrip('\n')
#         traditional = line.split('\t')[0]
#         simplified = line.split('\t')[1]
#         pronunciation = line.split('\t')[2]
#         definition = line.split('\t')[3]
#
#         if simplified== '日出':
#             break
# t2 = time.time()
# print(t2-t1)


# print(MandarinWord.objects.all()[0].id)
# print(MandarinWord.objects.get(id=1000))
# for n in range(len(MandarinWord.objects.all())):
#     MandarinWord.objects.get(id=n+10026)
#     if n%100==0:
#         print(n)
# print("done")
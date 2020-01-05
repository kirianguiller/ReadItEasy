from django.shortcuts import render, redirect
from .forms import formText
from django.http import HttpResponse
from collections import Counter
import re

# Create your views here.

import jieba
import os
import numpy as np
import matplotlib.pyplot as plt

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
    count_jie = len(re.findall('第.{1,5}节', txt))
    count_zhang = len(re.findall('第.{1,5}章', txt))
    count = 0

    if count_jie > count_zhang:
        separator = "节"
        count = count_jie
    elif count_zhang > count_jie:
        separator = '章'
        count = count_zhang
    elif (count_zhang == 0) & (count_jie == 0):
        separator = "Not Found"

    return (separator, count)

path_books = "data/books/"
path_books = os.path.abspath(path_books)
jieba.initialize()
path_ce_dict = "data/dict/tab_cedict_ts.u8"
path_ce_dict = os.path.abspath(path_ce_dict)
path_hsk_vocab = "data/hsk_vocab/HSK1->6.csv"
path_hsk_vocab = os.path.abspath(path_hsk_vocab)
path_books_app = os.path.dirname(os.path.abspath(__file__))
path_books_cache = os.path.join(path_books_app, 'static', 'books', 'cache')

if not os.path.isdir(path_books_cache):
    os.mkdir(path_books_cache)

zh2en = {}
sim2cedict = {}
with open(path_ce_dict, 'r') as f:
    for line in f:
        line = line.rstrip('\n')
        zh_trad = line.split('\t')[0]
        zh_simpl = line.split('\t')[1]
        # en_def = line.split('\t')[-1].split('/')[1]
        fayin = line.split('\t')[2]
        definitions = line.split('\t')[3]
        def_list = []
        for definition in definitions.split('/'):
            if definition != '':
                def_list.append(definition)
        list_line = [zh_simpl, zh_trad, fayin, def_list]
        sim2cedict[zh_simpl] = list_line

# extract hsk information
word2hsk = {}
with open(path_hsk_vocab, 'r') as f:
    for n, line in enumerate(f):
        if n == 0:
            pass
        else:
            hsk_level, word = line.split(',')
            word2hsk[word.rstrip('\n')] = int(hsk_level)


def home(request):
    return collection(request)


def get_books():
    list_books = []
    for book in os.listdir(path_books):
        list_books.append(book.split('.')[0])

    return list_books


def collection(request):
    list_books = get_books()
    return render(request, "books/collection.html", {"list_books": list_books})


def get_user_text(request):
    if request.method == 'POST':
        form = formText(request.POST)
        if form.is_valid():
            request.session['0'] = form.cleaned_data['text']

            return request.session['0']
    else:
        form = formText()
    return render(request, 'books/text_form.html', {
        'form': form
    })


def print_book(request, id_book):
    path_book = os.path.join(path_books, "{}.txt".format(id_book))

    path_book_cache = os.path.join(path_books_cache, id_book)
    with open(path_book, 'r') as infile:
        full_txt = infile.read()

    chapter_separator, _ = find_chapter_separator(full_txt)

    txt = re.split('第.{1,5}' + chapter_separator ,full_txt)[1].strip()
    tokens = jieba.cut(txt)
    freqs = Counter(jieba.cut(full_txt))
    freqs = rmv_not_chinese(freqs)
    # txt = ' '.join(tokens)
    txt = ''
    list_words_meta = []
    list_words = []
    for token in tokens:
        if token =='\n':
            token = '@$$@'
        list_words.append(token)
        list_words_meta.append(sim2cedict.get(token, ['-']*4))

    # save the tokenized text and data in cache
    path_tokenized_text_cache = os.path.join(path_book_cache, 'tokenized_text.txt')
    with open(path_tokenized_text_cache, 'w') as outfile:
        for word in list_words:
            outfile.write(word + '\n')


    # fetch hsk data from the book
    hsk_counter = {}
    for level in range(0, 7):
        hsk_counter[level] = 0

    for char, freq in freqs.items():
        hsk_counter[word2hsk.get(char, 0)] += freq

    hsk_counter['none'] = hsk_counter.pop(0)

    # build and save the hsk distribution bar plot
    values = list(hsk_counter.values())
    labels = ["level {}".format(level) for level in hsk_counter.keys()]
    plt.bar(range(len(hsk_counter)), values, align='center', alpha=0.9)
    plt.xticks(range(len(hsk_counter)), labels)


    if not os.path.isdir(path_book_cache):
        os.mkdir(path_book_cache)
    path_barplot = os.path.join(path_book_cache, 'hsk_barplot.png')

    rel_static_path = os.path.join('books', 'cache', id_book, 'hsk_barplot.png')
    plt.savefig(path_barplot)
    plt.clf()

    size_corpus = sum(freqs.values())
    zip_list = zip(list_words, list_words_meta)
    context = {
        "id_book": id_book,
        'zip_list': zip_list,
        "freqs": freqs.most_common(1000),
        "size_corpus": size_corpus,
        "hsk_counter": hsk_counter,
        "rel_static_path":rel_static_path,
    }
    return render(request, "books/print_book.html", context)


# 
# @bp.route("/upload", methods=("GET", "POST"))
# def upload():
#     if request.method == "POST":
#         text = request.form['text']
#         session['processed_text'] = text
#         return redirect(url_for("read.index"))
#         # return render_template("upload/uploaded.html")
#         # render_template("upload/uploaded.html", )
#     return render("read/upload.html")



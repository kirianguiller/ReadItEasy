from django.shortcuts import render, redirect
from .forms import formText
from django.http import HttpResponse
from collections import Counter
import re
import pickle

# Create your views here.
import time
import jieba
import os
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# path_books = "data/books/"
path_books = os.path.join(BASE_DIR, 'data', 'books')
jieba.initialize()
# path_ce_dict = "data/dict/tab_cedict_ts.u8"
# path_ce_dict = os.path.abspath(path_ce_dict)
path_ce_dict = os.path.join(BASE_DIR, 'data', 'dict', 'tab_cedict_ts.u8')


path_hsk_vocab = os.path.join(BASE_DIR, 'data', 'hsk_vocab', 'HSK1->6.csv')
# path_hsk_vocab = "data/hsk_vocab/HSK1->6.csv"
# path_hsk_vocab = os.path.abspath(path_hsk_vocab)
path_books_app = os.path.dirname(os.path.abspath(__file__))
path_books_cache = os.path.join(path_books_app, 'static', 'books', 'cache')

if not os.path.isdir(path_books_cache):
    os.mkdir(path_books_cache)

zh2en = {}
sim2cedict = {}
with open(path_ce_dict, 'r', encoding='utf-8') as f:
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
    return show_languages(request)


def get_books():
    list_books = []
    for book in os.listdir(path_books):
        list_books.append(book.split('.')[0])

    return list_books


def show_languages(request):
    list_languages = os.listdir(path_books)
    return render(request, "books/show_list.html", {"list": list_languages})


def show_books(request, language):
    if language not in ['english', 'mandarin']:
        return redirect(show_languages)
    path_language = os.path.join(path_books, language)
    list_books = []
    for book in os.listdir(path_language):
        list_books.append(book.split('.')[0])
    return render(request, "books/show_list.html", {"list": list_books})


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


# def show_id_book(request, language, id_book):
#     if language not in ['english', 'mandarin']:
#         return redirect(show_languages)
#
#     if language == 'mandarin':
#         return redirect(show_chapter, language, id_book)


def show_chapter(request, language, id_book, reader_chapter=1):
    if language == 'mandarin':
        return mandarin_chapter(request, language=language, id_book=id_book, reader_chapter=reader_chapter)

    elif language == 'english':
        return english_chapter(request, language=language, id_book=id_book, reader_chapter=reader_chapter)


    else:
        return redirect(show_languages)


def mandarin_chapter(request, language, id_book, reader_chapter=1):
    t1 = time.time()
    path_book = os.path.join(path_books, language, id_book + '.txt')

    # create the cache folder for the book if doesn't exist yet
    path_book_cache = os.path.join(path_books_cache, language, id_book)
    if not os.path.isdir(path_book_cache):
        os.makedirs(path_book_cache)


    # load all the book $$ Can improve a little speed here
    with open(path_book, 'r') as infile:
        full_txt = infile.read()

    # get info about chapter seperator
    chapter_separator, list_seps = find_chapter_separator(full_txt)
    chapters_number = len(list_seps)
    if reader_chapter > chapters_number:
        return redirect(show_chapter, language=language, id_book=id_book, reader_chapter=chapters_number)

    # get chapter name and chapter text
    chapter_name = list_seps[reader_chapter - 1]
    chapter_txt = re.split('第[一二三四五六七八九十百零0-9]{1,5}'+chapter_separator+ '[\n\\s\t]' ,full_txt)[reader_chapter].strip()

    # tokenize the chapter
    chapter_tokens = jieba.cut(chapter_txt)
    list_words_meta = []
    list_words = []
    for token in chapter_tokens:
        if token =='\n':
            token = '@$$@'
        list_words.append(token)
        list_words_meta.append(sim2cedict.get(token, ['-']*4))
    zip_list = zip(list_words, list_words_meta)

    # # save the tokenized text and data in cache
    # path_tokenized_text_cache = os.path.join(path_book_cache, 'tokenized_text.txt')
    # with open(path_tokenized_text_cache, 'w') as outfile:
    #     for word in list_words:
    #         outfile.write(word + '\n')


    # get statistics about the whole book
    path_freqs_pickle = os.path.join(path_book_cache, 'freqs.pkl')
    if os.path.isfile(path_freqs_pickle):
        with open(path_freqs_pickle, 'rb') as f:
            freqs = pickle.load(f)
    else:
        tokenized_full_text = jieba.cut(full_txt)
        freqs = Counter(tokenized_full_text)
        freqs = rmv_not_chinese(freqs)
        with open(path_freqs_pickle, 'wb') as f:
            pickle.dump(freqs, f, pickle.HIGHEST_PROTOCOL)

    size_corpus = sum(freqs.values())

    # fetch hsk data from the book
    path_barplot = os.path.join(path_book_cache, 'hsk_barplot.png')
    rel_path_barplot = path_barplot.split('books/static/')[-1]
    print(path_barplot)
    if os.path.isfile(path_barplot):
        pass
    else:
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
        plt.savefig(path_barplot)
        plt.clf()

    t2 = time.time()
    print('D2', t2 - t1)

    context = {
        "id_book": id_book,
        'zip_list': zip_list,
        "freqs": freqs.most_common(10000),
        "size_corpus": size_corpus,
        # "hsk_counter": hsk_counter,
        "chapter_name": chapter_name,
        'rel_path_barplot': rel_path_barplot,
    }
    return render(request, "books/chinese_text.html", context)


def english_chapter(request, language, id_book, reader_chapter):
    path_book = os.path.join(path_books, language, id_book + '.txt')

    # create the cache folder for the book if doesn't exist yet
    path_book_cache = os.path.join(path_books_cache, language, id_book)
    if not os.path.isdir(path_book_cache):
        os.makedirs(path_book_cache)

    # load all the book $$ Can improve a little speed here
    with open(path_book, 'r') as infile:
        full_txt = infile.read()

    txt = full_txt[:10000]

    context = {
        'id_book': id_book,
        'txt': txt,
    }

    return render(request, "books/english_text.html", context)

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



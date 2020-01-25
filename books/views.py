# django imports
from django.shortcuts import render, redirect
from .forms import formText, SearchForm
from django.http import Http404

# base imports
from collections import Counter
import re
import pickle
import time
import jieba
import os
import matplotlib.pyplot as plt

# user packages imports
from .utils.chinese_utils import rmv_not_chinese, find_chapter_separator

# jieba initialization
jieba.initialize()

# fetch the root project and app path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_books_app = os.path.dirname(os.path.abspath(__file__))


# fetch path to different data files
path_books = os.path.join(BASE_DIR, 'data', 'books')
path_ce_dict = os.path.join(BASE_DIR, 'data', 'dict', 'tab_cedict_ts.u8')
path_hsk_vocab = os.path.join(BASE_DIR, 'data', 'hsk_vocab', 'HSK1->6.csv')
path_corpus_stats = os.path.join(BASE_DIR, 'data', 'statistics', 'corpus_rank_freqs.pkl')


# check if the project is used in development or in production...
# ...this is useful because static files are not in the same folders...
# ...between dev and prod.
DJANGO_DEVELOPMENT = True
if 'www/ReadItEasy' in BASE_DIR:
    DJANGO_DEVELOPMENT = False

if DJANGO_DEVELOPMENT:
    path_books_cache = os.path.join(path_books_app, 'static', 'books', 'cache')
else:
    path_books_cache = os.path.join(BASE_DIR, 'ReadItEasy', 'static', 'books', 'cache')

# create the books cache folder. This folder will contains saved data which ...
# ... make the scripts run faster
if not os.path.isdir(path_books_cache):
    os.makedirs(path_books_cache)

# fetch the data of CE_dict, a chinese -> english open source dictionary.
# this dict contains informations about
# - the simplified and traditional form of a chinese caracter : 'zh_trad' and 'zh_simpl'
# - the pronunciation : 'pronunciation'
# - the english translation(s) : 'def_list'
#
# these information are fetch into the dicts 'sim2cedict'
cedict = {}
with open(path_ce_dict, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        splitted_line = line.split('\t')
        zh_trad = splitted_line[0]
        zh_simpl = splitted_line[1]
        pronunciation = splitted_line[2]
        definitions = splitted_line[3]
        def_list = []
        for definition in definitions.split('/'):
            if definition != '':
                def_list.append(definition)
        list_line = [zh_simpl, zh_trad, pronunciation, def_list]
        cedict[zh_simpl] = list_line

# extract hsk information
word2hsk = {}
with open(path_hsk_vocab, 'r', encoding='utf-8') as f:
    for n, line in enumerate(f):
        if n == 0:
            pass
        else:
            hsk_level, word = line.split(',')
            word2hsk[word.rstrip('\n')] = int(hsk_level)




# from here start the view function defintion. Views will be computed when ...
# its corresponding url (in 'url.py') will be request by the user
# IMPORTANT : view are computed at each url access by the user, that's why it's important
#             to have long time processing script in the first part of the view (outside
#             function definition). For instance in our case jieba.initialize() and
#             dict initialisation


def show_books_list(request):
    """view that show the list of books (per language) available on the server"""

    # get the languages available. All books are inside their corresponding language folder
    list_languages = os.listdir(path_books)

    # get the list of books per langage
    list_books_per_languages = []
    for language in list_languages:
        path_language = os.path.join(path_books, language)
        list_books = []
        for book in os.listdir(path_language):
            list_books.append(book.split('.')[0])

        list_books_per_languages.append(list_books)

    # create a zip list that associate each language to its available books
    lists = zip(list_languages, list_books_per_languages)

    return render(request, "books/books_list.html", {"lists": lists})


def show_chapter(request, language, id_book, reader_chapter=None):
    """show the chapter of a book. In the future, there will be more than one language
    so we will need a redirection language-wise"""

    # check if the book exists. If it doesn't, redirect to books selection page
    path_book = os.path.join(path_books, language, id_book + '.txt')
    if not os.path.isfile(path_book):
        return redirect(show_books_list)

    # if the reader doesn't select a chapter, redirect his request to the  ...
    # ... url's chapter 1 of the corresponding book
    if (reader_chapter is None) | (reader_chapter == 0):
        return redirect(show_chapter, language=language, id_book=id_book, reader_chapter=1)

    # if language is mandarin, redirect the request to the 'mandarin_chapter()' view
    if language == 'mandarin':
        return mandarin_chapter(request, language=language, id_book=id_book, reader_chapter=reader_chapter)

    # else, redirect to the show_books page
    else:
        return redirect(show_books_list)


def mandarin_chapter(request, language, id_book, reader_chapter):
    """IMPORTANT View
    This view will segment the selected book by chapter, tokenize the text, fetch
    the meta about words inside the text (pronunciation, definition), compute word
    frequencies and ranks and do some caching for faster loading
    """
    # fetch the path to the book
    path_book = os.path.join(path_books, language, id_book + '.txt')

    # create the cache folder for the book if doesn't exist yet
    path_book_cache = os.path.join(path_books_cache, language, id_book)
    if not os.path.isdir(path_book_cache):
        os.makedirs(path_book_cache)

    # load all the book $$ Can improve a little speed here
    with open(path_book, 'r', encoding='utf-8') as infile:
        full_txt = infile.read()

    # get info about chapter seperator so we can segment the text by chapter.
    # it allow to show the text to the user chapter-wise which is less data consuming
    # the 'find_chapter_separator()' is located in /utils/chinese_utils.py
    chapter_separator, list_seps = find_chapter_separator(full_txt)
    if chapter_separator is False:
        raise Http404
    chapters_number = len(list_seps)
    if reader_chapter > chapters_number:
        return redirect(show_chapter, language=language, id_book=id_book, reader_chapter=chapters_number)

    # get chapter name and chapter text
    chapter_name = list_seps[reader_chapter - 1]
    chapter_txt = re.split('第[一二三四五六七八九十百零0-9]{1,5}'+chapter_separator + '[\n\\s\t]',
                           full_txt)[reader_chapter].strip()

    # tokenize the chapter
    chapter_tokens = jieba.cut(chapter_txt)

    # fetch all words and words meta to 2 lists for later use in templates
    list_words_meta = []
    list_words = []
    n = 0
    for token in chapter_tokens:
        n += 1
        if n > 1000:
            break
        if token =='\n':
            token = '@$$@' # replace \n by specific token for later use in templates

        list_words.append(token)

        # add a punctuation marker on punctuation element to make it easier to
        # recognize them in the html template (so we can avoid to add tooltip for them)
        if token in ['—', '。', '，', '“', '”', '　', '？', '！', '、', '《', '》', '：', '…']:
            list_words_meta.append('punctuation')
        else:
            # fetch the meta of a word if it is in our dict
            list_words_meta.append(cedict.get(token, ['-'] * 4))

    zip_list = zip(list_words, list_words_meta)

    # compute the statistics of the words in the book and cache it for faster reload
    path_freqs_pickle = os.path.join(path_book_cache, 'freqs.pkl')
    if os.path.isfile(path_freqs_pickle):
        with open(path_freqs_pickle, 'rb') as f:
            book_freqs = pickle.load(f)
    else:
        tokenized_full_text = jieba.cut(full_txt)
        book_freqs = Counter(tokenized_full_text)
        book_freqs = rmv_not_chinese(book_freqs)
        with open(path_freqs_pickle, 'wb') as f:
            pickle.dump(book_freqs, f, pickle.HIGHEST_PROTOCOL)

    # load the corpus statistics about words. This corpus is a dict with word as
    # ... key and a list of 2 elements containing the corpus ranking and relative
    # ... frequence of a word as value
    with open(path_corpus_stats, 'rb') as pickle_stats:
        corpus_stats = pickle.load(pickle_stats)
    # compute the words statistics (book wise and corpus wise) and store them in a list of
    # ... list for later use in the template
    n_tokens_book = sum(book_freqs.values()) # number of token in the book
    list_words_stats = []
    size_limit = 100
    for char, abs_freq in book_freqs.most_common(size_limit):
        book_rel_freq = 100 * abs_freq / n_tokens_book          # freq in %
        corpus_rank, corpus_rel_freq = corpus_stats.get(char, [0, 0])

        # transform the percent freq in per million freq for better understanding
        book_rel_freq = int(book_rel_freq * (10**4))
        corpus_rel_freq = int(corpus_rel_freq * (10**4))
        list_words_stats.append([char, book_rel_freq, corpus_rank, corpus_rel_freq])

    context = {
        "id_book": id_book,
        'zip_list': zip_list,
        # "freqs": freqs.most_common(10000),
        # "size_corpus": size_book,
        'list_words_stats': list_words_stats,
        "chapter_name": chapter_name,
        "reader_chapter":reader_chapter,
        "next_chapter":reader_chapter+1,
        "previous_chapter":reader_chapter-1,
        'language': language,
    }
    return render(request, "books/mandarin_text.html", context)


def show_statistics(request, language, id_book):
    """this view's purpuse is to compute the statistics of the book and send the data
    to the corresponding template"""
    path_book = os.path.join(path_books, language, id_book + '.txt')

    # create the cache folder for the book if doesn't exist yet
    path_book_cache = os.path.join(path_books_cache, language, id_book)
    if not os.path.isdir(path_book_cache):
        os.makedirs(path_book_cache)

    # load the whole book
    with open(path_book, 'r', encoding='utf-8') as infile:
        full_txt = infile.read()

    # get statistics about the whole book and cache it for faster reload
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

    # fetch hsk data from the book and plot it as a bar chart
    path_barplot = os.path.join(path_book_cache, 'hsk_barplot.png')
    rel_path_barplot = path_barplot.split('/static/')[-1]
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

    context = {
        "id_book": id_book,
        'rel_path_barplot': rel_path_barplot,
        'language': language,
    }

    return render(request, "books/statistics.html", context)


def show_search(request, language, id_book):
    """View for the search tool. The search tool take a string as input
    and look in the current user book all the sentence that contains this
    string"""

    # check if there is a post request (the user search post)
    if request.method == 'POST':

        # use django form model to preprocess and clean the data
        # this prebuild module improve security
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['query']
            path_book = os.path.join(path_books, language, id_book + '.txt')

            # iterate through the book to find matching sentences
            matching_sentences = []
            with open(path_book, 'r', encoding='utf-8') as infile:
                for line in infile:
                    line = line.replace('\n', '')
                    for sentence in line.split('。'):
                        if search in sentence:
                            sentence = sentence.replace(' ', '')
                            matching_sentences.append(sentence)
            context = {
                'language': language,
                'id_book': id_book,
                'search': search,
                'matching_sentences': matching_sentences,
            }

            return render(request, 'books/search.html', context)

    raise Http404



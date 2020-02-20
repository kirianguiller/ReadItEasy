# django imports
from django.shortcuts import render, redirect
from .forms import formText, SearchForm
from django.http import Http404, JsonResponse

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
HMM = True
custom_seperated_words = []



# fetch the root project and app path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_books_app = os.path.dirname(os.path.abspath(__file__))


# path languages
path_languages = os.path.join(BASE_DIR, 'data', 'languages')

# fetch path to different data files
path_mandarin = os.path.join(path_languages, 'mandarin')
path_books = os.path.join(path_mandarin, 'books', 'content') #? change path_books name with path_content
path_freqs = os.path.join(path_mandarin, 'books', 'freqs')
path_extended_dict = os.path.join(path_mandarin, 'dict', 'extended_dict.u8')
path_ce_dict = os.path.join(path_mandarin, 'dict', 'tab_cedict_ts.u8') # deprecated
path_hsk_vocab = os.path.join(path_mandarin, 'hsk_vocab', 'HSK1->6.csv')
path_corpus_stats = os.path.join(path_mandarin, 'statistics', 'corpus_rank_freqs.pkl')
path_known_words = os.path.join(path_mandarin, 'known_words', 'user001')


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
with open(path_extended_dict, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        splitted_line = line.split('\t')
        zh_trad = splitted_line[0]
        zh_simpl = splitted_line[1]
        # old_style_pronunciation = splitted_line[2]
        pronunciation = splitted_line[3]
        definitions = splitted_line[5]
        hsk_level = splitted_line[4]
        def_list = []
        for definition in definitions.split('/'):
            if definition != '':
                def_list.append(definition)
        list_line = [zh_simpl, zh_trad, pronunciation, def_list, hsk_level]
        cedict[zh_simpl] = list_line


# from here start the view function defintion. Views will be computed when ...
# its corresponding url (in 'url.py') will be request by the user
# IMPORTANT : view are computed at each url access by the user, that's why it's important
#             to have long time processing script in the first part of the view (outside
#             function definition). For instance in our case jieba.initialize() and
#             dict initialisation


def show_books_list(request):
    """view that show the list of books (per language) available on the server"""

    # get the languages available. All books are inside their corresponding language folder
    list_languages = os.listdir(path_languages)

    # get the list of books per language
    list_books_per_languages = []
    for language in list_languages:
        path_books_language = os.path.join(path_languages, language, 'books', 'content')
        list_books = []
        for book in os.listdir(path_books_language):
            list_books.append(book.split('.')[0])

        list_books_per_languages.append(list_books)

    # create a zip list that associate each language to its available books
    lists = zip(list_languages, list_books_per_languages)

    return render(request, "books/books_list.html", {"lists": lists})


def show_chapter(request, language, id_book, reader_chapter=None):
    """show the chapter of a book. In the future, there will be more than one language
    so we will need a redirection language-wise"""

    path_books_language = os.path.join(path_languages, language, 'books', 'content')
    # check if the book exists. If it doesn't, redirect to books selection page
    path_book = os.path.join(path_books_language, id_book + '.txt')
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
    t1 = time.time()
    # fetch the path to the book
    path_books_language = os.path.join(path_languages, language, 'books', 'content')
    path_book = os.path.join(path_books_language, id_book + '.txt')

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
    chapter_tokens = jieba.cut(chapter_txt, HMM=HMM)

    # get the username (if authenticated)
    username = None
    if request.user.is_authenticated:
        username = request.user.username

    # load user known words
    user_known_words = set()
    path_known_words = os.path.join(path_mandarin, 'known_words', '{}_knowns_words.txt'.format(username))
    if os.path.isfile(path_known_words):
        with open(path_known_words, 'r', encoding='utf-8') as infile:
            for line in infile:
                user_known_words.add(line.rstrip('\n'))

    # fetch all words and words meta to 2 lists for later use in templates
    list_tokens = []
    list_metas = []
    for token in chapter_tokens:
        if token not in custom_seperated_words:
            list_tokens.append(token)
            meta = give_token_meta(token, user_known_words)
            list_metas.append(meta)
        else:
            for character in token:
                list_tokens.append(token)
                meta = give_token_meta(character, user_known_words)
                list_metas.append(meta)
    tk_meta_zl = zip(list_tokens, list_metas)


    ta = time.time()
    # compute the statistics of the words in the book and cache it for faster reload
    path_book_freqs_txt = os.path.join(path_freqs, id_book+'_freqs.txt')
    book_freqs = {}
    if os.path.isfile(path_book_freqs_txt):
        with open(path_book_freqs_txt, 'r', encoding="utf-8") as infile:
            for n, line in enumerate(infile):
                if n == 0:
                    _, n_book_tokens, _, n_book_types = line.rstrip("\n").split("\t")
                    n_book_tokens = int(n_book_tokens)
                    n_book_types = int(n_book_types)
                else:
                    char, rank, freq = line.rstrip("\n").split("\t")
                    book_freqs[char] = int(freq)
    else:
        tokenized_full_text = jieba.cut(full_txt, HMM=HMM)
        book_freqs = Counter(tokenized_full_text)
        book_freqs = rmv_not_chinese(book_freqs)
        n_book_tokens = sum(book_freqs.values())
        n_book_types = len(set(book_freqs.keys()))
        with open(path_book_freqs_txt, "w", encoding="utf-8") as outfile:
            outfile.write("#tokens:\t{}\ttype:\t{}\n".format(n_book_tokens, n_book_types))
            for rank, (char, freq) in enumerate(book_freqs.most_common()):
                outfile.write("{}\t{}\t{}\n".format(char, rank, freq))

    tb = time.time()
    # path_book_freqs_pkl = os.path.join(path_freqs, id_book+'_freqs.pkl')
    #
    # if os.path.isfile(path_book_freqs_pkl):
    #     with open(path_book_freqs_pkl, 'rb') as f:
    #         book_freqs = pickle.load(f)
    # else:
    #     tokenized_full_text = jieba.cut(full_txt, HMM=HMM)
    #     book_freqs = Counter(tokenized_full_text)
    #     book_freqs = rmv_not_chinese(book_freqs)
    #     with open(path_book_freqs_pkl, 'wb') as f:
    #         pickle.dump(book_freqs, f, pickle.HIGHEST_PROTOCOL)
    #
    # book_types = set(book_freqs.keys())
    #
    # n_book_tokens = sum(book_freqs.values())
    # n_book_types = len(book_types)

    tc = time.time()

    print('t1', tb-ta)
    print('t2', tc-tb)
    n_user_tokens = 0
    n_user_types = 0
    for known_word in user_known_words:
        n_user_tokens += book_freqs.get(known_word,0)
        if known_word in book_freqs:
            n_user_types += 1

    book_stats = {
        'n_book_tokens': n_book_tokens,
        'n_book_types': n_book_types,
        'n_user_tokens': n_user_tokens,
        'n_user_types': n_user_types,
    }

    print('\nTIME', time.time()-t1)
    context = {
        "id_book": id_book,
        'tk_meta_zl': tk_meta_zl,
        'book_stats': book_stats,
        "chapter_name": chapter_name,
        "reader_chapter":reader_chapter,
        "next_chapter":reader_chapter+1,
        "previous_chapter":reader_chapter-1,
        'language': language,
    }
    return render(request, "books/mandarin_text.html", context)

def show_book_words(request, language, id_book):
    """
    This view allow the user to see a table of a book's words and to interact with it
    """
    # get the username (if authenticated)
    username = None
    if request.user.is_authenticated:
        username = request.user.username

    # load user known words
    user_known_words = set()
    path_known_words = os.path.join(path_mandarin, 'known_words', '{}_knowns_words.txt'.format(username))
    if os.path.isfile(path_known_words):
        with open(path_known_words, 'r', encoding='utf-8') as infile:
            for line in infile:
                user_known_words.add(line.rstrip('\n'))

    # load the book stats
    # TODO : deal with the case the stats were never computed
    path_book_freqs_txt = os.path.join(path_freqs, id_book + '_freqs.txt')
    list_of_list = []
    with open(path_book_freqs_txt, 'r', encoding="utf-8") as infile:
        first_line = infile.readline()
        n_tokens = float((first_line.rstrip("\n").split("\t")[1]))
        for line in infile:
            char, rank, count = line.rstrip("\n").split("\t")
            _, _, pinyin, _, hsk = cedict.get(char, ["Not Found"]*5)
            is_known = (char in user_known_words)
            list_of_list.append([rank, char, count, pinyin, hsk, is_known])



    context = {
        "list_of_list" : list_of_list,

    }
    return render(request, "books/book_words.html", context)

def give_token_meta(token, known_words):
    """
    Function that take a token and the user known words as input,
    and return the token meta which can be one of the forth possibilities :
    - br (for return line)
    - punctuation
    - `known` for words known by the user
    - `unknown` for other words
    """

    # if the token is the special character '\n', add the info in the meta ...
    # ... as the django templates can't perform the {token == "\n"} operator.
    if token == '\n':
        meta = 'br'  # replace \n by specific token for later use in templates

    # add a punctuation marker on punctuation element to make it easier to ...
    # ... recognize them in the html template (so we can avoid to add tooltip for them)
    elif token in ['—', '。', '，', '“', '”', '　', '？', '！', '、', '《', '》', '：', '…']:
        meta = 'punctuation'

    # for other token (should be words), fetch if it's known or not by the user
    else:
        if token in known_words:
            meta = 'known'
        else:
            meta = 'unknown'

    return meta

# def show_statistics(request, language, id_book):
#     """this view's purpuse is to compute the statistics of the book and send the data
#     to the corresponding template"""
#     path_book = os.path.join(path_books, language, id_book + '.txt')
#
#     # create the cache folder for the book if doesn't exist yet
#     path_book_cache = os.path.join(path_books_cache, language, id_book)
#     if not os.path.isdir(path_book_cache):
#         os.makedirs(path_book_cache)
#
#     # load the whole book
#     with open(path_book, 'r', encoding='utf-8') as infile:
#         full_txt = infile.read()
#
#     # get statistics about the whole book and cache it for faster reload
#     path_freqs_pickle = os.path.join(path_book_cache, 'freqs.pkl')
#     if os.path.isfile(path_freqs_pickle):
#         with open(path_freqs_pickle, 'rb') as f:
#             freqs = pickle.load(f)
#     else:
#         tokenized_full_text = jieba.cut(full_txt)
#         freqs = Counter(tokenized_full_text)
#         freqs = rmv_not_chinese(freqs)
#         with open(path_freqs_pickle, 'wb') as f:
#             pickle.dump(freqs, f, pickle.HIGHEST_PROTOCOL)
#
#     # fetch hsk data from the book and plot it as a bar chart
#     path_barplot = os.path.join(path_book_cache, 'hsk_barplot.png')
#     rel_path_barplot = path_barplot.split('/static/')[-1]
#     if os.path.isfile(path_barplot):
#         pass
#     else:
#         hsk_counter = {}
#         for level in range(0, 7):
#             hsk_counter[level] = 0
#
#         for char, freq in freqs.items():
#             hsk_counter[word2hsk.get(char, 0)] += freq
#
#         hsk_counter['none'] = hsk_counter.pop(0)
#
#         # build and save the hsk distribution bar plot
#         values = list(hsk_counter.values())
#         labels = ["level {}".format(level) for level in hsk_counter.keys()]
#         plt.bar(range(len(hsk_counter)), values, align='center', alpha=0.9)
#         plt.xticks(range(len(hsk_counter)), labels)
#         plt.savefig(path_barplot)
#         plt.clf()
#
#     context = {
#         "id_book": id_book,
#         'rel_path_barplot': rel_path_barplot,
#         'language': language,
#     }
#
#     return render(request, "books/statistics.html", context)
#


# POST search pattern function
def show_search(request, language, id_book, search):
    """View for the search tool. The search tool take a string as input
    and look in the current user book all the sentence that contains this
    string"""

    path_book = os.path.join(path_books, id_book + '.txt')

    # iterate through the book to find matching sentences
    matching_sentences = []
    with open(path_book, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.replace('\n', '')
            for sentence in line.split('。'):
                if search in sentence:
                    sentence = sentence.replace(' ', '')
                    # add bold to the text
                    sentence = re.sub('({})'.format(search), r'<span style="font-weight:bold">\1</span>', sentence)
                    # add the sentence to the matching list
                    matching_sentences.append(sentence)

    context = {
        'language': language,
        'id_book': id_book,
        'search': search,
        'matching_sentences': matching_sentences,
    }

    return render(request, 'books/search.html', context)


def ajax_change_tokenization(request):
    """
    Ajax get that add a multi-characters word to the must-tokenize list
    """
    request_word = request.GET.get('word', None)
    request_action = request.GET.get('action', None)

    if request_word:
        custom_seperated_words.append(request_word)

    return JsonResponse({"succeed":"yes"})


def ajax_word_data(request):
    """
    Ajax GET that send diverse information about a word to the client
    !!! this function might need to be relocated to a new `requests` specific app !!!
    """
    username = None
    if request.user.is_authenticated:
        username = request.user.username

    request_word = request.GET.get('word', None)
    is_freqs = request.GET.get('is_freqs', None)
    id_book = request.GET.get('id_book', None)
    data_list = cedict.get(request_word, None)

    if data_list:
        data = {
            'zh_simpl': data_list[0],
            'zh_trad': data_list[1],
            'pronunciation': data_list[2],
            'definitions': data_list[3],
            'hsk_level': data_list[4],
            'is_in_dict': True,
        }
    else:
        data = {
            'is_in_dict': False,
        }
    if is_freqs == 'True':
        # fetch the word freq statistics for the current book
        book_rank, book_freq, book_tokens = get_w_book_freqs(request_word, id_book)
        # fetch the word freq statistics for the reference corpus
        corpus_rank, corpus_freq, corpus_tokens = get_w_corpus_freqs(request_word)

        data['book_rank'] = '{}e'.format(book_rank + 1) # because start from 0
        data['book_freq'] = book_freq
        data['book_rel_freq'] = int(1000000 * book_freq / book_tokens)

        if corpus_rank == None:
            data['corpus_rank'] = "-"
            data['corpus_freq'] = "-"

        else:
            data['corpus_rank'] = '{}e'.format(corpus_rank)
            data['corpus_freq'] = int(corpus_freq * 1000000 / 100)

    return JsonResponse(data)


def word_freqs_from_freq_txt(word, path_to_freq_txt):
    """get the word freqs from a freq.txt file"""
    with open(path_to_freq_txt, 'r', encoding="utf-8") as infile:
        first_line = infile.readline()
        n_tokens = 0.
        if "tokens" in first_line:
            n_tokens = float((first_line.rstrip("\n").split("\t")[1]))
        for line in infile:
            char, rank, freq = line.rstrip("\n").split("\t")
            if char == word:
                rank, freq = int(rank), float(freq)
                return int(rank), float(freq), n_tokens

    return None, None, None


def get_w_book_freqs(word, id_book):
    path_to_freq_txt = os.path.join(path_freqs, "{}_freqs.txt".format(id_book))
    rank, freq, n_tokens = word_freqs_from_freq_txt(word, path_to_freq_txt)

    return rank, freq, n_tokens

def get_w_corpus_freqs(word):
    path_to_freq_txt = path_corpus_stats.replace(".pkl", ".txt")
    rank, freq, n_tokens = word_freqs_from_freq_txt(word, path_to_freq_txt)

    return rank, freq, n_tokens

#
# def get_book_freqs(word, id_book=None):
#
#     path_freqs_pickle = os.path.join(path_freqs, "{}_freqs.pkl".format(id_book))
#     with open(path_freqs_pickle, 'rb') as f:
#         book_freqs = pickle.load(f)
#
#     for rank, (char, freq) in enumerate(book_freqs.most_common()):
#         if char == word:
#             print(rank, char, word, freq)
#             return rank, freq
#
#     return None, None
#
#
# def get_corpus_freqs(word):
#     path_freqs_pickle = path_corpus_stats
#     with open(path_freqs_pickle, 'rb') as f:
#         book_freqs = pickle.load(f)
#
#     corpus_rank, corpus_rel_freq = book_freqs.get(word, ['Na', 0])
#     print(corpus_rank, corpus_rel_freq)
#     return corpus_rank, corpus_rel_freq






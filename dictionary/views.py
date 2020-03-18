# django imports
from django.shortcuts import render
from django.http import Http404, JsonResponse
from .models import MandarinWord

# base imports
import os
import time
import pandas as pd

# fetch the root project and app path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_dictionary_app = os.path.dirname(os.path.abspath(__file__))

# path languages
path_languages = os.path.join(BASE_DIR, 'data', 'languages')

# fetch path to different data files
path_mandarin = os.path.join(path_languages, 'mandarin')
path_extended_dict = os.path.join(path_mandarin, 'dict', 'extended_dict.u8')
path_extended_dict_hsk_only = os.path.join(path_mandarin, 'dict', 'extended_dict_hsk_only.u8')
path_ce_dict = os.path.join(path_mandarin, 'dict', 'tab_cedict_ts.u8')
path_hsk_vocab = os.path.join(path_mandarin, 'hsk_vocab', 'HSK1->6.csv')
path_known_words = os.path.join(path_mandarin, 'known_words', 'user001')
path_neighbors_words = os.path.join(path_mandarin, 'embeddings', 'chinese_embeddings_552books_neighbors.tsv')
path_corpus_stats = os.path.join(path_mandarin, 'statistics', 'corpus_rank_freqs.txt')


dict_similar_words = {}
with open(path_neighbors_words, 'r', encoding='utf-8') as infile:
    for line in infile:
        word, *neighbors = line.split('\t')
        dict_similar_words[word] = neighbors

# # fetch the user001 known_words
# known_words_user001 = set()
# with open(path_known_words, 'r', encoding='utf-8') as infile:
#     for line in infile:
#         known_words_user001.add(line.rstrip('\n'))
# print(known_words_user001)


def view_word_data(request, language, user_word):
    """This view redirect the request for a corresponding valid language function.
    Currently, only mandarin is supported"""
    if language == 'mandarin':
        return mandarin_word_data(request, language=language, user_word=user_word)
    else:
        raise Http404


def mandarin_word_data(request, language, user_word):
    """This view prepare the data about a word for printing them in the
    html template"""
    t1 = time.time()
    is_in_dict = False # if the word is not in CEDICT, this value will stay false
    matching_words = MandarinWord.objects.filter(simplified=user_word)

    simplified = None
    traditional = None
    pronunciation = None
    def_list = []

    if len(matching_words) > 0:
        is_in_dict = True
        meta = matching_words[0]
        simplified = meta.traditional
        traditional = meta.simplified
        pronunciation = meta.pronunciation
        definitions = meta.definitions
        def_list = []
        for definition in definitions.split('/'):
            if definition != '':
                def_list.append(definition)
        # list_line = [simplified, traditional, pronunciation, def_list]

    user_relative_words = dict_similar_words.get(user_word, False)

    t2 = time.time()
    print('\ntime for loading word data : {}\n'.format(t2-t1))
    context = {
        'word': user_word,
        'language': language,
        'zh_simpl': simplified,
        'zh_trad': traditional,
        'fayin': pronunciation,
        'def_list': def_list,
        'is_in_dict': is_in_dict,
        'user_relative_words': user_relative_words,
    }

    return render(request, "dictionary/mandarin_word_data.html", context)


def view_words_list(request, language):
    """This view redirect the request for a corresponding valid language words list.
    Currently, only mandarin is supported"""
    if language == 'mandarin':
        return mandarin_words_list(request, language=language)
    else:
        raise Http404


def mandarin_words_list(request, language):
    """
    This view is for showing to the user the hsk words he knows and it allow him to interact
    with it
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

    # import the dict and zip the columns for easy access in template
    df_dict = pd.read_csv(path_extended_dict_hsk_only, sep='\t', header=0)
    df_dict = df_dict[df_dict["hsk"] < 5]

    # import the frequency tsv
    t1 = time.time()
    df_stats = pd.read_csv(path_corpus_stats, sep='\t', header=None, skiprows=1)
    dict_stats = df_stats.set_index(0).to_dict()[1]
    t2 = time.time()
    print('\n time : ', t2-t1)

    # build the hsk known word list
    words_corpus_rank = []
    hsk_known_words = []
    for sim in df_dict['sim']:
        hsk_known_words.append((sim in user_known_words))
        words_corpus_rank.append(dict_stats.get(sim, "-"))

    ext_dict_zl = zip(*[df_dict[col] for col in df_dict] + [hsk_known_words]+[words_corpus_rank])

    # ext_dict_zl = zip(ext_dict_zl, hsk_known_words)
    context = {
        "ext_dict_zl": ext_dict_zl,
    }
    return render(request, "dictionary/mandarin_words_list.html", context)


def ajax_interact_known_word(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username

    added_word = request.GET.get('word', None)
    action = request.GET.get('action', None)
    action_done = 'None'

    # load user known words
    user_known_words = set()
    path_known_words = os.path.join(path_mandarin, 'known_words', '{}_knowns_words.txt'.format(username))
    if os.path.isfile(path_known_words):
        with open(path_known_words, 'r', encoding='utf-8') as infile:
            for line in infile:
                user_known_words.add(line.rstrip('\n'))

    if action == 'add':
        user_known_words.add(added_word)
        action_done = 'added'
        print(added_word, action_done)

    elif action == 'remove':
        user_known_words.remove(added_word)
        action_done = 'remove'
        print(added_word, action_done)

    with open(path_known_words, 'w', encoding='utf-8') as outfile:
        for word in user_known_words:
            outfile.write(word + '\n')

    data = {
        'action_done': action_done,
            }
    return JsonResponse(data)


def api_sentence(request):
    
    json = {
        "sentence":
            ["四月", "间", "天气", "寒冷", "晴朗", "钟", "敲", "了", "十三", "下",  "。",
             "温斯顿", "史密斯", "为了", "要", "躲", "晴朗"],
        # "isKnownDict": {
        #     "四月": {"form": "四月", "isKnown": "true"},
        #     "间": {"form": "间", "isKnown": "true"},
        #     "天气": {"form": "天气", "isKnown": "true"},
        #     "寒冷": {"form": "寒冷", "isKnown": "false"},
        #     "晴朗": {"form": "晴朗", "isKnown": "false"},
        #     "钟": {"form": "钟", "isKnown": "false"},
        #     "敲": {"form": "敲", "isKnown": "true"},
        #     "了": {"form": "了", "isKnown": "true"},
        #     "十三": {"form": "十三", "isKnown": "true"},
        #     "下": {"form": "下", "isKnown": "true"},
        #     "。": {"form": "。", "isKnown": "true"},
        #     "温斯顿": {"form": "温斯顿", "isKnown": "false"},
        #     "史密斯": {"form": "史密斯", "isKnown": "true"},
        #     "为了": {"form": "为了", "isKnown": "true"},
        #     "要": {"form": "要", "isKnown": "true"},
        #     "躲": {"form": "躲", "isKnown": "true"},

            "isKnownList": [ "isKnown" ]*17
    }
    return JsonResponse(json)

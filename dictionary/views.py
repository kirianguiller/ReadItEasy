# django imports
from django.shortcuts import render
from django.http import Http404
from .models import MandarinWord

# base imports
import os
import time

# fetch the root project and app path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_dictionary_app = os.path.dirname(os.path.abspath(__file__))

# path languages
path_languages = os.path.join(BASE_DIR, 'data', 'languages')

# fetch path to different data files
path_mandarin = os.path.join(path_languages, 'mandarin')
path_ce_dict = os.path.join(path_mandarin, 'dict', 'tab_cedict_ts.u8')
path_hsk_vocab = os.path.join(path_mandarin, 'hsk_vocab', 'HSK1->6.csv')
path_known_words = os.path.join(path_mandarin, 'known_words', 'user001')
path_neighbors_words = os.path.join(path_mandarin, 'embeddings', 'chinese_embeddings_552books_neighbors.tsv')



dict_similar_words = {}
with open(path_neighbors_words, 'r', encoding='utf-8') as infile:
    for line in infile:
        word, *neighbors = line.split('\t')
        dict_similar_words[word] = neighbors

# fetch the user001 known_words
known_words_user001 = set()
with open(path_known_words, 'r', encoding='utf-8') as infile:
    for line in infile:
        known_words_user001.add(line.rstrip('\n'))
print(known_words_user001)


def show_word_data(request, language, user_word):
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


from django.http import JsonResponse


def getAJAX_user_known_word(request):
    request_word = request.GET.get('word', None)
    print('REQUEST GET', request.GET)
    is_known = False
    print(request_word)
    if request_word in known_words_user001:
        print('IIINNN', request_word)
        is_known = True
    data = {
        'is_known': is_known,
            }
    return JsonResponse(data)

def getAJAX_add_known_word(request):
    added_word = request.GET.get('word', None)
    action = request.GET.get('action', None)
    print('REQUEST GET', request.GET)


    action_done = 'None'

    if action == 'add':
        known_words_user001.add(added_word)
        action_done = 'added'
        print(added_word, action_done)

    elif action == 'remove':
        known_words_user001.remove(added_word)
        action_done = 'remove'
        print(added_word, action_done)

    with open(path_known_words, 'w', encoding='utf-8') as outfile:
        for word in known_words_user001:
            outfile.write(word + '\n')

    data = {
        'action_done': action_done,
            }
    return JsonResponse(data)

# django imports
from django.shortcuts import render
from django.http import Http404

# base imports
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_dictionary_app = os.path.dirname(os.path.abspath(__file__))

path_ce_dict = os.path.join(BASE_DIR, 'data', 'dict', 'tab_cedict_ts.u8')
path_hsk_vocab = os.path.join(BASE_DIR, 'data', 'hsk_vocab', 'HSK1->6.csv')
path_neighbors_words = os.path.join(BASE_DIR, 'data', 'embeddings', 'chinese_embeddings_552books_neighbors.tsv')


def show_word_data(request, language, user_word):
    if language == 'mandarin':
        return mandarin_word_data(request, language=language, user_word=user_word)
    else:
        raise Http404


def mandarin_word_data(request, language, user_word):
    is_in_dict = False

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

            if (user_word == zh_simpl) | (user_word == zh_trad):
                is_in_dict = True
                break

        user_relative_words = False
        with open(path_neighbors_words, 'r', encoding='utf-8') as infile:
            for line in infile:
                word, *neighbors = line.split('\t')
                if word == user_word:
                    user_relative_words = neighbors
                    print('EQUALITY', user_relative_words)



    context = {
        'word': user_word,
        'language': language,
        'zh_simpl': zh_simpl,
        'zh_trad': zh_trad,
        'fayin': fayin,
        'def_list': def_list,
        'is_in_dict': is_in_dict,
        'user_relative_words': user_relative_words,
    }

    return render(request, "dictionary/mandarin_word_data.html", context)


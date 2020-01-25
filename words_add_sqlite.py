import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReadItEasy.settings')

import django
django.setup()

from dictionary.models import MandarinWord

# fetch the root project and other paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path_ce_dict = os.path.join(BASE_DIR, 'data', 'dict', 'tab_cedict_ts.u8')
path_neighbors_words = os.path.join(BASE_DIR, 'data', 'embeddings', 'chinese_embeddings_552books_neighbors.tsv')

dict_similar_words = {}
with open(path_neighbors_words, 'r', encoding='utf-8') as infile:
    for line in infile:
        word, *neighbors = line.split('\t')
        dict_similar_words[word] = neighbors

# delete all object in the database for avoiding duplicates
MandarinWord.objects.all().delete()
#
#
# iterate through our dict
with open(path_ce_dict, 'r', encoding='utf-8') as f:
    for n, line in enumerate(f):
        line = line.rstrip('\n')
        traditional = line.split('\t')[0]
        simplified = line.split('\t')[1]
        pronunciation = line.split('\t')[2]
        definitions = line.split('\t')[3]
        similar_words = dict_similar_words.get(simplified, [])
        similar_words = '/'.join(similar_words)

        new_word = MandarinWord(simplified=simplified,
                                traditional=traditional,
                                pronunciation=pronunciation,
                                definitions=definitions,
                                similar_words=similar_words,
                                )
        new_word.save()
#
        if n % 100==0:
            print(n)
#
#

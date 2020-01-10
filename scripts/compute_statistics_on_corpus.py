import os
import time
import pickle
import re
import jieba
from collections import Counter

def get_chinese(text):
    """process a text to remove all non chinese character"""
    filtrate = re.compile(u'[^\u4E00-\u9FA5]') # non-Chinese unicode range
    text = filtrate.sub(r'', text) # remove all non-Chinese characters
    return text


def rmv_not_chinese(counter):
    """remove non chinese entries in a word frequency counter"""
    for key in counter.copy().keys():
        if get_chinese(key) == '':
            del counter[key]
    return counter


# fetch the root project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# jieba initialization
jieba.initialize()



# fetch path to different data files
path_mandarin_books = os.path.join(BASE_DIR, 'data', 'books', 'mandarin')
path_corpus_stats = os.path.join(BASE_DIR, 'data', 'statistics')

if not os.path.isdir(path_corpus_stats):
    os.makedirs(path_corpus_stats)

# process sentences tokenization
list_times = []
for n, file in enumerate(os.listdir(path_mandarin_books)):
    t1 = time.time()
    corpus_freqs = Counter({})
    path_file = os.path.join(path_mandarin_books, file)
    with open(path_file, 'r', encoding='utf-8') as infile:
        txt = infile.read()
        tokens_jieba = jieba.cut(txt, cut_all=False, HMM=True)
        corpus_freqs += Counter(tokens_jieba)

    # get time information
    t2 = time.time()
    book_process_time = t2-t1
    list_times.append(book_process_time)

n_books = n+1
print("\nSentences tokenized !")
print("{} seconds in total and {} seconds per book".format(sum(list_times),sum(list_times)/n_books))

corpus_freqs = rmv_not_chinese(corpus_freqs)
corpus_size = sum(corpus_freqs.values())


# for the most commun words in the counter, compute the relative frequence (in percentage)
# ... and the rank
size_limit = 100000
meta_dict = {}
for n, (key, value) in enumerate(corpus_freqs.most_common(size_limit)):
    corpus_rel_freq = 100*value/corpus_size
    corpus_rank = n+1
    meta_dict[key] = [corpus_rank, corpus_rel_freq]

# save the data in the path
name_corpus_stats = 'sample_corpus_stats.pkl'
path_corpus_meta = os.path.join(path_corpus_stats, name_corpus_stats)
with open(path_corpus_meta, 'wb') as f:
    pickle.dump(meta_dict, f, pickle.HIGHEST_PROTOCOL)
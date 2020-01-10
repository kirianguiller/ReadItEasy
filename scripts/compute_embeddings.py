import os
import time
import re
import jieba
from gensim.models import Word2Vec


# jieba initialization
jieba.initialize()

# fetch the root project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# fetch path to different data files
path_mandarin_books = os.path.join(BASE_DIR, 'data', 'books', 'mandarin')
path_embeddings = os.path.join(BASE_DIR, 'data', 'embeddings')

if not os.path.isdir(path_embeddings):
    os.makedirs(path_embeddings)


# for removing not needed punctuation like tab and comma
useless_punctuation = ''.join(['　', '\-', '\t'])

# process sentences tokenization
print("\nSentences tokenization ...")
tokenized_sentences = []
list_times = []
for n, file in enumerate(os.listdir(path_mandarin_books)):
    t1 = time.time()
    path_file = os.path.join(path_mandarin_books, file)
    with open(path_file, 'r', encoding='utf-8') as infile:
        txt = infile.read()

        # all our books start with a paragraph with meta. The following delimiter
        # allows us to know when the book start
        txt = txt.split("------章节内容开始-------")[-1]

        # remove useless punctuation from the book
        cleaned_txt = re.sub('[{}]'.format(useless_punctuation), '', txt)

        # split by line
        lines = cleaned_txt.split('\n')

        # tokenize by line with jieba
        for line in lines:
            if line:
                line_tokens = jieba.cut(line, cut_all=False, HMM=True)
                tokenized_sentence = [token for token in line_tokens]
                tokenized_sentences.append(tokenized_sentence)

    t2 = time.time()
    book_process_time = t2-t1
    list_times.append(book_process_time)
n_books = n+1
print("\nSentences tokenized !")
print("{} seconds in total and {} seconds per book".format(sum(list_times),sum(list_times)/n_books))

print('\nComputing Word2Vec ...')
model = Word2Vec(tokenized_sentences, window=5)
print('\nWord2Vec is computed !')

word_vectors = model.wv
name_model = 'mandarin_embeddings_{}book_model.tsv'.format(n_books)
path_model = os.path.join(path_embeddings, name_model)
word_vectors.save_word2vec_format(path_model)

print('model saved at path : {}'.format(path_model))

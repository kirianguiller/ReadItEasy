from django.shortcuts import render, redirect
from .forms import formText
from django.http import HttpResponse
from collections import Counter

# Create your views here.

import jieba
import os

path_books = "data/books/"
path_books = os.path.abspath(path_books)
jieba.initialize()
path_ce_dict = "data/dict/tab_cedict_ts.u8"
path_ce_dict = os.path.abspath(path_ce_dict)
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

# @bp.route("/")
# def index():
#     text = session.get("processed_text")
#     if text:
#         seg_list_hmmtrue = jieba.cut(session['processed_text'])
#         session['processed_text'] = ' '.join(seg_list_hmmtrue)
#         return render_template("read/show_text.html")
#     else:
#         return render(url_for("read.upload"))


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
    with open(path_book, 'r') as f:
        full_txt = f.read()
    txt = full_txt[:10000]
    tokens = jieba.cut(txt)
    freqs = Counter(jieba.cut(full_txt))
    # txt = ' '.join(tokens)
    txt = ''
    list_english_def = []
    list_words = []
    for token in tokens:
        if token =='\n':
            token = '@$$@'
        list_words.append(token)
        list_english_def.append(sim2cedict.get(token, ['-']*4))

    zip_list = zip(list_words, list_english_def)
    context = {
        "id_book": id_book,
        'zip_list': zip_list,
        "freqs": freqs.most_common(1000),
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



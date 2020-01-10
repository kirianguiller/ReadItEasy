#-*- coding: utf8 -*-
# Script for the search of one character or one word which return its index

import jieba

text = input("Please input your text : ")
choice = input("A character(c) or a word(w) ? : ")

def findChara(text):
    chara = str(input("\nPlease input the caracter you want to search :"))
    count_c = 0
    text_list_c = list(text)

    for each_char in text_list_c:
        count_c += 1
        if each_char == chara:
            print(each_char, count_c-1)

def findWord(text):
    word = str(input("\nPlease input the word you want to search : "))
    count_w = 0
    text_list_w = jieba.cut(text, cut_all = False)

    for each_word in text_list_w:
        count_w += 1
        if each_word == word:
            print(each_word, count_w-1)

if choice == "c":
    findChara(text)
else:
    findWord(text)
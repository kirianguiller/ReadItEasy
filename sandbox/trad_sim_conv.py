#-*- coding: utf8 -*-
# Script for the conversion (traditionnal & simplified) using "OpenCC"

# You need to install the module OpenCC by "pip install opencc-python-reimplemented==0.1.4"
# Attention : do not use "pip install opencc" which doesn't work

import opencc

choice = input("To convert the traditional Chinese into the simplified, enter 't2s' ; and vice versa 's2t' : ")
text = input("Enter the text you want to convert : ")
tache = opencc.OpenCC(choice)
print(tache.convert(text))
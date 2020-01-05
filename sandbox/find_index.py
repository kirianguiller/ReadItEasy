#-*- coding: utf8 -*-
# Script destiné à la recherche d'un caractère qui renvoie son ou ses index

texte = input("Please input your text : ")
cara = str(input("\nPlease input the caracter you want to search :"))
count = 0
texte_liste = list(texte)

for each_char in texte_liste:
    count += 1
    if each_char == cara:
        print(each_char, count-1)
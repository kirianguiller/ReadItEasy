#-*- coding: utf8 -*-
# Script destiné à la convertion du chinois traditionnel & simplifié utilisant "OpenCC"

# Il faut install la librairie Opencc par "pip install opencc-python-reimplemented==0.1.4"
# Veillez à ne pas exécuter "pip install opencc" qui ne marche pas.

# à implementer dans le site prochainement
import opencc

choice = input("Pour convertir le traditionnel en simplifié, tapez 't2s' et vice versa 's2t' : ")
texte = input("Entrez votre texte à convertir : ")
tache = opencc.OpenCC(choice)
print(tache.convert(texte))
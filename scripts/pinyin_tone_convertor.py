path_hsk_vocab = """/home/wran/plurital/ReadItEasy/data/languages/mandarin/hsk_vocab/HSK1->6.csv"""
word2hsk = {}
with open(path_hsk_vocab, 'r', encoding='utf-8') as f:
    for n, line in enumerate(f):
        if n == 0:
            pass
        else:
            hsk_level, word = line.split(',')
            word2hsk[word.rstrip('\n')] = int(hsk_level)


path_to_dict = """/home/wran/plurital/ReadItEasy/data/languages/mandarin/dict/tab_cedict_ts.u8"""
path_to_extended_dict = """/home/wran/plurital/ReadItEasy/data/languages/mandarin/dict/extended_dict.u8"""
with open(path_to_dict, 'r', encoding='utf-8') as infile, open(path_to_extended_dict, 'w') as outfile:
    for line in infile:
        line = line.rstrip('\n')
        splitted_line = line.split('\t')
        zh_trad = splitted_line[0]
        zh_simpl = splitted_line[1]
        pronunciation = splitted_line[2]
        definitions = splitted_line[3]
        hsk_level = word2hsk.get(zh_simpl, 0)
        new_pronunciation = pinyin_tone_convertor(pronunciation)

        new_line = [zh_trad, zh_simpl, pronunciation, new_pronunciation, str(hsk_level), definitions]

        outfile.write('\t'.join(new_line) + '\n')


pinyin_conversion = {
    'a' :['ā', 'á', 'ǎ', 'à', 'a'],
    'e' :['ē', 'é', 'ě', 'è', 'e'],
    'o' :['ō', 'ó', 'ǒ', 'ò', 'o'],
    'u:':['u:1', 'ǘ', 'ǚ', 'ǜ', 'u:5'],
    'u' :['ū', 'ú', 'ǔ', 'ù', 'u'],
    'i' :['ī', 'í', 'ǐ', 'ì', 'i'],

}


def pinyin_tone_convertor(pronunciation):
    new_pronunciation = []
    for syllabe in pronunciation.split(' '):

        if syllabe[-1] not in ['1', '2', '3', '4', '5']:
            new_pronunciation.append(syllabe)
            continue

        else:
            for old_vowel in pinyin_conversion:
                if old_vowel in syllabe:
                    syllabe_accent = int(syllabe[-1]) - 1
                    syllabe_pronun = syllabe[:-1]
                    new_vowel = pinyin_conversion[old_vowel][syllabe_accent]
                    new_syllabe = syllabe_pronun.replace(old_vowel, new_vowel)
                    new_pronunciation.append(new_syllabe)
                    break
    return ' '.join(new_pronunciation)



pinyin_tone_convertor('zhong1 wen2')
# 'zhōng wén'

pinyin_tone_convertor('A A zhi1')
# A A zhī

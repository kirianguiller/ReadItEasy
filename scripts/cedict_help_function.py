import pandas as pd
import csv


path_extended_dict = "/home/wran/plurital/ReadItEasy/data/languages/mandarin/dict/extended_dict.u8"
path_extended_dict_hsk_only = "/home/wran/plurital/ReadItEasy/data/languages/mandarin/dict/extended_dict_hsk_only.u8"

df = pd.read_csv(path_extended_dict, sep="\t", header=0, names=["trad", "sim", "pinyin_num", "pinyin", "hsk", "def"])
df['pinyin']=df['pinyin'].str.lower()
df['pinyin_num']=df['pinyin_num'].str.lower()
df.loc[df['hsk'] == 0, 'hsk'] = 7
df = df.sort_values(["hsk", "sim"], ascending=(True, True))
df.to_csv(path_extended_dict, sep="\t", index=False, quoting=csv.QUOTE_NONE)


df_hsk_only = df[df["hsk"]!=7]
df_hsk_only.to_csv(path_extended_dict_hsk_only, sep="\t", index=False, quoting=csv.QUOTE_NONE)
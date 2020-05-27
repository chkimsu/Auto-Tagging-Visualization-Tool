import os
import sys

from nlpre import titlecaps, dedash, identify_parenthetical_phrases
from nlpre import replace_acronyms, replace_from_dictionary
from shutil import copyfile
import csv
import pandas as pd
import warnings

warnings.filterwarnings(action='ignore')
pd.set_option('display.max_columns', 500)


os.chdir('/data01/CSB/CSB_Jupyter/ATVT/Xml_parsing')
parsing = pd.read_csv(str(sys.argv[1])+'_Parsing.csv')


os.chdir('/data01/CSB/CSB_Jupyter/ATVT/auto-tagging-master/Preprocessing/Text_Normalize/NLPre-master/CSB-NLpre/')

with open(str(sys.argv[1])+'.txt','w') as file:
    for line in parsing.PROP_OBJECT_NAME:
        file.writelines(line+'\n')
file.close()

import pandas as pd

data = pd.read_csv('/data01/CSB/CSB_Jupyter/ATVT/auto-tagging-master/Dictionary/NLPre_dictionary/MeSH_two_word_lexicon3.csv')
data = data.drop(['Unnamed: 0'], axis=1)
data.columns = ['term', 'replacement']
data.to_csv('/data01/CSB/CSB_Jupyter/ATVT/auto-tagging-master/Dictionary/NLPre_dictionary/MeSH_two_word_lexicon3.csv')


leng = pd.read_csv(str(sys.argv[1])+'.txt')
f1 = open(str(sys.argv[1])+'.txt','rb')
   
    
for i in range(len(leng)+1):
    text1 = str(f1.readline())
    
    
    ABBR = identify_parenthetical_phrases()(text1)
    parsers = [dedash(), titlecaps(), replace_acronyms(ABBR),
               replace_from_dictionary(f_dict = '/data01/CSB/CSB_Jupyter/ATVT/auto-tagging-master/Dictionary/NLPre_dictionary/MeSH_two_word_lexicon3.csv',prefix="MeSH_")]

    for f in parsers:
        text = f(text1)

    with open(str(sys.argv[1])+'_result.txt', 'a') as file:
        file.writelines(text+'\n')
    file.close()
    
PROP_OBJECT_NAME = pd.read_csv(str(sys.argv[1])+'_result.txt', delimiter='             ', header = None) 
PROP_OBJECT_NAME.columns = ['PROP_OBJECT_NAME']

parsing[['PROP_OBJECT_NAME']] = PROP_OBJECT_NAME

parsing.to_csv(str(sys.argv[1])+'_result.csv')
print(parsing)
import sys



import os
os.chdir('/data01/CSB/CSB_Jupyter/ATVT/Xml_parsing/')

import xml.etree.ElementTree as elemTree
import pandas as pd
pd.set_option('display.max_columns', 500)

tree = elemTree.parse(str(sys.argv[1])+'.xml')
root = tree.getroot()
Objects = root.findall('Objects')

a = {}
for child in root.iter('Object'):
    
    for user in child:
        for property in user:
            if property.attrib == {'Id': 'PROP_OBJECT_NAME', 'Tag': 'BACNET_APPLICATION_TAG_CHARACTER_STRING'}: 
                for xx in property:
                    
                    a[child.attrib['Type']+'_'+child.attrib['Instance']] = xx.text
       


result = pd.DataFrame(list(a.items()))
result.columns = ['PROP_OBJECT_NAME', 'BACNET_APPLICATION_TAG_CHARACTER_STRING']

import xml.etree.ElementTree as elemTree
import pandas as pd
 
tree = elemTree.parse(str(sys.argv[1])+'.xml')
root = tree.getroot()
Objects = root.findall('Objects')

a = {}
for child in root.iter('Object'):
    
    for user in child:
        for property in user:
            if property.attrib == {'Id': 'PROP_DESCRIPTION', 'Tag': 'BACNET_APPLICATION_TAG_CHARACTER_STRING'}: 
                for xx in property:
                    
                    a[child.attrib['Type']+'_'+child.attrib['Instance']] = xx.text
       


result2 = pd.DataFrame(list(a.items()))
result2.columns = ['PROP_OBJECT_NAME', 'BACNET_APPLICATION_TAG_CHARACTER_STRING']


import xml.etree.ElementTree as elemTree
import pandas as pd
 
tree = elemTree.parse(str(sys.argv[1])+'.xml')
root = tree.getroot()
Objects = root.findall('Objects')

a = {}
for child in root.iter('Object'):
    
    for user in child:
        for property in user:
            if property.attrib == {'Id': 'PROP_OBJECT_IDENTIFIER', 'Tag': 'BACNET_APPLICATION_TAG_OBJECT_ID'}: 
                for xx in property:
                    
                    a[child.attrib['Type']+'_'+child.attrib['Instance']] = xx.text
       


result3 = pd.DataFrame(list(a.items()))
result3.columns = ['PROP_OBJECT_IDENTIFIER', 'PROP_OBJECT_IDENTIFIER']


final = pd.concat([result3, result, result2], axis=1)
final = final.iloc[:, [0, 3,5]]
final.columns = ['PROP_OBJECT_IDENTIFIER', 'PROP_OBJECT_NAME', 'PROP_DESCRIPTION']
final.to_csv(str(sys.argv[1])+'_Parsing.csv')

print(final)

#################3
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


#################

import os
import pandas as pd
import sys
import ktrain
from ktrain import text
import numpy as np


os.chdir('/data01/CSB/CSB_Jupyter/ATVT/auto-tagging-master/Preprocessing/Text_Normalize/NLPre-master/CSB-NLpre/')
data = pd.read_csv(str(sys.argv[1])+'_result.csv')



data = data.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1)
data = data.fillna('0')
data['BERT'] = data['PROP_OBJECT_IDENTIFIER']+'_'+data['PROP_OBJECT_NAME']+'_'+data['PROP_DESCRIPTION']

databert = data[['BERT']]


os.chdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling')
predictor = ktrain.load_predictor('csbpredictor')

for i in range(len(databert)):
    databert.loc[i,'label'] = predictor.predict(databert.iloc[i,0])

    
data['label'] = databert['label']


print(data)

data.to_csv(str(sys.argv[1])+'_final.csv')
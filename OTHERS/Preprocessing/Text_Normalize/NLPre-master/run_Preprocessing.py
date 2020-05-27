from nlpre import titlecaps, dedash, identify_parenthetical_phrases
from nlpre import replace_acronyms, replace_from_dictionary
from shutil import copyfile
import csv

f1 = open('./Dataset/Raw_Data/testdata.txt','rb')
text1 = str(f1.read())

ABBR = identify_parenthetical_phrases()(text1)
parsers = [dedash(), titlecaps(), replace_acronyms(ABBR),
           replace_from_dictionary(prefix="MeSH_")]

for f in parsers:
    text = f(text1)

text2 = text

## To Do : 여러줄 바꿈 기능 필요, 여러줄 나누어서 파일로 변환하기 필요
with open("/tmp/pycharm_project_580/Preprocessing/Text_Normalize/NLPre-master/test2.txt", "w") as file:
    for line in text2:
        file.writelines(line)
file.close()

## 완료된 결과물 Dataset에 전달
copyfile('/tmp/pycharm_project_580/Preprocessing/Text_Normalize/NLPre-master/test2.txt','/tmp/pycharm_project_580/Dataset/Traning_Dataset/test2.txt')

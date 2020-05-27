import pandas as pd
import os
import os
# import ktrain and the ktrain.text modules
from ktrain import text
import ktrain
import numpy as np 
import pandas as pd
import math 
import numpy as np
from sklearn import preprocessing



#### 사전 작업으로 temp폴더에 AHUs, Boilers, Chillers등의 equip별 폴더를 만들고, 각 폴더안의 폴더명과 똑같은 txt 파일을 넣는다. 이 txt파일안에는 
#### label들이 들어있다. 즉, temp/AHUs/AHUs.txt 는 장혁대리님이 만드신 AHU Label들이 들어있다. 
#### 그 다음, train, test 폴더에다가, 각각의 label들을 다 분리해서 label별 폴더를 만든다. 

os.chdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/label/temp/')

for i in range(len(os.listdir())):
    data = pd.read_csv(os.listdir()[i]+'/'+os.listdir()[i]+'.txt', header = None)
    for j in range(len(data)):
        if data.iloc[j,0] in os.listdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/label/train'):
            continue
        else : 
            os.mkdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/label/train/'+data.iloc[j,0])
             os.mkdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/label/test/'+data.iloc[j,0])
                

                
#### fuzzywuzzy로 만든 label 붙인 데이터를 가지고 온다. 데이터에서 ahu label 별로 데이터를 분리해서 저장한다. 
                
os.chdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling')
data = pd.read_csv('NAE08_fuzzy.csv')
os.chdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/data')
data = data[~pd.isnull(data.label)]
data = data.drop(['Unnamed: 0'], axis=1)
data = data.fillna('0')
data['data'] = data['PROP_OBJECT_IDENTIFIER']+'_'+data['PROP_OBJECT_NAME']+'_'+data['PROP_DESCRIPTION']
data = data[['data', 'label']]

for i in range(len(data.label.unique())):
    np.savetxt(data.label.unique()[i]+'.txt', data[data.label == data.label.unique()[i]].data.values, delimiter="      ", fmt="%s")
    
    

#### 저장한 각각의 데이터를 한줄한줄 분리하여 train, test  폴더의 각각의 label에다가 한줄한줄 넣기. 
    
    
    
txt = []
for i in range(len(os.listdir())):
    if '.txt' in os.listdir()[i]:
        txt.append(os.listdir()[i])
        
for i in range(len(txt)):
    a = []
    f = open(txt[i], 'r')
    while True:
        line = f.readline()
        a.append(line)
        if not line: break
    f.close()
os.chdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/data')


for i in range(len(txt)):
    a = []
    f = open(txt[i], 'r')
    while True:
        line = f.readline()
        a.append(line)
        if not line: break
    f.close()
    
    
    for j in range(len(a)):
        with open('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/label/train/'+txt[i][:-4]+'/'+txt[i][:-4]+str(j+1)+'.'+'txt', 'w') as file:
            file.write(a[j])
       
for i in range(len(txt)):
    a = []
    f = open(txt[i], 'r')
    while True:
        line = f.readline()
        a.append(line)
        if not line: break
    f.close()
    
    
    for j in range(len(a)):
        with open('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/label/test/'+txt[i][:-4]+'/'+txt[i][:-4]+str(j+1)+'.'+'txt', 'w') as file:
            file.write(a[j])
       
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
import numpy as np


#### 데이터 가져오기(이름, description 등)

data = pd.read_csv('NAE08_result.csv')
data = data.drop(['Unnamed: 0', 'label'], axis = 1)  # 원래 붙여져있던 label떼내기.
data = data[~pd.isnull(data.PROP_DESCRIPTION)]


c = list(data['PROP_DESCRIPTION'])

a = pd.read_csv('AHUs.txt', header=None)  #### AHU haystack label(장혁 대리님 새로만드신것) 모아둔 txt 파일 가져오기. 
a.columns = ['a']
a = list(a.a)

b = []


#### fuzzywuzzy적용

finaldata = pd.DataFrame(columns=('rawdata', 'label'), index = range(len(c)))


for i in range(len(c)):
    for j in range(len(a)):
        
        b.append(fuzz.ratio(c[i], a[j]))
    finaldata.loc[i, 'rawdata'] = c[i]
    finaldata.loc[i, 'label'] = a[b.index(max(b))]
    b.clear()



#### fuzzywuzzy의 경우 None값에 대해서는 None으로 뱉어주지만, 
#### None 데이터가 하나라도 나오면 그 다음 데이터는 무엇이든 상관없이 None 으로 모두 뱉어준다. 이 부분 조심. 
#### fuzzywuzzy로 붙인 label을 원본데이터에 다시 붙이고 저장. 

data['label'] = None

rawdata = pd.read_csv('NAE08_result.csv')
rawdata['label'] = None

j = 0
for i in list(data.index):
    rawdata.loc[i, 'label'] = finaldata.iloc[j,1]
    j +=1
    
rawdata.drop(['Unnamed: 0'], axis = 1).to_csv('NAE08_fuzzy.csv')
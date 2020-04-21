from datetime import datetime
import os
import pandas as pd
import sys
import ktrain
from ktrain import text
import numpy as np
import pymysql
from datetime import datetime
import time
from nlpre import titlecaps, dedash, identify_parenthetical_phrases
from nlpre import replace_acronyms, replace_from_dictionary
from shutil import copyfile
import requests


## configure 파일은 경로 설정 굳이 안해줘도된다. 파이썬 파일과 같은 경로에 있는 것으로. 
## 전역변수 선언하는 부분이라 굳이 모듈화할 필요는 없다.
f = pd.read_csv('/data01/CSB/CSB_Jupyter/ATVT/ariflow/dags/reinferencing_configure.csv',encoding='utf-8')
variable = []
for i in range(len(f)):
    variable.append(f.Variable[i]) 

data = []
for i in range(len(f)):
    data.append(f.PATH[i]) 

for i in range(len(variable)):
    globals()[variable[i]] = data[i] 
    

    
    
## db에서 데이터 빼오기
def db_connect(command):
    
    if command == 'ALL':
        conn = pymysql.connect(host=host, port=int(port),
                                               user=user, password=password, db=db, charset=charset,
                                               cursorclass=pymysql.cursors.DictCursor)
        curs = conn.cursor()

        sql = sql_0
        curs.execute(sql)
        data0 = pd.DataFrame(curs.fetchall())

        sql = sql_1
        curs.execute(sql)
        data1 = pd.DataFrame(curs.fetchall())

        sql = sql_2
        curs.execute(sql)
        data2 = pd.DataFrame(curs.fetchall())

        data = pd.concat([data0, data1,data2])
        data = data.reset_index()

        return data

    elif command == 'CHANGED':
        
        conn = pymysql.connect(host=host, port=int(port),
                                           user=user, password=password, db=db, charset=charset,
                                           cursorclass=pymysql.cursors.DictCursor)
        curs = conn.cursor()

        sql = sql_2
        curs.execute(sql)
        data = pd.DataFrame(curs.fetchall())
        
        return data
        

## 결과저장용 빈 데이터프레임 생성    
def empty_dataframe(data):
    
    string = data[column1] + '_' + data[column2] + '_' + data[column3]
    result = pd.DataFrame(index=range(0, len(data)),
                            columns=[column4, column5, column6, column7, column8, column9, column10])
    result[[column4, column5, column6, column7, column8, column9, column10]] = data[[column4, column5, column6, column7, column8, column9, column10]]
    string = pd.DataFrame(string)
    string.columns = ['data']
    
    return string, result



## nlpre로 축약어 풀어주기
def nlpre_execute(leng, f, f1):
    
    for i in range(len(leng)+1):
        text1 = str(f1.readline())


        ABBR = identify_parenthetical_phrases()(text1)
        parsers = [dedash(), titlecaps(), replace_acronyms(ABBR),
                    replace_from_dictionary(f_dict =dictionary ,prefix=prefix)]

        for f in parsers:
            text = f(text1)

        with open(inferresult_text, 'a') as file:
            file.writelines(text+'\n')
        file.close()

    return 'nlpre success'




## 실제로 예측하는 부분
def predict(data, string, predictor, equip, result):

    for i in range(len(data)):

        prediction = predictor.predict(string.data[i])
        now = datetime.now()

        for j in equip:
            if prediction.find(j) != -1:
                test = prediction.lstrip(j)
                test = test.lstrip()
                break
        result.loc[i, [column9, column8,column10]] = j, test, now.strftime('%Y-%m-%d %H:%M:%S')


    for i in range(len(result)):
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'


    data[[column4, column5, column6, column7, column8, column9, column10]] = result[[column4, column5, column6, column7, column8, column9, column10]]

    return result, data



## API 전달하는 부분
def API_Request(data):

    headers = {'Content-Type': content_type}
    for i in range(len(data)):
        res = requests.post(url, headers=headers, data=data.iloc[i, :].to_json())
        
    return 'API REQUESTED'






## 메인 함수
def reinferencing(command):
    
      
    ## 모델 호출 
    predictor = ktrain.load_predictor(predictor_path)    
    
    ## command에 따라서 다른 데이터 뽑아오기.           
    data = db_connect(command)
        
    ## db에 데이터 없을 경우
    if data.empty == True:
        return 'There is no data'

    else: 

        os.chdir(PATH1)           
        ## 결과저장용 빈 데이터프레임 생성. 
        string, result = empty_dataframe(data)

        ## 데이터 조작 부분
        with open(infer_text,'w') as file:
            for line in string.data:
                file.writelines(line+'\n')
            file.close()

        leng = pd.read_csv(infer_text)
        f1 = open(infer_text,'rb')

        ## nlpre
        nlpre_execute(leng, f, f1)
        
        ## 다 쓴 폴더는 삭제해주기. 
        os.remove(infer_text)
        os.remove(inferresult_text)

        ## model version에서 앞의 날짜부분은 현재시간으로, version값은 configure로
        now = datetime.now()
        result.model_version = now.strftime('%Y.%m.%d.')+ version


        equip = list(equipments)


        ## 예측 부분
        result, data = predict(data, string, predictor, equip, result)
        
        ## API에 json파일 보내는 부분
        API_Request(data)
        
  
        return 'Reinferencing is Done'


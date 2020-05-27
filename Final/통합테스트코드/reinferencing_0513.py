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

datav = []
for i in range(len(f)):
    datav.append(f.PATH[i]) 

for i in range(len(variable)):
    globals()[variable[i]] = datav[i] 
    

    
    
## db에서 데이터 빼오기
def db_connect(command, yyscommand):
    
    if command == 'ALL':
        
        if yyscommand == 'yys':
            
            conn = pymysql.connect(host=host, port=int(port),
                                                   user=user, password=password, db=db, charset=charset,
                                                   cursorclass=pymysql.cursors.DictCursor)
            curs = conn.cursor()

            sql0 = sql_0  ## nnn
            curs.execute(sql0)
            data0 = pd.DataFrame(curs.fetchall())

            sql1 = sql_1  ## nyn
            curs.execute(sql1)
            data1 = pd.DataFrame(curs.fetchall())

            sql2 = sql_2  ## yys
            curs.execute(sql2)
            data2 = pd.DataFrame(curs.fetchall())

            sql3 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'y' AND inferenced = 'f';  '''
            curs.execute(sql3)
            data3 = pd.DataFrame(curs.fetchall())

            sql4 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'n' AND inferenced = 'f';  '''
            curs.execute(sql4)
            data4 = pd.DataFrame(curs.fetchall())

            data = pd.concat([data0, data1,data2,data3,data4])
            data = data.reset_index(drop=True)

        else:
            
            
            conn = pymysql.connect(host=host, port=int(port),
                                                   user=user, password=password, db=db, charset=charset,
                                                   cursorclass=pymysql.cursors.DictCursor)
            curs = conn.cursor()

            sql0 = sql_0  ## nnn
            curs.execute(sql0)
            data0 = pd.DataFrame(curs.fetchall())

            sql1 = sql_1  ## nyn
            curs.execute(sql1)
            data1 = pd.DataFrame(curs.fetchall())

            sql3 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'y' AND inferenced = 'f';  '''
            curs.execute(sql3)
            data3 = pd.DataFrame(curs.fetchall())

            sql4 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'n' AND inferenced = 'f';  '''
            curs.execute(sql4)
            data4 = pd.DataFrame(curs.fetchall())

            

            data = pd.concat([data0, data1,data3,data4])
            data = data.reset_index(drop=True)

            
            
    elif command == 'CHANGED':
        
        
        if yyscommand == 'yys':
        
            conn = pymysql.connect(host=host, port=int(port),
                                               user=user, password=password, db=db, charset=charset,
                                               cursorclass=pymysql.cursors.DictCursor)
            curs = conn.cursor()

            sql = sql_2  ## yys
            curs.execute(sql)
            data2 = pd.DataFrame(curs.fetchall())


            sql3 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'y' AND inferenced = 'n';  '''
            curs.execute(sql3)
            data3 = pd.DataFrame(curs.fetchall())


            sql4 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'y' AND inferenced = 'f';  '''
            curs.execute(sql4)
            data4 = pd.DataFrame(curs.fetchall())

            data = pd.concat([data2,data3,data4])
            data = data.reset_index(drop=True)

        
        else: 
            
    
            conn = pymysql.connect(host=host, port=int(port),
                                               user=user, password=password, db=db, charset=charset,
                                               cursorclass=pymysql.cursors.DictCursor)
            curs = conn.cursor()

            sql3 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'y' AND inferenced = 'n';  '''
            curs.execute(sql3)
            data3 = pd.DataFrame(curs.fetchall())


            sql4 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'y' AND inferenced = 'f';  '''
            curs.execute(sql4)
            data4 = pd.DataFrame(curs.fetchall())

            data = pd.concat([data3,data4])
            data = data.reset_index(drop=True)
    
    
    
    
    index = []

    for i in range(len(data)):
        if (data.loc[i, 'id'] == 'null') | (data.loc[i, 'description'] == 'null') | (data.loc[i, 'name'] == 'null') | (data.loc[i, 'present_value'] == 'null') | (data.loc[i, 'id'] == '') | (data.loc[i, 'description'] == '') | (data.loc[i, 'name'] == '') | (data.loc[i, 'present_value'] == '') | (data.loc[i, 'id'] == None) | (data.loc[i, 'description'] == None) | (data.loc[i, 'name'] == None) | (data.loc[i, 'present_value'] == None):  
            index.append(i)

    ## 이건 null 혹은 빈 string있는 data
    data_null = data.loc[index].reset_index(drop = True)
    ## 이건 정상 데이터.
    data_notnull = data.loc[list(set(list(data.index)) - set(index))].reset_index(drop=True)



    return data_null, data_notnull

        

        
        
        
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
        
       
    ## IDK로 예측해줄 경우는 Idk로 예측하도록 해주는 코드
    
        if prediction == 'idk':
            
            result.loc[i, [column9, column8,column10]] = 'idk', 'idk', now.strftime('%Y-%m-%d %H:%M:%S')

        ## IDK 외에 나머지 코드
        
        else:      
        
            for j in equip:
                if prediction.find(j) != -1:
                    test = prediction.lstrip(j)
                    test = test.lstrip()
                    break
            result.loc[i, [column9, column8,column10]] = j, test, now.strftime('%Y-%m-%d %H:%M:%S')
    
    
       
    ## IDK 있을 경우에는 자동으로 추론실패로 들어가도록 코드가 짜여 있다. 왜냐하면 IDK는 equip안에 없으므로. 
    ## yys가 있을 경우, 없을 경우 여기 코드에서 고칠건없다. yys자체를 호출하지 않았으므로 index에서도 찾을게 없다. 
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'n') & (result['inferenced'] =='n')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'    
        
        
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'y') & (result['inferenced'] =='n')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'       
        
   
    for i in result[(result['tagged'] == 'y') & (result['changed'] == 'y') & (result['inferenced'] =='s')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 'f'       
        

    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'n') & (result['inferenced'] =='f')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'       
        
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'y') & (result['inferenced'] =='f')].index:
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




### 4가지중에 하나라도 null 혹은 빈 string인 경우. 
def predict_null(result):
    
    
    
    now = datetime.now()
    
    for i in range(len(result)):
        result.inference_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'y') & (result['inferenced'] =='n')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'n') & (result['inferenced'] =='n')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'y') & (result['changed'] == 'y') & (result['inferenced'] =='s')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 'f'

    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'y') & (result['inferenced'] =='f')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'n') & (result['inferenced'] =='f')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
            
    return result








## 메인 함수
def reinferencing(command):
    
      
    ## 모델 호출 
    predictor = ktrain.load_predictor(predictor_path)    
    
    ## command에 따라서 다른 데이터 뽑아오기.  
    ## yyscommand에 따라서 yys 선택여부 달라짐. 
    data_null, data_notnull = db_connect(command, yyscommand = 'yys')
        
    ## db에 데이터 없을 경우
    
    if data_notnull.empty == True:
        
        
        if data_null.empty==True:
        
            return 'There is nothing to do'
        
        else:
            
            data_null = predict_null(data_null)
            data = data_null.copy()
       
            
            
            
            
    else: 

        os.chdir(PATH1)           
        ## 결과저장용 빈 데이터프레임 생성. 
        string, result = empty_dataframe(data_notnull)

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


        equip = ['vfds', 'elec', 'zones', 'ahus', 'vavs', 'chillers', 'boilers', 'tanks']

        
        
        if data_null.empty ==True:
            
            result, data_notnull = predict(data_notnull, string, predictor, equip, result)
            data = data_notnull.copy()
            
        else:
            data_null = predict_null(data_null)
            result, data_notnull = predict(data_notnull, string, predictor, equip, result)
            data = pd.concat([data_null, data_notnull]).reset_index(drop=True)
            
           
        print(time.strftime('%c', time.localtime(time.time())))
       
        ## API에 json파일 보내는 부분
        API_Request(data)
        
  
        return 'Reinferencing is Done'


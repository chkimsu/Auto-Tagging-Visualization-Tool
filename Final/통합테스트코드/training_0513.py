from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
import os
import pandas as pd
import sys
import ktrain
from ktrain import text
import numpy as np
import pymysql
from datetime import datetime
import time
import os
import pandas as pd
import sys
import ktrain
from ktrain import text
import numpy as np
import pymysql
from datetime import datetime
import time
import shutil
import os
import pandas as pd
import sys
import ktrain
from ktrain import text
import numpy as np
import pymysql
from datetime import datetime
import time
import shutil
from nlpre import titlecaps, dedash, identify_parenthetical_phrases
from nlpre import replace_acronyms, replace_from_dictionary
from shutil import copyfile



## 이 부분은 configure에 넣어줄 필요는 없다. 다만, configure파일은 무조건 파이썬 파일과 동일 디렉터리에. 
f = pd.read_csv('/data01/CSB/CSB_Jupyter/ATVT/ariflow/dags/training_configure.csv',encoding='utf-8')
## configure에서 가져온 변수명과 configure data혹은 path들을 할당해준다. 
variable = []
for i in range(len(f)):
    variable.append(f.Variable[i]) 

datav = []
for i in range(len(f)):
    datav.append(f.PATH[i]) 

for i in range(len(variable)):
    globals()[variable[i]] = datav[i] 
    

    
## db에서 데이터 호출하는 함수.     
def db_connect():
    
    conn = pymysql.connect(host=host, port=int(port),
                           user=user, password=passwd, db=db, charset=charset,
                           )

    curs = conn.cursor()
    sql =  ''' SELECT id,description,name,point_ref,equip_ref FROM t_points_atvt 
            WHERE id is not null and description is not null and name is not null and point is not null and equip is not null '''
    curs.execute(sql)
    curs.execute(sql)
    data = pd.DataFrame(curs.fetchall())
    
    return data
        

    
## 데이터 전처리. 
def preprocessing(data):
    
        ## 결과저장용 빈 데이터프레임 생성. 
    data.columns = [column1, column2, column3, column4, column5]
    data['label'] = data[column5] + ' ' + data[column4]
    data['data'] = data[column1] + '_' + data[column3] + '_' + data[column2]
    data = data.drop([column1, column2, column3, column4, column5], axis=1)

    return data

    

## nlpre이용하여 축약어 푸는 과정. 
def nlpre_execute(leng, f, f1):
        
    for i in range(len(leng)+1):
        text1 = str(f1.readline())

        ABBR = identify_parenthetical_phrases()(text1)
        parsers = [dedash(), titlecaps(), replace_acronyms(ABBR),
                   replace_from_dictionary(f_dict = dictionary ,prefix=prefix)]

        for f in parsers:
            text = f(text1)

        with open(PATH2, 'a') as file:
            file.writelines(text+'\n')
        file.close()
    
    nlpre = pd.read_csv(PATH2, delimiter='             ', header = None)
    nlpre.columns = ['data2']

    return nlpre
    

    
## data를 한줄한줄 분리해 놓는것. 
def data_translation(data):
    
    for i in range(len(data.label.unique())):
        np.savetxt(PATH5 + data.label.unique()[i] + '.txt', data[data.label == data.label.unique()[i]].data.values,
               delimiter="      ", fmt="%s")

    os.chdir(PATH5)

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

    return txt



## label별 folder 생성하는 함수
def label_folder():
    
    for i in range(len(os.listdir())):
        if os.listdir()[i] == '.ipynb_checkpoints':
            continue
        else:        

            data = pd.read_csv(os.listdir()[i] + '/' + os.listdir()[i] + '.txt', header=None)
            for j in range(len(data)):
                if data.iloc[j, 0] in os.listdir('../'+PATH3):
                    continue
                elif data.iloc[j, 0] in os.listdir('../'+PATH4):
                    continue
                else:
                    os.mkdir('../'+PATH3 + data.iloc[j, 0])
                    os.mkdir('../'+PATH4 + data.iloc[j, 0])

    return 'label folder'



## 만들어진 디렉터리들에 데이터 집어넣는 과정 (train/test)
def data_to_folder(txt):
    ### train 폴더에 데이터 넣는 것. 
    for i in range(len(txt)):
        a = []
        f = open(PATH5+txt[i], 'r')
        while True:
            line = f.readline()
            a.append(line)
            if not line: break
        f.close()

        for j in range(len(a)):
            with open(PATH3 + txt[i][:-4] + '/' + txt[i][:-4] + str(j + 1) + '.' + 'txt', 'w') as file:
                file.write(a[j])

    ### test 폴더에 데이터 넣는 것. 
    for i in range(len(txt)):
        a = []
        f = open(PATH5+txt[i], 'r')
        while True:
            line = f.readline()
            a.append(line)
            if not line: break
        f.close()

        for j in range(len(a)):
            with open(PATH4+ txt[i][:-4] + '/' + txt[i][:-4] + str(j + 1) + '.' + 'txt', 'w') as file:
                file.write(a[j])
    
    return 'data into folder'



## 실제 학습하는 함수 + 모델저장까지. 
def training():
    
    (x_train, y_train), (x_test, y_test), preproc = ktrain.text.texts_from_folder(os.getcwd(), maxlen=int(PATH16),
        preprocess_mode='bert',
        train_test_names=['train', 'test'],
        )
    model = ktrain.text.text_classifier('bert', train_data=(x_train, y_train), preproc=preproc)
    learner = ktrain.get_learner(model, train_data=(x_train, y_train), val_data=(x_test, y_test), batch_size=int(batchsize))


    learner.fit_onecycle(float(learning_rate), int(epoch))



    predictor = ktrain.get_predictor(learner.model, preproc)

    #### 모델 저장은 다음 디렉터리에 ####

    predictor.save(predictorpath)


    
    
    
def at_cloud_training_task():
    
    ## db에서 데이터 꺼내오는 작업. 
    data = db_connect()
    
    
    ## db에 데이터가 전혀 없으면 Fail을 airflow에 반환. 
    if data.empty == True:
        return 'Fail'
    
    else: 
        
        ## 데이터 전처리
        data = preprocessing(data)
        
        ## 데이터 조작하는 과정. 
        with open(PATH0,'w') as file:
            for line in data.data:
                file.writelines(line+'\n')
        file.close()

        leng = pd.read_csv(PATH0)
        f1 = open(PATH0,'rb')
        
        ##nlpre 하는과정.
        nlpre = nlpre_execute(leng, f, f1)

       
        data = pd.concat([data, nlpre], axis=1)
        data = data.drop(['data'], axis=1)
        data.columns = ['label', 'data']

        ##필요없는 파일 삭제. 
        os.remove(PATH0)
        os.remove(PATH2)


        ## NULL값이 있을 경우 대비
        data = data[~pd.isnull(data.label)]
        data = data.fillna('0')
        os.mkdir(PATH5)

        ## lable별 폴더 생성
        txt = data_translation(data)

        os.chdir('../')

        ## 상대경로로 train/test 빈 폴더 만들기
        os.mkdir(PATH3)
        os.mkdir(PATH4)
        ## temp폴더. 
        os.chdir(temp)


        ## 장혁 대리님 주신 것으로, Bert용 디렉터리 만들기. 
        label_folder()

        os.chdir('../')
       
        ###### 여기다가 train/test를 나누는 코드를 원래 넣어줘야 함. 그리고 밑에 코드도 수정해야 함. 
        ###### 지금은 train = test로 실행함. 
        
        
        
        
        
        
               
    
        #################################################
         
        ### training, test 폴더에 데이터 넣는 것. 이 함수에는 원래, train/test는 다르게 넣어야 한다. 
        data_to_folder(txt)

        ### 실제로 학습하는 과정.       
        training()

        #### DB에서 가지고 온 학습데이터 및 코드 재실행때 문제 될만한 폴더는 모두 지워준다. ####
        shutil.rmtree(PATH3)
        shutil.rmtree(PATH4)
        shutil.rmtree(PATH5)
               
        return 'Success'

    
dag = DAG(dags_name, description=description,
          schedule_interval=schedule,
          start_date=datetime(int(now_year), int(now_month), int(now_date)), catchup=False)

dummy_operator = DummyOperator(task_id=dummytask_id, retries=1, dag=dag)

at_cloud_training_operator = PythonOperator(task_id=pythontask_id,
                                            python_callable=at_cloud_training_task, dag=dag)

dummy_operator >> at_cloud_training_operator
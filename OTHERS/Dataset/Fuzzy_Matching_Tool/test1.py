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

def at_gateway_inference_task():
            ## 모델 불러오는 부분

            os.chdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling')
            predictor = ktrain.load_predictor('csbpredictor')

            ## tagged = n 인 data만 불러온다.
            conn = pymysql.connect(host='192.168.21.6', port=3306,
                                   user='root', password='ntels', db='nise', charset='utf8',
                                   cursorclass=pymysql.cursors.DictCursor)

            curs = conn.cursor()
            sql = "SELECT * FROM auto_tagging where tagged = 'n' "
            curs.execute(sql)
            data = pd.DataFrame(curs.fetchall())

            ## 결과저장용 빈 데이터프레임 생성.
            string = data['id'] + '_' + data['description'] + '_' + data['name']
            result = pd.DataFrame(index=range(0, len(data)),
                                  columns=['tagged', 'changed', 'model_version', 'point', 'equip', 'inference_time'])
            result[['tagged', 'changed', 'model_version', 'point', 'equip', 'inference_time']] = data[
                ['tagged', 'changed', 'model_version', 'point', 'equip', 'inference_time']]

            ## changed는 하드코딩으로 모두 n으로, model_version =2.0으로 하드코딩.
            result.changed = 'n'
            result.model_version = 2.0

            ## 예측을 해주는 메인 파트, point, equip을 예측해주며, 분리해주는 역할까지. 뿐만아니라, inferencing_time을 현재시간으로 맞추어 출력.

            equip = ['vfds', 'elec', 'zones', 'ahus', 'vavs', 'chillers', 'boilers', 'tanks']

            for i in range(len(data)):
                if data.loc[i, 'tagged'] == 'y':
                    continue
                else:
                    prediction = predictor.predict(string[i])
                    now = datetime.now()

                    for j in equip:
                        if prediction.find(j) != -1:
                            test = prediction.lstrip(j)
                            test = test.lstrip()
                            break
                    result.loc[i, ['equip', 'point', 'inference_time']] = j, test, now.strftime('%Y-%m-%d %H:%M:%S')

            ## tagged는 포인트 값이 NULL이 아니면 y로 변환
            for i in range(len(result)):
                if result.loc[i, 'point'] != None:
                    result.loc[i, 'tagged'] = 'y'

            ## 결과저장용 table을 원 데이터에 다시 붙여넣기.
            data[['tagged', 'changed', 'model_version', 'point', 'equip', 'inference_time']] = result[
                ['tagged', 'changed', 'model_version', 'point', 'equip', 'inference_time']]

            ## python 데이터 형식과 db 데이터 형식 호환을 위해 이러한 설정이 들어감.

            pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
            pymysql.converters.conversions = pymysql.converters.encoders.copy()
            pymysql.converters.conversions.update(pymysql.converters.decoders)

            ## DB에 넣기
            ## 필요한 부분에 대해서만 update를 쳐준다.

            conn = pymysql.connect(host='192.168.21.6', port=3306,
                                   user='root', password='ntels', db='nise', charset='utf8',
                                   )
            curs = conn.cursor()
            # for index, row in data.iterrows():
            sql = """ update auto_tagging
                     set tagged = %s, changed = %s, model_version = %s, id = %s, description = %s, name = %s, present_value = %s, point = %s, equip = %s, inference_time=%s
                     where id = %s """
            # sql = 'UPDATE auto_tagging SET point=10000 WHERE description= Zone2 Temperature'
            # curs.execute(sql, (data.loc[2, 'point'], data.loc[2,'id']))

            for i in range(len(data)):
                curs.execute(sql, (data.loc[i, 'tagged'], data.loc[i, 'changed'], data.loc[i, 'model_version'], data.loc[i, 'id'],
                                   data.loc[i, 'description'], data.loc[i, 'name'], data.loc[i, 'present_value'],
                                   data.loc[i, 'point'],
                                   data.loc[i, 'equip'],
                                   data.loc[i, 'inference_time'],
                                   data.loc[i, 'id']))
                conn.commit()
            conn.close()
            return 'Success'

dag = DAG('atvt', description='atvt_gateway_inference DAG',
          schedule_interval='*/2 * * * *',
          start_date=datetime(2020, 3, 30), catchup=False)

dummy_operator = DummyOperator(task_id='dummy_task', retries=1, dag=dag)

gateway_inference_operator = PythonOperator(task_id='at_gateway_inference_task',
                                            python_callable=at_gateway_inference_task, dag=dag)

dummy_operator >> gateway_inference_operator

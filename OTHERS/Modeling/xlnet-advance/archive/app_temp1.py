# 필요한 모듈을 불러온다
from flask import Flask, request
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api, Resource, fields
import pymysql
import pandas as pd
import csv
from glob import glob
from os.path import expanduser
from datetime import datetime
import os
import sys
import subprocess


######################################################################################################
# /////////////////////////////////////////////////////////////////////////////////////
# Setting_packages
import pandas as pd
import wandb
from simpletransformers.classification import ClassificationModel

# Setting_Value
train_args = {
    'reprocess_input_data': True,
    'overwrite_output_dir': True,
    'num_train_epochs': 5,
    'manual_seed': 10,
    'logging_steps': 10,
    'train_batch_size': 128,

    # 'wandb_project': 'atvt-board',
}
# 'reprocess_input_data': True,
#     'overwrite_output_dir': True,
#     'num_train_epochs': 10,
#     'manual_seed': 10,
#     'regression': True,
#     'evaluate_during_training': True,
#     'logging_steps': 10,
#     'evaluate_during_training_steps': 10,
#     'save_eval_checkpoints': False,
#     'train_batch_size': 128,
#     'eval_batch_size': 256,

# wandb.init(project="atvt-board")

print("Packge Loaded!")

# wandb.log({"generated_samples":
           # [wandb.Object3D(open("cow-nonormals.obj"))]})
# model_xlnet = ClassificationModel("xlnet", "xlnet-base-cased", num_labels=11, args=train_args, use_cuda=False)

# train_data_csv = pd.read_csv("/data01/justinjang87/ATVT/Dataset/Traning_Dataset/train_data.csv",
#                              index_col=False)
# update 2020-03-31 by jhc
model_xlnet = ClassificationModel("xlnet", "xlnet-base-cased", num_labels=3, args=train_args, use_cuda=False)
train_data_csv = pd.read_csv("/data01/justinjang87/ATVT/Dataset/Traning_Dataset/new_testhere1.csv",
                             index_col=False)
print("Network Built!")

def train_model():
    print("Train is start")
    train_df = train_data_csv
    model_xlnet.train_model(train_df)
    print("Train is done")
    # # run your program and collect the string output
    # cmd = "/home/justinjang87/anaconda3/envs/transformers2/bin/python3 /data01/justinjang87/ATVT/Modeling/xlnet-advance/wandb_setting_test2.py"
    # os.system(cmd)
    # out_str = subprocess.call(cmd, shell=True)
    # See if it works.
    # =print("run is done about wandb-train")
    return "Train is done"

def train_external_model():
    print("train_external_model is start")
    cmd = "/home/justinjang87/anaconda3/envs/transformers2/bin/python3 /data01/justinjang87/ATVT/Modeling/xlnet-advance/wandb_setting_test2.py"
    os.system(cmd)
    print("train_external_model is done")
    return "train_external_model is done"

def eval_model():
    print("Eval is start")
    eval_df = train_data_csv
    result, model_outputs, wrong_predictions = model_xlnet.eval_model(eval_df)
    print("eval_result:",result)
    # print("eval_model_outputs:", model_outputs)
    # print("eval_wrong_predictions:", wrong_predictions)
    print("Eval is done")
    return result


def predict(text):
    predictions_xlnet, raw_outputs_xlnet = model_xlnet.predict([text])
    # predictions_xlnet, raw_outputs_xlnet = model_xlnet.predict(["OBJECT_ANALOG_INPUT_3000323NAE02/FC-2.NAE2-T2-FEC20.ZN1-TWest Electrical Room"])
    print("predictions_xlnet:", predictions_xlnet)
    print("raw_outputs_xlnet:", raw_outputs_xlnet)

    if str(predictions_xlnet[0]) == '10':
        result = "zone air temperature sensor"
    elif str(predictions_xlnet[0]) == '9':
        result = "return air temperature sensor"
    elif str(predictions_xlnet[0]) == '8':
        result = "return air pressure sensor"
    elif str(predictions_xlnet[0]) == '7':
        result = "return air flow sensor"
    elif str(predictions_xlnet[0]) == '6':
        result = "return air damper cmd"
    elif str(predictions_xlnet[0]) == '5':
        result = "return air co2 sensor"
    elif str(predictions_xlnet[0]) == '4':
        result = "outside air temperature sensor"
    elif str(predictions_xlnet[0]) == '3':
        result = "outside air humidity sensor"
    elif str(predictions_xlnet[0]) == '2':
        result = "outside air flow sp"
    elif str(predictions_xlnet[0]) == '1':
        result = "exhaust air fan cmd"
    else:
        result = "idk"

    return result


def inference():
    conn0 = pymysql.connect(host='192.168.21.6', user='root', password='ntels',
                           db='nise', charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    # Connection 으로부터 Cursor 생성
    curs0 = conn0.cursor()

    # SQL문 실행
    sql0 = "select * from auto_tagging"
    curs0.execute(sql0)

    # 데이타 Fetch
    rows0 = curs.fetchall()
    print(rows0)
    rows_rows0 = pd.DataFrame(rows0)
    # print(rows_rows)
    rows_rows0.head()
    # rows_material = rows_rows.loc[1:1, 'object_description']
    object_id_value = rows_rows['id']
    return_value = predict(rows_rows['description'])

    update_sql = "UPDATE auto_tagging SET point = '" + return_value + \
                 "', tagged = 'y', changed = 'n', inference_time = '" + str(datetime.now()) + \
                 "' WHERE id  = '" + object_id_value + "'"
    result0 = curs.execute(update_sql)
    conn0.commit()
    check_sql0 = "select * from auto_tagging"
    curs0.execute(check_sql0)
    conn0.close()
    # return "ALL"
    return result0

def command_at_inference(text):
        if text == "ALL":
            # MySQL Connection 연결
            conn = pymysql.connect(host='192.168.21.6', user='root', password='ntels',
                                   db='nise', charset='utf8', cursorclass = pymysql.cursors.DictCursor)
            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()

            # SQL문 실행c
            sql = "select * from auto_tagging"
            curs.execute(sql)

            # 데이타 Fetch
            rows = curs.fetchall()
            print(rows)
            rows_rows = pd.DataFrame(rows)
            # print(rows_rows)
            rows_rows.head()
            # rows_material = rows_rows.loc[1:1, 'object_description']
            object_id_value = rows_rows['id'].iloc[0]
            return_value = predict(rows_rows['description'].iloc[0])

            update_sql = "UPDATE auto_tagging SET point = '"+return_value+\
                         "', tagged = 'y', changed = 'n', inference_time = '"+str(datetime.now())+\
                         "' WHERE id  = '"+ object_id_value +"'"
            result = curs.execute(update_sql)
            conn.commit()
            check_sql = "select * from auto_tagging"
            curs.execute(check_sql)
            # # Prediction
            # with open("out.csv", "w", newline='') as csv_file:
            #     csv_writer = csv.writer(csv_file)
            #     csv_writer.writerow([i[0] for i in curs.description])  # write headers
            #     csv_writer.writerows(rows)
            # check_sql = "select point from auto_tagging WHERE id = 'OBJECT_ANALOG_INPUT:3000054'"
            # curs.execute(check_sql)

            # insert_sql = "INSERT INTO auto_tagging (point) VALUES('"+return_value+"') WHERE id = 'OBJECT_ANALOG_INPUT:3000054'"
            # curs.execute(insert_sql)

            # check_rows = curs.fetchall()
            # print(check_rows)

            # Connection 닫기
            conn.close()
            # return "ALL"
            return result

        elif text == "CHANGED":
            # MySQL Connection 연결
            conn1 = pymysql.connect(host='192.168.21.6', user='root',
                                    password='ntels', db='nise', charset='utf8', cursorclass = pymysql.cursors.DictCursor)
            # Connection 으로부터 Cursor 생성
            curs1 = conn1.cursor()

            # SQL문 실행
            sql1 = "select * from auto_tagging where changed = 'y'"
            curs1.execute(sql1)

            # 데이타 Fetch
            rows1 = curs1.fetchall()
            print(rows1)
            rows_rows1 = pd.DataFrame(rows1)
            # print(rows_rows)
            rows_rows1.head()
            # rows_material = rows_rows.loc[1:1, 'object_description']
            object_id_value1 = rows_rows1['id'].iloc[0]
            return_value1 = predict(rows_rows1['description'].iloc[0])

            update_sql1 = "UPDATE auto_tagging SET point = '" + return_value1 + "', tagged = 'y', changed = 'n', inference_time = '" + str(
                datetime.now()) + "' WHERE id  = '"+ object_id_value1 +"'"
            result1 = curs1.execute(update_sql1)
            conn1.commit()
            check_sql1 = "select * from auto_tagging"
            curs1.execute(check_sql1)
            # with open("out.csv", "w", newline='') as csv_file:
            #     csv_writer = csv.writer(csv_file)
            #     csv_writer.writerow([i[0] for i in curs.description])  # write headers
            #     csv_writer.writerows(rows)

            # Connection 닫기
            conn1.close()
            # return "CHANGED"
            return result1
######################################################################################################

app = Flask(__name__) # Flask App 생성한다
api = Api(app, version='1.0', title='분류 예측 관리 API', description='분류 예측 관리 API 입니다') # API 만든다
ns  = api.namespace('prediction', description='예측') # /goods/ 네임스페이스를 만든다


@ns.route('/')
@ns.response(404, 'Train 을 할 수가 없어요')
@ns.param('Train', 'Train을 진행합니다')
class train_Algorithm(Resource):
    def post(self):
        '''Model Train'''
        # train_model()
        result = train_model()
        return result

@ns.route('/<int:id>')
@ns.response(404, 'eval을 할 수가 없어요')
@ns.param('eval', 'eval을 진행합니다')
class eval_Algorithm(Resource):
    def post(self,id):
        '''Model eval'''
        # eval_model()
        result = eval_model()
        return result

# @ns.route('/<string:text>')
# @ns.response(404, 'predict을 할 수가 없어요')
# @ns.param('predict', 'predict를 진행합니다. Text를 입력하세요.')
# class predict_Algorithm(Resource):
#     def get(self, text):
#         '''Prediction'''
#         result = predict(text)
#         return result

@ns.route('/<string:text>')
@ns.response(404, '재추론명령진행을 할 수가 없어요')
@ns.param('command-at-inference', '재추론명령진행')
class commandatinference(Resource):
    def post(self, text):
        '''command-at-inference'''
        if(text == 'ALL'):
            result = command_at_inference(text)
        elif(text == 'CHANGED'):
            result = command_at_inference(text)
        return result

@ns.route('/prediction/<string:text1>')
@ns.response(404, '네트워크가 불안정 합니다.')
@ns.param('at-direct-inference', '직접추론진행')
class atdirectinference(Resource):
    def post(self, text1):
        '''at-direct-inference'''
        result = predict(text1)
        return result

@ns.route('/prediction/train_external_model/')
@ns.response(404, '네트워크가 불안정 합니다.')
@ns.param('train_external_model', 'train_external_model')
class trainexternalmodel(Resource):
    def post(self):
        '''train_external_model'''
        result = train_external_model()
        return result

if __name__ == "__main__" :

    app.run(host='192.168.5.237', port=5000, debug=False)
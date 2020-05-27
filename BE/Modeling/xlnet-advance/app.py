"""
Title: ATVT PROJECT
Data: 2020-04-14
BY: nTels BI team

API setting Code line.
this is atvt code.
"""

""" Setting_packages """
from flask import Flask, request
import werkzeug

werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api, Resource, fields
import pymysql
import pandas as pd
import csv
import json
from glob import glob
from os.path import expanduser
from datetime import datetime
import os
import sys
import subprocess
import wandb
from simpletransformers.classification import ClassificationModel

print("Packge Loaded!")  # Packages load check

""" path_configure Setting """
f = pd.read_csv('path_configure.csv')
train_data_csv_path = f.iloc[0, 1]
print("Check train_data_csv_path:", train_data_csv_path)  # Check train_data_csv_path
python_path = f.iloc[1, 1]
print("Check python_path:", python_path)  # Check python_path
external_model_path = f.iloc[2, 1]
print("Check external_model_path:", external_model_path)  # Check external_model_path
host_path = f.iloc[3, 1]
print("Check host_path:", host_path)  # Check host_path
user_path = f.iloc[4, 1]
print("Check user_path:", user_path)  # Check user_path
password_path = f.iloc[5, 1]
print("Check password_path:", password_path)  # Check password_path
# db_path= f.iloc[6,1]
db_path = "t_points_atvt"
print("Check db_path:", db_path)  # Check db_path
charset_path = f.iloc[7, 1]
print("Check charset_path:", charset_path)  # Check charset_path
all_inference_sql = f.iloc[8, 1]
print("all_inference_sql:", all_inference_sql)  # Check all_inference_sql
command_at_inference_CHANGED_sql = f.iloc[9, 1]
print("Check command_at_inference_CHANGED_sql:",
      command_at_inference_CHANGED_sql)  # Check command_at_inference_CHANGED_sql
flask_host_path = f.iloc[10, 1]
print("Check flask_host_path:", flask_host_path)  # Check flask_host_path
flask_port_path = f.iloc[11, 1]
print("Check flask_port_path:", flask_port_path)  # Check flask_port_path
flask_debug_setting = f.iloc[12, 1]
print("Check flask_debug_setting:", flask_debug_setting)  # Check flask_debug_setting

""" Train_args Setting """
train_args = {
    'reprocess_input_data': True,
    'overwrite_output_dir': True,
    'num_train_epochs': 2,
    'manual_seed': 10,
    'logging_steps': 10,
    'train_batch_size': 128,
}

""" Model_object Setting """
model_xlnet = ClassificationModel("xlnet", "xlnet-base-cased", num_labels=3, args=train_args, use_cuda=False)

""" Train_data Setting """
train_data_csv = pd.read_csv(train_data_csv_path, index_col=False)

""" Flask Setting """
app = Flask(__name__)
api = Api(app, version='1.0', title='분류 예측 관리 API', description='분류 예측 관리 API 입니다')
ns = api.namespace('prediction', description='예측')

print("Global variable initialized!")  # Global variable load check


def train_model():
    """train to model.
       Args:
         none

       Returns:
         result message
    """
    print("train_model is start")  # train_model fucntion start
    train_df = train_data_csv
    model_xlnet.train_model(train_df)
    print("train_model is done")  # train_model fucntion done
    return "train_model is done"


def train_external_model():
    """train to model on external part.
               Args:
                 none

               Returns:
                 result message
    """
    print("train_external_model is start")  # train_external_model fucntion start
    cmd = python_path + " " + external_model_path
    os.system(cmd)
    print("train_external_model is done")  # train_external_model fucntion done
    return "train_external_model is done"


def eval_model():
    """evaluate to model.
               Args:
                 none

               Returns:
                 result message
    """
    print("eval_model is start")  # eval_model fucntion start
    eval_df = train_data_csv
    result, model_outputs, wrong_predictions = model_xlnet.eval_model(eval_df)
    print("eval_result:", result)
    print("Eval is done")  # eval_model fucntion done
    return result


def predict(text):
    """predict by using model

               Args:
                 text : (type) string // data for prediction

               Returns:
                 result : (type) string // prediction result
    """
    print("eval_model is start")  # predict fucntion start
    predictions_xlnet, raw_outputs_xlnet = model_xlnet.predict([text])
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

    print("predict is done")  # predict fucntion done
    return result


def inference():
    """inference by using model
               Args:
                 none

               Returns:
                 result : (type) int // prediction Success result
    """
    print("inference is start")  # inference fucntion start
    conn = pymysql.connect(host=host_path, user=user_path, password=password_path,
                           db=db_path, charset=charset_path, cursorclass=pymysql.cursors.DictCursor)

    curs = conn.cursor()  # Create Cursor by using Connection

    # execute sql line
    curs.execute(all_inference_sql)

    # Fetch data
    rows = curs.fetchall()

    # insert data to dataframe
    rows_rows = pd.DataFrame(rows)

    # check data frame
    rows_rows.head()

    # rows_material = rows_rows.loc[1:1, 'object_description']
    object_id_value = rows_rows['id']
    return_value = predict(rows_rows['description'])

    # update db by using predict result
    update_sql = "UPDATE auto_tagging SET point = '" + return_value + \
                 "', tagged = 'y', changed = 'n', inference_time = '" + str(datetime.now()) + \
                 "' WHERE id  = '" + object_id_value + "'"
    result = curs.execute(update_sql)

    # DB Commit
    conn.commit()
    # check_sql = "select * from auto_tagging"
    # curs.execute(check_sql)

    # DB connection close
    conn.close()
    print("inference is done")  # inference fucntion done
    return result


def command_at_inference_ALL():
    """command to command_at_inference_ALL
                   Args:
                     none

                   Returns:
                     result : (type) int // Success result
    """
    print("command_at_inference_ALL is start")  # command_at_inference_ALL fucntion start

    conn = pymysql.connect(host=host_path, user=user_path, password=password_path,
                           db=db_path, charset=charset_path, cursorclass=pymysql.cursors.DictCursor)
    curs = conn.cursor()
    curs.execute(all_inference_sql)
    rows = curs.fetchall()
    print(rows)
    rows_rows = pd.DataFrame(rows)
    rows_rows.head()
    object_id_value = rows_rows['id'].iloc[0]
    return_value = predict(rows_rows['description'].iloc[0])
    update_sql = "UPDATE auto_tagging SET point = '" + return_value + \
                 "', tagged = 'y', changed = 'n', inference_time = '" + str(datetime.now()) + \
                 "' WHERE id  = '" + object_id_value + "'"
    result = curs.execute(update_sql)
    conn.commit()
    check_sql = all_inference_sql
    curs.execute(check_sql)
    conn.close()
    print("command_at_inference_ALL is done")  # command_at_inference_ALL fucntion done
    return result


def command_at_inference_CHANGED():
    """command to command_at_inference_CHANGED
                   Args:
                     none

                   Returns:
                     result : (type) int // Success result
    """
    print("command_at_inference_CHANGED is start")  # command_at_inference_CHANGED fucntion start
    conn1 = pymysql.connect(host=host_path, user=user_path,
                            password=password_path, db=db_path, charset=charset_path,
                            cursorclass=pymysql.cursors.DictCursor)
    curs1 = conn1.cursor()
    curs1.execute(command_at_inference_CHANGED_sql)
    rows1 = curs1.fetchall()
    print(rows1)
    rows_rows1 = pd.DataFrame(rows1)
    rows_rows1.head()
    object_id_value1 = rows_rows1['id'].iloc[0]
    return_value1 = predict(rows_rows1['description'].iloc[0])
    update_sql1 = "UPDATE auto_tagging SET point = '" + return_value1 + "', tagged = 'y', changed = 'n', inference_time = '" + str(
        datetime.now()) + "' WHERE id  = '" + object_id_value1 + "'"
    result = curs1.execute(update_sql1)
    conn1.commit()
    check_sql1 = all_inference_sql
    curs1.execute(check_sql1)
    conn1.close()
    print("command_at_inference_CHANGED is done")  # command_at_inference_CHANGED fucntion done
    return result


def command_at_inference(text):
    """command to AT_PART_inference
               Args:
                 text : (type) string // command text

               Returns:
                 result : (type) int // Success result
    """
    print("command_at_inference is start")  # command_at_inference fucntion start
    if text == "ALL":
        result = command_at_inference_ALL()
        return result

    elif text == "CHANGED":
        result = command_at_inference_CHANGED()
        return result


@ns.route('/train_Algorithm/')  # Flask Route setting
@ns.response(404, 'Train 을 할 수가 없어요')  # Flask Response setting
@ns.param('Train', 'Train을 진행합니다')  ##Flask param setting
class train_Algorithm(Resource):
    """Flask API Class-train_Algorithm.
           Properties:
            post() : Message for post type
    """

    def post(self):
        """send message as post api method
                       Args:
                         self : class byself
                       Returns:
                         result : result message
        """
        print("train_Algorithm_post is start")  # train_Algorithm_post start
        result = train_model()
        print("train_Algorithm_post is done")  # train_Algorithm_post done
        return result


@ns.route('/eval_Algorithm/')  # Flask Route setting
@ns.response(404, 'eval을 할 수가 없어요')  # Flask Response setting
@ns.param('eval', 'eval을 진행합니다')  ##Flask param setting
class eval_Algorithm(Resource):
    """Flask API Class-eval_Algorithm.
           Properties:
            post() : Message for post type
    """

    def post(self):
        """send message as post api method
                       Args:
                         self : class byself
                       Returns:
                         result : result message
        """
        result = eval_model()
        return result


# Test body 2020-04-23
@ns.route('/Test/', methods=['POST'])  # Flask Route setting
@ns.response(404, 'Test 할 수가 없어요')  # Flask Response setting
@ns.param('eval', 'Test 진행합니다')  ##Flask param setting
class Test(Resource):
    """Flask API Class-eval_Algorithm.
           Properties:
            post() : Message for post type
    """

    def post(self):
        """send message as post api method
                       Args:
                         self : class byself
                       Returns:
                         result : result message
        """
        print(request.is_json)
        content = request.get_json()
        print(content)
        print(content['command'])
        # data=json.loads(content)
        # json_normalize(data['command'])
        if (content['command'] == 'all'):
            result = "it is all"
        elif (content['command'] == 'changed'):
            result = "it is changed"

        print("this is result:", result)
        return result


# 재추론기능_Refactor_20200427
@ns.route('/commandatinference/', methods=['POST'])  # Flask Route setting
@ns.response(404, '재추론명령진행을 할 수가 없어요')  # Flask Response setting
@ns.param('command-at-inference', '재추론명령진행')  ##Flask param setting
class commandatinference(Resource):
    """Flask API Class-commandatinference.
           Properties:
            post() : Message for post type
    """

    def post(self, text):
        """send message as post api method
                       Args:
                         self : class byself
                         text : (type) stirng //Command text
                       Returns:
                         result : result message
        """
        print(request.is_json)
        content = request.get_json()
        print(content)
        print(content['command'])
        if (content['command'] == 'all'):
            result = command_at_inference(text)
        elif (content['command'] == 'changed'):
            result = command_at_inference(text)

        print("commandatinference_post is done")  # commandatinference_post done
        return result


@ns.route('/prediction/<string:text1>')  # Flask Route setting
@ns.response(404, '네트워크가 불안정 합니다.')  # Flask Response setting
@ns.param('at-direct-inference', '직접추론진행')  ##Flask param setting
class atdirectinference(Resource):
    """Flask API Class-atdirectinference.
           Properties:
            post() : Message for post type
    """

    def post(self, text1):
        """send message as post api method
                       Args:
                         self : class byself
                         text1 : (type) stirng //data for prediction
                       Returns:
                         result : result message
        """
        print("atdirectinference_post is start")  # atdirectinference_post start
        result = predict(text1)
        print("atdirectinference_post is done")  # atdirectinference_post done
        return result
wlrm

if __name__ == "__main__":
    # init point
    print("app__main__is start")  # app__main__ start
    app.run(host=flask_host_path, port=flask_port_path, debug=flask_debug_setting)
    print("app__main__ is done")  # app__main__ done

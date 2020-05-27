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
import requests

print("Packge Loaded!")  # Packages load check
""" Flask Setting """
app = Flask(__name__)
api = Api(app, version='1.0', title='분류 예측 관리 API', description='분류 예측 관리 API 입니다')
ns = api.namespace('prediction', description='예측')

print("Global variable initialized!")  # Global variable load check


# Test body 2020-04-23
@ns.route('/Test/', methods = ['POST'])  # Flask Route setting
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
        if(content['command'] == 'all'):
            print("inference is start")  # inference fucntion start
            conn = pymysql.connect(host="192.168.21.6", user="root", password="ntels",
                                   db="nise", charset="utf8", cursorclass=pymysql.cursors.DictCursor)
            curs = conn.cursor()  # Create Cursor by using Connection
            curs.execute("select * from t_points_atvt")
            rows = curs.fetchall()
            # insert data to dataframe
            rows_rows = pd.DataFrame(rows)
            print(rows_rows)
            return rows_rows.to_json()

# init point
if __name__ == "__main__":
    print("app__main__is start")  # app__main__ start
    app.run(host="192.168.5.237", port=5000, debug= False )
    print("app__main__ is done")  # app__main__ done

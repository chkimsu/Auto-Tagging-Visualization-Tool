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
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
import ktrain
from ktrain import text
import numpy as np
from datetime import datetime
import time
import shutil
from nlpre import titlecaps, dedash, identify_parenthetical_phrases
from nlpre import replace_acronyms, replace_from_dictionary
from shutil import copyfile

print("Packge Loaded!")  # Packages load check

# tag_list=pd.read_csv("Project_Haystack3_Tags_List.csv")
# tag_list.head()
#
# label_list = pd.DataFrame(index=range(0, len(rows_rows)), columns=['name','labelnumber'])
# a = 0;
# for i in range(len(rows_rows)):
#     label_list['name'].iloc[i] = rows_rows['equip_ref'].iloc[i] + " " + rows_rows['point_ref'].iloc[i]
#
# label_list.drop_duplicates(["name"])

# for i in range(len(label_list)):
#     label_list['labelnumber'].iloc[i] = a
#     a+1

# label_list.to_csv('label_list.csv')

def create_training_dataset():
    conn = pymysql.connect(host="192.168.12.166", user="root", password="ntels", port=30037,
                           db="nisbcp", charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    curs = conn.cursor()
    curs.execute("select * from t_points_atvt where point_ref IS NOT NULL")
    rows = curs.fetchall()
    print(rows)
    rows_rows = pd.DataFrame(rows)
    rows_rows.head()

    conn1 = pymysql.connect(host="192.168.12.166", user="root", password="ntels", port=30037,
                            db="nisbcp", charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    curs1 = conn1.cursor()
    curs1.execute("select * from t_points_atvt where point_ref IS NULL")
    rows1 = curs1.fetchall()
    print(rows1)
    rows_rows1 = pd.DataFrame(rows1)

    return_value = pd.DataFrame(index=range(0, len(rows_rows)),
                                columns=['tagged', 'changed', 'inferenced', 'model_version', 'id', 'description',
                                         'name', 'point', 'equip', 'equip_id', 'present_value', 'inference_time',
                                         'create_time', 'update_time'])
    return_value2 = pd.DataFrame(index=range(0, len(rows_rows)),
                                 columns=['return'])
    final_len=len(rows_rows)+len(rows_rows1)
    train_df = pd.DataFrame(index= range(0, final_len), columns=['Data','Label'])

    label_list = pd.DataFrame(index=range(0, len(rows_rows)), columns=['name', 'labelnumber'])
    a = 1;
    for i in range(len(rows_rows)):
        label_list['name'].iloc[i] = rows_rows['equip_ref'].iloc[i] + " " + rows_rows['point_ref'].iloc[i]

    label_list.drop_duplicates(["name"])

    for i in range(len(label_list)):
        label_list['labelnumber'].iloc[i] = a
        a += 1

    label_list
    #"return air co2 sensor"
    #"zone air temp occ cooling sp"
    # for i in range(len(rows_rows)):
    #     if rows_rows['point_ref'].iloc[i] == 'zone air temperature sensor':
    #         return_value2['return'].iloc[i] = '10'
    #     elif rows_rows['point_ref'].iloc[i] == 'return air temperature sensor':
    #         return_value2['return'].iloc[i] = '9'
    #     elif rows_rows['point_ref'].iloc[i] == 'return air pressure sensor':
    #         return_value2['return'].iloc[i] = '8'
    #     elif rows_rows['point_ref'].iloc[i] == 'return air flow sensor':
    #         return_value2['return'].iloc[i] = '7'
    #     elif rows_rows['point_ref'].iloc[i] == 'return air damper cmd':
    #         return_value2['return'].iloc[i] = '6'
    #     elif rows_rows['point_ref'].iloc[i] == 'return air co2 sensor':
    #         return_value2['return'].iloc[i] = '5'
    #     elif rows_rows['point_ref'].iloc[i] == 'outside air temperature sensor':
    #         return_value2['return'].iloc[i] = '4'
    #     elif rows_rows['point_ref'].iloc[i] == 'outside air humidity sensor':
    #         return_value2['return'].iloc[i] = '3'
    #     elif rows_rows['point_ref'].iloc[i] == 'outside air flow sp':
    #         return_value2['return'].iloc[i] = '2'
    #     elif rows_rows['point_ref'].iloc[i] == 'exhaust air fan cmd':
    #         return_value2['return'].iloc[i] = '1'
    #     else:  # idk-case
    #         return_value2['return'].iloc[i] = "11"

    for i in range(len(rows_rows)):
        if rows_rows['point_ref'].iloc[i] == 'zone air temperature sensor':
            return_value2['return'].iloc[i] = '10'
        elif rows_rows['point_ref'].iloc[i] == 'return air temperature sensor':
            return_value2['return'].iloc[i] = '9'
        elif rows_rows['point_ref'].iloc[i] == 'return air pressure sensor':
            return_value2['return'].iloc[i] = '8'
        elif rows_rows['point_ref'].iloc[i] == 'return air flow sensor':
            return_value2['return'].iloc[i] = '7'
        elif rows_rows['point_ref'].iloc[i] == 'return air damper cmd':
            return_value2['return'].iloc[i] = '6'
        elif rows_rows['point_ref'].iloc[i] == 'return air co2 sensor':
            return_value2['return'].iloc[i] = '5'
        elif rows_rows['point_ref'].iloc[i] == 'outside air temperature sensor':
            return_value2['return'].iloc[i] = '4'
        elif rows_rows['point_ref'].iloc[i] == 'outside air humidity sensor':
            return_value2['return'].iloc[i] = '3'
        elif rows_rows['point_ref'].iloc[i] == 'outside air flow sp':
            return_value2['return'].iloc[i] = '2'
        elif rows_rows['point_ref'].iloc[i] == 'exhaust air fan cmd':
            return_value2['return'].iloc[i] = '1'
        else:  # idk-case
            return_value2['return'].iloc[i] = "11"

    # for i in range(len(rows_rows)):
    #     for j in range(len(label_list)):
    #          if rows_rows['point_ref'].iloc[i] == label_list['name'].iloc[j]:
    #             return_value2['return'].iloc[i] = label_list['labelnumber'].iloc[j]
    #          # else:  # idk-case
    #          #     return_value2['return'].iloc[i] = '0'

    for i in range(len(rows_rows)):
        train_df["Data"].iloc[i] = rows_rows["id"].iloc[i]
        train_df["Label"].iloc[i] = return_value2["return"].iloc[i]
    for i in range(len(rows_rows1)):
        train_df["Data"].iloc[i+len(rows_rows)] = rows_rows1["id"].iloc[i]
        train_df["Label"].iloc[i+len(rows_rows)] = '0'

    print(train_df.head())
    train_df.to_csv('new_testhere2.csv',index=False, header=True)

def train_model():
    train_args = {
        'reprocess_input_data': True,
        'overwrite_output_dir': True,
        'num_train_epochs': 2,
        'manual_seed': 10,
        'logging_steps': 10,
        'train_batch_size': 128,
        'output_dir': f"outputs/models",
        'best_model_dir': f"outputs/models/best_model",
    }
    model = ClassificationModel("xlnet", "xlnet-base-cased", num_labels=2, args=train_args, use_cuda=False)
    train_data_csv = pd.read_csv("new_testhere2.csv", index_col=False)
    model.train_model(train_data_csv)

if __name__=='__main__': #init_main_modeling
   print("modeling__main__is start")  # main_modeling__main__start
   print("Funiction_create_training_dataset__is start")  # Funiction_create_training_dataset__start
   create_training_dataset()
   print("Funiction_create_training_dataset__is done")  # Funiction_create_training_dataset__done
   print("Funiction_train_model__is start")   # Funiction_train_model__start
   train_model()
   print("Funiction_train_model__is done")   # Funiction_train_model__done
   print("modeling__main__is done")  # main_modeling__main__done

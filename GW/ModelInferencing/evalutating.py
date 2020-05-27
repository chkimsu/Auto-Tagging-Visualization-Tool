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
model = ClassificationModel('xlnet', 'outputs/models/', num_labels=2, args=train_args, use_cuda=False)

def evaluate_model():
    evaluate_data_csv = pd.read_csv("new_testhere2.csv", index_col=False)
    model.eval_model(evaluate_data_csv)

if __name__== '__main__': #init_main_modeling
    print("inferencing__main__is start")  # evaluating__main__is start
    print("Funiction__evaluate_model_is__start")  # Funiction__evaluate_model_is__start
    evaluate_model()
    print("Funiction__evaluate_model_is__done")  # Funiction__evaluate_model_is__done
    print("inferencing__main__is done")  # evaluating__main__is done

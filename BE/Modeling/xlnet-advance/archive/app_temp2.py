# //////////////////////////////////////////////////////////////
# Setting_packages
from xlnet_Train_model import *
from flask import Flask, request
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from flask_restplus import Api, Resource, fields
from simpletransformers.classification import ClassificationModel
import pandas as pd
import wandb

# //////////////////////////////////////////////////////////////
# Setting_Value
train_args = {
    'reprocess_input_data': True,
    'overwrite_output_dir': True,
    'num_train_epochs': 10,
    'manual_seed': 10,
    'regression': True,
    'evaluate_during_training': True,
    'logging_steps': 10,
    'evaluate_during_training_steps': 10,
    'save_eval_checkpoints': False,
    'train_batch_size': 128,
    'eval_batch_size': 256,

    'wandb_project': 'atvt-board',
}

model_xlnet = ClassificationModel("xlnet", "xlnet-base-cased", num_labels=11, args=train_args, use_cuda=False)
train_data_csv = pd.read_csv("/data01/justinjang87/simpletransformers/examples/text_classification/train_data.csv",
                             index_col=False)

# //////////////////////////////////////////////////////////////
# Flask Setting
app = Flask(__name__) # Flask App 생성한다
api = Api(app, version='1.0', title='분류 예측 관리 API', description='분류 예측 관리 API 입니다') # API 만든다
ns  = api.namespace('prediction', description='예측') # /goods/ 네임스페이스를 만든다

# //////////////////////////////////////////////////////////////
# Rest API Setting
@ns.route('/')
@ns.response(404, 'Train 을 할 수가 없어요')
@ns.param('Train', 'Train을 진행합니다')
class train_Algorithm(Resource):
    def get(self):
        '''Model Train'''
        result = model_xlnet.train_model(train_data_csv)
        return "Train is done"

@ns.route('/<int:id>')
@ns.response(404, 'eval을 할 수가 없어요')
@ns.param('eval', 'eval을 진행합니다')
class eval_Algorithm(Resource):
    def get(self,id):
        '''Model eval'''
        result = eval_model(model_xlnet,train_data_csv)
        return result

@ns.route('/<string:text>')
@ns.response(404, 'predict을 할 수가 없어요')
@ns.param('predict', 'predict를 진행합니다. Text를 입력하세요.')
class predict_Algorithm(Resource):
    def get(self, text):
        '''Prediction'''
        result = predict(model_xlnet,text)
        return result


# //////////////////////////////////////////////////////////////
# init
if __name__ == "__main__" :
    app.run(host='192.168.5.237', port=15003)

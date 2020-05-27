
# Setting_packages
from simpletransformers.classification import ClassificationModel
import pandas as pd
import wandb

# Setting_Value
# model_xlnet = ClassificationModel("xlnet", "xlnet-base-cased", num_labels=11, args=train_args, use_cuda=False)
# train_data_csv = pd.read_csv("/data01/justinjang87/simpletransformers/examples/text_classification/train_data.csv",
#                              index_col=False)
# train_args
# model_xlnet
# train_data_csv

def train_model(model,data):
    model_xlnet=model
    train_data_csv = data
    print("Train is start")
    train_df = train_data_csv
    model_xlnet.train_model(train_df)
    print("Train is done")
    return "Train is done"

def eval_model(model,data):
    model_xlnet = model
    train_data_csv = data
    print("Eval is start")
    eval_df = train_data_csv
    result, model_outputs, wrong_predictions = model_xlnet.eval_model(eval_df)
    print("eval_result:",result)
    print("Eval is done")
    return result

def predict(model, text):
    model_xlnet = model
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
import os
import pandas as pd
import sys
import ktrain
from ktrain import text
import numpy as np


os.chdir('/data01/CSB/CSB_Jupyter/ATVT/auto-tagging-master/Preprocessing/Text_Normalize/NLPre-master/CSB-NLpre/')
data = pd.read_csv(str(sys.argv[1])+'_result.csv')



data = data.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1)
data = data.fillna('0')
data['BERT'] = data['PROP_OBJECT_IDENTIFIER']+'_'+data['PROP_OBJECT_NAME']+'_'+data['PROP_DESCRIPTION']

databert = data[['BERT']]


os.chdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling')
predictor = ktrain.load_predictor('csbpredictor')

for i in range(len(databert)):
    databert.loc[i,'label'] = predictor.predict(databert.iloc[i,0])

    
data['label'] = databert['label']
data = data.drop(['BERT'],axis=1)

print(data)
os.chdir('/data01/CSB/CSB_Jupyter/ATVT/BERT/CSB_Modelling/Prediction')
data.to_csv(str(sys.argv[1])+'_final.csv')
    
    

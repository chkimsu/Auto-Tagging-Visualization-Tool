from simpletransformers.classification import ClassificationModel
import pandas as pd

train_data = [
    ['Example sentence belonging to class 1', 'Yep, this is 1', 1.8],
    ['Example sentence belonging to class 0', 'Yep, this is 0', 0.2],
    ['Example  2 sentence belonging to class 0', 'Yep, this is 0', 4.5]
]

train_df = pd.DataFrame(train_data, columns=['text_a', 'text_b', 'labels'])

eval_data = [
    ['Example sentence belonging to class 1', 'Yep, this is 1', 1.9],
    ['Example sentence belonging to class 0', 'Yep, this is 0', 0.1],
    ['Example  2 sentence belonging to class 0', 'Yep, this is 0', 5]
]

eval_df = pd.DataFrame(eval_data, columns=['text_a', 'text_b', 'labels'])

train_args={
    'reprocess_input_data': True,
    'regression': True,
    'evaluate_during_training': True,
    'logging_steps': 10,
    'num_train_epochs': 10,
    'evaluate_during_training_steps': 10,
    'save_eval_checkpoints': False,
    'train_batch_size': 128,
    'eval_batch_size': 256,
    'overwrite_output_dir': True,

    'wandb_project': 'atvt-board',
}

# Create a ClassificationModel
model = ClassificationModel('roberta', 'roberta-base', num_labels=1, use_cuda=False, cuda_device=0, args=train_args)
print(train_df.head())

# Train the model
model.train_model(train_df, eval_df=eval_df)

# Evaluate the model
result, model_outputs, wrong_predictions = model.eval_model(eval_df)

predictions, raw_outputs = model.predict([["I'd like to puts some CD-ROMS on my iPad, is that possible?'", "Yes, but wouldn't that block the screen?"]])
print(predictions)
print(raw_outputs)
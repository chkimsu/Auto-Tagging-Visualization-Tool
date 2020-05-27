from ktrain import text
import ktrain


#### 미리 만들어놓은 train, test 폴더의 데이터를 가지고 와서 센텐스피스 전처리해줌. 
(x_train, y_train), (x_test, y_test), preproc = text.texts_from_folder('label', maxlen=500, 
                                                                     preprocess_mode='bert',
                                                                     train_test_names=['train', 'test'],
                                                                     )


#### 모델 객체 생성
model = text.text_classifier('bert', train_data=(x_train, y_train), preproc=preproc)
learner = ktrain.get_learner(model, train_data=(x_train, y_train),val_data=(x_test, y_test), batch_size= 5)


#### 실제 학습. 
learner.fit_onecycle(2e-5, 8)


#### 실제 예측하는 것은 따로 만들어주어야함. 
predictor = ktrain.get_predictor(learner.model, preproc)


#### predictior저장. 
predictor.save('csbpredictor')
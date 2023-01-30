from keras.datasets import mnist
import matplotlib.pyplot as plt
import cv2
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv2D, MaxPool2D, Dropout
from keras.optimizers import SGD, Adam
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
from keras.utils import to_categorical
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.utils import np_utils
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook
from sklearn.utils import shuffle

from data.ai_data import AI_Data





def train():
    data = AI_Data("emnist_train")



    x = []
    y = []
    for i, letter in enumerate(data.ref_data):
        for image in letter:
            x.append(np.reshape(image, (28, 28)))
            y.append(i)
    x = np.array(x)
    y = np.array(y)


    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size = 0.2)


    #Reshaping the training & test dataset so that it can be put in the model...
    train_X = train_x.reshape(train_x.shape[0],train_x.shape[1],train_x.shape[2],1)
    print("New shape of train data: ", train_X.shape)

    test_X = test_x.reshape(test_x.shape[0], test_x.shape[1], test_x.shape[2],1)
    print("New shape of train data: ", test_X.shape)

    # Converting the labels to categorical values...
    train_yOHE = to_categorical(train_y, num_classes = 26, dtype='int')
    print("New shape of train labels: ", train_yOHE.shape)

    test_yOHE = to_categorical(test_y, num_classes = 26, dtype='int')
    print("New shape of test labels: ", test_yOHE.shape)


    # CNN model...
    model = Sequential()

    model.add(Conv2D(filters=32, kernel_size=(3, 3), activation='relu', input_shape=(28,28,1)))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))

    model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding = 'same'))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))

    model.add(Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding = 'valid'))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))

    model.add(Flatten())

    model.add(Dense(64,activation ="relu"))
    model.add(Dense(128,activation ="relu"))

    model.add(Dense(26,activation ="softmax"))



    model.compile(optimizer = Adam(learning_rate=0.002), loss='categorical_crossentropy', metrics=['accuracy'])
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.0001)
    early_stop = EarlyStopping(monitor='val_loss', min_delta=0, patience=2, verbose=0, mode='auto')


    history = model.fit(train_X, train_yOHE, epochs=3, callbacks=[reduce_lr, early_stop],  validation_data = (test_X,test_yOHE))
    history = model.fit(train_X, train_yOHE, epochs=3, callbacks=[reduce_lr, early_stop],  validation_data = (test_X,test_yOHE))


    model.summary()
    model.save(r'model_hand.h5')


    # Displaying the accuracies & losses for train & validation set...
    print("The validation accuracy is :", history.history['val_accuracy'])
    print("The training accuracy is :", history.history['accuracy'])
    print("The validation loss is :", history.history['val_loss'])
    print("The training loss is :", history.history['loss'])


def test():
    data = AI_Data("emnist_test")
    
    x = []
    y = []
    for i, letter in enumerate(data.ref_data):
        for image in letter:
            x.append(np.reshape(image, (28, 28)))
            y.append(i)
    x = np.array(x)
    y = np.array(y)

 
    model = Sequential()

    model.add(Conv2D(filters=32, kernel_size=(3, 3), activation='relu', input_shape=(28,28,1)))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))

    model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding = 'same'))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))

    model.add(Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding = 'valid'))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2))

    model.add(Flatten())

    model.add(Dense(64,activation ="relu"))
    model.add(Dense(128,activation ="relu"))

    model.add(Dense(26,activation ="softmax"))

    model.compile(optimizer = Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=1, min_lr=0.0001)
    early_stop = EarlyStopping(monitor='val_loss', min_delta=0, patience=2, verbose=0, mode='auto')

    model.load_weights("src/models/emnist_2/model_hand.h5")

    
    predictions = []


    for img in x:
        img = np.array([img])
        predictions.append(np.argmax(model(img)))

    #calculate accuracy
    accuracy = 0
    for i, j in zip(predictions, y):
        accuracy += int(i == j)
    accuracy /= len(y)

    print(accuracy)



import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Masking
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import BatchNormalization
import json

def main():
    with open('./data/processed_data/bach_chorale_melodies.json') as melody_file:
        melody_data = json.load(melody_file)

    with open('./data/processed_data/bach_chorale_harmonies_flat.json') as harmony_file:
        harmony_data = json.load(harmony_file)

    train_melodies = melody_data['train']
    test_melodies = melody_data['test']
    validation_melodies = melody_data['validation']

    train_harmonies = harmony_data['train']
    test_harmonies = harmony_data['test']
    validation_harmonies = harmony_data['validation']

    train_melodies_np_array = convert_to_np_array(train_melodies)
    test_melodies_np_array = convert_to_np_array(test_melodies)
    validation_melodies_np_array = convert_to_np_array(validation_melodies)
    train_harmonies_np_array = convert_to_np_array(train_harmonies)
    test_harmonies_np_array = convert_to_np_array(test_harmonies)
    validation_harmonies_np_array = convert_to_np_array(validation_harmonies)


    # Normalize values
    normalized_train_harmonies_array = train_harmonies_np_array
    normalized_train_melodies_array = train_melodies_np_array
    normalized_validation_harmonies_array = validation_harmonies_np_array
    normalized_validation_melodies_array = validation_melodies_np_array
    
    model = Sequential()
    #optimizer = Adam(learning_rate = 0.001)
    model.add(BatchNormalization())
    model.add(Masking(mask_value=0.0))
    model.add(LSTM(256, activation='relu', input_shape=(160, 1)))
    model.add(RepeatVector(480))

    model.add(LSTM(256, activation='softmax', return_sequences=True))
    model.add(TimeDistributed(Dense(1)))

    model.compile(optimizer='adam', loss='categorical_crossentropy')

    model.fit(normalized_train_melodies_array, 
              normalized_train_harmonies_array, 
              epochs=265, 
              validation_data=(normalized_validation_melodies_array, normalized_validation_harmonies_array))


    tf.keras.models.save_model(model, "./models/bach_chorale_cce_50/")

def convert_to_np_array(list: list):
    list = np.array(list)
    list = np.expand_dims(list, axis=-1)
    return list

if __name__ == '__main__':
    main()
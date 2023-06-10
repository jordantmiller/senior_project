import tensorflow as tf
import numpy as np
import json
from tensorflow.keras.preprocessing.sequence import pad_sequences

def main():
    with open('./data/processed_data/trimmed_bach_chorale_melodies.json') as melody_file:
        melody_data = json.load(melody_file)

    with open('./data/processed_data/trimmed_bach_chorale_harmonies_flat.json') as harmony_file:
        harmony_data = json.load(harmony_file)

    test_melodies = melody_data['test']
    test_harmonies = harmony_data['test']

    test_melodies = convert_to_np_array(test_melodies)
    test_harmonies = convert_to_np_array(test_harmonies)
    test_melodies = test_melodies / 127
    test_harmonies = test_harmonies / 127

    model = tf.keras.models.load_model("./models/alt_bach_chorale_trimmed_data_300/")

    sample_melody = convert_to_np_array(test_melodies[0])
    normalized_sample_melody = sample_melody / 127

    # padded_sample_melody = pad_sequences([sample_melody], maxlen=160, padding='post')

    reshaped_sample_melody = np.reshape(normalized_sample_melody, (32, 1))

    # normalized_sample_melody = reshaped_sample_melody / 127.0

    prediction = model.predict(reshaped_sample_melody)

    denormalized_prediction = prediction * 127
    integer_prediction = np.round(denormalized_prediction).astype(int)
    print(integer_prediction)

def convert_to_np_array(list: list):
    list = np.array(list)
    list = np.expand_dims(list, axis=-1)
    return list


if __name__ == '__main__':
    main()
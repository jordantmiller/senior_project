import tensorflow as tf
from tensorflow import keras
from midiutil import MIDIFile

import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

# Constants used to adjust data to ensure no negative values in the target columns
BASS_TARGET_ADJ = 15
BASS_NUM_OUTPUT_NODES = 40
TENOR_TARGET_ADJ = 16
TENOR_NUM_OUTPUT_NODES = 32
ALTO_TARGET_ADJ = 15
ALTO_NUM_OUTPUT_NODES = 35
SOPRANO_TARGET_ADJ = 12
SOPRANO_NUM_OUTPUT_NODES = 25

MIDDLE_C = 48

def generate_midi_file(chords: list, file_name: str) -> None:
  midi = MIDIFile(1)

  track = 0
  time = 0
  midi.addTrackName(track, time, "Test Track")
  midi.addTempo(track, time, 60)

  for i, chord in enumerate(chords):
      for note in chord:
          duration = 1
          volume = 100
          midi.addNote(track, 0, note, time + i, duration, volume)

  with open("./midi/test_midi_files/" + file_name, "wb") as output_file:
      midi.writeFile(output_file)

def normalize_chord_over_bass(chord: list) -> list:
  return [item - chord[0] for item in chord]

def old_get_next_chord(starting_chord: list, b_model, t_model, a_model, s_model) -> list:
  """
  Given the four part models and a starting chord, returns the changes for each part
  representing the subsequent chord.
  """

  # Convert starting chord to a numpy array
  np_chord = np.array(starting_chord)

  # Gets the bass prediction
  bass_prediction = b_model.predict(np_chord, verbose=0)

  # Removes the adjustment made before training
  bass_prediction = bass_prediction[0].argmax() - BASS_TARGET_ADJ

  # Adds the part to np_chord so it can be used in subsequent predictions
  np_chord = np.append(np_chord, bass_prediction)
  
  # As above for remaining parts.  NOTE: Order matters as each prediction
  # requires the previous prediction.

  soprano_prediction = s_model.predict(np_chord, verbose=0)
  soprano_prediction = soprano_prediction[0].argmax() - SOPRANO_TARGET_ADJ
  np_chord = np.append(np_chord, soprano_prediction)

  tenor_prediction = t_model.predict(np_chord, verbose=0)
  tenor_prediction = tenor_prediction[0].argmax() - TENOR_TARGET_ADJ
  np_chord = np.append(np_chord, tenor_prediction)

  alto_prediction = a_model.predict(np_chord, verbose=0)
  alto_prediction = alto_prediction[0].argmax() - ALTO_TARGET_ADJ
  np_chord = np.append(np_chord, alto_prediction)

  return [bass_prediction, tenor_prediction, alto_prediction, soprano_prediction]



def get_next_chord(starting_chord: list, next_melody_note: int, b_model, t_model, a_model) -> list:
  """
  Given the four part models and a starting chord, returns the changes for each part
  representing the sunsequent chord.
  """
  starting_chord.append(next_melody_note)
  # Convert starting chord to a numpy array
  np_chord = np.array(starting_chord)

  # Gets the bass prediction
  bass_prediction = b_model.predict(np_chord, verbose=0)

  # Removes the adjustment made before training
  bass_prediction = bass_prediction[0].argmax() - BASS_TARGET_ADJ

  # Adds the part to np_chord so it can be used in subsequent predictions
  np_chord = np.append(np_chord, bass_prediction)

  # switch because tenor model is expecting the soprano to be after the bass
  np_chord[-1], np_chord[-2], = np_chord[-2], np_chord[-1]
  
  # As above for remaining parts.  NOTE: Order matters as each prediction
  # requires the previous prediction.

  # soprano_prediction = s_model.predict(np_chord, verbose=0)
  # soprano_prediction = soprano_prediction[0].argmax() - SOPRANO_TARGET_ADJ
  # np_chord = np.append(np_chord, soprano_prediction)

  tenor_prediction = t_model.predict(np_chord, verbose=0)
  tenor_prediction = tenor_prediction[0].argmax() - TENOR_TARGET_ADJ
  np_chord = np.append(np_chord, tenor_prediction)

  alto_prediction = a_model.predict(np_chord, verbose=0)
  alto_prediction = alto_prediction[0].argmax() - ALTO_TARGET_ADJ
  np_chord = np.append(np_chord, alto_prediction)

  return [bass_prediction, tenor_prediction, alto_prediction, next_melody_note]



if __name__ == '__main__':

  # The 8 starting chords
  starting_chords = [[0, 3, 7, 15], 
                     [0, 7, 16, 24],
                     [0, 7, 16, 19],
                     [0, 4, 7, 12],
                     [0, 12, 16, 19],
                     [0, 7, 7, 16],
                     [0, 3, 8, 18],
                     [0, 3, 12, 21]]
  
  starting_melodies = [[0, -2, 4, -2, 4, 1, 0, 0],
                       [0, 0, 1, 0, 0, 0, 2, 2],
                       [0, 0, 2, -2, 0, -3, 3, -2, -1, -5, 1],
                       [0, 2, 2, 2, 0, 3, -2, -1, -2, -2],
                       [0, 7, 0, 2, 0, -2, 0, -2, 0, -1, 0, -2, 0, -2]]



  # Load the models
  bass_model = keras.models.load_model("./models/super_bass_model")
  tenor_model = keras.models.load_model("./models/super_tenor_model")
  alto_model = keras.models.load_model("./models/super_alto_model")
  soprano_model = keras.models.load_model("./models/super_soprano_model")
  bass_with_sop_model = keras.models.load_model("./models/super_bass_model_with_soprano")

  current_number = 4
  next_chord = starting_chords[current_number]
  final_chords = list()
  final_chords.append([item + MIDDLE_C for item in next_chord])

  # print(old_get_next_chord(starting_chords[0], bass_model, tenor_model, alto_model, soprano_model))

  # for i in range(4):
  #    next_chord = old_get_next_chord(next_chord, bass_model, tenor_model, alto_model, soprano_model)
  #    print(next_chord)
  #    final_chords.append([final_chords[-1][i] + next_chord[i] for i in range(len(next_chord))])
  #    print(final_chords[-2], " + ", next_chord, " = ", final_chords[-1])
  #    next_chord = normalize_chord_over_bass(final_chords[-1])
  #    print(next_chord)

  for note in starting_melodies[current_number]:
    next_chord = get_next_chord(next_chord, note, bass_with_sop_model, tenor_model, alto_model)
    final_chords.append([final_chords[-1][i] + next_chord[i] for i in range(len(next_chord))])
    next_chord = normalize_chord_over_bass(final_chords[-1])
      
  print(final_chords)

  generate_midi_file(final_chords, "piece_5.mid")

  # print(starting_chords[2])

  # next_chord = get_next_chord(starting_chords[2], starting_melodies[0], bass_model, tenor_model, alto_model)
  # print(next_chord)
  # next_chord = normalize_chord_over_bass(next_chord)
  # print(next_chord)

  # next_chord = get_next_chord(next_chord, starting_melodies[1], bass_model, tenor_model, alto_model)
  # print(next_chord)
  # next_chord = normalize_chord_over_bass(next_chord)
  # print(next_chord)

  # next_chord = get_next_chord(next_chord, starting_melodies[2], bass_model, tenor_model, alto_model)
  # print(next_chord)
  # next_chord = normalize_chord_over_bass(next_chord)
  # print(next_chord)

  # next_chord = get_next_chord(next_chord, starting_melodies[3], bass_model, tenor_model, alto_model)
  # print(next_chord)
  # next_chord = normalize_chord_over_bass(next_chord)
  # print(next_chord)


  
  #soprano_model = keras.models.load_model("./models/super_soprano_model")

  # NOTE: The following code is awful, apologies.

  # Empty list to hold second chords for each of the starting chords
  # second_chords = []

  # # Iterates through each starting chord and gets the next chord
  # for i in range(len(starting_chords)):

  #   # Prints the starting chord
  #   print(f"{i}: {starting_chords[i]} -> ", end="")

  #   # Gets next chord using the models
  #   next_chord = get_next_chord(starting_chords[i], bass_model, tenor_model, alto_model, soprano_model)
  #   print(next_chord)

  #   # appends the 4 notes of the chord to the second chord list and transforms them
  #   # from changes relative to previous chord to absolute values
  #   second_chords.append([starting_chords[i][j] + next_chord[j] for j in range(4)])
  #   second_chords[i] = [item - second_chords[i][0] for item in second_chords[i]]
  
  # print(second_chords)


  # # The remainder is as above for the third and four sets of chords. The process
  # # should have been made a function.

  # third_chords = []

  # for i in range(len(second_chords)):
  #   print(f"{i}: {second_chords[i]} -> ", end="")
  #   next_chord = get_next_chord(second_chords[i], bass_model, tenor_model, alto_model, soprano_model)
  #   print(next_chord)
  #   third_chords.append([second_chords[i][j] + next_chord[j] for j in range(4)])
  #   third_chords[i] = [item - third_chords[i][0] for item in third_chords[i]]

  # print(third_chords)

  # fourth_chords = []

  # for i in range(len(third_chords)):
  #   print(f"{i}: {third_chords[i]} -> ", end="")
  #   next_chord = get_next_chord(third_chords[i], bass_model, tenor_model, alto_model, soprano_model)
  #   print(next_chord)
  #   fourth_chords.append([third_chords[i][j] + next_chord[j] for j in range(4)])
  #   fourth_chords[i] = [item - fourth_chords[i][0] for item in fourth_chords[i]]

  # print(fourth_chords)

  # for i in range(len(starting_chords)):
  #   print(f"{starting_chords[i]}, {second_chords[i]}, {third_chords[i]}, {fourth_chords[i]}")
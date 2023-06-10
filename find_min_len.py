import json

        
def main():
    MAX_MELODY_LENGTH = 160
    MIN_MELODY_LENGTH = 32
    MIN_HARMONY_LENGTH = 32 * 3

    with open('./data/raw_data/jsb-chorales-quarter.json') as json_file:
        data = json.load(json_file)

    # Extract melodies and harmonies from raw data
    train_melodies = extract_melodies(data, 'train')
    test_melodies = extract_melodies(data, 'test')
    validation_melodies = extract_melodies(data, 'valid')

    train_harmonies = extract_harmonies(data, 'train')
    test_harmonies = extract_harmonies(data, 'test')
    validation_harmonies = extract_harmonies(data, 'valid')

    # Find the indices for which the melody and harmony have unequal lengths (Problem with the data)
    train_mismatches = find_mismatched_indices(train_melodies, train_harmonies)
    test_mismatches = find_mismatched_indices(test_melodies, test_harmonies)
    validation_mismatches = find_mismatched_indices(validation_melodies, validation_harmonies)

    # Safely remove the items at each of the indices found above by removing them from largest index first
    for mismatch_index in sorted(train_mismatches, reverse=True):
        del train_harmonies[mismatch_index]
        del train_melodies[mismatch_index]

    for mismatch_index in sorted(test_mismatches, reverse=True):
        del test_harmonies[mismatch_index]
        del test_melodies[mismatch_index]

    for mismatch_index in sorted(validation_mismatches, reverse=True):
        del validation_harmonies[mismatch_index]
        del validation_melodies[mismatch_index]

    for melodies in [train_melodies, test_melodies, validation_melodies]:
        for melody in melodies:
            if len(melody) is 25:
                print("removing melody")
                melodies.remove(melody)

    for harmonies in [train_harmonies, test_harmonies, validation_harmonies]:
        for harmony in harmonies:
            if len(harmony) is 25:
                print("removing harmony")
                harmonies.remove(harmony)


    for melodies in [train_melodies, test_melodies, validation_melodies]:
        for melody in melodies:
            if len(melody) < 32:
                print("still in there")

    trimmed_train_melodies = [melody[:MIN_MELODY_LENGTH] for melody in train_melodies]
    trimmed_test_melodies = [melody[:MIN_MELODY_LENGTH] for melody in test_melodies]
    trimmed_validation_melodies = [melody[:MIN_MELODY_LENGTH] for melody in validation_melodies]

    for melodies in [trimmed_train_melodies, trimmed_test_melodies, trimmed_validation_melodies]:
        for melody in melodies:
            if len(melody) != MIN_MELODY_LENGTH:
                print("Problem melody")

    trimmed_train_harmonies = [harmony[:MIN_MELODY_LENGTH] for harmony in train_harmonies]
    trimmed_test_harmonies = [harmony[:MIN_MELODY_LENGTH] for harmony in test_harmonies]
    trimmed_validation_harmonies = [harmony[:MIN_MELODY_LENGTH] for harmony in validation_harmonies]

    for harmonies in [trimmed_train_harmonies, trimmed_test_harmonies, trimmed_validation_harmonies]:
        for harmony in harmonies:
            if len(harmony) != MIN_MELODY_LENGTH:
                print(len(harmony))

    # for harmonies in [train_harmonies, test_harmonies, validation_harmonies]:
    #     for harmony in harmonies:
    #         harmony = trim_data(harmony, MIN_HARMONY_LENGTH)

    # for melodies in [train_melodies, test_melodies, validation_melodies]:
    #     for melody in melodies:
    #         print(len(melody))

    # for harmonies in [train_harmonies, test_harmonies, validation_harmonies]:
    #     for harmony in harmonies:
    #         if len(harmony) != MIN_HARMONY_LENGTH:
    #             print("harmony problem")


    # # Add padding of 0's to melodies and harmonies to achieve the same length
    # for melodies in [train_melodies, test_melodies, validation_melodies]:
    #     for melody in melodies:
    #         add_melody_padding(melody, MAX_MELODY_LENGTH)
   
    # for harmonies in [train_harmonies, test_harmonies, validation_harmonies]:
    #     for harmony in harmonies:
    #         add_harmony_padding(harmony, MAX_MELODY_LENGTH)

    # # Check for consistent length
    # # for melodies in [train_melodies, test_melodies, validation_melodies]:
    # #     for melody in melodies:
    # #         if len(melody) != 160:
    # #             print(melody)

    # # for harmonies in [train_harmonies, test_harmonies, validation_harmonies]:
    # #     for harmony in harmonies:
    # #         if len(harmony) != 160:
    # #             print(harmony)

    # #Create flattened harmony data
    train_harmonies_flat = list()
    test_harmonies_flat = list()
    validation_harmonies_flat = list()
    for chorale in trimmed_train_harmonies:
        train_harmonies_flat.append(generate_flattened_harmony(chorale))
    for chorale in trimmed_test_harmonies:
        test_harmonies_flat.append(generate_flattened_harmony(chorale))
    for chorale in trimmed_validation_harmonies:
        validation_harmonies_flat.append(generate_flattened_harmony(chorale))    

    for harmonies in [train_harmonies_flat, test_harmonies_flat, validation_harmonies_flat]:
        for harmony in harmonies:
            if len(harmony) != MIN_HARMONY_LENGTH:
                print("problem flat harmony")


    # Create dictionaries to be saved as JSON files
    melodies = dict()
    melodies['train'] = trimmed_train_melodies
    melodies['test'] = trimmed_test_melodies
    melodies['validation'] = trimmed_validation_melodies

    # harmonies = dict()
    # harmonies['train'] = train_harmonies
    # harmonies['test'] = test_harmonies
    # harmonies['validation'] = validation_harmonies

    harmonies_flat = dict()
    harmonies_flat['train'] = train_harmonies_flat
    harmonies_flat['test'] = test_harmonies_flat
    harmonies_flat['validation'] = validation_harmonies_flat

    # for key in melodies.keys():
    #     for i in range(len(melodies[key])):
    #         for j in range(len(melodies[key][i])):
    #             harmonies[key][i][j].append(melodies[key][i][j])

    # with open('./data/processed_data/bach_chorale_full.json', 'w') as full_file:
    #     json.dump(harmonies, full_file)
    
    with open('./data/processed_data/trimmed_bach_chorale_melodies.json', 'w') as melody_file:
        json.dump(melodies, melody_file)

    # with open('./data/processed_data/bach_chorale_harmonies_grouped.json', 'w') as harmony_file:
    #     json.dump(harmonies, harmony_file)

    with open('./data/processed_data/trimmed_bach_chorale_harmonies_flat.json', 'w') as harmony_flat_file:
        json.dump(harmonies_flat, harmony_flat_file)
    


def extract_melodies(data: dict, partition: str) -> list:
    melody_list = list()

    for chorale in data[partition]:
        indv_melody = list()
        for chord in chorale:
            if len(chord) > 0:
                indv_melody.append(max(chord))
        melody_list.append(indv_melody)

    return melody_list

def extract_harmonies(data: dict, partition: str) -> list:
    harmony_list = list()

    for chorale in data[partition]:
        indv_harmony = list()
        for chord in chorale:
            if len(chord) > 1:
                harmony = chord[:-1]
                if len(harmony) < 3:
                    # Duplicate middle part until 3 parts achieved
                    while(len(harmony) < 3):
                        harmony.append(harmony[-1])
            indv_harmony.append(harmony)
        harmony_list.append(indv_harmony)
    
    return harmony_list

def generate_flattened_harmony(harmony: list) -> list:
    return [note for chord in harmony for note in chord]

def trim_data(data: list, length: int) -> list:
    return data[:length]



def add_melody_padding(melody: list, req_length: int) -> list:
    while(len(melody) < req_length):
        melody.append(0)

def add_harmony_padding(harmony: list, req_length: int) -> list:
    while(len(harmony) < req_length):
        harmony.append([0, 0, 0])


def find_mismatched_indices(melodies: list, harmonies: list) -> list:
    mismatched_indices = list()
    for i in range(len(melodies)):
        if len(melodies[i]) != len(harmonies[i]):
            mismatched_indices.append(i)

    return mismatched_indices
    

if __name__ == "__main__":
    main()
      
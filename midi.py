from midiutil import MIDIFile


def main():
    chords = [[72, 76, 79, 84], [72, 76, 79, 84], [71, 74, 79, 86], [73, 73, 73, 73]]
    
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

    with open("./midi/test_midi_files/test.mid", "wb") as output_file:
        midi.writeFile(output_file)


if __name__ == '__main__':
    main()
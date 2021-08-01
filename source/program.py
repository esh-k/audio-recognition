import sounddevice as sd
import simpleaudio as sa
import numpy as np
import matchsong as ms
import databasecreate as dc
import pathlib
import os

SAMPLE_RATE = 44100
SAMPLE_TIME = 10
MAX_TRIES = 3

def record_samples(duration, samplerate=SAMPLE_RATE, playback=False):
    myrecording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16)
    sd.wait()
    if playback:
        input("Press any key to playback")
        play_obj = sa.play_buffer(myrecording, 1, 2, SAMPLE_RATE)
        play_obj.wait_done()
    return myrecording.reshape(-1)

def rec_match(num_tries=MAX_TRIES):
    match = None
    tally = None
    for i in range(MAX_TRIES):
        samples = record_samples(15)
        match, tally = ms.match_song(samples=samples, dbfile=dc.DEFAULT_DATABASE_PATH)
        if match[2]:
            return (match, tally)
        print("retrying...")
    return (match, tally)

def main():
    fileparentdir = pathlib.Path(__file__).parent.resolve()
    os.chdir(fileparentdir)
    songnames = [os.path.splitext(f)[0] for f in os.listdir(dc.DEFAULT_WAVFILES_PATH) if os.path.splitext(f)[1] == ".wav"]
    songfiles = [os.path.join(dc.DEFAULT_WAVFILES_PATH, f + ".wav") for f in songnames]
    while True:
        x = input("Press 's' to create database; 'r' to search song; and any other key to exit.")
        if x == 's':
            dc.add_songs2db_parallel(songfiles, dc.DEFAULT_DATABASE_PATH, print_progress=True)
        elif x == 'r':
            input("Press any key to start search song")
            match, tally = rec_match()
            print(f"found match '{songfiles[match[0]]}'." if match[2] else "Song not found.")
            print(tally)
        else:
            return

if __name__ == '__main__':
    main()
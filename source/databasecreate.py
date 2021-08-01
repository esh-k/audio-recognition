from scipy.io import wavfile
import numpy as np
import os
import csvwriter
import analyzer
from joblib import Parallel, delayed
import time

DEFAULT_DATABASE_PATH = "..\\data\\database.csv"
DEFAULT_WAVFILES_PATH = "..\\wavfiles"
DEFAULT_RECORDINGS_PATH = "..\\recordings"
TABLE_COLUMN_TYPES = [int, int, int]

# add songs
def analyze_song(songfile, songid, print_progress=False):
    if print_progress:
        print(f"converting {songid}: '{songfile}'")
    tic = time.time()
    fs, samples = wavfile.read(songfile)
    table = list(analyzer.fingerprint(samples, songid, Fs=fs))
    if print_progress:
        print(f"{time.time()-tic}s done converting {songid}: '{songfile}'")
    return table

def add_song2db(songfile, id, dbfile):
    table = analyze_song(songfile, id)
    csvwriter.write2csv(table, dbfile)
    return table

def add_songs2db(songfiles, dbfile, print_progress=False):
    database = []
    for i in range(len(songfiles)):
        if print_progress:
            print(f"converting {i}: '{songfiles[i]}'")
        database += analyze_song(songfiles[i], i)
    database.sort(key=lambda x: x[0])
    csvwriter.write2csv(database, dbfile)
    return database

def add_songs2db_parallel(songfiles, dbfile, print_progress=False):
    tic = time.time()
    tables = Parallel(n_jobs=os.cpu_count())(delayed(analyze_song)(songfiles[i], i, print_progress) for i in range(len(songfiles)))
    database = []
    for table in tables:
        database += table
    database.sort(key=lambda x: x[0])
    csvwriter.write2csv(database, dbfile)
    if print_progress:
        print(f"total time: {time.time()-tic}")
    return database
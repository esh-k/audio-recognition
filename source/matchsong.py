import databasecreate as dc
from scipy.io import wavfile
import analyzer
import csvwriter
import math

def binary_search_helper(l, r, key, arr):
    if r < l:
        return -1
    c = (l + r)//2
    if arr[c] == key:
        return c
    elif arr[c] < key:
        return binary_search_helper(c+1, r, key, arr)
    else:
        return binary_search_helper(l, c-1, key, arr)

def binary_search(key, arr):
    return binary_search_helper(0, len(arr)-1, key, arr)

def estimate_gaussian(tally, id):
    if not tally:
        return 0
    if len(tally) == 1:
        return 1
    else:
        values = list(tally.values())
        values.remove(tally[id])
        m = len(tally.keys()) - 1
        mu = sum(values)/m
        std2 = sum([(x-mu)**2 for x in values])/m + 1e-3
        return 1/math.sqrt(2 * math.pi * std2) * math.exp(-(tally[id]-mu)**2/2/std2)

def match_song_from_db(recording, dbtable, threshold=0.9):
    tally = {}
    match = [-1,-1,False]
    dbtable_hashes, _, _ = zip(*dbtable)
    for x in recording:
        idx = binary_search(x[0], dbtable_hashes)
        if idx == -1:
            continue
        first = True
        while first or (idx < len(dbtable_hashes) - 1 and dbtable_hashes[idx] == dbtable_hashes[idx-1]):
            if dbtable[idx][2] in tally:
                tally[dbtable[idx][2]] += 1
            else:
                tally[dbtable[idx][2]] = 1
            if tally[dbtable[idx][2]] > match[1]:
                match[1] = tally[dbtable[idx][2]]
                match[0] = int(dbtable[idx][2])
            idx += 1
            first = False
    match[2] = 1 - estimate_gaussian(tally, match[0]) > threshold
    return (match, tally)

def match_song(samples=None, recfile=None, dbfile=None, dbtable=None):
    if dbfile is None and dbtable is None:
        raise ValueError("Expected either 'dbtable' or 'dbfile' keyword argument")
    elif dbfile:
        dbtable = list(filter(lambda x : x != [], csvwriter.readcsv(dbfile, column_types=dc.TABLE_COLUMN_TYPES)))
    
    fs = 44100
    if samples is None and recfile is None:
        raise ValueError("Expected either 'samples' or 'recfile' keyword argument")
    elif recfile:
        fs, samples = wavfile.read(recfile)

    recording = list(analyzer.fingerprint(samples, 0, Fs=fs))
    return match_song_from_db(recording, dbtable)

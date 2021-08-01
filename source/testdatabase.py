import os
import databasecreate as dc
import matchsong as ms

os.chdir("source")
demofiles = ['..\\WavFiles\\1698 Pachelbel , Canon in D.wav',
             '..\\WavFiles\\1788 Mozart- Symphony No. 40, 1st movement.wav',
             '..\\WavFiles\\1721 Bach , Brandenburg Concerto No. 3, 1st movement.wav',
             '..\\WavFiles\\1685 Purcell , Trumpet Tune and Air.wav',
             '..\\WavFiles\\1709 Bach , Toccata in D minor.wav',
             '..\\WavFiles\\Let It Be.wav']

recordingfile = "..\\recordings\\rec_let_it_be.wav"
dbfile = "..\\Data\\test_database.csv"
dbfile2 = "..\\Data\\test_recording_database.csv"

dc.add_songs2db_parallel(demofiles, dbfile, print_progress=True)

match, tally = ms.match_song(recfile=recordingfile, dbfile=dbfile)
print(f"found match '{demofiles[match[0]]}'." if match[2] else "Song not found.")
print(tally)
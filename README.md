# audio-recognition
This is my attempt at replicating from the [shazam paper](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf).

### Setup
Install the following packages<br>
`pip install scipy numpy matplotlib joblib sounddevice simpleaudio pathlib`

### Running
Make sure you have a mic before trying this out
- Place original song files in 'audio-recognition/wavfiles/...' 
  - Note: The project currently only support reading wav files.
- Run the 'program.py' and press 's' to create the database
- Press 'r' to record a song.

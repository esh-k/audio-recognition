import numpy as np
import matplotlib.mlab as mlab
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)
from operator import itemgetter
import math

IDX_FREQ_I = 0
IDX_TIME_J = 1
DEFAULT_FS = 44100
DEFAULT_WINDOW_SIZE = 4096
DEFAULT_OVERLAP_RATIO = 0.5
DEFAULT_FAN_VALUE = 30
DEFAULT_AMP_MIN = 10
PEAK_NEIGHBORHOOD_SIZE = 20
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 400
MIN_HASH_FREQ_DELTA = 0
MAX_HASH_FREQ_DELTA = 60
PEAK_SORT = True
FINGERPRINT_REDUCTION = 20

MAX_SAMPLE_SIZE = 524288


a1 = np.fromiter(map(lambda x: (2-math.exp(x)), np.arange(math.log(2), step=math.log(2)/600)), dtype=np.float)
a2 = np.zeros(int(DEFAULT_WINDOW_SIZE/2 + 1 - len(a1)), dtype=np.float)
FFT_FILTER = np.concatenate((a1, a2))
FFT_FILTER = FFT_FILTER.reshape(len(FFT_FILTER), 1)

def fingerprint(channel_samples, song_number, Fs=DEFAULT_FS,
                wsize=DEFAULT_WINDOW_SIZE,
                wratio=DEFAULT_OVERLAP_RATIO,
                fan_value=DEFAULT_FAN_VALUE,
                amp_min=DEFAULT_AMP_MIN):

    arr2D = mlab.specgram(
                channel_samples,
                NFFT=wsize,
                Fs=Fs,
                window=mlab.window_hanning,
                noverlap=int(wsize * wratio))[0]

    if np.shape(FFT_FILTER)[0] != np.shape(arr2D)[0]:
      raise Exception("size missmatch")

    arr2D = 10 * np.log10(replaceZeroes(arr2D))
    arr2D = np.multiply(arr2D, FFT_FILTER)
    arr2D[arr2D == -np.inf] = 0 

    local_maxima = get_2D_peaks(arr2D, amp_min=amp_min)

    return generate_hashes(local_maxima, song_number, fan_value=fan_value)

def replaceZeroes(data):
    min_nonzero = np.min(data[np.nonzero(data)])
    data[data == 0] = min_nonzero
    return data

def get_2D_peaks(arr2D, amp_min=DEFAULT_AMP_MIN):
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood,
                                       border_value=1)

    detected_peaks = local_max ^ eroded_background
    amps = arr2D[detected_peaks]
    j, i = np.where(detected_peaks)
    amps = amps.flatten()
    
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min] 

    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]
    
    return zip(frequency_idx, time_idx)

def generate_hashes(peaks, song_number, fan_value=DEFAULT_FAN_VALUE):
    peaks = sorted(peaks, key=itemgetter(1))
    for i in range(len(peaks)):
        for j in range(1, fan_value):
            if (i + j) < len(peaks):
                freq1 = peaks[i][IDX_FREQ_I]
                freq2 = peaks[i + j][IDX_FREQ_I]
                fdelta = abs(freq1 - freq2)
                t1 = peaks[i][IDX_TIME_J]
                t2 = peaks[i + j][IDX_TIME_J]
                t_delta = t2 - t1
                if t_delta > MIN_HASH_TIME_DELTA and t_delta <= MAX_HASH_TIME_DELTA\
                    and fdelta > 0 and fdelta <= MAX_HASH_FREQ_DELTA:
                    yield (freq1*10**6 + freq2*10**3 +t_delta, t1, song_number)

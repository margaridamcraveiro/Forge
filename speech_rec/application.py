import librosa
import numpy as np
import pandas as pd


def extract_features(path):
    y, sr = librosa.load(path, sr=None)
    # convert to mono audio
    y = librosa.to_mono(y)
    # crop to get only the first 7 seconds
    duration_seconds = 7
    y = y[:duration_seconds * sr]

    # Pitch (F0)
    f0, voiced_flag, _ = librosa.pyin(y, fmin=80, fmax=300)
    f0 = f0[~np.isnan(f0)]  # keep voiced frames

    # Loudness (RMS)
    rms = librosa.feature.rms(y=y)[0]

    # Speaking rate (approximate syllable rate)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    if isinstance(tempo, (np.ndarray, list, tuple)):
        # tempo is a one element array
        tempo = tempo[0]

    return {
        "pitch_mean": np.mean(f0),
        "pitch_std": np.std(f0),
        "loudness_mean": np.mean(rms),
        "loudness_std": np.std(rms),
        "speaking_rate": tempo 
}


def initiateIntervals():
    """returns lower, upper"""
    feat1 = extract_features("../sounds/harvard.wav")
    feat2 = extract_features("../sounds/jeff.wav")


    df = pd.DataFrame([feat1, feat2])
    confident_profile = df.mean()
    confident_variability = df.std()

    lower = confident_profile - 2 * confident_variability
    upper = confident_profile + 2 * confident_variability
    return lower, upper

def to_scalar(x):
    if isinstance(x, dict):
        if len(x) == 0:
            return np.nan
        return float(x[0])
    else: 
        return x

def isConfident(filepath, lower, upper): 
    """..."""
    new_feat = extract_features(filepath)
    new_feat = pd.Series({k: to_scalar(v) for k, v in new_feat.items()})
    ok = (new_feat >= lower) & (new_feat <= upper)   
    return ok.all()
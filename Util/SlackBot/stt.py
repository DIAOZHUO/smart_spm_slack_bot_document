import time

import whisper
import numpy as np
from moviepy.audio.io.readers import FFMPEG_AudioReader

model = whisper.load_model("medium")

# hard-coded audio hyperparameters
SAMPLE_RATE = 16000

def load_audio(file: str, sr: int = SAMPLE_RATE):
    """
    Open an audio file and read as mono waveform, resampling as necessary
    Parameters
    ----------
    file: str
        The audio file to open
    sr: int
        The sample rate to resample the audio if necessary
    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """
    # fps: ar
    # nchannels=1: ac=1
    # nbytes=2: format=s16le & acodec=pcm_s16le
    reader = FFMPEG_AudioReader(file, fps=sr, nbytes=2, buffersize=float('inf'), nchannels=1)

    if reader.buffer.shape[0] == 0:
        raise RuntimeError(f"Failed to load audio: {file}")

    return reader.buffer.flatten().astype(np.float32)




def stt(audio_path):
    t = time.time()
    audio = load_audio(audio_path)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    language = max(probs, key=probs.get)

    # decode the audio
    result = whisper.decode(model, mel, options=whisper.DecodingOptions(task="transcribe"))

    if language != "en":
        translate = whisper.decode(model, mel, whisper.DecodingOptions(task="translate")).text
    else:
        translate = result.text
    print("tts time:", time.time()-t)
    return language, result.text, translate


def stt_fast(audio_path, language_code):
    t = time.time()
    audio = load_audio(audio_path)
    audio = whisper.pad_or_trim(audio)
    result = model.transcribe(audio, language=language_code)
    print("tts time:", time.time() - t)
    return result["text"]



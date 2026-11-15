import os
import wave
import struct
import random
import subprocess
from datetime import datetime
import numpy as np

SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

SAMPLE_RATE = 44100
BPM = random.choice([132, 136, 140, 144])
DURATION_SEC = 45
TOTAL_SAMPLES = SAMPLE_RATE * DURATION_SEC
BEAT_SAMPLES = int(SAMPLE_RATE * 60 / BPM)
STEP_SAMPLES = BEAT_SAMPLES // 4  # 16th notes

t = np.linspace(0, DURATION_SEC, TOTAL_SAMPLES, endpoint=False)
audio = np.zeros(TOTAL_SAMPLES, dtype=np.float64)

# 1. Punchy 4-on-the-floor Rave Kick Drum
kick_len = int(SAMPLE_RATE * 0.28)
kt = np.linspace(0, 0.28, kick_len, endpoint=False)
kick_freq = 48 + 130 * np.exp(-kt * 28)
kick_phase = 2 * np.pi * np.cumsum(kick_freq) / SAMPLE_RATE
kick_wave = np.sin(kick_phase) * np.exp(-kt * 11)
kick_wave = np.tanh(kick_wave * 2.2) * 0.85

for pos in range(0, TOTAL_SAMPLES - kick_len, BEAT_SAMPLES):
    audio[pos:pos + kick_len] += kick_wave

# 2. Offbeat Rave Open Hi-Hat
hat_len = int(SAMPLE_RATE * 0.14)
ht = np.linspace(0, 0.14, hat_len, endpoint=False)
rng = np.random.default_rng()
noise = rng.uniform(-1, 1, hat_len)
# Simple high-pass effect via first-order difference
hp_noise = np.diff(noise, prepend=0)
hat_wave = hp_noise * np.exp(-ht * 24) * 0.35

for pos in range(BEAT_SAMPLES // 2, TOTAL_SAMPLES - hat_len, BEAT_SAMPLES):
    audio[pos:pos + hat_len] += hat_wave

# 3. Acid / Rave Synth Bassline (16-step pattern)
scale_freqs = [55.0, 65.41, 73.42, 82.41, 98.0, 110.0, 130.81]  # A minor rave scale
pattern = [random.choice(scale_freqs) * random.choice([1, 1, 2]) for _ in range(16)]

for step_idx in range(TOTAL_SAMPLES // STEP_SAMPLES):
    start = step_idx * STEP_SAMPLES
    end = min(start + STEP_SAMPLES, TOTAL_SAMPLES)
    seg_len = end - start
    st = np.linspace(0, seg_len / SAMPLE_RATE, seg_len, endpoint=False)

    freq = pattern[step_idx % 16]
    # Sawtooth wave with resonant sweep
    saw = 2.0 * ((st * freq) % 1.0) - 1.0
    env = np.exp(-st * 9.0)
    cutoff = 0.15 + 0.75 * np.exp(-st * 14.0)
    synth = np.tanh(saw * (2.5 * cutoff)) * env * 0.45
    audio[start:end] += synth

# Normalize to prevent clipping
audio = audio / np.max(np.abs(audio)) * 0.9
pcm = (audio * 32767).astype(np.int16)

timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
wav_path = os.path.join(SAVE_DIR, f"rave_{BPM}bpm_{timestamp}.wav")
mp3_path = os.path.join(SAVE_DIR, f"rave_{BPM}bpm_{timestamp}.mp3")

with wave.open(wav_path, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(pcm.tobytes())

# Convert to MP3 if ffmpeg is installed on Ubuntu runner, otherwise keep WAV
if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0:
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-b:a", "192k", mp3_path], check=True)
    os.remove(wav_path)
    print(f"Generated rave track: {mp3_path}")
else:
    print(f"Generated rave track: {wav_path}")

import os
import math
import wave
import struct
import random
import subprocess
from datetime import datetime, timezone

SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

SAMPLE_RATE = 44100
BPM = random.choice([132, 136, 140])
DURATION_SEC = 30
TOTAL_SAMPLES = SAMPLE_RATE * DURATION_SEC
BEAT_SAMPLES = int(SAMPLE_RATE * 60 / BPM)
STEP_SAMPLES = BEAT_SAMPLES // 4  # 16th notes

# Precompute a single 909-style rave kick drum
kick_len = int(SAMPLE_RATE * 0.25)
kick_wave = []
phase = 0.0
for i in range(kick_len):
    t = i / SAMPLE_RATE
    freq = 48.0 + 135.0 * math.exp(-t * 28.0)
    phase += 2.0 * math.pi * freq / SAMPLE_RATE
    sample = math.sin(phase) * math.exp(-t * 11.0)
    kick_wave.append(math.tanh(sample * 2.2) * 0.85)

# Precompute an offbeat open hi-hat
hat_len = int(SAMPLE_RATE * 0.12)
hat_wave = []
prev_noise = 0.0
for i in range(hat_len):
    t = i / SAMPLE_RATE
    noise = random.uniform(-1.0, 1.0)
    hp = noise - prev_noise
    prev_noise = noise
    hat_wave.append(hp * math.exp(-t * 26.0) * 0.28)

# Generate a 16-step acid rave bassline pattern
scale_freqs = [55.0, 65.41, 73.42, 82.41, 98.0, 110.0, 130.81]
pattern = [random.choice(scale_freqs) * random.choice([1.0, 2.0]) for _ in range(16)]

audio = [0.0] * TOTAL_SAMPLES

# Layer 1: 4-on-the-floor kick
for pos in range(0, TOTAL_SAMPLES - kick_len, BEAT_SAMPLES):
    for j in range(kick_len):
        audio[pos + j] += kick_wave[j]

# Layer 2: Offbeat hi-hat
for pos in range(BEAT_SAMPLES // 2, TOTAL_SAMPLES - hat_len, BEAT_SAMPLES):
    for j in range(hat_len):
        audio[pos + j] += hat_wave[j]

# Layer 3: Acid synth bassline
for step_idx in range(TOTAL_SAMPLES // STEP_SAMPLES):
    start = step_idx * STEP_SAMPLES
    end = min(start + STEP_SAMPLES, TOTAL_SAMPLES)
    freq = pattern[step_idx % 16]
    for i in range(start, end):
        st = (i - start) / SAMPLE_RATE
        saw = 2.0 * ((st * freq) % 1.0) - 1.0
        env = math.exp(-st * 9.0)
        cutoff = 0.2 + 0.75 * math.exp(-st * 14.0)
        audio[i] += math.tanh(saw * (2.5 * cutoff)) * env * 0.42

# Normalize audio to 16-bit PCM
peak = max(abs(x) for x in audio) or 1.0
scale = 32000.0 / peak
pcm_bytes = bytearray()
for sample in audio:
    pcm_bytes.extend(struct.pack("<h", int(sample * scale)))

timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
wav_path = os.path.join(SAVE_DIR, f"rave_{BPM}bpm_{timestamp}.wav")
mp3_path = os.path.join(SAVE_DIR, f"rave_{BPM}bpm_{timestamp}.mp3")

with wave.open(wav_path, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(pcm_bytes)

# Convert to MP3 using pre-installed ffmpeg
if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode == 0:
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-b:a", "192k", mp3_path], check=True)
    os.remove(wav_path)
    print(f"Generated rave track: {mp3_path}")
else:
    print(f"Generated rave track: {wav_path}")

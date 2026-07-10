#!/usr/bin/env python3
"""
Generate pre-rendered metronome audio files for BPM range 40-240.

Each file contains exactly BPM beats spread over 60 seconds,
ensuring seamless looping (duration is always an exact multiple of the beat interval).

Output format: WAV mono 44100Hz 16-bit → converted to MP3 64kbps for smaller file size.
Output directory: ./metronome-files/

Requirements:
  pip install numpy
  brew install ffmpeg  (or apt install ffmpeg)

Usage:
  python scripts/generate-metronome-files.py
"""

import os
import subprocess
import struct
import math
import sys

SAMPLE_RATE = 44100
CLICK_FREQ = 880.0
CLICK_DURATION = 0.05  # 50ms
AMPLITUDE = 0.7
BPM_MIN = 40
BPM_MAX = 240
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'metronome-files')


def generate_click_samples():
    """Generate a single click (880Hz, 50ms, with envelope decay)."""
    num_samples = int(SAMPLE_RATE * CLICK_DURATION)
    samples = []
    for i in range(num_samples):
        envelope = 1.0 - (i / num_samples)
        value = math.sin(2.0 * math.pi * CLICK_FREQ * i / SAMPLE_RATE) * envelope * AMPLITUDE
        samples.append(value)
    return samples


def generate_metronome_wav(bpm: int, click_samples: list, output_path: str):
    """Generate a WAV file with clicks at the given BPM for exactly 60 seconds."""
    num_beats = bpm  # BPM beats in 60 seconds
    total_samples = SAMPLE_RATE * 60  # exactly 60 seconds

    # Create silence buffer
    audio = [0.0] * total_samples

    # Place clicks at each beat position (individually rounded to avoid drift)
    for beat in range(num_beats):
        start = round(beat * SAMPLE_RATE * 60.0 / bpm)
        for i, sample in enumerate(click_samples):
            pos = start + i
            if pos < total_samples:
                audio[pos] += sample

    # Write WAV file
    write_wav(output_path, audio)


def write_wav(path: str, samples: list):
    """Write a mono 16-bit WAV file."""
    num_samples = len(samples)
    data_size = num_samples * 2  # 16-bit = 2 bytes per sample
    file_size = 36 + data_size

    with open(path, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', file_size))
        f.write(b'WAVE')
        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # chunk size
        f.write(struct.pack('<H', 1))   # PCM format
        f.write(struct.pack('<H', 1))   # mono
        f.write(struct.pack('<I', SAMPLE_RATE))
        f.write(struct.pack('<I', SAMPLE_RATE * 2))  # byte rate
        f.write(struct.pack('<H', 2))   # block align
        f.write(struct.pack('<H', 16))  # bits per sample
        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        for sample in samples:
            clamped = max(-1.0, min(1.0, sample))
            int_val = int(clamped * 32767)
            f.write(struct.pack('<h', int_val))


def convert_to_mp3(wav_path: str, mp3_path: str):
    """Convert WAV to MP3 using ffmpeg."""
    result = subprocess.run(
        ['ffmpeg', '-y', '-i', wav_path, '-codec:a', 'libmp3lame', '-b:a', '64k', '-ar', '44100', '-ac', '1', mp3_path],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"  ffmpeg error: {result.stderr}", file=sys.stderr)
        return False
    return True


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    click_samples = generate_click_samples()
    total = BPM_MAX - BPM_MIN + 1

    print(f"Generating {total} metronome files ({BPM_MIN}-{BPM_MAX} BPM)...")
    print(f"Output: {OUTPUT_DIR}")
    print()

    for bpm in range(BPM_MIN, BPM_MAX + 1):
        wav_path = os.path.join(OUTPUT_DIR, f'{bpm}.wav')
        mp3_path = os.path.join(OUTPUT_DIR, f'{bpm}.mp3')

        sys.stdout.write(f"\r  [{bpm - BPM_MIN + 1}/{total}] Generating {bpm} BPM...")
        sys.stdout.flush()

        generate_metronome_wav(bpm, click_samples, wav_path)
        success = convert_to_mp3(wav_path, mp3_path)

        # Remove the WAV intermediate file
        if success and os.path.exists(wav_path):
            os.remove(wav_path)

    print(f"\n\nDone! {total} MP3 files generated in {OUTPUT_DIR}")

    # Print total size
    total_size = sum(
        os.path.getsize(os.path.join(OUTPUT_DIR, f))
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith('.mp3')
    )
    print(f"Total size: {total_size / 1024 / 1024:.1f} MB")


if __name__ == '__main__':
    main()

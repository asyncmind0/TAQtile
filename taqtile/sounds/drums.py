import numpy as np
import simpleaudio as sa
from scipy.signal import butter, lfilter


def hihat_open0(duration=0.4, volume=0.5):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate white noise
    white_noise = np.random.uniform(-1, 1, len(t))

    # Define a bandpass filter
    def bandpass_filter(data, low, high, sample_rate, order=5):
        nyquist = 0.5 * sample_rate
        low /= nyquist
        high /= nyquist
        b, a = butter(order, [low, high], btype="band")
        return lfilter(b, a, data)

    # Apply the bandpass filter to the white noise
    filtered_noise = bandpass_filter(white_noise, 3000, 10000, sample_rate)

    # Apply an envelope to the filtered noise
    envelope = np.exp(-t * 5)

    # Combine the filtered noise with the envelope
    hi_hat_wave = (filtered_noise * envelope) * volume

    # Normalize the wave to 16-bit PCM format
    audio_data = (hi_hat_wave * 32767 / np.max(np.abs(hi_hat_wave))).astype(
        np.int16
    )

    # Play the audio using the simpleaudio library
    play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)
    play_obj.wait_done()


def hihat_open1(duration=0.4, volume=0.5):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate white noise
    white_noise = np.random.uniform(-1, 1, len(t))

    # Define a bandpass filter
    def bandpass_filter(data, low, high, sample_rate, order=5):
        nyquist = 0.5 * sample_rate
        low /= nyquist
        high /= nyquist
        b, a = butter(order, [low, high], btype="band")
        return lfilter(b, a, data)

    # Define a high-pass filter
    def highpass_filter(data, cutoff, sample_rate, order=5):
        nyquist = 0.5 * sample_rate
        cutoff /= nyquist
        b, a = butter(order, cutoff, btype="high")
        return lfilter(b, a, data)

    # Apply the bandpass filter to the white noise
    filtered_noise = bandpass_filter(white_noise, 4000, 12000, sample_rate)

    # Apply the high-pass filter to the white noise
    high_passed_noise = highpass_filter(filtered_noise, 6000, sample_rate)

    # Apply an envelope to the filtered noise
    envelope = np.exp(-t * 5)

    # Combine the filtered noise with the envelope
    hi_hat_wave = (high_passed_noise * envelope) * volume

    # Normalize the wave to 16-bit PCM format
    audio_data = (hi_hat_wave * 32767 / np.max(np.abs(hi_hat_wave))).astype(
        np.int16
    )

    # Play the audio using the simpleaudio library
    play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)
    play_obj.wait_done()


def snare_drum(duration=0.5, volume=0.02):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate a sine wave for the snare's fundamental frequency
    sine_wave = np.sin(180 * 2 * np.pi * t)

    # Generate white noise
    white_noise = np.random.uniform(-1, 1, len(t))

    # Apply an envelope to both sine wave and white noise
    envelope = np.exp(-t * 10)

    # Combine the sine wave and white noise with their respective envelopes
    snare_wave = (sine_wave * envelope + white_noise * envelope) * volume

    # Normalize the wave to 16-bit PCM format
    audio_data = (snare_wave * 32767 / np.max(np.abs(snare_wave))).astype(
        np.int16
    )

    # Play the audio using the simpleaudio library
    play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)
    play_obj.wait_done()


def bass_drum(duration=0.5, frequency=60, volume=0.8):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate a sine wave with a decaying frequency
    sine_wave = np.sin(frequency * 2 * np.pi * t * np.exp(-t * 10))

    # Apply an envelope to simulate the bass drum sound
    envelope = np.exp(-t * 10)

    bass_drum_wave = sine_wave * envelope * volume

    # Normalize the wave to 16-bit PCM format
    audio_data = (
        bass_drum_wave * 32767 / np.max(np.abs(bass_drum_wave))
    ).astype(np.int16)

    # Play the audio using the simpleaudio library
    play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)
    play_obj.wait_done()


def hihat_closed(duration=0.1, volume=0.5):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate white noise
    white_noise = np.random.uniform(-1, 1, len(t))

    # Define a bandpass filter
    def bandpass_filter(data, low, high, sample_rate, order=5):
        nyquist = 0.5 * sample_rate
        low /= nyquist
        high /= nyquist
        b, a = butter(order, [low, high], btype="band")
        return lfilter(b, a, data)

    # Apply the bandpass filter to the white noise
    filtered_noise = bandpass_filter(white_noise, 4000, 8000, sample_rate)

    # Apply an envelope to the filtered noise
    envelope = np.exp(-t * 80)

    # Combine the filtered noise with the envelope
    hi_hat_wave = (filtered_noise * envelope) * volume

    # Normalize the wave to 16-bit PCM format
    audio_data = (hi_hat_wave * 32767 / np.max(np.abs(hi_hat_wave))).astype(
        np.int16
    )

    # Play the audio using the simpleaudio library
    play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)
    play_obj.wait_done()

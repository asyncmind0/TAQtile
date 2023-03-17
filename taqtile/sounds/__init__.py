import threading
import pygame
import numpy as np
import simpleaudio as sa
from pydub import AudioSegment, generators
from pydub.playback import play
import io
import numpy as np
import simpleaudio as sa
from scipy.signal import butter, lfilter
from libqtile.hook import subscribe
from taqtile.widgets.togglebtn import requires_toggle_button_active


def tick0(duration=0.01, volume=0.5):
    # Calculate the time values for the waveform
    time = np.linspace(0, duration, int(duration * 44100), False)

    # Generate a noise waveform with a high-frequency component
    noise = np.random.normal(0, 0.5, len(time))
    noise *= np.exp(-time * 20)
    noise *= np.sin(2 * np.pi * 9500 * time) ** 2

    # Scale the waveform by the volume and convert to an integer format
    waveform = (volume * noise * (2**15 - 1)).astype(np.int16)

    # Play the waveform using simpleaudio
    play_obj = sa.play_buffer(
        waveform, num_channels=1, bytes_per_sample=2, sample_rate=44100
    )


def metallic_click(duration=0.005, frequency=6500, volume=1):
    # Calculate the time values for the waveform
    time = np.linspace(0, duration, int(duration * 44100), False)

    # Generate a high-frequency sine wave
    waveform = np.sin(2 * np.pi * frequency * time)

    # Apply a decay envelope to the waveform
    envelope = np.exp(-10 * time)
    waveform *= envelope

    # Scale the waveform by the volume and convert to an integer format
    waveform = (volume * waveform * (2**15 - 1)).astype(np.int16)

    play_obj = sa.play_buffer(
        waveform, num_channels=1, bytes_per_sample=2, sample_rate=44100
    )


def thud(duration=0.5, frequency=300, volume=1):
    # Calculate the time values for the waveform
    time = np.linspace(0, duration, int(duration * 44100), False)

    # Generate a low-frequency sine wave
    waveform = np.sin(2 * np.pi * frequency * time)

    # Apply an envelope that simulates the impact of a blunt object hitting a surface
    envelope = np.exp(-time * 50) * np.sin(2 * np.pi * 10 * time) ** 2
    waveform *= envelope

    # Scale the waveform by the volume and convert to an integer format
    waveform = (volume * waveform * (2**15 - 1)).astype(np.int16)

    # Generate a low-frequency thud with a duration of 0.5 seconds and play it
    play_obj = sa.play_buffer(
        waveform, num_channels=1, bytes_per_sample=2, sample_rate=44100
    )


def tone(duration=1, frequency=440):
    sample_rate = 44100
    t = np.linspace(0, duration, sample_rate * duration, False)

    # Generate a sine wave
    sine_wave = np.sin(frequency * 2 * np.pi * t)

    # Apply a simple envelope to the sine wave to give it a sci-fi sound
    envelope = np.linspace(1, 0, len(sine_wave), False)
    sci_fi_wave = sine_wave * envelope

    # Normalize the wave to 16-bit PCM format
    audio_data = (sci_fi_wave * 32767 / np.max(np.abs(sci_fi_wave))).astype(
        np.int16
    )

    # Play the audio using the simpleaudio library
    play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)


def bong(duration=1, base_frequency=50, volume=0.5):
    if not 0 <= volume <= 1:
        raise ValueError("Volume must be a value between 0 and 1.")

    sample_rate = 44100
    t = np.linspace(0, duration, sample_rate * duration, False)

    # Generate multiple sine waves with varying frequencies and envelopes
    freq1 = base_frequency * 2
    freq2 = base_frequency * 4
    freq3 = base_frequency * 6

    sine_wave1 = np.sin(freq1 * 2 * np.pi * t)
    sine_wave2 = np.sin(freq2 * 2 * np.pi * t)
    sine_wave3 = np.sin(freq3 * 2 * np.pi * t)

    # Apply envelopes to each sine wave to create a whoosh sound
    envelope1 = np.exp(-t * 5)
    envelope2 = np.exp(-t * 10)
    envelope3 = np.exp(-t * 15)

    whoosh_wave1 = sine_wave1 * envelope1
    whoosh_wave2 = sine_wave2 * envelope2
    whoosh_wave3 = sine_wave3 * envelope3

    # Combine the sine waves
    combined_wave = whoosh_wave1 + whoosh_wave2 + whoosh_wave3

    # Adjust the volume by multiplying the combined wave with the volume parameter
    combined_wave = combined_wave * volume

    # Normalize the wave to 16-bit PCM format
    audio_data = (combined_wave * 32767 / np.max(np.abs(combined_wave))).astype(
        np.int16
    )

    # Play the audio using the simpleaudio library
    play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)


def tick():
    thud()
    # threading.Thread(target=thud, args=()).start()


def _context_switch_sound(duration=0.15, volume=0.3):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Generate multiple sine waves with different frequencies
    sine_wave1 = np.sin(800 * 2 * np.pi * t)
    sine_wave2 = np.sin(1200 * 2 * np.pi * t)

    # Apply different envelopes to the sine waves
    envelope1 = np.exp(-t * 20)
    envelope2 = np.exp(-t * 30)

    # Combine the sine waves with their envelopes
    textured_wave1 = sine_wave1 * envelope1
    textured_wave2 = sine_wave2 * envelope2

    # Combine the textured waves and apply the volume
    context_switch_wave = (textured_wave1 + textured_wave2) * volume

    # Normalize the wave to 16-bit PCM format
    audio_data = (
        context_switch_wave * 32767 / np.max(np.abs(context_switch_wave))
    ).astype(np.int16)

    # Play the audio using the simpleaudio library
    play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)


def context_switch_sound(duration=15, volume=-30):
    sample_rate = 48000

    # Generate multiple sine waves with different frequencies
    sine_wave1 = generators.Sine(800).to_audio_segment(duration=duration)
    sine_wave1 = sine_wave1.set_sample_width(2)
    sine_wave2 = generators.Sine(1200).to_audio_segment(duration=duration)
    sine_wave2 = sine_wave2.set_sample_width(2)

    # Apply different envelopes to the sine waves
    envelope1 = (
        AudioSegment.silent(duration=duration)
        .fade_in(duration)
        .fade_out(duration // 2)
    )
    envelope2 = (
        AudioSegment.silent(duration=duration)
        .fade_in(duration)
        .fade_out(duration // 3)
    )

    # Combine the sine waves with their envelopes
    textured_wave1 = sine_wave1.overlay(envelope1)
    textured_wave2 = sine_wave2.overlay(envelope2)

    # Combine the textured waves and apply the volume
    context_switch_wave = (textured_wave1 + textured_wave2).apply_gain(volume)

    # Play the audio using the pydub library
    play(context_switch_wave)


def play_sound(filename):
    # Create a new thread and start playing the sound
    sound_thread = threading.Thread(target=_play_sound, args=(filename,))
    sound_thread.start()

    # Do other tasks while the sound is playing
    print("Sound playing in the background...")


def _play_sound(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()


@requires_toggle_button_active("sound_effects")
@subscribe.setgroup
def setgroup():
    # sounds.context_switch_sound()
    from taqtile.sounds import drums

    drums.snare_drum()


@requires_toggle_button_active("sound_effects")
@subscribe.client_focus
def client_focused(window):
    from taqtile.sounds import drums

    drums.hihat_closed()


@requires_toggle_button_active("sound_effects")
@subscribe.client_killed
def client_killed(window):
    from taqtile.sounds import drums

    drums.hihat_open1()


@requires_toggle_button_active("sound_effects")
@subscribe.current_screen_change
def screen_change():
    from taqtile.sounds import drums

    drums.bass_drum()


@requires_toggle_button_active("sound_effects")
@subscribe.client_managed
def set_group(client):
    from taqtile.sounds import drums

    drums.hihat_open0()

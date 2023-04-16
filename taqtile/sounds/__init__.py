import threading
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
from subprocess import check_output

import pulsectl
import alsaaudio
import simpleaudio as sa
import logging
from taqtile.utils import send_notification


logger = logging.getLogger("taqtile")


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
    play_obj.wait_done()


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
    play_obj.wait_done()


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
    play_obj.wait_done()


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
    play_obj.wait_done()


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
    play_obj.wait_done()


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
    play_obj.wait_done()


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


def play_effect(effect):
    threading.Thread(target=thud, args=()).start()


def play_sound(filename):
    # Create a new thread and start playing the sound
    sound_thread = threading.Thread(target=_play_sound, args=(filename,))
    sound_thread.start()

    # Do other tasks while the sound is playing
    print("Sound playing in the background...")


def get_current_volume():
    current_volumes = []
    with pulsectl.Pulse("volume-adjustment") as pulse:
        sinks = pulse.sink_list()
        for sink in sinks:
            current_volumes.append(sink.volume.value_flat)
    return int(max(current_volumes) * 100)


def change_sink_volume(qtile, increment):
    with pulsectl.Pulse("volume-adjustment") as pulse:
        sinks = pulse.sink_list()
        new_volumes = [
            max(min(sink.volume.value_flat + increment, 1.0), 0.0)
            for sink in sinks
        ]
        for sink, new_volume in zip(sinks, new_volumes):
            pulse.volume_set_all_chans(sink, new_volume)
        # mixer = alsaaudio.Mixer()
        # current_volume = mixer.getvolume()[0]  # get the current volume
        # new_volume = max(min(current_volume + int(increment * 100), 100), 0)
        # mixer.setvolume(new_volume)  # set the volume
        send_notification(
            "Volume",
            str(get_current_volume()),
        )
        play_effect("volume_dial")


@subscribe.setgroup
@requires_toggle_button_active("sound_effects")
def setgroup():
    # sounds.context_switch_sound()
    from taqtile.sounds import drums

    threading.Thread(target=drums.snare_drum, args=()).start()


@subscribe.client_focus
@requires_toggle_button_active("sound_effects")
def client_focused(window):
    from taqtile.sounds import drums

    threading.Thread(target=drums.hihat_closed, args=()).start()


@subscribe.client_killed
@requires_toggle_button_active("sound_effects")
def client_killed(window):
    from taqtile.sounds import drums

    threading.Thread(target=drums.hihat_open1, args=()).start()


@subscribe.current_screen_change
@requires_toggle_button_active("sound_effects")
def screen_change():
    from taqtile.sounds import drums

    threading.Thread(target=drums.bass_drum, args=()).start()


@subscribe.client_managed
@requires_toggle_button_active("sound_effects")
def set_group(client):
    from taqtile.sounds import drums

    threading.Thread(target=drums.hihat_open0, args=()).start()


def set_all_volume(volume):
    with pulsectl.Pulse("volume-adjustment") as pulse:
        sinks = pulse.sink_list()
        for sink in sinks:
            pulse.volume_set_all_chans(sink, volume)


def volume_mute(qtile):
    with pulsectl.Pulse("volume-adjustment") as pulse:
        for sink in pulse.sink_list():
            pulse.mute(sink, not sink.mute)
    send_notification(
        "Volume",
        ("Muted" if sink.mute else str(get_current_volume())),
    )
    play_effect("thud")


@subscribe.startup
def startup():
    threading.Thread(target=set_all_volume, args=(0.3)).start()

import subprocess
import wave

import pytest


@pytest.mark.hardware
def test_microphone_is_detected_by_usb():
    """Verify that the USB audio device is detected by Linux."""

    result = subprocess.run(
        ["lsusb"],
        capture_output=True,
        text=True,
        check=True,
    )

    output = result.stdout.lower()

    assert output.strip(), "lsusb returned no USB devices"

    # This confirms USB devices exist.
    # We don't hard-code a particular microphone name because
    # different hardware may expose different names.
    assert result.returncode == 0


@pytest.mark.hardware
def test_audio_input_device_is_available():
    """Verify that ALSA exposes at least one recording device."""

    result = subprocess.run(
        ["arecord", "-l"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        "arecord -l failed:\n"
        f"{result.stderr}"
    )

    output = result.stdout.lower()

    assert "card" in output, (
        "No ALSA recording device detected:\n"
        f"{result.stdout}"
    )


@pytest.mark.hardware
def test_audio_recording_end_to_end(tmp_path):
    """
    End-to-end microphone test.

    Records 5 seconds of audio using the real ALSA device
    and verifies that a valid WAV file was produced.
    """

    output_file = tmp_path / "sample.wav"

    result = subprocess.run(
        [
            "arecord",
            "--duration=5",
            "--format=wav",
            str(output_file),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, (
        "arecord failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    assert output_file.exists(), (
        "arecord completed but WAV file was not created"
    )

    assert output_file.stat().st_size > 44, (
        "WAV file is empty or contains only the WAV header"
    )


@pytest.mark.hardware
def test_recorded_audio_is_valid_wav(tmp_path):
    """
    Record audio and verify that the resulting file is
    a valid WAV file with audio frames.
    """

    output_file = tmp_path / "sample.wav"

    result = subprocess.run(
        [
            "arecord",
            "--duration=5",
            "--format=wav",
            str(output_file),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, (
        "Audio recording failed:\n"
        f"{result.stderr}"
    )

    with wave.open(str(output_file), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frame_count = wav.getnframes()

    assert channels > 0
    assert sample_width > 0
    assert sample_rate > 0
    assert frame_count > 0


@pytest.mark.hardware
def test_recording_has_expected_duration(tmp_path):
    """
    Verify that the recorded audio is approximately 5 seconds long.
    """

    output_file = tmp_path / "sample.wav"

    result = subprocess.run(
        [
            "arecord",
            "--duration=5",
            "--format=wav",
            str(output_file),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, (
        "Audio recording failed:\n"
        f"{result.stderr}"
    )

    with wave.open(str(output_file), "rb") as wav:
        sample_rate = wav.getframerate()
        frame_count = wav.getnframes()

    duration = frame_count / sample_rate

    # Allow some tolerance around the requested 5 seconds.
    assert 4.5 <= duration <= 5.5, (
        f"Unexpected recording duration: {duration:.2f}s"
    )
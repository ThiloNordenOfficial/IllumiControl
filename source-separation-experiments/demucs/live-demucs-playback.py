import logging
import os
import time
import numpy as np
import pyaudio
from demucs_infer.pretrained import get_model
from demucs_infer.apply import apply_model
from demucs_infer.audio import save_audio
import torch
import torchaudio


class LiveDemucsAnalyzer:
    """
    Real-time audio source separation with live playback of a stem (e.g., vocals).
    Uses PyAudio for input and output — no sounddevice, no PortAudio time field issues.
    """

    def __init__(
        self,
        model_name: str,
        target_sample_rate: int,
        chunk_size: int,
        channels: int,
        device: str = None,
        input_device_index: int = None,
        output_device_index: int = None,
        output_stem: str = "vocals",  # Which stem to play back
        output_dir: str = "live_output",
        log_level: int = logging.INFO,
    ):
        self.model_name = model_name
        self.target_sample_rate = target_sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.input_device_index = input_device_index
        self.output_device_index = output_device_index
        self.output_stem = output_stem
        self.output_dir = output_dir
        self.log_level = log_level

        # Set device
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cuda" and not torch.cuda.is_available():
            logging.warning("CUDA not available. Falling back to CPU.")
            self.device = "cpu"

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Set up logging
        logging.basicConfig(level=self.log_level)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"LiveDemucsAnalyzer initialized on {self.device}")

        # Initialize model
        self.model = None
        self.resampler = None
        self._load_model()

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Output stream (for playback)
        self.output_stream = None

    def _load_model(self):
        """Load the Demucs model."""
        try:
            self.model = get_model(self.model_name)
            self.model.eval()
            self.logger.info(f"Model '{self.model_name}' loaded successfully.")
        except Exception as e:
            self.logger.critical(f"Failed to load model '{self.model_name}': {e}")
            raise

    def _detect_input_device(self):
        """Detect available input devices."""
        devices = []
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append((i, info['name'], info['defaultSampleRate']))
        if not devices:
            raise RuntimeError("No input devices found!")
        return devices

    def _detect_output_device(self):
        """Detect available output devices."""
        devices = []
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:
                devices.append((i, info['name'], info['defaultSampleRate']))
        if not devices:
            raise RuntimeError("No output devices found!")
        return devices

    def _resample_if_needed(self, audio: np.ndarray, input_sample_rate: float) -> np.ndarray:
        """Resample audio to target sample rate if needed."""
        if input_sample_rate == self.target_sample_rate:
            return audio

        if self.resampler is None:
            self.resampler = torchaudio.transforms.Resample(
                orig_freq=int(input_sample_rate),
                new_freq=self.target_sample_rate
            )

        audio_tensor = torch.tensor(audio).unsqueeze(0)  # [1, T]
        audio_tensor = self.resampler(audio_tensor)
        audio = audio_tensor.squeeze().numpy()

        self.logger.info(f"Resampled from {input_sample_rate} Hz to {self.target_sample_rate} Hz")
        return audio

    def _playback_callback(self, in_data, frame_count, time_info, status):
        """Callback to play back a stem (e.g., vocals)."""
        # This is just a placeholder — we'll handle playback in the main callback
        return None, pyaudio.paContinue

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """
        Main audio callback: process input, separate, save stems, and play back a stem.
        """
        if status:
            self.logger.warning(f"Audio status: {status}")

        # Convert to float32 and mono
        audio = np.frombuffer(in_data, dtype=np.float32)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)  # Convert to mono
        audio = audio.astype(np.float32)

        # Get input sample rate
        input_sample_rate = self.target_sample_rate  # Default fallback

        # In real use, get from device info
        # For now, assume it's known
        # You can pass it from device detection

        # Resample if needed
        audio = self._resample_if_needed(audio, input_sample_rate)

        # Convert to tensor: [1, 1, T]
        wav = torch.tensor(audio).unsqueeze(0).unsqueeze(0)  # [1, 1, T]

        # 🔥 Fix: If model expects 2 channels, duplicate mono to stereo
        if self.model.audio_channels == 2 and wav.shape[1] == 1:
            wav = wav.repeat(1, 2, 1)
            self.logger.info("Duplicated mono to stereo for model compatibility.")

        # Move to device
        wav = wav.to(self.device)

        # Run separation
        start_time = time.time()
        with torch.no_grad():
            sources = apply_model(self.model, wav, device=self.device)
        elapsed = time.time() - start_time
        self.logger.info(f"Processing time: {elapsed:.2f}s")

        # Save all stems
        timestamp = int(time.time())
        for i, source_name in enumerate(self.model.sources):
            source = sources[0, i].cpu()
            save_audio(source, f"{self.output_dir}/{source_name}_{timestamp}.wav", self.target_sample_rate)
            self.logger.info(f"Saved {source_name}.wav")

        # 🔊 Play back a specific stem (e.g., vocals)
        try:
            stem_idx = self.model.sources.index(self.output_stem)
            stem = sources[0, stem_idx].cpu().numpy()

            # Normalize to avoid clipping
            max_val = np.max(np.abs(stem))
            if max_val > 0:
                stem = stem / max_val * 0.8  # Reduce volume

            # Convert to bytes and play
            if self.output_stream is None:
                # Open output stream on first use
                self.output_stream = self.p.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=self.target_sample_rate,
                    output=True,
                    output_device_index=self.output_device_index,
                    frames_per_buffer=self.chunk_size
                )

            # Write to output stream
            self.output_stream.write(stem.astype(np.float32).tobytes())

        except Exception as e:
            self.logger.warning(f"Failed to play back {self.output_stem}: {e}")

        # Return (data, pyaudio.paContinue)
        return None, pyaudio.paContinue

    def start(self):
        """Start live audio processing with real-time playback."""
        self.logger.info("Starting live audio processing with real-time playback... Press Ctrl+C to stop.")
        try:
            # Detect input devices
            devices = self._detect_input_device()
            self.logger.info("Available input devices:")
            for i, name, rate in devices:
                self.logger.info(f"  {i}: {name} (Sample rate: {rate} Hz)")

            # Use specified device or first available
            device_idx = self.input_device_index if self.input_device_index is not None else devices[0][0]
            device_info = self.p.get_device_info_by_index(device_idx)
            input_sample_rate = device_info['defaultSampleRate']

            self.logger.info(f"Using input device: {device_info['name']} (Sample rate: {input_sample_rate} Hz)")

            # Detect output devices
            output_devices = self._detect_output_device()
            self.logger.info("Available output devices:")
            for i, name, rate in output_devices:
                self.logger.info(f"  {i}: {name} (Sample rate: {rate} Hz)")

            # Use specified output device or first available
            output_idx = self.output_device_index if self.output_device_index is not None else output_devices[0][0]
            output_info = self.p.get_device_info_by_index(output_idx)
            self.logger.info(f"Using output device: {output_info['name']} (Sample rate: {output_info['defaultSampleRate']} Hz)")

            # Open input stream
            stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=int(input_sample_rate),
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback,
                input_device_index=device_idx
            )

            # Start stream
            stream.start_stream()
            self.logger.info("Listening and playing back stem... Press Ctrl+C to stop.")

            # Keep stream alive
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Stopping...")
        except Exception as e:
            self.logger.critical(f"Stream error: {e}")
            raise
        finally:
            # Close streams and terminate PyAudio
            if hasattr(self, 'p') and self.p:
                if self.output_stream:
                    self.output_stream.stop_stream()
                    self.output_stream.close()
                stream.stop_stream()
                stream.close()
                self.p.terminate()
            self.logger.info("LiveDemucsAnalyzer stopped.")

    def stop(self):
        """Stop the analyzer."""
        self.logger.info("Stopping analyzer...")
        # Handled in `start()` via KeyboardInterrupt
        pass


# 🚀 Example Usage
if __name__ == "__main__":
    analyzer = LiveDemucsAnalyzer(
        model_name="mdx_extra_q",
        target_sample_rate=44100,
        chunk_size=44100,
        channels=1,
        device="cuda",
        input_device_index=21,  # Auto-detect
        output_device_index=21,  # Auto-detect
        output_stem="vocals",  # Which stem to play back
        output_dir="live_output",
        log_level=logging.INFO
    )
    analyzer.start()
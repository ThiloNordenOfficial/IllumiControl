import os
import time
import numpy as np
import torch
import soundfile as sf
# Prefer package imports when available; when running the script directly, adjust sys.path so local modules can be imported.
import sys
from pathlib import Path
from scnetlib.scnet.SCNet import SCNet
from scnetlib.scnet.utils import load_model, convert_audio
from scnetlib.scnet.apply import apply_model
from ml_collections import ConfigDict
import argparse
import yaml

# New imports for live mode
import threading
import queue
from datetime import datetime, timezone


class Seperator:
    def __init__(self, model, checkpoint_path):
        self.separator = load_model(model, checkpoint_path)

        if torch.cuda.device_count():
            self.device = torch.device('cuda')
        else:
            print("WARNING, using CPU")
            self.device = torch.device('cpu')
        self.separator.to(self.device)

    @property
    def instruments(self):
        return ['bass', 'drums', 'other', 'vocals']

    def raise_aicrowd_error(self, msg):
        raise NameError(msg)

    def separate_music_file(self, mixed_sound_array, sample_rate):
        """
        Implements the sound separation for a single sound file
        Inputs: Outputs from soundfile.read('mixture.wav')
            mixed_sound_array
            sample_rate
        Outputs:
            separated_music_arrays: Dictionary numpy array of each separated instrument
            output_sample_rates: Dictionary of sample rates separated sequence
        """
        # Convert audio to tensor and handle shape properly
        mix = torch.from_numpy(np.asarray(mixed_sound_array.T, np.float32))

        # Check shape and dimensions
        print(f"Input audio shape before processing: {mix.shape}")

        # Store original number of channels for output conversion
        original_channels = 1 if mix.ndim == 1 else mix.shape[0]
        print(f"Original audio has {original_channels} channel(s)")

        # Move to GPU
        mix = mix.to(self.device)

        # Convert to model's expected format
        mix = convert_audio(mix, sample_rate, 44100, self.separator.audio_channels)

        b = time.time()
        mono = mix.mean(0)
        mean = mono.mean()
        std = mono.std()
        mix = (mix - mean) / std
        # Separate
        with torch.no_grad():
            estimates = apply_model(self.separator, mix[None], overlap=0.5, progress=False)[0]

        # Printing some sanity checks.
        print(time.time() - b, mono.shape[-1] / sample_rate, mix.std(), estimates.std())

        estimates = estimates * std + mean

        print(f"Model output shape before conversion: {estimates.shape}")
        # Convert back to original sample rate and channel count
        estimates = convert_audio(estimates, 44100, sample_rate, original_channels)

        separated_music_arrays = {}
        output_sample_rates = {}
        for instrument in self.instruments:
            idx = self.separator.sources.index(instrument)
            separated_music_arrays[instrument] = torch.squeeze(estimates[idx]).detach().cpu().numpy().T
            output_sample_rates[instrument] = sample_rate

        return separated_music_arrays, output_sample_rates


    def load_audio(self, file_path):
        try:
            data, sample_rate = sf.read(file_path, dtype='float32')
            return data, sample_rate
        except Exception as e:
            print(f"Error loading audio file {file_path}: {e}")
            raise

    def save_sources(self, sources, output_sample_rates, save_dir):
        os.makedirs(save_dir, exist_ok=True)
        for name, src in sources.items():
            save_path = os.path.join(save_dir, f'{name}.wav')
            sf.write(save_path, src, output_sample_rates[name])
            print(f"Saved {name} to {save_path}")

    def process_directory(self, input_dir, output_dir):
        for entry in os.listdir(input_dir):
            entry_path = os.path.join(input_dir, entry)
            if os.path.isdir(entry_path):
                mixture_path = os.path.join(entry_path, 'mixture.wav')
                if os.path.isfile(mixture_path):
                    print(f"Processing {mixture_path}")
                    entry_name = os.path.basename(entry)
                else:
                    continue
            elif os.path.isfile(entry_path) and entry_path.lower().endswith('.wav'):
                print(f"Processing {entry_path}")
                mixture_path = entry_path
                entry_name = os.path.splitext(os.path.basename(entry))[0]
            else:
                continue

            mixed_sound_array, sample_rate = self.load_audio(mixture_path)
            separated_music_arrays, output_sample_rates = self.separate_music_file(mixed_sound_array, sample_rate)
            save_dir = os.path.join(output_dir, entry_name)
            self.save_sources(separated_music_arrays, output_sample_rates, save_dir)


# New helper: live streaming processing
def run_live(seperator: Seperator, out_dir: str, samplerate: int = 44100, channels: int = 2, segment: float = 8.0, hop: float = None, input_device=None):
    """
    Run live microphone separation. Buffers audio into `segment` seconds and advances by `hop` seconds.
    Saves each separated output into a timestamped subdirectory under out_dir.
    """
    try:
        import sounddevice as sd
    except Exception:
        print("Live mode requires the `sounddevice` package. Install it with `pip install sounddevice`.")
        return

    if hop is None:
        hop = segment / 2.0  # 50% overlap default

    q = queue.Queue()
    stop_event = threading.Event()

    def callback(indata, frames, time_info, status):
        # indata shape: (frames, channels)
        if status:
            print(f"Input stream status: {status}")
        q.put(indata.copy())

    stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback, device=input_device, dtype='float32')

    def consumer():
        buffer_chunks = []
        total_samples = 0
        target_samples = int(segment * samplerate)
        hop_samples = int(hop * samplerate)

        while not stop_event.is_set():
            try:
                chunk = q.get(timeout=1.0)
            except queue.Empty:
                continue
            # chunk shape: (frames, channels)
            buffer_chunks.append(chunk)
            total_samples += chunk.shape[0]

            if total_samples >= target_samples:
                # concatenate earliest samples into a contiguous buffer
                buf = np.concatenate(buffer_chunks, axis=0)
                # take exactly target_samples from start
                buf_to_process = buf[:target_samples]

                try:
                    separated, out_rates = seperator.separate_music_file(buf_to_process, samplerate)
                except Exception as e:
                    print(f"Error during separation: {e}")
                    # slide buffer forward and continue
                    # drop hop_samples from the front
                    remaining = buf[hop_samples:]
                    buffer_chunks = [remaining]
                    total_samples = remaining.shape[0]
                    continue

                # Save only the part that will NOT be covered again by the next overlapping chunk.
                # We keep processing on full `segment` for better model context, but write only the first `hop_samples`.
                to_save = {}
                for name, arr in separated.items():
                    # arr shape: (samples, channels) as returned by separate_music_file
                    save_len = min(hop_samples, arr.shape[0])
                    to_save[name] = arr[:save_len]

                timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
                save_dir = os.path.join(out_dir, f'live_{timestamp}')
                seperator.save_sources(to_save, {k: out_rates[k] for k in to_save.keys()}, save_dir)

                # advance buffer by hop_samples
                remaining = buf[hop_samples:]
                # reset buffer_chunks to the remaining part
                buffer_chunks = [remaining] if remaining.shape[0] > 0 else []
                total_samples = remaining.shape[0]

        # Loop exited: flush remaining audio (if any) so no audio is left unsaved.
        try:
            if buffer_chunks:
                buf = np.concatenate(buffer_chunks, axis=0)
                if buf.shape[0] > 0:
                    try:
                        separated, out_rates = seperator.separate_music_file(buf, samplerate)
                        # Save the whole remaining buffer (it won't be duplicated)
                        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
                        save_dir = os.path.join(out_dir, f'live_flush_{timestamp}')
                        seperator.save_sources(separated, out_rates, save_dir)
                    except Exception as e:
                        print(f"Error during final flush separation: {e}")
        except Exception:
            pass

    consumer_thread = threading.Thread(target=consumer, daemon=True)

    try:
        stream.start()
        print(f"Started input stream (samplerate={samplerate}, channels={channels}). Press Ctrl+C to stop.")
        consumer_thread.start()
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping live inference...")
    finally:
        stop_event.set()
        stream.stop()
        stream.close()
        consumer_thread.join(timeout=2.0)
        print("Live inference stopped.")


def parse_args():
    parser = argparse.ArgumentParser(description="Music Source Separation using SCNet")
    parser.add_argument('--input_dir', type=str, help='Input directory containing audio files')
    parser.add_argument('--output_dir', type=str, help='Output directory to save separated sources')
    parser.add_argument('--config_path', type=str, default='./scnetlib/conf/config.yaml', help='Path to configuration file')
    parser.add_argument('--checkpoint_path', type=str, default='./scnetlib/result/checkpoint.th', help='Path to model checkpoint file')

    # Live mode flags
    parser.add_argument('--live', action='store_true', help='Run in live (microphone) mode')
    parser.add_argument('--samplerate', type=int, default=44100, help='Samplerate for live input')
    parser.add_argument('--channels', type=int, default=2, help='Number of input channels for live mode')
    parser.add_argument('--segment', type=float, default=8.0, help='Segment length in seconds to buffer before separation')
    parser.add_argument('--hop', type=float, default=None, help='Hop length in seconds to advance buffer (defaults to 50% overlap)')
    parser.add_argument('--device', type=int, default=None, help='Input audio device ID for sounddevice (live mode)')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    with open(args.config_path, 'r') as file:
          config = ConfigDict(yaml.load(file, Loader=yaml.FullLoader))

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    model = SCNet(**config.model)
    model.eval()
    seperator = Seperator(model, args.checkpoint_path)

    if args.live:
        run_live(seperator, args.output_dir, samplerate=args.samplerate, channels=args.channels, segment=args.segment, hop=args.hop, input_device=args.device)
    else:
        if not args.input_dir:
            print("Please provide --input_dir for file mode or use --live for microphone mode.")
        else:
            seperator.process_directory(args.input_dir, args.output_dir)

import logging
import os.path

from demucs_infer.pretrained import get_model
from demucs_infer.apply import apply_model
from demucs_infer.audio import save_audio
import torch
import torchaudio
import time


def separate(path: str):
    output_path = output_dir + audio_path
    os.makedirs(output_path, exist_ok=True)

    wav, sr = torchaudio.load(path)
    wav = wav.unsqueeze(0)  # Add batch dimension
    start_time = time.time()
    with torch.no_grad():
        stems = apply_model(model, wav, device="cuda")
    end_time = time.time()
    print(f"{os.path.basename(path)}, {end_time - start_time}")

    filehandle = open(f'{output_path}/times.txt', 'a')
    filehandle.write(f'{end_time - start_time}\n')
    filehandle.flush()
    filehandle.close()

    for i, source_name in enumerate(model.sources):
        source = stems[0, i]  # Remove batch dimension
        save_audio(source, f"{output_path}/{source_name}.wav", sr)


if __name__ == '__main__':
    input_dir = '../input/'
    output_dir = '../output/demucs-mdx-q/'
    file_type = '.wav'

    model = get_model("mdx_q")
    # model = get_model("htdemucs")
    model.eval()

    for audio_path in os.listdir(input_dir):
        if audio_path.endswith(file_type):
            for i in range(50):
                separate(input_dir+audio_path)


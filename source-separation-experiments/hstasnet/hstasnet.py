import os
import time

import soundfile
import torch
import torchaudio
from hs_tasnet import HSTasNet


def separate(path: str):
    output_path = output_dir + audio_path
    os.makedirs(output_path, exist_ok=True)

    wav, sr = torchaudio.load(path)
    wav = wav.unsqueeze(0)
    audio = wav.to('cuda')

    start_time = time.time()
    stems, _ = model(audio)
    end_time = time.time()
    print(f"{os.path.basename(path)}, {end_time - start_time}")

    for i in range(model.num_sources):
        source = stems[0, i].cpu()
        torchaudio.save(f'{output_path}/{i}.wav', source, model.sample_rate)

    filehandle = open(f'{output_path}/times.txt', 'a')
    filehandle.write(f'{end_time - start_time}\n')
    filehandle.close()


if __name__ == '__main__':
    input_dir = '../input/'
    output_dir = '../output/hstasnet-small/'
    file_type = '.wav'

    os.makedirs(output_dir, exist_ok=True)

    model = HSTasNet(small=True).to('cuda')

    for audio_path in os.listdir(input_dir):
        if audio_path.endswith(file_type):
            for i in range(50):
                separate(input_dir + audio_path)

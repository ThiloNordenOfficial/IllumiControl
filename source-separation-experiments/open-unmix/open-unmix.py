import os.path
import time
from os.path import isfile

import torch
import torchaudio



def separate(path: str):
    output_path = output_dir + audio_path
    os.makedirs(output_path, exist_ok=True)
    try:
        wav, sr = torchaudio.load(path)
        wav = wav.unsqueeze(0)
        if separator.sample_rate != sr:
            resampler = torchaudio.transforms.Resample(sr, separator.sample_rate)
            wav = resampler(wav)
        audio = wav.to(device)
        start_time = time.time()
        stems = separator(audio)
        end_time = time.time()
        print(f"{os.path.basename(path)}, {time.time() - start_time}")


        filehandle = open(f'{output_path}/times.txt', 'a')
        filehandle.write(f'{end_time-start_time}\n')
        filehandle.close()

        for i, name in enumerate(separator.target_models):
            source = stems[0, i].cpu()
            torchaudio.save(f'{output_path}/{name}.wav',source,separator.sample_rate)
    except torch.OutOfMemoryError as e:
        filehandle = open(f'{output_path}/error.txt','wt')
        filehandle.write(f'{str(e)}\n')
        filehandle.flush()
        filehandle.close()


if __name__ == '__main__':
    input_dir = '../input/'
    output_dir = '../output/open-unmix-umxhq/'
    file_type = '.wav'

    device = 'cuda'
    separator = torch.hub.load('sigsep/open-unmix-pytorch', 'umxhq').to(device)

    for audio_path in os.listdir(input_dir):
        if audio_path.endswith(file_type):
            for i in range(50):
                separate(input_dir+audio_path)




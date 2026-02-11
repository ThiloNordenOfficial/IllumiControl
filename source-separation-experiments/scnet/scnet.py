import os
import time

import soundfile
import yaml
from ml_collections import ConfigDict

from scnetlib.scnet.SCNet import SCNet
from scnetlib.scnet.inference import Seperator as sep


def separate(path: str):
    output_path = output_dir + audio_path
    os.makedirs(output_path, exist_ok=True)

    wav, sr = soundfile.read(path)
    start_time = time.time()
    stems, osr = separator.separate_music_file(wav, sr)
    end_time = time.time()
    print(f"{os.path.basename(path)}, {end_time - start_time}")

    filehandle = open(f'{output_path}/times.txt', 'a')
    filehandle.write(f'{end_time - start_time}\n')
    filehandle.close()

    sep.save_sources(separator, stems, osr, output_path)


if __name__ == '__main__':
    input_dir = '../input/'
    output_dir = '../output/scnet-large/'
    file_type = '.wav'

    config_path = 'scnetlib/conf/config.yaml'
    checkpoint_path = 'scnetlib/checkpoints/SCNet-large.th'

    with open(config_path, 'r') as file:
        config = ConfigDict(yaml.load(file, Loader=yaml.FullLoader))

    os.makedirs(output_dir, exist_ok=True)

    model = SCNet(**config.model)
    model.eval()
    separator = sep(model, checkpoint_path)

    for audio_path in os.listdir(input_dir):
        if audio_path.endswith(file_type):
            for i in range(50):
                separate(input_dir + audio_path)

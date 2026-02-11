import os
import time

import soundfile
from spleeter.separator import Separator

def separate(path: str):
    output_path = output_dir + audio_path
    os.makedirs(output_path, exist_ok=True)

    wav, _ = soundfile.read(path, dtype='float32')
    start_time = time.time()
    stems = separator.separate(wav)
    end_time = time.time()
    print(f"{os.path.basename(path)}, {end_time - start_time}")

    filehandle = open(f'{output_path}/times.txt', 'a')
    filehandle.write(f'{end_time - start_time}\n')
    filehandle.flush()
    filehandle.close()

    separator.save_to_file(stems, path, output_path)

if __name__ == '__main__':
    input_dir = '../input/'
    output_dir = '../output/spleeter/'
    file_type = '.wav'

    separator = Separator('spleeter:4stems')

    for audio_path in os.listdir(input_dir):
        if audio_path.endswith(file_type):
            for i in range(50):
                separate(input_dir+audio_path)


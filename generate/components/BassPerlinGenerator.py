import argparse

import numpy as np
import noise

from generate import GeneratorBase
from shared import CommandLineArgumentAdder
from shared.shared_memory import SmSender, NumpyArrayReceiver, NumpyArraySender
from PIL import Image


class BassPerlinGenerator(GeneratorBase, CommandLineArgumentAdder):

    def __init__(self, data_senders):
        GeneratorBase.__init__(self, data_senders)
        self.vocal_loudness_receiver = NumpyArrayReceiver(data_senders.get("stem_loudness_bass"))
        CommandLineArgumentAdder.__init__(self)
        self.height = 250
        self.width = 250
        self.rgb_image = NumpyArraySender((self.width, self.height, 3))
        self.outbound_data_senders = {
            "bass_rgb_image": self.rgb_image
        }
        self.movement_speed = 0.7

        self.x_offset, self.y_offset = 0, 0
        self.n = 1

    def delete(self):
        pass

    async def run_procedure(self):
        loudness = self.vocal_loudness_receiver.read_on_update()[0]
        loudness_scale = loudness if loudness > 10 else 0
        scale = 250
        self.x_offset = self.x_offset + self.movement_speed * 3 + (self.movement_speed * loudness_scale * 7)
        self.y_offset = self.y_offset + self.movement_speed * 3 + (self.movement_speed * loudness_scale * 7)

        red_noise = np.zeros((self.height, self.width))
        green_noise = np.zeros((self.height, self.width))
        blue_noise = np.zeros((self.height, self.width))

        for y in range(self.height):
            for x in range(self.width):
                red_noise[y][x] = noise.snoise2(
                    (x + self.x_offset) / scale * 0.1,
                    (y + self.y_offset) / scale * 0.2,
                    octaves=1,
                )
                green_noise[y][x] = noise.snoise2(
                    (x + self.x_offset) / scale * 0.3,
                    (y + self.y_offset) / scale * 0.4,
                    octaves=2
                )
                blue_noise[y][x] = noise.snoise2(
                    (x + self.x_offset) / scale * 0.5,
                    (y + self.y_offset) / scale * 0.6,
                    octaves=3
                )

        red_noise = ((red_noise + 1) / 2) * 255
        green_noise = ((green_noise + 1) / 2) * 255
        blue_noise = ((blue_noise + 1) / 2) * 255

        red_noise = red_noise.astype(np.uint8)
        green_noise = green_noise.astype(np.uint8)
        blue_noise = blue_noise.astype(np.uint8)

        rgb_array = np.stack([red_noise, green_noise, blue_noise], axis=-1)
        self.rgb_image.update(rgb_array)
        # img = Image.fromarray(rgb_array, 'RGB')
        # img.save(f"simplex-noise/bass/{self.n}.png")
        # self.n = self.n + 1

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.outbound_data_senders

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        # parser.add_argument("--max-loudness", dest='max_loudness', type=float)
        pass

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        pass

from numpy.random import default_rng
import pickle

if __name__ == "__main__":
    # generate a random 3D array containing 3 color channels
    image = default_rng(1).integers(0, 256, size=(3, 3, 3))
    # noinspection PyTypeChecker
    pickle.dump(image, open("../image.pickle", "wb"))
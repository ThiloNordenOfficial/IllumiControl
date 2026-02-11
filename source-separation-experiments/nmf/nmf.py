import numpy as np
from sklearn.decomposition import NMF

X = np.array([[1, 1], [2, 1], [3, 1.2], [4, 1], [5, 0.8], [6, 1]])

model = NMF(n_components=2, init='random', random_state=0)

W = model.fit_transform(X)

H = model.components_

if __name__ == '__main__':
    print("Original Matrix X:")
    print(X)
    print("\nBasis Matrix W:")
    print(W)
    print("\nCoefficient Matrix H:")
    print(H)
    print("\nReconstructed Matrix (W @ H):")
    print(np.dot(W, H))
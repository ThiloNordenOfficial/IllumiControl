import numpy as np
import torch

# Install confirmation (optional, but helpful)
try:
    import torchvision
    import transformers

    print("All dependencies installed successfully!")
except ImportError as e:
    print(f"Missing dependency: {e}")

# Check device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")


# Reproducibility
def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)


if __name__ == "__main__":
    set_seed(42)

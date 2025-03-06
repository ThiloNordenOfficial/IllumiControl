from torchvision import datasets, transforms
from torch.utils.data import DataLoader


def preprocess_and_augmentation():
    # Define transformations
    transform = transforms.Compose([
        transforms.Resize((64, 64)),  # Resize images to 64x64
        transforms.ToTensor(),  # Convert to tensor
        transforms.Normalize((0.5,), (0.5,)),  # Normalize to [-1, 1]
    ])

    # Load dataset
    dataset = datasets.CelebA(root="./data", split="train", transform=transform, download=True)

    # Create DataLoader
    batch_size = 32
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    print(f"Number of batches: {len(dataloader)}")

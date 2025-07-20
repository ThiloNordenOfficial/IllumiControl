import numpy as np
import torch
import torch.optim as optim
from matplotlib import pyplot as plt
from torch import nn
from torchvision.utils import save_image

from generate.stable_diffusion.UNet import UNet
from generate.stable_diffusion.forward_diffusion_process import forward_diffusion_process
from generate.stable_diffusion.linear_beta_schedule import linear_beta_schedule
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Save generated samples
def save_samples(model, epoch, dataloader, device):
    model.eval()
    with torch.no_grad():
        for batch_idx, (images, _) in enumerate(dataloader):
            images = images.to(device)
            t = torch.randint(0, timesteps, (images.size(0),)).to(device)
            noisy_images = forward_diffusion_process(images, t, beta_schedule)
            denoised_images = model(noisy_images)  # Predicted clean images
            save_image(denoised_images, f"generated_epoch_{epoch}.png")
            break
    model.train()


if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        raise Exception("Please make sure to use cuda enabled GPU")

    # Model, optimizer, and device setup
    model = UNet(in_channels=3, out_channels=3).to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    loss_function = nn.MSELoss()

    # Training loop
    epochs = 10
    timesteps = 1000
    beta_schedule = linear_beta_schedule(timesteps, device).view(-1, 1, 1, 1)
    # Define transformations

    transform = transforms.Compose([
        transforms.Resize((64, 64)),  # Resize images to 64x64
        transforms.ToTensor(),  # Convert to tensor
        transforms.Normalize((0.5,), (0.5,)),  # Normalize to [-1, 1]
    ])

    # Load dataset
    dataset = datasets.CelebA(root="./data", split="train", transform=transform, download=True)
    # filter out every image that does not make this shape [32, 3, 32, 32]

    # Create DataLoader
    batch_size = 32
    dataloader = DataLoader(dataset, batch_size=batch_size)
    loss_over_time = []
    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")
        for batch_idx, (images, _) in enumerate(dataloader):
            images = images.to(device)
            if images.shape != torch.Size([32, 3, 64, 64]):
                print("Skipped an image")
                continue

            # Forward diffusion: Add noise
            t = torch.randint(0, timesteps, (images.size(0),)).to(device)  # Random timestep for each image
            noisy_images = forward_diffusion_process(images, t, beta_schedule)
            noise = torch.randn_like(images)  # True noise

            # UNet prediction
            predicted_noise = model(noisy_images)

            # Compute loss
            loss = loss_function(predicted_noise, noise)

            # Backpropagation and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            loss_over_time.append(loss.item())
            if batch_idx % 10 == 0:
                print(f"Batch {batch_idx}/{len(dataloader)} - Loss: {loss.item():.4f}")

        save_samples(model, epoch, dataloader, device)
    plt.plot(np.array(loss_over_time))
    plt.title("Loss function over timer")
    plt.xlabel("batches")
    plt.ylabel("loss")
    plt.show()

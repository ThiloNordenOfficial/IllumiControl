import torch
from matplotlib import pyplot as plt
from torch import nn

from image_generator.stable_diffusion.UNet import UNet
from image_generator.stable_diffusion.VAE.VAE import VAE
from image_generator.stable_diffusion.VAE.VAEDecoder import VAEDecoder
from image_generator.stable_diffusion.VAE.VAEEncoder import VAEEncoder
from image_generator.stable_diffusion.forward_diffusion_process import forward_diffusion_process
from image_generator.stable_diffusion.linear_beta_schedule import linear_beta_schedule
from image_generator.stable_diffusion.plot_noisy_images import plot_noisy_images
from image_generator.stable_diffusion.reverse_diffusion_step import reverse_diffusion_step


if __name__ == "__main__":
    # Example usage
    timesteps = 1000
    beta_schedule = linear_beta_schedule(timesteps)
    print(f"First 5 beta values: {beta_schedule[:5]}")

    # Visualize the beta schedule
    plt.plot(beta_schedule.numpy())
    plt.title("Linear Beta Schedule")
    plt.xlabel("Timesteps")
    plt.ylabel("Beta")
    plt.show()

    # Example image tensor
    image = torch.rand((3, 64, 64))  # Simulated 64x64 RGB image
    noisy_image = forward_diffusion_process(image, 10, beta_schedule)
    # function diffuses natively
    plot_noisy_images(image, beta_schedule)
    # Example of reverse diffusion
    denoised_image = reverse_diffusion_step(noisy_image, 10, beta_schedule)

    # Example usage
    model = UNet(in_channels=3, out_channels=3)
    print(model)

    # Example usage
    encoder = VAEEncoder(in_channels=3, latent_dim=256)
    print(encoder)

    # Example usage
    decoder = VAEDecoder(latent_dim=256, out_channels=3)
    print(decoder)

    vae = VAE(3, 256, 3)

    # LOSSFUNCTION
    loss_function = nn.MSELoss()
    predicted_noise = torch.randn((32, 3, 64, 64))  # Simulated UNet output
    actual_noise = torch.randn((32, 3, 64, 64))  # Ground truth noise
    loss = loss_function(predicted_noise, actual_noise)

    print(f"Loss: {loss.item()}")

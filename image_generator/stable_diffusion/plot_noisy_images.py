import torch
from matplotlib import pyplot as plt

from image_generator.stable_diffusion.forward_diffusion_process import forward_diffusion_process
from image_generator.stable_diffusion.linear_beta_schedule import linear_beta_schedule


def plot_noisy_images(image, noise_schedule, steps=[0, 100, 500, 999]):
    """
    Visualize the noisy images at selected timesteps.
    """
    fig, axes = plt.subplots(1, len(steps), figsize=(15, 5))
    for i, t in enumerate(steps):
        noisy_image = forward_diffusion_process(image, t, noise_schedule)
        axes[i].imshow(noisy_image.permute(1, 2, 0).numpy())
        axes[i].set_title(f"Timestep {t}")
        axes[i].axis("off")
    plt.show()


if __name__ == "__main__":
    image = torch.rand((3, 64, 64))
    beta_schedule = linear_beta_schedule(1000)
    noisy_image = forward_diffusion_process(image, 10, beta_schedule)
    plot_noisy_images(image, beta_schedule)

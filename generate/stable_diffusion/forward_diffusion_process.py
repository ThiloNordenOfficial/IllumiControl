import torch


def forward_diffusion_process(x, t, noise_schedule):
    """
    Adds noise to an image at a specific timestep.

    Args:
        x (torch.Tensor): Original image tensor.
        t (int): Timestep index.
        noise_schedule (torch.Tensor): Beta schedule tensor.

    Returns:
        torch.Tensor: Noisy image.
    """
    beta_t = noise_schedule[t]
    noise = torch.randn_like(x)  # Random Gaussian noise
    return torch.sqrt(1 - beta_t) * x + torch.sqrt(beta_t) * noise

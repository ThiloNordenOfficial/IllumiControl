import torch


def reverse_diffusion_step(x, t, noise_schedule):
    """
    Simulates one step of reverse diffusion.

    Args:
        x (torch.Tensor): Noisy image tensor.
        t (int): Timestep index.
        noise_schedule (torch.Tensor): Beta schedule tensor.

    Returns:
        torch.Tensor: Less noisy image.
    """
    beta_t = noise_schedule[t]
    noise = torch.randn_like(x)
    return (x - torch.sqrt(beta_t) * noise) / torch.sqrt(1 - beta_t)
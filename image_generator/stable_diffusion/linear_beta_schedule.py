import torch
from matplotlib import pyplot as plt


def linear_beta_schedule(timesteps, device="cpu"):
    """
    Generate a linear beta schedule.

    Args:
        timesteps (int): Number of timesteps in the schedule.

    Returns:
        torch.Tensor: A tensor of beta values.
    """
    beta_start = 1e-4  # Smallest beta value
    beta_end = 2e-2  # Largest beta value
    return torch.linspace(beta_start, beta_end, timesteps, device=device)


def plot_beta_schedule():
    # Visualize the beta schedule
    plt.plot(beta_schedule.numpy())
    plt.title("Linear Beta Schedule")
    plt.xlabel("Timesteps")
    plt.ylabel("Beta")
    plt.show()


if __name__ == "__main__":
    # Example usage
    timesteps = 1000
    beta_schedule = linear_beta_schedule(timesteps)
    print(f"First 5 beta values: {beta_schedule[:5]}")

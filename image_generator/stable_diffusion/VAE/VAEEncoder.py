from torch import nn


class VAEEncoder(nn.Module):
    def __init__(self, in_channels, latent_dim):
        super(VAEEncoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, latent_dim, kernel_size=4, stride=2, padding=1),
        )

    def forward(self, x):
        return self.encoder(x)
